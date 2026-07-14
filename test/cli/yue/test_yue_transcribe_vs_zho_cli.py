#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.yue.yue_transcribe_vs_zho_cli."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from unittest.mock import Mock, patch

from pytest import raises

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.cli.yue.yue_transcribe_vs_zho_cli import YueTranscribeVsZhoCli
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.llms.delineation import DelineationPrompt
from scinoephile.llms.punctuation import PunctuationPrompt
from scinoephile.multilang.yue_zho.transcription import DEFAULT_YUE_WHISPER_MODEL_NAME
from scinoephile.multilang.yue_zho.transcription.delineation import (
    YueDelineationVsZhoPromptYueHant,
)
from scinoephile.multilang.yue_zho.transcription.punctuation import (
    YuePunctuationVsZhoPromptYueHant,
)
from test.helpers import (
    assert_series_equal,
    test_data_root,
)


def test_yue_transcribe_vs_zho_help_lists_transcription_options():
    """Test written Cantonese CLI help lists transcription options."""
    stdout = StringIO()
    stderr = StringIO()

    with raises(SystemExit, match="0"):
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(YueTranscribeVsZhoCli, "-h")

    help_text = stdout.getvalue()
    normalized_help_text = " ".join(help_text.split())
    assert stderr.getvalue() == ""
    assert "--script {simplified,traditional}" in help_text
    assert "script used for transcription prompts" in help_text
    assert "--convert" not in normalized_help_text
    assert "--demucs {on,off}" in help_text
    assert "Demucs vocal-separation mode" in help_text
    assert "options: on, off;" in help_text
    assert "default: off" in help_text
    assert "--vad {auto,on,off}" in help_text
    assert "Whisper voice activity detection mode" in help_text
    assert "off, auto; default: auto" in help_text
    assert "--whisper-model WHISPER_MODEL_NAME" in help_text
    assert "Whisper model identifier used for transcription" in help_text
    assert "default: first audio stream" in help_text


def test_yue_transcribe_vs_zho_cli_uses_default_whisper_model_constant():
    """Test CLI default Whisper model matches the transcription default."""
    parser = YueTranscribeVsZhoCli.argparser()
    whisper_model_action = next(
        action
        for action in parser._actions  # noqa: SLF001
        if "--whisper-model" in action.option_strings
    )

    assert whisper_model_action.default == DEFAULT_YUE_WHISPER_MODEL_NAME


def test_yue_transcribe_vs_zho_cli_writes_file():
    """Test written Cantonese transcribe-vs-zho CLI writes file output."""
    zhongwen_infile_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"
    expected_series = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n你好\n",
        format_="srt",
    )
    yuewen_audio_series = Mock(spec=AudioSeries)

    with get_temp_file_path(".srt") as outfile_path:
        with patch(
            "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.AudioSeries.load_from_media",
            return_value=yuewen_audio_series,
        ):
            with patch(
                "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.get_yue_vs_zho_transcriber",
                return_value="transcriber",
            ):
                with patch(
                    "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.get_yue_transcribed_vs_zho",
                    return_value=expected_series,
                ):
                    run_cli_with_args(
                        YueTranscribeVsZhoCli,
                        f"--media-infile {media_infile_path} "
                        f"--zho-infile {zhongwen_infile_path} "
                        f"--stream-index 1 -o {outfile_path}",
                    )
        output_series = Series.load(outfile_path)

    assert_series_equal(output_series, expected_series)


def test_yue_transcribe_vs_zho_cli_writes_stdout():
    """Test written Cantonese transcribe-vs-zho CLI writes stdout output."""
    zhongwen_infile_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"
    expected_series = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n你好\n",
        format_="srt",
    )
    yuewen_audio_series = Mock(spec=AudioSeries)
    stdout_stream = StringIO()

    with patch(
        "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.AudioSeries.load_from_media",
        return_value=yuewen_audio_series,
    ):
        with patch(
            "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.get_yue_vs_zho_transcriber",
            return_value="transcriber",
        ):
            with patch(
                "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.get_yue_transcribed_vs_zho",
                return_value=expected_series,
            ):
                with patch("scinoephile.cli.helpers.io.stdout", stdout_stream):
                    run_cli_with_args(
                        YueTranscribeVsZhoCli,
                        f"--media-infile {media_infile_path} "
                        f"--zho-infile {zhongwen_infile_path}",
                    )

    output_series = Series.from_string(stdout_stream.getvalue(), format_="srt")
    assert_series_equal(output_series, expected_series)


def test_yue_transcribe_vs_zho_cli_rejects_removed_convert_flag():
    """Test written Cantonese CLI rejects the removed conversion option."""
    zhongwen_infile_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"
    with raises(SystemExit, match="2"):
        run_cli_with_args(
            YueTranscribeVsZhoCli,
            f"--media-infile {media_infile_path} "
            f"--zho-infile {zhongwen_infile_path} --convert hk2s",
        )


def test_yue_transcribe_vs_zho_cli_uses_selected_prompt_script():
    """Test written Cantonese CLI uses prompts for the selected script."""
    zhongwen_infile_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"
    expected_series = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n你好\n",
        format_="srt",
    )
    yuewen_audio_series = Mock(spec=AudioSeries)

    def get_transcriber(
        *,
        model_name: str,
        demucs_mode: object,
        vad_mode: object,
        provider: object,
        delineation_prompt: DelineationPrompt,
        punctuation_prompt: PunctuationPrompt,
        additional_context: str | None,
    ) -> str:
        """Validate prompt script options passed by the CLI."""
        assert model_name == DEFAULT_YUE_WHISPER_MODEL_NAME
        assert demucs_mode is not None
        assert vad_mode is not None
        assert provider is not None
        assert delineation_prompt is YueDelineationVsZhoPromptYueHant
        assert punctuation_prompt is YuePunctuationVsZhoPromptYueHant
        assert additional_context is None
        return "transcriber"

    with patch(
        "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.AudioSeries.load_from_media",
        return_value=yuewen_audio_series,
    ):
        with patch(
            "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.get_yue_vs_zho_transcriber",
            side_effect=get_transcriber,
        ):
            with patch(
                "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.get_yue_transcribed_vs_zho",
                return_value=expected_series,
            ):
                run_cli_with_args(
                    YueTranscribeVsZhoCli,
                    f"--media-infile {media_infile_path} "
                    f"--zho-infile {zhongwen_infile_path} "
                    "--script traditional",
                )


def test_yue_transcribe_vs_zho_cli_rejects_negative_stream_index():
    """Test written Cantonese transcribe-vs-zho CLI rejects negative stream indexes."""
    zhongwen_infile_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"
    with raises(SystemExit, match="2"):
        run_cli_with_args(
            YueTranscribeVsZhoCli,
            f"--media-infile {media_infile_path} "
            f"--zho-infile {zhongwen_infile_path} --stream-index -1",
        )


def test_yue_transcribe_vs_zho_cli_stream_errors_are_user_facing():
    """Test written Cantonese transcribe-vs-zho CLI surfaces stream-selection errors."""
    zhongwen_infile_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"
    with patch(
        "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.AudioSeries.load_from_media",
        side_effect=ScinoephileError("No stream index 7 found"),
    ):
        with raises(SystemExit, match="2"):
            run_cli_with_args(
                YueTranscribeVsZhoCli,
                f"--media-infile {media_infile_path} "
                f"--zho-infile {zhongwen_infile_path} --stream-index 7",
            )


def test_yue_transcribe_vs_zho_cli_rejects_missing_subtitle_infile():
    """Test written Cantonese CLI surfaces missing subtitle infiles."""
    media_infile_path = "/tmp/test_media.mp4"
    zhongwen_infile_path = "/tmp/missing_subtitles.srt"

    with raises(SystemExit, match="2"):
        run_cli_with_args(
            YueTranscribeVsZhoCli,
            f"--media-infile {media_infile_path} --zho-infile {zhongwen_infile_path}",
        )


def test_yue_transcribe_vs_zho_cli_rejects_missing_media_infile():
    """Test written Cantonese transcribe-vs-zho CLI surfaces missing media infiles."""
    zhongwen_infile_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"
    media_infile_path = "/tmp/missing_media.mp4"

    with raises(SystemExit, match="2"):
        run_cli_with_args(
            YueTranscribeVsZhoCli,
            f"--media-infile {media_infile_path} --zho-infile {zhongwen_infile_path}",
        )


def test_yue_transcribe_vs_zho_cli_allows_stdin_subtitle_infile():
    """Test written Cantonese transcribe-vs-zho CLI allows stdin subtitle input."""
    zhongwen_infile_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"
    expected_series = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n你好\n",
        format_="srt",
    )
    yuewen_audio_series = Mock(spec=AudioSeries)
    stdout_stream = StringIO()
    stdin_stream = StringIO(zhongwen_infile_path.read_text(encoding="utf-8"))
    yuewen_inputs: list[AudioSeries] = []
    zhongwen_inputs: list[Series] = []
    media_paths: list[str] = []
    subtitle_paths: list[object] = []

    def load_from_media(
        *,
        media_path: str,
        subtitle_path: object,
        stream_index: int | None,
    ) -> AudioSeries:
        """Record media loading inputs."""
        assert stream_index is None
        media_paths.append(media_path)
        subtitle_paths.append(subtitle_path)
        return yuewen_audio_series

    def get_transcribed_vs_zho(
        *,
        yuewen: AudioSeries,
        zhongwen: Series,
        transcriber: str,
    ) -> Series:
        """Record transcription inputs."""
        assert transcriber == "transcriber"
        yuewen_inputs.append(yuewen)
        zhongwen_inputs.append(zhongwen)
        return expected_series

    with patch("scinoephile.cli.helpers.io.stdin", stdin_stream):
        with patch(
            "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.AudioSeries.load_from_media",
            side_effect=load_from_media,
        ):
            with patch(
                "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.get_yue_vs_zho_transcriber",
                return_value="transcriber",
            ):
                with patch(
                    "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.get_yue_transcribed_vs_zho",
                    side_effect=get_transcribed_vs_zho,
                ):
                    with patch("scinoephile.cli.helpers.io.stdout", stdout_stream):
                        run_cli_with_args(
                            YueTranscribeVsZhoCli,
                            f"--media-infile {media_infile_path} --zho-infile -",
                        )

    assert yuewen_inputs == [yuewen_audio_series]
    assert_series_equal(zhongwen_inputs[0], Series.load(zhongwen_infile_path))
    assert media_paths == [media_infile_path]
    assert subtitle_paths != ["-"]
    output_series = Series.from_string(stdout_stream.getvalue(), format_="srt")
    assert_series_equal(output_series, expected_series)


def test_yue_transcribe_vs_zho_cli_rejects_two_stdin_infiles():
    """Test written Cantonese transcribe-vs-zho CLI rejects stdin for both inputs."""
    with raises(SystemExit, match="2"):
        run_cli_with_args(
            YueTranscribeVsZhoCli,
            "--media-infile - --zho-infile -",
        )


def test_yue_transcribe_vs_zho_cli_rejects_overwrite_without_outfile():
    """Test written Cantonese CLI rejects overwrite when writing to stdout."""
    zhongwen_infile_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"

    with raises(SystemExit, match="2"):
        run_cli_with_args(
            YueTranscribeVsZhoCli,
            f"--media-infile {media_infile_path} "
            f"--zho-infile {zhongwen_infile_path} --overwrite",
        )


def test_yue_transcribe_vs_zho_cli_rejects_old_zhongwen_infile_flag():
    """Test written Cantonese CLI rejects the old Zhongwen infile flag."""
    zhongwen_infile_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"

    with raises(SystemExit, match="2"):
        run_cli_with_args(
            YueTranscribeVsZhoCli,
            f"--media-infile {media_infile_path} "
            f"--zhongwen-infile {zhongwen_infile_path}",
        )
