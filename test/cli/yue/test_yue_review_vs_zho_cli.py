#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.yue.yue_review_vs_zho_cli."""

from __future__ import annotations

from unittest.mock import patch

from scinoephile.cli.yue.yue_review_vs_zho_cli import YueReviewVsZhoCli
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from scinoephile.multilang.yue_zho.block_review import YueBlockReviewVsZhoPromptYueHans
from test.helpers import (
    assert_series_equal,
    test_data_root,
)


def test_yue_review_vs_zho_cli_line_mode():
    """Test written Cantonese review-vs-zho CLI line mode."""
    yue_input_path = test_data_root / "mlamd/output/yue-Hans_transcribe/transcribe.srt"
    zho_input_path = (
        test_data_root
        / "mlamd/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )
    expected = Series.load(
        test_data_root / "mlamd/output/yue-Hans_transcribe/transcribe_review.srt"
    )
    yuewen_inputs: list[Series] = []
    zhongwen_inputs: list[Series] = []
    line_reviewers: list[str] = []

    def get_line_reviewed_vs_zho(
        *,
        yuewen: Series,
        zhongwen: Series,
        line_reviewer: str,
    ) -> Series:
        """Record line-review inputs."""
        yuewen_inputs.append(yuewen)
        zhongwen_inputs.append(zhongwen)
        line_reviewers.append(line_reviewer)
        return expected

    with get_temp_file_path(".srt") as outfile_path:
        with patch(
            "scinoephile.cli.yue.yue_review_vs_zho_cli.get_yue_vs_zho_line_reviewer",
            return_value="line reviewer",
        ):
            with patch(
                "scinoephile.cli.yue.yue_review_vs_zho_cli.get_yue_line_reviewed_vs_zho",
                side_effect=get_line_reviewed_vs_zho,
            ):
                with patch(
                    "scinoephile.cli.yue.yue_review_vs_zho_cli.get_yue_vs_zho_block_reviewer",
                    side_effect=AssertionError("block reviewer should not be used"),
                ):
                    run_cli_with_args(
                        YueReviewVsZhoCli,
                        f"--yue-infile {yue_input_path} "
                        f"--zho-infile {zho_input_path} "
                        f"--mode line --outfile {outfile_path}",
                    )
        output = Series.load(outfile_path)

    assert_series_equal(yuewen_inputs[0], Series.load(yue_input_path))
    assert_series_equal(zhongwen_inputs[0], Series.load(zho_input_path))
    assert line_reviewers == ["line reviewer"]
    assert_series_equal(output, expected)


def test_yue_review_vs_zho_cli_block_mode_uses_default_prompt():
    """Test written Cantonese review-vs-zho CLI block mode."""
    yue_input_path = (
        test_data_root
        / "mlamd/output/yue-Hans_transcribe/transcribe_review_translate.srt"
    )
    zho_input_path = (
        test_data_root
        / "mlamd/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )
    expected = Series.load(
        test_data_root / "mlamd/output/yue-Hans_transcribe/"
        "transcribe_review_translate_block_review.srt"
    )
    yuewen_inputs: list[Series] = []
    zhongwen_inputs: list[Series] = []
    reviewers: list[str] = []

    def get_block_reviewer(
        *,
        prompt_cls: type[YueBlockReviewVsZhoPromptYueHans],
        provider: object,
        additional_context: str | None,
    ) -> str:
        """Get a block reviewer for the selected prompt."""
        assert prompt_cls is YueBlockReviewVsZhoPromptYueHans
        assert provider is not None
        assert additional_context is None
        return "reviewer"

    def get_block_reviewed_vs_zho(
        *,
        yuewen: Series,
        zhongwen: Series,
        reviewer: str,
    ) -> Series:
        """Record block-review inputs."""
        yuewen_inputs.append(yuewen)
        zhongwen_inputs.append(zhongwen)
        reviewers.append(reviewer)
        return expected

    with get_temp_file_path(".srt") as outfile_path:
        with patch(
            "scinoephile.cli.yue.yue_review_vs_zho_cli.get_yue_vs_zho_block_reviewer",
            side_effect=get_block_reviewer,
        ):
            with patch(
                "scinoephile.cli.yue.yue_review_vs_zho_cli.get_yue_block_reviewed_vs_zho",
                side_effect=get_block_reviewed_vs_zho,
            ):
                with patch(
                    "scinoephile.cli.yue.yue_review_vs_zho_cli.get_yue_line_reviewed_vs_zho",
                    side_effect=AssertionError("line review should not be used"),
                ):
                    run_cli_with_args(
                        YueReviewVsZhoCli,
                        f"--yue-infile {yue_input_path} "
                        f"--zho-infile {zho_input_path} "
                        f"--outfile {outfile_path}",
                    )
        output = Series.load(outfile_path)

    assert_series_equal(yuewen_inputs[0], Series.load(yue_input_path))
    assert_series_equal(zhongwen_inputs[0], Series.load(zho_input_path))
    assert reviewers == ["reviewer"]
    assert_series_equal(output, expected)
