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
