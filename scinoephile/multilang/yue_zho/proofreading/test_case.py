#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Proofreading-specific DualSingle test case."""

from __future__ import annotations

from functools import cache
from typing import ClassVar, Self

from pydantic import create_model, model_validator

from scinoephile.llms.base.models import get_model_name
from scinoephile.llms.dual_single import (
    DualSinglePrompt,
    DualSingleQuery,
    DualSingleTestCase,
)

from .answer import YueZhoProofreadingAnswer

__all__ = ["YueZhoProofreadingTestCase"]


class YueZhoProofreadingTestCase(DualSingleTestCase):
    """DualSingle test case with relaxed note/output rules for proofreading."""

    answer_cls: ClassVar[type[YueZhoProofreadingAnswer]]

    @model_validator(mode="after")
    def validate_test_case(self) -> Self:
        """Require notes only when the output differs from the sources."""
        if self.answer is None:
            return self

        output = getattr(self.answer, self.prompt_cls.output_field, None)
        note = getattr(self.answer, self.prompt_cls.note_field, None)
        source_one = getattr(self.query, self.prompt_cls.source_one_field, None)
        source_two = getattr(self.query, self.prompt_cls.source_two_field, None)

        if output not in (source_one, source_two) and not note:
            raise ValueError(self.prompt_cls.note_missing_error)
        return self

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        prompt_cls: type[DualSinglePrompt],
    ) -> type[Self]:
        """Get concrete proofreading test case class."""
        name = get_model_name(cls.__name__, prompt_cls.__name__)
        query_cls = DualSingleQuery.get_query_cls(prompt_cls)
        answer_cls = YueZhoProofreadingAnswer.get_answer_cls(prompt_cls)
        fields = cls.get_fields(query_cls, answer_cls, prompt_cls)

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        model.prompt_cls = prompt_cls
        return model
