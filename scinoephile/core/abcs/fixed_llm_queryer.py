#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for LLM queryers whose classes are fixed for all requests."""

from __future__ import annotations

from abc import ABC
from functools import cached_property
from typing import get_args, get_origin

from scinoephile.core.abcs.answer import Answer
from scinoephile.core.abcs.llm_queryer import LLMQueryer
from scinoephile.core.abcs.query import Query
from scinoephile.core.abcs.test_case import TestCase


class FixedLLMQueryer[TQuery: Query, TAnswer: Answer, TTestCase: TestCase](
    LLMQueryer[TQuery, TAnswer, TTestCase], ABC
):
    """Abstract base class for LLM queryers whose classes are fixed for all requests."""

    def __call__(self, query: TQuery) -> TAnswer:
        """Query LLM.

        Arguments:
            query: query for LLM
        Returns:
            LLM's answer
        """
        answer = self._call(
            system_prompt=self.system_prompt,
            query=query,
            answer_cls=self.answer_cls,
            test_case_cls=self.test_case_cls,
        )
        return answer

    async def acall(self, query: TQuery) -> TAnswer:
        """Query LLM asynchronously.

        Arguments:
            query: query for LLM
        Returns:
            LLM's answer
        """
        answer = await self._acall(
            system_prompt=self.system_prompt,
            query=query,
            answer_cls=self.answer_cls,
            test_case_cls=self.test_case_cls,
        )
        return answer

    @cached_property
    def answer_cls(self) -> type[TAnswer]:
        """Answer class."""
        for base in getattr(self.__class__, "__orig_bases__", []):
            if get_origin(base) is FixedLLMQueryer:
                return get_args(base)[1]
        raise TypeError(
            f"Could not determine answer class for {self.__class__.__name__}"
        )

    @cached_property
    def answer_example(self) -> TAnswer:
        """Example answer."""
        return self.answer_cls(
            **{
                field_name: f"{field.description}"
                for field_name, field in self.answer_cls.model_fields.items()
            }
        )

    @property
    def encountered_test_cases_source_str(self) -> str:
        """String representation of all test cases in the log."""
        test_case_log_str = "[\n"
        for test_case in self._encountered_test_cases.values():
            source_str: str = test_case.source_str
            test_case_log_str += f"{source_str},\n"
        test_case_log_str += "]"
        return test_case_log_str

    @cached_property
    def query_cls(self) -> type[TQuery]:
        """Query class."""
        for base in getattr(self.__class__, "__orig_bases__", []):
            if get_origin(base) is FixedLLMQueryer:
                return get_args(base)[0]
        raise TypeError(
            f"Could not determine query class for {self.__class__.__name__}"
        )

    @cached_property
    def system_prompt(self) -> str:
        """System prompt template."""
        return self._get_system_prompt(self.answer_example)

    @cached_property
    def test_case_cls(self) -> type[TTestCase]:
        """Test case class."""
        for base in getattr(self.__class__, "__orig_bases__", []):
            if get_origin(base) is FixedLLMQueryer:
                return get_args(base)[2]
        raise TypeError(
            f"Could not determine test case class for {self.__class__.__name__}"
        )
