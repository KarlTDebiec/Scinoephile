#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Persisted LLM prompt model."""

from __future__ import annotations

from dataclasses import dataclass, fields

from scinoephile.core import Language
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.llms import Manager, Prompt

from .id import get_prompt_id

__all__ = ["PersistedPrompt"]


@dataclass(frozen=True, slots=True)
class PersistedPrompt:
    """An immutable prompt loaded from SQLite."""

    prompt_id: str
    """Deterministic identifier derived from operation and prompt attributes."""
    operation: str
    """Operation to which this prompt belongs."""
    language: Language
    """Language in which the prompt corresponds with the LLM."""
    attributes: tuple[tuple[str, str], ...]
    """Ordered effective string attributes."""

    @classmethod
    def from_prompt(
        cls,
        prompt: Prompt,
        manager_cls: type[Manager],
    ) -> PersistedPrompt:
        """Convert a prompt to its persisted representation.

        Arguments:
            prompt: concrete prompt
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
        attributes = tuple(
            sorted(
                (field.name, value)
                for field in fields(prompt)
                if field.name != "language"
                and isinstance(value := getattr(prompt, field.name), str)
            )
        )
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
