#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for OCR fusion LLM classes."""

from __future__ import annotations

from functools import cache
from typing import Any, ClassVar

from pydantic import Field, create_model

from scinoephile.core.llms import Answer, Manager, Query, TestCase
from scinoephile.core.llms.models import get_model_name

from .models import OcrFusionAnswer, OcrFusionQuery, OcrFusionTestCase
from .prompt import OcrFusionPrompt

__all__ = ["OcrFusionManager"]


class OcrFusionManager(Manager):
    """Factories for OCR fusion LLM classes."""

    operation: ClassVar[str] = "ocr-fusion"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[OcrFusionPrompt] = OcrFusionPrompt()
    """Base prompt defining persisted test-case field names."""
    test_case_base_cls: ClassVar[type[TestCase]] = OcrFusionTestCase
    """Static test-case model defining OCR fusion's semantic shape."""

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
            "output": (
                str,
                Field(..., alias=prompt.output, description=prompt.output_desc),
            ),
            "note": (
                str,
                Field(..., alias=prompt.note, description=prompt.note_desc),
            ),
        }

        model = create_model(
            name,
            __base__=OcrFusionAnswer,
            __module__=Answer.__module__,
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
            "source_one": (
                str,
                Field(..., alias=prompt.src_1, description=prompt.src_1_desc),
            ),
            "source_two": (
                str,
                Field(..., alias=prompt.src_2, description=prompt.src_2_desc),
            ),
        }

        model = create_model(
            name,
            __base__=OcrFusionQuery,
            __module__=Query.__module__,
            **fields,
        )
        model.prompt = prompt
        return model
