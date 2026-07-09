#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for OCR fusion LLM classes."""

from __future__ import annotations

from functools import cache
from typing import Any, ClassVar, cast

from pydantic import Field, create_model, model_validator

from scinoephile.core.llms import Answer, Manager, Query, TestCase
from scinoephile.core.llms.models import get_model_name

from .prompt import OcrFusionPrompt

__all__ = ["OcrFusionManager"]


class OcrFusionManager(Manager):
    """Factories for OCR fusion LLM classes."""

    prompt_cls: ClassVar[type[OcrFusionPrompt]] = OcrFusionPrompt
    """Default prompt class."""

    @classmethod
    @cache
    def get_answer_cls[TAnswer: Answer](
        cls,
        prompt_cls: type[OcrFusionPrompt],
    ) -> type[TAnswer]:
        """Get concrete answer class with provided configuration.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            answer model class
        """
        name = get_model_name(Answer.__name__, prompt_cls.__name__)
        fields: dict[str, Any] = {
            prompt_cls.output: (str, Field(..., description=prompt_cls.output_desc)),
            prompt_cls.note: (str, Field(..., description=prompt_cls.note_desc)),
        }
        validators: dict[str, Any] = {
            "validate_answer": model_validator(mode="after")(cls.validate_answer),
        }

        model = cast(
            "type[TAnswer]",
            create_model(
                name,
                __base__=Answer,
                __module__=Answer.__module__,
                __validators__=validators,
                **fields,
            ),
        )
        model.prompt_cls = prompt_cls
        return model

    @classmethod
    @cache
    def get_query_cls[TQuery: Query](
        cls,
        prompt_cls: type[OcrFusionPrompt],
    ) -> type[TQuery]:
        """Get concrete query class with provided configuration.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            query model class
        """
        name = get_model_name(Query.__name__, prompt_cls.__name__)
        fields: dict[str, Any] = {
            prompt_cls.src_1: (str, Field(..., description=prompt_cls.src_1_desc)),
            prompt_cls.src_2: (str, Field(..., description=prompt_cls.src_2_desc)),
        }
        validators: dict[str, Any] = {
            "validate_query": model_validator(mode="after")(cls.validate_query),
        }

        model = cast(
            "type[TQuery]",
            create_model(
                name,
                __base__=Query,
                __module__=Query.__module__,
                __validators__=validators,
                **fields,
            ),
        )
        model.prompt_cls = prompt_cls
        return model

    @staticmethod
    def get_auto_verified(model: TestCase) -> bool:
        """Whether this test case should automatically be verified.

        Arguments:
            model: test case to inspect
        Returns:
            whether the test case should be auto-verified
        """
        if model.answer is None:
            return False

        if model.get_min_difficulty() > 1:
            return False

        prompt_cls: type[OcrFusionPrompt] = getattr(model, "prompt_cls")
        source_one = getattr(model.query, prompt_cls.src_1, None)
        source_two = getattr(model.query, prompt_cls.src_2, None)
        output_text = getattr(model.answer, prompt_cls.output, None)
        if (
            source_one is not None
            and source_two is not None
            and output_text is not None
        ):
            if source_one == output_text and "\n" not in source_one:
                return True
            if source_two == output_text and "\n" not in source_two:
                return True
        return Manager.get_auto_verified(model)

    @staticmethod
    def get_min_difficulty(model: TestCase) -> int:
        """Get minimum difficulty based on the test case properties.

        Arguments:
            model: test case to inspect
        Returns:
            minimum difficulty
        """
        prompt_cls: type[OcrFusionPrompt] = getattr(model, "prompt_cls")
        min_difficulty = max(Manager.get_min_difficulty(model), 1)
        if model.answer is None:
            return min_difficulty

        if output_text := getattr(model.answer, prompt_cls.output):
            if any(char in output_text for char in ("-", '"', "“", "”")):
                min_difficulty = max(min_difficulty, 2)
        return min_difficulty

    @staticmethod
    def validate_answer(model: Answer) -> Answer:
        """Ensure answer is internally valid.

        Arguments:
            model: answer to validate
        Returns:
            validated answer
        """
        prompt_cls: type[OcrFusionPrompt] = getattr(model, "prompt_cls")
        output = getattr(model, prompt_cls.output, None)
        note = getattr(model, prompt_cls.note, None)
        if not output:
            raise ValueError(prompt_cls.output_missing_err)
        if not note:
            raise ValueError(prompt_cls.note_missing_err)
        return model

    @staticmethod
    def validate_query(model: Query) -> Query:
        """Ensure query is internally valid.

        Arguments:
            model: query to validate
        Returns:
            validated query
        """
        prompt_cls: type[OcrFusionPrompt] = getattr(model, "prompt_cls")
        source_one = getattr(model, prompt_cls.src_1, None)
        source_two = getattr(model, prompt_cls.src_2, None)
        if not source_one:
            raise ValueError(prompt_cls.src_1_missing_err)
        if not source_two:
            raise ValueError(prompt_cls.src_2_missing_err)
        if source_one == source_two:
            raise ValueError(prompt_cls.src_1_src_2_equal_err)
        return model
