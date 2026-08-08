#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of timestamped multiple-sequence alignment."""

from __future__ import annotations

from scinoephile.analysis.multisequence_alignment import (
    TimedAlignmentColumn,
    TimedAlignmentSequence,
    TimedAlignmentSettings,
    TimedAlignmentToken,
    TimedMultiSequenceAligner,
    TimedMultiSequenceAlignment,
    get_timed_alignment_with_pauses,
)


def test_large_timed_alignment_uses_guide_orders():
    """Test a large source set is aligned without factorial order enumeration."""
    texts = ("我真係", "我真系", "我係", "我真是", "我就係", "我就系")
    sequences = tuple(
        _get_sequence(
            f"source-{idx}",
            text,
            tuple(character_idx / 2 for character_idx in range(len(text))),
        )
        for idx, text in enumerate(texts)
    )

    alignment = TimedMultiSequenceAligner(_get_similarity)(sequences)

    assert alignment.source_names == tuple(sequence.name for sequence in sequences)
    assert (
        tuple(alignment.get_sequence_text(sequence.name) for sequence in sequences)
        == texts
    )


def test_timed_alignment_settings_reject_too_small_exhaustive_limit():
    """Test at least pairwise order search is required."""
    try:
        TimedAlignmentSettings(exhaustive_order_source_limit=1)
    except ValueError as exc:
        assert str(exc) == (
            "Exhaustive alignment order source limit must be at least two."
        )
    else:
        raise AssertionError("Expected invalid exhaustive source limit to fail.")


def test_timed_alignment_preserves_sources_and_insertion_gaps():
    """Test progressive alignment preserves every source and exposes gaps."""
    sequences = (
        _get_sequence("whisper", "我係", (0.0, 0.4)),
        _get_sequence("mimo", "我真是", (0.0, 0.2, 0.4)),
        _get_sequence("qwen", "我系", (0.0, 0.4)),
    )

    alignment = TimedMultiSequenceAligner(_get_similarity)(sequences)

    assert alignment.source_names == ("whisper", "mimo", "qwen")
    assert alignment.get_sequence_text("whisper") == "我係"
    assert alignment.get_sequence_text("mimo") == "我真是"
    assert alignment.get_sequence_text("qwen") == "我系"
    assert [
        tuple(None if token is None else token.text for token in column.tokens)
        for column in alignment.columns
    ] == [("我", "我", "我"), (None, "真", None), ("係", "是", "系")]


def test_timed_alignment_uses_time_to_resolve_repeated_character():
    """Test timestamp scoring aligns a repeated character to its local peer."""
    one = TimedAlignmentSequence(
        "one",
        (TimedAlignmentToken("啊", 0.0, 0.2), TimedAlignmentToken("啊", 10.0, 10.2)),
    )
    two = TimedAlignmentSequence("two", (TimedAlignmentToken("啊", 10.0, 10.2),))

    def similarity(left: TimedAlignmentToken, right: TimedAlignmentToken) -> float:
        """Prefer identical characters that occur at the same time."""
        distance = abs(left.start_seconds - right.start_seconds)
        return 4.0 - distance

    alignment = TimedMultiSequenceAligner(similarity)((one, two))

    assert [column.tokens[1] is None for column in alignment.columns] == [True, False]


def test_add_sequence_preserves_existing_profile_alignment():
    """Test a subsequent sequence cannot change existing row relationships."""
    aligner = TimedMultiSequenceAligner(_get_similarity)
    alignment = aligner(
        (
            _get_sequence("whisper", "我係", (0.0, 1.0)),
            _get_sequence("qwen", "我系", (0.0, 1.0)),
        )
    )
    original_profile = [column.tokens for column in alignment.columns]

    alignment = aligner.add_sequence(
        alignment, _get_sequence("reference", "我真係", (0.0, 0.5, 1.0))
    )

    projected_profile = [
        column.tokens[:2]
        for column in alignment.columns
        if any(token is not None for token in column.tokens[:2])
    ]
    assert projected_profile == original_profile
    assert alignment.get_sequence_text("reference") == "我真係"


def test_timed_pauses_are_shared_columns_with_explicit_duration():
    """Test shared timing gaps become bounded pause-unit columns."""
    alignment = TimedMultiSequenceAlignment(
        source_names=("whisper", "qwen", "reference"),
        columns=(
            TimedAlignmentColumn(
                (
                    TimedAlignmentToken("甲", 0.0, 0.1),
                    TimedAlignmentToken("甲", 0.0, 0.1),
                    TimedAlignmentToken("甲", 0.0, 0.1),
                )
            ),
            TimedAlignmentColumn(
                (
                    TimedAlignmentToken("乙", 2.6, 2.7),
                    TimedAlignmentToken("乙", 2.6, 2.7),
                    TimedAlignmentToken("乙", 2.6, 2.7),
                )
            ),
        ),
    )

    alignment = get_timed_alignment_with_pauses(
        alignment,
        source_names=("whisper", "qwen"),
        start_seconds=0.0,
        end_seconds=3.4,
        minimum_pause_seconds=0.5,
        pause_unit_seconds=1.0,
    )

    pauses = [column for column in alignment.columns if column.is_pause]
    assert [column.pause_interval_seconds for column in pauses] == [
        (0.1, 1.1),
        (1.1, 2.1),
        (2.1, 2.6),
        (2.7, 3.4),
    ]
    assert all(all(token is None for token in column.tokens) for column in pauses)
    assert alignment.get_sequence_text("reference") == "甲乙"


def test_explicit_timed_pauses_are_inserted_at_source_time():
    """Externally detected pauses should become shared profile columns."""
    alignment = TimedMultiSequenceAlignment(
        source_names=("one", "two"),
        columns=(
            TimedAlignmentColumn(
                (
                    TimedAlignmentToken("甲", 0.0, 0.2),
                    TimedAlignmentToken("甲", 0.0, 0.2),
                )
            ),
            TimedAlignmentColumn(
                (
                    TimedAlignmentToken("乙", 1.2, 1.4),
                    TimedAlignmentToken("乙", 1.2, 1.4),
                )
            ),
        ),
    )

    with_pauses = get_timed_alignment_with_pauses(
        alignment,
        pause_intervals_seconds=((0.3, 1.1),),
        pause_unit_seconds=1.0,
        source_names=("one", "two"),
    )

    assert tuple(column.is_pause for column in with_pauses.columns) == (
        False,
        True,
        False,
    )
    assert with_pauses.columns[1].pause_interval_seconds == (0.3, 1.1)


def test_explicit_timed_pause_prefers_matching_source_gap():
    """A real source gap should override correlated forced-alignment timing."""
    alignment = TimedMultiSequenceAlignment(
        source_names=("native", "ctc-one", "ctc-two"),
        columns=(
            TimedAlignmentColumn(
                (
                    TimedAlignmentToken("三", 0.0, 0.2),
                    TimedAlignmentToken("三", 0.0, 1.4),
                    TimedAlignmentToken("三", 0.0, 1.4),
                )
            ),
            TimedAlignmentColumn(
                (
                    TimedAlignmentToken("夜", 0.2, 0.4),
                    TimedAlignmentToken("夜", 1.4, 1.5),
                    TimedAlignmentToken("夜", 1.4, 1.5),
                )
            ),
            TimedAlignmentColumn(
                (
                    TimedAlignmentToken("見", 1.2, 1.4),
                    TimedAlignmentToken("見", 1.5, 1.7),
                    TimedAlignmentToken("見", 1.5, 1.7),
                )
            ),
        ),
    )

    with_pauses = get_timed_alignment_with_pauses(
        alignment,
        pause_intervals_seconds=((0.5, 1.1),),
        source_names=("native", "ctc-one", "ctc-two"),
    )

    assert tuple(
        column_idx
        for column_idx, column in enumerate(with_pauses.columns)
        if column.is_pause
    ) == (2, 3)
    assert [
        token.text
        for column in with_pauses.columns
        if (token := column.tokens[0]) is not None
    ] == ["三", "夜", "見"]


def test_timed_pause_default_threshold_is_point_two_five_seconds():
    """Default pause rendering should include 0.25 seconds but exclude shorter gaps."""
    alignment = TimedMultiSequenceAlignment(
        source_names=("one", "two"),
        columns=(
            TimedAlignmentColumn(
                (
                    TimedAlignmentToken("甲", 0.0, 0.1),
                    TimedAlignmentToken("甲", 0.0, 0.1),
                )
            ),
        ),
    )

    with_pauses = get_timed_alignment_with_pauses(
        alignment, pause_intervals_seconds=((0.0, 0.25), (0.5, 0.74))
    )

    assert [
        column.pause_interval_seconds
        for column in with_pauses.columns
        if column.is_pause
    ] == [(0.0, 0.25)]


def test_timed_pause_columns_encode_point_two_five_second_buckets():
    """Pause columns should increase once for each 0.25-second duration bucket."""
    alignment = TimedMultiSequenceAlignment(
        source_names=("one", "two"),
        columns=(
            TimedAlignmentColumn(
                (
                    TimedAlignmentToken("甲", 0.0, 0.1),
                    TimedAlignmentToken("甲", 0.0, 0.1),
                )
            ),
        ),
    )

    for duration_seconds, expected_count in ((0.3, 1), (0.55, 2), (0.8, 3)):
        with_pauses = get_timed_alignment_with_pauses(
            alignment, pause_intervals_seconds=((1.0, 1.0 + duration_seconds),)
        )
        pauses = [column for column in with_pauses.columns if column.is_pause]

        assert len(pauses) == expected_count
        assert pauses[0].pause_interval_seconds is not None
        assert pauses[0].pause_interval_seconds[0] == 1.0
        assert pauses[-1].pause_interval_seconds is not None
        assert pauses[-1].pause_interval_seconds[1] == 1.0 + duration_seconds


def _get_sequence(
    name: str, text: str, starts: tuple[float, ...]
) -> TimedAlignmentSequence:
    """Build a compact timed-character test sequence."""
    return TimedAlignmentSequence(
        name,
        tuple(
            TimedAlignmentToken(character, start, start + 0.1)
            for character, start in zip(text, starts, strict=True)
        ),
    )


def _get_similarity(one: TimedAlignmentToken, two: TimedAlignmentToken) -> float:
    """Score exact test characters above substitutions."""
    if one.text == two.text:
        return 4.0
    return 1.0
