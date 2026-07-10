#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Declarative zero-shot prompt definitions and runtime materialization."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from functools import cache
from typing import ClassVar, cast

from scinoephile.core import Language
from scinoephile.core.llms import Prompt

__all__ = [
    "PromptDefinition",
    "define_prompt",
    "get_prompt_attribute_names",
]

_EXCLUDED_ATTRIBUTE_NAMES = frozenset(
    {
        "difficulty_description",
        "few_shot_answer_intro",
        "few_shot_intro",
        "few_shot_query_intro",
        "language",
        "prompt_description",
        "verified_description",
    }
)
"""Prompt attributes that do not affect zero-shot execution."""


@dataclass(frozen=True, slots=True)
class PromptDefinition:
    """A declarative, hashable zero-shot prompt definition."""

    language: Language
    """Language in which the prompt corresponds with the LLM."""
    attributes: tuple[tuple[str, str], ...]
    """Ordered effective string attributes affecting zero-shot execution."""

    @classmethod
    def from_attributes(
        cls,
        language: Language,
        attributes: Mapping[str, str],
    ) -> PromptDefinition:
        """Build a definition from zero-shot prompt attributes.

        Arguments:
            language: language in which the prompt corresponds with the LLM
            attributes: effective zero-shot prompt attributes
        Returns:
            declarative prompt definition
        Raises:
            ValueError: if an attribute name is empty
        """
        if invalid_names := sorted(name for name in attributes if not name):
            raise ValueError(
                f"Prompt attribute names may not be empty: {', '.join(invalid_names)}"
            )
        return cls(
            language=language,
            attributes=tuple(sorted(attributes.items())),
        )

    @classmethod
    def from_prompt_cls(cls, prompt_cls: type[Prompt]) -> PromptDefinition:
        """Build a definition from an existing runtime prompt class.

        Arguments:
            prompt_cls: runtime prompt class
        Returns:
            declarative prompt definition
        Raises:
            ValueError: if the prompt does not declare a supported language
        """
        language = getattr(prompt_cls, "language", None)
        if not isinstance(language, Language):
            raise ValueError(
                f"Prompt class {prompt_cls.__name__} does not declare a language."
            )
        attributes: dict[str, str] = {}
        for name in sorted(get_prompt_attribute_names(prompt_cls)):
            value = getattr(prompt_cls, name, None)
            if isinstance(value, str):
                attributes[name] = value
        return cls.from_attributes(language, attributes)

    def get_prompt_cls[TPrompt: Prompt](
        self,
        base_prompt_cls: type[TPrompt],
    ) -> type[TPrompt]:
        """Materialize a cached runtime class from this definition.

        Arguments:
            base_prompt_cls: operation-specific base prompt class
        Returns:
            cached runtime prompt class
        """
        return _get_prompt_cls(base_prompt_cls, self, ())

    def transformed(
        self,
        language: Language,
        transform: Callable[[str], str],
    ) -> PromptDefinition:
        """Build a definition by transforming every string attribute.

        Arguments:
            language: language of the transformed prompt
            transform: string transformation to apply
        Returns:
            transformed prompt definition
        """
        return PromptDefinition(
            language=language,
            attributes=tuple(
                (name, transform(value)) for name, value in self.attributes
            ),
        )

    def with_attributes(self, attributes: Mapping[str, str]) -> PromptDefinition:
        """Build a definition with additional or overridden attributes.

        Arguments:
            attributes: attributes to merge into this definition
        Returns:
            merged prompt definition
        """
        merged_attributes = dict(self.attributes)
        merged_attributes.update(attributes)
        return self.from_attributes(self.language, merged_attributes)


def define_prompt[TPrompt: Prompt](
    base_prompt_cls: type[TPrompt],
    language: Language,
    *,
    parent: type[Prompt] | None = None,
    transform: Callable[[str], str] | None = None,
) -> Callable[[type[object]], type[TPrompt]]:
    """Define a prompt as declarative class text and materialize its runtime class.

    Arguments:
        base_prompt_cls: operation-specific base prompt class
        language: language in which the prompt corresponds with the LLM
        parent: optional prompt whose effective attributes should be inherited
        transform: optional transformation applied to all effective attributes
    Returns:
        declarative class decorator
    """

    def decorator(definition_cls: type[object]) -> type[TPrompt]:
        """Materialize one declarative prompt class."""
        attributes: dict[str, str] = {}
        if parent is not None:
            attributes.update(_get_prompt_string_attributes(parent))
        annotations = vars(definition_cls).get("__annotations__", {})
        for name in annotations:
            if name.startswith("_"):
                continue
            value = getattr(definition_cls, name, None)
            if isinstance(value, str):
                attributes[name] = value
        if transform is not None:
            attributes = {name: transform(value) for name, value in attributes.items()}
        definition = PromptDefinition.from_attributes(
            language,
            {
                name: value
                for name, value in attributes.items()
                if name not in _EXCLUDED_ATTRIBUTE_NAMES
            },
        )
        supplemental_attributes = tuple(
            sorted(
                (name, value)
                for name, value in attributes.items()
                if name in _EXCLUDED_ATTRIBUTE_NAMES
            )
        )
        return _get_prompt_cls(base_prompt_cls, definition, supplemental_attributes)

    return decorator


def get_prompt_attribute_names(prompt_cls: type[Prompt]) -> set[str]:
    """Get declared public zero-shot attributes across a prompt hierarchy.

    Arguments:
        prompt_cls: prompt class to inspect
    Returns:
        public zero-shot prompt attribute names
    """
    names: set[str] = set()
    for base_cls in prompt_cls.__mro__:
        annotations = vars(base_cls).get("__annotations__", {})
        for name in annotations:
            if name.startswith("_") or name in _EXCLUDED_ATTRIBUTE_NAMES:
                continue
            names.add(name)
    return names


def _get_prompt_string_attributes(prompt_cls: type[Prompt]) -> dict[str, str]:
    """Get effective public string attributes across a prompt hierarchy.

    Arguments:
        prompt_cls: prompt class to inspect
    Returns:
        effective public string attributes
    """
    names: set[str] = set()
    for base_cls in prompt_cls.__mro__:
        annotations = vars(base_cls).get("__annotations__", {})
        names.update(name for name in annotations if not name.startswith("_"))
    return {
        name: value
        for name in names
        if isinstance(value := getattr(prompt_cls, name, None), str)
    }


@cache
def _get_prompt_cls[TPrompt: Prompt](
    base_prompt_cls: type[TPrompt],
    definition: PromptDefinition,
    supplemental_attributes: tuple[tuple[str, str], ...],
) -> type[TPrompt]:
    """Materialize and cache a runtime prompt class.

    Arguments:
        base_prompt_cls: operation-specific base prompt class
        definition: declarative prompt definition
        supplemental_attributes: runtime attributes excluded from persistence
    Returns:
        cached runtime prompt class
    """
    payload_json = json.dumps(
        {
            "attributes": dict(definition.attributes),
            "language": definition.language.tag,
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    digest = hashlib.sha256(payload_json.encode()).hexdigest()[:12]
    language_name = definition.language.tag.replace("-", "_")
    runtime_attributes = {
        **dict(definition.attributes),
        **dict(supplemental_attributes),
    }
    class_attributes: dict[str, object] = {
        "__annotations__": {
            "language": ClassVar[Language],
            **{name: ClassVar[str] for name in runtime_attributes},
        },
        "__module__": base_prompt_cls.__module__,
        "language": definition.language,
        **runtime_attributes,
    }
    prompt_cls = type(
        f"{base_prompt_cls.__name__}_{language_name}_{digest}",
        (base_prompt_cls,),
        class_attributes,
    )
    return cast("type[TPrompt]", prompt_cls)
