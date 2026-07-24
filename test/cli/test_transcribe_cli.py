#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.transcribe_cli."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch

from pytest import fixture, mark, raises

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.transcribe_cli import TranscribeCli
from scinoephile.common.argument_parsing import enum_metavar, enum_options_list_str
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.lang.transcription.transcriber import (
    DemucsMode,
    TranscriptionBackend,
    VADMode,
)
from test.helpers import assert_series_equal, test_data_root

_MEDIA_INFILE_PATH = "/tmp/test_media.mp4"
_GUIDE_INFILE_PATH = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"


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
    assert "--media-infile MEDIA_INFILE_PATH" in help_text
    assert "--guide-infile GUIDE_INFILE_PATH" in help_text
    assert "--reference-infile" not in help_text
    assert "--language" in help_text
    assert "--guide-language" in help_text
    assert "--reference-language" not in help_text
    assert "transcription language" in normalized_help_text
    assert "transcription language tag" not in normalized_help_text
    assert "guide language (detected from infile if omitted)" in normalized_help_text
    assert "guide language tag" not in normalized_help_text
    assert "--delineation-json DELINEATION_JSON_PATH" in help_text
    assert "--punctuation-json PUNCTUATION_JSON_PATH" in help_text
    assert "--first-block FIRST_BLOCK" in help_text
    assert "--last-block LAST_BLOCK" in help_text
    assert "--script" not in normalized_help_text
    assert "--convert" not in normalized_help_text
    assert "--demucs {auto,on,off}" in help_text
    assert "--vad {auto,on,off}" in help_text
    assert "--backend {whisper,mlx-audio}" in help_text
    assert "--model MODEL_NAME" in help_text
    assert "transcription model (default: backend default)" in normalized_help_text
    assert "--cache-overwrite" in help_text
    assert "overwrite matching cache files" in normalized_help_text
    media_action = next(
        action
        for action in TranscribeCli.argparser()._actions  # noqa: SLF001
        if "--media-infile" in action.option_strings
    )
    assert media_action.required
    provider_action = next(
        action
        for action in TranscribeCli.argparser()._actions  # noqa: SLF001
        if "--llm-provider" in action.option_strings
    )
    assert provider_action.help == (
        "LLM provider (default: openai). Use --list-llm-providers for more information."
    )
    assert "LLM model" in normalized_help_text
    assert (
        "text file from which to read additional LLM prompt context"
        in normalized_help_text
    )
    assert "JSON file containing delineation test cases" in normalized_help_text
    assert "JSON file containing punctuation test cases" in normalized_help_text
    for removed_option in (
        "--mimo-aligner",
        "--mimo-aligner-language",
        "--mimo-aligner-model",
        "--mimo-aligner-worker-command",
        "--mimo-chunk-duration",
        "--mimo-chunk-overlap",
        "--mimo-fallback",
        "--mimo-language",
        "--mimo-max-tokens",
        "--mimo-model",
        "--mimo-runtime",
        "--mimo-tokenizer",
        "--mimo-worker-command",
    ):
        assert removed_option not in help_text


def test_transcribe_cli_defers_model_default_to_factory():
    """Test the transcription factory supplies the backend's default model."""
    parser = TranscribeCli.argparser()
    model_action = next(
        action
        for action in parser._actions  # noqa: SLF001
        if "--model" in action.option_strings
    )

    assert model_action.default is None
    assert model_action.help == "transcription model (default: backend default)"


def test_transcribe_cli_enum_arguments_are_consistent():
    """Test enum validation, metavars, help, and defaults derive from enums."""
    actions = {
        action.dest: action
        for action in TranscribeCli.argparser()._actions  # noqa: SLF001
    }
    expected = {
        "backend": (TranscriptionBackend, TranscriptionBackend.WHISPER),
        "demucs_mode": (DemucsMode, DemucsMode.AUTO),
        "vad_mode": (VADMode, VADMode.AUTO),
    }

    for action_name, (enum_type, default) in expected.items():
        action = actions[action_name]
        assert action.choices is None
        assert action.default is default
        assert action.metavar == enum_metavar(enum_type)
        assert isinstance(action.help, str)
        assert enum_options_list_str(enum_type) in action.help
        assert "default: %(default)s" in action.help


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
                    f"--media-infile {_MEDIA_INFILE_PATH} "
                    f"--guide-infile {_GUIDE_INFILE_PATH} "
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
                    f"--media-infile {_MEDIA_INFILE_PATH} "
                    f"--guide-infile {_GUIDE_INFILE_PATH} "
                    "--language yue-Hans",
                )

    output_series = Series.from_string(stdout_stream.getvalue(), format_="srt")
    assert_series_equal(output_series, expected_series)


def test_transcribe_cli_passes_generic_configuration(
    audio_series: Mock,
    expected_series: Series,
    tmp_path: Path,
):
    """Test transcription CLI passes generic language and model configuration.

    Arguments:
        audio_series: mock audio subtitle series
        expected_series: expected transcribed subtitle series
        tmp_path: temporary directory path
    """

    def transcribe(
        input_audio_series: AudioSeries,
        reference_series: Series,
        *,
        language: Language,
        reference_language: Language | None,
        model_name: str | None,
        backend: TranscriptionBackend,
        demucs_mode: DemucsMode,
        vad_mode: VADMode,
        cache_dir_path: Path | None,
        overwrite_cache: bool,
        provider: object,
        additional_context: str | None,
        delineation_json_path: Path | None,
        punctuation_json_path: Path | None,
        start_at_idx: int,
        stop_at_idx: int | None,
    ) -> Series:
        """Validate transcription options passed by the CLI."""
        assert input_audio_series is audio_series
        assert isinstance(reference_series, Series)
        assert language is Language.yue_hant
        assert reference_language is Language.zho_hans
        assert model_name == "mlx-community/Qwen3-ASR-0.6B-8bit"
        assert backend is TranscriptionBackend.MLX_AUDIO
        assert demucs_mode is DemucsMode.ON
        assert vad_mode is VADMode.OFF
        assert cache_dir_path == tmp_path / "cache"
        assert overwrite_cache
        assert provider is not None
        assert additional_context is None
        assert delineation_json_path == tmp_path / "delineation.json"
        assert punctuation_json_path == tmp_path / "punctuation.json"
        assert start_at_idx == 1
        assert stop_at_idx == 3
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
                f"--media-infile {_MEDIA_INFILE_PATH} "
                f"--guide-infile {_GUIDE_INFILE_PATH} "
                "--language yue-Hant --guide-language zho-Hans "
                "--model mlx-community/Qwen3-ASR-0.6B-8bit "
                "--backend mlx-audio --demucs on --vad off "
                f"--cache-dir {tmp_path / 'cache'} --cache-overwrite "
                f"--delineation-json {tmp_path / 'delineation.json'} "
                f"--punctuation-json {tmp_path / 'punctuation.json'} "
                "--first-block 2 --last-block 3",
            )


@mark.parametrize(
    "args",
    (
        f"--media-infile {_MEDIA_INFILE_PATH} "
        f"--guide-infile {_GUIDE_INFILE_PATH} "
        "--language yue-Hans --stream-index -1",
        f"--media-infile {_MEDIA_INFILE_PATH} "
        "--guide-infile /tmp/missing.srt --language yue-Hans",
        f"--media-infile /tmp/missing.mp4 "
        f"--guide-infile {_GUIDE_INFILE_PATH} --language yue-Hans",
        "--media-infile - --guide-infile - --language yue-Hans",
        f"--guide-infile {_GUIDE_INFILE_PATH} --language yue-Hans",
        f"--media-infile {_MEDIA_INFILE_PATH} "
        f"--guide-infile {_GUIDE_INFILE_PATH} "
        "--language yue-Hans --overwrite",
        f"--media-infile {_MEDIA_INFILE_PATH} "
        f"--guide-infile {_GUIDE_INFILE_PATH} "
        "--language yue-Hans --first-block 3 --last-block 2",
        f"--media-infile {_MEDIA_INFILE_PATH} "
        f"--guide-infile {_GUIDE_INFILE_PATH} "
        "--language yue-Hans --script traditional",
    ),
    ids=(
        "negative stream index",
        "missing guide infile",
        "missing media infile",
        "two stdin infiles",
        "missing media option",
        "overwrite without outfile",
        "reversed block range",
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


def test_transcribe_cli_rejects_oversized_last_block_before_loading_audio():
    """Test an oversized last block fails before media audio is extracted."""
    block_count = len(Series.load(_GUIDE_INFILE_PATH).blocks)

    with patch(
        "scinoephile.cli.transcribe_cli.AudioSeries.load_from_media"
    ) as load_from_media:
        with raises(SystemExit, match="2"):
            run_cli_with_args(
                TranscribeCli,
                f"--media-infile {_MEDIA_INFILE_PATH} "
                f"--guide-infile {_GUIDE_INFILE_PATH} "
                f"--language yue-Hans --last-block {block_count + 1}",
            )

    load_from_media.assert_not_called()


def test_transcribe_cli_stream_errors_are_user_facing():
    """Test transcription CLI surfaces stream-selection errors."""
    with patch(
        "scinoephile.cli.transcribe_cli.AudioSeries.load_from_media",
        side_effect=ScinoephileError("No stream index 7 found"),
    ):
        with raises(SystemExit, match="2"):
            run_cli_with_args(
                TranscribeCli,
                f"--media-infile {_MEDIA_INFILE_PATH} "
                f"--guide-infile {_GUIDE_INFILE_PATH} "
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
                    f"--media-infile {_MEDIA_INFILE_PATH} "
                    f"--guide-infile {_GUIDE_INFILE_PATH} "
                    "--language eng",
                )


def test_transcribe_cli_allows_stdin_guide_infile(
    audio_series: Mock,
    expected_series: Series,
):
    """Test transcription CLI allows stdin guide subtitle input.

    Arguments:
        audio_series: mock audio subtitle series
        expected_series: expected transcribed subtitle series
    """
    stdin_stream = StringIO(_GUIDE_INFILE_PATH.read_text(encoding="utf-8"))
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
                        f"--media-infile {_MEDIA_INFILE_PATH} "
                        "--guide-infile - --language yue-Hans",
                    )

    assert subtitle_paths != ["-"]
    output_series = Series.from_string(stdout_stream.getvalue(), format_="srt")
    assert_series_equal(output_series, expected_series)
