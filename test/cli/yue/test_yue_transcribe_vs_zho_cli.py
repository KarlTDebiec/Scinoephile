#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.yue.yue_transcribe_vs_zho_cli."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from unittest.mock import Mock, patch

import pytest

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.yue.yue_cli import YueCli
from scinoephile.cli.yue.yue_transcribe_vs_zho_cli import YueTranscribeVsZhoCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.lang.zho.conversion import OpenCCConfig
from scinoephile.multilang.yue_zho.transcription import DemucsMode, VADMode
from scinoephile.multilang.yue_zho.transcription.deliniation import (
    YueZhoHansDeliniationPrompt,
    YueZhoHantDeliniationPrompt,
)
from scinoephile.multilang.yue_zho.transcription.punctuation import (
    YueZhoHansPunctuationPrompt,
    YueZhoHantPunctuationPrompt,
)
from test.helpers import assert_cli_help, assert_cli_usage, test_data_root


@pytest.mark.parametrize(
    "cli",
    [
        (YueTranscribeVsZhoCli,),
        (YueCli, YueTranscribeVsZhoCli),
        (ScinoephileCli, YueCli, YueTranscribeVsZhoCli),
    ],
)
def test_yue_transcribe_vs_zho_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test 粤文 transcribe-vs-zho CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (YueTranscribeVsZhoCli,),
        (YueCli, YueTranscribeVsZhoCli),
        (ScinoephileCli, YueCli, YueTranscribeVsZhoCli),
    ],
)
def test_yue_transcribe_vs_zho_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test 粤文 transcribe-vs-zho CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


def test_yue_transcribe_vs_zho_help_lists_script_convert_demucs_and_vad_options():
    """Test 粤文 transcribe-vs-zho CLI help lists prompt and conversion options."""
    stdout = StringIO()
    stderr = StringIO()

    with pytest.raises(SystemExit, match="0"):
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(YueTranscribeVsZhoCli, "-h")

    help_text = stdout.getvalue()
    normalized_help_text = " ".join(help_text.split())
    assert stderr.getvalue() == ""
    assert "--script SCRIPT" in help_text
    assert "script used for transcription prompts" in help_text
    assert "--convert CONVERT" in normalized_help_text
    assert (
        "convert transcribed Chinese characters using specified OpenCC "
        "configuration" in normalized_help_text
    )
    assert "--demucs DEMUCS" in help_text
    assert "Demucs vocal-separation mode" in help_text
    assert "options: on, off;" in help_text
    assert "default: off" in help_text
    assert "--vad VAD" in help_text
    assert "Whisper voice activity detection mode" in help_text
    assert "off, auto; default: auto" in help_text


def test_yue_transcribe_vs_zho_cli_writes_file():
    """Test 粤文 transcribe-vs-zho CLI writes file output.

    Also verifies dependency dispatch.
    """
    zhongwen_infile_path = test_data_root / "mnt" / "output" / "zho-Hans_fuse.srt"
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
        ) as patched_loader:
            with patch(
                "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.get_yue_vs_zho_transcriber",
                return_value="transcriber",
            ) as patched_factory:
                with patch(
                    "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.get_yue_transcribed_vs_zho",
                    return_value=expected_series,
                ) as patched_transcribe:
                    run_cli_with_args(
                        YueTranscribeVsZhoCli,
                        f"--media-infile {media_infile_path} "
                        f"--zhongwen-infile {zhongwen_infile_path} "
                        f"--stream-index 1 -o {outfile_path}",
                    )
        output_series = Series.load(outfile_path)

    assert (
        patched_factory.call_args.kwargs["deliniation_prompt_cls"]
        is YueZhoHansDeliniationPrompt
    )
    assert (
        patched_factory.call_args.kwargs["punctuation_prompt_cls"]
        is YueZhoHansPunctuationPrompt
    )
    assert patched_factory.call_args.kwargs["convert"] is None
    assert patched_factory.call_args.kwargs["demucs_mode"] == DemucsMode.OFF
    assert patched_factory.call_args.kwargs["vad_mode"] == VADMode.AUTO
    called_kwargs = patched_transcribe.call_args.kwargs
    assert called_kwargs["yuewen"] == yuewen_audio_series
    assert called_kwargs["zhongwen"] == Series.load(zhongwen_infile_path)
    assert called_kwargs["transcriber"] == "transcriber"
    patched_loader.assert_called_once_with(
        media_path=media_infile_path,
        subtitle_path=zhongwen_infile_path,
        stream_index=1,
    )
    assert output_series == expected_series


def test_yue_transcribe_vs_zho_cli_writes_stdout():
    """Test 粤文 transcribe-vs-zho CLI writes stdout output."""
    zhongwen_infile_path = test_data_root / "mnt" / "output" / "zho-Hans_fuse.srt"
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
                with patch("scinoephile.core.cli.stdout", stdout_stream):
                    run_cli_with_args(
                        YueTranscribeVsZhoCli,
                        f"--media-infile {media_infile_path} "
                        f"--zhongwen-infile {zhongwen_infile_path}",
                    )

    output_series = Series.from_string(stdout_stream.getvalue(), format_="srt")
    assert output_series == expected_series


def test_yue_transcribe_vs_zho_cli_passes_requested_vad_mode():
    """Test 粤文 transcribe-vs-zho CLI passes through explicit VAD mode."""
    zhongwen_infile_path = test_data_root / "mnt" / "output" / "zho-Hans_fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"
    expected_series = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n你好\n",
        format_="srt",
    )
    yuewen_audio_series = Mock(spec=AudioSeries)

    with patch(
        "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.AudioSeries.load_from_media",
        return_value=yuewen_audio_series,
    ):
        with patch(
            "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.get_yue_vs_zho_transcriber",
            return_value="transcriber",
        ) as patched_factory:
            with patch(
                "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.get_yue_transcribed_vs_zho",
                return_value=expected_series,
            ):
                run_cli_with_args(
                    YueTranscribeVsZhoCli,
                    f"--media-infile {media_infile_path} "
                    f"--zhongwen-infile {zhongwen_infile_path} --vad off",
                )

    assert patched_factory.call_args.kwargs["vad_mode"] == VADMode.OFF


def test_yue_transcribe_vs_zho_cli_passes_requested_demucs_mode():
    """Test 粤文 transcribe-vs-zho CLI passes through explicit Demucs mode."""
    zhongwen_infile_path = test_data_root / "mnt" / "output" / "zho-Hans_fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"
    expected_series = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n你好\n",
        format_="srt",
    )
    yuewen_audio_series = Mock(spec=AudioSeries)

    with patch(
        "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.AudioSeries.load_from_media",
        return_value=yuewen_audio_series,
    ):
        with patch(
            "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.get_yue_vs_zho_transcriber",
            return_value="transcriber",
        ) as patched_factory:
            with patch(
                "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.get_yue_transcribed_vs_zho",
                return_value=expected_series,
            ):
                run_cli_with_args(
                    YueTranscribeVsZhoCli,
                    f"--media-infile {media_infile_path} "
                    f"--zhongwen-infile {zhongwen_infile_path} --demucs on",
                )

    assert patched_factory.call_args.kwargs["demucs_mode"] == DemucsMode.ON


def test_yue_transcribe_vs_zho_cli_passes_requested_convert():
    """Test 粤文 transcribe-vs-zho CLI passes through explicit conversion."""
    zhongwen_infile_path = test_data_root / "mnt" / "output" / "zho-Hans_fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"
    expected_series = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n你好\n",
        format_="srt",
    )
    yuewen_audio_series = Mock(spec=AudioSeries)

    with patch(
        "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.AudioSeries.load_from_media",
        return_value=yuewen_audio_series,
    ):
        with patch(
            "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.get_yue_vs_zho_transcriber",
            return_value="transcriber",
        ) as patched_factory:
            with patch(
                "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.get_yue_transcribed_vs_zho",
                return_value=expected_series,
            ):
                run_cli_with_args(
                    YueTranscribeVsZhoCli,
                    f"--media-infile {media_infile_path} "
                    f"--zhongwen-infile {zhongwen_infile_path} --convert s2hk",
                )

    assert patched_factory.call_args.kwargs["convert"] == OpenCCConfig.s2hk


def test_yue_transcribe_vs_zho_cli_rejects_bare_convert_flag():
    """Test 粤文 transcribe-vs-zho CLI requires an explicit conversion config."""
    zhongwen_infile_path = test_data_root / "mnt" / "output" / "zho-Hans_fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"
    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            YueTranscribeVsZhoCli,
            f"--media-infile {media_infile_path} "
            f"--zhongwen-infile {zhongwen_infile_path} --convert",
        )


def test_yue_transcribe_vs_zho_cli_keeps_script_and_convert_independent():
    """Test 粤文 transcribe-vs-zho CLI keeps prompt script separate from conversion."""
    zhongwen_infile_path = test_data_root / "mnt" / "output" / "zho-Hans_fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"
    expected_series = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n你好\n",
        format_="srt",
    )
    yuewen_audio_series = Mock(spec=AudioSeries)

    with patch(
        "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.AudioSeries.load_from_media",
        return_value=yuewen_audio_series,
    ):
        with patch(
            "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.get_yue_vs_zho_transcriber",
            return_value="transcriber",
        ) as patched_factory:
            with patch(
                "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.get_yue_transcribed_vs_zho",
                return_value=expected_series,
            ):
                run_cli_with_args(
                    YueTranscribeVsZhoCli,
                    f"--media-infile {media_infile_path} "
                    f"--zhongwen-infile {zhongwen_infile_path} "
                    "--script traditional --convert hk2s",
                )

    assert (
        patched_factory.call_args.kwargs["deliniation_prompt_cls"]
        is YueZhoHantDeliniationPrompt
    )
    assert (
        patched_factory.call_args.kwargs["punctuation_prompt_cls"]
        is YueZhoHantPunctuationPrompt
    )
    assert patched_factory.call_args.kwargs["convert"] == OpenCCConfig.hk2s


def test_yue_transcribe_vs_zho_cli_rejects_negative_stream_index():
    """Test 粤文 transcribe-vs-zho CLI rejects negative stream indexes."""
    zhongwen_infile_path = test_data_root / "mnt" / "output" / "zho-Hans_fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"
    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            YueTranscribeVsZhoCli,
            f"--media-infile {media_infile_path} "
            f"--zhongwen-infile {zhongwen_infile_path} --stream-index -1",
        )


def test_yue_transcribe_vs_zho_cli_stream_errors_are_user_facing():
    """Test 粤文 transcribe-vs-zho CLI surfaces stream-selection errors."""
    zhongwen_infile_path = test_data_root / "mnt" / "output" / "zho-Hans_fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"
    with patch(
        "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.AudioSeries.load_from_media",
        side_effect=ScinoephileError("Invalid audio stream index 7"),
    ):
        with pytest.raises(SystemExit, match="2"):
            run_cli_with_args(
                YueTranscribeVsZhoCli,
                f"--media-infile {media_infile_path} "
                f"--zhongwen-infile {zhongwen_infile_path} --stream-index 7",
            )


def test_yue_transcribe_vs_zho_cli_rejects_missing_subtitle_infile():
    """Test 粤文 transcribe-vs-zho CLI surfaces missing subtitle infiles."""
    media_infile_path = "/tmp/test_media.mp4"
    zhongwen_infile_path = "/tmp/missing_subtitles.srt"

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            YueTranscribeVsZhoCli,
            f"--media-infile {media_infile_path} "
            f"--zhongwen-infile {zhongwen_infile_path}",
        )


def test_yue_transcribe_vs_zho_cli_rejects_missing_media_infile():
    """Test 粤文 transcribe-vs-zho CLI surfaces missing media infiles."""
    zhongwen_infile_path = test_data_root / "mnt" / "output" / "zho-Hans_fuse.srt"
    media_infile_path = "/tmp/missing_media.mp4"

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            YueTranscribeVsZhoCli,
            f"--media-infile {media_infile_path} "
            f"--zhongwen-infile {zhongwen_infile_path}",
        )


def test_yue_transcribe_vs_zho_cli_allows_stdin_subtitle_infile():
    """Test 粤文 transcribe-vs-zho CLI allows stdin subtitle input."""
    zhongwen_infile_path = test_data_root / "mnt" / "output" / "zho-Hans_fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"
    expected_series = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n你好\n",
        format_="srt",
    )
    yuewen_audio_series = Mock(spec=AudioSeries)
    stdout_stream = StringIO()
    stdin_stream = StringIO(zhongwen_infile_path.read_text())

    with patch("scinoephile.core.cli.stdin", stdin_stream):
        with patch(
            "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.AudioSeries.load_from_media",
            return_value=yuewen_audio_series,
        ) as patched_loader:
            with patch(
                "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.get_yue_vs_zho_transcriber",
                return_value="transcriber",
            ):
                with patch(
                    "scinoephile.cli.yue.yue_transcribe_vs_zho_cli.get_yue_transcribed_vs_zho",
                    return_value=expected_series,
                ) as patched_transcribe:
                    with patch("scinoephile.core.cli.stdout", stdout_stream):
                        run_cli_with_args(
                            YueTranscribeVsZhoCli,
                            f"--media-infile {media_infile_path} --zhongwen-infile -",
                        )

    called_kwargs = patched_transcribe.call_args.kwargs
    assert called_kwargs["yuewen"] == yuewen_audio_series
    assert called_kwargs["zhongwen"] == Series.load(zhongwen_infile_path)
    patched_loader.assert_called_once()
    assert patched_loader.call_args.kwargs["media_path"] == media_infile_path
    assert patched_loader.call_args.kwargs["subtitle_path"] != "-"
    output_series = Series.from_string(stdout_stream.getvalue(), format_="srt")
    assert output_series == expected_series


def test_yue_transcribe_vs_zho_cli_rejects_two_stdin_infiles():
    """Test 粤文 transcribe-vs-zho CLI rejects stdin for both inputs."""
    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            YueTranscribeVsZhoCli,
            "--media-infile - --zhongwen-infile -",
        )


def test_yue_transcribe_vs_zho_cli_rejects_overwrite_without_outfile():
    """Test 粤文 transcribe-vs-zho CLI rejects overwrite when writing to stdout."""
    zhongwen_infile_path = test_data_root / "mnt" / "output" / "zho-Hans_fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            YueTranscribeVsZhoCli,
            f"--media-infile {media_infile_path} "
            f"--zhongwen-infile {zhongwen_infile_path} --overwrite",
        )
