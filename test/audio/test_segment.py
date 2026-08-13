#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of pydub audio segment loading."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from pytest import raises

from scinoephile.audio.segment import load_audio_segment
from scinoephile.common.file import get_temp_file_path
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.media.audio import AudioExtractionMode


def test_load_audio_segment_extracts_and_decodes_selected_stream():
    """Load media through the canonical extraction path."""
    with get_temp_file_path(".wav") as media_path:
        media_path.touch()
        with patch(
            "scinoephile.audio.segment.extract_audio", side_effect=_write_selected_audio
        ) as extract:
            audio = load_audio_segment(
                media_path, stream_index=12, mode=AudioExtractionMode.CENTER_HEAVY
            )

    extract.assert_called_once()
    assert extract.call_args.args[0] == media_path
    assert extract.call_args.args[1].suffix == ".wav"
    assert extract.call_args.kwargs == {
        "stream_index": 12,
        "mode": AudioExtractionMode.CENTER_HEAVY,
    }
    assert len(audio) == 3126


def test_load_audio_segment_wraps_input_path_errors(tmp_path: Path):
    """Present invalid media paths as domain errors.

    Arguments:
        tmp_path: pytest temporary directory path
    """
    with raises(ScinoephileError, match="Unable to extract audio") as excinfo:
        load_audio_segment(tmp_path / "missing.mkv")

    assert isinstance(excinfo.value.__cause__, OSError)


def test_load_audio_segment_wraps_decode_errors():
    """Present pydub decode failures as domain errors."""
    with get_temp_file_path(".mp4") as media_path:
        media_path.touch()
        with (
            patch("scinoephile.audio.segment.extract_audio"),
            patch(
                "scinoephile.audio.segment.AudioSegment.from_wav",
                side_effect=CouldntDecodeError("invalid audio"),
            ),
            raises(
                ScinoephileError, match="Unable to load audio from media"
            ) as excinfo,
        ):
            load_audio_segment(media_path)

    assert isinstance(excinfo.value.__cause__, CouldntDecodeError)


def _write_selected_audio(
    infile_path: Path,
    outfile_path: Path,
    *,
    stream_index: int | None = None,
    mode: AudioExtractionMode = AudioExtractionMode.ORIGINAL,
    overwrite: bool = False,
):
    """Write a WAV whose duration identifies the selected stream.

    Arguments:
        infile_path: input media path
        outfile_path: output WAV path
        stream_index: selected audio stream index
        mode: channel preparation used during audio extraction
        overwrite: whether an existing output may be replaced
    """
    _ = infile_path, mode, overwrite
    if stream_index is None:
        stream_index = 1
    channels = 6 if stream_index == 12 else 2
    AudioSegment.silent(duration=3000 + stream_index * 10 + channels).export(
        outfile_path, format="wav"
    )
