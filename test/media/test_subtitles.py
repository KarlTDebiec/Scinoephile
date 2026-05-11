#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of media subtitle extraction."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from scinoephile.core import ScinoephileError
from scinoephile.core.media import SubtitleStream
from scinoephile.media.subtitles import extraction
from scinoephile.media.subtitles.cache import get_cached_subtitle_artifact_path
from scinoephile.media.subtitles.extraction import extract_subtitle_stream


def test_extract_subtitle_stream_copies_cached_artifact(tmp_path: Path):
    """Test subtitle extraction copies an existing cached artifact."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    outfile_path = tmp_path / "subtitles" / "eng-2.srt"
    stream = SubtitleStream(index=2, language="eng", codec_name="subrip")
    artifact_path = get_cached_subtitle_artifact_path(
        infile_path,
        stream,
        cache_dir_path=tmp_path / "cache",
    )
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text("cached subtitles", encoding="utf-8")

    with patch(
        "scinoephile.media.subtitles.extraction.cache_subtitle_stream_artifacts"
    ) as cache_artifacts:
        extracted_path = extract_subtitle_stream(
            infile_path=infile_path,
            stream=stream,
            outfile_path=outfile_path,
            cache_dir_path=tmp_path / "cache",
        )

    assert extracted_path == outfile_path
    assert outfile_path.read_text(encoding="utf-8") == "cached subtitles"
    cache_artifacts.assert_not_called()


def test_extract_subtitle_stream_caches_missing_artifact(tmp_path: Path):
    """Test subtitle extraction builds a missing cached artifact."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    outfile_path = tmp_path / "subtitles" / "eng-2.srt"
    cache_dir_path = tmp_path / "cache"
    stream = SubtitleStream(index=2, language="eng", codec_name="subrip")
    artifact_path = get_cached_subtitle_artifact_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )

    def cache_artifacts(
        infile_path: Path,
        streams: list[SubtitleStream],
        *,
        cache_dir_path: Path | None = None,
    ):
        artifact_path.parent.mkdir(parents=True)
        artifact_path.write_text("new subtitles", encoding="utf-8")

    with patch(
        "scinoephile.media.subtitles.extraction.cache_subtitle_stream_artifacts",
        side_effect=cache_artifacts,
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


def test_extract_subtitle_stream_from_cache_is_not_public():
    """Test the cached extraction implementation does not expose a second API."""
    assert not hasattr(extraction, "extract_subtitle_stream_from_cache")
