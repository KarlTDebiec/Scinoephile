#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of media subtitle extraction."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from scinoephile.media.subtitles.selection import get_media_subtitle_stream

from scinoephile.core import ScinoephileError
from scinoephile.core.media import SubtitleStream
from scinoephile.media.subtitles.cache import get_subtitle_cache_path
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
    stream_path = get_subtitle_cache_path(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )
    stream_path.parent.mkdir(parents=True)
    stream_path.write_text("cached subtitles", encoding="utf-8")

    caplog.set_level("INFO", logger="scinoephile.media.subtitles.extraction")
    with patch("scinoephile.media.subtitles.extraction.cache_subtitles") as cache:
        extracted_path = extract_subtitle_stream(
            infile_path=infile_path,
            stream=stream,
            outfile_path=outfile_path,
            cache_dir_path=tmp_path / "cache",
        )

    assert extracted_path == outfile_path
    assert outfile_path.read_text(encoding="utf-8") == "cached subtitles"
    assert f"Created subtitle output directory: {outfile_path.parent}" in caplog.text
    cache.assert_called_once_with(
        infile_path, [stream], cache_dir_path=tmp_path / "cache"
    )


def test_extract_subtitle_stream_caches_missing_stream(tmp_path: Path):
    """Test subtitle extraction builds a missing cached subtitle stream."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    outfile_path = tmp_path / "subtitles" / "eng-2.srt"
    cache_dir_path = tmp_path / "cache"
    stream = SubtitleStream(index=2, language="eng", codec_name="subrip")
    stream_path = get_subtitle_cache_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )

    def cache_streams(
        infile_path: Path,
        streams: list[SubtitleStream],
        *,
        cache_dir_path: Path | None = None,
    ):
        stream_path.parent.mkdir(parents=True)
        stream_path.write_text("new subtitles", encoding="utf-8")

    with patch(
        "scinoephile.media.subtitles.extraction.cache_subtitles",
        side_effect=cache_streams,
    ) as cache:
        extracted_path = extract_subtitle_stream(
            infile_path=infile_path,
            stream=stream,
            outfile_path=outfile_path,
            cache_dir_path=cache_dir_path,
        )

    assert extracted_path == outfile_path
    assert outfile_path.read_text(encoding="utf-8") == "new subtitles"
    cache.assert_called_once_with(infile_path, [stream], cache_dir_path=cache_dir_path)


def test_extract_subtitle_stream_rejects_unknown_codec(tmp_path: Path):
    """Test single-stream extraction rejects unknown subtitle codecs."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    outfile_path = tmp_path / "subtitles" / "eng-2.srt"
    outfile_path.parent.mkdir()

    with pytest.raises(ScinoephileError, match="Unsupported subtitle codec unknown"):
        extract_subtitle_stream(
            infile_path=infile_path,
            stream=SubtitleStream(index=2, language="eng", codec_name="unknown"),
            outfile_path=outfile_path,
            cache_dir_path=tmp_path / "cache",
        )


def test_get_media_subtitle_stream_returns_matching_sup_stream(tmp_path: Path):
    """Test media subtitle stream selection returns the matching SUP stream."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    stream = SubtitleStream(index=5, codec_name="hdmv_pgs_subtitle")

    with patch(
        "scinoephile.media.subtitles.selection.get_subtitle_streams",
        return_value=[stream],
    ) as get_subtitle_streams:
        selected_stream = get_media_subtitle_stream(infile_path, 5)

    assert selected_stream is stream
    get_subtitle_streams.assert_called_once_with(infile_path)


def test_get_media_subtitle_stream_requires_stream_index(tmp_path: Path):
    """Test media subtitle stream selection requires a stream index."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with pytest.raises(
        ScinoephileError,
        match="stream index is required for media OCR input",
    ):
        get_media_subtitle_stream(infile_path, None)


def test_get_media_subtitle_stream_rejects_non_sup_stream(tmp_path: Path):
    """Test media subtitle stream selection rejects non-SUP subtitle streams."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with (
        patch(
            "scinoephile.media.subtitles.selection.get_subtitle_streams",
            return_value=[SubtitleStream(index=5, codec_name="subrip")],
        ),
        pytest.raises(
            ScinoephileError,
            match="Subtitle stream 5 is not an image-based SUP stream",
        ),
    ):
        get_media_subtitle_stream(infile_path, 5)


def test_get_media_subtitle_stream_wraps_probe_errors(tmp_path: Path):
    """Test media subtitle stream selection wraps probe failures."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with (
        patch(
            "scinoephile.media.subtitles.selection.get_subtitle_streams",
            side_effect=RuntimeError("ffprobe failed"),
        ),
        pytest.raises(
            ScinoephileError,
            match="Unable to inspect subtitle streams in .*video.mkv.*ffprobe failed",
        ) as excinfo,
    ):
        get_media_subtitle_stream(infile_path, 5)

    assert isinstance(excinfo.value.__cause__, RuntimeError)
