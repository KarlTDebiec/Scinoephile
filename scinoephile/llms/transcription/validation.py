#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Deterministic validation of transcription against aligned ASR evidence."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import IntEnum
from math import floor
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

    @property
    def majority_coverage(self) -> float:
        """Get the proportion of strict-majority columns preserved in order."""
        if not self.majority_column_count:
            return 1.0
        return self.preserved_majority_column_count / self.majority_column_count

    def preserves_required_majority(self, minimum_coverage: float) -> bool:
        """Whether majority evidence meets coverage with a short-answer safeguard.

        The configured coverage may permit omissions in longer requests. For short
        requests, one mapped but unsupported replacement may also be tolerated so a
        contextual spelling correction does not block transcription. The tolerance
        never excuses a majority column omitted from the answer entirely.

        Arguments:
            minimum_coverage: minimum proportion of majority columns to preserve
        Returns:
            whether the answer passes deterministic majority preservation
        Raises:
            ValueError: if minimum coverage is outside its accepted range
        """
        if not 0.0 <= minimum_coverage <= 1.0:
            raise ValueError("Minimum majority coverage must be between zero and one.")
        missing_column_count = (
            self.majority_column_count - self.preserved_majority_column_count
        )
        proportional_tolerance = floor(
            self.majority_column_count * (1.0 - minimum_coverage) + 1e-12
        )
        if missing_column_count <= proportional_tolerance:
            return True
        if self.mapped_majority_column_count < self.majority_column_count:
            return False
        return missing_column_count <= max(proportional_tolerance, 1)


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
        for profile_column_idx, source_characters in profile_columns:
            if not self._has_strict_majority(source_characters, source_count):
                continue
            majority_column_count += 1
            answer_idx = answer_index_by_profile_column.get(profile_column_idx)
            if answer_idx is None:
                continue
            mapped_majority_column_count += 1
            answer_character = answer_characters[answer_idx]
            if any(
                self.get_character_relationship(answer_character, source_character)
                >= TranscriptionCharacterRelationship.equivalent
                for source_character in source_characters
            ):
                preserved_majority_column_count += 1

        return TranscriptionValidation(
            majority_column_count=majority_column_count,
            mapped_majority_column_count=mapped_majority_column_count,
            preserved_majority_column_count=preserved_majority_column_count,
        )

    def _get_answer_profile_indexes(
        self,
        profile_columns: Sequence[tuple[int, tuple[str, ...]]],
        answer_characters: Sequence[str],
        source_count: int,
    ) -> tuple[int | None, ...]:
        """Project answer characters onto fixed profile columns.

        Arguments:
            profile_columns: indexed source-character profile columns
            answer_characters: answer characters to project
            source_count: total number of transcription sources
        Returns:
            profile column index for each answer character, when mapped
        """
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
                profile_score = max(map(self._get_relationship_score, relationships))
                strong_source_count = sum(
                    relationship >= TranscriptionCharacterRelationship.equivalent
                    for relationship in relationships
                )
                profile_score += 2.0 * strong_source_count / source_count
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

    def _has_strict_majority(
        self, source_characters: Sequence[str], source_count: int
    ) -> bool:
        """Check whether any character has strict strong-equivalent source support.

        Arguments:
            source_characters: source characters in one profile column
            source_count: total number of transcription sources
        Returns:
            whether one character has strict majority support
        """
        for candidate in source_characters:
            count = sum(
                self.get_character_relationship(candidate, character)
                >= TranscriptionCharacterRelationship.equivalent
                for character in source_characters
            )
            if count > source_count / 2:
                return True
        return False

    @staticmethod
    def _get_relationship_score(
        relationship: TranscriptionCharacterRelationship,
    ) -> float:
        """Get the profile-alignment substitution score for a relationship.

        Arguments:
            relationship: relationship between answer and source characters
        Returns:
            substitution score
        """
        if relationship is TranscriptionCharacterRelationship.exact:
            return 6.0
        if relationship is TranscriptionCharacterRelationship.equivalent:
            return 5.0
        if relationship is TranscriptionCharacterRelationship.pronunciation:
            return 3.0
        return -2.0


def _validate_rows(source_texts: Sequence[str]):
    """Validate aligned source row widths.

    Arguments:
        source_texts: aligned source rows
    """
    if not source_texts:
        raise ValueError("Transcription validation requires at least one source.")
    row_lengths = {len(source_text) for source_text in source_texts}
    if len(row_lengths) != 1 or not next(iter(row_lengths)):
        raise ValueError("Transcription validation rows must have equal nonzero width.")
