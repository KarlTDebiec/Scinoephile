#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of color-coded diff rendering and alignment."""

from __future__ import annotations

from scinoephile.analysis.alignment import AlignmentOp, AlignmentPolicy, align_chars
from scinoephile.analysis.colored_diff import format_colored_line_diff
from scinoephile.analysis.line_diff import LineDiff
from scinoephile.analysis.line_diff_kind import LineDiffKind

__all__ = []


def test_align_chars_match():
    """Test that exact matches align without edits."""
    alignment = align_chars("abc", "abc", policy=AlignmentPolicy.HUMAN)
    assert [c.op for c in alignment] == [AlignmentOp.MATCH] * 3


def test_align_chars_insert():
    """Test a single insertion alignment."""
    alignment = align_chars("abc", "abxc", policy=AlignmentPolicy.HUMAN)
    ops = [c.op for c in alignment]
    assert ops.count(AlignmentOp.INSERT) == 1
    assert ops.count(AlignmentOp.MATCH) == 3


def test_align_chars_delete():
    """Test a single deletion alignment."""
    alignment = align_chars("abc", "ac", policy=AlignmentPolicy.HUMAN)
    ops = [c.op for c in alignment]
    assert ops.count(AlignmentOp.DELETE) == 1
    assert ops.count(AlignmentOp.MATCH) == 2


def test_align_chars_substitute():
    """Test a single substitution alignment."""
    alignment = align_chars("abc", "axc", policy=AlignmentPolicy.HUMAN)
    ops = [c.op for c in alignment]
    assert ops.count(AlignmentOp.SUBSTITUTE) == 1
    assert ops.count(AlignmentOp.MATCH) == 2


def test_format_colored_line_diff_no_color_full_width_placeholder():
    """Test full-width placeholder selection with use_color=False."""
    msg = LineDiff(
        kind=LineDiffKind.EDIT,
        one_lbl="one",
        two_lbl="two",
        one_idxs=[0],
        two_idxs=[0],
        one_texts=["廣東話"],
        two_texts=["廣東　話"],
    )
    rendered = format_colored_line_diff(msg, use_color=False)
    lines = rendered.splitlines()
    assert lines[0] == "1 1"
    assert lines[1] == "廣東　話"
    assert lines[2] == "廣東　話"


def test_format_colored_line_diff_delete_header_marker():
    """Test delete header includes missing-side marker."""
    msg = LineDiff(
        kind=LineDiffKind.DELETE,
        one_lbl="one",
        two_lbl="two",
        one_idxs=[4],
        one_texts=["abc"],
    )
    rendered = format_colored_line_diff(msg, use_color=False)
    assert rendered.splitlines()[0] == "5 |"


def test_format_colored_line_diff_full_width_punctuation_placeholder():
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
    rendered = format_colored_line_diff(msg, use_color=False)
    assert rendered.splitlines()[2] == "　"


def test_format_colored_line_diff_insert_uses_public_insert_side():
    """Test insert rendering uses the inserted side of a public `LineDiff`."""
    msg = LineDiff(
        kind=LineDiffKind.INSERT,
        one_lbl="one",
        two_lbl="two",
        two_idxs=[2],
        two_texts=["xyz"],
    )
    rendered = format_colored_line_diff(msg, use_color=False)
    lines = rendered.splitlines()
    assert lines[0] == "| 3"
    assert lines[1] == ""
    assert lines[2] == "xyz"


def test_format_colored_line_diff_joiner_uses_full_width_punctuation():
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
    rendered = format_colored_line_diff(msg, use_color=False)
    lines = rendered.splitlines()
    assert lines[1] == "甲。　乙"
    assert lines[2] == "甲。　乙"
