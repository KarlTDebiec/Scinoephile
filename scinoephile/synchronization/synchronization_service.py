#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
from __future__ import annotations

from copy import deepcopy
from pprint import pformat

import numpy as np

from scinoephile.core import ScinoephileException, Subtitle, SubtitleSeries
from scinoephile.core.pairs import (
    get_pair_blocks_by_pause,
    get_pair_with_zero_start,
    is_pair_one_to_one_mapped,
)
from scinoephile.open_ai import OpenAiService, SubtitleGroupResponse
from scinoephile.open_ai.functions import (
    get_sync_from_sync_groups,
    get_sync_groups_from_indexes,
    get_sync_indexes_from_notes,
)


class SynchronizationService:
    def __init__(self):
        self.open_ai_service = OpenAiService()

    def get_synced(
        self,
        hanzi: SubtitleSeries,
        english: SubtitleSeries,
    ) -> SubtitleSeries:
        pair_blocks = get_pair_blocks_by_pause(hanzi, english)
        bilingual_blocks = []

        for hanzi_block, english_block in pair_blocks:
            # Simple 1:1 mapping
            if is_pair_one_to_one_mapped(hanzi_block, english_block):
                bilingual_block = self.get_synced_simple(hanzi_block, english_block)
                bilingual_blocks.append(bilingual_block)
                continue

            # Short block mappable in a single request
            length = max(len(hanzi_block.events), len(english_block.events))
            if length <= 10:
                bilingual_block = self.get_synced_short(hanzi_block, english_block)
                bilingual_blocks.append(bilingual_block)
                continue

            # Long block mappable in multiple requests
            bilingual_block = self.get_synced_long(hanzi_block, english_block)
            bilingual_blocks.append(bilingual_block)

        bilingual = self.get_merged(bilingual_blocks)
        return bilingual

    def get_synced_long(
        self,
        hanzi: SubtitleSeries,
        english: SubtitleSeries,
    ) -> SubtitleSeries:
        return SubtitleSeries()

    def get_synced_short(
        self,
        hanzi: SubtitleSeries,
        english: SubtitleSeries,
    ) -> SubtitleSeries:
        hanzi_zero, english_zero = get_pair_with_zero_start(hanzi, english)

        # Get synchronization in Chinese direction
        chinese_notes = self.open_ai_service.get_sync_notes(
            hanzi_zero, english_zero, "chinese"
        ).model_dump()
        chinese_mapping = get_sync_indexes_from_notes(chinese_notes)
        chinese_groups = get_sync_groups_from_indexes(chinese_mapping)
        chinese_sync = get_sync_from_sync_groups(
            chinese_groups, "chinese", len(hanzi.events)
        )

        # Get synchronization in English direction
        english_notes = self.open_ai_service.get_sync_notes(
            hanzi_zero, english_zero, "english"
        ).model_dump()
        english_mapping = get_sync_indexes_from_notes(english_notes)
        english_groups = get_sync_groups_from_indexes(english_mapping)
        english_sync = get_sync_from_sync_groups(
            english_groups, "chinese", len(hanzi.events)
        )

        if chinese_sync == english_sync:
            return self.get_merged(hanzi, english, chinese_groups)

        chinese_notes_2 = self.open_ai_service.get_reconciled_sync_notes(
            hanzi_zero, english_zero, chinese_notes, english_notes, "chinese"
        ).model_dump()
        chinese_mapping = get_sync_indexes_from_notes(chinese_notes_2)
        chinese_groups = get_sync_groups_from_indexes(chinese_mapping)
        chinese_sync = get_sync_from_sync_groups(
            chinese_groups, "chinese", len(hanzi.events)
        )

        english_notes_2 = self.open_ai_service.get_reconciled_sync_notes(
            hanzi_zero, english_zero, chinese_notes, english_notes, "english"
        ).model_dump()
        english_mapping = get_sync_indexes_from_notes(english_notes_2)
        english_groups = get_sync_groups_from_indexes(english_mapping)
        english_sync = get_sync_from_sync_groups(
            english_groups, "chinese", len(hanzi.events)
        )

        if chinese_sync == english_sync:
            return self.get_merged(hanzi, english, chinese_groups)

        raise ScinoephileException(
            "Inconsistent groups obtained from Chinese and English directions:\n"
            f"Chinese notes:\n{pformat(chinese_notes_2)}\n"
            f"Chinese sync:\n{pformat(chinese_sync)}\n"
            f"English notes:\n{pformat(english_notes_2)}\n"
            f"English sync:\n{pformat(english_sync)}"
        )

    @staticmethod
    def get_merged(
        hanzi: SubtitleSeries,
        english: SubtitleSeries,
        groups: list[SubtitleGroupResponse],
    ) -> SubtitleSeries:
        bilingual = SubtitleSeries()

        for group in groups:
            hanzi_events = [hanzi.events[i - 1] for i in group["chinese"]]
            english_events = [english.events[i - 1] for i in group["english"]]

            # One-to-one mapping
            if len(hanzi_events) == 1 and len(english_events) == 1:
                synced_event = deepcopy(hanzi_events[0])
                synced_event.text = f"{hanzi_events[0].text}\n{english_events[0].text}"
                bilingual.events.append(synced_event)
                continue

            # Multiple Chinese to one English
            if len(hanzi_events) > 1 and len(english_events) == 1:
                english_text = english_events[0].text
                start = hanzi_events[0].start
                end = hanzi_events[-1].end
                edges = np.linspace(start, end, len(hanzi_events) + 1, dtype=int)

                for event, start, end in zip(hanzi_events, edges[:-1], edges[1:]):
                    text = f"{event.text}\n{english_text}"
                    bilingual.events.append(Subtitle(start=start, end=end, text=text))
                continue

            # One Chinese to multiple English
            if len(hanzi_events) == 1 and len(english_events) > 1:
                hanzi_text = hanzi_events[0].text
                start = english_events[0].start
                end = english_events[-1].end
                edges = np.linspace(start, end, len(english_events) + 1, dtype=int)

                for event, start, end in zip(english_events, edges[:-1], edges[1:]):
                    text = f"{hanzi_text}\n{event.text}"
                    bilingual.events.append(Subtitle(start=start, end=end, text=text))
                continue

            raise ScinoephileException()

        return bilingual

    @staticmethod
    def get_synced_simple(
        hanzi: SubtitleSeries,
        english: SubtitleSeries,
    ) -> SubtitleSeries:
        """Get synchronized subtitles from a cleanly mapped pair of subtitle series.

        Arguments:
            hanzi: Hanzi subtitles
            english: English subtitles
        Returns:
            synchronized subtitles
        """
        bilingual = SubtitleSeries()
        bilingual.events = []
        for event_one, event_two in zip(hanzi.events, english.events):
            synced_event = deepcopy(event_one)
            synced_event.text = f"{event_one.text}\n{event_two.text}"
            bilingual.events.append(synced_event)

        return bilingual
