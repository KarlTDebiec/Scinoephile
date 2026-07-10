#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Immutable text and field configuration for LLM correspondence."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import ClassVar, Self

from scinoephile.core.language import Language

__all__ = ["Prompt"]

_EXCLUDED_ZERO_SHOT_ATTRIBUTE_NAMES = frozenset(
    {
        "difficulty_description",
        "few_shot_answer_intro",
        "few_shot_intro",
        "few_shot_query_intro",
        "prompt_description",
        "verified_description",
    }
)
"""Prompt attributes that do not affect zero-shot execution."""


@dataclass(frozen=True, slots=True)
class Prompt:
    """Immutable text and field configuration for LLM correspondence."""

    language: Language
    """Language in which the prompt corresponds with the LLM."""
    attributes: tuple[tuple[str, str], ...]
    """Ordered effective string attributes."""

    _attribute_defaults: ClassVar[Mapping[str, str]] = {
        "answer_invalid_post": "",
        "answer_invalid_pre": "",
        "base_system_prompt": "",
        "difficulty_description": (
            "Difficulty level of the test case, used for filtering."
        ),
        "few_shot_answer_intro": "",
        "few_shot_intro": "",
        "few_shot_query_intro": "",
        "prompt_description": "Whether to include test case in prompt examples.",
        "schema_intro": "",
        "test_case_invalid_post": "",
        "test_case_invalid_pre": "",
        "verified_description": (
            "Whether to include test case in the verified answers cache."
        ),
    }
    """Default effective string attributes."""

    # Prompt
    base_system_prompt: ClassVar[str]
    """Base system prompt."""
    schema_intro: ClassVar[str]
    """Text preceding schema description."""
    few_shot_intro: ClassVar[str]
    """Text preceding few-shot examples."""
    few_shot_query_intro: ClassVar[str]
    """Text preceding each few-shot example query."""
    few_shot_answer_intro: ClassVar[str]
    """Text preceding each few-shot expected answer."""

    # Answer validation errors
    answer_invalid_pre: ClassVar[str]
    """Text preceding answer validation errors."""
    answer_invalid_post: ClassVar[str]
    """Text following answer validation errors."""

    # Test case field descriptions
    difficulty_description: ClassVar[str]
    """Description of 'difficulty' field."""
    prompt_description: ClassVar[str]
    """Description of 'prompt' field."""
    verified_description: ClassVar[str]
    """Description of 'verified' field."""

    # Test case validation errors
    test_case_invalid_pre: ClassVar[str]
    """Text preceding test case validation errors."""
    test_case_invalid_post: ClassVar[str]
    """Text following test case validation errors."""

    def __getattribute__(self, name: str) -> object:
        """Get effective string attributes before prompt-type defaults."""
        if name not in {"attributes", "language"}:
            attributes = object.__getattribute__(self, "attributes")
            for attribute_name, value in attributes:
                if attribute_name == name:
                    return value
        return object.__getattribute__(self, name)

    def __getattr__(self, name: str) -> str:
        """Get an effective prompt attribute by name.

        Arguments:
            name: attribute name
        Returns:
            effective string attribute
        Raises:
            AttributeError: if the prompt does not define the attribute
        """
        try:
            return dict(self.attributes)[name]
        except KeyError as exc:
            raise AttributeError(
                f"{type(self).__name__} has no attribute {name!r}"
            ) from exc

    @property
    def name(self) -> str:
        """Stable content-addressed name used for generated model classes."""
        payload_json = json.dumps(
            {
                "attributes": dict(self.attributes),
                "language": self.language.tag,
                "type": type(self).__name__,
            },
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        digest = hashlib.sha256(payload_json.encode()).hexdigest()[:12]
        language_name = self.language.tag.replace("-", "_")
        return f"{type(self).__name__}_{language_name}_{digest}"

    @property
    def zero_shot_attributes(self) -> tuple[tuple[str, str], ...]:
        """Ordered attributes affecting zero-shot execution."""
        return tuple(
            (name, value)
            for name, value in self.attributes
            if name not in _EXCLUDED_ZERO_SHOT_ATTRIBUTE_NAMES
        )

    @classmethod
    def from_attributes(
        cls,
        language: Language = Language.eng,
        attributes: Mapping[str, str] | None = None,
    ) -> Self:
        """Build a prompt from effective string attributes.

        Arguments:
            language: language in which the prompt corresponds with the LLM
            attributes: effective string attributes overriding defaults
        Returns:
            immutable prompt
        Raises:
            ValueError: if an attribute name is empty or a value is not a string
        """
        merged_attributes = cls.get_attribute_defaults()
        if attributes is not None:
            merged_attributes.update(attributes)
        invalid_names = sorted(
            name
            for name, value in merged_attributes.items()
            if not name or not isinstance(value, str)
        )
        if invalid_names:
            raise ValueError(
                "Prompt attributes must have nonempty names and string values: "
                f"{', '.join(invalid_names)}."
            )
        return cls(
            language=language,
            attributes=tuple(sorted(merged_attributes.items())),
        )

    @classmethod
    def get_attribute_defaults(cls) -> dict[str, str]:
        """Get effective attribute defaults across the prompt type hierarchy."""
        defaults: dict[str, str] = {}
        for prompt_type in reversed(cls.__mro__):
            prompt_defaults = vars(prompt_type).get("_attribute_defaults")
            if isinstance(prompt_defaults, Mapping):
                defaults.update(prompt_defaults)
            annotations = vars(prompt_type).get("__annotations__", {})
            for name in annotations:
                value = vars(prompt_type).get(name)
                if isinstance(value, str):
                    defaults[name] = value
        return defaults

    def transformed(
        self,
        language: Language,
        transform: Callable[[str], str],
    ) -> Self:
        """Build a prompt by transforming every effective string attribute.

        Arguments:
            language: language of the transformed prompt
            transform: string transformation to apply
        Returns:
            transformed prompt
        """
        return type(self).from_attributes(
            language,
            {name: transform(value) for name, value in self.attributes},
        )

    def with_attributes(self, attributes: Mapping[str, str]) -> Self:
        """Build a prompt with additional or overridden attributes.

        Arguments:
            attributes: attributes to merge into this prompt
        Returns:
            merged prompt
        """
        merged_attributes = dict(self.attributes)
        merged_attributes.update(attributes)
        return type(self).from_attributes(self.language, merged_attributes)
