#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Progressive affine-gap alignment of timestamped sequences."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from itertools import permutations

import numpy as np

from .models import (
    TimedAlignmentColumn,
    TimedAlignmentSequence,
    TimedAlignmentSettings,
    TimedAlignmentToken,
    TimedMultiSequenceAlignment,
)

__all__ = ["TimedMultiSequenceAligner"]

type _TimedTokenSimilarity = Callable[[TimedAlignmentToken, TimedAlignmentToken], float]
"""Callable returning a substitution score for two timestamped tokens."""

_STATE_MATCH = 0
_STATE_GAP_IN_SEQUENCE = 1
_STATE_GAP_IN_PROFILE = 2
_STATE_NONE = 255


class TimedMultiSequenceAligner:
    """Align timestamped sequences using progressive affine-gap alignment."""

    def __init__(
        self,
        similarity: _TimedTokenSimilarity,
        settings: TimedAlignmentSettings | None = None,
    ):
        """Initialize.

        Arguments:
            similarity: timestamp-aware token substitution scoring function
            settings: optional affine-gap scoring configuration
        """
        self.similarity = similarity
        """Timestamp-aware token substitution scoring function."""
        if settings is None:
            settings = TimedAlignmentSettings()
        self.settings = settings
        """Affine-gap scoring configuration."""

    def __call__(
        self, sequences: Sequence[TimedAlignmentSequence]
    ) -> TimedMultiSequenceAlignment:
        """Align two or more named timestamped sequences.

        For small source sets, all progressive source orders are considered and
        the alignment with the greatest source-pair score is retained. Larger
        source sets use pairwise affinity guide orders, avoiding factorial growth
        while continuing to consider every source as an initial anchor.

        Arguments:
            sequences: named timestamped character sequences
        Returns:
            source-neutral multiple alignment in the input row order
        Raises:
            ValueError: if there are too few sequences or names are duplicated
        """
        if len(sequences) < 2:
            raise ValueError("Multiple alignment requires at least two sequences.")
        source_names = tuple(sequence.name for sequence in sequences)
        if len(set(source_names)) != len(source_names):
            raise ValueError("Multiple alignment sequence names must be unique.")

        best_alignment = None
        best_score = float("-inf")
        if len(sequences) <= self.settings.exhaustive_order_source_limit:
            ordered_sequence_candidates = permutations(sequences)
        else:
            ordered_sequence_candidates = self._get_guide_orders(sequences)
        for ordered_sequences in ordered_sequence_candidates:
            candidate = self._align_in_order(ordered_sequences)
            candidate = self._get_reordered(candidate, source_names)
            candidate_score = self._get_sum_of_pairs_score(candidate)
            if candidate_score > best_score:
                best_alignment = candidate
                best_score = candidate_score
        assert best_alignment is not None
        return best_alignment

    def add_sequence(
        self, alignment: TimedMultiSequenceAlignment, sequence: TimedAlignmentSequence
    ) -> TimedMultiSequenceAlignment:
        """Align one non-authoritative sequence onto a fixed existing profile.

        Existing rows retain their mutual alignment. The added sequence may place
        new columns between them but cannot realign them against one another.

        Arguments:
            alignment: fixed multiple-sequence alignment profile
            sequence: additional sequence to project onto the profile
        Returns:
            alignment with the additional sequence appended as its final row
        Raises:
            ValueError: if the name is duplicated or annotations were already inserted
        """
        if sequence.name in alignment.source_names:
            raise ValueError("Added alignment sequence name must be unique.")
        if any(not any(column.tokens) for column in alignment.columns):
            raise ValueError("Additional sequences must be aligned before annotations.")
        return self._align_profile_to_sequence(alignment, sequence)

    def _align_in_order(
        self, sequences: Sequence[TimedAlignmentSequence]
    ) -> TimedMultiSequenceAlignment:
        """Progressively align sequences in one specified order."""
        first = sequences[0]
        alignment = TimedMultiSequenceAlignment(
            source_names=(first.name,),
            columns=tuple(TimedAlignmentColumn((token,)) for token in first.tokens),
        )
        for sequence in sequences[1:]:
            alignment = self._align_profile_to_sequence(alignment, sequence)
        return alignment

    def _align_profile_to_sequence(  # noqa: PLR0912, PLR0915
        self, profile: TimedMultiSequenceAlignment, sequence: TimedAlignmentSequence
    ) -> TimedMultiSequenceAlignment:
        """Align one existing profile to one additional sequence."""
        profile_length = len(profile.columns)
        sequence_length = len(sequence.tokens)
        shape = (profile_length + 1, sequence_length + 1)
        match_scores = np.full(shape, float("-inf"), dtype=np.float64)
        gap_in_sequence_scores = np.full(shape, float("-inf"), dtype=np.float64)
        gap_in_profile_scores = np.full(shape, float("-inf"), dtype=np.float64)
        match_backpointers = np.full(shape, _STATE_NONE, dtype=np.uint8)
        gap_in_sequence_backpointers = np.full(shape, _STATE_NONE, dtype=np.uint8)
        gap_in_profile_backpointers = np.full(shape, _STATE_NONE, dtype=np.uint8)
        match_scores[0, 0] = 0.0

        for profile_idx in range(1, profile_length + 1):
            gap_in_sequence_scores[profile_idx, 0] = (
                self.settings.gap_open_score
                + (profile_idx - 1) * self.settings.gap_extend_score
            )
            if profile_idx == 1:
                gap_in_sequence_backpointers[profile_idx, 0] = _STATE_MATCH
            else:
                gap_in_sequence_backpointers[profile_idx, 0] = _STATE_GAP_IN_SEQUENCE
        for sequence_idx in range(1, sequence_length + 1):
            gap_in_profile_scores[0, sequence_idx] = (
                self.settings.gap_open_score
                + (sequence_idx - 1) * self.settings.gap_extend_score
            )
            if sequence_idx == 1:
                gap_in_profile_backpointers[0, sequence_idx] = _STATE_MATCH
            else:
                gap_in_profile_backpointers[0, sequence_idx] = _STATE_GAP_IN_PROFILE

        for profile_idx, column in enumerate(profile.columns, 1):
            for sequence_idx, token in enumerate(sequence.tokens, 1):
                previous_match_scores = (
                    match_scores[profile_idx - 1, sequence_idx - 1],
                    gap_in_sequence_scores[profile_idx - 1, sequence_idx - 1],
                    gap_in_profile_scores[profile_idx - 1, sequence_idx - 1],
                )
                previous_match_state = int(np.argmax(previous_match_scores))
                match_scores[profile_idx, sequence_idx] = previous_match_scores[
                    previous_match_state
                ] + self._get_profile_similarity(column, token)
                match_backpointers[profile_idx, sequence_idx] = previous_match_state

                previous_gap_in_sequence_scores = (
                    match_scores[profile_idx - 1, sequence_idx]
                    + self.settings.gap_open_score,
                    gap_in_sequence_scores[profile_idx - 1, sequence_idx]
                    + self.settings.gap_extend_score,
                    gap_in_profile_scores[profile_idx - 1, sequence_idx]
                    + self.settings.gap_open_score,
                )
                previous_gap_in_sequence_state = int(
                    np.argmax(previous_gap_in_sequence_scores)
                )
                gap_in_sequence_scores[profile_idx, sequence_idx] = (
                    previous_gap_in_sequence_scores[previous_gap_in_sequence_state]
                )
                gap_in_sequence_backpointers[profile_idx, sequence_idx] = (
                    previous_gap_in_sequence_state
                )

                previous_gap_in_profile_scores = (
                    match_scores[profile_idx, sequence_idx - 1]
                    + self.settings.gap_open_score,
                    gap_in_sequence_scores[profile_idx, sequence_idx - 1]
                    + self.settings.gap_open_score,
                    gap_in_profile_scores[profile_idx, sequence_idx - 1]
                    + self.settings.gap_extend_score,
                )
                previous_gap_in_profile_state = int(
                    np.argmax(previous_gap_in_profile_scores)
                )
                gap_in_profile_scores[profile_idx, sequence_idx] = (
                    previous_gap_in_profile_scores[previous_gap_in_profile_state]
                )
                gap_in_profile_backpointers[profile_idx, sequence_idx] = (
                    previous_gap_in_profile_state
                )

        final_scores = (
            match_scores[profile_length, sequence_length],
            gap_in_sequence_scores[profile_length, sequence_length],
            gap_in_profile_scores[profile_length, sequence_length],
        )
        state = int(np.argmax(final_scores))
        profile_idx = profile_length
        sequence_idx = sequence_length
        columns = []
        while profile_idx > 0 or sequence_idx > 0:
            if state == _STATE_MATCH:
                columns.append(
                    TimedAlignmentColumn(
                        (
                            *profile.columns[profile_idx - 1].tokens,
                            sequence.tokens[sequence_idx - 1],
                        )
                    )
                )
                state = int(match_backpointers[profile_idx, sequence_idx])
                profile_idx -= 1
                sequence_idx -= 1
            elif state == _STATE_GAP_IN_SEQUENCE:
                columns.append(
                    TimedAlignmentColumn(
                        (*profile.columns[profile_idx - 1].tokens, None)
                    )
                )
                state = int(gap_in_sequence_backpointers[profile_idx, sequence_idx])
                profile_idx -= 1
            elif state == _STATE_GAP_IN_PROFILE:
                columns.append(
                    TimedAlignmentColumn(
                        (
                            *(None for _ in profile.source_names),
                            sequence.tokens[sequence_idx - 1],
                        )
                    )
                )
                state = int(gap_in_profile_backpointers[profile_idx, sequence_idx])
                sequence_idx -= 1
            else:
                raise RuntimeError("Timed multiple alignment backtrace is incomplete.")
        columns.reverse()
        return TimedMultiSequenceAlignment(
            source_names=(*profile.source_names, sequence.name), columns=tuple(columns)
        )

    def _get_guide_orders(
        self, sequences: Sequence[TimedAlignmentSequence]
    ) -> tuple[tuple[TimedAlignmentSequence, ...], ...]:
        """Get pairwise-affinity progressive orders for a large source set."""
        pairwise_scores: dict[tuple[int, int], float] = {}
        for one_idx in range(len(sequences) - 1):
            for two_idx in range(one_idx + 1, len(sequences)):
                pairwise_alignment = self._align_in_order(
                    (sequences[one_idx], sequences[two_idx])
                )
                column_count = max(len(pairwise_alignment.columns), 1)
                pairwise_scores[(one_idx, two_idx)] = (
                    self._get_sum_of_pairs_score(pairwise_alignment) / column_count
                )

        orders = []
        seen_orders = set()
        for first_idx in range(len(sequences)):
            order = [first_idx]
            remaining = list(range(len(sequences)))
            remaining.remove(first_idx)
            while remaining:
                best_idx = remaining[0]
                best_score = float("-inf")
                for candidate_idx in remaining:
                    candidate_score = 0.0
                    for profile_idx in order:
                        pair = (
                            min(profile_idx, candidate_idx),
                            max(profile_idx, candidate_idx),
                        )
                        candidate_score += pairwise_scores[pair]
                    candidate_score /= len(order)
                    if candidate_score > best_score:
                        best_idx = candidate_idx
                        best_score = candidate_score
                order.append(best_idx)
                remaining.remove(best_idx)
            order_tuple = tuple(order)
            if order_tuple in seen_orders:
                continue
            seen_orders.add(order_tuple)
            orders.append(tuple(sequences[idx] for idx in order_tuple))
        return tuple(orders)

    def _get_profile_similarity(
        self, column: TimedAlignmentColumn, token: TimedAlignmentToken
    ) -> float:
        """Get mean similarity between a profile column and one token."""
        similarities = [
            self.similarity(profile_token, token)
            for profile_token in column.tokens
            if profile_token is not None
        ]
        return sum(similarities) / len(similarities)

    def _get_reordered(
        self, alignment: TimedMultiSequenceAlignment, source_names: tuple[str, ...]
    ) -> TimedMultiSequenceAlignment:
        """Reorder alignment rows to a requested stable source order."""
        indexes = tuple(alignment.source_names.index(name) for name in source_names)
        return TimedMultiSequenceAlignment(
            source_names=source_names,
            columns=tuple(
                TimedAlignmentColumn(tuple(column.tokens[idx] for idx in indexes))
                for column in alignment.columns
            ),
        )

    def _get_sum_of_pairs_score(self, alignment: TimedMultiSequenceAlignment) -> float:
        """Score a completed alignment across every projected source pair."""
        score = 0.0
        for one_idx in range(len(alignment.source_names) - 1):
            for two_idx in range(one_idx + 1, len(alignment.source_names)):
                gap_state = None
                for column in alignment.columns:
                    one = column.tokens[one_idx]
                    two = column.tokens[two_idx]
                    if one is None and two is None:
                        continue
                    if one is not None and two is not None:
                        score += self.similarity(one, two)
                        gap_state = None
                        continue
                    current_gap_state = one is None
                    if current_gap_state == gap_state:
                        score += self.settings.gap_extend_score
                    else:
                        score += self.settings.gap_open_score
                    gap_state = current_gap_state
        return score
