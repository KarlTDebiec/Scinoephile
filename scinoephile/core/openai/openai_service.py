#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Service for interacting with OpenAI API."""
from __future__ import annotations

from openai import OpenAI
from pydantic import ValidationError

from scinoephile.core.openai.subtitle_series_response import SubtitleSeriesResponse
from scinoephile.core.subtitle_series import SubtitleSeries


class OpenAiService:
    synchronize_bilingual_subtitle_block_prompt = """
Instructions:
  * Each request will start with CHINESE: followed by a series of Chinese subtitles in
    SRT format, and then ENGLISH: followed by a series of English subtitles in SRT
    format.
  * You are tasked with mapping the English subtitles to their corresponding Chinese
    subtitles, based on their meaning and timing.
  * Your response should be a JSON object following this exact specification:

{
    "synchronization": [
        {
            "chinese": [<list of Chinese subtitle indexes>],
            "english": [<list of English subtitle indexes>],
        },
        ...
    ],
    "explanation": [<list of explanations of ONLY subtitles that did not map cleanly
      1:1; specific examples of situations that warrant explanation are listed
      below>],
}
    
  * "synchronization" defines a list of synchronization groups. Each group contains a
    group of Chinese and English subtitles that contain the same meaning.
  * Within each synchronization group:
    * The "chinese" field lists the indices of the Chinese subtitles in the group.
    * The "english" field lists the indices of the English subtitles in the group

The following rules must never be violated:
  * A Chinese subtitle must never be skipped.
  * Chinese subtitles must never be reordered.
  * English subtitles must never be reordered.
  * Each synchronization group must contain either:
    * One Chinese subtitle and one English subtitle.
    * One Chinese subtitle and multiple English subtitles.
    * Multiple Chinese subtitles and one English subtitle.
  * Synchronization groups must not contain both multiple Chinese and multiple English
    subtitles.
  * Seriously, synchronization groups must not contain both multiple Chinese and
    multiple English subtitles.

The following guidelines should be followed:
  * Use the text of the subtitles as the primary guide for alignment, considering your
    understanding of both languages.
  * Timing should roughly align between Chinese and English sources, but may not be
    exact.
  * Meaning should roughly align between Chinese and English, but may be fairly loose.
  * Most of the time, the Chinese and English subtitles will align 1:1. In these
    cases, "chinese" and "english" for the synchronization group will contain only a
    single index each.
  * English subtitles may be skipped if there is no corresponding Chinese subtitle.
    This should be relatively rare.

Here are some examples to help you understand the task better:

Given the following input:

CHINESE:

1
00:00:00,000 --> 00:00:02,044
好破哦

2
00:00:02,169 --> 00:00:03,587
好破哦

3
00:00:03,712 --> 00:00:05,214
好像一间鬼屋哦

4
00:00:05,380 --> 00:00:06,214
鬼屋

ENGLISH:

1
00:00:00,003 --> 00:00:01,834
It's a wreck!

2
00:00:02,003 --> 00:00:03,402
Wreck!

3
00:00:03,643 --> 00:00:04,996
Looks like a haunted house!

4
00:00:05,163 --> 00:00:05,993
Haunted?

The expected output is:

{
    "explanation": [],
    "synchronization": [
        {
            "chinese": [1],
            "english": [1]
        },
        {
            "chinese": [2],
            "english": [2]
        },
        {
            "chinese": [3],
            "english": [3]
        },
        {
            "chinese": [4],
            "english": [4]
        }
    ]
}

Given the following input:

CHINESE:

1
00:00:00,000 --> 00:00:01,877
爸爸，牛奶糖

2
00:00:02,002 --> 00:00:03,045
谢谢

3
00:00:03,754 --> 00:00:04,755
妳们两个累不累啊？

4
00:00:05,589 --> 00:00:06,715
就快到了

ENGLISH:

1
00:00:00,000 --> 00:00:01,752
Dad, do you want a caramel?

2
00:00:01,960 --> 00:00:04,713
Thanks. Aren't you tired?

3
00:00:04,920 --> 00:00:05,432
All right.

4
00:00:05,760 --> 00:00:06,829
We're almost there.

The expected output is:

{
    "explanation": [
        "Chinese subtitle 3 contains '妳们两个累不累啊？', which can be roughly interpreted as 'Aren't you two tired?' This matches with part of English subtitle 2, after 'Thanks.' Thus, it combines with the Chinese subtitle 2 '谢谢', which means 'Thanks.', making the synchronization group for English subtitle 2 mapping to Chinese subtitles 2 and 3.",
        "English subtitle 3 has no corresponding Chinese subtitle, and is omitted"
    ],
    "synchronization": [
        {
            "chinese": [1],
            "english": [1]
        },
        {
            "chinese": [2, 3],
            "english": [2]
        },
        {
            "chinese": [4],
            "english": [4]
        }
    ]
}

The following rules must never be violated:
  * A Chinese subtitle must never be skipped.
  * Chinese subtitles must never be reordered.
  * English subtitles must never be reordered.
  * Each synchronization group must contain either:
    * One Chinese subtitle and one English subtitle.
    * One Chinese subtitle and multiple English subtitles.
    * Multiple Chinese subtitles and one English subtitle.
  * Synchronization groups must not contain both multiple Chinese and multiple English
    subtitles.
  * Seriously, synchronization groups must not contain both multiple Chinese and
    multiple English subtitles.

The following guidelines should be followed:
  * Use the text of the subtitles as the primary guide for alignment, considering your
    understanding of both languages.
  * Timing should roughly align between Chinese and English sources, but may not be
    exact.
  * Meaning should roughly align between Chinese and English, but may be fairly loose.
  * Most of the time, the Chinese and English subtitles will align 1:1. In these
    cases, "chinese" and "english" for the synchronization group will contain only a
    single index each.
  * English subtitles may be skipped if there is no corresponding Chinese subtitle.
    This should be relatively rare.
"""

    def __init__(self):
        self.model = "gpt-4o"
        self.client = OpenAI()

    def get_synchronization(
        self, hanzi: SubtitleSeries, english: SubtitleSeries
    ) -> SubtitleSeriesResponse:
        query = (
            f"CHINESE:\n\n"
            f"{hanzi.to_string('srt')}\n\n"
            f"ENGLISH:\n\n"
            f"{english.to_string('srt')}"
        )

        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            response_format=SubtitleSeriesResponse,
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

        # Deserialize
        message = completion.choices[0].message
        content = message.content
        try:
            subtitle_series_response = SubtitleSeriesResponse.parse_raw(content)
            return subtitle_series_response
        except ValidationError as e:
            print(f"Validation error: {e}")
            raise e
