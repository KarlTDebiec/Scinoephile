#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of alignment-derived series diffing."""

from __future__ import annotations

from scinoephile.analysis.diff import LineDiffKind, SeriesDiff
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


def test_series_diff_delete():
    """Test alignment-derived deletion."""
    diff = SeriesDiff(_get_series("alpha"), _get_series())
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.DELETE
    assert messages[0].one_idxs == (0,)
    assert messages[0].one_texts == ("alpha",)


def test_series_diff_edit():
    """Test alignment-derived one-to-one edit."""
    diff = SeriesDiff(_get_series("alpha"), _get_series("alps"))
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.EDIT
    assert messages[0].one_idxs == (0,)
    assert messages[0].two_idxs == (0,)


def test_series_diff_insert():
    """Test alignment-derived insertion."""
    diff = SeriesDiff(_get_series(), _get_series("alpha"))
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.INSERT
    assert messages[0].two_idxs == (0,)
    assert messages[0].two_texts == ("alpha",)


def test_series_diff_merge():
    """Test alignment-derived exact merge."""
    diff = SeriesDiff(_get_series("alpha", "beta"), _get_series("alpha beta"))
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.MERGE
    assert messages[0].one_idxs == (0, 1)
    assert messages[0].two_idxs == (0,)


def test_series_diff_split():
    """Test alignment-derived exact split."""
    diff = SeriesDiff(_get_series("alpha beta"), _get_series("alpha", "beta"))
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.SPLIT
    assert messages[0].one_idxs == (0,)
    assert messages[0].two_idxs == (0, 1)


def test_series_diff_does_not_duplicate_line_delete():
    """Test one changed line is not emitted as both edit and delete."""
    diff = SeriesDiff(
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


def test_series_diff_pairs_same_position_delete_insert():
    """Test same-position delete and insert spans merge into one edit."""
    diff = SeriesDiff(
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


def test_series_diff_pairs_adjacent_similar_insert_delete():
    """Test adjacent similar insert and delete spans merge into one edit."""
    diff = SeriesDiff(
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


def test_series_diff_pairs_bracketed_insert():
    """Test target-only edits pair with a bracketed source line."""
    diff = SeriesDiff(
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


def test_series_diff_does_not_merge_cross_side_index_matches():
    """Test same-numbered first- and second-side indices remain independent."""
    diff = SeriesDiff(
        _get_series(
            "你听我讲，爹哋出名系二世祖",
            "副身家都洗到七七八八㗎喇",
            "好话唔好听，但系第日我两个脚一伸呢",
            "你个王八蛋，点解嚟呢度讨饭呀？",
            "我不嬲都靠自己㗎啦",
        ),
        _get_series(
            "你听我讲，阿爹出咗名系二世祖",
            "副身家都洗到七七八八喇",
            "好话唔好听，第日阿爹两脚一伸呢",
            "你就冚扮烂都要靠自己喇",
        ),
    )
    messages = list(diff)
    assert [message.kind for message in messages] == [
        LineDiffKind.EDIT,
        LineDiffKind.EDIT,
        LineDiffKind.EDIT,
        LineDiffKind.MERGE_EDIT,
    ]
    assert messages[1].one_idxs == (1,)
    assert messages[1].two_idxs == (1,)


def test_series_diff_pairs_one_sided_punctuation_with_context_line():
    """Test one-sided punctuation edits include the matching opposite line."""
    diff = SeriesDiff(
        _get_series("辛苦啦！少爷", "抹汗啦，少爷！"),
        _get_series("辛苦喇！少爷", "抹汗啦，少爷"),
    )
    messages = list(diff)
    assert [message.kind for message in messages] == [
        LineDiffKind.EDIT,
        LineDiffKind.EDIT,
    ]
    assert messages[1].one_idxs == (1,)
    assert messages[1].two_idxs == (1,)


def test_series_diff_does_not_tag_neighbor_for_line_insert():
    """Test an inserted middle line does not tag unchanged neighbors."""
    diff = SeriesDiff(_get_series("a", "b"), _get_series("a", "x", "b"))
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.INSERT
    assert messages[0].two_idxs == (1,)
    assert messages[0].two_texts == ("x",)


def test_series_diff_does_not_tag_neighbor_for_line_delete():
    """Test a deleted middle line does not tag unchanged neighbors."""
    diff = SeriesDiff(_get_series("a", "x", "b"), _get_series("a", "b"))
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.DELETE
    assert messages[0].one_idxs == (1,)
    assert messages[0].one_texts == ("x",)


def test_series_diff_does_not_pair_dissimilar_bracketed_span():
    """Test positional fallback does not pair dissimilar one-sided spans."""
    one = _get_series("editA", "qqqq", "editB")
    two = _get_series("editZ", "real insert", "editY")
    diff = SeriesDiff(one, two)
    one_side = diff._get_block_side(
        (0, 1, 2),
        diff._get_series_event_line_records(one),
    )
    two_side = diff._get_block_side(
        (0, 1, 2),
        diff._get_series_event_line_records(two),
    )

    paired = diff._pair_bracketed_one_sided_spans(
        [((0,), (0,)), ((), (1,)), ((2,), (2,))],
        one_side,
        two_side,
    )

    assert paired == [((0,), (0,)), ((), (1,)), ((2,), (2,))]


def test_series_diff_does_not_merge_sparse_one_sided_spans():
    """Test one-sided spans separated by unchanged lines are not merged."""
    one = _get_series("start", "alpha", "same1", "same2", "end")
    two = _get_series("start", "same1", "same2", "alpha!", "end")
    diff = SeriesDiff(one, two)
    one_side = diff._get_block_side(
        (0, 1, 2, 3, 4),
        diff._get_series_event_line_records(one),
    )
    two_side = diff._get_block_side(
        (0, 1, 2, 3, 4),
        diff._get_series_event_line_records(two),
    )

    should_merge = diff._should_merge_adjacent_one_sided_spans(
        one_side,
        two_side,
        (1,),
        (),
        (),
        (3,),
    )

    assert should_merge is False


def test_series_diff_merges_adjacent_one_sided_spans():
    """Test nearby similar one-sided spans still merge."""
    one = _get_series("靠你了", "莫大叔！莲花落阵你都冇有把握")
    two = _get_series("靠你喇！", "莫大叔呀！莲花落阵你都冇把握")
    diff = SeriesDiff(one, two)
    one_side = diff._get_block_side(
        (0, 1),
        diff._get_series_event_line_records(one),
    )
    two_side = diff._get_block_side(
        (0, 1),
        diff._get_series_event_line_records(two),
    )

    should_merge = diff._should_merge_adjacent_one_sided_spans(
        one_side,
        two_side,
        (1,),
        (),
        (),
        (1,),
    )

    assert should_merge is True


def test_series_diff_large_block_falls_back_to_line_alignment():
    """Test large blocks use bounded line-level fallback alignment."""
    diff = SeriesDiff(
        _get_series("editA", "real delete", "same", "editB"),
        _get_series("editZ", "same", "real insert", "editY"),
        max_alignment_cells=1,
    )
    messages = list(diff)
    assert messages
