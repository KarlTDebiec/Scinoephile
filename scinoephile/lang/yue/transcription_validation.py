#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Cantonese scoring of transcription alignment evidence."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from functools import cache

import pycantonese

from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_text_converted
from scinoephile.llms.transcription import (
    TranscriptionAlignmentScorer,
    TranscriptionCharacterRelationship,
)

__all__ = ["CantoneseTranscriptionAlignmentScorer"]


_EQUIVALENCE_GROUPS = (
    frozenset({"不", "唔"}),
    frozenset({"他", "佢", "她", "它"}),
    frozenset({"了", "咗"}),
    frozenset({"在", "喺"}),
    frozenset({"是", "係", "系"}),
    frozenset({"的", "嘅"}),
    frozenset({"這", "呢"}),
)
"""Common Mandarinized and Cantonese ASR substitutions."""


@dataclass(frozen=True, slots=True)
class _CharacterFeatures:
    """Cached Cantonese comparison features for one character."""

    equivalence_groups: frozenset[int]
    """Known Cantonese equivalence-group indexes."""
    jyutping: str
    """Context-free Cantonese reading with tone, when available."""
    jyutping_base: str
    """Context-free Cantonese reading without tone, when available."""
    simplified: str
    """Compatibility-normalized Simplified Chinese form."""

    @classmethod
    @cache
    def get(cls, character: str) -> _CharacterFeatures:
        """Get cached script and Cantonese pronunciation features.

        Arguments:
            character: character for which to get features
        Returns:
            cached comparison features
        """
        nfkc = unicodedata.normalize("NFKC", character)
        simplified = get_zho_text_converted(
            nfkc, OpenCCConfig.t2s, apply_exclusions=False
        )
        traditional = get_zho_text_converted(
            nfkc, OpenCCConfig.s2t, apply_exclusions=False
        )
        script_forms = frozenset({nfkc, simplified, traditional})
        equivalence_groups = frozenset(
            group_idx
            for group_idx, group in enumerate(_EQUIVALENCE_GROUPS)
            if script_forms.intersection(group)
        )
        jyutping = ""
        if len(traditional) == 1:
            _, raw_jyutping = pycantonese.characters_to_jyutping([traditional])[0]
            if raw_jyutping is not None:
                jyutping = raw_jyutping
        return cls(
            equivalence_groups=equivalence_groups,
            jyutping=jyutping,
            jyutping_base=jyutping.rstrip("123456"),
            simplified=simplified,
        )


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

        one_features = _CharacterFeatures.get(one)
        two_features = _CharacterFeatures.get(two)
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
