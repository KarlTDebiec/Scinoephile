#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for LLM queryers whose classes vary between requests."""

from __future__ import annotations

from abc import ABC, abstractmethod
from asyncio import run

from scinoephile.core import ScinoephileError
from scinoephile.core.abcs.answer import Answer
from scinoephile.core.abcs.llm_queryer import LLMQueryer
from scinoephile.core.abcs.query import Query
from scinoephile.core.abcs.test_case import TestCase


class DynamicLLMQueryer[TQuery: Query, TAnswer: Answer, TTestCase: TestCase](
    LLMQueryer[TQuery, TAnswer, TTestCase], ABC
):
    """Abstract base class for LLM queryers whose classes vary between requests."""

    def __call__(
        self,
        query: Query,
        answer_cls: type[TAnswer],
        test_case_cls: type[TTestCase],
    ) -> TAnswer:
        """Query LLM.

        Arguments:
            query: Query for LLM
            answer_cls: Class of answer to return
            test_case_cls: Class of test case to return
        Returns:
            LLM's answer
        """
        return run(self.call(query, answer_cls, test_case_cls))

    async def call(
        self,
        query: Query,
        answer_cls: type[TAnswer],
        test_case_cls: type[TTestCase],
    ) -> TAnswer:
        """Query LLM asynchronously.

        Arguments:
            query: Query for LLM
            answer_cls: Class of answer to return
            test_case_cls: Class of test case to return
        Returns:
            LLM's answer
        """
        answer = await self._call(
            system_prompt=self.get_system_prompt(answer_cls),
            query=query,
            answer_cls=answer_cls,
            test_case_cls=test_case_cls,
        )
        return answer

    @property
    def encountered_test_cases_source_str(self) -> str:
        """String representation of all test cases in the log."""
        if len(self._encountered_test_cases) == 0:
            return "None"
        if len(self._encountered_test_cases) == 1:
            return next(iter(self._encountered_test_cases.values())).source_str
        raise ScinoephileError(
            "Test case log must contain zero or one test cases for string "
            "representation."
        )

    def get_system_prompt(self, answer_cls: type[TAnswer]) -> str:
        """Get system prompt for the given answer class.

        Arguments:
            answer_cls: Class of answer to return
        Returns:
            System prompt for the given answer class
        """
        answer_example = self.get_answer_example(answer_cls)
        return self._get_system_prompt(answer_example)

    @staticmethod
    @abstractmethod
    def get_answer_example(answer_cls: type[TAnswer]) -> TAnswer:
        """Example answer."""
        raise NotImplementedError()
