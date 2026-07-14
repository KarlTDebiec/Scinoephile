#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.transcribe_cli."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from unittest.mock import Mock, patch

from pytest import raises

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.transcribe_cli import TranscribeCli
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.multilang.transcription.processor import DemucsMode, VADMode
from test.helpers import assert_series_equal, test_data_root


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
    assert "--demucs {on,off}" in help_text
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


def test_transcribe_cli_writes_file():
    """Test generic transcription CLI writes file output."""
    reference_infile_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"
    expected_series = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n你好\n",
        format_="srt",
    )
    audio_series = Mock(spec=AudioSeries)

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
                    f"{media_infile_path} "
                    f"--reference-infile {reference_infile_path} "
                    f"--language yue-Hans --stream-index 1 -o {outfile_path}",
                )
        output_series = Series.load(outfile_path)

    assert_series_equal(output_series, expected_series)


def test_transcribe_cli_writes_stdout():
    """Test generic transcription CLI writes stdout output."""
    reference_infile_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"
    expected_series = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n你好\n",
        format_="srt",
    )
    audio_series = Mock(spec=AudioSeries)
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
                    f"{media_infile_path} "
                    f"--reference-infile {reference_infile_path} "
                    "--language yue-Hans",
                )

    output_series = Series.from_string(stdout_stream.getvalue(), format_="srt")
    assert_series_equal(output_series, expected_series)


def test_transcribe_cli_passes_generic_configuration():
    """Test transcription CLI passes generic language and model configuration."""
    reference_infile_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"
    expected_series = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n你好\n",
        format_="srt",
    )
    audio_series = Mock(spec=AudioSeries)

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
                f"{media_infile_path} "
                f"--reference-infile {reference_infile_path} "
                "--language yue-Hant --reference-language zho-Hans "
                "--whisper-model custom/whisper --demucs on --vad off",
            )


def test_transcribe_cli_rejects_negative_stream_index():
    """Test transcription CLI rejects negative stream indexes."""
    reference_infile_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"

    with raises(SystemExit, match="2"):
        run_cli_with_args(
            TranscribeCli,
            f"/tmp/test_media.mp4 --reference-infile {reference_infile_path} "
            "--language yue-Hans --stream-index -1",
        )


def test_transcribe_cli_stream_errors_are_user_facing():
    """Test transcription CLI surfaces stream-selection errors."""
    reference_infile_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"

    with patch(
        "scinoephile.cli.transcribe_cli.AudioSeries.load_from_media",
        side_effect=ScinoephileError("No stream index 7 found"),
    ):
        with raises(SystemExit, match="2"):
            run_cli_with_args(
                TranscribeCli,
                f"/tmp/test_media.mp4 --reference-infile {reference_infile_path} "
                "--language yue-Hans --stream-index 7",
            )


def test_transcribe_cli_workflow_errors_are_user_facing():
    """Test transcription CLI surfaces unsupported language-pair errors."""
    reference_infile_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"
    audio_series = Mock(spec=AudioSeries)

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
                    f"/tmp/test_media.mp4 --reference-infile {reference_infile_path} "
                    "--language eng",
                )


def test_transcribe_cli_rejects_missing_reference_infile():
    """Test transcription CLI surfaces missing reference subtitle infiles."""
    with raises(SystemExit, match="2"):
        run_cli_with_args(
            TranscribeCli,
            "/tmp/test_media.mp4 --reference-infile /tmp/missing.srt "
            "--language yue-Hans",
        )


def test_transcribe_cli_rejects_missing_media_infile():
    """Test transcription CLI surfaces missing media infiles."""
    reference_infile_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"

    with raises(SystemExit, match="2"):
        run_cli_with_args(
            TranscribeCli,
            f"/tmp/missing.mp4 --reference-infile {reference_infile_path} "
            "--language yue-Hans",
        )


def test_transcribe_cli_allows_stdin_reference_infile():
    """Test transcription CLI allows stdin reference subtitle input."""
    reference_infile_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"
    expected_series = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n你好\n",
        format_="srt",
    )
    audio_series = Mock(spec=AudioSeries)
    stdin_stream = StringIO(reference_infile_path.read_text(encoding="utf-8"))
    stdout_stream = StringIO()
    subtitle_paths: list[object] = []

    def load_from_media(
        *,
        media_path: str,
        subtitle_path: object,
        stream_index: int | None,
    ) -> AudioSeries:
        """Record media loading inputs."""
        assert media_path == "/tmp/test_media.mp4"
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
                        "/tmp/test_media.mp4 --reference-infile - --language yue-Hans",
                    )

    assert subtitle_paths != ["-"]
    output_series = Series.from_string(stdout_stream.getvalue(), format_="srt")
    assert_series_equal(output_series, expected_series)


def test_transcribe_cli_rejects_two_stdin_infiles():
    """Test transcription CLI rejects stdin for both inputs."""
    with raises(SystemExit, match="2"):
        run_cli_with_args(
            TranscribeCli,
            "- --reference-infile - --language yue-Hans",
        )


def test_transcribe_cli_rejects_overwrite_without_outfile():
    """Test transcription CLI rejects overwrite when writing to stdout."""
    reference_infile_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"

    with raises(SystemExit, match="2"):
        run_cli_with_args(
            TranscribeCli,
            f"/tmp/test_media.mp4 --reference-infile {reference_infile_path} "
            "--language yue-Hans --overwrite",
        )


def test_transcribe_cli_rejects_language_specific_options():
    """Test generic transcription CLI rejects former Yue-specific options."""
    reference_infile_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"

    with raises(SystemExit, match="2"):
        run_cli_with_args(
            TranscribeCli,
            f"/tmp/test_media.mp4 --reference-infile {reference_infile_path} "
            "--language yue-Hans --script traditional",
        )
