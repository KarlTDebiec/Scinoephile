#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Translates 粤文 text based on corresponding 中文."""

from __future__ import annotations

import hashlib
import json
from doctest import debug
from logging import error
from pathlib import Path
from textwrap import dedent

from openai import BaseModel
from pydantic import ValidationError

from scinoephile.audio.cantonese.shifting.shift_answer import ShiftAnswer
from scinoephile.common.validation import val_output_dir_path
from scinoephile.core import ScinoephileError
from scinoephile.core.abcs import LLMProvider
from scinoephile.openai import OpenAIProvider


class Translator:
    """Translates 粤文 text based on corresponding 中文."""

    def __init__(
        self,
        model: str,
        examples: list[BaseModel] | None = None,
        print_test_case: bool = False,
        cache_dir_path: str | None = None,
        provider: LLMProvider | None = None,
        max_attempts: int = 2,
    ):
        """Initialize.

        Arguments:
            model: Model to use
            examples: Examples of inputs and expected outputs for few-shot learning
            print_test_case: Whether to print test case after merging
            cache_dir_path: Directory in which to cache
            provider: Provider to use for queries
            max_attempts: Maximum number of attempts
        """
        self.provider = provider or OpenAIProvider()
        """LLM Provider to use for queries."""
        self.model = model
        """Model name to use for queries."""
        self.print_test_case = print_test_case
        """Whether to print test case after merging query and answer."""
        self.max_attempts = max_attempts
        """Maximum number of query attempts."""

        self._examples_log: dict[tuple, BaseModel] = {}
        """Log of examples, keyed by query key."""
        self._test_case_log: dict[tuple, BaseModel] = {}
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

        # Set up cache directory
        self.cache_dir_path = None
        """Directory in which to cache query results."""
        if cache_dir_path is not None:
            self.cache_dir_path = val_output_dir_path(cache_dir_path)

    def __call__(self, query: BaseModel) -> BaseModel:
        """Query LLM.

        Arguments:
            query: Query for LLM
        Returns:
            LLM's answer
        """
        query_prompt = json.dumps(query.model_dump(), indent=4, ensure_ascii=False)
        cache_path = self._get_cache_path(query_prompt)

        # Load from cache if available
        if cache_path is not None and cache_path.exists():
            debug(f"Loaded from cache: {cache_path}")
            with cache_path.open("r", encoding="utf-8") as f:
                answer = self.answer_cls.model_validate(json.load(f))
                if self.print_test_case:
                    test_case = self.test_case_cls.from_query_and_answer(query, answer)
                    self._test_case_log[test_case.query.query_key] = test_case
                    print(f"{test_case.source_str},")
                return answer

        # Query provider
        answer: BaseModel | None = None
        test_case: BaseModel | None = None
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
        self._test_case_log[test_case.query.query_key] = test_case
        if self.print_test_case:
            print(f"{test_case.source_str},")

        # Update cache
        if cache_path is not None:
            with cache_path.open("w", encoding="utf-8") as f:
                json.dump(answer.model_dump(), f, ensure_ascii=False, indent=2)
                debug(f"Saved to cache: {cache_path}")

        return answer

    @property
    def system_prompt(self) -> str:
        """System prompt template."""
        return self._system_prompt

    @property
    def test_case_log(self) -> dict[tuple, BaseModel]:
        """Log of test cases, keyed by query key."""
        return self._test_case_log

    @property
    def test_case_log_str(self) -> str:
        """String representation of all test cases in the log."""
        test_case_log_str = "[\n"
        for key, value in self._test_case_log.items():
            source_str: str = value.source_str
            if key in self._examples_log:
                source_str = f"{source_str[:-1]}    include_in_prompt=True,\n)"
            test_case_log_str += f"{source_str},\n"
        test_case_log_str += "\n]"
        return test_case_log_str

    def answer_example(self) -> ShiftAnswer:
        """Example answer."""
        return ShiftAnswer(
            one_yuewen_shifted="粤文 one shifted",
            two_yuewen_shifted="粤文 two shifted",
        )

    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return (
            "Read the two consecutive 中文 texts and two consecutive 粤文 texts, and adjust "
            "the breakpoint between the first and second 粤文 texts so that they align with "
            "the two corresponding 中文 texts. "
            "This is, either shift characters from the end of the first 粤文 text to the "
            "beginning of the second 粤文 text, or shift characters from the beginning of "
            "the second 粤文 text to the end of the first 粤文 text. "
            "If no changes are needed, return the original 粤文 texts. "
            "Include all 粤文 characters from the inputs in the same order in the outputs. "
            "Do not copy punctuation or whitespace from the 中文 texts."
        )

    def clear_test_case_log(self):
        """Clear the test case log."""
        self._test_case_log.clear()

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
