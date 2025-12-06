#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for LLM queryers."""

from __future__ import annotations

import asyncio
import hashlib
import json
from abc import ABC
from dataclasses import dataclass
from functools import cache
from logging import debug, error, info
from pathlib import Path
from typing import ClassVar

import aiofiles
from aiofiles import os as aioos
from pydantic import ValidationError

from scinoephile.common.validation import val_output_dir_path
from scinoephile.core.abcs.answer import Answer
from scinoephile.core.abcs.llm_provider import LLMProvider
from scinoephile.core.abcs.prompt import Prompt
from scinoephile.core.abcs.query import Query
from scinoephile.core.abcs.test_case import TestCase
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.providers import get_default_provider

__all__ = ["LLMQueryer", "LLMQueryerOptions"]


@dataclass
class LLMQueryerOptions:
    """Configuration options for :class:`LLMQueryer`."""

    max_attempts: int = 5
    auto_verify: bool = False


class LLMQueryer[TQuery: Query, TAnswer: Answer, TTestCase: TestCase](ABC):
    """Abstract base class for LLM queryers."""

    text: ClassVar[type[Prompt]]
    """Text strings to be used for corresponding with LLM."""

    def __init__(
        self,
        prompt_test_cases: list[TTestCase] | None = None,
        verified_test_cases: list[TTestCase] | None = None,
        provider: LLMProvider | None = None,
        *,
        cache_dir_path: str | Path | None = None,
        query_options: LLMQueryerOptions | None = None,
    ):
        """Initialize.

        Arguments:
            prompt_test_cases: test cases included in the prompt for few-shot learning
            verified_test_cases: test cases whose answers are verified and for which
              LLM need not be queried
            provider: provider to use for queries
            cache_dir_path: directory in which to cache
            query_options: options that control query behavior
        """
        self._provider = provider

        self.prompt_test_cases = {tc.query.key: tc for tc in prompt_test_cases or {}}
        """Test cases included in the prompt for few-shot learning."""
        self.verified_test_cases = {
            tc.query.key: tc for tc in verified_test_cases or {}
        }
        """Test cases whose answers are verified for which LLM will not be queried."""
        self.encountered_test_cases: dict[tuple, TTestCase] = {}
        """Test cases actually encountered."""

        self.cache_dir_path = None
        """Directory in which to cache query results."""
        if cache_dir_path is not None:
            self.cache_dir_path = val_output_dir_path(cache_dir_path)

        options = query_options or LLMQueryerOptions()

        self.max_attempts = options.max_attempts
        """Maximum number of query attempts."""
        self.auto_verify = options.auto_verify
        """Automatically verify test cases if they meet selected criteria."""

    def __call__(
        self, query: Query, answer_cls: type[TAnswer], test_case_cls: type[TTestCase]
    ) -> TAnswer:
        """Query LLM.

        Arguments:
            query: query for LLM
            answer_cls: class of answer to return
            test_case_cls: class of test case to return
        Returns:
            LLM's answer
        """
        return self.call(query, answer_cls, test_case_cls)

    @property
    def provider(self) -> LLMProvider:
        """LLM Provider to use for queries."""
        if self._provider is None:
            self._provider = get_default_provider()
        return self._provider

    @provider.setter
    def provider(self, value: LLMProvider):
        """Set LLM Provider to use for queries."""
        self._provider = value

    def call(
        self,
        query: Query,
        answer_cls: type[TAnswer],
        test_case_cls: type[TTestCase],
    ) -> TAnswer:
        """Query LLM synchronously.

        Arguments:
            query: query for LLM
            answer_cls: class of answer to return
            test_case_cls: class of test case to return
        Returns:
            LLM's answer
        """
        # Load from verified if available
        if answer := self._get_verified_answer(query):
            return answer

        # Load from cache if available
        system_prompt = self._get_system_prompt(answer_cls)
        if answer := self._get_cached_answer(system_prompt, query, test_case_cls):
            return answer

        # Query provider
        query_prompt = json.dumps(query.model_dump(), indent=4, ensure_ascii=False)
        answer: TAnswer | None = None
        test_case: TTestCase | None = None
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query_prompt},
        ]
        for attempt in range(1, self.max_attempts + 1):
            # Get answer from provider
            try:
                content = self.provider.chat_completion(messages, answer_cls)
            except ScinoephileError as exc:
                error(f"Attempt {attempt} failed: {type(exc).__name__}: {exc}")
                if attempt == self.max_attempts:
                    raise
                continue

            # Validate answer
            try:
                answer = answer_cls.model_validate_json(content)
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
                            f"{self.text.answer_invalid_pre}\n"
                            f"{'\n'.join([e['msg'] for e in exc.errors()])}\n"
                            f"{self.text.answer_invalid_post}"
                        ),
                    }
                )
                continue

            # Validate test case
            try:
                test_case = test_case_cls.from_query_and_answer(query, answer)
                if self.auto_verify and test_case.get_auto_verified():
                    test_case.verified = True
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
                            f"{self.text.test_case_invalid_pre}\n"
                            f"{'\n'.join([e['msg'] for e in exc.errors()])}\n"
                            f"{self.text.test_case_invalid_post}"
                        ),
                    }
                )
                continue
            break
        if answer is None or test_case is None:
            raise ScinoephileError("Unable to obtain valid answer")

        # Log encountered test case
        self.log_encountered_test_case(test_case)

        # Update cache
        if cache_path := self._get_cache_path(system_prompt, query_prompt):
            contents = json.dumps(test_case.model_dump(), ensure_ascii=False, indent=2)
            with open(cache_path, mode="w", encoding="utf-8") as f:
                f.write(contents)
            debug(f"Saved to cache: {cache_path}")

        return answer

    async def call_async(
        self,
        query: Query,
        answer_cls: type[TAnswer],
        test_case_cls: type[TTestCase],
    ) -> TAnswer:
        """Query LLM asynchronously.

        Arguments:
            query: query for LLM
            answer_cls: class of answer to return
            test_case_cls: class of test case to return
        Returns:
            LLM's answer
        """
        # Load from verified if available
        if answer := self._get_verified_answer(query):
            return answer

        # Load from cache if available
        system_prompt = self._get_system_prompt(answer_cls)
        if answer := await self._get_cached_answer_async(
            system_prompt, query, test_case_cls
        ):
            return answer

        # Query provider
        query_prompt = json.dumps(query.model_dump(), indent=4, ensure_ascii=False)
        answer: TAnswer | None = None
        test_case: TTestCase | None = None
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query_prompt},
        ]
        for attempt in range(1, self.max_attempts + 1):
            # Get answer from provider
            try:
                content = await self.provider.chat_completion_async(
                    messages, answer_cls
                )
            except ScinoephileError as exc:
                error(f"Attempt {attempt} failed: {type(exc).__name__}: {exc}")
                if attempt == self.max_attempts:
                    raise
                continue

            # Validate answer
            try:
                answer = answer_cls.model_validate_json(content)
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
                            f"{self.text.answer_invalid_pre}\n"
                            f"{'\n'.join([e['msg'] for e in exc.errors()])}\n"
                            f"{self.text.answer_invalid_post}"
                        ),
                    }
                )
                continue

            # Validate test case
            try:
                test_case = test_case_cls.from_query_and_answer(query, answer)
                if self.auto_verify and test_case.get_auto_verified():
                    test_case.verified = True
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
                            f"{self.text.test_case_invalid_pre}\n"
                            f"{'\n'.join([e['msg'] for e in exc.errors()])}\n"
                            f"{self.text.test_case_invalid_post}"
                        ),
                    }
                )
                continue
            break
        if answer is None or test_case is None:
            raise ScinoephileError("Unable to obtain valid answer")

        # Log encountered test case
        self.log_encountered_test_case(test_case)

        # Update cache
        if cache_path := self._get_cache_path(system_prompt, query_prompt):
            contents = json.dumps(test_case.model_dump(), ensure_ascii=False, indent=2)
            async with aiofiles.open(cache_path, mode="w", encoding="utf-8") as f:
                await f.write(contents)
            debug(f"Saved to cache: {cache_path}")

        return answer

    def get_encountered_test_cases_source_str(self) -> str:
        """String representation of all test cases in the log."""
        test_case_log_str = "[\n"
        for test_case in self.encountered_test_cases.values():
            source_str: str = test_case.source_str
            test_case_log_str += f"{source_str},\n"
        test_case_log_str += "]"
        return test_case_log_str

    def get_prompt_test_cases_few_shot_str(self) -> str:
        """String representation of all test cases in the log."""
        if not self.prompt_test_cases:
            return ""
        few_shot = f"\n\n{self.text.few_shot_intro}"
        for test_case in self.prompt_test_cases.values():
            few_shot += f"\n\n{self.text.few_shot_query_intro}\n"
            few_shot += json.dumps(
                test_case.query.model_dump(), indent=4, ensure_ascii=False
            )
            few_shot += f"\n{self.text.few_shot_answer_intro}\n"
            few_shot += json.dumps(
                test_case.answer.model_dump(), indent=4, ensure_ascii=False
            )
        return few_shot

    def log_encountered_test_case(self, test_case: TTestCase):
        """Log a test case as having been encountered.

        Arguments:
            test_case: test case to log
        """
        key = test_case.query.key
        test_case.prompt = key in self.prompt_test_cases
        test_case.verified = key in self.verified_test_cases
        self.encountered_test_cases[key] = test_case
        debug(f"Logged test case: {test_case.query.key_str}")

    @cache
    def _get_cache_path(self, system_prompt: str, query_prompt: str) -> Path | None:
        """Get cache path based on hash of prompts.

        Arguments:
            system_prompt: system prompt used for the query
            query_prompt: query prompt used for the query
        Returns:
            Path to cache file
        """
        if self.cache_dir_path is None:
            return None

        prompt_str = system_prompt + query_prompt
        sha256 = hashlib.sha256(prompt_str.encode("utf-8")).hexdigest()
        return self.cache_dir_path / f"{sha256}.json"

    def _get_cached_answer(
        self, system_prompt: str, query: Query, test_case_cls: type[TTestCase]
    ) -> TAnswer | None:
        """Get cached answer for the given query if available.

        Arguments:
            system_prompt: system prompt used for the query
            query: query for which to get cached answer
            test_case_cls: class of test case
        Returns:
            cached answer if available, else None
        """
        query_prompt = json.dumps(query.model_dump(), indent=4, ensure_ascii=False)
        cache_path = self._get_cache_path(system_prompt, query_prompt)
        if cache_path is None:
            return None
        if not cache_path.exists():
            return None
        with open(cache_path, encoding="utf-8") as f:
            contents = f.read()
        try:
            test_case = test_case_cls.model_validate(json.loads(contents))
            if self.auto_verify and test_case.get_auto_verified():
                test_case.verified = True
            self.log_encountered_test_case(test_case)
            info(f"Loaded from cache: {query.key_str}")
            cache_path.touch()
            return test_case.answer
        except ValidationError as exc:
            error(f"Cache content for query {query.key_str} is invalid: {exc}")
            cache_path.unlink()
            info(f"Deleted invalid cache file: {cache_path}")
        return None

    async def _get_cached_answer_async(
        self, system_prompt: str, query: Query, test_case_cls: type[TTestCase]
    ) -> TAnswer | None:
        """Get cached answer for the given query if available.

        Arguments:
            system_prompt: system prompt used for the query
            query: query for which to get cached answer
            test_case_cls: class of test case
        Returns:
            cached answer if available, else None
        """
        query_prompt = json.dumps(query.model_dump(), indent=4, ensure_ascii=False)
        cache_path = self._get_cache_path(system_prompt, query_prompt)
        if cache_path is None:
            return None
        if not cache_path.exists():
            return None
        async with aiofiles.open(cache_path, encoding="utf-8") as f:
            contents = await f.read()
        try:
            test_case = test_case_cls.model_validate(json.loads(contents))
            if self.auto_verify and test_case.get_auto_verified():
                test_case.verified = True
            self.log_encountered_test_case(test_case)
            info(f"Loaded from cache: {query.key_str}")
            await asyncio.to_thread(cache_path.touch)
            return test_case.answer
        except ValidationError as exc:
            error(f"Cache content for query {query.key_str} is invalid: {exc}")
            await aioos.remove(cache_path)
            info(f"Deleted invalid cache file: {cache_path}")
        return None

    def _get_system_prompt(self, answer_cls: type[TAnswer]) -> str:
        """Get system prompt for the given answer class.

        Arguments:
            answer_cls: class of answer
        Returns:
            system prompt for the given answer class
        """
        schema = answer_cls.model_json_schema()
        schema_json = json.dumps(schema, indent=4, ensure_ascii=False)

        system_prompt = self.text.base_system_prompt
        system_prompt += self.get_prompt_test_cases_few_shot_str()
        system_prompt += f"\n\n{self.text.schema_intro}\n{schema_json}\n"

        return system_prompt

    def _get_verified_answer(self, query: Query) -> TAnswer | None:
        """Get verified answer for the given query if available.

        Arguments:
            query: query for which to get verified answer
        Returns:
            verified answer if available, else None
        """
        if test_case := self.verified_test_cases.get(query.key):
            answer = test_case.answer
            self.log_encountered_test_case(test_case)
            info(f"Loaded from verified log: {query.key_str}")
            return answer
        return None
