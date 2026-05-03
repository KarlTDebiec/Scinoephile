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


@pytest.mark.parametrize(
    (
        "one_texts",
        "two_texts",
        "expected_kind",
        "expected_one_idxs",
        "expected_two_idxs",
    ),
    [
        (("你", "好"), ("你好",), LineDiffKind.MERGE_EDIT, (0, 1), (0,)),
        (("ab",), ("a", "b"), LineDiffKind.SPLIT_EDIT, (0,), (0, 1)),
    ],
)
def test_series_diff_reports_separator_only_line_wrapping(
    one_texts: tuple[str, ...],
    two_texts: tuple[str, ...],
    expected_kind: LineDiffKind,
    expected_one_idxs: tuple[int, ...],
    expected_two_idxs: tuple[int, ...],
):
    """Test separator-only line wrapping preserves both sides.

    Arguments:
        one_texts: first subtitle series texts
        two_texts: second subtitle series texts
        expected_kind: expected diff kind
        expected_one_idxs: expected first-side line indices
        expected_two_idxs: expected second-side line indices
    """
    diff = SeriesDiff(_get_series(*one_texts), _get_series(*two_texts))
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == expected_kind
    assert messages[0].one_idxs == expected_one_idxs
    assert messages[0].two_idxs == expected_two_idxs


def test_series_diff_reports_covered_edited_continuation_split():
    """Test edited wrapped text includes the continuation line."""
    diff = SeriesDiff(
        _get_series("我一定要喺第一招就出尽全力将佢打低"),
        _get_series("我一定要系第一招", "就出尽全力将佢打低"),
    )
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.SPLIT_EDIT
    assert messages[0].one_idxs == (0,)
    assert messages[0].two_idxs == (0, 1)


def test_series_diff_keeps_uncovered_insert_separate():
    """Test a standalone insert after an equal line is not reported as a split."""
    diff = SeriesDiff(_get_series("Yes!"), _get_series("Yes!", "Damn!"))
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.INSERT
    assert messages[0].two_idxs == (1,)
    assert messages[0].two_texts == ("Damn!",)


@pytest.mark.parametrize(
    (
        "one_fixture_name",
        "two_fixture_name",
        "one_label",
        "two_label",
        "expected_fixture_name",
    ),
    [
        (
            "kob_eng_ocr_fuse_clean_validate_review_flatten",
            "kob_eng_timewarp_clean_review_flatten",
            "OCR",
            "SRT",
            "kob_eng_expected_series_diff",
        ),
        (
            "mlamd_zho_hans_fuse_clean_validate_review_flatten",
            "mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
            "SIMP",
            "TRAD",
            "mlamd_zho_simplify_expected_series_diff",
        ),
        (
            "mnt_zho_hans_fuse_clean_validate_review_flatten",
            "mnt_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
            "SIMP",
            "TRAD",
            "mnt_zho_simplify_expected_series_diff",
        ),
        (
            "t_zho_hans_fuse_clean_validate_review_flatten",
            "t_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
            "SIMP",
            "TRAD",
            "t_zho_simplify_expected_series_diff",
        ),
    ],
)
def test_series_diff_matches_expected_fixture(
    one_fixture_name: str,
    two_fixture_name: str,
    one_label: str,
    two_label: str,
    expected_fixture_name: str,
    request: pytest.FixtureRequest,
):
    """Test end-to-end series diffs against stored fixture expectations.

    Arguments:
        one_fixture_name: fixture name for the first subtitle series
        two_fixture_name: fixture name for the second subtitle series
        one_label: label for the first subtitle series
        two_label: label for the second subtitle series
        expected_fixture_name: fixture name containing expected diff strings
        request: pytest fixture request object
    """
    one: Series = request.getfixturevalue(one_fixture_name)
    two: Series = request.getfixturevalue(two_fixture_name)
    expected: list[str] = request.getfixturevalue(expected_fixture_name)

    diff = SeriesDiff(one, two, one_lbl=one_label, two_lbl=two_label)

    assert [str(message) for message in diff] == expected


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


@pytest.mark.parametrize(
    ("one_texts", "two_texts", "expected_lines"),
    [
        (
            ("a", "b"),
            ("a", "x", "b"),
            ["1 1", "a", "a", "", "| 2", "", "x", "", "2 3", "b", "b"],
        ),
        (
            ("a", "x", "b"),
            ("a", "b"),
            ["1 1", "a", "a", "", "2 |", "x", "", "", "3 2", "b", "b"],
        ),
    ],
)
def test_series_diff_get_stacked_str_keeps_equal_lines_around_one_sided_changes(
    one_texts: tuple[str, ...],
    two_texts: tuple[str, ...],
    expected_lines: list[str],
):
    """Test equal stacked lines stay aligned around inserts and deletes.

    Arguments:
        one_texts: first subtitle series texts
        two_texts: second subtitle series texts
        expected_lines: expected stacked output lines
    """
    rendered = SeriesDiff(
        _get_series(*one_texts),
        _get_series(*two_texts),
    ).get_stacked_str(color=False, include_equal=True)

    assert rendered.splitlines() == expected_lines


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
