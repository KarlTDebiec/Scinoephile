#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to OpenAI"""
from __future__ import annotations

from scinoephile.core import ScinoephileException, Subtitle, SubtitleSeries
from scinoephile.core.openai.openai_service import OpenAiService
from scinoephile.core.openai.subtitle_group_response import SubtitleGroupResponse
from scinoephile.core.openai.subtitle_series_response import SubtitleSeriesResponse


def get_synced_subtitles(
    hanzi: SubtitleSeries, english: SubtitleSeries, response: SubtitleSeriesResponse
) -> SubtitleSeries:
    events = []
    for i, group in enumerate(response.synchronization):
        chinese_indexes = [i - 1 for i in group.chinese]
        english_indexes = [i - 1 for i in group.english]

        # One Chinese to zero English
        if len(chinese_indexes) == 1 and len(english_indexes) == 0:
            start = hanzi.events[chinese_indexes[0]].start
            end = hanzi.events[chinese_indexes[0]].end
            chinese_text = hanzi.events[chinese_indexes[0]].text
            events.append(Subtitle(start=start, end=end, text=chinese_text))
            continue

        # One Chinese to one English
        if len(chinese_indexes) == 1 and len(english_indexes) == 1:
            start = hanzi.events[chinese_indexes[0]].start
            end = hanzi.events[chinese_indexes[0]].end
            chinese_text = hanzi.events[chinese_indexes[0]].text
            english_text = english.events[english_indexes[0]].text
            bilingual_text = f"{chinese_text}\n{english_text}"
            events.append(Subtitle(start=start, end=end, text=bilingual_text))
            continue

        # One Chinese to multiple English
        if len(chinese_indexes) == 1 and len(english_indexes) > 1:
            chinese_text = hanzi.events[chinese_indexes[0]].text
            start = hanzi.events[chinese_indexes[0]].start
            end = hanzi.events[chinese_indexes[0]].end
            duration = (end - start) / len(english_indexes)
            for english_index in english_indexes:
                english_text = english.events[english_index].text
                bilingual_text = f"{chinese_text}\n{english_text}"
                events.append(
                    Subtitle(start=start, end=start + duration, text=bilingual_text)
                )
                start += duration
            continue

        # Multiple Chinese to one English
        if len(chinese_indexes) > 1 and len(english_indexes) == 1:
            english_text = english.events[english_indexes[0]].text
            start = hanzi.events[chinese_indexes[0]].start
            end = hanzi.events[chinese_indexes[-1]].end
            duration = (end - start) / len(chinese_indexes)
            for chinese_index in chinese_indexes:
                chinese_text = hanzi.events[chinese_index].text
                bilingual_text = f"{chinese_text}\n{english_text}"
                events.append(
                    Subtitle(start=start, end=start + duration, text=bilingual_text)
                )
                start += duration
            continue

        # Any other case
        raise ScinoephileException(
            f"Unexpected number of Chinese ({len(chinese_indexes)}) and "
            f"English ({len(english_indexes)}) subtitles for group {i}"
        )

    # Organize and return
    synced = SubtitleSeries()
    synced.events = events
    return synced


__all__ = [
    "OpenAiService",
    "SubtitleGroupResponse",
    "SubtitleSeriesResponse",
    "get_synced_subtitles",
]
