#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for LLM queryers."""

from __future__ import annotations

import hashlib
import json
from abc import ABC
from functools import cache
from json import JSONDecodeError
from logging import debug, error, info, warning
from pathlib import Path
from typing import ClassVar, Self, cast

from pydantic import ValidationError

from scinoephile.common.validation import val_output_dir_path
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.open_ai import OpenAIProvider

from .answer import Answer
from .llm_provider import LLMProvider
from .prompt import Prompt
from .query import Query
from .test_case import TestCase

__all__ = ["Queryer"]


class Queryer[
    TQuery: Query,
    TAnswer: Answer,
    TTestCase: TestCase,
    TPrompt: Prompt,
](ABC):
    """ABC for LLM queryers."""

    prompt_cls: ClassVar[type[Prompt]]
    """Text for LLM correspondence."""

    def __init__(
        self,
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
            prompt_test_cases: test cases included in the prompt for few-shot learning
            verified_test_cases: test cases whose answers are verified and for which
              LLM need not be queried
            provider: provider to use for queries
            cache_dir_path: directory in which to cache
            max_attempts: maximum number of attempts
            auto_verify: automatically mark test cases as verified if no changes
        """
        self._provider = provider

        self.prompt_test_cases = {tc.query.key: tc for tc in prompt_test_cases or []}
        """Test cases included in the prompt for few-shot learning."""
        self.verified_test_cases = {
            tc.query.key: tc for tc in verified_test_cases or []
        }
        """Test cases whose answers are verified for which LLM will not be queried."""
        self.encountered_test_cases: dict[tuple, TTestCase] = {}
        """Test cases actually encountered."""

        self.cache_dir_path = None
        """Directory in which to cache query results."""
        if cache_dir_path is not None:
            self.cache_dir_path = val_output_dir_path(cache_dir_path)

        self.max_attempts = max_attempts
        """Maximum number of query attempts."""
        self.auto_verify = auto_verify
        """Automatically verify test cases if they meet selected criteria."""

    def __call__(self, test_case: TTestCase) -> TTestCase:
        """Query LLM.

        Arguments:
            test_case: test case containing query for LLM
        Returns:
            test case including LLM's answer
        """
        return self.call(test_case)

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

    def call(self, test_case: TTestCase) -> TTestCase:
        """Query LLM synchronously.

        Arguments:
            test_case: test case containing query for LLM
        Returns:
            test case including LLM's answer
        """
        # Load from verified if available
        if verified_test_case := self._get_verified_test_case(test_case.query):
            return verified_test_case

        # Load from cache if available
        system_prompt = self._get_system_prompt(test_case.answer_cls)
        if cached_test_case := self._get_cached_test_case(system_prompt, test_case):
            return cached_test_case

        # Query provider
        query_prompt = json.dumps(
            test_case.query.model_dump(), indent=4, ensure_ascii=False
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query_prompt},
        ]
        for attempt in range(1, self.max_attempts + 1):
            # Get answer from provider
            try:
                content = self.provider.chat_completion(messages, test_case.answer_cls)
            except ScinoephileError as exc:
                error(f"Attempt {attempt} failed: {type(exc).__name__}: {exc}")
                if attempt == self.max_attempts:
                    raise
                continue

            # Validate answer
            try:
                answer = test_case.answer_cls.model_validate_json(content)
            except ValidationError as exc:
                error(
                    f"Query:\n{test_case.query}\n"
                    f"Yielded invalid content (attempt {attempt}):\n{content}"
                )
                if attempt == self.max_attempts:
                    raise exc
                messages.append({"role": "assistant", "content": content})
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            f"{self.prompt_cls.answer_invalid_pre}\n"
                            f"{'\n'.join([e['msg'] for e in exc.errors()])}\n"
                            f"{self.prompt_cls.answer_invalid_post}"
                        ),
                    }
                )
                continue

            # Validate test case
            try:
                test_case = type(test_case).model_validate(
                    {**test_case.model_dump(), "answer": answer}
                )
                if self.auto_verify and test_case.get_auto_verified():
                    test_case.verified = True
            except ValidationError as exc:
                error(
                    f"Query:\n{test_case.query}\n"
                    f"Yielded invalid answer (attempt {attempt}):\n{answer}"
                )
                if attempt == self.max_attempts:
                    raise exc
                messages.append({"role": "assistant", "content": content})
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            f"{self.prompt_cls.test_case_invalid_pre}\n"
                            f"{'\n'.join([e['msg'] for e in exc.errors()])}\n"
                            f"{self.prompt_cls.test_case_invalid_post}"
                        ),
                    }
                )
                continue
            break
        if test_case.answer is None:
            raise ScinoephileError("Unable to obtain valid answer")

        # Log encountered test case
        self.log_encountered_test_case(test_case)

        # Update cache
        if cache_path := self._get_cache_path(system_prompt, query_prompt):
            contents = json.dumps(
                test_case.model_dump(exclude_defaults=True),
                ensure_ascii=False,
                indent=2,
            )
            with open(cache_path, mode="w", encoding="utf-8") as f:
                f.write(contents)
            debug(f"Saved to cache: {cache_path}")

        return test_case

    def get_prompt_test_cases_few_shot_str(self) -> str:
        """String representation of all test cases in the log."""
        if not self.prompt_test_cases:
            return ""
        few_shot = f"\n\n{self.prompt_cls.few_shot_intro}"
        for test_case in self.prompt_test_cases.values():
            if test_case.answer is None:
                warning(
                    f"Prompt test case {test_case.query.key_str} has no answer; "
                    "skipping."
                )
                continue
            few_shot += f"\n\n{self.prompt_cls.few_shot_query_intro}\n"
            few_shot += json.dumps(
                test_case.query.model_dump(), indent=4, ensure_ascii=False
            )
            few_shot += f"\n{self.prompt_cls.few_shot_answer_intro}\n"
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

    def _get_cached_test_case(
        self,
        system_prompt: str,
        test_case: TTestCase,
    ) -> TTestCase | None:
        """Get cached test case for the given query if available.

        Arguments:
            system_prompt: system prompt used for the query
            test_case: test case containing query for which to get cached version
        Returns:
            cached test case if available, else None
        """
        query_prompt = json.dumps(
            test_case.query.model_dump(), indent=4, ensure_ascii=False
        )
        cache_path = self._get_cache_path(system_prompt, query_prompt)
        if cache_path is None:
            return None
        if not cache_path.exists():
            return None
        with open(cache_path, encoding="utf-8") as f:
            contents = f.read()
        try:
            content = json.loads(contents)
            test_case = type(test_case).model_validate(content)
            if self.auto_verify and test_case.get_auto_verified():
                test_case.verified = True
            self.log_encountered_test_case(test_case)
            info(f"Loaded from cache: {test_case.query.key_str}")
            cache_path.touch()
            return test_case
        except (AttributeError, JSONDecodeError, ValidationError) as exc:
            error(
                f"Cache content for query {test_case.query.key_str} is invalid: {exc}"
            )
            cache_path.unlink()
            info(f"Deleted invalid cache file: {cache_path}")
        return None

    def _get_system_prompt(self, answer_cls: type[Answer]) -> str:
        """Get system prompt for the given answer class.

        Arguments:
            answer_cls: class of answer
        Returns:
            system prompt for the given answer class
        """
        schema = answer_cls.model_json_schema()
        schema_json = json.dumps(schema, indent=4, ensure_ascii=False)

        system_prompt = self.prompt_cls.base_system_prompt
        system_prompt += self.get_prompt_test_cases_few_shot_str()
        system_prompt += f"\n\n{self.prompt_cls.schema_intro}\n{schema_json}\n"

        return system_prompt

    def _get_verified_test_case(self, query: TQuery) -> TTestCase | None:
        """Get verified test case for the given query if available.

        Arguments:
            query: query for which to get verified test case
        Returns:
            verified test case if available, else None
        """
        if test_case := self.verified_test_cases.get(query.key):
            self.log_encountered_test_case(test_case)
            info(f"Loaded from verified log: {query.key_str}")
            return test_case
        return None

    @classmethod
    @cache
    def get_queryer_cls(cls, prompt_cls: type[Prompt]) -> type[Self]:
        """Get concrete queryer class with provided text.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            LLMQueryer type with appropriate text
        """
        name = f"{cls.__name__}_{prompt_cls.__name__}"
        attrs = {
            "__module__": cls.__module__,
            "prompt_cls": prompt_cls,
        }
        queryer_cls = type(name, (cls,), attrs)
        return cast(type[Self], queryer_cls)
