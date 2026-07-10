#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for OCR fusion LLM classes."""

from __future__ import annotations

from functools import cache
from typing import Any, ClassVar

from pydantic import Field, create_model, model_validator

from scinoephile.core.llms import Answer, Manager, Query, TestCase
from scinoephile.core.llms.models import get_model_name

from .prompt import OcrFusionPrompt

__all__ = ["OcrFusionManager"]


class OcrFusionManager(Manager):
    """Factories for OCR fusion LLM classes."""

    operation: ClassVar[str] = "ocr-fusion"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[OcrFusionPrompt] = OcrFusionPrompt()
    """Base prompt defining persisted test-case field names."""

    @classmethod
    @cache
    def get_answer_cls(cls, prompt: OcrFusionPrompt) -> type[Answer]:
        """Get concrete answer class with provided configuration.

        Arguments:
            prompt: text for LLM correspondence
        Returns:
            answer model class
        """
        name = get_model_name(Answer.__name__, prompt.name)
        fields: dict[str, Any] = {
            prompt.output: (str, Field(..., description=prompt.output_desc)),
            prompt.note: (str, Field(..., description=prompt.note_desc)),
        }
        validators: dict[str, Any] = {
            "validate_answer": model_validator(mode="after")(cls.validate_answer),
        }

        model = create_model(
            name,
            __base__=Answer,
            __module__=Answer.__module__,
            __validators__=validators,
            **fields,
        )
        model.prompt = prompt
        return model

    @classmethod
    @cache
    def get_query_cls(cls, prompt: OcrFusionPrompt) -> type[Query]:
        """Get concrete query class with provided configuration.

        Arguments:
            prompt: text for LLM correspondence
        Returns:
            query model class
        """
        name = get_model_name(Query.__name__, prompt.name)
        fields: dict[str, Any] = {
            prompt.src_1: (str, Field(..., description=prompt.src_1_desc)),
            prompt.src_2: (str, Field(..., description=prompt.src_2_desc)),
        }
        validators: dict[str, Any] = {
            "validate_query": model_validator(mode="after")(cls.validate_query),
        }

        model = create_model(
            name,
            __base__=Query,
            __module__=Query.__module__,
            __validators__=validators,
            **fields,
        )
        model.prompt = prompt
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

        prompt: OcrFusionPrompt = getattr(model, "prompt")
        source_one = getattr(model.query, prompt.src_1, None)
        source_two = getattr(model.query, prompt.src_2, None)
        output_text = getattr(model.answer, prompt.output, None)
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
        prompt: OcrFusionPrompt = getattr(model, "prompt")
        min_difficulty = max(Manager.get_min_difficulty(model), 1)
        if model.answer is None:
            return min_difficulty

        if output_text := getattr(model.answer, prompt.output):
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
        prompt: OcrFusionPrompt = getattr(model, "prompt")
        output = getattr(model, prompt.output, None)
        note = getattr(model, prompt.note, None)
        if not output:
            raise ValueError(prompt.output_missing_err)
        if not note:
            raise ValueError(prompt.note_missing_err)
        return model

    @staticmethod
    def validate_query(model: Query) -> Query:
        """Ensure query is internally valid.

        Arguments:
            model: query to validate
        Returns:
            validated query
        """
        prompt: OcrFusionPrompt = getattr(model, "prompt")
        source_one = getattr(model, prompt.src_1, None)
        source_two = getattr(model, prompt.src_2, None)
        if not source_one:
            raise ValueError(prompt.src_1_missing_err)
        if not source_two:
            raise ValueError(prompt.src_2_missing_err)
        if source_one == source_two:
            raise ValueError(prompt.src_1_src_2_equal_err)
        return model
