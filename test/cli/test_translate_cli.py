#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.translate_cli."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from pytest import raises

from scinoephile.cli.translate_cli import TranslateCli
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core import Language
from scinoephile.core.subtitles import Series
from test.helpers import (
    assert_series_equal,
    test_data_root,
)


def test_translate_cli_regular_translation_detects_source_and_uses_target_arg(
    tmp_path: Path,
):
    """Test translate CLI routes regular translation with detected source language."""
    source_path = test_data_root / (
        "mnt/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )
    expected_path = test_data_root / "mnt/output/eng_ocr/fuse_clean_validate_review.srt"
    expected = Series.load(expected_path)
    context_path = tmp_path / "context.txt"
    context_path.write_text("Use canonical character names.\n", encoding="utf-8")

    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.translate_cli.get_provider", return_value="provider"
        ):
            with patch(
                "scinoephile.cli.translate_cli.translate_series",
                return_value=expected,
            ) as translate_series:
                run_cli_with_args(
                    TranslateCli,
                    f"{source_path} --target-language eng "
                    f"--llm-additional-content-file {context_path} "
                    f"--outfile {output_path}",
                )
        output = Series.load(output_path)

    assert_series_equal(output, expected)
    kwargs = translate_series.call_args.kwargs
    assert kwargs["source_language"] is Language.zho_hans
    assert kwargs["target_language"] is Language.eng
    assert kwargs["mode"] == "regular"
    assert kwargs["target"] is None
    assert kwargs["provider"] == "provider"
    assert kwargs["additional_context"] == "Use canonical character names.\n"


def test_translate_cli_guided_translation_detects_target_from_guide():
    """Test translate CLI infers target language from guide subtitles."""
    source_path = test_data_root / (
        "mnt/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )
    guide_path = test_data_root / "mnt/output/eng_ocr/fuse_clean_validate_review.srt"
    expected = Series.load(guide_path)

    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.translate_cli.get_provider", return_value="provider"
        ):
            with patch(
                "scinoephile.cli.translate_cli.translate_series",
                return_value=expected,
            ) as translate_series:
                run_cli_with_args(
                    TranslateCli,
                    f"{source_path} --guide-infile {guide_path} "
                    f"--outfile {output_path}",
                )
        output = Series.load(output_path)

    assert_series_equal(output, expected)
    kwargs = translate_series.call_args.kwargs
    assert kwargs["source_language"] is Language.zho_hans
    assert kwargs["target_language"] is Language.eng
    assert kwargs["mode"] == "guided"
    assert kwargs["target"] is not None


def test_translate_cli_gapped_translation_uses_explicit_target_language():
    """Test translate CLI routes gapped translation with explicit target language."""
    source_path = test_data_root / (
        "mnt/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )
    gapped_path = test_data_root / "mnt/output/eng_ocr/fuse_clean_validate.srt"
    expected_path = test_data_root / "mnt/output/eng_ocr/fuse_clean_validate_review.srt"
    expected = Series.load(expected_path)

    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.translate_cli.get_provider", return_value="provider"
        ):
            with patch(
                "scinoephile.cli.translate_cli.translate_series",
                return_value=expected,
            ) as translate_series:
                run_cli_with_args(
                    TranslateCli,
                    f"{source_path} --gapped-infile {gapped_path} "
                    f"--target-language eng --outfile {output_path}",
                )
        output = Series.load(output_path)

    assert_series_equal(output, expected)
    kwargs = translate_series.call_args.kwargs
    assert kwargs["target_language"] is Language.eng
    assert kwargs["mode"] == "gapped"
    assert kwargs["target"] is not None


def test_translate_cli_warns_when_explicit_source_language_mismatches_detection():
    """Test translate CLI warns and uses explicit source language on mismatch."""
    source_path = test_data_root / (
        "mnt/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )
    expected_path = test_data_root / "mnt/output/eng_ocr/fuse_clean_validate_review.srt"
    expected = Series.load(expected_path)

    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.translate_cli.get_provider", return_value="provider"
        ):
            with patch(
                "scinoephile.cli.translate_cli.translate_series",
                return_value=expected,
            ) as translate_series:
                with patch("scinoephile.cli.translate_cli.logger.warning") as warning:
                    run_cli_with_args(
                        TranslateCli,
                        f"{source_path} --source-language yue-Hans "
                        f"--target-language eng --outfile {output_path}",
                    )

    warning.assert_called_once_with(
        "Explicit source language yue-Hans does not match detected source language "
        "zho-Hans; using yue-Hans"
    )
    assert translate_series.call_args.kwargs["source_language"] is Language.yue_hans


def test_translate_cli_rejects_missing_target_language_without_target_input():
    """Test translate CLI requires target language without guide or gapped input."""
    source_path = test_data_root / (
        "mnt/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )

    with raises(SystemExit, match="2"):
        run_cli_with_args(TranslateCli, str(source_path))


def test_translate_cli_rejects_unsupported_language_argument():
    """Test translate CLI rejects language tags outside the Language enum."""
    source_path = test_data_root / (
        "mnt/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )

    with raises(SystemExit, match="2"):
        run_cli_with_args(TranslateCli, f"{source_path} --target-language zho")


def test_translate_cli_rejects_unsupported_translation_pair():
    """Test translate CLI reports unsupported language pairs."""
    source_path = test_data_root / (
        "mnt/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )

    with patch("scinoephile.cli.translate_cli.get_provider", return_value="provider"):
        with raises(SystemExit, match="2"):
            run_cli_with_args(TranslateCli, f"{source_path} --target-language zho-Hant")


def test_translate_cli_rejects_source_and_target_stdin_together():
    """Test translate CLI rejects using stdin for both source and target input."""
    with raises(SystemExit, match="2"):
        run_cli_with_args(
            TranslateCli,
            "- --guide-infile - --target-language eng",
        )


def test_translate_cli_rejects_gapped_and_guide_together():
    """Test translate CLI rejects mutually exclusive target-side inputs."""
    source_path = test_data_root / (
        "mnt/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )
    guide_path = test_data_root / "mnt/output/eng_ocr/fuse_clean_validate_review.srt"

    with raises(SystemExit, match="2"):
        run_cli_with_args(
            TranslateCli,
            f"{source_path} --gapped-infile {guide_path} --guide-infile {guide_path}",
        )
