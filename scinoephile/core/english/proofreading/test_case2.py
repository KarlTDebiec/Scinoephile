#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for English proofreading test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import Field, create_model, model_validator

from scinoephile.core.abcs.test_case2 import TestCase2

from .answer2 import EnglishProofreadingAnswer2
from .prompt2 import EnglishProofreadingPrompt2
from .query2 import EnglishProofreadingQuery2

__all__ = ["EnglishProofreadingTestCase2"]


class EnglishProofreadingTestCase2(
    TestCase2[EnglishProofreadingQuery2, EnglishProofreadingAnswer2], ABC
):
    """Abstract base class for English proofreading test cases."""

    answer_cls: ClassVar[type[EnglishProofreadingAnswer2]]  # type: ignore
    """Answer class for this test case."""
    query_cls: ClassVar[type[EnglishProofreadingQuery2]]  # type: ignore
    """Query class for this test case."""
    prompt_cls: ClassVar[type[EnglishProofreadingPrompt2]]  # type: ignore
    """Text strings to be used for corresponding with LLM."""

    size: ClassVar[int]
    """Number of subtitles."""

    @model_validator(mode="after")
    def validate_test_case(self) -> Self:
        """Ensure query and answer together are valid."""
        if self.answer is None:
            return self

        subtitle_revised_equal_error = self.prompt_cls.subtitle_revised_equal_error
        note_missing_error = self.prompt_cls.note_missing_error
        revised_missing_error = self.prompt_cls.revised_missing_error

        for idx in range(self.size):
            subtitle = getattr(self.query, f"subtitle_{idx + 1}")
            revised = getattr(self.answer, f"revised_{idx + 1}")
            note = getattr(self.answer, f"note_{idx + 1}")
            if revised != "":
                if subtitle == revised:
                    raise ValueError(subtitle_revised_equal_error.format(idx=idx + 1))
                if note == "":
                    raise ValueError(note_missing_error.format(idx=idx + 1))
            elif note != "":
                raise ValueError(revised_missing_error.format(idx=idx + 1))
        return self

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        size: int,
        prompt_cls: type[EnglishProofreadingPrompt2] = EnglishProofreadingPrompt2,
    ) -> type[Self]:
        """Get concrete test case class with provided size and text.

        Arguments:
            size: number of subtitles
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            TestCase type with appropriate fields and text
        """
        name = f"{cls.__name__}_{size}_{prompt_cls.__name__}"
        query_cls = EnglishProofreadingQuery2.get_query_cls(size, prompt_cls)
        answer_cls = EnglishProofreadingAnswer2.get_answer_cls(size, prompt_cls)
        fields = {
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
        return model
