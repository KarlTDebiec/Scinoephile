#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for translation LLM classes."""

from __future__ import annotations

import re
from functools import cache
from typing import Any, ClassVar, Unpack, cast

from pydantic import Field, create_model

from scinoephile.core import ScinoephileError
from scinoephile.core.llms import (
    Answer,
    Manager,
    Prompt,
    Query,
    TestCase,
    TestCaseClsKwargs,
)
from scinoephile.core.llms.models import get_model_name

from .prompt import TranslationPrompt

__all__ = ["TranslationManager"]


class TranslationManager(Manager):
    """Factories for translation LLM classes."""

    prompt_cls: ClassVar[type[TranslationPrompt]] = TranslationPrompt
    """Default prompt class."""

    @classmethod
    @cache
    def get_query_cls(
        cls,
        size: int,
        prompt_cls: type[TranslationPrompt] = TranslationPrompt,
    ) -> type[Query]:
        """Get concrete query class with provided configuration.

        Arguments:
            size: number of subtitles in the block
            prompt_cls: text for LLM correspondence
        Returns:
            query model class
        """
        name = get_model_name("TranslationQuery", f"{size}_{prompt_cls.__name__}")
        fields: dict[str, Any] = {}
        for idx in range(size):
            key = prompt_cls.input(idx + 1)
            desc = prompt_cls.input_desc(idx + 1)
            fields[key] = (str, Field(..., description=desc, max_length=1000))

        model = create_model(
            name,
            __base__=Query,
            __module__=Query.__module__,
            **fields,
        )
        model.prompt_cls = prompt_cls
        setattr(model, "size", size)
        return model

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        size: int,
        prompt_cls: type[TranslationPrompt] = TranslationPrompt,
    ) -> type[Answer]:
        """Get concrete answer class with provided configuration.

        Arguments:
            size: number of subtitles in the block
            prompt_cls: text for LLM correspondence
        Returns:
            answer model class
        """
        name = get_model_name("TranslationAnswer", f"{size}_{prompt_cls.__name__}")
        fields: dict[str, Any] = {}
        for idx in range(size):
            key = prompt_cls.output(idx + 1)
            desc = prompt_cls.output_desc(idx + 1)
            fields[key] = (str, Field(..., description=desc))

        model = create_model(
            name,
            __base__=Answer,
            __module__=Answer.__module__,
            **fields,
        )
        model.prompt_cls = prompt_cls
        setattr(model, "size", size)
        return model

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        size: int,
        prompt_cls: type[TranslationPrompt] = TranslationPrompt,
    ) -> type[TestCase]:
        """Get concrete test case class with provided configuration.

        Arguments:
            size: number of subtitles in the block
            prompt_cls: text for LLM correspondence
        Returns:
            test case model class
        """
        name = get_model_name("TranslationTestCase", f"{size}_{prompt_cls.__name__}")
        query_cls = cls.get_query_cls(size, prompt_cls)
        answer_cls = cls.get_answer_cls(size, prompt_cls)
        fields = cls.get_test_case_fields(query_cls, answer_cls, prompt_cls)
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
        model.prompt_cls = prompt_cls
        setattr(model, "size", size)
        setattr(model, "get_auto_verified", cls.get_auto_verified)
        setattr(model, "get_min_difficulty", cls.get_min_difficulty)
        return model

    @classmethod
    def get_test_case_cls_from_data(
        cls,
        data: dict,
        **kwargs: Unpack[TestCaseClsKwargs],
    ) -> type[TestCase]:
        """Get concrete test case class for provided data.

        Arguments:
            data: data from JSON
            **kwargs: additional keyword arguments passed to get_test_case_cls
        Returns:
            test case model class
        """
        if (prompt_cls := kwargs.get("prompt_cls")) is None:
            raise ScinoephileError("prompt_cls must be provided as a keyword argument")
        prompt_cls = cast(type[TranslationPrompt], prompt_cls)
        pattern = re.compile(rf"^{re.escape(prompt_cls.input_pfx)}\d+$")
        size = sum(1 for field in data["query"] if pattern.match(field))
        return cls.get_test_case_cls(size=size, prompt_cls=prompt_cls)

    @classmethod
    def get_test_case_cls_with_prompt(
        cls,
        test_case_cls: type[TestCase],
        prompt_cls: type[Prompt],
    ) -> type[TestCase]:
        """Get an equivalently sized test-case class for another prompt.

        Arguments:
            test_case_cls: test-case class whose size should be preserved
            prompt_cls: prompt class whose correspondence fields should be used
        Returns:
            equivalently sized test-case class
        """
        size: int = getattr(test_case_cls, "size")
        return cls.get_test_case_cls(
            size=size,
            prompt_cls=cast(type[TranslationPrompt], prompt_cls),
        )
