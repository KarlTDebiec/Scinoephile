#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of `SeriesDiff`."""

from __future__ import annotations

from pytest import FixtureRequest, param, raises

from scinoephile.analysis.diff import LineDiffKind, SeriesDiff
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series
from test.helpers import parametrize
from test.helpers.series_files import get_text_series


@parametrize(
    (
        "one_fixture_name",
        "two_fixture_name",
        "one_label",
        "two_label",
        "expected_fixture_name",
    ),
    [
        param(
            "acopopb_yue_hans_ocr_fuse_clean_validate_review_flatten",
            "acopopb_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            "SIMP",
            "TRAD",
            "acopopb_yue_simplify_expected_series_diff",
            id="acopopb-yue-simplify",
        ),
        param(
            "acopopb_zho_hans_ocr_fuse_clean_validate_review_flatten",
            "acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            "SIMP",
            "TRAD",
            "acopopb_zho_simplify_expected_series_diff",
            id="acopopb-zho-simplify",
        ),
        param(
            "acoptc_yue_hans_ocr_fuse_clean_validate_review_flatten",
            "acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            "SIMP",
            "TRAD",
            "acoptc_yue_simplify_expected_series_diff",
            id="acoptc-yue-simplify",
        ),
        param(
            "acoptc_zho_hans_ocr_fuse_clean_validate_review_flatten",
            "acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            "SIMP",
            "TRAD",
            "acoptc_zho_simplify_expected_series_diff",
            id="acoptc-zho-simplify",
        ),
        param(
            "kob_eng_ocr_fuse_clean_validate_review_flatten",
            "kob_eng_clean_review_flatten_timewarp",
            "OCR",
            "SRT",
            "kob_eng_expected_series_diff",
            id="kob-eng-ocr-vs-srt",
        ),
        param(
            "kob_yue_hans_clean_review_flatten_timewarp",
            "kob_yue_hant_clean_review_flatten_timewarp_simplify_review",
            "SIMP",
            "TRAD",
            "kob_yue_simplify_expected_series_diff",
            id="kob-yue-simplify",
        ),
        param(
            "mlamd_zho_hans_fuse_clean_validate_review_flatten",
            "mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
            "SIMP",
            "TRAD",
            "mlamd_zho_simplify_expected_series_diff",
            id="mlamd-zho-simplify",
        ),
        param(
            "mnt_zho_hans_fuse_clean_validate_review_flatten",
            "mnt_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
            "SIMP",
            "TRAD",
            "mnt_zho_simplify_expected_series_diff",
            id="mnt-zho-simplify",
        ),
        param(
            "t_zho_hans_fuse_clean_validate_review_flatten",
            "t_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
            "SIMP",
            "TRAD",
            "t_zho_simplify_expected_series_diff",
            id="t-zho-simplify",
        ),
        param(
            "tmm_yue_hans_ocr_fuse_clean_validate_review_flatten",
            "tmm_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            "SIMP",
            "TRAD",
            "tmm_yue_simplify_expected_series_diff",
            id="tmm-yue-simplify",
        ),
        param(
            "tmm_zho_hans_ocr_fuse_clean_validate_review_flatten",
            "tmm_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            "SIMP",
            "TRAD",
            "tmm_zho_simplify_expected_series_diff",
            id="tmm-zho-simplify",
        ),
    ],
)
def test_series_diff(
    one_fixture_name: str,
    two_fixture_name: str,
    one_label: str,
    two_label: str,
    expected_fixture_name: str,
    request: FixtureRequest,
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


def test_series_diff_empty_for_identical_series():
    """Test no messages are emitted for identical series."""
    diff = SeriesDiff(get_text_series("alpha"), get_text_series("alpha"))
    assert list(diff) == []
    assert str(diff) == "[]"


def test_series_diff_get_event_indices():
    """Test line indices map to unique event indices on both sides."""
    cases = [
        (
            SeriesDiff(
                get_text_series("first second"), get_text_series("first\\Nsecond")
            ),
            ((0,), (0,)),
        ),
        (
            SeriesDiff(get_text_series("same"), get_text_series("same", "insert")),
            ((), (1,)),
        ),
        (
            SeriesDiff(get_text_series("same", "delete"), get_text_series("same")),
            ((1,), ()),
        ),
    ]

    for diff, expected in cases:
        (message,) = diff.get_messages()
        assert diff.get_event_indices(message) == expected


def test_series_diff_get_messages_can_include_equal():
    """Test structured messages optionally include equal lines."""
    one = get_text_series("same", "first\\Nsecond")
    two = get_text_series("same", "first\\Nedited")
    diff = SeriesDiff(one, two)

    changed_messages = diff.get_messages()
    all_messages = diff.get_messages(include_equal=True)

    assert [message.kind for message in changed_messages] == [LineDiffKind.EDIT]
    assert [message.kind for message in all_messages] == [
        LineDiffKind.EQUAL,
        LineDiffKind.EQUAL,
        LineDiffKind.EDIT,
    ]


def test_series_diff_get_stacked_str_appends_blank_third_line_for_insert():
    """Test third-series output is blank for second-side-only inserts."""
    one = get_text_series()
    two = get_text_series("extra")
    three = get_text_series()

    rendered = SeriesDiff(one, two).get_stacked_str(color=False, three=three)

    assert rendered.splitlines() == ["| 1", "", "extra", ""]


def test_series_diff_get_stacked_str_appends_third_series():
    """Test stacked diff output can include an unaligned third series."""
    one = get_text_series("alpha beta")
    two = get_text_series("alpha", "beta")
    three = get_text_series("source alpha beta")

    rendered = SeriesDiff(one, two).get_stacked_str(color=False, three=three)

    assert rendered.splitlines() == [
        "1 1-2",
        "alpha beta",
        "alpha beta",
        "source alpha beta",
    ]


def test_series_diff_get_stacked_str_can_include_equal_lines():
    """Test stacked diff output can include unchanged aligned lines."""
    one = get_text_series("same", "before", "changed")
    two = get_text_series("same", "before", "edited")
    three = get_text_series("source same", "source before", "source changed")

    rendered = SeriesDiff(one, two).get_stacked_str(
        color=False, three=three, include_equal=True
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


@parametrize(
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
    one_texts: tuple[str, ...], two_texts: tuple[str, ...], expected_lines: list[str]
):
    """Test equal stacked lines stay aligned around inserts and deletes.

    Arguments:
        one_texts: first subtitle series texts
        two_texts: second subtitle series texts
        expected_lines: expected stacked output lines
    """
    rendered = SeriesDiff(
        get_text_series(*one_texts), get_text_series(*two_texts)
    ).get_stacked_str(color=False, include_equal=True)

    assert rendered.splitlines() == expected_lines


def test_series_diff_get_stacked_str_rejects_non_one_to_one_third_series():
    """Test stacked diff output rejects a third series not matched with one."""
    one = get_text_series("alpha beta")
    two = get_text_series("alpha", "beta")
    three = get_text_series("source alpha beta", "extra")

    with raises(ScinoephileError, match="one-to-one matched"):
        SeriesDiff(one, two).get_stacked_str(color=False, three=three)


def test_series_diff_keeps_uncovered_insert_separate():
    """Test a standalone insert after an equal line is not reported as a split."""
    diff = SeriesDiff(get_text_series("Yes!"), get_text_series("Yes!", "Damn!"))
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.INSERT
    assert messages[0].two_idxs == (1,)
    assert messages[0].two_texts == ("Damn!",)


def test_series_diff_represents_line_before_one_sided_span():
    """Test every line is represented after splitting one-to-many changes."""
    one = get_text_series(
        "師爺，少爺寫乜嘢呀？", "名呀", "嘩，好叻呀！原來少爺識寫自己個名喎！", "係呀。"
    )
    two = get_text_series(
        "師爺，少爺寫乜嘢呀？",
        "名呀！",
        "好叻呀！原來少爺識寫自己個名喎",
        "係呀！",
        "妖！",
    )

    diff = SeriesDiff(one, two)
    messages = diff.get_messages(include_equal=True)

    assert diff.get_event_indices(messages[1]) == ((1,), (1,))
    assert messages[1].one_texts == ("名呀",)
    assert messages[1].two_texts == ("名呀！",)
    assert sorted(idx for message in messages for idx in message.one_idxs or ()) == [
        0,
        1,
        2,
        3,
    ]
    assert sorted(idx for message in messages for idx in message.two_idxs or ()) == [
        0,
        1,
        2,
        3,
        4,
    ]


def test_series_diff_represents_line_before_shifted_changed_span():
    """Test lines before a shifted changed span are aligned in place."""
    messages = SeriesDiff(
        get_text_series("a", "b"), get_text_series("a", "ab")
    ).get_messages(include_equal=True)

    assert [
        (message.kind, message.one_idxs, message.two_idxs) for message in messages
    ] == [(LineDiffKind.EQUAL, (0,), (0,)), (LineDiffKind.EDIT, (1,), (1,))]


def test_series_diff_represents_deleted_repeated_line_before_equal_lines():
    """Test repeated lines do not offset subsequent equal-line matches."""
    messages = SeriesDiff(
        get_text_series("pre", "打賞⋯打賞", "打賞⋯打賞", "恭喜蘇翁生辰快樂", "post"),
        get_text_series("pre", "打賞⋯打賞", "恭喜蘇翁生辰快樂", "post"),
    ).get_messages(include_equal=True)

    assert [
        (message.kind, message.one_idxs, message.two_idxs) for message in messages
    ] == [
        (LineDiffKind.EQUAL, (0,), (0,)),
        (LineDiffKind.EQUAL, (1,), (1,)),
        (LineDiffKind.DELETE, (2,), None),
        (LineDiffKind.EQUAL, (3,), (2,)),
        (LineDiffKind.EQUAL, (4,), (3,)),
    ]


@parametrize(
    ("one_texts", "two_texts", "expected_message_indices"),
    [
        (
            ("c", "world", "c"),
            ("c",),
            [
                (LineDiffKind.EQUAL, (0,), (0,)),
                (LineDiffKind.DELETE, (1,), None),
                (LineDiffKind.DELETE, (2,), None),
            ],
        ),
        (
            ("baz", "beta"),
            ("baz", "alpha!", "bar", "beta!"),
            [
                (LineDiffKind.EQUAL, (0,), (0,)),
                (LineDiffKind.INSERT, None, (1,)),
                (LineDiffKind.INSERT, None, (2,)),
                (LineDiffKind.EDIT, (1,), (3,)),
            ],
        ),
    ],
)
def test_series_diff_discards_out_of_order_span_indices(
    one_texts: tuple[str, ...],
    two_texts: tuple[str, ...],
    expected_message_indices: list[
        tuple[LineDiffKind, tuple[int, ...] | None, tuple[int, ...] | None]
    ],
):
    """Test stale indices do not duplicate implicit matches.

    Arguments:
        one_texts: first subtitle series texts
        two_texts: second subtitle series texts
        expected_message_indices: expected diff message kinds and line indices
    """
    messages = SeriesDiff(
        get_text_series(*one_texts), get_text_series(*two_texts)
    ).get_messages(include_equal=True)

    assert [
        (message.kind, message.one_idxs, message.two_idxs) for message in messages
    ] == expected_message_indices


def test_series_diff_reports_aligned_edit():
    """Test a one-line edit from alignment-derived diffing."""
    diff = SeriesDiff(
        get_text_series("莫大叔！莲花落阵你都冇有把握"),
        get_text_series("莫大叔呀！莲花落阵你都冇把握"),
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


def test_series_diff_reports_covered_edited_continuation_split():
    """Test edited wrapped text includes the continuation line."""
    diff = SeriesDiff(
        get_text_series("我一定要喺第一招就出尽全力将佢打低"),
        get_text_series("我一定要系第一招", "就出尽全力将佢打低"),
    )
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.SPLIT_EDIT
    assert messages[0].one_idxs == (0,)
    assert messages[0].two_idxs == (0, 1)


def test_series_diff_reports_edited_split_with_shorter_suffix():
    """Test punctuation and a shorter edited suffix preserve a wrapped match."""
    diff = SeriesDiff(
        get_text_series("只要你哋邊個出得多過十萬兩銀票咯，"),
        get_text_series("只要你哋邊個出得多過", "十萬兩銀票喇喎"),
    )

    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.SPLIT_EDIT
    assert messages[0].one_idxs == (0,)
    assert messages[0].two_idxs == (0, 1)


def test_series_diff_reports_edited_split_with_distributed_prefix():
    """Test an edited line split after its short shared prefix stays paired."""
    diff = SeriesDiff(
        get_text_series("你放心呀，我哋有好多好靚好醒嘅姑娘㗎。"),
        get_text_series("你放心！", "我仲有好多好靚好省鏡嘅姑娘嘅"),
    )

    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.SPLIT_EDIT
    assert messages[0].one_idxs == (0,)
    assert messages[0].two_idxs == (0, 1)


@parametrize(
    ("candidate_text", "reference_texts"),
    [
        ("嚟，攞去打賞畀條女啦，老爺。", ("嚟⋯擺去打賞畀呢度啲姑娘", "老爺")),
        (
            "不過老爺諗住阿燦一個咁就夠咁解啫。",
            ("不過老爺諗住", "有阿燦一個咁就夠咁解啫"),
        ),
        ("有，攞嚟使住先。", ("有！", "拎嚟洗住先呀！")),
        (
            "雖然你休息咗兩個月，啲手腳就喐得下。",
            ("雖然你抖咗兩個月", "手腳都叫做郁得吓！"),
        ),
        (
            "順便返嚟就煲埋最後呢劑藥畀你飲下。",
            ("順便返嚟就煲埋最後呢劑藥", "畀你飲呀吓"),
        ),
        ("有就攞嚟，嚟嚟嚟嚟嚟嚟嚟！做乜嘢？", ("有就拎嚟！嚟⋯", "做咩呀？")),
        ("等我走咗你先唱。好啊。", ("等我走咗你先唱啦", "好喇")),
    ],
)
def test_series_diff_reports_temporally_aligned_weak_split(
    candidate_text: str, reference_texts: tuple[str, str]
):
    """Test timing preserves a split whose paraphrased text is weakly similar."""
    diff = SeriesDiff(
        get_text_series(candidate_text, start_ms=708, duration_ms=1600),
        get_text_series(*reference_texts, duration_ms=700, step_ms=800),
    )

    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.SPLIT_EDIT
    assert messages[0].one_idxs == (0,)
    assert messages[0].two_idxs == (0, 1)


def test_series_diff_pairs_punctuation_variant_contained_line():
    """Test punctuation does not hide a contained implicit line match."""
    messages = list(
        SeriesDiff(
            get_text_series("多謝，多謝，多謝，真係可憐⋯"), get_text_series("多謝⋯")
        )
    )

    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.EDIT
    assert messages[0].one_idxs == (0,)
    assert messages[0].two_idxs == (0,)


def test_series_diff_realigns_line_after_edited_split():
    """Test a split does not shift the next matching subtitle out of alignment."""
    diff = SeriesDiff(
        get_text_series(
            "你放心呀，我哋有好多好靚好醒嘅姑娘㗎。",
            "龜婆，咁今晚我就靠晒你喇。",
            "我衰咗啊，",
            "放肆！係",
        ),
        get_text_series(
            "你放心！",
            "我仲有好多好靚好省鏡嘅姑娘嘅",
            "龜婆，咁今晚我就靠晒你喇",
            "唔關我事嘅",
            "大膽！放肆！",
        ),
    )

    messages = diff.get_messages(include_equal=True)
    assert messages[0].kind == LineDiffKind.SPLIT_EDIT
    assert messages[0].one_idxs == (0,)
    assert messages[0].two_idxs == (0, 1)
    assert messages[1].kind == LineDiffKind.EDIT
    assert messages[1].one_idxs == (1,)
    assert messages[1].two_idxs == (2,)


def test_series_diff_reports_repeated_wrapped_lines_separately():
    """Test repeated lines are not collapsed into one wrapped match."""
    messages = list(
        SeriesDiff(
            get_text_series("〝送给妈妈〞"),
            get_text_series("「送给妈妈」", "「送给妈妈」", "「送给妈妈」"),
        )
    )

    assert [
        (message.kind, message.one_idxs, message.two_idxs) for message in messages
    ] == [
        (LineDiffKind.EDIT, (0,), (0,)),
        (LineDiffKind.INSERT, None, (1,)),
        (LineDiffKind.INSERT, None, (2,)),
    ]


def test_series_diff_reports_merge_edit():
    """Test many-to-one merge with edited text."""
    diff = SeriesDiff(get_text_series("alpha", "beta"), get_text_series("alpha betx"))
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.MERGE_EDIT
    assert messages[0].one_idxs == (0, 1)
    assert messages[0].two_idxs == (0,)


@parametrize(
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
    diff = SeriesDiff(get_text_series(*one_texts), get_text_series(*two_texts))
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == expected_kind
    assert messages[0].one_idxs == expected_one_idxs
    assert messages[0].two_idxs == expected_two_idxs


def test_series_diff_reports_shift():
    """Test many-to-many shifted text."""
    diff = SeriesDiff(
        get_text_series("alpha", "beta"),
        get_text_series("beta", "alpha"),
        similarity_cutoff=0.4,
    )
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.SHIFT
    assert messages[0].one_idxs == (0, 1)
    assert messages[0].two_idxs == (0, 1)


def test_series_diff_reports_transitively_overlapping_shift():
    """Test changed spans connected through an intermediate span are merged."""
    diff = SeriesDiff(
        get_text_series("係咁啊，皇上，", "依例最多判抄家咋喎。"),
        get_text_series("係咁嘅話喇", "皇上，依例最多判抄家！"),
    )

    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.SHIFT
    assert messages[0].one_idxs == (0, 1)
    assert messages[0].two_idxs == (0, 1)


def test_series_diff_reports_split():
    """Test an exact one-to-many split from alignment-derived diffing."""
    diff = SeriesDiff(get_text_series("alpha beta"), get_text_series("alpha", "beta"))
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.SPLIT
    assert messages[0].one_idxs == (0,)
    assert messages[0].two_idxs == (0, 1)


def test_series_diff_reports_split_edit():
    """Test one-to-many split with edited text."""
    diff = SeriesDiff(get_text_series("alpha beta"), get_text_series("alpha", "betx"))
    messages = list(diff)
    assert len(messages) == 1
    assert messages[0].kind == LineDiffKind.SPLIT_EDIT
    assert messages[0].one_idxs == (0,)
    assert messages[0].two_idxs == (0, 1)
