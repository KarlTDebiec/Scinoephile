#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for dual track / single subtitle LLM classes."""

from __future__ import annotations

from functools import cache
from typing import Any

from pydantic import Field, create_model, model_validator

from scinoephile.llms.base import Answer, Manager, Query
from scinoephile.llms.base.models import get_model_name

from .prompt import DualSinglePrompt

__all__ = ["DualSingleManager"]


class DualSingleManager(Manager):
    """Factories for dual track / single subtitle LLM classes."""

    @classmethod
    @cache
    def get_query_cls[TQuery: Query](
        cls,
        prompt_cls: type[DualSinglePrompt],
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

        model = create_model(
            name,
            __base__=Query,
            __module__=Query.__module__,
            __validators__=validators,
            **fields,
        )
        model.prompt_cls = prompt_cls
        return model

    @classmethod
    @cache
    def get_answer_cls[TAnswer: Answer](
        cls,
        prompt_cls: type[DualSinglePrompt],
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

        model = create_model(
            name,
            __base__=Answer,
            __module__=Answer.__module__,
            __validators__=validators,
            **fields,
        )
        model.prompt_cls = prompt_cls
        return model

    @staticmethod
    def validate_query(model: Query) -> Query:
        """Ensure query is internally valid.

        Arguments:
            model: query to validate
        Returns:
            validated query
        """
        source_one = getattr(model, model.prompt_cls.src_1, None)
        source_two = getattr(model, model.prompt_cls.src_2, None)
        if not source_one:
            raise ValueError(model.prompt_cls.src_1_missing_err)
        if not source_two:
            raise ValueError(model.prompt_cls.src_2_missing_err)
        if source_one == source_two:
            raise ValueError(model.prompt_cls.src_1_src_2_equal_err)
        return model

    @staticmethod
    def validate_answer(model: Answer) -> Answer:
        """Ensure answer is internally valid.

        Arguments:
            model: answer to validate
        Returns:
            validated answer
        """
        output = getattr(model, model.prompt_cls.output, None)
        note = getattr(model, model.prompt_cls.note, None)
        output_err = getattr(model.prompt_cls, "output_missing_err", None)
        note_err = getattr(model.prompt_cls, "note_missing_err", None)
        if output_err and not output:
            raise ValueError(output_err)
        if note_err and not note:
            raise ValueError(note_err)
        return model
