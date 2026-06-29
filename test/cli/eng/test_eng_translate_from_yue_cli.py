#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.eng.eng_translate_from_yue_cli."""

from __future__ import annotations

from unittest.mock import patch

from pytest import raises

from scinoephile.cli.eng.eng_translate_from_yue_cli import EngTranslateFromYueCli
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from test.helpers import (
    assert_series_equal,
    test_data_root,
)


def test_eng_translate_from_yue_cli_regular_translation():
    """Test English translate-from-yue CLI routes to regular translation."""
    yue_input_path = (
        test_data_root / "mlamd/output/yue-Hans_transcribe/transcribe_review.srt"
    )
    expected_path = test_data_root / "mlamd/output/yue-Hans_eng.srt"
    expected = Series.load(expected_path)

    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.eng.eng_translate_from_yue_cli.get_eng_yue_translator",
            return_value="translator",
        ):
            with patch(
                "scinoephile.cli.eng.eng_translate_from_yue_cli."
                "get_eng_translated_from_yue",
                return_value=expected,
            ):
                run_cli_with_args(
                    EngTranslateFromYueCli,
                    f"--yue-infile {yue_input_path} --outfile {output_path}",
                )
        output = Series.load(output_path)

    assert_series_equal(output, expected)


def test_eng_translate_from_yue_cli_rejects_gapped_and_guide_together():
    """Test English translate-from-yue CLI rejects mutually exclusive inputs."""
    eng_input_path = test_data_root / "mlamd/output/eng_ocr/fuse_clean_validate.srt"
    yue_input_path = (
        test_data_root / "mlamd/output/yue-Hans_transcribe/transcribe_review.srt"
    )

    with raises(SystemExit, match="2"):
        run_cli_with_args(
            EngTranslateFromYueCli,
            f"--yue-infile {yue_input_path} "
            f"--eng-gapped-infile {eng_input_path} "
            f"--eng-guide-infile {eng_input_path}",
        )

