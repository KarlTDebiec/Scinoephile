#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Yue-aware similarity scoring for timed alignment tokens."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from scinoephile.analysis.alignment.timed_msa.models import Token
from scinoephile.lang.yue.character_features import (
    CharacterRelationship,
    get_character_relationship,
)

__all__ = ["YueTokenSimilarity"]


@dataclass(frozen=True, slots=True, kw_only=True)
class YueTokenSimilarity:
    """Score timed Yue character substitutions by text and proximity."""

    exact_score: float = 6.0
    """Lexical score for identical characters."""
    script_variant_score: float = 5.5
    """Lexical score for Simplified/Traditional variants."""
    yue_equivalent_score: float = 5.0
    """Lexical score for known Yue/standard-Chinese equivalents."""
    same_jyutping_score: float = 4.0
    """Lexical score for identical Yue pronunciations including tone."""
    same_jyutping_base_score: float = 3.0
    """Lexical score for identical Yue syllables with differing tone."""
    substitution_score: float = -2.0
    """Lexical score for otherwise unrelated characters."""
    timing_weight: float = 2.0
    """Maximum magnitude of the temporal contribution."""
    timing_tolerance_seconds: float = 1.0
    """Midpoint distance over which positive temporal support decays to zero."""

    def __call__(self, one: Token, two: Token) -> float:
        """Score two timestamped characters.

        Arguments:
            one: first timestamped character
            two: second timestamped character
        Returns:
            combined lexical and temporal substitution score
        """
        lexical_score = self._get_lexical_score(one.text, two.text)
        one_midpoint = (one.start_seconds + one.end_seconds) / 2
        two_midpoint = (two.start_seconds + two.end_seconds) / 2
        midpoint_distance = abs(one_midpoint - two_midpoint)
        scaled_distance = midpoint_distance / self.timing_tolerance_seconds
        temporal_score = self.timing_weight * max(-1.0, 1.0 - scaled_distance)
        return lexical_score + temporal_score

    def __post_init__(self):
        """Validate score ordering and timing configuration.

        Raises:
            ValueError: if scores are out of order or timing settings are invalid
        """
        lexical_scores = (
            self.exact_score,
            self.script_variant_score,
            self.yue_equivalent_score,
            self.same_jyutping_score,
            self.same_jyutping_base_score,
            self.substitution_score,
        )
        if any(not isfinite(score) for score in lexical_scores):
            raise ValueError("Yue alignment lexical scores must be finite.")
        if any(
            left < right
            for left, right in zip(lexical_scores, lexical_scores[1:], strict=False)
        ):
            raise ValueError("Yue alignment lexical scores must be descending.")
        if not isfinite(self.timing_weight):
            raise ValueError("Yue alignment timing weight must be finite.")
        if self.timing_weight < 0.0:
            raise ValueError("Yue alignment timing weight must be non-negative.")
        if not isfinite(self.timing_tolerance_seconds):
            raise ValueError("Yue alignment timing tolerance must be finite.")
        if self.timing_tolerance_seconds <= 0.0:
            raise ValueError("Yue alignment timing tolerance must be positive.")

    def _get_lexical_score(self, one: str, two: str) -> float:
        """Get the substitution-matrix component for two characters.

        Arguments:
            one: first character
            two: second character
        Returns:
            Yue-aware lexical substitution score
        """
        relationship = get_character_relationship(one, two)
        if relationship is CharacterRelationship.EXACT:
            return self.exact_score
        if relationship is CharacterRelationship.SCRIPT_VARIANT:
            return self.script_variant_score
        if relationship is CharacterRelationship.EQUIVALENT:
            return self.yue_equivalent_score
        if relationship is CharacterRelationship.SAME_JYUTPING:
            return self.same_jyutping_score
        if relationship is CharacterRelationship.SAME_JYUTPING_BASE:
            return self.same_jyutping_base_score
        return self.substitution_score
