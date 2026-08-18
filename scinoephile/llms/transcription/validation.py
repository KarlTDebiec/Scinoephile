#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Deterministic validation of transcription against aligned ASR evidence."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import IntEnum
from typing import ClassVar

from scinoephile.core.text import is_lexical_character, normalize_nfkc

__all__ = [
    "TranscriptionAlignmentScorer",
    "TranscriptionCharacterRelationship",
    "TranscriptionValidation",
]


class TranscriptionCharacterRelationship(IntEnum):
    """Strength of source support for one answer character."""

    none = 0
    pronunciation = 1
    equivalent = 2
    exact = 3


@dataclass(frozen=True, slots=True)
class TranscriptionValidation:
    """Sequence-aware comparison of one answer with its ASR profile."""

    majority_column_count: int
    """Number of input columns containing strict-majority lexical evidence."""
    mapped_majority_column_count: int
    """Number of strict-majority columns occupied by an answer character."""
    preserved_majority_column_count: int
    """Number of strict-majority columns preserved by supported answer characters."""
    longest_unpreserved_consensus_text: str
    """Representative text of the longest unpreserved strong-consensus run."""

    @property
    def longest_unpreserved_consensus_run(self) -> int:
        """Get the longest consecutive run of unpreserved consensus columns."""
        return len(self.longest_unpreserved_consensus_text)

    @property
    def majority_coverage(self) -> float:
        """Get the proportion of strict-majority columns preserved in order."""
        if not self.majority_column_count:
            return 1.0
        return self.preserved_majority_column_count / self.majority_column_count

    @property
    def mapped_majority_coverage(self) -> float:
        """Get the proportion of majority columns occupied by answer text."""
        if not self.majority_column_count:
            return 1.0
        return self.mapped_majority_column_count / self.majority_column_count

    def preserves_consensus(self, maximum_unpreserved_columns: int) -> bool:
        """Whether the answer avoids a long omission of strong consensus evidence.

        Arguments:
            maximum_unpreserved_columns: maximum permitted consecutive omissions
        Returns:
            whether the answer passes deterministic consensus preservation
        Raises:
            ValueError: if the maximum is negative
        """
        if maximum_unpreserved_columns < 0:
            raise ValueError("Maximum unpreserved column count must be non-negative.")
        return self.longest_unpreserved_consensus_run <= maximum_unpreserved_columns


class TranscriptionAlignmentScorer:
    """Align answers with ASR evidence using language-neutral character support."""

    gap_score: ClassVar[float] = -3.0
    """Linear gap score used to project an answer onto an existing profile."""

    def get_character_relationship(
        self, one: str, two: str
    ) -> TranscriptionCharacterRelationship:
        """Classify language-neutral support between two characters.

        Arguments:
            one: first character
            two: second character
        Returns:
            relationship between the characters
        """
        if normalize_nfkc(one) == normalize_nfkc(two):
            return TranscriptionCharacterRelationship.exact
        return TranscriptionCharacterRelationship.none

    def score(
        self, source_texts: Sequence[str], answer_text: str
    ) -> TranscriptionValidation:
        """Align an answer to ASR evidence and quantify majority preservation.

        Arguments:
            source_texts: equal-width aligned ASR rows
            answer_text: unaligned consensus transcript, with optional punctuation
        Returns:
            deterministic sequence-aware validation result
        Raises:
            ValueError: if no sources are provided or row widths differ
        """
        _validate_rows(source_texts)
        source_count = len(source_texts)
        profile_columns = tuple(
            (
                column_idx,
                tuple(
                    source_text[column_idx]
                    for source_text in source_texts
                    if is_lexical_character(source_text[column_idx])
                ),
            )
            for column_idx in range(len(source_texts[0]))
            if any(
                is_lexical_character(source_text[column_idx])
                for source_text in source_texts
            )
        )
        answer_characters = tuple(
            character for character in answer_text if is_lexical_character(character)
        )
        answer_profile_indexes = self._get_answer_profile_indexes(
            profile_columns, answer_characters, source_count
        )

        answer_index_by_profile_column = {
            profile_column_idx: answer_idx
            for answer_idx, profile_column_idx in enumerate(answer_profile_indexes)
            if profile_column_idx is not None
        }

        majority_column_count = 0
        mapped_majority_column_count = 0
        preserved_majority_column_count = 0
        missing_consensus_characters: list[str | None] = []
        unpreserved_consensus_characters: list[str | None] = []
        majority_source_count = source_count // 2 + 1
        strong_consensus_source_count = max(majority_source_count, source_count - 1)
        for profile_column_idx, source_characters in profile_columns:
            majority_character = self._get_consensus_character(
                source_characters, majority_source_count
            )
            if majority_character is None:
                missing_consensus_characters.append(None)
                unpreserved_consensus_characters.append(None)
                continue
            majority_column_count += 1
            answer_idx = answer_index_by_profile_column.get(profile_column_idx)
            is_preserved = False
            if answer_idx is not None:
                mapped_majority_column_count += 1
                answer_character = answer_characters[answer_idx]
                is_preserved = (
                    self.get_character_relationship(
                        answer_character, majority_character
                    )
                    >= TranscriptionCharacterRelationship.pronunciation
                )
            if is_preserved:
                preserved_majority_column_count += 1

            consensus_character = self._get_consensus_character(
                source_characters, strong_consensus_source_count
            )
            missing_consensus_characters.append(
                consensus_character if answer_idx is None else None
            )
            unpreserved_consensus_characters.append(
                consensus_character
                if consensus_character and not is_preserved
                else None
            )

        longest_unpreserved_consensus_text = _get_longest_run_text(
            missing_consensus_characters
        )
        if not preserved_majority_column_count:
            longest_unpreserved_consensus_text = _get_longest_run_text(
                unpreserved_consensus_characters
            )

        return TranscriptionValidation(
            majority_column_count=majority_column_count,
            mapped_majority_column_count=mapped_majority_column_count,
            preserved_majority_column_count=preserved_majority_column_count,
            longest_unpreserved_consensus_text=longest_unpreserved_consensus_text,
        )

    def _get_answer_profile_indexes(
        self,
        profile_columns: Sequence[tuple[int, tuple[str, ...]]],
        answer_characters: Sequence[str],
        source_count: int,
    ) -> tuple[int | None, ...]:
        """Project answer characters onto fixed profile columns."""
        profile_length = len(profile_columns)
        answer_length = len(answer_characters)
        scores = [
            [float("-inf")] * (answer_length + 1) for _ in range(profile_length + 1)
        ]
        backpointers = [[-1] * (answer_length + 1) for _ in range(profile_length + 1)]
        scores[0][0] = 0.0
        for profile_idx in range(1, profile_length + 1):
            scores[profile_idx][0] = profile_idx * self.gap_score
            backpointers[profile_idx][0] = 1
        for answer_idx in range(1, answer_length + 1):
            scores[0][answer_idx] = answer_idx * self.gap_score
            backpointers[0][answer_idx] = 2

        for profile_idx, (_, source_characters) in enumerate(profile_columns, start=1):
            for answer_idx, answer_character in enumerate(answer_characters, start=1):
                relationships = tuple(
                    self.get_character_relationship(answer_character, source_character)
                    for source_character in source_characters
                )
                relationship_scores = tuple(
                    self._get_relationship_score(relationship)
                    for relationship in relationships
                )
                missing_source_count = source_count - len(relationship_scores)
                profile_score = (
                    sum(relationship_scores)
                    + missing_source_count
                    * self._get_relationship_score(
                        TranscriptionCharacterRelationship.none
                    )
                ) / source_count
                best_score = scores[profile_idx - 1][answer_idx - 1] + profile_score
                best_state = 0
                gap_in_answer_score = (
                    scores[profile_idx - 1][answer_idx] + self.gap_score
                )
                if gap_in_answer_score > best_score:
                    best_score = gap_in_answer_score
                    best_state = 1
                gap_in_profile_score = (
                    scores[profile_idx][answer_idx - 1] + self.gap_score
                )
                if gap_in_profile_score > best_score:
                    best_score = gap_in_profile_score
                    best_state = 2
                scores[profile_idx][answer_idx] = best_score
                backpointers[profile_idx][answer_idx] = best_state

        answer_profile_indexes: list[int | None] = [None] * answer_length
        profile_idx = profile_length
        answer_idx = answer_length
        while profile_idx or answer_idx:
            state = backpointers[profile_idx][answer_idx]
            if state == 0:
                profile_column_idx = profile_columns[profile_idx - 1][0]
                answer_profile_indexes[answer_idx - 1] = profile_column_idx
                profile_idx -= 1
                answer_idx -= 1
            elif state == 1:
                profile_idx -= 1
            elif state == 2:
                answer_idx -= 1
            else:
                raise RuntimeError("Unable to backtrack transcription validation.")
        return tuple(answer_profile_indexes)

    def _get_consensus_character(
        self, source_characters: Sequence[str], required_source_count: int
    ) -> str | None:
        """Get a representative of the strongest sufficiently supported group."""
        consensus_character = None
        consensus_count = required_source_count - 1
        for candidate in source_characters:
            count = sum(
                self.get_character_relationship(candidate, character)
                >= TranscriptionCharacterRelationship.equivalent
                for character in source_characters
            )
            if count > consensus_count:
                consensus_character = candidate
                consensus_count = count
        return consensus_character

    @staticmethod
    def _get_relationship_score(
        relationship: TranscriptionCharacterRelationship,
    ) -> float:
        """Get the profile-alignment substitution score for a relationship."""
        if relationship is TranscriptionCharacterRelationship.exact:
            return 6.0
        if relationship is TranscriptionCharacterRelationship.equivalent:
            return 5.0
        if relationship is TranscriptionCharacterRelationship.pronunciation:
            return 3.0
        return -2.0


def _get_longest_run_text(characters: Sequence[str | None]) -> str:
    """Get the text of the longest run not interrupted by a missing character."""
    longest_text = ""
    current_characters = []
    for character in characters:
        if character is not None:
            current_characters.append(character)
            continue
        if len(current_characters) > len(longest_text):
            longest_text = "".join(current_characters)
        current_characters = []
    if len(current_characters) > len(longest_text):
        longest_text = "".join(current_characters)
    return longest_text


def _validate_rows(source_texts: Sequence[str]):
    """Validate aligned source row widths."""
    if not source_texts:
        raise ValueError("Transcription validation requires at least one source.")
    row_lengths = {len(source_text) for source_text in source_texts}
    if len(row_lengths) != 1 or not next(iter(row_lengths)):
        raise ValueError("Transcription validation rows must have equal nonzero width.")
