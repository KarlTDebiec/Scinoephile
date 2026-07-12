#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for LLM managers."""

from __future__ import annotations

from abc import ABC
from collections.abc import Mapping
from copy import copy
from dataclasses import dataclass
from functools import cache
from typing import Any, ClassVar

from pydantic import create_model

from .answer import Answer
from .models import LLMModel, get_model_name
from .prompt import Prompt
from .query import Query
from .test_case import TestCase

__all__ = [
    "Manager",
    "PromptModelField",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class PromptModelField:
    """Prompt-specific changes to one semantic model field."""

    alias: str | None = None
    """Serialized field name, or None to retain the semantic name."""
    annotation: Any = None
    """Replacement field annotation, or None to retain the semantic annotation."""
    description: str | None = None
    """JSON schema description, or None to retain the semantic description."""


class Manager(ABC):
    """ABC for LLM managers."""

    operation: ClassVar[str]
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[Prompt]
    """Base prompt defining persisted test-case field names."""
    test_case_base_cls: ClassVar[type[TestCase]]
    """Static test-case model defining the operation's semantic shape."""

    @classmethod
    def create_prompt_model[TModel: LLMModel](
        cls,
        base_cls: type[TModel],
        prompt: Prompt,
        field_configs: Mapping[str, PromptModelField],
        *,
        module: str | None = None,
        name: str | None = None,
    ) -> type[TModel]:
        """Create a prompt-specific model from a semantic base model.

        Arguments:
            base_cls: semantic model class whose shape and constraints are retained
            prompt: text and field aliases for LLM correspondence
            field_configs: prompt-specific field changes keyed by semantic field name
            module: generated model module, or None to use the base model module
            name: generated model base name, or None to use the base model name
        Returns:
            prompt-specific model class
        """
        fields: dict[str, Any] = {}
        for field_name, field_config in field_configs.items():
            field_info = copy(base_cls.model_fields[field_name])
            if field_config.alias is not None:
                field_info.alias = field_config.alias
                field_info.validation_alias = field_config.alias
                field_info.serialization_alias = field_config.alias
            if field_config.description is not None:
                field_info.description = field_config.description

            annotation = field_config.annotation
            if annotation is None:
                annotation = field_info.annotation
            fields[field_name] = (annotation, field_info)

        if module is None:
            module = base_cls.__module__
        if name is None:
            name = base_cls.__name__
        model = create_model(
            get_model_name(name, prompt.name),
            __base__=base_cls,
            __module__=module,
            **fields,
        )
        if issubclass(model, (Answer, Query, TestCase)):
            model.prompt = prompt
        return model

    @classmethod
    def get_answer_cls(cls, prompt: Prompt) -> type[Answer]:
        """Get concrete answer class with provided configuration.

        Arguments:
            prompt: text for LLM correspondence
        Returns:
            answer model class
        """
        raise NotImplementedError

    @classmethod
    def get_query_cls(cls, prompt: Prompt) -> type[Query]:
        """Get concrete query class with provided configuration.

        Arguments:
            prompt: text for LLM correspondence
        Returns:
            query model class
        """
        raise NotImplementedError

    @classmethod
    @cache
    def get_test_case_cls(cls, prompt: Prompt) -> type[TestCase]:
        """Get concrete test case class with provided configuration.

        Arguments:
            prompt: text for LLM correspondence
        Returns:
            test case model class
        """
        query_cls = cls.get_query_cls(prompt)
        answer_cls = cls.get_answer_cls(prompt)
        model = cls.create_prompt_model(
            cls.test_case_base_cls,
            prompt,
            {
                "query": PromptModelField(annotation=query_cls),
                "answer": PromptModelField(annotation=answer_cls | None),
            },
        )
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        return model
