#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Merges transcribed 粤文 text to match 中文 punctuation and spacing."""

from __future__ import annotations

from pprint import pprint
from textwrap import dedent

from openai import OpenAI

from scinoephile.audio.testing import MergeTestCase


class CantoneseMerger:
    """Merges transcribed 粤文 text to match 中文 punctuation and spacing."""

    prompt_template = "中文:\n{zhongwen}\n粤文:\n{yuewen}\n结果:\n"

    def __init__(
        self,
        model: str = "gpt-4.1",
        examples: list[MergeTestCase] = None,
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
            dedent("""
            You are a helpful assistant that merges multi-line 粤文 subtitles of spoken
            Cantonese to match the spacing and punctuation of a single-line 中文
            subtitle.
            Include all 粤文 characters and merge them into one line.
            All 汉字 in the output must come from the 粤文 input.
            No 汉字 in the output may come from the 中文 input.
            Adjust punctuation and spacing to match the 中文 input.
            """)
            .strip()
            .replace("\n", " ")
        )

        if examples:
            self.system_prompt += (
                "\n\nHere are some examples of inputs and expected outputs:\n"
            )
            for example in examples:
                self.system_prompt += (
                    f"中文:\n{example.zhongwen_input}\n"
                    f"粤文:\n" + "\n".join(example.yuewen_input) + "\n"
                    f"结果:\n{example.yuewen_output}\n\n"
                )

    def __call__(self, zhongwen_input: str, yuewen_input: list[str]) -> str:
        """Merge 粤文 text to match 中文 punctuation and spacing.

        Arguments:
            zhongwen_input: Single 中文 text against which to match
            yuewen_input: 粤文 text
        """
        return self.punctuate(zhongwen_input, yuewen_input)

    def punctuate(self, zhongwen_input: str, yuewen_input: list[str]) -> str:
        """Merge 粤文 text to match 中文 punctuation and spacing.

        Arguments:
            zhongwen_input: Single 中文 text against which to match
            yuewen_input: 粤文 text
        """
        user_prompt = self.prompt_template.format(
            zhongwen=zhongwen_input,
            yuewen="\n".join(yuewen_input),
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
            seed=0,
        )
        if self.print_test_case:
            test_case = MergeTestCase(
                zhongwen_input=zhongwen_input,
                yuewen_input=yuewen_input,
                yuewen_output=response.choices[0].message.content.strip(),
            )
            pprint(test_case)
        return response.choices[0].message.content.strip()
