#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.zho.zho_translate_from_eng_cli."""

from __future__ import annotations

from unittest.mock import patch

from pytest import raises

from scinoephile.cli.zho.zho_translate_from_eng_cli import ZhoTranslateFromEngCli
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from test.helpers import (
    assert_series_equal,
    test_data_root,
)


def test_zho_translate_from_eng_cli_regular_translation():
    """Test standard Chinese translate-from-eng CLI routes to regular translation."""
    eng_input_path = test_data_root / "mlamd/output/eng_ocr/fuse_clean_validate.srt"
    expected_path = test_data_root / "mlamd/output/zho-Hans_ocr/fuse_clean_validate.srt"
    expected = Series.load(expected_path)

    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.zho.zho_translate_from_eng_cli.get_zho_eng_translator",
            return_value="translator",
        ):
            with patch(
                "scinoephile.cli.zho.zho_translate_from_eng_cli."
                "get_zho_translated_from_eng",
                return_value=expected,
            ):
                run_cli_with_args(
                    ZhoTranslateFromEngCli,
                    f"--eng-infile {eng_input_path} --outfile {output_path}",
                )
        output = Series.load(output_path)

    assert_series_equal(output, expected)


def test_zho_translate_from_eng_cli_rejects_gapped_and_guide_together():
    """Test standard Chinese translate-from-eng CLI rejects conflicts."""
    eng_input_path = test_data_root / "mlamd/output/eng_ocr/fuse_clean_validate.srt"
    zho_input_path = test_data_root / (
        "mlamd/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )

    with raises(SystemExit, match="2"):
        run_cli_with_args(
            ZhoTranslateFromEngCli,
            f"--eng-infile {eng_input_path} "
            f"--zho-gapped-infile {zho_input_path} "
            f"--zho-guide-infile {zho_input_path}",
        )

