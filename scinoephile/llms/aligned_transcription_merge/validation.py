#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Deterministic validation of merged text against aligned ASR evidence."""

from __future__ import annotations

import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass
from enum import IntEnum
from functools import cache
from math import floor

import pycantonese
from opencc import OpenCC

from scinoephile.core import Language

__all__ = [
    "AlignedTranscriptionMergeCharacterSupport",
    "AlignedTranscriptionMergeValidation",
    "get_aligned_transcription_merge_support_row",
    "get_aligned_transcription_merge_validation",
]

_ALIGNMENT_GAP_CHARACTER = "　"
"""Fullwidth ideographic space used for ordinary alignment gaps."""
_CANTONESE_EQUIVALENCE_GROUPS = (
    frozenset({"不", "唔"}),
    frozenset({"他", "佢", "她", "它"}),
    frozenset({"了", "咗"}),
    frozenset({"在", "喺"}),
    frozenset({"是", "係", "系"}),
    frozenset({"的", "嘅"}),
    frozenset({"這", "呢"}),
)
"""Common Mandarinized and Cantonese ASR substitutions."""
_GAP_SCORE = -3.0
"""Linear gap score used to project an answer onto an existing profile."""
_PAUSE_CHARACTER = "・"
"""Wide middle dot used for shared timed pauses."""
_SIMPLIFIER = OpenCC("t2s")
"""Converter used to compare Simplified and Traditional characters."""
_SUPPORT_CHARACTERS = "０１２３４５６７８９"
"""Ascending fullwidth-digit scale used to encode source support."""
_TRADITIONALIZER = OpenCC("s2t")
"""Converter used to obtain Traditional characters for Cantonese readings."""


class _CharacterRelationship(IntEnum):
    """Strength of source support for one merged character."""

    none = 0
    pronunciation = 1
    equivalent = 2
    exact = 3


@dataclass(frozen=True, slots=True)
class _CharacterFeatures:
    """Cached comparison features for one character."""

    equivalence_groups: frozenset[int]
    """Known Cantonese equivalence-group indexes."""
    jyutping: str
    """Context-free Cantonese reading with tone, when available."""
    jyutping_base: str
    """Context-free Cantonese reading without tone, when available."""
    nfkc: str
    """Compatibility-normalized character text."""
    simplified: str
    """Compatibility-normalized Simplified Chinese form."""


@dataclass(frozen=True, slots=True)
class AlignedTranscriptionMergeCharacterSupport:
    """Cross-source evidence supporting one lexical answer character."""

    answer_index: int
    """Zero-based character index in the lexical answer sequence."""
    character: str
    """Original answer character."""
    profile_column_index: int | None
    """Zero-based input alignment column, or None for an inserted character."""
    exact_source_count: int
    """Sources supporting the character exactly after compatibility normalization."""
    equivalent_source_count: int
    """Additional sources supporting a script or defined Cantonese equivalent."""
    pronunciation_source_count: int
    """Additional sources supporting only the same Cantonese pronunciation."""
    source_count: int
    """Successful ASR source rows considered."""

    @property
    def is_inserted(self) -> bool:
        """Whether the answer character aligned outside the input profile."""
        return self.profile_column_index is None

    @property
    def strong_source_count(self) -> int:
        """Get sources providing exact or defined-equivalent support."""
        return self.exact_source_count + self.equivalent_source_count

    @property
    def support_fraction(self) -> float:
        """Get the fraction of sources providing strong lexical support."""
        return self.strong_source_count / self.source_count


@dataclass(frozen=True, slots=True)
class AlignedTranscriptionMergeValidation:
    """Sequence-aware comparison of one merged answer with its ASR profile."""

    character_support: tuple[AlignedTranscriptionMergeCharacterSupport, ...]
    """Answer-character support in reading order."""
    majority_column_indexes: tuple[int, ...]
    """Input columns containing strict-majority lexical evidence."""
    mapped_majority_column_indexes: tuple[int, ...]
    """Strict-majority columns occupied by an answer character of any support."""
    preserved_majority_column_indexes: tuple[int, ...]
    """Strict-majority columns preserved by locally supported answer characters."""

    @property
    def majority_coverage(self) -> float:
        """Get the proportion of strict-majority columns preserved in order."""
        if not self.majority_column_indexes:
            return 1.0
        return len(self.preserved_majority_column_indexes) / len(
            self.majority_column_indexes
        )

    @property
    def unsupported_character_count(self) -> int:
        """Get answer characters lacking exact or defined-equivalent source support."""
        return sum(
            not support.strong_source_count for support in self.character_support
        )

    def preserves_required_majority(
        self, minimum_coverage: float, *, isolated_replacement_tolerance: int = 1
    ) -> bool:
        """Whether majority evidence meets coverage with a short-answer safeguard.

        The configured coverage may permit omissions in longer requests. For short
        requests, one mapped but unsupported replacement may also be tolerated so a
        contextual spelling correction does not block the merger. The tolerance never
        excuses a majority column omitted from the answer entirely.

        Arguments:
            minimum_coverage: minimum proportion of majority columns to preserve
            isolated_replacement_tolerance: maximum mapped unsupported replacements
                tolerated when proportional coverage would otherwise permit none
        Returns:
            whether the answer passes deterministic majority preservation
        Raises:
            ValueError: if either validation setting is outside its accepted range
        """
        if not 0.0 <= minimum_coverage <= 1.0:
            raise ValueError("Minimum majority coverage must be between zero and one.")
        if isolated_replacement_tolerance < 0:
            raise ValueError("Isolated replacement tolerance must be non-negative.")
        missing_columns = set(self.majority_column_indexes) - set(
            self.preserved_majority_column_indexes
        )
        proportional_tolerance = floor(
            len(self.majority_column_indexes) * (1.0 - minimum_coverage) + 1e-12
        )
        if len(missing_columns) <= proportional_tolerance:
            return True
        if not missing_columns.issubset(self.mapped_majority_column_indexes):
            return False
        return len(missing_columns) <= max(
            proportional_tolerance, isolated_replacement_tolerance
        )


def get_aligned_transcription_merge_support_row(
    source_texts: Sequence[str], merged_text: str, language: Language
) -> str:
    """Get a compact fullwidth-digit support row for an aligned merged row.

    Arguments:
        source_texts: equal-width aligned ASR rows
        merged_text: merged row aligned to the same profile
        language: transcription language controlling Cantonese equivalence
    Returns:
        fullwidth support digits, gaps, and shared pause characters
    Raises:
        ValueError: if fewer than two sources are provided or row widths differ
    """
    _validate_rows(source_texts, merged_text)
    source_count = len(source_texts)
    output = []
    for column_idx, merged_character in enumerate(merged_text):
        if merged_character == _ALIGNMENT_GAP_CHARACTER:
            output.append(_ALIGNMENT_GAP_CHARACTER)
            continue
        if merged_character == _PAUSE_CHARACTER:
            output.append(_PAUSE_CHARACTER)
            continue
        relationships = (
            _get_character_relationship(
                merged_character, source_text[column_idx], language
            )
            for source_text in source_texts
            if source_text[column_idx]
            not in {_ALIGNMENT_GAP_CHARACTER, _PAUSE_CHARACTER}
        )
        strong_source_count = sum(
            relationship >= _CharacterRelationship.equivalent
            for relationship in relationships
        )
        support_level = min(
            len(_SUPPORT_CHARACTERS) - 1,
            int(
                strong_source_count / source_count * (len(_SUPPORT_CHARACTERS) - 1)
                + 0.5
            ),
        )
        output.append(_SUPPORT_CHARACTERS[support_level])
    return "".join(output)


def get_aligned_transcription_merge_validation(
    source_texts: Sequence[str], answer_text: str, language: Language
) -> AlignedTranscriptionMergeValidation:
    """Align a lexical answer to an ASR profile and quantify its evidence support.

    Arguments:
        source_texts: equal-width aligned ASR rows
        answer_text: unaligned merged transcript, with optional punctuation
        language: transcription language controlling Cantonese equivalence
    Returns:
        deterministic sequence-aware validation result
    Raises:
        ValueError: if fewer than two sources are provided or row widths differ
    """
    _validate_rows(source_texts)
    source_count = len(source_texts)
    profile_columns = tuple(
        (
            column_idx,
            tuple(
                source_text[column_idx]
                for source_text in source_texts
                if source_text[column_idx]
                not in {_ALIGNMENT_GAP_CHARACTER, _PAUSE_CHARACTER}
            ),
        )
        for column_idx in range(len(source_texts[0]))
        if any(
            source_text[column_idx] not in {_ALIGNMENT_GAP_CHARACTER, _PAUSE_CHARACTER}
            for source_text in source_texts
        )
    )
    answer_characters = tuple(
        character for character in answer_text if _is_lexical_character(character)
    )
    answer_profile_indexes = _get_answer_profile_indexes(
        profile_columns, answer_characters, source_count, language
    )

    support = []
    answer_index_by_profile_column = {}
    profile_characters_by_index = dict(profile_columns)
    for answer_idx, (character, profile_column_idx) in enumerate(
        zip(answer_characters, answer_profile_indexes, strict=True)
    ):
        relationships = []
        if profile_column_idx is not None:
            answer_index_by_profile_column[profile_column_idx] = answer_idx
            relationships = [
                _get_character_relationship(character, source_character, language)
                for source_character in profile_characters_by_index[profile_column_idx]
            ]
        support.append(
            AlignedTranscriptionMergeCharacterSupport(
                answer_index=answer_idx,
                character=character,
                profile_column_index=profile_column_idx,
                exact_source_count=relationships.count(_CharacterRelationship.exact),
                equivalent_source_count=relationships.count(
                    _CharacterRelationship.equivalent
                ),
                pronunciation_source_count=relationships.count(
                    _CharacterRelationship.pronunciation
                ),
                source_count=source_count,
            )
        )

    majority_columns = []
    mapped_majority_columns = []
    preserved_majority_columns = []
    for profile_column_idx, source_characters in profile_columns:
        majority_character = _get_majority_character(
            source_characters, source_count, language
        )
        if majority_character is None:
            continue
        majority_columns.append(profile_column_idx)
        answer_idx = answer_index_by_profile_column.get(profile_column_idx)
        if answer_idx is None:
            continue
        mapped_majority_columns.append(profile_column_idx)
        answer_character = answer_characters[answer_idx]
        if any(
            _get_character_relationship(answer_character, source_character, language)
            >= _CharacterRelationship.equivalent
            for source_character in source_characters
        ):
            preserved_majority_columns.append(profile_column_idx)

    return AlignedTranscriptionMergeValidation(
        character_support=tuple(support),
        majority_column_indexes=tuple(majority_columns),
        mapped_majority_column_indexes=tuple(mapped_majority_columns),
        preserved_majority_column_indexes=tuple(preserved_majority_columns),
    )


@cache
def _get_character_features(character: str) -> _CharacterFeatures:
    """Get reusable compatibility, script, and Cantonese pronunciation features."""
    nfkc = unicodedata.normalize("NFKC", character)
    simplified = _SIMPLIFIER.convert(nfkc)
    traditional = _TRADITIONALIZER.convert(nfkc)
    script_forms = frozenset({nfkc, simplified, traditional})
    equivalence_groups = frozenset(
        group_idx
        for group_idx, group in enumerate(_CANTONESE_EQUIVALENCE_GROUPS)
        if script_forms.intersection(group)
    )
    jyutping = ""
    if len(traditional) == 1:
        _, raw_jyutping = pycantonese.characters_to_jyutping([traditional])[0]
        if raw_jyutping is not None:
            jyutping = raw_jyutping
    return _CharacterFeatures(
        equivalence_groups=equivalence_groups,
        jyutping=jyutping,
        jyutping_base=jyutping.rstrip("123456"),
        nfkc=nfkc,
        simplified=simplified,
    )


def _get_answer_profile_indexes(
    profile_columns: Sequence[tuple[int, tuple[str, ...]]],
    answer_characters: Sequence[str],
    source_count: int,
    language: Language,
) -> tuple[int | None, ...]:
    """Project answer characters onto fixed profile columns using global alignment."""
    profile_length = len(profile_columns)
    answer_length = len(answer_characters)
    scores = [[float("-inf")] * (answer_length + 1) for _ in range(profile_length + 1)]
    backpointers = [[-1] * (answer_length + 1) for _ in range(profile_length + 1)]
    scores[0][0] = 0.0
    for profile_idx in range(1, profile_length + 1):
        scores[profile_idx][0] = profile_idx * _GAP_SCORE
        backpointers[profile_idx][0] = 1
    for answer_idx in range(1, answer_length + 1):
        scores[0][answer_idx] = answer_idx * _GAP_SCORE
        backpointers[0][answer_idx] = 2

    for profile_idx, (_, source_characters) in enumerate(profile_columns, start=1):
        for answer_idx, answer_character in enumerate(answer_characters, start=1):
            relationships = tuple(
                _get_character_relationship(
                    answer_character, source_character, language
                )
                for source_character in source_characters
            )
            profile_score = max(map(_get_relationship_score, relationships))
            strong_source_count = sum(
                relationship >= _CharacterRelationship.equivalent
                for relationship in relationships
            )
            profile_score += 2.0 * strong_source_count / source_count
            best_score = scores[profile_idx - 1][answer_idx - 1] + profile_score
            best_state = 0
            gap_in_answer_score = scores[profile_idx - 1][answer_idx] + _GAP_SCORE
            if gap_in_answer_score > best_score:
                best_score = gap_in_answer_score
                best_state = 1
            gap_in_profile_score = scores[profile_idx][answer_idx - 1] + _GAP_SCORE
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
            raise RuntimeError("Unable to backtrack aligned merge validation.")
    return tuple(answer_profile_indexes)


def _get_character_relationship(
    one: str, two: str, language: Language
) -> _CharacterRelationship:
    """Classify lexical support between two characters."""
    one_features = _get_character_features(one)
    two_features = _get_character_features(two)
    if one_features.nfkc == two_features.nfkc:
        return _CharacterRelationship.exact
    if one_features.simplified == two_features.simplified:
        return _CharacterRelationship.equivalent
    if language.is_cantonese and one_features.equivalence_groups.intersection(
        two_features.equivalence_groups
    ):
        return _CharacterRelationship.equivalent
    if language.is_cantonese and (
        one_features.jyutping
        and one_features.jyutping == two_features.jyutping
        or one_features.jyutping_base
        and one_features.jyutping_base == two_features.jyutping_base
    ):
        return _CharacterRelationship.pronunciation
    return _CharacterRelationship.none


def _get_majority_character(
    source_characters: Sequence[str], source_count: int, language: Language
) -> str | None:
    """Get a representative character with strict strong-equivalent support."""
    best_character = None
    best_count = 0
    for candidate in source_characters:
        count = sum(
            _get_character_relationship(candidate, character, language)
            >= _CharacterRelationship.equivalent
            for character in source_characters
        )
        if count > best_count:
            best_character = candidate
            best_count = count
    if best_count > source_count / 2:
        return best_character
    return None


def _get_relationship_score(relationship: _CharacterRelationship) -> float:
    """Get the profile-alignment substitution score for a relationship."""
    if relationship is _CharacterRelationship.exact:
        return 6.0
    if relationship is _CharacterRelationship.equivalent:
        return 5.0
    if relationship is _CharacterRelationship.pronunciation:
        return 3.0
    return -2.0


def _is_lexical_character(character: str) -> bool:
    """Whether a character participates in merge validation alignment."""
    return not unicodedata.category(character).startswith(("C", "P", "S", "Z"))


def _validate_rows(source_texts: Sequence[str], merged_text: str | None = None):
    """Validate aligned source and optional merged row widths."""
    if len(source_texts) < 2:
        raise ValueError("Aligned merge validation requires at least two sources.")
    row_lengths = {len(source_text) for source_text in source_texts}
    if merged_text is not None:
        row_lengths.add(len(merged_text))
    if len(row_lengths) != 1 or not next(iter(row_lengths)):
        raise ValueError("Aligned merge validation rows must have equal nonzero width.")
