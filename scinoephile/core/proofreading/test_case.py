#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Concrete test case factory for proofreading."""

from __future__ import annotations

import re
from functools import cache
from typing import Any, ClassVar, Self, cast

from pydantic import create_model, model_validator

from scinoephile.core.llms import Answer, Prompt, Query, TestCase
from scinoephile.core.models import get_model_name
from scinoephile.core.proofreading.answer import ProofreadingAnswer
from scinoephile.core.proofreading.prompt import ProofreadingPrompt
from scinoephile.core.proofreading.query import ProofreadingQuery

__all__ = ["ProofreadingTestCase"]


class ProofreadingTestCase(TestCase):
    """Concrete test case factory for proofreading."""

    answer_cls: ClassVar[type[Answer]] = ProofreadingAnswer
    """Answer class for this test case."""
    query_cls: ClassVar[type[Query]] = ProofreadingQuery
    """Query class for this test case."""
    prompt_cls: ClassVar[type[Prompt]] = ProofreadingPrompt
    """Text strings to be used for corresponding with LLM."""

    size: ClassVar[int]
    """Number of subtitles."""

    answer: ProofreadingAnswer | None
    """Answer associated with this test case."""

    query: ProofreadingQuery
    """Query associated with this test case."""

    prompt: bool
    """Whether this test case should be included in the prompt."""

    verified: bool
    """Whether this test case has been verified."""

    def get_min_difficulty(self) -> int:
        """Get minimum difficulty based on the test case properties.

        0: No change needed
        1: Change needed
        2: Difficult change needed, worthy of inclusion in prompt or difficult test set
        3: Not considered realistic for LLM to handle correctly

        Returns:
            minimum difficulty level based on the test case properties
        """
        min_difficulty = super().get_min_difficulty()
        prompt_cls = cast(type[ProofreadingPrompt], self.prompt_cls)
        if self.answer is not None:
            if any(
                getattr(self.answer, prompt_cls.revised_field(idx)) != ""
                for idx in range(1, self.size + 1)
            ):
                min_difficulty = max(min_difficulty, 1)
        return min_difficulty

    @model_validator(mode="after")
    def validate_test_case(self) -> Self:
        """Ensure query and answer together are valid."""
        if self.answer is None:
            return self

        prompt_cls = cast(type[ProofreadingPrompt], self.prompt_cls)

        for idx in range(self.size):
            subtitle = getattr(self.query, prompt_cls.subtitle_field(idx + 1))
            revised = getattr(self.answer, prompt_cls.revised_field(idx + 1))
            note = getattr(self.answer, prompt_cls.note_field(idx + 1))
            if revised != "":
                if subtitle == revised:
                    raise ValueError(prompt_cls.subtitle_revised_equal_error(idx + 1))
                if note == "":
                    raise ValueError(prompt_cls.note_missing_error(idx + 1))
            elif note != "":
                raise ValueError(prompt_cls.revised_missing_error(idx + 1))
        return self

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        size: int,
        prompt_cls: type[ProofreadingPrompt] | None = None,
    ) -> type[Self]:
        """Get concrete test case class with provided configuration.

        Arguments:
            size: number of subtitles
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            TestCase type with appropriate configuration
        """
        prompt_cls = cast(type[ProofreadingPrompt], prompt_cls or cls.prompt_cls)

        name = get_model_name(cls.__name__, f"{size}_{prompt_cls.__name__}")
        query_cls = ProofreadingQuery.get_query_cls(size, prompt_cls)
        answer_cls = ProofreadingAnswer.get_answer_cls(size, prompt_cls)
        fields = cls.get_fields(query_cls, answer_cls, prompt_cls)

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        model.prompt_cls = prompt_cls
        model.size = size
        return model

    @classmethod
    def get_test_case_cls_from_data(cls, data: dict, **kwargs: Any) -> type[Self]:
        """Get concrete test case class for provided data with provided configuration.

        Arguments:
            data: data from JSON
            kwargs: additional keyword arguments passed to get_test_case_cls
        Returns:
            TestCase type with appropriate configuration
        """
        prompt_cls = cast(
            type[ProofreadingPrompt], kwargs.get("prompt_cls", cls.prompt_cls)
        )

        pattern = re.compile(rf"^{re.escape(prompt_cls.subtitle_prefix)}\d+$")
        size = sum(1 for field in data["query"] if pattern.match(field))
        return cls.get_test_case_cls(size=size, prompt_cls=prompt_cls, **kwargs)
