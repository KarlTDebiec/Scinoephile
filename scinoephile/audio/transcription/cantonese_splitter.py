#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Splits 粤文 text between two nascent 粤文 texts based on 中文."""

from __future__ import annotations

import json
from pprint import pprint
from textwrap import dedent

from openai import OpenAI
from pydantic import BaseModel, Field

from scinoephile.audio.testing import SplitTestCase


class CantoneseSplitter:
    """Splits 粤文 text between two nascent 粤文 texts based on 中文."""

    prompt_template = (
        "中文 one:\n"
        "{zhongwen_one_input}\n"
        "Nascent 粤文 one:\n"
        "{yuewen_one_input}\n"
        "中文 two:\n"
        "{zhongwen_two_input}\n"
        "Nascent 粤文 two:\n"
        "{yuewen_two_input}\n"
        "粤文:\n"
        "{yuewen_input}\n"
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
            (
                dedent("""
            You are a helpful assistant that matches 粤文 subtitles of spoken Cantonese
            to 中文 subtitles of the same spoken content. You will be given a 中文
            subtitle and its nascent 粤文 subtitle, and a second 中文 subtitle with its
            nascent 粤文 subtitle. You will be given and additional 粤文 text whose
            assignment between the two subtitles is ambiguous, and you will determine
            how the 粤文 text should be distributed between the two nascent 粤文
            subtitles.
            Include all 粤文 characters from the input.
            All 汉字 in the output must come from the 粤文 input.
            No 汉字 in the output may come from the 中文 input. 
            Your response must be JSON; fill in the following template:
            """)
                .strip()
                .replace("\n", " ")
            )
            + "\n"
            + json.dumps(self.Response.model_json_schema(), indent=4)
        )
        if examples:
            self.system_prompt += (
                "\n\nHere are some examples of inputs and expected outputs:\n"
            )
            for example in examples:
                expected_response = self.Response(
                    one=example.yuewen_one_output,
                    two=example.yuewen_two_output,
                )
                self.system_prompt += (
                    f"中文 one:\n{example.zhongwen_one_input}\n"
                    f"Nascent 粤文 one:\n{example.yuewen_one_input}\n"
                    f"中文 two:\n{example.zhongwen_two_input}\n"
                    f"Nascent 粤文 two:\n{example.yuewen_two_input}\n"
                    f"粤文:\n{example.yuewen_input}\n"
                    f"结果:\n{json.dumps(expected_response, indent=4)}\n\n"
                )

    def __call__(
        self,
        zhongwen_one_input: str,
        yuewen_one_input: str,
        zhongwen_two_input: str,
        yuewen_two_input: str,
        yuewen_input: str,
    ) -> tuple[str, str]:
        return self.split(
            zhongwen_one_input,
            yuewen_one_input,
            zhongwen_two_input,
            yuewen_two_input,
            yuewen_input,
        )

    def split(
        self,
        zhongwen_one_input: str,
        yuewen_one_input: str,
        zhongwen_two_input: str,
        yuewen_two_input: str,
        yuewen_input: str,
    ) -> tuple[str, str]:
        user_prompt = self.prompt_template.format(
            zhongwen_one_input=zhongwen_one_input,
            yuewen_one_input=yuewen_one_input,
            zhongwen_two_input=zhongwen_two_input,
            yuewen_two_input=yuewen_two_input,
            yuewen_input=yuewen_input,
        )
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
            seed=0,
        )
        message = completion.choices[0].message
        content = message.content
        response = self.Response.model_validate_json(content)
        yuewen_one_output = response.one.strip()
        yuewen_two_output = response.two.strip()

        # TODO: Validate that output makes sense

        if self.print_test_case:
            test_case = SplitTestCase(
                zhongwen_one_input=zhongwen_one_input,
                yuewen_one_input=yuewen_one_input,
                zhongwen_two_input=zhongwen_two_input,
                yuewen_two_input=yuewen_two_input,
                yuewen_input=yuewen_input,
                yuewen_one_output=yuewen_one_output,
                yuewen_two_output=yuewen_two_output,
            )
            pprint(test_case)
        return yuewen_one_output, yuewen_two_output

    class Response(BaseModel):
        """Response model."""

        one: str = Field(..., description="Input text to append to first subtitle.")
        two: str = Field(..., description="Input text to prepend to second subtitle.")
