#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.media.MediaExtractAudioCli."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from pytest import CaptureFixture, raises

from scinoephile.cli.media.media_extract_audio_cli import MediaExtractAudioCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.media.audio_stream import AudioStream


def test_media_extract_audio_cli_extracts_selected_stream(
    tmp_path: Path,
    capsys: CaptureFixture[str],
):
    """Test extract-audio forwards its options and reports the output.

    Arguments:
        tmp_path: temporary directory provided by pytest
        capsys: pytest output capture fixture
    """
    infile_path = tmp_path / "movie.mkv"
    infile_path.touch()
    outfile_path = tmp_path / "audio.wav"
    stream = AudioStream(
        index=3,
        codec_type="audio",
        codec_name="aac",
        language="yue",
        channels=6,
    )

    with patch(
        "scinoephile.cli.media.media_extract_audio_cli.extract_audio",
        return_value=stream,
    ) as extract:
        run_cli_with_args(
            MediaExtractAudioCli,
            f"--infile {infile_path} --stream-index 3 --outfile {outfile_path} "
            "--overwrite",
        )

    extract.assert_called_once_with(
        infile_path.resolve(),
        outfile_path.resolve(),
        stream_index=3,
        overwrite=True,
    )
    assert capsys.readouterr().out.strip() == (
        f"Extracted audio: {stream.description} -> {outfile_path.resolve()}"
    )


def test_media_extract_audio_cli_maps_extraction_errors_to_parser_errors(
    tmp_path: Path,
):
    """Test extract-audio presents domain failures as argument errors.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "movie.mkv"
    infile_path.touch()
    outfile_path = tmp_path / "audio.wav"

    with (
        patch(
            "scinoephile.cli.media.media_extract_audio_cli.extract_audio",
            side_effect=ScinoephileError("No audio streams found"),
        ),
        raises(SystemExit) as excinfo,
    ):
        run_cli_with_args(
            MediaExtractAudioCli,
            f"--infile {infile_path} --outfile {outfile_path}",
        )

    assert excinfo.value.code == 2
