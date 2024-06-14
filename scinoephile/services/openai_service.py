#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
from __future__ import annotations

import json
from pprint import pformat
from typing import Any

from openai import OpenAI

from scinoephile.core import (
    SubtitleSeries,
    get_subtitle_blocks_for_synchronization,
)


class OpenAiService:

    synchronize_bilingual_subtitle_block_prompt = """
Instructions:

* Each request will start with CHINESE: followed by a series of Chinese subtitles in SRT
  format, and then ENGLISH: followed by a series of English subtitles in SRT format.
* Your responsiblitily is to provide a JSON response describing the synchronization of
  the Chinese and English subtitles.
* When determining the appropriate synchronization, special attention is needed for
  cases where the two languages do not align perfectly in number or content.
* The subtitle index may not align between the two languages, since one language may
  have subtitles not present in the other.
* The timing may not align between the two languages, since they may originate from 
  different sources with different timing
* Therefore, use the text of the subtitles as the primary guide for alignment, making
  use of your understanding of both languages.
* Use Chinese as the authoritativate source for timing, aligning the English subtitles
  to match this timing.
* In some cases, text that is relatively short in one language may be split across
  multiple sibtitles in the other language. In this case, the shorter text may appear in
  a single subtitle, displayed for a longer period of time, or the shorter text may
  appear in two consecutive subtitles, each with the same text.

Here are some examples to help you understand the task better:

Given the following input:

CHINESE:

2
00:02:32,152 --> 00:02:34,029
爸爸，牛奶糖

3
00:02:34,154 --> 00:02:35,197
謝謝

4
00:02:35,906 --> 00:02:36,907
妳們兩個累不累啊？

5
00:02:37,741 --> 00:02:38,867
就快到了

6
00:02:50,796 --> 00:02:51,588
小梅，快躲起來

7
00:02:57,761 --> 00:02:59,429
還以為是警察呢！

ENGLISH:

25
00:02:36,120 --> 00:02:37,872
Dad, do you want a caramel?

26
00:02:38,080 --> 00:02:40,833
Thanks. Aren't you tired?

27
00:02:41,040 --> 00:02:41,552
All right.

28
00:02:41,880 --> 00:02:42,949
We're almost there.

29
00:02:54,440 --> 00:02:55,350
Mei, hide!

30
00:03:01,600 --> 00:03:03,158
It wasn't a policeman.

The expected output is:

{'synchronization': 
    [
        {
            "chinese": [2],
            "end": ["chinese", 2],
            "english": [25],
            "merge": "one_one",
            "start": ["chinese", 2],
        },
        {
            "chinese": [3, 4],
            "end": ["chinese", 4],
            "english": [26],
            "merge": "two_one",
            "start": ["chinese", 3],
        },
        {
            "chinese": [5],
            "end": ["chinese", 5],
            "english": [28],
            "merge": "one_one",
            "start": ["chinese", 5],
        },
        {
            "chinese": [6],
            "end": ["chinese", 6],
            "english": [29],
            "merge": "one_one",
            "start": ["chinese", 6],
        },
        {
            "chinese": [7],
            "end": ["chinese", 7],
            "english": [30],
            "merge": "one_one",
            "start": ["chinese", 7],
        }
    ]
}

Chinese subtitles 3 and 4 have one corresponding English subtitle, 26.
English subtitle 27 has no corresponding Chinese subtitle, and is dropped.
The others have a clean 1:1 mapping.
"""

    def __init__(self):
        self.model = "gpt-4o"
        self.client = OpenAI()

    def synchronize_bilingual_subtitles(
        self,
        hanzi: SubtitleSeries,
        english: SubtitleSeries,
    ) -> SubtitleSeries:
        # 1
        #   Get subtitles 0-15 from hanzi, and the amount of time that they cover
        #   Get the corresponding subtitles from english
        #   Prompt LLM to synchronize the subtitles
        #   Ensure that the output can be parsed into a SubtitleSeries

        # 2
        #   Get subtitles 11-25 from hanzi, and the amount of time that they cover
        #   Get the corresponding subtitles from english
        #   Prompt LLM to synchronize the subtitles
        #   Ensure that the output can be parsed into a SubtitleSeries

        # 3
        #   Validate that subtitles 11-14 are the same from both queries
        #   If not, prompt LLM to reconcile the two

        # 4
        #   Get subtitles 21-35 from hanzi, and the amount of time that they cover
        #   Get the corresponding subtitles from english
        #   Prompt LLM to synchronize the subtitles
        #   Ensure that the output can be parsed into a SubtitleSeries

        # 5
        #   Validate that subtitles 21-24 are the same from both queries
        #   If not, prompt LLM to reconcile the two

        block_size = 16
        overlap = 12

        start_index = 0
        end_index = 0

        bilingual = SubtitleSeries()
        blocks = get_subtitle_blocks_for_synchronization(
            hanzi, english, block_size, overlap
        )
        last_bilingual_block = None
        for i, (hanzi_block, english_block) in enumerate(blocks):
            print(f"Processing block {i + 1}/{len(blocks)}")
            bilingual_block = self.get_synchronization(hanzi_block, english_block)

            if last_bilingual_block:
                overlap_previous_events = last_bilingual_block.events[-overlap:]
                overlap_current_events = bilingual_block.events[:overlap]
                if overlap_previous_events != overlap_current_events:
                    print(
                        f"Mismatch between last and current block:\n\n",
                        f"{pformat(overlap_previous_events)}\n\n",
                        f"{pformat(overlap_current_events)}",
                    )

            bilingual.events.extend(bilingual_block.events[: (block_size - overlap)])

            last_bilingual_block = bilingual_block

        return bilingual

    def get_synchronization(
        self, hanzi: SubtitleSeries, english: SubtitleSeries
    ) -> list[dict[str, Any]]:
        query = (
            f"CHINESE:\n\n"
            f"{hanzi.to_string('srt')}\n\n"
            f"ENGLISH:\n\n"
            f"{english.to_string('srt')}"
        )

        completion = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": self.synchronize_bilingual_subtitle_block_prompt,
                },
                {
                    "role": "user",
                    "content": query,
                },
            ],
        )

        response = completion.choices[0].message.content
        parsed_response = json.loads(response)

        return parsed_response

    def check_bilingual_subtitle_block(
        self, hanzi: SubtitleSeries, english: SubtitleSeries
    ) -> SubtitleSeries:
        pass
