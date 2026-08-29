#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Yue character features used for text comparison."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from functools import cache

import pycantonese

from scinoephile.core.script import OpenCCConfig
from scinoephile.core.text import normalize_nfkc
from scinoephile.lang.zho.script.conversion import get_zho_text_converted

__all__ = ["CharacterFeatures", "CharacterRelationship", "get_character_relationship"]

_EQUIVALENCE_GROUPS = (
    frozenset({"不", "唔"}),
    frozenset({"他", "佢", "她", "它"}),
    frozenset({"了", "咗"}),
    frozenset({"在", "喺"}),
    frozenset({"是", "係", "系"}),
    frozenset({"的", "嘅"}),
    frozenset({"這", "呢"}),
    frozenset({"下", "吓"}),
    frozenset({"噶", "㗎"}),
)
"""Common Mandarinized and Yue ASR substitutions."""


class CharacterRelationship(IntEnum):
    """Strength of Yue evidence relating two characters."""

    UNRELATED = 0
    """No known lexical or pronunciation relationship."""
    SAME_JYUTPING_BASE = 1
    """Same context-free Yue syllable with different tone."""
    SAME_JYUTPING = 2
    """Same context-free Yue pronunciation including tone."""
    EQUIVALENT = 3
    """Known Yue and standard-Chinese equivalents."""
    SCRIPT_VARIANT = 4
    """Simplified or Traditional forms of the same character."""
    EXACT = 5
    """Compatibility-normalized exact match."""


@dataclass(frozen=True, slots=True)
class CharacterFeatures:
    """Cached Yue comparison features for one character."""

    equivalence_groups: frozenset[int]
    """Known Yue equivalence-group indexes."""
    jyutping: str
    """Context-free Yue reading with tone, when available."""
    jyutping_base: str
    """Context-free Yue reading without tone, when available."""
    simplified: str
    """Compatibility-normalized Simplified Chinese form."""

    @classmethod
    @cache
    def get(cls, character: str) -> CharacterFeatures:
        """Get cached script and Yue pronunciation features.

        Arguments:
            character: character for which to get features
        Returns:
            cached comparison features
        """
        nfkc = normalize_nfkc(character)
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


def get_character_relationship(one: str, two: str) -> CharacterRelationship:
    """Classify the shared Yue evidence between two characters.

    Arguments:
        one: first character
        two: second character
    Returns:
        strongest known Yue relationship
    """
    if normalize_nfkc(one) == normalize_nfkc(two):
        return CharacterRelationship.EXACT
    one_features = CharacterFeatures.get(one)
    two_features = CharacterFeatures.get(two)
    if one_features.simplified == two_features.simplified:
        return CharacterRelationship.SCRIPT_VARIANT
    if one_features.equivalence_groups.intersection(two_features.equivalence_groups):
        return CharacterRelationship.EQUIVALENT
    if one_features.jyutping and one_features.jyutping == two_features.jyutping:
        return CharacterRelationship.SAME_JYUTPING
    if (
        one_features.jyutping_base
        and one_features.jyutping_base == two_features.jyutping_base
    ):
        return CharacterRelationship.SAME_JYUTPING_BASE
    return CharacterRelationship.UNRELATED
