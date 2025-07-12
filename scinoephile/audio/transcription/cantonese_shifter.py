# Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
# and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shifts 粤文 text between adjacent subtitles based on 中文."""

from __future__ import annotations

import hashlib
import json
from logging import error, info
from pathlib import Path
from textwrap import dedent

from openai import OpenAI
from pydantic import ValidationError

from scinoephile.audio.models import ShiftAnswer, ShiftQuery
from scinoephile.audio.testing import ShiftTestCase
from scinoephile.common.validation import validate_output_directory


class CantoneseShifter:
    """Shifts 粤文 text between adjacent subtitles based on 中文."""

    system_prompt_template = """
        You are a helpful assistant that shifts the start of the second 粤文
        subtitle so that two 粤文 subtitles align with their corresponding 中文
        subtitles. Include all 粤文 characters from the inputs. Do not add or
        remove characters. Your output must be a JSON object with the following
        structure:
    """
    query_template = (
        "中文 one:\n{one_zhongwen}\n"
        "粤文 one original:\n{one_yuewen}\n"
        "中文 two:\n{two_zhongwen}\n"
        "粤文 two original:\n{two_yuewen}\n"
    )
    answer_template = (
        "粤文 one shifted:\n{one_yuewen_shifted}\n"
        "粤文 two shifted:\n{two_yuewen_shifted}\n"
    )
    answer_example = ShiftAnswer(
        one_yuewen_shifted="粤文 one shifted",
        two_yuewen_shifted="粤文 two shifted",
    )

    def __init__(
        self,
        model: str = "gpt-4.1",
        examples: list[ShiftTestCase] | None = None,
        print_test_case: bool = False,
        cache_dir_path: str | None = None,
    ) -> None:
        """Initialize."""
        self.client = OpenAI()
        self.model = model
        self.print_test_case = print_test_case

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

        self.cache_dir_path = None
        if cache_dir_path is not None:
            self.cache_dir_path = validate_output_directory(cache_dir_path)

    def __call__(self, query: ShiftQuery) -> ShiftAnswer:
        """Shift 粤文 text between adjacent subtitles based on 中文."""
        return self.shift(query)

    def shift(self, query: ShiftQuery) -> ShiftAnswer:
        """Shift 粤文 text between adjacent subtitles based on 中文."""
        query_prompt = self.query_template.format_map(query.model_dump())
        cache_path = self._get_cache_path(query_prompt)

        if cache_path is not None and cache_path.exists():
            info(f"Loaded from cache: {cache_path}")
            with cache_path.open("r", encoding="utf-8") as f:
                answer = ShiftAnswer.model_validate(json.load(f))
                if self.print_test_case:
                    test_case = ShiftTestCase.from_query_and_answer(query, answer)
                    print(test_case.to_source())
                return answer

        response = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": query_prompt},
            ],
            temperature=0,
            seed=0,
            response_format=ShiftAnswer,
        )
        message = response.choices[0].message
        content = message.content

        try:
            answer = ShiftAnswer.model_validate_json(content)
        except ValidationError as exc:
            error(f"Query:\n{query}\nYielded invalid content:\n{content}")
            raise exc
        try:
            test_case = ShiftTestCase.from_query_and_answer(query, answer)
        except ValidationError as exc:
            error(f"Query:\n{query}\nYielded invalid answer:\n{answer}")
            raise exc
        if self.print_test_case:
            print(test_case.to_source())

        if cache_path is not None:
            with cache_path.open("w", encoding="utf-8") as f:
                json.dump(answer.model_dump(), f, ensure_ascii=False, indent=2)
                info(f"Saved shift to cache: {cache_path}")

        return answer

    def _get_cache_path(self, query_prompt: str) -> Path | None:
        """Get cache path based on hash of prompts."""
        if self.cache_dir_path is None:
            return None
        prompt_str = self.system_prompt + query_prompt
        sha256 = hashlib.sha256(prompt_str.encode("utf-8")).hexdigest()
        return self.cache_dir_path / f"{sha256}.json"
