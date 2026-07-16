#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.transcribe_cli."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from unittest.mock import Mock, patch

from pytest import fixture, mark, raises

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.transcribe_cli import TranscribeCli
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.lang.transcription.processor import DemucsMode, VADMode
from test.helpers import assert_series_equal, test_data_root

_MEDIA_INFILE_PATH = "/tmp/test_media.mp4"
_REFERENCE_INFILE_PATH = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"


@fixture
def audio_series() -> Mock:
    """Get a mock audio subtitle series."""
    return Mock(spec=AudioSeries)


@fixture
def expected_series() -> Series:
    """Get the expected transcribed subtitle series."""
    return Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n你好\n",
        format_="srt",
    )


def test_transcribe_cli_is_top_level_command():
    """Test the generic transcription CLI is registered at the top level."""
    assert TranscribeCli.name() == "transcribe"
    assert ScinoephileCli.subcommands()["transcribe"] is TranscribeCli
    assert "yue" not in ScinoephileCli.subcommands()


def test_transcribe_help_lists_generic_options():
    """Test transcription CLI help lists generic transcription options."""
    stdout = StringIO()
    stderr = StringIO()

    with raises(SystemExit, match="0"):
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(TranscribeCli, "-h")

    help_text = stdout.getvalue()
    normalized_help_text = " ".join(help_text.split())
    assert stderr.getvalue() == ""
    assert "MEDIA_INFILE" in help_text
    assert "--reference-infile REFERENCE_INFILE_PATH" in help_text
    assert "--language" in help_text
    assert "--reference-language" in help_text
    assert "--script" not in normalized_help_text
    assert "--convert" not in normalized_help_text
    assert "--demucs {auto,on,off}" in help_text
    assert "--vad {auto,on,off}" in help_text
    assert "--whisper-model MODEL_NAME" in help_text
    assert "uses language-pair default if omitted" in normalized_help_text


def test_transcribe_cli_defers_whisper_model_default_to_registry():
    """Test the language-pair registry supplies the default Whisper model."""
    parser = TranscribeCli.argparser()
    whisper_model_action = next(
        action
        for action in parser._actions  # noqa: SLF001
        if "--whisper-model" in action.option_strings
    )

    assert whisper_model_action.default is None


def test_transcribe_cli_defaults_audio_preprocessing_to_auto():
    """Test transcription CLI defaults Demucs and VAD to automatic modes."""
    parser = TranscribeCli.argparser()
    demucs_action = next(
        action
        for action in parser._actions  # noqa: SLF001
        if "--demucs" in action.option_strings
    )
    vad_action = next(
        action
        for action in parser._actions  # noqa: SLF001
        if "--vad" in action.option_strings
    )

    assert demucs_action.default is DemucsMode.AUTO
    assert vad_action.default is VADMode.AUTO


def test_transcribe_cli_writes_file(
    audio_series: Mock,
    expected_series: Series,
):
    """Test generic transcription CLI writes file output.

    Arguments:
        audio_series: mock audio subtitle series
        expected_series: expected transcribed subtitle series
    """
    with get_temp_file_path(".srt") as outfile_path:
        with patch(
            "scinoephile.cli.transcribe_cli.AudioSeries.load_from_media",
            return_value=audio_series,
        ):
            with patch(
                "scinoephile.cli.transcribe_cli.transcribe_series_guided",
                return_value=expected_series,
            ):
                run_cli_with_args(
                    TranscribeCli,
                    f"{_MEDIA_INFILE_PATH} "
                    f"--reference-infile {_REFERENCE_INFILE_PATH} "
                    f"--language yue-Hans --stream-index 1 -o {outfile_path}",
                )
        output_series = Series.load(outfile_path)

    assert_series_equal(output_series, expected_series)


def test_transcribe_cli_writes_stdout(
    audio_series: Mock,
    expected_series: Series,
):
    """Test generic transcription CLI writes stdout output.

    Arguments:
        audio_series: mock audio subtitle series
        expected_series: expected transcribed subtitle series
    """
    stdout_stream = StringIO()

    with patch(
        "scinoephile.cli.transcribe_cli.AudioSeries.load_from_media",
        return_value=audio_series,
    ):
        with patch(
            "scinoephile.cli.transcribe_cli.transcribe_series_guided",
            return_value=expected_series,
        ):
            with patch("scinoephile.cli.helpers.io.stdout", stdout_stream):
                run_cli_with_args(
                    TranscribeCli,
                    f"{_MEDIA_INFILE_PATH} "
                    f"--reference-infile {_REFERENCE_INFILE_PATH} "
                    "--language yue-Hans",
                )

    output_series = Series.from_string(stdout_stream.getvalue(), format_="srt")
    assert_series_equal(output_series, expected_series)


def test_transcribe_cli_passes_generic_configuration(
    audio_series: Mock,
    expected_series: Series,
):
    """Test transcription CLI passes generic language and model configuration.

    Arguments:
        audio_series: mock audio subtitle series
        expected_series: expected transcribed subtitle series
    """

    def transcribe(
        input_audio_series: AudioSeries,
        reference_series: Series,
        *,
        language: Language,
        reference_language: Language | None,
        model_name: str | None,
        demucs_mode: DemucsMode,
        vad_mode: VADMode,
        provider: object,
        additional_context: str | None,
    ) -> Series:
        """Validate transcription options passed by the CLI."""
        assert input_audio_series is audio_series
        assert isinstance(reference_series, Series)
        assert language is Language.yue_hant
        assert reference_language is Language.zho_hans
        assert model_name == "custom/whisper"
        assert demucs_mode is DemucsMode.ON
        assert vad_mode is VADMode.OFF
        assert provider is not None
        assert additional_context is None
        return expected_series

    with patch(
        "scinoephile.cli.transcribe_cli.AudioSeries.load_from_media",
        return_value=audio_series,
    ):
        with patch(
            "scinoephile.cli.transcribe_cli.transcribe_series_guided",
            side_effect=transcribe,
        ):
            run_cli_with_args(
                TranscribeCli,
                f"{_MEDIA_INFILE_PATH} "
                f"--reference-infile {_REFERENCE_INFILE_PATH} "
                "--language yue-Hant --reference-language zho-Hans "
                "--whisper-model custom/whisper --demucs on --vad off",
            )


@mark.parametrize(
    "args",
    (
        f"{_MEDIA_INFILE_PATH} --reference-infile {_REFERENCE_INFILE_PATH} "
        "--language yue-Hans --stream-index -1",
        f"{_MEDIA_INFILE_PATH} --reference-infile /tmp/missing.srt --language yue-Hans",
        f"/tmp/missing.mp4 --reference-infile {_REFERENCE_INFILE_PATH} "
        "--language yue-Hans",
        "- --reference-infile - --language yue-Hans",
        f"{_MEDIA_INFILE_PATH} --reference-infile {_REFERENCE_INFILE_PATH} "
        "--language yue-Hans --overwrite",
        f"{_MEDIA_INFILE_PATH} --reference-infile {_REFERENCE_INFILE_PATH} "
        "--language yue-Hans --script traditional",
    ),
    ids=(
        "negative stream index",
        "missing reference infile",
        "missing media infile",
        "two stdin infiles",
        "overwrite without outfile",
        "language-specific option",
    ),
)
def test_transcribe_cli_rejects_invalid_arguments(args: str):
    """Test transcription CLI rejects invalid arguments.

    Arguments:
        args: invalid CLI argument string
    """
    with raises(SystemExit, match="2"):
        run_cli_with_args(TranscribeCli, args)


def test_transcribe_cli_stream_errors_are_user_facing():
    """Test transcription CLI surfaces stream-selection errors."""
    with patch(
        "scinoephile.cli.transcribe_cli.AudioSeries.load_from_media",
        side_effect=ScinoephileError("No stream index 7 found"),
    ):
        with raises(SystemExit, match="2"):
            run_cli_with_args(
                TranscribeCli,
                f"{_MEDIA_INFILE_PATH} --reference-infile {_REFERENCE_INFILE_PATH} "
                "--language yue-Hans --stream-index 7",
            )


def test_transcribe_cli_workflow_errors_are_user_facing(audio_series: Mock):
    """Test transcription CLI surfaces unsupported language-pair errors.

    Arguments:
        audio_series: mock audio subtitle series
    """
    with patch(
        "scinoephile.cli.transcribe_cli.AudioSeries.load_from_media",
        return_value=audio_series,
    ):
        with patch(
            "scinoephile.cli.transcribe_cli.transcribe_series_guided",
            side_effect=ScinoephileError("Unsupported language pair"),
        ):
            with raises(SystemExit, match="2"):
                run_cli_with_args(
                    TranscribeCli,
                    f"{_MEDIA_INFILE_PATH} "
                    f"--reference-infile {_REFERENCE_INFILE_PATH} "
                    "--language eng",
                )


def test_transcribe_cli_allows_stdin_reference_infile(
    audio_series: Mock,
    expected_series: Series,
):
    """Test transcription CLI allows stdin reference subtitle input.

    Arguments:
        audio_series: mock audio subtitle series
        expected_series: expected transcribed subtitle series
    """
    stdin_stream = StringIO(_REFERENCE_INFILE_PATH.read_text(encoding="utf-8"))
    stdout_stream = StringIO()
    subtitle_paths: list[object] = []

    def load_from_media(
        *,
        media_path: str,
        subtitle_path: object,
        stream_index: int | None,
    ) -> AudioSeries:
        """Record media loading inputs."""
        assert media_path == _MEDIA_INFILE_PATH
        assert stream_index is None
        subtitle_paths.append(subtitle_path)
        return audio_series

    with patch("scinoephile.cli.helpers.io.stdin", stdin_stream):
        with patch(
            "scinoephile.cli.transcribe_cli.AudioSeries.load_from_media",
            side_effect=load_from_media,
        ):
            with patch(
                "scinoephile.cli.transcribe_cli.transcribe_series_guided",
                return_value=expected_series,
            ):
                with patch("scinoephile.cli.helpers.io.stdout", stdout_stream):
                    run_cli_with_args(
                        TranscribeCli,
                        f"{_MEDIA_INFILE_PATH} "
                        "--reference-infile - --language yue-Hans",
                    )

    assert subtitle_paths != ["-"]
    output_series = Series.from_string(stdout_stream.getvalue(), format_="srt")
    assert_series_equal(output_series, expected_series)
