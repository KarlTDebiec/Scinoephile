#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of media subtitle stream selection."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from pytest import raises

from scinoephile.core import ScinoephileError
from scinoephile.core.media import SubtitleStream
from scinoephile.media.subtitles.selection import get_media_subtitle_stream


def test_get_media_subtitle_stream_returns_matching_sup_stream(tmp_path: Path):
    """Test media subtitle stream selection returns the matching SUP stream."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    stream = SubtitleStream(index=5, codec_name="hdmv_pgs_subtitle")

    with patch(
        "scinoephile.media.subtitles.selection.get_subtitle_streams",
        return_value=[stream],
    ):
        selected_stream = get_media_subtitle_stream(infile_path, 5)

    assert selected_stream is stream


def test_get_media_subtitle_stream_requires_stream_index(tmp_path: Path):
    """Test media subtitle stream selection requires a stream index."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with raises(
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
        raises(
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
        raises(
            ScinoephileError,
            match="Unable to inspect subtitle streams in .*video.mkv.*ffprobe failed",
        ) as excinfo,
    ):
        get_media_subtitle_stream(infile_path, 5)

    assert isinstance(excinfo.value.__cause__, RuntimeError)
