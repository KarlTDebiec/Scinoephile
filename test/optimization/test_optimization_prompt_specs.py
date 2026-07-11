#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for registered prompt specifications."""

from __future__ import annotations

from scinoephile.core import Language
from scinoephile.optimization.operations import OPERATIONS
from scinoephile.optimization.persistence.prompts import PersistedPrompt
from scinoephile.optimization.prompt_specs import PROMPT_SPECS


def test_prompt_specs_are_stable_and_manager_compatible():
    """Registry aliases should be ordered and compatible with their managers."""
    assert tuple(PROMPT_SPECS) == tuple(sorted(PROMPT_SPECS))
    for prompt_spec in PROMPT_SPECS.values():
        assert OPERATIONS[prompt_spec.manager_cls.operation] is prompt_spec.manager_cls
        assert isinstance(prompt_spec.prompt, type(prompt_spec.manager_cls.base_prompt))
        persisted = PersistedPrompt.from_prompt(
            prompt_spec.prompt,
            prompt_spec.manager_cls,
        )
        assert isinstance(persisted.language, Language)
