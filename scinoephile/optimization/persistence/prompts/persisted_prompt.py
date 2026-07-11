#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Persisted zero-shot LLM prompt model."""

from __future__ import annotations

from dataclasses import dataclass, fields

from scinoephile.core import Language
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.llms import Manager, Prompt

from .id import get_prompt_id

__all__ = ["PersistedPrompt"]

_EXCLUDED_ZERO_SHOT_ATTRIBUTE_NAMES = frozenset(
    {
        "difficulty_description",
        "few_shot_answer_intro",
        "few_shot_description",
        "few_shot_intro",
        "few_shot_query_intro",
        "verified_description",
    }
)
"""Prompt fields that do not affect zero-shot execution."""


@dataclass(frozen=True, slots=True)
class PersistedPrompt:
    """An immutable zero-shot prompt loaded from SQLite."""

    prompt_id: str
    """Deterministic identifier derived from operation and prompt attributes."""
    operation: str
    """Operation to which this prompt belongs."""
    language: Language
    """Language in which the prompt corresponds with the LLM."""
    attributes: tuple[tuple[str, str], ...]
    """Ordered effective string attributes that affect zero-shot execution."""

    @classmethod
    def from_prompt(
        cls,
        prompt: Prompt,
        manager_cls: type[Manager],
    ) -> PersistedPrompt:
        """Convert a prompt to its persisted representation.

        Arguments:
            prompt: concrete zero-shot prompt
            manager_cls: manager defining the prompt's operation and contract
        Returns:
            persisted prompt
        Raises:
            ScinoephileError: if the prompt is incompatible or incomplete
        """
        if not isinstance(prompt, type(manager_cls.base_prompt)):
            raise ScinoephileError(
                f"Prompt type {type(prompt).__name__} is not compatible with "
                f"operation {manager_cls.operation}."
            )
        attributes = _get_zero_shot_attributes(prompt)
        return cls(
            prompt_id=get_prompt_id(
                attributes,
                manager_cls.operation,
                prompt.language,
            ),
            operation=manager_cls.operation,
            language=prompt.language,
            attributes=attributes,
        )


def _get_zero_shot_attributes(prompt: Prompt) -> tuple[tuple[str, str], ...]:
    """Get persisted string fields that affect zero-shot execution.

    Arguments:
        prompt: prompt whose zero-shot fields should be returned
    Returns:
        zero-shot prompt attributes keyed by field name
    """
    return tuple(
        sorted(
            (field.name, value)
            for field in fields(prompt)
            if field.name != "language"
            and field.name not in _EXCLUDED_ZERO_SHOT_ATTRIBUTE_NAMES
            and isinstance(value := getattr(prompt, field.name), str)
        )
    )
