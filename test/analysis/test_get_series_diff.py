#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of `SeriesDiff`."""

from __future__ import annotations

from scinoephile.analysis.diff import LineDiffKind, SeriesDiff
from scinoephile.core.subtitles import Series, Subtitle


def _get_series(*texts: str) -> Series:
    """Build a compact subtitle series for diff tests.

    Arguments:
        *texts: subtitle event texts
    Returns:
        subtitle series with one event per text
    """
    return Series(
        events=[
            Subtitle(start=idx * 1000, end=idx * 1000 + 500, text=text)
            for idx, text in enumerate(texts)
        ]
    )


def test_series_diff_empty_for_identical_series():
    """Test no messages are emitted for identical series."""
    diff = SeriesDiff(_get_series("alpha"), _get_series("alpha"))
    assert list(diff) == []
    assert str(diff) == "[]"


def test_series_diff_reports_aligned_edit():
    """Test a one-line edit from alignment-derived diffing."""
    diff = SeriesDiff(
        _get_series("莫大叔！莲花落阵你都冇有把握"),
        _get_series("莫大叔呀！莲花落阵你都冇把握"),
        one_lbl="TRANSCRIBE",
        two_lbl="REFERENCE",
    )
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.EDIT
    assert str(messages[0]) == (
        "edit: TRANSCRIBE[1] -> REFERENCE[1]: "
        "'莫大叔！莲花落阵你都冇有把握' -> '莫大叔呀！莲花落阵你都冇把握'"
    )


def test_series_diff_reports_split():
    """Test an exact one-to-many split from alignment-derived diffing."""
    diff = SeriesDiff(_get_series("alpha beta"), _get_series("alpha", "beta"))
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.SPLIT
    assert messages[0].one_idxs == (0,)
    assert messages[0].two_idxs == (0, 1)
