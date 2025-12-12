#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 transcription translation test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import Field, create_model

from scinoephile.core import ScinoephileError
from scinoephile.core.llms import TestCase2
from scinoephile.core.models import get_model_name

from .answer2 import TranslationAnswer2
from .prompt2 import TranslationPrompt2
from .query2 import TranslationQuery2

__all__ = ["TranslationTestCase2"]


class TranslationTestCase2(TestCase2, ABC):
    """Abstract base class for 粤文 transcription translation test cases."""

    answer_cls: ClassVar[type[TranslationAnswer2]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[TranslationQuery2]]
    """Query class for this test case."""
    prompt_cls: ClassVar[type[TranslationPrompt2]]
    """Text strings to be used for corresponding with LLM."""

    size: ClassVar[int]
    """Number of subtitles."""
    missing: ClassVar[tuple[int, ...]]
    """Indexes of missing subtitles (0-indexed)."""

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        size: int,
        missing: tuple[int, ...],
        prompt_cls: type[TranslationPrompt2] = TranslationPrompt2,
    ) -> type[Self]:
        """Get concrete test case class with provided configuration.

        Arguments:
            size: number of subtitles
            missing: indexes of missing subtitles
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            TestCase type with appropriate configuration
        """
        if any(m < 0 or m > size for m in missing):
            raise ScinoephileError(
                f"Missing indices must be in range 1 to {size}, got {missing}."
            )

        name = get_model_name(
            cls.__name__,
            f"{size}_"
            f"{'-'.join(map(str, [m + 1 for m in missing]))}_"
            f"{prompt_cls.__name__}",
        )
        query_cls = TranslationQuery2.get_query_cls(size, missing, prompt_cls)
        answer_cls = TranslationAnswer2.get_answer_cls(size, missing, prompt_cls)
        fields: dict[str, Any] = {
            "query": (query_cls, Field(...)),
            "answer": (answer_cls | None, Field(default=None)),
            "difficulty": (
                int,
                Field(0, description=prompt_cls.difficulty_description),
            ),
            "prompt": (
                bool,
                Field(False, description=prompt_cls.prompt_description),
            ),
            "verified": (
                bool,
                Field(False, description=prompt_cls.verified_description),
            ),
        }

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        model.prompt_cls = prompt_cls
        model.size = size
        model.missing = missing
        return model

    @classmethod
    def get_test_case_cls_from_data(cls, data: dict, **kwargs: Any) -> type[Self]:
        """Get concrete test case class for provided data with provided configuration.

        Arguments:
            data: data dictionary
            kwargs: additional keyword arguments passed to get_test_case_cls
        Returns:
            test case class
        """
        size = sum(1 for key in data["query"] if key.startswith("zhongwen_"))
        yuewen_idxs = [
            int(key.split("_")[-1]) - 1
            for key in data["query"]
            if key.startswith("yuewen_")
        ]
        missing = tuple(idx for idx in range(size) if idx not in yuewen_idxs)
        test_case_cls = cls.get_test_case_cls(size=size, missing=missing, **kwargs)
        return test_case_cls
