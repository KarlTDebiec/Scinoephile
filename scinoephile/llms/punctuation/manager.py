#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for punctuation LLM classes."""

from __future__ import annotations

from functools import cache
from typing import Any, ClassVar

from pydantic import Field, create_model, model_validator

from scinoephile.core.llms import Answer, Manager, Query
from scinoephile.core.llms.models import get_model_name

from .prompt import PunctuationPrompt

__all__ = ["PunctuationManager"]


class PunctuationManager(Manager):
    """Factories for punctuation LLM classes."""

    operation: ClassVar[str] = "punctuation"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[PunctuationPrompt] = PunctuationPrompt()
    """Base prompt defining persisted test-case field names."""

    @classmethod
    @cache
    def get_query_cls(
        cls,
        prompt: PunctuationPrompt,
    ) -> type[Query]:
        """Get concrete query class with provided configuration.

        Arguments:
            prompt: text for LLM correspondence
        Returns:
            query model class
        """
        name = get_model_name("PunctuationQuery", prompt.name)
        fields: dict[str, Any] = {
            prompt.src_1: (
                list[str],
                Field(..., description=prompt.src_1_desc),
            ),
            prompt.src_2: (
                str,
                Field(..., description=prompt.src_2_desc),
            ),
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

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        prompt: PunctuationPrompt,
    ) -> type[Answer]:
        """Get concrete answer class with provided configuration.

        Arguments:
            prompt: text for LLM correspondence
        Returns:
            answer model class
        """
        name = get_model_name("PunctuationAnswer", prompt.name)
        fields: dict[str, Any] = {
            prompt.output: (
                str,
                Field(..., description=prompt.output_desc),
            ),
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

    @staticmethod
    def validate_query(model: Query) -> Query:
        """Ensure query is internally valid.

        Arguments:
            model: query to validate
        Returns:
            validated query
        """
        prompt: PunctuationPrompt = getattr(model, "prompt")
        source_one = getattr(model, prompt.src_1, None)
        source_two = getattr(model, prompt.src_2, None)
        if not source_one:
            raise ValueError(prompt.src_1_missing_err)
        if not source_two:
            raise ValueError(prompt.src_2_missing_err)
        return model

    @staticmethod
    def validate_answer(model: Answer) -> Answer:
        """Ensure answer is internally valid.

        Arguments:
            model: answer to validate
        Returns:
            validated answer
        """
        prompt: PunctuationPrompt = getattr(model, "prompt")
        output = getattr(model, prompt.output, None)
        if not output:
            raise ValueError(prompt.output_missing_err)
        return model
