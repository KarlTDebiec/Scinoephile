#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Declarative construction of immutable prompt values."""

from __future__ import annotations

from collections.abc import Callable

from scinoephile.core import Language
from scinoephile.core.llms import Prompt

__all__ = [
    "define_prompt",
    "get_prompt_attribute_names",
]

_EXCLUDED_ZERO_SHOT_ATTRIBUTE_NAMES = frozenset(
    {
        "difficulty_description",
        "few_shot_answer_intro",
        "few_shot_intro",
        "few_shot_query_intro",
        "few_shot_description",
        "verified_description",
    }
)
"""Prompt attributes that do not affect zero-shot execution."""


def define_prompt[TPrompt: Prompt](
    prompt_type: type[TPrompt],
    language: Language,
    *,
    parent: Prompt | None = None,
    transform: Callable[[str], str] | None = None,
) -> Callable[[type[object]], TPrompt]:
    """Define an immutable prompt using a declarative class body.

    Arguments:
        prompt_type: operation-specific prompt value type
        language: language in which the prompt corresponds with the LLM
        parent: optional prompt whose effective attributes should be inherited
        transform: optional transformation applied to all effective attributes
    Returns:
        declarative prompt decorator
    """

    def decorator(definition_type: type[object]) -> TPrompt:
        """Build one immutable prompt value."""
        attributes = prompt_type.get_attribute_defaults()
        if parent is not None:
            attributes.update(parent.attributes)
        annotations = vars(definition_type).get("__annotations__", {})
        for name in annotations:
            if name.startswith("_"):
                continue
            value = getattr(definition_type, name, None)
            if isinstance(value, str):
                attributes[name] = value
        if transform is not None:
            attributes = {name: transform(value) for name, value in attributes.items()}
        return prompt_type.from_attributes(language, attributes)

    return decorator


def get_prompt_attribute_names(prompt_type: type[Prompt]) -> set[str]:
    """Get required public attributes across a prompt type hierarchy.

    Arguments:
        prompt_type: prompt value type to inspect
    Returns:
        required public prompt attribute names
    """
    names: set[str] = set()
    for base_type in prompt_type.__mro__:
        annotations = vars(base_type).get("__annotations__", {})
        names.update(
            name
            for name in annotations
            if not name.startswith("_")
            and name not in {"attributes", "language"}
            and name not in _EXCLUDED_ZERO_SHOT_ATTRIBUTE_NAMES
        )
    return names
