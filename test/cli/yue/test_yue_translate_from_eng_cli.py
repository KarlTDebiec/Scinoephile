#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.yue.yue_translate_from_eng_cli."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from scinoephile.cli.yue.yue_translate_from_eng_cli import YueTranslateFromEngCli
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from scinoephile.multilang.yue_eng.gapped_translation import (
    YueGappedTranslationVsEngPromptYueHans,
)
from scinoephile.multilang.yue_eng.guided_translation import (
    YueGuidedTranslationVsEngPromptYueHans,
)
from scinoephile.multilang.yue_eng.translation import (
    YueTranslationVsEngPromptYueHans,
)
from test.helpers import (
    assert_series_equal,
    test_data_root,
)


def test_yue_translate_from_eng_cli_gapped_translation():
    """Test written Cantonese translate-from-eng CLI routes to gapped translation."""
    eng_input_path = test_data_root / "mlamd/output/eng_ocr/fuse_clean_validate.srt"
    yue_input_path = (
        test_data_root / "mlamd/output/yue-Hans_transcribe/transcribe_review.srt"
    )
    expected_path = test_data_root / (
        "mlamd/output/yue-Hans_transcribe/transcribe_review_translate.srt"
    )
    expected = Series.load(expected_path)

    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.yue.yue_translate_from_eng_cli."
            "get_yue_vs_eng_gapped_translator",
            return_value="translator",
        ) as patched_factory:
            with patch(
                "scinoephile.cli.yue.yue_translate_from_eng_cli."
                "get_yue_gapped_translated_vs_eng",
                return_value=expected,
            ) as patched_translate:
                run_cli_with_args(
                    YueTranslateFromEngCli,
                    f"--eng-infile {eng_input_path} "
                    f"--yue-gapped-infile {yue_input_path} "
                    f"--outfile {output_path}",
                )
        output = Series.load(output_path)

    assert (
        patched_factory.call_args.kwargs["prompt_cls"]
        is YueGappedTranslationVsEngPromptYueHans
    )
    assert patched_factory.call_args.kwargs["provider"] is not None
    called_kwargs = patched_translate.call_args.kwargs
    assert_series_equal(called_kwargs["yuewen"], Series.load(yue_input_path))
    assert_series_equal(called_kwargs["eng"], Series.load(eng_input_path))
    assert called_kwargs["translator"] == "translator"
    assert_series_equal(output, expected)


def test_yue_translate_from_eng_cli_guided_translation():
    """Test written Cantonese translate-from-eng CLI routes to guided translation."""
    eng_input_path = test_data_root / "mlamd/output/eng_ocr/fuse_clean_validate.srt"
    yue_input_path = (
        test_data_root / "mlamd/output/yue-Hans_transcribe/transcribe_review.srt"
    )
    expected_path = test_data_root / (
        "mlamd/output/yue-Hans_transcribe/transcribe_review_translate.srt"
    )
    expected = Series.load(expected_path)

    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.yue.yue_translate_from_eng_cli."
            "get_yue_eng_guided_translator",
            return_value="translator",
        ) as patched_factory:
            with patch(
                "scinoephile.cli.yue.yue_translate_from_eng_cli."
                "get_yue_translated_from_eng_with_yue_guidance",
                return_value=expected,
            ) as patched_translate:
                run_cli_with_args(
                    YueTranslateFromEngCli,
                    f"--eng-infile {eng_input_path} "
                    f"--yue-guide-infile {yue_input_path} "
                    f"--outfile {output_path}",
                )
        output = Series.load(output_path)

    assert (
        patched_factory.call_args.kwargs["prompt_cls"]
        is YueGuidedTranslationVsEngPromptYueHans
    )
    assert patched_factory.call_args.kwargs["provider"] is not None
    called_kwargs = patched_translate.call_args.kwargs
    assert_series_equal(called_kwargs["eng"], Series.load(eng_input_path))
    assert_series_equal(called_kwargs["yuewen"], Series.load(yue_input_path))
    assert called_kwargs["translator"] == "translator"
    assert_series_equal(output, expected)


def test_yue_translate_from_eng_cli_regular_translation():
    """Test written Cantonese translate-from-eng CLI routes to regular translation."""
    eng_input_path = test_data_root / "mlamd/output/eng_ocr/fuse_clean_validate.srt"
    expected_path = test_data_root / (
        "mlamd/output/yue-Hans_transcribe/transcribe_review_translate.srt"
    )
    expected = Series.load(expected_path)

    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.yue.yue_translate_from_eng_cli.get_yue_eng_translator",
            return_value="translator",
        ) as patched_factory:
            with patch(
                "scinoephile.cli.yue.yue_translate_from_eng_cli."
                "get_yue_translated_from_eng",
                return_value=expected,
            ) as patched_translate:
                run_cli_with_args(
                    YueTranslateFromEngCli,
                    f"--eng-infile {eng_input_path} --outfile {output_path}",
                )
        output = Series.load(output_path)

    assert (
        patched_factory.call_args.kwargs["prompt_cls"]
        is YueTranslationVsEngPromptYueHans
    )
    assert patched_factory.call_args.kwargs["provider"] is not None
    called_kwargs = patched_translate.call_args.kwargs
    assert_series_equal(called_kwargs["eng"], Series.load(eng_input_path))
    assert called_kwargs["translator"] == "translator"
    assert_series_equal(output, expected)


def test_yue_translate_from_eng_cli_rejects_gapped_and_guide_together():
    """Test written Cantonese translate-from-eng CLI rejects conflicts."""
    eng_input_path = test_data_root / "mlamd/output/eng_ocr/fuse_clean_validate.srt"
    yue_input_path = (
        test_data_root / "mlamd/output/yue-Hans_transcribe/transcribe_review.srt"
    )

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            YueTranslateFromEngCli,
            f"--eng-infile {eng_input_path} "
            f"--yue-gapped-infile {yue_input_path} "
            f"--yue-guide-infile {yue_input_path}",
        )
