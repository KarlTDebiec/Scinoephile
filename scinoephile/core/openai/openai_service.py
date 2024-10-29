#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Service for interacting with OpenAI API."""
from __future__ import annotations

from openai import OpenAI
from pydantic import ValidationError

from scinoephile.core.openai.subtitle_series_response import SubtitleSeriesResponse
from scinoephile.core.subtitle_series import SubtitleSeries
from scinoephile.core.subtitles import get_pair_strings_with_proportional_timings


class OpenAiService:
    synchronize_bilingual_subtitle_block_prompt = """
Instructions:
  * Each request will start with CHINESE: followed by a series of Chinese subtitles in
    SRT format, and then ENGLISH: followed by a series of English subtitles in SRT
    format. For clarity, the timings have been converted to a relative scale from 0 to
    100, where 0 is the start of the subtitles and 100 is the end.
  * You are tasked with mapping the English subtitles to their corresponding Chinese
    subtitles, based on their meaning and timing.
  * Your response should be a JSON object following this exact specification:

{
    "explanation": <text explaining the mapping between Chinese and English>,
    "synchronization": [
        {
            "chinese": [<list of Chinese subtitle indexes>],
            "english": [<list of English subtitle indexes>],
        },
        ...
    ],
}

  * "explanation" contains text describing the rationale for the mapping between Chinese
     and English subtitles.
  * "synchronization" defines a list of synchronization groups. Each group contains a
    group of Chinese and English subtitles that contain the same meaning.
  * Within each synchronization group:
    * The "chinese" field lists the indices of the Chinese subtitles in the group.
    * The "english" field lists the indices of the English subtitles in the group.

Synchronization must follow these rules:
  * All Chinese subtitles are in exactly one synchronization group.
  * All English subtitles are in exactly one synchronization group, or none at all.
  * All Chinese subtitles are in their original order.
  * All English subtitles are in their original order.
  * English subtitles are not in more than one subtitle group.
  * Chinese subtitles are not in more than one subtitle group.
  * All Synchronization group contain either:
    * One Chinese subtitle and one English subtitle.
    * One Chinese subtitle and multiple English subtitles.
    * Multiple Chinese subtitles and one English subtitle.
  * Synchronization groups do not contain both multiple Chinese and multiple English
    subtitles.

Synchronization should follow these guidlines:
  * Use a combination of the timing and meaning of the subtitles to determine the
    synchronization.
  * If multiple Chinese subtitles combine to form one thought that corresponds to a
    single English subtitle, they must be grouped together in one synchronization group.
  * The Chinese and English subtitles' meaning should be similar, but may have
    significant differences, particular if the subtitles are idiomatic.
  * The Chinese and English subtitles' timing should be similar, but may have variation.
  * If a Chinese subtitle only overlaps with one English subtitle, and that English
    subtitle aligns only with that Chinese subtitle, they are likely a simple pair.
  * Most of the time, the Chinese and English subtitles will align 1:1. In these
    cases, "chinese" and "english" for the synchronization group will contain only a
    single index each.
  * If an English subtitle does not overlap with any Chinese subtitles, it may be
    dropped.
  * If a Chinese subtitle has no corresponding English subtitle, it must be included
    on its own in a synchronization group.

Explanation must follow these rules:
  * Do not include any generic text like "The subtitles are aligned based on their
    meaning and timing." Focus on the specific subtitles you have been asked about.
  * Explain every subtitle group with at least one sentence.
  * For each each subtitle group, explain which Chinese and English subtitles were
    included and why, explicitly referencing their timing and meaning.
  * When referring to any subtitle, explicitly identify it by language and index, for
    example "Chinese 1" or "English 2".
"""

    def __init__(self):
        self.model = "gpt-4o"
        self.client = OpenAI()

    def get_synchronization(
        self, hanzi: SubtitleSeries, english: SubtitleSeries
    ) -> SubtitleSeriesResponse:
        hanzi_str, english_str = get_pair_strings_with_proportional_timings(
            hanzi, english
        )
        query = f"CHINESE:\n{hanzi_str}\n\nENGLISH:\n{english_str}"

        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            temperature=1.0,
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
