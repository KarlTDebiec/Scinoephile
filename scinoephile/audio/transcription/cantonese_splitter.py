#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Splits 粤文 text between two nascent 粤文 texts based on corresponding 中文."""

from __future__ import annotations

import json
from logging import error
from textwrap import dedent

from openai import OpenAI
from pydantic import ValidationError

from scinoephile.audio.models import SplitAnswer, SplitQuery
from scinoephile.audio.testing import SplitTestCase


class CantoneseSplitter:
    """Splits 粤文 text between two nascent 粤文 texts based on corresponding 中文."""

    system_prompt_template = """
        You are a helpful assistant that matches 粤文 subtitles of spoken Cantonese
        to 中文 subtitles of the same spoken content. You will be given a 中文
        subtitle and its nascent 粤文 subtitle, and a second 中文 subtitle with its
        nascent 粤文 subtitle. You will be given and additional 粤文 text whose
        distribution between the two subtitles is ambiguous, and you will determine
        how the 粤文 text should be distributed between the two nascent 粤文
        subtitles.
        Include all characters "ambiguous 粤文" in either "one" or "two".
        Do not copy "Nascent 粤文 one" into "one", nor "Nascent 粤文 two" into "two".
        Your output "one" and "two" concatenated should equal "ambiguous 粤文".
        Your response must be a JSON object with the following structure:
    """
    query_template = (
        "中文 one:\n{one_zhongwen}\n"
        "粤文 one start:\n{one_yuewen_start}\n"
        "中文 two:\n{two_zhongwen}\n"
        "粤文 two end:\n{two_yuewen_end}\n"
        "粤文 to split:\n{yuewen_to_split}\n"
    )
    answer_template = (
        "粤文 to append to one:\n{one_yuewen_to_append}\n"
        "粤文 to prepend to two:\n{two_yuewen_to_prepend}\n"
    )
    answer_example = SplitAnswer(
        one_yuewen_to_append="粤文 one to append",
        two_yuewen_to_prepend="粤文 text two to prepend",
    )

    def __init__(
        self,
        model: str = "gpt-4.1",
        examples: list[SplitTestCase] = None,
        print_test_case: bool = False,
    ):
        """Initialize.

        Arguments:
            model: OpenAI model to use.
            examples: Examples of inputs and expected outputs for few-shot learning
            print_test_case: Print test case afterward
        """
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

    def __call__(self, query: SplitQuery) -> SplitAnswer:
        """Split 粤文 text between two nascent 粤文 texts based on corresponding 中文.

        Arguments:
            query: Query containing 中文 and 粤文 texts and 粤文 text to split
        Returns:
            Answer including 粤文 text split between two nascent 粤文 texts
        """
        return self.split(query)

    def split(self, query: SplitQuery) -> SplitAnswer:
        """Split 粤文 text between two nascent 粤文 texts based on corresponding 中文.

        Arguments:
            query: Query containing 中文 and 粤文 texts and 粤文 text to split
        Returns:
            Answer including 粤文 text split between two nascent 粤文 texts
        """
        query_prompt = self.query_template.format_map(query.model_dump())
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
            answer = SplitAnswer.model_validate_json(content)
        except ValidationError as exc:
            error(f"Invalid response: {content}")
            raise exc
            # TODO: Try again if response is not valid
        try:
            test_case = SplitTestCase.from_query_and_answer(query, answer)
        except ValidationError as exc:
            error(f"Invalid test case:\nQuery:\n{query}\nAnswer:\n{answer}")
            raise exc
            # TODO: Try again if response is not valid

        if self.print_test_case:
            print(test_case)
        return answer
