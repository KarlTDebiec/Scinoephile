#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Cantonese scoring of transcription alignment evidence."""

from __future__ import annotations

from scinoephile.lang.yue.character_features import CharacterFeatures
from scinoephile.llms.transcription import (
    TranscriptionAlignmentScorer,
    TranscriptionCharacterRelationship,
)

__all__ = ["CantoneseTranscriptionAlignmentScorer"]


class CantoneseTranscriptionAlignmentScorer(TranscriptionAlignmentScorer):
    """Score transcription alignment using Cantonese character relationships."""

    def get_character_relationship(
        self, one: str, two: str
    ) -> TranscriptionCharacterRelationship:
        """Classify Cantonese support between two characters.

        Arguments:
            one: first character
            two: second character
        Returns:
            relationship between the characters
        """
        relationship = super().get_character_relationship(one, two)
        if relationship is TranscriptionCharacterRelationship.exact:
            return relationship

        one_features = CharacterFeatures.get(one)
        two_features = CharacterFeatures.get(two)
        if one_features.simplified == two_features.simplified:
            return TranscriptionCharacterRelationship.equivalent
        if one_features.equivalence_groups.intersection(
            two_features.equivalence_groups
        ):
            return TranscriptionCharacterRelationship.equivalent

        matching_pronunciation = (
            one_features.jyutping and one_features.jyutping == two_features.jyutping
        ) or (
            one_features.jyutping_base
            and one_features.jyutping_base == two_features.jyutping_base
        )
        if matching_pronunciation:
            return TranscriptionCharacterRelationship.pronunciation
        return TranscriptionCharacterRelationship.none
