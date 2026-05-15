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


def test_eng_translate_vs_zho_cli_regular_translation():
    """Test English translate-vs-zho CLI routes to regular translation."""
    zho_input_path = test_data_root / (
        "mnt/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )
    expected_path = test_data_root / "mnt/output/eng_ocr/fuse_clean_validate_review.srt"
    expected = Series.load(expected_path)

    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.eng.eng_translate_vs_zho_cli.get_eng_zho_translator",
            return_value="translator",
        ) as patched_factory:
            with patch(
                "scinoephile.cli.eng.eng_translate_vs_zho_cli.get_eng_translated_from_zho",
                return_value=expected,
            ) as patched_translate:
                run_cli_with_args(
                    EngTranslateVsZhoCli,
                    f"--zho-infile {zho_input_path} --outfile {output_path}",
                )
        output = Series.load(output_path)

    assert patched_factory.call_args.kwargs["provider"] is not None
    called_kwargs = patched_translate.call_args.kwargs
    assert_series_equal(called_kwargs["zho"], Series.load(zho_input_path))
    assert called_kwargs["translator"] == "translator"
    assert_series_equal(output, expected)


def test_eng_translate_vs_zho_cli_gapped_translation():
    """Test English translate-vs-zho CLI routes to gapped translation."""
    eng_input_path = test_data_root / "mnt/output/eng_ocr/fuse_clean_validate.srt"
    zho_input_path = test_data_root / (
        "mnt/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )
    expected_path = test_data_root / "mnt/output/eng_ocr/fuse_clean_validate_review.srt"
    expected = Series.load(expected_path)

    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.eng.eng_translate_vs_zho_cli."
            "get_eng_vs_zho_gapped_translator",
            return_value="translator",
        ) as patched_factory:
            with patch(
                "scinoephile.cli.eng.eng_translate_vs_zho_cli."
                "get_eng_gapped_translated_vs_zho",
                return_value=expected,
            ) as patched_translate:
                run_cli_with_args(
                    EngTranslateVsZhoCli,
                    f"--zho-infile {zho_input_path} "
                    f"--eng-gapped-infile {eng_input_path} "
                    f"--outfile {output_path}",
                )
        output = Series.load(output_path)

    assert patched_factory.call_args.kwargs["provider"] is not None
    called_kwargs = patched_translate.call_args.kwargs
    assert_series_equal(called_kwargs["eng"], Series.load(eng_input_path))
    assert_series_equal(called_kwargs["zho"], Series.load(zho_input_path))
    assert called_kwargs["translator"] == "translator"
    assert_series_equal(output, expected)


def test_eng_translate_vs_zho_cli_guided_translation():
    """Test English translate-vs-zho CLI routes to guided translation."""
    eng_input_path = test_data_root / "mnt/output/eng_ocr/fuse_clean_validate.srt"
    zho_input_path = test_data_root / (
        "mnt/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )
    expected_path = test_data_root / "mnt/output/eng_ocr/fuse_clean_validate_review.srt"
    expected = Series.load(expected_path)

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
                    f"--zho-infile {zho_input_path} "
                    f"--eng-guide-infile {eng_input_path} "
                    f"--outfile {output_path}",
                )
        output = Series.load(output_path)

    assert patched_factory.call_args.kwargs["provider"] is not None
    called_kwargs = patched_translate.call_args.kwargs
    assert_series_equal(called_kwargs["zho"], Series.load(zho_input_path))
    assert_series_equal(called_kwargs["eng"], Series.load(eng_input_path))
    assert called_kwargs["translator"] == "translator"
    assert_series_equal(output, expected)


def test_eng_translate_vs_zho_cli_rejects_gapped_and_guide_together():
    """Test English translate-vs-zho CLI rejects mutually exclusive inputs."""
    eng_input_path = test_data_root / "mnt/output/eng_ocr/fuse_clean_validate.srt"
    zho_input_path = test_data_root / (
        "mnt/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            EngTranslateVsZhoCli,
            f"--zho-infile {zho_input_path} "
            f"--eng-gapped-infile {eng_input_path} "
            f"--eng-guide-infile {eng_input_path}",
        )
