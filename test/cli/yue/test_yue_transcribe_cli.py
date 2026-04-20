#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli Yue transcription CLIs."""

from __future__ import annotations

from io import StringIO
from unittest.mock import Mock, patch

import pytest

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.yue.yue_cli import YueCli
from scinoephile.cli.yue.yue_transcribe_cli import YueTranscribeCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series
from test.helpers import assert_cli_help, assert_cli_usage, test_data_root


@pytest.mark.parametrize(
    "cli",
    [
        (YueTranscribeCli,),
        (YueCli, YueTranscribeCli),
        (ScinoephileCli, YueCli, YueTranscribeCli),
    ],
)
def test_yue_transcribe_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test 粤文 transcription CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (YueTranscribeCli,),
        (YueCli, YueTranscribeCli),
        (ScinoephileCli, YueCli, YueTranscribeCli),
    ],
)
def test_yue_transcribe_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test 粤文 transcription CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


def test_yue_transcribe_cli_writes_file():
    """Test 粤文 transcription CLI writes file output and dispatches dependencies."""
    zhongwen_infile_path = test_data_root / "mnt" / "output" / "zho-Hans_fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"
    expected_series = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n你好\n",
        format_="srt",
    )
    yuewen_audio_series = Mock(spec=AudioSeries)

    with get_temp_file_path(".srt") as outfile_path:
        with patch(
            "scinoephile.cli.yue.yue_transcribe_cli.AudioSeries.load_from_media",
            return_value=yuewen_audio_series,
        ) as patched_loader:
            with patch(
                "scinoephile.cli.yue.yue_transcribe_cli.get_yue_transcribed_vs_zho",
                return_value=expected_series,
            ) as patched_transcribe:
                run_cli_with_args(
                    YueTranscribeCli,
                    f"--media-infile {media_infile_path} "
                    f"--zhongwen-infile {zhongwen_infile_path} "
                    f"--stream-index 1 -o {outfile_path}",
                )
        output_series = Series.load(outfile_path)

    called_kwargs = patched_transcribe.call_args.kwargs
    assert called_kwargs["yuewen"] == yuewen_audio_series
    assert called_kwargs["zhongwen"] == Series.load(zhongwen_infile_path)
    patched_loader.assert_called_once_with(
        media_path=media_infile_path,
        subtitle_path=zhongwen_infile_path,
        stream_index=1,
    )
    assert output_series == expected_series


def test_yue_transcribe_cli_writes_stdout():
    """Test 粤文 transcription CLI writes stdout output."""
    zhongwen_infile_path = test_data_root / "mnt" / "output" / "zho-Hans_fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"
    expected_series = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n你好\n",
        format_="srt",
    )
    yuewen_audio_series = Mock(spec=AudioSeries)
    stdout_stream = StringIO()

    with patch(
        "scinoephile.cli.yue.yue_transcribe_cli.AudioSeries.load_from_media",
        return_value=yuewen_audio_series,
    ):
        with patch(
            "scinoephile.cli.yue.yue_transcribe_cli.get_yue_transcribed_vs_zho",
            return_value=expected_series,
        ):
            with patch("scinoephile.core.cli.stdout", stdout_stream):
                run_cli_with_args(
                    YueTranscribeCli,
                    f"--media-infile {media_infile_path} "
                    f"--zhongwen-infile {zhongwen_infile_path}",
                )

    output_series = Series.from_string(stdout_stream.getvalue(), format_="srt")
    assert output_series == expected_series


def test_yue_transcribe_cli_rejects_negative_stream_index():
    """Test 粤文 transcription CLI rejects negative stream indexes."""
    zhongwen_infile_path = test_data_root / "mnt" / "output" / "zho-Hans_fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"
    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            YueTranscribeCli,
            f"--media-infile {media_infile_path} "
            f"--zhongwen-infile {zhongwen_infile_path} --stream-index -1",
        )


def test_yue_transcribe_cli_stream_errors_are_user_facing():
    """Test 粤文 transcription CLI surfaces stream-selection errors."""
    zhongwen_infile_path = test_data_root / "mnt" / "output" / "zho-Hans_fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"
    with patch(
        "scinoephile.cli.yue.yue_transcribe_cli.AudioSeries.load_from_media",
        side_effect=ScinoephileError("Invalid audio stream index 7"),
    ):
        with pytest.raises(SystemExit, match="2"):
            run_cli_with_args(
                YueTranscribeCli,
                f"--media-infile {media_infile_path} "
                f"--zhongwen-infile {zhongwen_infile_path} --stream-index 7",
            )


def test_yue_transcribe_cli_rejects_missing_subtitle_infile():
    """Test 粤文 transcription CLI surfaces missing subtitle infiles."""
    media_infile_path = "/tmp/test_media.mp4"
    zhongwen_infile_path = "/tmp/missing_subtitles.srt"

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            YueTranscribeCli,
            f"--media-infile {media_infile_path} "
            f"--zhongwen-infile {zhongwen_infile_path}",
        )


def test_yue_transcribe_cli_rejects_missing_media_infile():
    """Test 粤文 transcription CLI surfaces missing media infiles."""
    zhongwen_infile_path = test_data_root / "mnt" / "output" / "zho-Hans_fuse.srt"
    media_infile_path = "/tmp/missing_media.mp4"

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            YueTranscribeCli,
            f"--media-infile {media_infile_path} "
            f"--zhongwen-infile {zhongwen_infile_path}",
        )


def test_yue_transcribe_cli_allows_stdin_subtitle_infile():
    """Test 粤文 transcription CLI allows stdin subtitle input."""
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
            "scinoephile.cli.yue.yue_transcribe_cli.AudioSeries.load_from_media",
            return_value=yuewen_audio_series,
        ) as patched_loader:
            with patch(
                "scinoephile.cli.yue.yue_transcribe_cli.get_yue_transcribed_vs_zho",
                return_value=expected_series,
            ) as patched_transcribe:
                with patch("scinoephile.core.cli.stdout", stdout_stream):
                    run_cli_with_args(
                        YueTranscribeCli,
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


def test_yue_transcribe_cli_rejects_two_stdin_infiles():
    """Test 粤文 transcription CLI rejects stdin for both inputs."""
    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            YueTranscribeCli,
            "--media-infile - --zhongwen-infile -",
        )


def test_yue_transcribe_cli_rejects_overwrite_without_outfile():
    """Test 粤文 transcription CLI rejects overwrite when writing to stdout."""
    zhongwen_infile_path = test_data_root / "mnt" / "output" / "zho-Hans_fuse.srt"
    media_infile_path = "/tmp/test_media.mp4"

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            YueTranscribeCli,
            f"--media-infile {media_infile_path} "
            f"--zhongwen-infile {zhongwen_infile_path} --overwrite",
        )
