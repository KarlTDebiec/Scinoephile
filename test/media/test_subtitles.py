#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of media subtitle extraction."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from scinoephile.core.media import SubtitleStream

from scinoephile.core import ScinoephileError
from scinoephile.media.subtitles import extract_subtitle_stream


def test_extract_subtitle_stream_runs_ffmpeg(tmp_path: Path):
    """Test single-stream extraction runs ffmpeg and returns output path."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    outfile_path = tmp_path / "subtitles" / "eng-2.srt"
    outfile_path.parent.mkdir()
    ffmpeg_input = Mock()

    with patch(
        "scinoephile.media.subtitles.ffmpeg.input",
        return_value=ffmpeg_input,
    ):
        extracted_path = extract_subtitle_stream(
            infile_path=infile_path,
            stream=SubtitleStream(index=2, language="eng", codec_name="subrip"),
            outfile_path=outfile_path,
        )

    assert extracted_path == outfile_path
    ffmpeg_input.output.assert_called_once_with(
        str(outfile_path),
        map="0:2",
        **{"c:s": "subrip"},
    )


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
        )
