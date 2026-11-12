#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the OCR processing workflow."""

from __future__ import annotations

from os import utime
from pathlib import Path

from pytest import MonkeyPatch, mark

from scinoephile.core import Language
from scinoephile.web.ocr_validation.html_index import load_html_entries
from scinoephile.workflows.ocr_processing import OcrProcessingWorkflow
from test.helpers.ocr_validation import make_ocr_html_dir
from test.helpers.series_files import get_ocr_text_series


def test_ocr_processing_workflow_keeps_cache_policy_on_cache(tmp_path: Path):
    """Test resolved cache configuration remains owned by the subtitle cache.

    Arguments:
        tmp_path: temporary directory path
    """
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


@mark.parametrize("resume", [False, True], ids=["new-review", "saved-review"])
def test_ocr_process_interactive_opens_the_shared_editor(
    tmp_path: Path, monkeypatch: MonkeyPatch, resume: bool
):
    """Seed a new review and retain the image index when resuming a saved one.

    Arguments:
        tmp_path: isolated OCR images and pipeline outputs
        monkeypatch: pytest monkeypatch fixture
        resume: whether the editor already has saved output
    """
    images_path = make_ocr_html_dir(tmp_path, text="Saved edit")
    utime(images_path / "index.html", (1_700_000_000, 1_700_000_000))
    fused = get_ocr_text_series("Fused text")
    fused.save(tmp_path / "fuse_clean.srt")
    outfile_path = tmp_path / "fuse_clean_validate.srt"
    expected_text = "Fused text"
    if resume:
        get_ocr_text_series("Saved edit").save(outfile_path)
        expected_text = "Saved edit"
    opened_texts = []

    def serve(
        dir_path: Path,
        output_path: Path,
        *,
        validation_data_dir_path: Path,
        dev: bool,
        host: str,
        port: int,
        title: str | None,
    ):
        """Record the text and settings the pipeline hands to the editor.

        Arguments:
            dir_path: prepared image directory
            output_path: SRT path for saving the review
            validation_data_dir_path: directory with OCR validation data
            dev: whether to write to repository data
            host: editor host
            port: editor port
            title: editor title
        """
        assert dir_path == images_path
        assert output_path == outfile_path
        assert validation_data_dir_path.name == "ocr_validation"
        assert not dev
        assert (host, port, title) == ("127.0.0.1", 5050, "Film")
        opened_texts.extend(entry.text for entry in load_html_entries(dir_path))

    monkeypatch.setattr(
        "scinoephile.workflows.ocr_processing.serve_ocr_validation", serve
    )
    workflow = OcrProcessingWorkflow(
        tmp_path / "source.sup",
        tmp_path,
        language=Language.eng,
        interactive=True,
        port=5050,
        title="Film",
    )

    workflow._validate(fused)

    assert opened_texts == [expected_text]
    assert workflow.output_paths["fuse_clean_validate"] == outfile_path


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
