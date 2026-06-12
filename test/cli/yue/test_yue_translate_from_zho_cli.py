#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.yue.yue_translate_from_zho_cli."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from scinoephile.cli.yue.yue_translate_from_zho_cli import YueTranslateFromZhoCli
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from scinoephile.multilang.yue_zho.gapped_translation import (
    YueGappedTranslationVsZhoPromptYueHans,
)
from scinoephile.multilang.yue_zho.guided_translation import (
    YueGuidedTranslationVsZhoPromptYueHans,
)
from scinoephile.multilang.yue_zho.translation import (
    YueTranslationVsZhoPromptYueHans,
)
from test.helpers import (
    assert_series_equal,
    test_data_root,
)


def test_yue_translate_from_zho_cli_regular_translation():
    """Test written Cantonese translate-from-zho CLI routes to regular translation."""
    zho_input_path = test_data_root / (
        "mlamd/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )
    expected_path = test_data_root / (
        "mlamd/output/yue-Hans_transcribe/transcribe_review_translate.srt"
    )
    expected = Series.load(expected_path)

    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.yue.yue_translate_from_zho_cli.get_yue_zho_translator",
            return_value="translator",
        ) as patched_factory:
            with patch(
                "scinoephile.cli.yue.yue_translate_from_zho_cli."
                "get_yue_translated_from_zho",
                return_value=expected,
            ) as patched_translate:
                run_cli_with_args(
                    YueTranslateFromZhoCli,
                    f"--zho-infile {zho_input_path} --outfile {output_path}",
                )
        output = Series.load(output_path)

    assert (
        patched_factory.call_args.kwargs["prompt_cls"]
        is YueTranslationVsZhoPromptYueHans
    )
    assert patched_factory.call_args.kwargs["provider"] is not None
    called_kwargs = patched_translate.call_args.kwargs
    assert_series_equal(called_kwargs["zhongwen"], Series.load(zho_input_path))
    assert called_kwargs["translator"] == "translator"
    assert_series_equal(output, expected)


def test_yue_translate_from_zho_cli_gapped_translation():
    """Test written Cantonese translate-from-zho CLI routes to gapped translation."""
    yue_input_path = (
        test_data_root / "mlamd/output/yue-Hans_transcribe/transcribe_review.srt"
    )
    zho_input_path = test_data_root / (
        "mlamd/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )
    expected_path = test_data_root / (
        "mlamd/output/yue-Hans_transcribe/transcribe_review_translate.srt"
    )
    expected = Series.load(expected_path)

    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.yue.yue_translate_from_zho_cli."
            "get_yue_vs_zho_gapped_translator",
            return_value="translator",
        ) as patched_factory:
            with patch(
                "scinoephile.cli.yue.yue_translate_from_zho_cli."
                "get_yue_gapped_translated_vs_zho",
                return_value=expected,
            ) as patched_translate:
                run_cli_with_args(
                    YueTranslateFromZhoCli,
                    f"--zho-infile {zho_input_path} "
                    f"--yue-gapped-infile {yue_input_path} "
                    f"--outfile {output_path}",
                )
        output = Series.load(output_path)

    assert (
        patched_factory.call_args.kwargs["prompt_cls"]
        is YueGappedTranslationVsZhoPromptYueHans
    )
    assert patched_factory.call_args.kwargs["provider"] is not None
    called_kwargs = patched_translate.call_args.kwargs
    assert_series_equal(called_kwargs["yuewen"], Series.load(yue_input_path))
    assert_series_equal(called_kwargs["zhongwen"], Series.load(zho_input_path))
    assert called_kwargs["translator"] == "translator"
    assert_series_equal(output, expected)


def test_yue_translate_from_zho_cli_guided_translation():
    """Test written Cantonese translate-from-zho CLI routes to guided translation."""
    yue_input_path = (
        test_data_root / "mlamd/output/yue-Hans_transcribe/transcribe_review.srt"
    )
    zho_input_path = test_data_root / (
        "mlamd/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )
    expected_path = test_data_root / (
        "mlamd/output/yue-Hans_transcribe/transcribe_review_translate.srt"
    )
    expected = Series.load(expected_path)

    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.yue.yue_translate_from_zho_cli."
            "get_yue_zho_guided_translator",
            return_value="translator",
        ) as patched_factory:
            with patch(
                "scinoephile.cli.yue.yue_translate_from_zho_cli."
                "get_yue_translated_from_zho_with_yue_guidance",
                return_value=expected,
            ) as patched_translate:
                run_cli_with_args(
                    YueTranslateFromZhoCli,
                    f"--zho-infile {zho_input_path} "
                    f"--yue-guide-infile {yue_input_path} "
                    f"--outfile {output_path}",
                )
        output = Series.load(output_path)

    assert (
        patched_factory.call_args.kwargs["prompt_cls"]
        is YueGuidedTranslationVsZhoPromptYueHans
    )
    assert patched_factory.call_args.kwargs["provider"] is not None
    called_kwargs = patched_translate.call_args.kwargs
    assert_series_equal(called_kwargs["zhongwen"], Series.load(zho_input_path))
    assert_series_equal(called_kwargs["yuewen"], Series.load(yue_input_path))
    assert called_kwargs["translator"] == "translator"
    assert_series_equal(output, expected)


def test_yue_translate_from_zho_cli_rejects_gapped_and_guide_together():
    """Test written Cantonese translate-from-zho CLI rejects conflicts."""
    yue_input_path = (
        test_data_root / "mlamd/output/yue-Hans_transcribe/transcribe_review.srt"
    )
    zho_input_path = test_data_root / (
        "mlamd/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            YueTranslateFromZhoCli,
            f"--zho-infile {zho_input_path} "
            f"--yue-gapped-infile {yue_input_path} "
            f"--yue-guide-infile {yue_input_path}",
        )
