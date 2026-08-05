#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the OCR processing workflow."""

from __future__ import annotations

from pathlib import Path

from scinoephile.core import Language
from scinoephile.workflows.ocr_processing import OcrProcessingWorkflow


def test_ocr_processing_workflow_keeps_cache_policy_on_cache(tmp_path: Path):
    """Test resolved cache configuration remains owned by the subtitle cache."""
    cache_root_path = tmp_path / "cache"
    workflow = OcrProcessingWorkflow(
        tmp_path / "source.sup",
        tmp_path / "output",
        language=Language.eng,
        cache_root_path=cache_root_path,
        overwrite_cache=True,
    )

    assert workflow._subtitle_cache.cache_root_path == cache_root_path
    assert workflow._subtitle_cache.overwrite
    assert not hasattr(workflow, "cache_root_path")
    assert not hasattr(workflow, "overwrite_cache")


def test_ocr_processing_workflow_sets_default_fusion_current_test_cases_path(
    tmp_path: Path,
):
    """Test OCR processing persists fusion decisions at its conventional path.

    Arguments:
        tmp_path: pytest temporary path fixture
    """
    workflow = OcrProcessingWorkflow(
        tmp_path / "source.sup", tmp_path / "output", language=Language.yue_hant
    )

    assert workflow.fuser_kw["current_test_cases_path"] == (
        tmp_path / "output" / "lang" / "yue" / "ocr_fusion.json"
    )


def test_ocr_processing_workflow_preserves_fusion_current_test_cases_path(
    tmp_path: Path,
):
    """Test supplied OCR-fusion test-case paths take precedence.

    Arguments:
        tmp_path: pytest temporary path fixture
    """
    current_test_cases_path = tmp_path / "custom.json"
    workflow = OcrProcessingWorkflow(
        tmp_path / "source.sup",
        tmp_path / "output",
        language=Language.eng,
        fuser_kw={"current_test_cases_path": current_test_cases_path},
    )

    assert workflow.fuser_kw["current_test_cases_path"] == current_test_cases_path
