#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of `SeriesDiff`."""

from __future__ import annotations

import pytest

from scinoephile.analysis.diff import LineDiffKind, SeriesDiff
from scinoephile.core import ScinoephileError
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


def test_series_diff_reports_split_edit():
    """Test one-to-many split with edited text."""
    diff = SeriesDiff(_get_series("alpha beta"), _get_series("alpha", "betx"))
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.SPLIT_EDIT
    assert messages[0].one_idxs == (0,)
    assert messages[0].two_idxs == (0, 1)


def test_series_diff_reports_merge_edit():
    """Test many-to-one merge with edited text."""
    diff = SeriesDiff(_get_series("alpha", "beta"), _get_series("alpha betx"))
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.MERGE_EDIT
    assert messages[0].one_idxs == (0, 1)
    assert messages[0].two_idxs == (0,)


def test_series_diff_reports_shift():
    """Test many-to-many shifted text."""
    diff = SeriesDiff(
        _get_series("alpha", "beta"),
        _get_series("beta", "alpha"),
        similarity_cutoff=0.4,
    )
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.SHIFT
    assert messages[0].one_idxs == (0, 1)
    assert messages[0].two_idxs == (0, 1)


def test_series_diff_get_stacked_str_appends_third_series():
    """Test stacked diff output can include an unaligned third series."""
    one = _get_series("alpha beta")
    two = _get_series("alpha", "beta")
    three = _get_series("source alpha beta")

    rendered = SeriesDiff(one, two).get_stacked_str(color=False, three=three)

    assert rendered.splitlines() == [
        "1 1-2",
        "alpha beta",
        "alpha beta",
        "source alpha beta",
    ]


def test_series_diff_get_stacked_str_can_include_equal_lines():
    """Test stacked diff output can include unchanged aligned lines."""
    one = _get_series("same", "before", "changed")
    two = _get_series("same", "before", "edited")
    three = _get_series("source same", "source before", "source changed")

    rendered = SeriesDiff(one, two).get_stacked_str(
        color=False,
        three=three,
        include_equal=True,
    )

    assert rendered.splitlines() == [
        "1 1",
        "same",
        "same",
        "source same",
        "",
        "2 2",
        "before",
        "before",
        "source before",
        "",
        "3 3",
        "changed",
        " edited",
        "source changed",
    ]


def test_series_diff_get_stacked_str_appends_blank_third_line_for_insert():
    """Test third-series output is blank for second-side-only inserts."""
    one = _get_series()
    two = _get_series("extra")
    three = _get_series()

    rendered = SeriesDiff(one, two).get_stacked_str(color=False, three=three)

    assert rendered.splitlines() == ["| 1", "", "extra", ""]


def test_series_diff_get_stacked_str_rejects_non_one_to_one_third_series():
    """Test stacked diff output rejects a third series not matched with one."""
    one = _get_series("alpha beta")
    two = _get_series("alpha", "beta")
    three = _get_series("source alpha beta", "extra")

    with pytest.raises(ScinoephileError, match="one-to-one matched"):
        SeriesDiff(one, two).get_stacked_str(color=False, three=three)
