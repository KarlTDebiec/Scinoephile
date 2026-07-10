#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for registered zero-shot prompt specifications."""

from __future__ import annotations

from scinoephile.core import Language
from scinoephile.optimization.operations import OPERATIONS
from scinoephile.optimization.persistence.prompts import PersistedPrompt
from scinoephile.optimization.prompt_specs import PROMPT_SPECS


def test_prompt_specs_are_stable_and_manager_compatible():
    """Registry aliases should be ordered and compatible with their managers."""
    assert tuple(PROMPT_SPECS) == tuple(sorted(PROMPT_SPECS))
    for alias, prompt_spec in PROMPT_SPECS.items():
        assert prompt_spec.alias == alias
        assert OPERATIONS[prompt_spec.manager_cls.operation] is prompt_spec.manager_cls
        assert issubclass(prompt_spec.prompt_cls, prompt_spec.manager_cls.prompt_cls)
        persisted = PersistedPrompt.from_prompt_cls(
            prompt_spec.prompt_cls,
            prompt_spec.manager_cls,
        )
        assert isinstance(persisted.language, Language)


def test_prompt_specs_preserve_distinct_workflow_aliases():
    """Equivalent workflow variants should retain aliases but share content."""
    first = PROMPT_SPECS["guided-review-eng-vs-yue-hans"]
    second = PROMPT_SPECS["guided-review-eng-vs-zho-hans"]

    first_prompt = PersistedPrompt.from_prompt_cls(
        first.prompt_cls,
        first.manager_cls,
    )
    second_prompt = PersistedPrompt.from_prompt_cls(
        second.prompt_cls,
        second.manager_cls,
    )

    assert first.alias != second.alias
    assert first_prompt.prompt_id == second_prompt.prompt_id
