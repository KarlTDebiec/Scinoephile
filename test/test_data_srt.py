#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of test-data SRT processing helpers."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from pytest import MonkeyPatch

from scinoephile.core import Language
from scinoephile.core.subtitles import Series
from test.data.srt import process_srt


def test_process_srt_uses_standard_paths_and_returns_flatten(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Test SRT fixture helper path conventions.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    title_root_path = tmp_path / "title"
    reference_path = (
        title_root_path / "output" / "zho-Hant_ocr" / "fuse_clean_validate_review.srt"
    )
    flatten_path = (
        title_root_path / "output" / "yue-Hans" / "clean_review_flatten_timewarp.srt"
    )
    workflow_result = SimpleNamespace(
        output_paths={"clean_review_flatten_timewarp": flatten_path}
    )
    workflow = Mock(return_value=workflow_result)
    workflow_cls = Mock(return_value=workflow)
    load = Mock(return_value=Mock(spec=Series))

    monkeypatch.setattr("test.data.srt.SrtProcessingWorkflow", workflow_cls)
    monkeypatch.setattr("test.data.srt.Series.load", load)

    result = process_srt(
        title_root_path,
        Language.yue_hans,
        reference_path,
        one_end_idx=1421,
        two_end_idx=1461,
        overwrite=True,
    )

    assert result is load.return_value
    workflow_cls.assert_called_once_with(
        title_root_path / "input" / "yue-Hans.srt",
        reference_path,
        title_root_path / "output" / "yue-Hans",
        language=Language.yue_hans,
        one_start_idx=None,
        one_end_idx=1421,
        two_start_idx=None,
        two_end_idx=1461,
        overwrite=True,
        provider=None,
        additional_context=None,
        reviewer_kw=None,
    )
    workflow.assert_called_once_with()
    load.assert_called_once_with(flatten_path)
