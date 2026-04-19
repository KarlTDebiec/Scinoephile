#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli Yue transcription CLIs."""

from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest

from scinoephile.cli import ScinoephileCli, YueCli, YueTranscribeCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series
from test.helpers import assert_cli_help, assert_cli_usage, test_data_root


@pytest.mark.parametrize(
    "cli",
    [
        (YueCli,),
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
        (YueCli,),
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
    """Test 粤文 transcription CLI writes file output and dispatches media args."""
    zhongwen_infile_path = test_data_root / "mnt" / "output" / "zho-Hans_fuse.srt"
    media_path = "/tmp/test_media.mp4"
    expected = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n你好\n",
        format_="srt",
    )

    with get_temp_file_path(".srt") as outfile_path:
        with patch(
            "scinoephile.cli.yue_transcribe_cli.get_yue_vs_zho_transcribed",
            return_value=expected,
        ) as patched_transcribe:
            run_cli_with_args(
                YueTranscribeCli,
                f"{zhongwen_infile_path} "
                f"{media_path} --stream-index 1 -o {outfile_path}",
            )
        output = Series.load(outfile_path)

    called_kwargs = patched_transcribe.call_args.kwargs
    assert called_kwargs["stream_index"] == 1
    assert called_kwargs["media_path"] == media_path
    assert called_kwargs["zhongwen"] == Series.load(zhongwen_infile_path)
    assert output == expected


def test_yue_transcribe_cli_writes_stdout():
    """Test 粤文 transcription CLI writes stdout output."""
    zhongwen_infile_path = test_data_root / "mnt" / "output" / "zho-Hans_fuse.srt"
    media_path = "/tmp/test_media.mp4"
    expected = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n你好\n",
        format_="srt",
    )
    stdout_stream = StringIO()

    with patch(
        "scinoephile.cli.yue_transcribe_cli.get_yue_vs_zho_transcribed",
        return_value=expected,
    ):
        with patch("scinoephile.cli.yue_transcribe_cli.stdout", stdout_stream):
            run_cli_with_args(YueTranscribeCli, f"{zhongwen_infile_path} {media_path}")

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    assert output == expected


def test_yue_transcribe_cli_rejects_negative_stream_index():
    """Test 粤文 transcription CLI rejects negative stream indexes."""
    zhongwen_infile_path = test_data_root / "mnt" / "output" / "zho-Hans_fuse.srt"
    media_path = "/tmp/test_media.mp4"
    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            YueTranscribeCli,
            f"{zhongwen_infile_path} {media_path} --stream-index -1",
        )


def test_yue_transcribe_cli_stream_errors_are_user_facing():
    """Test 粤文 transcription CLI surfaces stream-selection errors."""
    zhongwen_infile_path = test_data_root / "mnt" / "output" / "zho-Hans_fuse.srt"
    media_path = "/tmp/test_media.mp4"
    with patch(
        "scinoephile.cli.yue_transcribe_cli.get_yue_vs_zho_transcribed",
        side_effect=ScinoephileError("Invalid audio stream index 7"),
    ):
        with pytest.raises(SystemExit, match="2"):
            run_cli_with_args(
                YueTranscribeCli,
                f"{zhongwen_infile_path} {media_path} --stream-index 7",
            )
