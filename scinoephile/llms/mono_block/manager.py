#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for mono track / subtitle block LLM classes."""

from __future__ import annotations

import re
from functools import cache
from typing import Any, ClassVar, Unpack

from pydantic import Field, create_model

from scinoephile.core import ScinoephileError
from scinoephile.llms.base import Answer, Manager, Query, TestCase, TestCaseClsKwargs
from scinoephile.llms.base.models import get_model_name

from .prompt import MonoBlockPrompt

__all__ = ["MonoBlockManager"]


class MonoBlockManager(Manager):
    """Factories for mono track / subtitle block LLM classes."""

    prompt_cls: ClassVar[type[MonoBlockPrompt]] = MonoBlockPrompt
    """Default prompt class."""

    @classmethod
    @cache
    def get_query_cls(
        cls,
        size: int,
        prompt_cls: type[MonoBlockPrompt] = MonoBlockPrompt,
    ) -> type[Query]:
        """Get concrete query class with provided configuration.

        Arguments:
            size: number of subtitles in the block
            prompt_cls: text for LLM correspondence
        Returns:
            query model class
        """
        name = get_model_name("MonoBlockQuery", f"{size}_{prompt_cls.__name__}")
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
        model.size = size
        return model

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        size: int,
        prompt_cls: type[MonoBlockPrompt] = MonoBlockPrompt,
    ) -> type[Answer]:
        """Get concrete answer class with provided configuration.

        Arguments:
            size: number of subtitles in the block
            prompt_cls: text for LLM correspondence
        Returns:
            answer model class
        """
        name = get_model_name("MonoBlockAnswer", f"{size}_{prompt_cls.__name__}")
        fields: dict[str, Any] = {}
        for idx in range(size):
            key = prompt_cls.output(idx + 1)
            desc = prompt_cls.output_desc(idx + 1)
            fields[key] = (str, Field("", description=desc))
            key = prompt_cls.note(idx + 1)
            desc = prompt_cls.note_desc(idx + 1)
            fields[key] = (str, Field("", description=desc, max_length=1000))

        model = create_model(
            name,
            __base__=Answer,
            __module__=Answer.__module__,
            **fields,
        )
        model.prompt_cls = prompt_cls
        model.size = size
        return model

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        size: int,
        prompt_cls: type[MonoBlockPrompt] = MonoBlockPrompt,
    ) -> type[TestCase]:
        """Get concrete test case class with provided configuration.

        Arguments:
            size: number of subtitles in the block
            prompt_cls: text for LLM correspondence
        Returns:
            test case model class
        """
        name = get_model_name("MonoBlockTestCase", f"{size}_{prompt_cls.__name__}")
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
        model.size = size
        model.get_auto_verified = cls.get_auto_verified
        model.get_min_difficulty = cls.get_min_difficulty
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
        pattern = re.compile(rf"^{re.escape(prompt_cls.input_pfx)}\d+$")
        size = sum(1 for field in data["query"] if pattern.match(field))
        return cls.get_test_case_cls(size=size, prompt_cls=prompt_cls)

    @staticmethod
    def get_min_difficulty(model: TestCase) -> int:
        """Get minimum difficulty based on the test case properties.

        Arguments:
            model: test case to inspect
        Returns:
            minimum difficulty
        """
        min_difficulty = 0
        if model.answer is None:
            return min_difficulty

        if any(
            getattr(model.answer, model.prompt_cls.output(idx)) != ""
            for idx in range(1, model.size + 1)
        ):
            min_difficulty = max(min_difficulty, 1)
        return min_difficulty

    @staticmethod
    def validate_test_case(model: TestCase) -> TestCase:
        """Ensure query and answer together are valid.

        Arguments:
            model: test case to validate
        Returns:
            validated test case
        """
        if model.answer is None:
            return model

        for idx in range(model.size):
            input_text = getattr(model.query, model.prompt_cls.input(idx + 1))
            output_text = getattr(model.answer, model.prompt_cls.output(idx + 1))
            note = getattr(model.answer, model.prompt_cls.note(idx + 1))
            if output_text != "":
                if input_text == output_text:
                    raise ValueError(model.prompt_cls.output_unmodified_err(idx + 1))
                if note == "":
                    raise ValueError(model.prompt_cls.note_missing_err(idx + 1))
            elif note != "":
                raise ValueError(model.prompt_cls.output_missing_err(idx + 1))
        return model
