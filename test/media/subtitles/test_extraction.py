#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of media subtitle extraction."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from pytest import raises

from scinoephile.core import ScinoephileError
from scinoephile.core.media import SubtitleStream
from scinoephile.media.subtitles.cache import SubtitleCache
from scinoephile.media.subtitles.extraction import extract_subtitle_stream


def test_extract_subtitle_stream_copies_cached_stream(tmp_path: Path, caplog):
    """Test subtitle extraction copies an existing cached subtitle stream.

    Arguments:
        tmp_path: temporary directory provided by pytest
        caplog: pytest log capture fixture
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    outfile_path = tmp_path / "subtitles" / "eng-2.srt"
    stream = SubtitleStream(index=2, language="eng", codec_name="subrip")
    cache_root_path = tmp_path / "cache"
    stream_path = SubtitleCache(cache_root_path).get_path(infile_path, stream)
    stream_path.parent.mkdir(parents=True)
    stream_path.write_text("cached subtitles", encoding="utf-8")

    caplog.set_level("INFO", logger="scinoephile.media.subtitles.extraction")
    with patch(
        "scinoephile.media.subtitles.extraction.SubtitleExtractor.extract",
        return_value=[stream_path],
    ):
        extracted_path = extract_subtitle_stream(
            infile_path=infile_path,
            stream=stream,
            outfile_path=outfile_path,
            cache_root_path=cache_root_path,
        )

    assert extracted_path == outfile_path
    assert outfile_path.read_text(encoding="utf-8") == "cached subtitles"
    assert f"Created subtitle output directory: {outfile_path.parent}" in caplog.text


def test_extract_subtitle_stream_caches_missing_stream(tmp_path: Path):
    """Test subtitle extraction builds a missing cached subtitle stream.

    Arguments:
        tmp_path: temporary directory path
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    outfile_path = tmp_path / "subtitles" / "eng-2.srt"
    cache_root_path = tmp_path / "cache"
    stream = SubtitleStream(index=2, language="eng", codec_name="subrip")
    stream_path = SubtitleCache(cache_root_path).get_path(infile_path, stream)

    def cache_streams(
        infile_path: Path, streams: list[SubtitleStream], *, render_images: bool = True
    ) -> list[Path]:
        """Create and return a cached subtitle stream.

        Arguments:
            infile_path: infile path
            streams: streams value
            render_images: render images value
        Returns:
            and return a cached subtitle stream
        """
        _ = infile_path, streams, render_images
        stream_path.parent.mkdir(parents=True)
        stream_path.write_text("new subtitles", encoding="utf-8")
        return [stream_path]

    with patch(
        "scinoephile.media.subtitles.extraction.SubtitleExtractor.extract",
        side_effect=cache_streams,
    ):
        extracted_path = extract_subtitle_stream(
            infile_path=infile_path,
            stream=stream,
            outfile_path=outfile_path,
            cache_root_path=cache_root_path,
        )

    assert extracted_path == outfile_path
    assert outfile_path.read_text(encoding="utf-8") == "new subtitles"


def test_extract_subtitle_stream_rejects_unknown_codec(tmp_path: Path):
    """Test single-stream extraction rejects unknown subtitle codecs.

    Arguments:
        tmp_path: temporary directory path
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    outfile_path = tmp_path / "subtitles" / "eng-2.srt"
    outfile_path.parent.mkdir()

    with raises(ScinoephileError, match="Unsupported subtitle codec unknown"):
        extract_subtitle_stream(
            infile_path=infile_path,
            stream=SubtitleStream(index=2, language="eng", codec_name="unknown"),
            outfile_path=outfile_path,
            cache_root_path=tmp_path / "cache",
        )
