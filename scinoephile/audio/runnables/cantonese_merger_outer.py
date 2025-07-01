#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runnable that merges Cantonese subtitles into one."""

from __future__ import annotations

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from openai import OpenAI
from pydantic import BaseModel, Field

from scinoephile.audio import AudioSeries, AudioSubtitle
from scinoephile.audio.models import TranscriptionPayload
from scinoephile.core import ScinoephileException
from scinoephile.testing import MergeTestCase


class MergePayload(BaseModel):
    """Payload for merging Cantonese subtitles."""

    zhongwen: str = Field(..., description="中文 subtitle text")
    yuewen: list[str] = Field(..., description="粤文 subtitle text")


class CantoneseMerger(Runnable):
    """Runnable that merges Cantonese subtitles into one."""

    system_prompt = PromptTemplate.from_template(
        "You are a helpful assistant that merges multi-line 粤文 subtitles of spoken "
        "Cantonese to match the format of a single-string 中文 subtitle. The merged "
        "粤文 subtitle should match the spacing and punctuation of the 中文 subtitle. "
        "Do not alter the 粤文 wording."
    ).format()

    def get_system_prompt_with_examples(test_cases: list[MergeTestCase]) -> str:
        intro = (
            "You are a helpful assistant that merges multi-line 粤文 subtitles of spoken Cantonese "
            "to match the spacing and punctuation of a single-line 中文 subtitle. "
            "Preserve all 粤文 characters and merge them into one line. "
            "Add punctuation and spacing to reflect the 中文 version.\n\n"
            "Here are some examples:\n\n"
        )

        example_texts = []
        for case in test_cases:
            example = (
                f"中文:\n{case.zhongwen_input}\n"
                f"粤文:\n" + "\n".join(case.yuewen_input) + "\n"
                f"结果:\n{case.yuewen_output}\n"
            )
            example_texts.append(example)

        return intro + "\n".join(example_texts) + "\nNow merge the following:"

    merge_prompt_template = PromptTemplate.from_template(
        "中文 subtitle:\n"
        "{zhongwen}\n"
        "粤文 subtitles:\n"
        "{yuewen}\n"
        "Merge the 粤文 subtitles into a single line. Do not change the wording "
        "of the 粤文 subtitles. Ensure all characters present in the 粤文 subtitle "
        "input remain present int he output. Adjust spacing and punctuation to match "
        "the 中文 subtitle."
    )

    def __init__(self, model: str = "gpt-4.1"):
        self.client = OpenAI()
        self.model = model

    def invoke(
        self,
        input: TranscriptionPayload,
        config: RunnableConfig | None = None,
        **kwargs,
    ) -> TranscriptionPayload:
        zhongwen_subs = input["zhongwen_subs"]
        sync_groups = input["sync_groups"]
        yuewen_subs = input["yuewen_subs"]

        merged_yuewen_subs = AudioSeries()
        merged_yuewen_subs.audio = yuewen_subs.audio
        for i, sync_group in enumerate(sync_groups):
            zhongwen_indexes = [i - 1 for i in sync_group[0]]
            yuewen_indexes = [i - 1 for i in sync_group[1]]
            if len(zhongwen_indexes) != 1:
                raise ScinoephileException("Expected exactly one 中文 subtitle.")
            if len(yuewen_indexes) == 0:
                raise ScinoephileException("Expected at least one 粤文 subtitle.")
            zhongwen_sub = zhongwen_subs.events[zhongwen_indexes[0]]
            print(
                f"Group {i:02d} | "
                f"中文: {zhongwen_sub.text} | "
                f"粤文: {'_'.join(yuewen_subs.events[i].text.strip() for i in yuewen_indexes)}"
            )
            if len(yuewen_indexes) == 1:
                merged_yuewen_text = yuewen_subs.events[yuewen_indexes[0]].text.strip()
            else:
                zhongwen = zhongwen_sub.text.strip()
                yuewen = [yuewen_subs.events[i].text.strip() for i in yuewen_indexes]
                payload = MergePayload(
                    zhongwen=zhongwen,
                    yuewen=yuewen,
                )
                user_prompt = self.merge_prompt_template.format(
                    zhongwen=payload.zhongwen,
                    yuewen="\n".join(payload.yuewen),
                )
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0,
                )
                merged_yuewen_text = response.choices[0].message.content.strip()
                print(
                    f"Group {i:02d} | "
                    f"中文: {zhongwen_sub.text} | "
                    f"粤文: {merged_yuewen_text}"
                )
            merged_yuewen_subs.events.append(
                AudioSubtitle(
                    start=zhongwen_sub.start,
                    end=zhongwen_sub.end,
                    text=merged_yuewen_text,
                )
            )

        return TranscriptionPayload(
            zhongwen_subs=zhongwen_subs,
            yuewen_segments=input["yuewen_segments"],
            yuewen_subs=merged_yuewen_subs,
            sync_groups=sync_groups,
        )
