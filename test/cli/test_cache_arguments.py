#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for shared cache arguments across cache-producing CLIs."""

from __future__ import annotations

from argparse import ArgumentParser

from scinoephile.cli.dictionary.build.dictionary_build_cuhk_cli import (
    DictionaryBuildCuhkCli,
)
from scinoephile.cli.media.media_extract_subs_cli import MediaExtractSubsCli
from scinoephile.cli.media.media_probe_cli import MediaProbeCli
from scinoephile.cli.ocr.ocr_fuse_cli import OcrFuseCli
from scinoephile.cli.ocr.ocr_lens_cli import OcrLensCli
from scinoephile.cli.ocr.ocr_paddle_cli import OcrPaddleCli
from scinoephile.cli.ocr.ocr_process_cli import OcrProcessCli
from scinoephile.cli.ocr.ocr_tesseract_cli import OcrTesseractCli
from scinoephile.cli.review_cli import ReviewCli
from scinoephile.cli.transcribe_cli import TranscribeCli
from scinoephile.cli.translate_cli import TranslateCli
from scinoephile.core.cli import ScinoephileCliBase
from test.helpers import parametrize


@parametrize(
    "cli",
    (
        DictionaryBuildCuhkCli,
        MediaExtractSubsCli,
        MediaProbeCli,
        OcrFuseCli,
        OcrLensCli,
        OcrPaddleCli,
        OcrProcessCli,
        OcrTesseractCli,
        ReviewCli,
        TranscribeCli,
        TranslateCli,
    ),
)
def test_cache_producing_cli_uses_shared_cache_arguments(
    cli: type[ScinoephileCliBase],
):
    """Test each cache-producing CLI exposes one shared cache section.

    Arguments:
        cli: CLI class under test
    """
    parser: ArgumentParser = cli.argparser()
    cache_groups = [
        group
        for group in parser._action_groups  # noqa: SLF001
        if group.title == "cache arguments"
    ]
    assert len(cache_groups) == 1
    option_strings = {
        option
        for action in cache_groups[0]._group_actions  # noqa: SLF001
        for option in action.option_strings
    }
    assert option_strings == {"--cache-dir", "--cache-overwrite"}
    assert "--overwrite-cache" not in parser.format_help()
