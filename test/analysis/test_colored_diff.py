#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of color-coded diff rendering and alignment."""

from __future__ import annotations

from scinoephile.analysis.line_alignment import (
    LineAlignment,
    LineAlignmentOperation,
)
from scinoephile.analysis.line_diff import LineDiff
from scinoephile.analysis.line_diff_kind import LineDiffKind

__all__ = []


def test_align_chars_match():
    """Test that exact matches align without edits."""
    alignment = LineAlignment("abc", "abc")
    assert [c.operation for c in alignment.alignment_pairs] == [
        LineAlignmentOperation.MATCH
    ] * 3


def test_align_chars_insert():
    """Test a single insertion alignment."""
    alignment = LineAlignment("abc", "abxc")
    ops = [c.operation for c in alignment.alignment_pairs]
    assert ops.count(LineAlignmentOperation.INSERT) == 1
    assert ops.count(LineAlignmentOperation.MATCH) == 3


def test_align_chars_delete():
    """Test a single deletion alignment."""
    alignment = LineAlignment("abc", "ac")
    ops = [c.operation for c in alignment.alignment_pairs]
    assert ops.count(LineAlignmentOperation.DELETE) == 1
    assert ops.count(LineAlignmentOperation.MATCH) == 2


def test_align_chars_substitute():
    """Test a single substitution alignment."""
    alignment = LineAlignment("abc", "axc")
    ops = [c.operation for c in alignment.alignment_pairs]
    assert ops.count(LineAlignmentOperation.SUBSTITUTE) == 1
    assert ops.count(LineAlignmentOperation.MATCH) == 2


def test_line_diff_get_stacked_str_no_color_full_width_placeholder():
    """Test full-width placeholder selection with color=False."""
    msg = LineDiff(
        kind=LineDiffKind.EDIT,
        one_lbl="one",
        two_lbl="two",
        one_idxs=[0],
        two_idxs=[0],
        one_texts=["廣東話"],
        two_texts=["廣東　話"],
    )
    rendered = msg.get_stacked_str(color=False)
    lines = rendered.splitlines()
    assert lines[0] == "1 1"
    assert lines[1] == "廣東　話"
    assert lines[2] == "廣東　話"


def test_line_diff_get_stacked_str_delete_header_marker():
    """Test delete header includes missing-side marker."""
    msg = LineDiff(
        kind=LineDiffKind.DELETE,
        one_lbl="one",
        two_lbl="two",
        one_idxs=[4],
        one_texts=["abc"],
    )
    rendered = msg.get_stacked_str(color=False)
    assert rendered.splitlines()[0] == "5 |"


def test_line_diff_get_stacked_str_full_width_punctuation_placeholder():
    """Test full-width punctuation uses an ideographic placeholder."""
    msg = LineDiff(
        kind=LineDiffKind.EDIT,
        one_lbl="one",
        two_lbl="two",
        one_idxs=[0],
        two_idxs=[0],
        one_texts=["。"],
        two_texts=[""],
    )
    rendered = msg.get_stacked_str(color=False)
    assert rendered.splitlines()[2] == "　"


def test_line_diff_get_stacked_str_insert_uses_public_insert_side():
    """Test insert rendering uses the inserted side of a public `LineDiff`."""
    msg = LineDiff(
        kind=LineDiffKind.INSERT,
        one_lbl="one",
        two_lbl="two",
        two_idxs=[2],
        two_texts=["xyz"],
    )
    rendered = msg.get_stacked_str(color=False)
    lines = rendered.splitlines()
    assert lines[0] == "| 3"
    assert lines[1] == ""
    assert lines[2] == "xyz"


def test_line_diff_get_stacked_str_joiner_uses_full_width_punctuation():
    """Test joining near full-width punctuation uses an ideographic space."""
    msg = LineDiff(
        kind=LineDiffKind.EDIT,
        one_lbl="one",
        two_lbl="two",
        one_idxs=[0, 1],
        two_idxs=[0, 1],
        one_texts=["甲。", "乙"],
        two_texts=["甲。", "乙"],
    )
    rendered = msg.get_stacked_str(color=False)
    lines = rendered.splitlines()
    assert lines[1] == "甲。　乙"
    assert lines[2] == "甲。　乙"
