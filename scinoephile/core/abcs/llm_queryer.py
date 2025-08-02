#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for LLM queryers."""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from functools import cached_property
from logging import debug, error, info
from pathlib import Path
from textwrap import dedent
from typing import get_args, get_origin

from pydantic import ValidationError

from scinoephile.common.validation import val_output_dir_path
from scinoephile.core import ScinoephileError
from scinoephile.core.abcs.answer import Answer
from scinoephile.core.abcs.llm_provider import LLMProvider
from scinoephile.core.abcs.query import Query
from scinoephile.core.abcs.test_case import TestCase
from scinoephile.openai.openai_provider import OpenAIProvider


class LLMQueryer[TQuery: Query, TAnswer: Answer, TTestCase: TestCase](ABC):
    """Abstract base class for LLM queryers."""

    def __init__(
        self,
        model: str = "gpt-4.1",
        examples: list[TTestCase] | None = None,
        verified: list[TTestCase] | None = None,
        provider: LLMProvider | None = None,
        *,
        cache_dir_path: str | None = None,
        print_test_case: bool = False,
        max_attempts: int = 2,
    ):
        """Initialize.

        Arguments:
            model: Model to use
            examples: Examples of inputs and expected outputs for few-shot learning
            verified: Verified test cases whose answers are already known
            provider: Provider to use for queries
            cache_dir_path: Directory in which to cache
            print_test_case: Whether to print test case after merging
            max_attempts: Maximum number of attempts
        """
        self.provider = provider or OpenAIProvider()
        """LLM Provider to use for queries."""
        self.model = model
        """Model name to use for queries."""

        self._examples_log: dict[tuple, TTestCase] = {}
        """Log of examples, keyed by query key."""
        self._verified_log: dict[tuple, TTestCase] = {}
        """Log of verified test cases, keyed by query key."""
        self._test_case_log: dict[tuple, TTestCase] = {}
        """Log of test cases, keyed by query key."""

        # Set up system prompt, with examples if provided
        system_prompt = dedent(self.base_system_prompt).strip().replace("\n", " ")
        system_prompt += (
            "\nYour response must be a JSON object with the following structure:\n"
        )
        system_prompt += json.dumps(
            self.answer_example.model_dump(), indent=4, ensure_ascii=False
        )
        if examples:
            system_prompt += (
                "\n\nHere are some examples of queries and expected answers:"
            )
            for example in examples:
                system_prompt += "\n\nExample query:\n"
                system_prompt += json.dumps(
                    example.query.model_dump(), indent=4, ensure_ascii=False
                )
                system_prompt += "\nExpected answer:\n"
                system_prompt += json.dumps(
                    example.answer.model_dump(), indent=4, ensure_ascii=False
                )
                self._examples_log[example.query.query_key] = example
        self._system_prompt = system_prompt

        # Set up verified log
        if verified is not None:
            for test_case in verified:
                self._verified_log[test_case.query.query_key] = test_case

        # Set up cache directory
        self.cache_dir_path = None
        """Directory in which to cache query results."""
        if cache_dir_path is not None:
            self.cache_dir_path = val_output_dir_path(cache_dir_path)

        self.print_test_case = print_test_case
        """Whether to print test case after merging query and answer."""
        self.max_attempts = max_attempts
        """Maximum number of query attempts."""

    def __call__(self, query: TQuery) -> TAnswer:
        """Query LLM.

        Arguments:
            query: query for LLM
        Returns:
            LLM's answer
        """
        query_prompt = json.dumps(query.model_dump(), indent=4, ensure_ascii=False)

        # Load from verified log if available
        if query.query_key in self._verified_log:
            info(f"Loaded from verified log: {query.query_key}")
            test_case = self._verified_log[query.query_key]
            answer = test_case.answer
            self.log_test_case(test_case)
            return answer

        # Load from cache if available
        cache_path = self._get_cache_path(query_prompt)
        if cache_path is not None and cache_path.exists():
            info(f"Loaded from cache: {query.query_key}")
            with cache_path.open("r", encoding="utf-8") as f:
                answer = self.answer_cls.model_validate(json.load(f))
                test_case = self.test_case_cls.from_query_and_answer(query, answer)
                self.log_test_case(test_case)
                return answer

        # Query provider
        answer: TAnswer | None = None
        test_case: TTestCase | None = None
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": query_prompt},
        ]
        for attempt in range(1, self.max_attempts + 1):
            # Get answer from provider
            try:
                content = self.provider.chat_completion(
                    model=self.model,
                    messages=messages,
                    temperature=0,
                    seed=0,
                    response_format=self.answer_cls,
                )
            except ScinoephileError as exc:
                error(f"Attempt {attempt} failed: {type(exc).__name__}: {exc}")
                if attempt == self.max_attempts:
                    raise
                continue

            # Validate answer
            try:
                answer = self.answer_cls.model_validate_json(content)
            except ValidationError as exc:
                error(
                    f"Query:\n{query}\n"
                    f"Yielded invalid content (attempt {attempt}):\n{content}"
                )
                if attempt == self.max_attempts:
                    raise exc
                messages.append({"role": "assistant", "content": content})
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "Your previous response was not valid JSON or did not "
                            "match the expected schema. "
                            "Error details:\n"
                            f"{'\n'.join([e['msg'] for e in exc.errors()])}. "
                            "Please try again and respond only with a valid JSON "
                            "object."
                        ),
                    }
                )
                continue

            # Validate test case
            try:
                test_case = self.test_case_cls.from_query_and_answer(query, answer)
            except ValidationError as exc:
                error(
                    f"Query:\n{query}\n"
                    f"Yielded invalid answer (attempt {attempt}):\n{answer}"
                )
                if attempt == self.max_attempts:
                    raise exc
                messages.append({"role": "assistant", "content": content})
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "Your previous response was valid JSON, but failed "
                            "validation when combined with the query.\n"
                            "Error details:\n"
                            f"{'\n'.join([e['msg'] for e in exc.errors()])}\n"
                            "Please revise your response accordingly."
                        ),
                    }
                )
                continue

            break
        if answer is None or test_case is None:
            raise ScinoephileError("Unable to obtain valid answer")

        # Log test case
        self.log_test_case(test_case)

        # Update cache
        if cache_path is not None:
            with cache_path.open("w", encoding="utf-8") as f:
                json.dump(answer.model_dump(), f, ensure_ascii=False, indent=2)
                debug(f"Saved to cache: {cache_path}")

        return answer

    @property
    def test_case_log(self) -> dict[tuple, TTestCase]:
        """Log of test cases, keyed by query key."""
        return self._test_case_log

    @property
    def test_case_log_str(self) -> str:
        """String representation of all test cases in the log."""
        test_case_log_str = "[\n"
        for test_case in self._test_case_log.values():
            source_str: str = test_case.source_str
            test_case_log_str += f"{source_str},\n"
        test_case_log_str += "]"
        return test_case_log_str

    @cached_property
    @abstractmethod
    def answer_example(self) -> TAnswer:
        """Example answer."""
        raise NotImplementedError()

    @cached_property
    def answer_cls(self) -> type[TAnswer]:
        """Answer class."""
        for base in getattr(self.__class__, "__orig_bases__", []):
            if get_origin(base) is LLMQueryer:
                return get_args(base)[1]
        raise TypeError(
            f"Could not determine answer class for {self.__class__.__name__}"
        )

    @cached_property
    @abstractmethod
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        raise NotImplementedError()

    @cached_property
    def query_cls(self) -> type[TQuery]:
        """Query class."""
        for base in getattr(self.__class__, "__orig_bases__", []):
            if get_origin(base) is LLMQueryer:
                return get_args(base)[0]
        raise TypeError(
            f"Could not determine answer class for {self.__class__.__name__}"
        )

    @property
    def system_prompt(self) -> str:
        """System prompt template."""
        return self._system_prompt

    @cached_property
    def test_case_cls(self) -> type[TTestCase]:
        """Test case class."""
        for base in getattr(self.__class__, "__orig_bases__", []):
            if get_origin(base) is LLMQueryer:
                return get_args(base)[2]
        raise TypeError(
            f"Could not determine answer class for {self.__class__.__name__}"
        )

    def clear_test_case_log(self):
        """Clear the test case log."""
        self._test_case_log.clear()

    def log_test_case(self, test_case: TTestCase):
        """Log a test case.

        Arguments:
            test_case: Test case to log
        """
        key = test_case.query.query_key
        if key in self._examples_log:
            test_case.prompt = True
        if key in self._verified_log:
            test_case.verified = True
        self._test_case_log[key] = test_case
        if self.print_test_case:
            print(f"{test_case.source_str},")
        debug(f"Logged test case: {test_case.query.query_key}")

    def _get_cache_path(self, query_prompt: str) -> Path | None:
        """Get cache path based on hash of prompts.

        Arguments:
            query_prompt: Query prompt used for the query
        Returns:
            Path to cache file
        """
        if self.cache_dir_path is None:
            return None

        prompt_str = self.system_prompt + query_prompt
        sha256 = hashlib.sha256(prompt_str.encode("utf-8")).hexdigest()
        return self.cache_dir_path / f"{sha256}.json"
