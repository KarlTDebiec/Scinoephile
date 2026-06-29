#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.eng.eng_translate_from_zho_cli."""

from __future__ import annotations

from unittest.mock import patch

from pytest import raises

from scinoephile.cli.eng.eng_translate_from_zho_cli import EngTranslateFromZhoCli
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from test.helpers import (
    assert_series_equal,
    test_data_root,
)


def test_eng_translate_from_zho_cli_regular_translation():
    """Test English translate-from-zho CLI routes to regular translation."""
    zho_input_path = test_data_root / (
        "mnt/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )
    expected_path = test_data_root / "mnt/output/eng_ocr/fuse_clean_validate_review.srt"
    expected = Series.load(expected_path)

    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.eng.eng_translate_from_zho_cli.get_eng_zho_translator",
            return_value="translator",
        ):
            with patch(
                "scinoephile.cli.eng.eng_translate_from_zho_cli.get_eng_translated_from_zho",
                return_value=expected,
            ):
                run_cli_with_args(
                    EngTranslateFromZhoCli,
                    f"--zho-infile {zho_input_path} --outfile {output_path}",
                )
        output = Series.load(output_path)

    assert_series_equal(output, expected)


def test_eng_translate_from_zho_cli_passes_llm_additional_context_file(tmp_path):
    """Test English translate-from-zho CLI passes LLM additional context."""
    zho_input_path = test_data_root / (
        "mnt/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )
    expected_path = test_data_root / "mnt/output/eng_ocr/fuse_clean_validate_review.srt"
    expected = Series.load(expected_path)
    context_path = tmp_path / "context.txt"
    context_path.write_text("Use canonical character names.\n", encoding="utf-8")
    additional_contexts: list[str | None] = []

    def get_translator(*, provider: object, additional_context: str | None) -> str:
        """Record translator context."""
        assert provider is not None
        additional_contexts.append(additional_context)
        return "translator"

    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.eng.eng_translate_from_zho_cli.get_eng_zho_translator",
            side_effect=get_translator,
        ):
            with patch(
                "scinoephile.cli.eng.eng_translate_from_zho_cli.get_eng_translated_from_zho",
                return_value=expected,
            ):
                run_cli_with_args(
                    EngTranslateFromZhoCli,
                    f"--zho-infile {zho_input_path} "
                    f"--llm-additional-content-file {context_path} "
                    f"--outfile {output_path}",
                )

    assert additional_contexts == ["Use canonical character names.\n"]


def test_eng_translate_from_zho_cli_rejects_gapped_and_guide_together():
    """Test English translate-from-zho CLI rejects mutually exclusive inputs."""
    eng_input_path = test_data_root / "mnt/output/eng_ocr/fuse_clean_validate.srt"
    zho_input_path = test_data_root / (
        "mnt/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )

    with raises(SystemExit, match="2"):
        run_cli_with_args(
            EngTranslateFromZhoCli,
            f"--zho-infile {zho_input_path} "
            f"--eng-gapped-infile {eng_input_path} "
            f"--eng-guide-infile {eng_input_path}",
        )

