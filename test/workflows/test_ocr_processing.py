#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the OCR processing workflow."""

from __future__ import annotations

from pathlib import Path

from scinoephile.core import Language
from scinoephile.workflows.ocr_processing import OcrProcessingWorkflow


def test_ocr_processing_workflow_sets_default_fusion_test_case_path(
    tmp_path: Path,
):
    """Test OCR processing persists fusion decisions at its conventional path.

    Arguments:
        tmp_path: pytest temporary path fixture
    """
    workflow = OcrProcessingWorkflow(
        tmp_path / "source.sup",
        tmp_path / "output",
        language=Language.yue_hant,
    )

    assert workflow.fuser_kw["test_case_path"] == (
        tmp_path / "output" / "lang" / "yue" / "ocr_fusion.json"
    )


def test_ocr_processing_workflow_preserves_fusion_test_case_path(
    tmp_path: Path,
):
    """Test supplied OCR-fusion test-case paths take precedence.

    Arguments:
        tmp_path: pytest temporary path fixture
    """
    test_case_path = tmp_path / "custom.json"
    workflow = OcrProcessingWorkflow(
        tmp_path / "source.sup",
        tmp_path / "output",
        language=Language.eng,
        fuser_kw={"test_case_path": test_case_path},
    )

    assert workflow.fuser_kw["test_case_path"] == test_case_path
