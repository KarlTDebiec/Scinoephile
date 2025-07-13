#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for LLM queryers."""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from logging import error, info
from pathlib import Path
from textwrap import dedent

from pydantic import ValidationError

from scinoephile.common.validation import validate_output_directory
from scinoephile.core.abcs.answer import Answer
from scinoephile.core.abcs.llm_provider import LLMProvider
from scinoephile.openai.openai_provider import OpenAIProvider
from scinoephile.core.abcs.query import Query
from scinoephile.core.abcs.test_case import TestCase


class LLMQueryer[TQuery: Query, TAnswer: Answer, TTestCase: TestCase](ABC):
    """Abstract base class for LLM queryers."""

    def __init__(
        self,
        model: str = "gpt-4.1",
        examples: list[TTestCase] | None = None,
        print_test_case: bool = False,
        cache_dir_path: str | None = None,
        provider: LLMProvider | None = None,
    ):
        """Initialize.

        Arguments:
            model: Model to use
            examples: Examples of inputs and expected outputs for few-shot learning
            print_test_case: Whether to print test case after merging
            cache_dir_path: Directory in which to cache
            provider: Provider to use for queries, defaults to ``OpenAIProvider``
        """
        self.provider = provider or OpenAIProvider()
        self.model = model
        self.print_test_case = print_test_case

        # Set up system prompt, with examples if provided
        system_prompt = dedent(self.base_system_prompt).strip().replace("\n", " ")
        system_prompt += "\n"
        system_prompt += json.dumps(self.answer_example.model_dump(), indent=4)
        if examples:
            system_prompt += (
                "\n\nHere are some examples of inputs and expected outputs:\n"
            )
            for example in examples:
                system_prompt += self.query_template.format_map(
                    example.query.model_dump()
                )
                system_prompt += self.answer_template.format_map(
                    example.answer.model_dump()
                )
        self._system_prompt = system_prompt

        # Set up cache directory
        self.cache_dir_path = None
        if cache_dir_path is not None:
            self.cache_dir_path = validate_output_directory(cache_dir_path)

    def __call__(self, query: TQuery) -> TAnswer:
        """Query LLM.

        Arguments:
            query: query for LLM
        Returns:
            LLM's answer
        """
        query_prompt = self._format_query_prompt(query)
        cache_path = self._get_cache_path(query_prompt)

        # Load from cache if available
        if cache_path is not None and cache_path.exists():
            info(f"Loaded from cache: {cache_path}")
            with cache_path.open("r", encoding="utf-8") as f:
                answer = self.answer_cls.model_validate(json.load(f))
                if self.print_test_case:
                    test_case = self.test_case_cls.from_query_and_answer(query, answer)
                    print(test_case.to_source())
                return answer

        # Query provider
        content = self.provider.chat_completion(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": query_prompt},
            ],
            temperature=0,
            seed=0,
            response_format=self.answer_cls,
        )

        # Validate answer
        try:
            answer = self.answer_cls.model_validate_json(content)
        except ValidationError as exc:
            error(f"Query:\n{query}\nYielded invalid content:\n{content}")
            raise exc
            # TODO: Try again if response is not valid
        try:
            test_case = self.test_case_cls.from_query_and_answer(query, answer)
        except ValidationError as exc:
            error(f"Query:\n{query}\nYielded invalid answer:\n{answer}")
            raise exc
            # TODO: Try again if response is not valid
        if self.print_test_case:
            print(test_case.to_source())

        # Update cache
        if cache_path is not None:
            with cache_path.open("w", encoding="utf-8") as f:
                json.dump(answer.model_dump(), f, ensure_ascii=False, indent=2)
                info(f"Saved split to cache: {cache_path}")

        return answer

    @property
    @abstractmethod
    def answer_example(self) -> TAnswer:
        """Example answer."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def answer_cls(self) -> type[TAnswer]:
        """Answer class."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def answer_template(self) -> str:
        """Answer template."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def query_cls(self) -> type[TQuery]:
        """Query class."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def query_template(self) -> str:
        """Query template."""
        raise NotImplementedError()

    @property
    def system_prompt(self) -> str:
        """System prompt template."""
        return self._system_prompt

    @property
    @abstractmethod
    def test_case_cls(self) -> type[TTestCase]:
        """Test case class."""
        raise NotImplementedError()

    def _format_query_prompt(self, query: TQuery) -> str:
        """Format query prompt based on query.

        Arguments:
            query: Query to format
        Returns:
            Formatted query prompt
        """
        return self.query_template.format_map(query.model_dump())

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
