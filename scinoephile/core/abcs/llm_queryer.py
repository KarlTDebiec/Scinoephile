#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for LLM queryers."""

from __future__ import annotations

import asyncio
import hashlib
import json
from abc import ABC, abstractmethod
from logging import debug, error, info
from pathlib import Path
from typing import ClassVar

import aiofiles
from aiofiles import os as aioos
from pydantic import ValidationError

from scinoephile.common.validation import val_output_dir_path
from scinoephile.core import ScinoephileError
from scinoephile.core.abcs.answer import Answer
from scinoephile.core.abcs.llm_provider import LLMProvider
from scinoephile.core.abcs.llm_text import LLMText
from scinoephile.core.abcs.query import Query
from scinoephile.core.abcs.test_case import TestCase
from scinoephile.openai import OpenAIProvider


class LLMQueryer[TQuery: Query, TAnswer: Answer, TTestCase: TestCase](ABC):
    """Abstract base class for LLM queryers."""

    text: ClassVar[type[LLMText]]
    """Text strings to be used for corresponding with LLM."""

    def __init__(
        self,
        model: str = "gpt-5.1",
        prompt_test_cases: list[TTestCase] | None = None,
        verified_test_cases: list[TTestCase] | None = None,
        provider: LLMProvider | None = None,
        *,
        cache_dir_path: str | None = None,
        max_attempts: int = 5,
        auto_verify: bool = False,
    ):
        """Initialize.

        Arguments:
            model: model to use
            prompt_test_cases: test cases included in the prompt for few-shot learning
            verified_test_cases: test cases whose answers are verified and for which
              LLM need not be queried
            provider: provider to use for queries
            cache_dir_path: directory in which to cache
            max_attempts: maximum number of attempts
            auto_verify: automatically mark test cases as verified if no changes
        """
        self.model = model
        """Model name to use for queries."""
        self._provider = provider

        # Track which test cases are to be included in the prompt for few-shot learning
        self._prompt_test_cases: dict[tuple, TTestCase] = {}
        """Test cases included in the prompt for few-shot learning."""
        if prompt_test_cases is not None:
            for test_case in prompt_test_cases:
                self._prompt_test_cases[test_case.query.query_key] = test_case

        # Track which test cases are verified
        self._verified_test_cases: dict[tuple, TTestCase] = {}
        """Test cases whose answers are verified for which LLM will not be queried."""
        if verified_test_cases is not None:
            for test_case in verified_test_cases:
                self._verified_test_cases[test_case.query.query_key] = test_case

        # Track which test cases are actually encountered
        self._encountered_test_cases: dict[tuple, TTestCase] = {}
        """Test cases actually encountered."""

        # Set up cache directory
        self.cache_dir_path = None
        """Directory in which to cache query results."""
        if cache_dir_path is not None:
            self.cache_dir_path = val_output_dir_path(cache_dir_path)

        self.max_attempts = max_attempts
        """Maximum number of query attempts."""
        self.auto_verify = auto_verify
        """Automatically verify test cases if they meet selected criteria."""

    @property
    def provider(self):
        """LLM Provider to use for queries."""
        if self._provider is None:
            self._provider = OpenAIProvider()
        return self._provider

    @provider.setter
    def provider(self, value: LLMProvider):
        """Set LLM Provider to use for queries."""
        self._provider = value

    @property
    def encountered_test_cases(self) -> dict[tuple, TTestCase]:
        """Test cases actually encountered."""
        return self._encountered_test_cases

    @property
    @abstractmethod
    def encountered_test_cases_source_str(self) -> str:
        """String representation of all test cases in the log."""
        raise NotImplementedError()

    @property
    def prompt_test_cases(self) -> dict[tuple, TTestCase]:
        """Test cases included in the prompt for few-shot learning."""
        return self._prompt_test_cases

    @property
    def prompt_test_cases_few_shot_str(self) -> str:
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

    @property
    def verified_test_cases(self) -> dict[tuple, TTestCase]:
        """Test cases whose answers are verified for which LLM will not be queried."""
        return self._verified_test_cases

    def clear_encountered_test_cases(self):
        """Clear the test case log."""
        self._encountered_test_cases.clear()

    def log_encountered_test_case(self, test_case: TTestCase):
        """Log a test case as having been encountered.

        Arguments:
            test_case: test case to log
        """
        key = test_case.query.query_key
        test_case.prompt = key in self._prompt_test_cases
        test_case.verified = key in self._verified_test_cases
        self._encountered_test_cases[key] = test_case
        debug(f"Logged test case: {test_case.query.query_key_str}")

    async def _call(
        self,
        system_prompt: str,
        query: Query,
        answer_cls: type[TAnswer],
        test_case_cls: type[TTestCase],
    ) -> TAnswer:
        # Load from verified log if available
        if query.query_key in self._verified_test_cases:
            test_case = self._verified_test_cases[query.query_key]
            answer = test_case.answer
            self.log_encountered_test_case(test_case)
            info(f"Loaded from verified log: {query.query_key_str}")
            return answer

        query_prompt = json.dumps(query.model_dump(), indent=4, ensure_ascii=False)

        # Load from cache if available
        cache_path = self._get_cache_path(system_prompt, query_prompt)
        if cache_path is not None and cache_path.exists():
            try:
                async with aiofiles.open(cache_path, encoding="utf-8") as f:
                    contents = await f.read()
                try:
                    test_case = test_case_cls.model_validate(json.loads(contents))
                    if self.auto_verify and test_case.get_auto_verified():
                        test_case.verified = True
                    self.log_encountered_test_case(test_case)
                    info(f"Loaded from cache: {query.query_key_str}")
                    await asyncio.to_thread(cache_path.touch)
                    return test_case.answer
                except ValidationError as exc:
                    error(
                        f"Cache content for query {query.query_key_str} is invalid: "
                        f"{exc}"
                    )
                    await aioos.remove(cache_path)
                    info(f"Deleted invalid cache file: {cache_path}")
            except FileNotFoundError:
                pass

        # Query provider
        answer: TAnswer | None = None
        test_case: TTestCase | None = None
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query_prompt},
        ]
        for attempt in range(1, self.max_attempts + 1):
            # Get answer from provider
            try:
                content = await self.provider.achat_completion(
                    model=self.model,
                    messages=messages,
                    temperature=0,
                    seed=0,
                    response_format=answer_cls,
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
        if cache_path is not None:
            contents = json.dumps(test_case.model_dump(), ensure_ascii=False, indent=2)
            async with aiofiles.open(cache_path, mode="w", encoding="utf-8") as f:
                await f.write(contents)
            debug(f"Saved to cache: {cache_path}")

        return answer

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

    def _get_system_prompt(self, answer_example: TAnswer) -> str:
        """Get system prompt for the given answer class.

        Arguments:
            answer_example: class of answer to return
        Returns:
            System prompt for the given answer class
        """
        system_prompt = self.text.base_system_prompt
        system_prompt += self.prompt_test_cases_few_shot_str
        system_prompt += f"\n\n{self.text.schema_intro}\n"
        system_prompt += json.dumps(
            answer_example.model_dump(), indent=4, ensure_ascii=False
        )
        return system_prompt
