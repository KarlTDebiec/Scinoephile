#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for blockwise review test cases."""

from __future__ import annotations

import re
from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import create_model, model_validator

from scinoephile.core.llms import TestCase
from scinoephile.core.llms.models import get_model_name

from .answer import BlockwiseAnswer
from .prompt import BlockwisePrompt
from .query import BlockwiseQuery

__all__ = ["BlockwiseTestCase"]


class BlockwiseTestCase(TestCase, ABC):
    """ABC for blockwise review test cases."""

    answer_cls: ClassVar[type[BlockwiseAnswer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[BlockwiseQuery]]
    """Query class for this test case."""
    prompt_cls: ClassVar[type[BlockwisePrompt]]
    """Text for LLM correspondence."""

    size: ClassVar[int]
    """Number of items."""

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
        if self.answer is None:
            return min_difficulty

        if any(
            getattr(self.answer, self.prompt_cls.output_field(idx)) != ""
            for idx in range(1, self.size + 1)
        ):
            min_difficulty = max(min_difficulty, 1)
        return min_difficulty

    @model_validator(mode="after")
    def validate_test_case(self) -> Self:
        """Ensure query and answer together are valid."""
        if self.answer is None:
            return self

        for idx in range(self.size):
            input_text = getattr(self.query, self.prompt_cls.input_field(idx + 1))
            output_text = getattr(self.answer, self.prompt_cls.output_field(idx + 1))
            note = getattr(self.answer, self.prompt_cls.note_field(idx + 1))
            if output_text != "":
                if input_text == output_text:
                    raise ValueError(self.prompt_cls.output_unmodified_error(idx + 1))
                if note == "":
                    raise ValueError(self.prompt_cls.note_missing_error(idx + 1))
            elif note != "":
                raise ValueError(self.prompt_cls.output_missing_error(idx + 1))
        return self

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        size: int,
        prompt_cls: type[BlockwisePrompt],
    ) -> type[Self]:
        """Get concrete test case class with provided configuration.

        Arguments:
            size: number of items
            prompt_cls: text for LLM correspondence
        Returns:
            TestCase type with appropriate configuration
        """
        name = get_model_name(cls.__name__, f"{size}_{prompt_cls.__name__}")
        query_cls = BlockwiseQuery.get_query_cls(size, prompt_cls)
        answer_cls = BlockwiseAnswer.get_answer_cls(size, prompt_cls)
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
        prompt_cls = kwargs.get("prompt_cls")
        pattern = re.compile(rf"^{re.escape(prompt_cls.input_prefix)}\d+$")
        size = sum(1 for field in data["query"] if pattern.match(field))
        return cls.get_test_case_cls(size=size, **kwargs)
