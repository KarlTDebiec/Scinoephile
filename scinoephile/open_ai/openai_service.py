#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Service for interacting with OpenAI API."""
from __future__ import annotations

import json

from openai import OpenAI
from pydantic import ValidationError

from scinoephile.core import ScinoephileException
from scinoephile.core.subtitle_series import SubtitleSeries
from scinoephile.core.subtitles import (
    get_series_pair_strings,
)
from scinoephile.open_ai.functions import get_sync_notes_response_model
from scinoephile.open_ai.sync_notes_response import SyncNotesResponse


class OpenAiService:
    sync_notes_prompt = """
Instructions:
  * Read the provided Chinese and English subtitles for the same video clip, and write
    notes on how each {language_1} subtitle corresponds to the {language_2} subtitles.
  * The format of subtitles provided is pipe delimeted, with the following four fields:
    1. Index
    2. Start time, on a relative scale from 0 to 100, where 0 is the start of the clip
      and 100 is the end.
    3. End time, on a relative scale from 0 to 100, where 0 is the start of the clip
      and 100 is the end.
    4. Text of subtitle.
  * When referring to any subtitle, explicitly identify it by language and index, for
    example "{language_1} 1" and "{language_2} 2".
  * When mentioning multiple subtitles, incude the full language and index, for example
    "{language_1} 1 corresponds to {language_2} 1 and {language_2} 2".
  * **Only mention corresponding subtitles**: If a {language_1} subtitle has no
    corresponding {language_2} subtitle, state this clearly (e.g., "{language_1} 4 has
    no corresponding {language_2} subtitle"). Do not mention or describe any
    non-corresponding subtitles.
  * Small differences in timing and meaning are expected and do not need to be
    mentioned.
"""

    def __init__(self):
        self.model = "gpt-4o"
        self.temperature = 1.0
        self.client = OpenAI()

    def get_sync_notes(
        self,
        hanzi: SubtitleSeries,
        english: SubtitleSeries,
        language: str,
    ) -> SyncNotesResponse:
        hanzi_str, english_str = get_series_pair_strings(hanzi, english)

        if language == "chinese":
            prompt = self.sync_notes_prompt.format(
                language_1="Chinese", language_2="English"
            )
            response_model = get_sync_notes_response_model(language, len(hanzi.events))
        elif language == "english":
            prompt = self.sync_notes_prompt.format(
                language_1="English", language_2="Chinese"
            )
            response_model = get_sync_notes_response_model(
                language, len(english.events)
            )
        else:
            raise ScinoephileException()

        template_json = response_model.model_json_schema()

        query = (
            f"CHINESE:\n"
            f"{hanzi_str}\n\n"
            f"ENGLISH:\n"
            f"{english_str}\n\n"
            f"Your response must be JSON; fill in the following template:\n"
            f"{json.dumps(template_json, indent=4)}"
        )

        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            temperature=self.temperature,
            response_format=response_model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": query},
            ],
        )

        # Deserialize
        message = completion.choices[0].message
        content = message.content
        try:
            response = response_model.model_validate_json(content)
            return response
        except ValidationError as e:
            print(f"Validation error: {e}")
            raise e
