#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for translation LLM classes."""

from __future__ import annotations

import re
from functools import cache
from typing import Any, ClassVar, cast

from pydantic import Field, create_model

from scinoephile.core.llms import (
    Answer,
    Manager,
    Prompt,
    Query,
    TestCase,
)
from scinoephile.core.llms.models import get_model_name

from .prompt import TranslationPrompt

__all__ = ["TranslationManager"]


class TranslationManager(Manager):
    """Factories for translation LLM classes."""

    operation: ClassVar[str] = "translation"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[TranslationPrompt] = TranslationPrompt()
    """Base prompt defining persisted test-case field names."""

    @classmethod
    @cache
    def get_query_cls(
        cls,
        size: int,
        prompt: TranslationPrompt = TranslationPrompt(),
    ) -> type[Query]:
        """Get concrete query class with provided configuration.

        Arguments:
            size: number of subtitles in the block
            prompt: text for LLM correspondence
        Returns:
            query model class
        """
        name = get_model_name("TranslationQuery", f"{size}_{prompt.name}")
        fields: dict[str, Any] = {}
        for idx in range(size):
            key = prompt.input(idx + 1)
            desc = prompt.input_desc(idx + 1)
            fields[key] = (str, Field(..., description=desc, max_length=1000))

        model = create_model(
            name,
            __base__=Query,
            __module__=Query.__module__,
            **fields,
        )
        model.prompt = prompt
        setattr(model, "size", size)
        return model

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        size: int,
        prompt: TranslationPrompt = TranslationPrompt(),
    ) -> type[Answer]:
        """Get concrete answer class with provided configuration.

        Arguments:
            size: number of subtitles in the block
            prompt: text for LLM correspondence
        Returns:
            answer model class
        """
        name = get_model_name("TranslationAnswer", f"{size}_{prompt.name}")
        fields: dict[str, Any] = {}
        for idx in range(size):
            key = prompt.output(idx + 1)
            desc = prompt.output_desc(idx + 1)
            fields[key] = (str, Field(..., description=desc))

        model = create_model(
            name,
            __base__=Answer,
            __module__=Answer.__module__,
            **fields,
        )
        model.prompt = prompt
        setattr(model, "size", size)
        return model

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        size: int,
        prompt: TranslationPrompt = TranslationPrompt(),
    ) -> type[TestCase]:
        """Get concrete test case class with provided configuration.

        Arguments:
            size: number of subtitles in the block
            prompt: text for LLM correspondence
        Returns:
            test case model class
        """
        name = get_model_name("TranslationTestCase", f"{size}_{prompt.name}")
        query_cls = cls.get_query_cls(size, prompt)
        answer_cls = cls.get_answer_cls(size, prompt)
        fields = cls.get_test_case_fields(query_cls, answer_cls, prompt)
        validators = cls.get_test_case_validators()

        model = create_model(
            name,
            __base__=TestCase,
            __module__=TestCase.__module__,
            __validators__=validators,
            **fields,
        )
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        model.prompt = prompt
        setattr(model, "size", size)
        setattr(model, "get_auto_verified", cls.get_auto_verified)
        setattr(model, "get_min_difficulty", cls.get_min_difficulty)
        return model

    @classmethod
    def get_test_case_cls_from_data(cls, data: dict) -> type[TestCase]:
        """Get concrete test case class for canonical serialized data.

        Arguments:
            data: data from JSON
        Returns:
            test case model class
        """
        prompt = cls.base_prompt
        pattern = re.compile(rf"^{re.escape(prompt.input_pfx)}\d+$")
        size = sum(1 for field in data["query"] if pattern.match(field))
        return cls.get_test_case_cls(size=size, prompt=prompt)

    @classmethod
    def get_test_case_cls_with_prompt(
        cls,
        test_case_cls: type[TestCase],
        prompt: Prompt,
    ) -> type[TestCase]:
        """Get an equivalently sized test-case class for another prompt.

        Arguments:
            test_case_cls: test-case class whose size should be preserved
            prompt: prompt whose correspondence fields should be used
        Returns:
            equivalently sized test-case class
        """
        size: int = getattr(test_case_cls, "size")
        return cls.get_test_case_cls(
            size=size,
            prompt=cast(TranslationPrompt, prompt),
        )
