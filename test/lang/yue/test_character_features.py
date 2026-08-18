#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of centralized Yue character relationships."""

from __future__ import annotations

from scinoephile.lang.yue.character_features import (
    CharacterRelationship,
    get_character_relationship,
)


def test_character_relationship_orders_flexible_yue_matches():
    """Central relationships should classify every supported match category."""
    relationships = (
        get_character_relationship("係", "係"),
        get_character_relationship("裡", "里"),
        get_character_relationship("不", "唔"),
        get_character_relationship("事", "是"),
        get_character_relationship("嗰", "個"),
        get_character_relationship("係", "八"),
    )

    assert relationships == (
        CharacterRelationship.exact,
        CharacterRelationship.script_variant,
        CharacterRelationship.equivalent,
        CharacterRelationship.same_jyutping,
        CharacterRelationship.same_jyutping_base,
        CharacterRelationship.unrelated,
    )
    assert get_character_relationship("系", "係") >= CharacterRelationship.equivalent
    assert (
        get_character_relationship("啊", "呀")
        >= CharacterRelationship.same_jyutping_base
    )
    assert get_character_relationship("下", "吓") >= CharacterRelationship.equivalent
    assert get_character_relationship("噶", "㗎") >= CharacterRelationship.equivalent
