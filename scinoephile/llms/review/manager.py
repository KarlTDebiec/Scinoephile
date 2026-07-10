#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for review LLM classes."""

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

from .prompt import ReviewPrompt

__all__ = ["ReviewManager"]


class ReviewManager(Manager):
    """Factories for review LLM classes."""

    operation: ClassVar[str] = "review"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[ReviewPrompt] = ReviewPrompt()
    """Base prompt defining persisted test-case field names."""

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        size: int,
        prompt: ReviewPrompt = ReviewPrompt(),
    ) -> type[Answer]:
        """Get concrete answer class with provided configuration.

        Arguments:
            size: number of subtitles in the block
            prompt: text for LLM correspondence
        Returns:
            answer model class
        """
        name = get_model_name("ReviewAnswer", f"{size}_{prompt.name}")
        fields: dict[str, Any] = {}
        for idx in range(size):
            key = prompt.output(idx + 1)
            desc = prompt.output_desc(idx + 1)
            fields[key] = (str, Field("", description=desc))
            key = prompt.note(idx + 1)
            desc = prompt.note_desc(idx + 1)
            fields[key] = (str, Field("", description=desc, max_length=1000))

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
    def get_query_cls(
        cls,
        size: int,
        prompt: ReviewPrompt = ReviewPrompt(),
    ) -> type[Query]:
        """Get concrete query class with provided configuration.

        Arguments:
            size: number of subtitles in the block
            prompt: text for LLM correspondence
        Returns:
            query model class
        """
        name = get_model_name("ReviewQuery", f"{size}_{prompt.name}")
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
    def get_test_case_cls(
        cls,
        size: int,
        prompt: ReviewPrompt = ReviewPrompt(),
    ) -> type[TestCase]:
        """Get concrete test case class with provided configuration.

        Arguments:
            size: number of subtitles in the block
            prompt: text for LLM correspondence
        Returns:
            test case model class
        """
        name = get_model_name("ReviewTestCase", f"{size}_{prompt.name}")
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
            prompt=cast(ReviewPrompt, prompt),
        )

    @staticmethod
    def get_min_difficulty(model: TestCase) -> int:
        """Get minimum difficulty based on the test case properties.

        Arguments:
            model: test case to inspect
        Returns:
            minimum difficulty
        """
        prompt: ReviewPrompt = getattr(model, "prompt")
        size: int = getattr(model, "size")
        min_difficulty = 0
        if model.answer is None:
            return min_difficulty

        if any(
            getattr(model.answer, prompt.output(idx)) != ""
            for idx in range(1, size + 1)
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
        prompt: ReviewPrompt = getattr(model, "prompt")
        size: int = getattr(model, "size")
        if model.answer is None:
            return model

        for idx in range(size):
            input_text = getattr(model.query, prompt.input(idx + 1))
            output_text = getattr(model.answer, prompt.output(idx + 1))
            note = getattr(model.answer, prompt.note(idx + 1))
            if output_text != "":
                if input_text == output_text:
                    setattr(model.answer, prompt.output(idx + 1), "")
                    setattr(model.answer, prompt.note(idx + 1), "")
                    continue
                if note == "":
                    raise ValueError(prompt.note_missing_err(idx + 1))
            elif note != "":
                raise ValueError(prompt.output_missing_err(idx + 1))
        return model
