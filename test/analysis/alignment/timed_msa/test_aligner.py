#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of progressive timestamped multiple-sequence alignment."""

from __future__ import annotations

from pytest import raises

from scinoephile.analysis.alignment import timed_msa


def test_add_sequence_preserves_existing_profile_alignment():
    """Test a subsequent sequence cannot change existing row relationships."""
    aligner = timed_msa.Aligner(_get_similarity)
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


def test_alignment_preserves_sources_and_insertion_gaps():
    """Test progressive alignment preserves every source and exposes gaps."""
    sequences = (
        _get_sequence("whisper", "我係", (0.0, 0.4)),
        _get_sequence("mimo", "我真是", (0.0, 0.2, 0.4)),
        _get_sequence("qwen", "我系", (0.0, 0.4)),
    )

    alignment = timed_msa.Aligner(_get_similarity)(sequences)

    assert alignment.source_names == ("whisper", "mimo", "qwen")
    assert alignment.get_sequence_text("whisper") == "我係"
    assert alignment.get_sequence_text("mimo") == "我真是"
    assert alignment.get_sequence_text("qwen") == "我系"
    texts_by_column = []
    for column in alignment.columns:
        texts: list[str | None] = []
        for token in column.tokens:
            if token is None:
                texts.append(None)
            else:
                texts.append(token.text)
        texts_by_column.append(tuple(texts))
    assert texts_by_column == [
        ("我", "我", "我"),
        (None, "真", None),
        ("係", "是", "系"),
    ]


def test_alignment_uses_time_to_resolve_repeated_character():
    """Test timestamp scoring aligns a repeated character to its local peer."""
    one = timed_msa.AlignmentSequence(
        "one", (timed_msa.Token("啊", 0.0, 0.2), timed_msa.Token("啊", 10.0, 10.2))
    )
    two = timed_msa.AlignmentSequence("two", (timed_msa.Token("啊", 10.0, 10.2),))

    def similarity(left: timed_msa.Token, right: timed_msa.Token) -> float:
        """Prefer identical characters that occur at the same time.

        Arguments:
            left: first timestamped character
            right: second timestamped character
        Returns:
            timestamp-aware substitution score
        """
        distance = abs(left.start_seconds - right.start_seconds)
        return 4.0 - distance

    alignment = timed_msa.Aligner(similarity)((one, two))

    assert [column.tokens[1] is None for column in alignment.columns] == [True, False]


def test_large_alignment_uses_guide_orders():
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

    alignment = timed_msa.Aligner(_get_similarity)(sequences)

    assert alignment.source_names == tuple(sequence.name for sequence in sequences)
    assert (
        tuple(alignment.get_sequence_text(sequence.name) for sequence in sequences)
        == texts
    )


def test_settings_reject_too_small_exhaustive_limit():
    """Test at least pairwise order search is required."""
    with raises(
        ValueError, match="Exhaustive alignment order source limit must be at least two"
    ):
        timed_msa.Settings(exhaustive_order_source_limit=1)


def _get_sequence(
    name: str, text: str, starts: tuple[float, ...]
) -> timed_msa.AlignmentSequence:
    """Build a compact timed-character test sequence.

    Arguments:
        name: source name
        text: source characters
        starts: token start times
    Returns:
        timestamped character sequence
    """
    return timed_msa.AlignmentSequence(
        name,
        tuple(
            timed_msa.Token(character, start, start + 0.1)
            for character, start in zip(text, starts, strict=True)
        ),
    )


def _get_similarity(one: timed_msa.Token, two: timed_msa.Token) -> float:
    """Score exact test characters above substitutions.

    Arguments:
        one: first timestamped character
        two: second timestamped character
    Returns:
        character substitution score
    """
    if one.text == two.text:
        return 4.0
    return 1.0
