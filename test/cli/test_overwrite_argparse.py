#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of CLI overwrite argument parsing."""

from __future__ import annotations

from pathlib import Path

from scinoephile.cli.eng.eng_process_cli import EngProcessCli
from scinoephile.cli.multi.multi_timewarp_cli import MultiTimewarpCli
from scinoephile.cli.ocr.ocr_fuse_cli import OcrFuseCli
from scinoephile.cli.translate_cli import TranslateCli
from scinoephile.cli.yue.yue_process_cli import YueProcessCli
from scinoephile.cli.yue.yue_review_vs_zho_cli import YueReviewVsZhoCli
from scinoephile.cli.yue.yue_transcribe_vs_zho_cli import YueTranscribeVsZhoCli
from scinoephile.cli.zho.zho_process_cli import ZhoProcessCli
from scinoephile.common import CommandLineInterface
from test.helpers import parametrize


@parametrize(
    ("cli_class", "args_template"),
    [
        (
            EngProcessCli,
            [
                "--infile",
                "{infile}",
                "--clean",
                "--outfile",
                "{outfile}",
                "--overwrite",
            ],
        ),
        (
            ZhoProcessCli,
            [
                "--infile",
                "{infile}",
                "--clean",
                "--outfile",
                "{outfile}",
                "--overwrite",
            ],
        ),
        (
            YueProcessCli,
            [
                "--infile",
                "{infile}",
                "--clean",
                "--outfile",
                "{outfile}",
                "--overwrite",
            ],
        ),
        (
            TranslateCli,
            [
                "{infile}",
                "--target-language",
                "eng",
                "--outfile",
                "{outfile}",
                "--overwrite",
            ],
        ),
        (
            YueReviewVsZhoCli,
            [
                "--yue-infile",
                "{infile}",
                "--zho-infile",
                "{infile}",
                "--outfile",
                "{outfile}",
                "--overwrite",
            ],
        ),
        (
            YueTranscribeVsZhoCli,
            [
                "--media-infile",
                "{infile}",
                "--zho-infile",
                "{infile}",
                "--outfile",
                "{outfile}",
                "--overwrite",
            ],
        ),
        (
            MultiTimewarpCli,
            [
                "--anchor-infile",
                "{infile}",
                "--mobile-infile",
                "{infile}",
                "--outfile",
                "{outfile}",
                "--overwrite",
            ],
        ),
        (
            OcrFuseCli,
            [
                "--language",
                "eng",
                "--lens-infile",
                "{infile}",
                "--tesseract-infile",
                "{infile}",
                "--outfile",
                "{outfile}",
                "--overwrite",
            ],
        ),
    ],
    ids=[
        "eng-process",
        "zho-process",
        "yue-process",
        "translate",
        "yue-review-vs-zho",
        "yue-transcribe-vs-zho",
        "multi-timewarp",
        "ocr-fuse",
    ],
)
def test_overwrite_allows_existing_outfile_during_argument_parsing(
    tmp_path: Path,
    cli_class: type[CommandLineInterface],
    args_template: list[str],
):
    """Test overwrite-capable CLIs accept existing outfiles during parsing."""
    infile_path = tmp_path / "input.srt"
    outfile_path = tmp_path / "output.srt"
    infile_path.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\ninput\n", encoding="utf-8"
    )
    outfile_path.write_text("existing\n", encoding="utf-8")
    args = [
        arg.format(infile=str(infile_path), outfile=str(outfile_path))
        for arg in args_template
    ]

    namespace = cli_class.argparser().parse_args(args)

    assert namespace.outfile_path == outfile_path.resolve()
    assert namespace.overwrite is True
