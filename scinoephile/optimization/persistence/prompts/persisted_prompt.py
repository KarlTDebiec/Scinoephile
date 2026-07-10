#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Persisted zero-shot LLM prompt model."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core import Language
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.llms import Manager, Prompt
from scinoephile.llms import PromptDefinition
from scinoephile.llms.prompt_definition import get_prompt_attribute_names

from .id import get_prompt_id

__all__ = ["PersistedPrompt"]


@dataclass(frozen=True, slots=True)
class PersistedPrompt:
    """An immutable zero-shot prompt loaded from SQLite."""

    prompt_id: str
    """Deterministic identifier derived from operation and prompt attributes."""
    operation: str
    """Operation to which this prompt belongs."""
    language: Language
    """Language in which the prompt corresponds with the LLM."""
    attributes: dict[str, str]
    """Effective string attributes that affect zero-shot execution."""
    aliases: tuple[str, ...]
    """Stable aliases currently associated with this prompt."""

    @classmethod
    def from_prompt_cls(
        cls,
        prompt_cls: type[Prompt],
        manager_cls: type[Manager],
    ) -> PersistedPrompt:
        """Convert a prompt class to its persisted representation.

        Arguments:
            prompt_cls: concrete zero-shot prompt class
            manager_cls: manager defining the prompt's operation and base contract
        Returns:
            persisted prompt
        Raises:
            ScinoephileError: if the prompt is incompatible or incomplete
        """
        if not issubclass(prompt_cls, manager_cls.prompt_cls):
            raise ScinoephileError(
                f"Prompt class {prompt_cls.__name__} is not compatible with "
                f"operation {manager_cls.operation}."
            )
        try:
            definition = PromptDefinition.from_prompt_cls(prompt_cls)
        except ValueError as exc:
            raise ScinoephileError(str(exc)) from exc
        attributes = dict(definition.attributes)
        _require_attributes(attributes, manager_cls)
        return cls(
            prompt_id=get_prompt_id(
                attributes,
                manager_cls.operation,
                definition.language,
            ),
            operation=manager_cls.operation,
            language=definition.language,
            attributes=attributes,
            aliases=(),
        )

    def to_prompt_cls(self, manager_cls: type[Manager]) -> type[Prompt]:
        """Reconstruct a runtime prompt class.

        Arguments:
            manager_cls: manager defining the prompt's operation and base contract
        Returns:
            runtime prompt class
        Raises:
            ScinoephileError: if the persisted prompt is incompatible or invalid
        """
        if self.operation != manager_cls.operation:
            raise ScinoephileError(
                f"Prompt operation {self.operation} does not match requested "
                f"operation {manager_cls.operation}."
            )
        expected_id = get_prompt_id(
            self.attributes,
            self.operation,
            self.language,
        )
        if self.prompt_id != expected_id:
            raise ScinoephileError(
                f"Prompt {self.prompt_id} does not match its content-addressed ID."
            )
        _require_attributes(self.attributes, manager_cls)
        definition = PromptDefinition.from_attributes(
            self.language,
            self.attributes,
        )
        return definition.get_prompt_cls(manager_cls.prompt_cls)


def _require_attributes(
    attributes: dict[str, str],
    manager_cls: type[Manager],
):
    """Require all attributes in a manager's zero-shot prompt contract.

    Arguments:
        attributes: prompt attributes to validate
        manager_cls: manager defining the required base contract
    Raises:
        ScinoephileError: if an attribute is missing or not string-valued
    """
    invalid_names = sorted(
        name
        for name, value in attributes.items()
        if not name or not isinstance(value, str)
    )
    if invalid_names:
        raise ScinoephileError(
            f"Prompt attributes must have nonempty names and string values: "
            f"{', '.join(invalid_names)}."
        )
    required_names = get_prompt_attribute_names(manager_cls.prompt_cls)
    missing_names = sorted(required_names - attributes.keys())
    if missing_names:
        raise ScinoephileError(
            f"Prompt for operation {manager_cls.operation} is missing attributes: "
            f"{', '.join(missing_names)}."
        )
