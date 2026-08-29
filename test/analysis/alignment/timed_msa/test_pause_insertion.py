#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of pause insertion in timestamped multiple-sequence alignments."""

from __future__ import annotations

from scinoephile.analysis.alignment import timed_msa


def test_explicit_pause_prefers_matching_source_gap():
    """A real source gap should override correlated forced-alignment timing."""
    alignment = timed_msa.MsaAlignment(
        source_names=("native", "ctc-one", "ctc-two"),
        columns=(
            timed_msa.MsaColumn(
                (
                    timed_msa.MsaToken("三", 0.0, 0.2),
                    timed_msa.MsaToken("三", 0.0, 1.4),
                    timed_msa.MsaToken("三", 0.0, 1.4),
                )
            ),
            timed_msa.MsaColumn(
                (
                    timed_msa.MsaToken("夜", 0.2, 0.4),
                    timed_msa.MsaToken("夜", 1.4, 1.5),
                    timed_msa.MsaToken("夜", 1.4, 1.5),
                )
            ),
            timed_msa.MsaColumn(
                (
                    timed_msa.MsaToken("見", 1.2, 1.4),
                    timed_msa.MsaToken("見", 1.5, 1.7),
                    timed_msa.MsaToken("見", 1.5, 1.7),
                )
            ),
        ),
    )

    with_pauses = alignment.with_pauses(
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


def test_explicit_pauses_are_inserted_at_source_time():
    """Externally detected pauses should become shared profile columns."""
    alignment = timed_msa.MsaAlignment(
        source_names=("one", "two"),
        columns=(
            timed_msa.MsaColumn(
                (timed_msa.MsaToken("甲", 0.0, 0.2), timed_msa.MsaToken("甲", 0.0, 0.2))
            ),
            timed_msa.MsaColumn(
                (timed_msa.MsaToken("乙", 1.2, 1.4), timed_msa.MsaToken("乙", 1.2, 1.4))
            ),
        ),
    )

    with_pauses = alignment.with_pauses(
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


def test_inferred_pauses_are_split_at_marker_time():
    """Inferred pauses should remain chronological around timed markers."""
    alignment = timed_msa.MsaAlignment(
        source_names=("one",),
        columns=(
            timed_msa.MsaColumn((timed_msa.MsaToken("甲", 0.0, 0.1),)),
            timed_msa.MsaColumn((None,), marker="|", marker_time_seconds=1.0),
            timed_msa.MsaColumn((timed_msa.MsaToken("乙", 2.0, 2.1),)),
        ),
    )

    with_pauses = alignment.with_pauses(pause_unit_seconds=1.0)

    assert [
        column.pause_interval_seconds
        for column in with_pauses.columns
        if column.is_pause
    ] == [(0.1, 1.0), (1.0, 2.0)]
    assert [column.start_seconds for column in with_pauses.columns] == sorted(
        column.start_seconds for column in with_pauses.columns
    )
    assert [column.end_seconds for column in with_pauses.columns] == sorted(
        column.end_seconds for column in with_pauses.columns
    )


def test_pause_columns_encode_point_two_five_second_buckets():
    """Pause columns should increase once for each 0.25-second duration bucket."""
    alignment = timed_msa.MsaAlignment(
        source_names=("one", "two"),
        columns=(
            timed_msa.MsaColumn(
                (timed_msa.MsaToken("甲", 0.0, 0.1), timed_msa.MsaToken("甲", 0.0, 0.1))
            ),
        ),
    )

    for duration_seconds, expected_count in ((0.3, 1), (0.55, 2), (0.8, 3)):
        with_pauses = alignment.with_pauses(
            pause_intervals_seconds=((1.0, 1.0 + duration_seconds),)
        )
        pauses = [column for column in with_pauses.columns if column.is_pause]

        assert len(pauses) == expected_count
        assert pauses[0].pause_interval_seconds is not None
        assert pauses[0].pause_interval_seconds[0] == 1.0
        assert pauses[-1].pause_interval_seconds is not None
        assert pauses[-1].pause_interval_seconds[1] == 1.0 + duration_seconds


def test_pause_default_threshold_is_point_two_five_seconds():
    """Default pause rendering should include 0.25 seconds but exclude shorter gaps."""
    alignment = timed_msa.MsaAlignment(
        source_names=("one", "two"),
        columns=(
            timed_msa.MsaColumn(
                (timed_msa.MsaToken("甲", 0.0, 0.1), timed_msa.MsaToken("甲", 0.0, 0.1))
            ),
        ),
    )

    with_pauses = alignment.with_pauses(
        pause_intervals_seconds=((0.0, 0.25), (0.5, 0.74))
    )

    assert [
        column.pause_interval_seconds
        for column in with_pauses.columns
        if column.is_pause
    ] == [(0.0, 0.25)]


def test_pauses_are_shared_columns_with_explicit_duration():
    """Test shared timing gaps become bounded pause-unit columns."""
    alignment = timed_msa.MsaAlignment(
        source_names=("whisper", "qwen", "reference"),
        columns=(
            timed_msa.MsaColumn(
                (
                    timed_msa.MsaToken("甲", 0.0, 0.1),
                    timed_msa.MsaToken("甲", 0.0, 0.1),
                    timed_msa.MsaToken("甲", 0.0, 0.1),
                )
            ),
            timed_msa.MsaColumn(
                (
                    timed_msa.MsaToken("乙", 2.6, 2.7),
                    timed_msa.MsaToken("乙", 2.6, 2.7),
                    timed_msa.MsaToken("乙", 2.6, 2.7),
                )
            ),
        ),
    )

    alignment = alignment.with_pauses(
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
