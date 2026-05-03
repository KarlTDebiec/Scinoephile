#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of experimental alignment-derived series diffing."""

from __future__ import annotations

from scinoephile.analysis.diff import AlignmentSeriesDiff, LineDiffKind
from scinoephile.core.subtitles import Series, Subtitle


def _get_series(*texts: str) -> Series:
    """Build a compact subtitle series for alignment diff tests.

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


def test_alignment_series_diff_delete():
    """Test alignment-derived deletion."""
    diff = AlignmentSeriesDiff(_get_series("alpha"), _get_series())
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.DELETE
    assert messages[0].one_idxs == (0,)
    assert messages[0].one_texts == ("alpha",)


def test_alignment_series_diff_edit():
    """Test alignment-derived one-to-one edit."""
    diff = AlignmentSeriesDiff(_get_series("alpha"), _get_series("alps"))
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.EDIT
    assert messages[0].one_idxs == (0,)
    assert messages[0].two_idxs == (0,)


def test_alignment_series_diff_insert():
    """Test alignment-derived insertion."""
    diff = AlignmentSeriesDiff(_get_series(), _get_series("alpha"))
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.INSERT
    assert messages[0].two_idxs == (0,)
    assert messages[0].two_texts == ("alpha",)


def test_alignment_series_diff_merge():
    """Test alignment-derived exact merge."""
    diff = AlignmentSeriesDiff(_get_series("alpha", "beta"), _get_series("alpha beta"))
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.MERGE
    assert messages[0].one_idxs == (0, 1)
    assert messages[0].two_idxs == (0,)


def test_alignment_series_diff_split():
    """Test alignment-derived exact split."""
    diff = AlignmentSeriesDiff(_get_series("alpha beta"), _get_series("alpha", "beta"))
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.SPLIT
    assert messages[0].one_idxs == (0,)
    assert messages[0].two_idxs == (0, 1)


def test_alignment_series_diff_does_not_duplicate_line_delete():
    """Test one changed line is not emitted as both edit and delete."""
    diff = AlignmentSeriesDiff(
        _get_series("第十八掌——降龙有悔啊", "阿灿,你没事　吧?"),
        _get_series("第十八掌──杀龙有悔　", "阿灿，你冇事呀嘛？"),
    )
    messages = list(diff)
    assert [message.kind for message in messages] == [
        LineDiffKind.EDIT,
        LineDiffKind.EDIT,
    ]
    assert messages[0].one_idxs == (0,)
    assert messages[0].two_idxs == (0,)


def test_alignment_series_diff_pairs_same_position_delete_insert():
    """Test same-position delete and insert spans merge into one edit."""
    diff = AlignmentSeriesDiff(
        _get_series(
            "阿灿,你没事　吧?",
            "你睇我姿势，你话我有冇事？",
            "你的姿势　很有型　",
        ),
        _get_series(
            "阿灿，你冇事呀嘛？",
            "你睇我姿势你话有冇事呀？",
            "你个姿势仲好有型！",
        ),
    )
    messages = list(diff)
    assert [message.kind for message in messages] == [
        LineDiffKind.EDIT,
        LineDiffKind.EDIT,
        LineDiffKind.EDIT,
    ]
    assert messages[1].one_idxs == (1,)
    assert messages[1].two_idxs == (1,)


def test_alignment_series_diff_pairs_adjacent_similar_insert_delete():
    """Test adjacent similar insert and delete spans merge into one edit."""
    diff = AlignmentSeriesDiff(
        _get_series(
            "靠你了",
            "莫大叔！莲花落阵你都冇有把握",
            "以我现在打狗棒法的功力",
        ),
        _get_series(
            "靠你喇！",
            "莫大叔呀！莲花落阵你都冇把握",
            "以我而家打狗棍法嘅功力",
        ),
    )
    messages = list(diff)
    assert [message.kind for message in messages] == [
        LineDiffKind.EDIT,
        LineDiffKind.EDIT,
        LineDiffKind.EDIT,
    ]
    assert messages[1].one_idxs == (1,)
    assert messages[1].two_idxs == (1,)


def test_alignment_series_diff_pairs_bracketed_insert():
    """Test target-only edits pair with a bracketed source line."""
    diff = AlignmentSeriesDiff(
        _get_series(
            "以我现在打狗棒法的功力",
            "我又点可以打低三位长老做帮主？",
            "这颗大还丹，你吃了之后会功力大增",
        ),
        _get_series(
            "以我而家打狗棍法嘅功力",
            "我又点可以打低三位长老做帮主呀？",
            "呢粒大还丹，你食咗之后会功力大增",
        ),
    )
    messages = list(diff)
    assert [message.kind for message in messages] == [
        LineDiffKind.EDIT,
        LineDiffKind.EDIT,
        LineDiffKind.EDIT,
    ]
    assert messages[1].one_idxs == (1,)
    assert messages[1].two_idxs == (1,)
