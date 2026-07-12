#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for OCR fusion LLM classes."""

from __future__ import annotations

from functools import cache
from typing import ClassVar

from scinoephile.core.llms import (
    Answer,
    Manager,
    PromptModelField,
    Query,
    TestCase,
)

from .models import OcrFusionAnswer, OcrFusionQuery, OcrFusionTestCase
from .prompt import OcrFusionPrompt

__all__ = ["OcrFusionManager"]


class OcrFusionManager(Manager):
    """Factories for OCR fusion LLM classes."""

    operation: ClassVar[str] = "ocr-fusion"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[OcrFusionPrompt] = OcrFusionTestCase.prompt
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
        return cls.create_prompt_model(
            OcrFusionAnswer,
            prompt,
            {
                "output": PromptModelField(
                    alias=prompt.output,
                    description=prompt.output_desc,
                ),
                "note": PromptModelField(
                    alias=prompt.note,
                    description=prompt.note_desc,
                ),
            },
            module=Answer.__module__,
            name=Answer.__name__,
        )

    @classmethod
    @cache
    def get_query_cls(cls, prompt: OcrFusionPrompt) -> type[Query]:
        """Get concrete query class with provided configuration.

        Arguments:
            prompt: text for LLM correspondence
        Returns:
            query model class
        """
        return cls.create_prompt_model(
            OcrFusionQuery,
            prompt,
            {
                "source_one": PromptModelField(
                    alias=prompt.src_1,
                    description=prompt.src_1_desc,
                ),
                "source_two": PromptModelField(
                    alias=prompt.src_2,
                    description=prompt.src_2_desc,
                ),
            },
            module=Query.__module__,
            name=Query.__name__,
        )
