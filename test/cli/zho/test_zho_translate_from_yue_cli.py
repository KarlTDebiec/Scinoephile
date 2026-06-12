#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.zho.zho_translate_from_yue_cli."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from scinoephile.cli.zho.zho_translate_from_yue_cli import ZhoTranslateFromYueCli
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from scinoephile.multilang.zho_yue.gapped_translation import (
    ZhoGappedTranslationVsYuePromptZhoHans,
)
from scinoephile.multilang.zho_yue.guided_translation import (
    ZhoGuidedTranslationVsYuePromptZhoHans,
)
from scinoephile.multilang.zho_yue.translation import (
    ZhoTranslationVsYuePromptZhoHans,
)
from test.helpers import (
    assert_series_equal,
    test_data_root,
)


def test_zho_translate_from_yue_cli_gapped_translation():
    """Test standard Chinese translate-from-yue CLI routes to gapped translation."""
    yue_input_path = (
        test_data_root / "mlamd/output/yue-Hans_transcribe/transcribe_review.srt"
    )
    zho_input_path = test_data_root / (
        "mlamd/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )
    expected_path = test_data_root / "mlamd/output/zho-Hans_ocr/fuse_clean_validate.srt"
    expected = Series.load(expected_path)

    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.zho.zho_translate_from_yue_cli."
            "get_zho_vs_yue_gapped_translator",
            return_value="translator",
        ) as patched_factory:
            with patch(
                "scinoephile.cli.zho.zho_translate_from_yue_cli."
                "get_zho_gapped_translated_vs_yue",
                return_value=expected,
            ) as patched_translate:
                run_cli_with_args(
                    ZhoTranslateFromYueCli,
                    f"--yue-infile {yue_input_path} "
                    f"--zho-gapped-infile {zho_input_path} "
                    f"--outfile {output_path}",
                )
        output = Series.load(output_path)

    assert (
        patched_factory.call_args.kwargs["prompt_cls"]
        is ZhoGappedTranslationVsYuePromptZhoHans
    )
    assert patched_factory.call_args.kwargs["provider"] is not None
    called_kwargs = patched_translate.call_args.kwargs
    assert_series_equal(called_kwargs["zhongwen"], Series.load(zho_input_path))
    assert_series_equal(called_kwargs["yuewen"], Series.load(yue_input_path))
    assert called_kwargs["translator"] == "translator"
    assert_series_equal(output, expected)


def test_zho_translate_from_yue_cli_guided_translation():
    """Test standard Chinese translate-from-yue CLI routes to guided translation."""
    yue_input_path = (
        test_data_root / "mlamd/output/yue-Hans_transcribe/transcribe_review.srt"
    )
    zho_input_path = test_data_root / (
        "mlamd/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )
    expected_path = test_data_root / "mlamd/output/zho-Hans_ocr/fuse_clean_validate.srt"
    expected = Series.load(expected_path)

    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.zho.zho_translate_from_yue_cli."
            "get_zho_yue_guided_translator",
            return_value="translator",
        ) as patched_factory:
            with patch(
                "scinoephile.cli.zho.zho_translate_from_yue_cli."
                "get_zho_translated_from_yue_with_zho_guidance",
                return_value=expected,
            ) as patched_translate:
                run_cli_with_args(
                    ZhoTranslateFromYueCli,
                    f"--yue-infile {yue_input_path} "
                    f"--zho-guide-infile {zho_input_path} "
                    f"--outfile {output_path}",
                )
        output = Series.load(output_path)

    assert (
        patched_factory.call_args.kwargs["prompt_cls"]
        is ZhoGuidedTranslationVsYuePromptZhoHans
    )
    assert patched_factory.call_args.kwargs["provider"] is not None
    called_kwargs = patched_translate.call_args.kwargs
    assert_series_equal(called_kwargs["yuewen"], Series.load(yue_input_path))
    assert_series_equal(called_kwargs["zhongwen"], Series.load(zho_input_path))
    assert called_kwargs["translator"] == "translator"
    assert_series_equal(output, expected)


def test_zho_translate_from_yue_cli_regular_translation():
    """Test standard Chinese translate-from-yue CLI routes to regular translation."""
    yue_input_path = (
        test_data_root / "mlamd/output/yue-Hans_transcribe/transcribe_review.srt"
    )
    expected_path = test_data_root / "mlamd/output/zho-Hans_ocr/fuse_clean_validate.srt"
    expected = Series.load(expected_path)

    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.zho.zho_translate_from_yue_cli.get_zho_yue_translator",
            return_value="translator",
        ) as patched_factory:
            with patch(
                "scinoephile.cli.zho.zho_translate_from_yue_cli."
                "get_zho_translated_from_yue",
                return_value=expected,
            ) as patched_translate:
                run_cli_with_args(
                    ZhoTranslateFromYueCli,
                    f"--yue-infile {yue_input_path} --outfile {output_path}",
                )
        output = Series.load(output_path)

    assert (
        patched_factory.call_args.kwargs["prompt_cls"]
        is ZhoTranslationVsYuePromptZhoHans
    )
    assert patched_factory.call_args.kwargs["provider"] is not None
    called_kwargs = patched_translate.call_args.kwargs
    assert_series_equal(called_kwargs["yuewen"], Series.load(yue_input_path))
    assert called_kwargs["translator"] == "translator"
    assert_series_equal(output, expected)


def test_zho_translate_from_yue_cli_rejects_gapped_and_guide_together():
    """Test standard Chinese translate-from-yue CLI rejects conflicts."""
    yue_input_path = (
        test_data_root / "mlamd/output/yue-Hans_transcribe/transcribe_review.srt"
    )
    zho_input_path = test_data_root / (
        "mlamd/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            ZhoTranslateFromYueCli,
            f"--yue-infile {yue_input_path} "
            f"--zho-gapped-infile {zho_input_path} "
            f"--zho-guide-infile {zho_input_path}",
        )
