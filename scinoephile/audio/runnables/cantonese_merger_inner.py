#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runnable that merges Cantonese subtitles into one."""

from __future__ import annotations

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from openai import OpenAI

from scinoephile.audio.models import MergePayload
from scinoephile.testing import MergeTestCase


class CantoneseMergerInner(Runnable):
    """Runnable that merges Cantonese subtitles into one."""

    merge_prompt_template = PromptTemplate.from_template(
        "中文 subtitle:\n"
        "{zhongwen}\n"
        "粤文 subtitles:\n"
        "{yuewen}\n"
        "Merge the 粤文 subtitles into a single line. Do not change the wording "
        "of the 粤文 subtitles. Ensure all characters present in the 粤文 subtitle "
        "input remain present in the output. Adjust spacing and punctuation to match "
        "the 中文 subtitle."
    )

    def __init__(self, model: str = "gpt-4.1", examples: list[MergeTestCase] = None):
        self.client = OpenAI()
        self.model = model

        self.system_prompt = (
            "You are a helpful assistant that merges multi-line 粤文 subtitles of "
            "spoken Cantonese to match the spacing and punctuation of a single-line "
            "中文 subtitle. Preserve all 粤文 characters and merge them into one line. "
            "Adjust punctuation and spacing to match the 中文 version."
        )
        if examples:
            self.system_prompt += (
                "\n\nHere are some examples of inputs and expected outputs:\n"
            )
            for example in examples:
                self.system_prompt += (
                    f"中文:\n{example.zhongwen_input}\n"
                    f"粤文:\n" + "\n".join(example.yuewen_input) + "\n"
                    f"结果:\n{example.yuewen_output}\n"
                )

    def invoke(
        self,
        input: MergePayload,
        config: RunnableConfig | None = None,
        **kwargs,
    ) -> str:
        user_prompt = self.merge_prompt_template.format(
            zhongwen=input.zhongwen,
            yuewen="\n".join(input.yuewen),
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
        )
        return response.choices[0].message.content.strip()
