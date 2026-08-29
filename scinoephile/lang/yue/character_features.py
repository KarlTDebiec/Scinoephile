#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Yue character features used for text comparison."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

import pycantonese

from scinoephile.core.script import OpenCCConfig
from scinoephile.core.text import normalize_nfkc
from scinoephile.lang.zho.script.conversion import get_zho_text_converted

__all__ = ["CharacterFeatures"]

_EQUIVALENCE_GROUPS = (
    frozenset({"不", "唔"}),
    frozenset({"他", "佢", "她", "它"}),
    frozenset({"了", "咗"}),
    frozenset({"在", "喺"}),
    frozenset({"是", "係", "系"}),
    frozenset({"的", "嘅"}),
    frozenset({"這", "呢"}),
)
"""Common Mandarinized and Yue ASR substitutions."""


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
