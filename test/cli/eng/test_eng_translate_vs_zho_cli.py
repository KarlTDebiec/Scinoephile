#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.eng.eng_translate_vs_zho_cli."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from scinoephile.cli.eng.eng_cli import EngCli
from scinoephile.cli.eng.eng_translate_vs_zho_cli import EngTranslateVsZhoCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from test.helpers import (
    assert_cli_help,
    assert_cli_usage,
    assert_series_equal,
    test_data_root,
)


@pytest.mark.parametrize(
    "cli",
    [
        (EngTranslateVsZhoCli,),
        (EngCli, EngTranslateVsZhoCli),
        (ScinoephileCli, EngCli, EngTranslateVsZhoCli),
    ],
)
def test_eng_translate_vs_zho_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test English translate-vs-zho CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (EngTranslateVsZhoCli,),
        (EngCli, EngTranslateVsZhoCli),
        (ScinoephileCli, EngCli, EngTranslateVsZhoCli),
    ],
)
def test_eng_translate_vs_zho_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test English translate-vs-zho CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


def test_eng_translate_vs_zho_cli():
    """Test English translate-vs-zho CLI with file arguments."""
    eng_input_path = test_data_root / "mlamd/output/eng_ocr/fuse_clean_validate.srt"
    zho_input_path = test_data_root / "mlamd/output/zho-Hans_ocr/fuse_clean.srt"
    expected = Series.load(test_data_root / "mlamd/output/eng_ocr/fuse_clean.srt")

    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.eng.eng_translate_vs_zho_cli."
            "get_eng_zho_guided_translator",
            return_value="translator",
        ) as patched_factory:
            with patch(
                "scinoephile.cli.eng.eng_translate_vs_zho_cli."
                "get_eng_translated_from_zho_with_eng_guidance",
                return_value=expected,
            ) as patched_translate:
                run_cli_with_args(
                    EngTranslateVsZhoCli,
                    f"--eng-infile {eng_input_path} --zho-infile {zho_input_path} "
                    f"--stop-at-idx 3 --outfile {output_path}",
                )
        output = Series.load(output_path)

    patched_factory.assert_called_once_with()
    called_kwargs = patched_translate.call_args.kwargs
    assert_series_equal(called_kwargs["eng"], Series.load(eng_input_path))
    assert_series_equal(called_kwargs["zho"], Series.load(zho_input_path))
    assert called_kwargs["translator"] == "translator"
    assert called_kwargs["stop_at_idx"] == 3
    assert_series_equal(output, expected)
