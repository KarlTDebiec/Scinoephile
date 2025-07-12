#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Merges transcribed 粤文 text to match 中文 text punctuation and spacing."""

from __future__ import annotations

import hashlib
import json
from logging import error, info
from pathlib import Path
from textwrap import dedent

from openai import OpenAI
from pydantic import ValidationError

from scinoephile.audio.models import MergeAnswer, MergeQuery
from scinoephile.audio.testing import MergeTestCase
from scinoephile.common.validation import validate_output_directory


class CantoneseMerger:
    """Merges transcribed 粤文 texts to match 中文 text punctuation and spacing."""

    system_prompt_template = """
        You are a helpful assistant that merges multi-line 粤文 subtitles of
        spoken Cantonese to match the spacing and punctuation of a single-line
        中文 subtitle. Include all 粤文 characters and merge them into one line.
        All 汉字 in the output must come from the 粤文 input. No 汉字 in the
        output may come from the 中文 input. Adjust punctuation and spacing to
        match the 中文 input.
    """
    query_template = "中文:\n{zhongwen}\n粤文 to merge:\n{yuewen_to_merge}\n"
    answer_template = "粤文 merged:\n{yuewen_merged}\n"
    answer_example = MergeAnswer(yuewen_merged="粤文 merged")

    def __init__(
        self,
        model: str = "gpt-4.1",
        examples: list[MergeTestCase] = None,
        print_test_case: bool = False,
        cache_dir_path: str | None = None,
    ):
        """Initialize.

        Arguments:
            model: OpenAI model to use.
            examples: Examples of inputs and expected outputs for few-shot learning
            print_test_case: Print test case after merging
            cache_dir_path: Path to cache directory for OpenAI API responses
        """
        self.client = OpenAI()
        self.model = model
        self.print_test_case = print_test_case

        # Set up system prompt, with examples if provided
        self.system_prompt = (
            dedent(self.system_prompt_template).strip().replace("\n", " ")
        )
        self.system_prompt += "\n"
        self.system_prompt += json.dumps(self.answer_example.model_dump(), indent=4)
        if examples:
            self.system_prompt += (
                "\n\nHere are some examples of inputs and expected outputs:\n"
            )
            for example in examples:
                self.system_prompt += self.query_template.format_map(
                    example.query.model_dump()
                )
                self.system_prompt += self.answer_template.format_map(
                    example.answer.model_dump()
                )

        # Set up cache directory
        self.cache_dir_path = None
        if cache_dir_path is not None:
            self.cache_dir_path = validate_output_directory(cache_dir_path)

    def __call__(self, query: MergeQuery) -> MergeAnswer:
        """Merge 粤文 text to match 中文 text punctuation and spacing.

        Arguments:
            query: query containing 中文 text and 粤文 texts to merge
        Returns:
            Answer including merged 粤文 text
        """
        return self.merge(query)

    def merge(self, query: MergeQuery) -> MergeAnswer:
        """Merge 粤文 text to match 中文 text punctuation and spacing.

        Arguments:
            query: Query containing 中文 text and 粤文 texts to merge
        Returns:
            Answer including merged 粤文 text
        """
        query_prompt = self.query_template.format(
            zhongwen=query.zhongwen, yuewen_to_merge="\n".join(query.yuewen_to_merge)
        )
        cache_path = self._get_cache_path(query_prompt)

        # Load from cache if available
        if cache_path is not None and cache_path.exists():
            info(f"Loaded from cache: {cache_path}")
            with cache_path.open("r", encoding="utf-8") as f:
                answer = MergeAnswer.model_validate(json.load(f))
                if self.print_test_case:
                    test_case = MergeTestCase.from_query_and_answer(query, answer)
                    print(test_case.to_source())
                return answer

        # Process using OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": query_prompt},
            ],
            temperature=0,
            seed=0,
        )
        message = response.choices[0].message
        content = message.content

        # Validate the response
        try:
            answer = MergeAnswer.model_validate_json(content)
        except ValidationError as exc:
            error(f"Query:\n{query}\nYielded invalid content:\n{content}")
            raise exc
            # TODO: Try again if response is not valid
        try:
            test_case = MergeTestCase.from_query_and_answer(query, answer)
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
