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
    get_pair_strings_with_proportional_timings,
    get_series_pair_strings,
)
from scinoephile.open_ai.functions import get_sync_notes_response_model
from scinoephile.open_ai.subtitle_series_response import SubtitleSeriesResponse
from scinoephile.open_ai.sync_group_notes_response import SyncGroupNotesResponse
from scinoephile.open_ai.sync_notes_response import SyncNotesResponse


class OpenAiService:
    sync_notes_prompt = """
Instructions:
  * Read the provided Chinese and English subtitles for the same video clip, and write
    notes on the correspondence between the two.
  * The format of subtitles provided is pipe delimeted, with the following four fields:
    1. Index
    2. Start time, on a relative scale from 0 to 100, where 0 is the start of the clip
      and 100 is the end.
    3. End time, on a relative scale from 0 to 100, where 0 is the start of the clip
      and 100 is the end.
    4. Text of subtitle.
  * Your response must be a JSON object following this exact specification:

{
    "chinese": {
        "Chinese 1 corresponds to...",
        "Chinese 2 corresponds to...",
        ...
        },
    "english": {
        "English 1 corresponds to...",
        "English 2 corresponds to...",
        ...
    },
}

  * The number of notes under "chinese" must exactly equal the number of Chinese
    subtitles.
    * If two Chinese subtitles correspond to a single English subtitle, there still
      must be a separate note for each Chinese subtitle. Do not group Chinese subtitles
      together into a single note.
    * If one Chinese subtitle corresponds to two English subtitles, there still must
      be one single note for that Chinese subtitle.
  * The number of notes under "english" must exactly equal the number of English
    subtitles.
    * If two English subtitles correspond to a single Chinese subtitle, there still
      must be a separate note for each English subtitle. Do not group English subtitles
      together into a single note.
    * If one English subtitle corresponds to two Chinese subtitles, there still must
      be one single note for that English subtitle.
  * When referring to any subtitle, explicitly identify it by language and index, for
    example "Chinese 1" or "English 2". Every note must start with "Chinese" or
    "English" followed by the index.
  * Explicitly mention both the timing and meaning of the subtitles as you describe
    their correspondence to the other language.
    * The subtitles may be from completely different audio tracks, and may therefore not
      align exactly in time.
    * The subtitles may be from completely different audio tracks, and some subtitles
      may not have a corresponding subtitle in the other language.
  * Minor differences in timing are expected and do not need to be commented on.
  * If subtitles do not overlap in time but are close, do not comment on this.
  * If subtitles do not overlap in time at all, they do not correspond and should not be
    mentioned.
  * Balance the weight of timing and meaning in your notes; if two subtitles overlap
    extensively in time, more leniency in evaluating the correspondence of their
    meanings may be warranted.
"""

    sync_notes_prompt_eee = """
Instructions:
  * Read the provided Chinese and English subtitles for the same video clip, and write
    notes on how each English subtitle corresponds to the Chinese subtitles.
  * The format of subtitles provided is pipe delimeted, with the following four fields:
    1. Index
    2. Start time, on a relative scale from 0 to 100, where 0 is the start of the clip
      and 100 is the end.
    3. End time, on a relative scale from 0 to 100, where 0 is the start of the clip
      and 100 is the end.
    4. Text of subtitle.
  * When referring to any subtitle, explicitly identify it by language and index, for
    example "Chinese 1" or "English 2".
"""

    sync_group_notes_prompt = """
Instructions:
  * Read the Chinese and English subtitles for the same video clip, and notes on the
    correspondence between the two, and write notes on how they should be grouped into
    a single series of synchronized subtitles.
  * The format of subtitles provided is pipe delimeted, with the following four fields:
    * Index
    * Start time, on a relative scale from 0 to 100, where 0 is the start of the clip
      and 100 is the end.
    * End time, on a relative scale from 0 to 100, where 0 is the start of the clip
      and 100 is the end.
    * Text of subtitle.
  * Your response should be a JSON object following this exact specification:

{
    "synchronization": [
        <notes on synchronization group 1>,
        <notes on synchronization group 2>,
        ...
        ],
    ],
}

  * The synchronization groups are a sequence of mutually-exclusive, non-overlapping,
    sequential groups that will be used to compile synchronized bilingual subtitles.
  * The groups are mutually-exclusive; each Chinese and English subtitle may
    only be in a single group.
    * Do not, for example, state that "the first part of English 2" is in one group
      with Chinese 1, and "the latter part of English 2" is in another group with
      Chinese 2. Instead, describe one group with Chinese 1, Chinese2, and English 2.
  * Carefully read the notes to help judge which subtitles should be grouped together.
  * Groups must contain at least one Chinese subtitle.
    * If an English subtitle appears to stand alone in meaning and timing, do not
      include it in any group.
  * Groups may contain multiple Chinese subtitles and one English subtitle.
  * Groups with a single Chinese subtitle may contain more than one English subtitle.
  * Groups must not contain both multiple Chinese and multiple English subtitles.
  * When referring to any group, explicitly identify it by index, for example "Group 1".
  * When referring to any subtitle, explicitly identify it by language and index, for
    example "Chinese 1" or "English 2".
"""

    synchronize_bilingual_subtitle_block_prompt = """
Instructions:
  * Your task is to take Chinese and English subtitles for the same video clip and
    produce JSON output that will be used to produce a synchronized bilingual subtitle
    file.
  * Each request will start with CHINESE: followed by the Chinese subtitles, and then
    ENGLISH: followed by the English subtitles.
  * The format of subtitles is similar to SRT, but times have been adjusted to a
    relative scale from 0 to 100, where 0 is the start of the clip and 100 is the end.
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
  * "synchronization" defines a list of synchronization groups. Each synchronization
    group includes the indexes of the Chinese and English subtitles that encompass the
    same meaning and timing.
  * Within each synchronization group:
    * The "chinese" field lists the indices of the Chinese subtitles in the group.
    * The "english" field lists the indices of the English subtitles in the group.

Synchronization must follow these rules:
  * All Chinese subtitles are in exactly one synchronization group.
  * All English subtitles are in exactly one synchronization group, or none at all.
  * All Chinese subtitles are in their original order.
  * All English subtitles are in their original order.
  * English subtitles are in only one subtitle group.
  * Chinese subtitles are in only one subtitle group.
  * All Synchronization group contain either:
    * One Chinese subtitle and one English subtitle.
    * One Chinese subtitle and multiple English subtitles.
    * Multiple Chinese subtitles and one English subtitle.
  * Synchronization groups do not contain both multiple Chinese and multiple English
    subtitles.

Synchronization should follow these guidelines:
  * Use a combination of the timing and meaning of the subtitles to determine the
    synchronization.
  * If multiple Chinese subtitles combine to form one thought that corresponds to a
    single English subtitle, they should be grouped together in one synchronization
    group.
  * The Chinese and English subtitles' meaning should be similar, but may have
    significant differences, particular if the subtitles are idiomatic.
  * The Chinese and English subtitles' timing should be similar, but may not line up
    exactly.
  * If a Chinese subtitle only overlaps with one English subtitle, and that English
    subtitle aligns only with that Chinese subtitle, they are likely a simple pair.
  * Most of the time, the Chinese and English subtitles will align 1:1. In these
    cases, "chinese" and "english" for the synchronization group will contain only a
    single index each.
  * If an English subtitle does not overlap with any Chinese subtitles, it may be
    dropped.
  * If a Chinese subtitle has no corresponding English subtitle, it should be included
    on its own in a synchronization group.

Explanation must follow these rules:
  * Explain the subtitle groups in the order they appear in the input.
  * Do not include any generic text like "The subtitles are aligned based on their
    meaning and timing." Focus on the specific subtitles you have been asked about.
  * Include one bullet point for each subtitle group, starting with "Group 1:".
  * Explain every subtitle group with at least one sentence.
  * For each subtitle group, explain which Chinese and English subtitles were included
    and why, explicitly referencing their timing and meaning.
  * When referring to any subtitle, explicitly identify it by language and index, for
    example "Chinese 1" or "English 2".
"""

    def __init__(self):
        self.model = "gpt-4o"
        self.temperature = 1.0
        self.client = OpenAI()

    def get_sync_notes_yat(
        self,
        hanzi: SubtitleSeries,
        english: SubtitleSeries,
    ) -> SyncNotesResponse:
        hanzi_str, english_str = get_series_pair_strings(hanzi, english)

        template_json = {
            "chinese": [
                f"Chinese {i} corresponds to..."
                for i in range(1, len(hanzi.events) + 1)
            ],
            "english": [
                f"English {i} corresponds to..."
                for i in range(1, len(english.events) + 1)
            ],
        }

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
            response_format=SyncNotesResponse,
            messages=[
                {
                    "role": "system",
                    "content": self.sync_notes_prompt,
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
            response = SyncNotesResponse.parse_raw(content)
            return response
        except ValidationError as e:
            print(f"Validation error: {e}")
            raise e

    def get_sync_notes_eee(
        self,
        hanzi: SubtitleSeries,
        english: SubtitleSeries,
        language: str,
    ) -> SyncNotesResponse:
        hanzi_str, english_str = get_series_pair_strings(hanzi, english)

        if language == "chinese":
            response_model = get_sync_notes_response_model(language, len(hanzi.events))
        elif language == "english":
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
                {
                    "role": "system",
                    "content": self.sync_notes_prompt,
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
            response = response_model.model_validate_json(content)
            return response
        except ValidationError as e:
            print(f"Validation error: {e}")
            raise e

    def get_synchronization_group_notes(
        self,
        hanzi: SubtitleSeries,
        english: SubtitleSeries,
        notes: SyncNotesResponse,
    ) -> SyncGroupNotesResponse:
        hanzi_str, english_str = get_series_pair_strings(hanzi, english)
        query = f"CHINESE:\n{hanzi_str}\n\nENGLISH:\n{english_str}"
        query += f"\n\nCHINESE NOTES:"
        for note in notes.chinese:
            query += f"\n* {note}"
        query += f"\n\nENGLISH NOTES:"
        for note in notes.english:
            query += f"\n* {note}"

        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            temperature=self.temperature,
            response_format=SyncGroupNotesResponse,
            messages=[
                {
                    "role": "system",
                    "content": self.sync_group_notes_prompt,
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
            response = SyncGroupNotesResponse.parse_raw(content)
            return response
        except ValidationError as e:
            print(f"Validation error: {e}")
            raise e

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
