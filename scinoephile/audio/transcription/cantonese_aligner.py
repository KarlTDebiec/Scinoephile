#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runnable for getting sync groups between source and transcribed series."""

from __future__ import annotations

from logging import warning
from pprint import pformat

import numpy as np

from scinoephile.audio import AudioSeries, AudioSubtitle
from scinoephile.audio.models import SplitAnswer, SplitQuery
from scinoephile.audio.transcription.cantonese_splitter import CantoneseSplitter
from scinoephile.core import ScinoephileError
from scinoephile.core.pairs import get_pair_strings
from scinoephile.core.synchronization import (
    SyncGroup,
    get_overlap_string,
    get_sync_overlap_matrix,
)


class CantoneseAlignmentOperation:
    def __init__(
        self,
        zhongwen: AudioSeries,
        yuewen: AudioSeries,
        overlap_threshold: float = 0.33,
    ) -> None:
        """Initialize.

        Arguments:
            zhongwen: 中文 subs
            yuewen: 粤文 subs
            overlap_threshold: Threshold for overlap of sync groups
        """
        self._zhongwen = zhongwen
        self._yuewen = yuewen
        self.overlap_threshold = overlap_threshold

        self._overlap = None
        self._scaled_overlap = None
        self._sync_groups = None
        self._yuewen_to_review = None

    def __str__(self):
        """String representation."""
        zhongwen_str, yuewen_str = get_pair_strings(self.zhongwen, self.yuewen)
        string = f"\nMANDARIN:\n{zhongwen_str}"
        string += f"\nCANTONESE:\n{yuewen_str}"
        string += f"\nOVERLAP:\n{get_overlap_string(self.overlap)}"
        string += f"\nSYNC GROUPS:\n{pformat(self.sync_groups, width=120)}"
        string += f"\nTO REVIEW:\n{self.yuewen_to_review}"
        return string

    @property
    def overlap(self) -> np.ndarray:
        if self._overlap is None:
            self._overlap = get_sync_overlap_matrix(self.zhongwen, self.yuewen)
        return self._overlap

    @property
    def scaled_overlap(self) -> np.ndarray:
        if self._scaled_overlap is None:
            scaled_overlap = self.overlap.copy()
            column_maxes = scaled_overlap.max(axis=0)
            column_maxes[column_maxes == 0] = 1
            scaled_overlap /= column_maxes
            self._scaled_overlap = scaled_overlap
        return self._scaled_overlap

    @property
    def sync_groups(self) -> list[SyncGroup]:
        """List of sync groups between 中文 and 粤文; 1-indexed to match SRT."""
        if self._sync_groups is None:
            self._init_sync_groups()
        return self._sync_groups

    @property
    def yuewen(self) -> AudioSeries:
        return self._yuewen

    @yuewen.setter
    def yuewen(self, value: AudioSeries) -> None:
        self._yuewen = value
        self._clear_cache()

    @property
    def yuewen_to_review(self) -> list[int]:
        """List of 粤文 indices to review; 1-indexed to match SRT."""
        if self._yuewen_to_review is None:
            self._init_sync_groups()
        return self._yuewen_to_review

    @property
    def zhongwen(self) -> AudioSeries:
        return self._zhongwen

    @zhongwen.setter
    def zhongwen(self, value: AudioSeries) -> None:
        self._zhongwen = value
        self._clear_cache()

    def _clear_cache(self) -> None:
        """Clear cached values."""
        self._overlap = None
        self._scaled_overlap = None
        self._sync_groups = None
        self._yuewen_to_review = None

    def _init_sync_groups(self):
        """Initialize nascent sync groups and list of 粤文 to review."""
        # Each sync group must be one 中文 and zero or more 粤文.
        nascent_sync_groups = []
        for zw_i1 in range(1, len(self.zhongwen) + 1):  # 1-indexed to match SRT
            nascent_sync_groups.append(([zw_i1], []))

        # For each 粤文, find the corresponding 中文 and add it to the sync group.
        yuewen_to_review = []
        for yw_i in range(len(self.yuewen)):
            rank = np.argsort(self.scaled_overlap[:, yw_i])[::-1]
            yw_overlapping_is = np.where(
                self.scaled_overlap[:, yw_i] > self.overlap_threshold
            )[0]

            yw_i1 = yw_i + 1  # 1-indexed to match SRT
            if len(yw_overlapping_is) == 1:
                yuewen_to_review.append(yw_i1)
            else:
                zw_i = yw_overlapping_is[0]
                nascent_sync_groups[zw_i][1].append(yw_i1)

        self._sync_groups = nascent_sync_groups
        self._yuewen_to_review = yuewen_to_review

    def apply_split_answer(
        self, one_zw_i: int, two_zw_i: int, yw_i: int, answer: SplitAnswer
    ):
        if not answer.one_yuewen_to_append and not answer.two_yuewen_to_prepend:
            raise ScinoephileError()
        if answer.one_yuewen_to_append and not answer.two_yuewen_to_prepend:
            self.sync_groups[one_zw_i][1].append(answer.one_yuewen_to_append)
        if not answer.one_yuewen_to_append and answer.two_yuewen_to_prepend:
            self.sync_groups[two_zw_i][1].insert(0, answer.two_yuewen_to_prepend)
        # Split yuewen event into two parts
        # Need to make sure timings make it here.
        print()
        sub_to_split = self.yuewen.events[yw_i]
        # Figure out where subtitle 1 should start
        one_start = sub_to_split.start
        # Figure out where subtitle 1 should end
        split_i = len(answer.one_yuewen_to_append)
        one_end = sub_to_split.segment.words[split_i].end

        # Figure out where subtitle 2 should start
        two_start = sub_to_split.segment.words[split_i].start
        # Figure out where subtitle 2 should end
        two_end = sub_to_split.end

        # Need to split segment as well
        one = AudioSubtitle(
            start=one_start,
            end=one_end,
            text=answer.one_yuewen_to_append,
            # segment
        )
        two = AudioSubtitle(
            start=two_start,
            end=two_end,
            text=answer.two_yuewen_to_prepend,
            # segment
        )
        updated_series = AudioSeries()
        updated_events = self.yuewen.events[:yw_i]
        updated_events.append(one)
        updated_events.append(two)
        updated_events.extend(self.yuewen.events[yw_i + 1 :])
        updated_series.events = updated_events
        self.yuewen = updated_series

    def get_split_query(self, one_zw_i: int, two_zw_i: int, yw_i: int) -> SplitQuery:
        if yw_i not in self.yuewen_to_review:
            raise ScinoephileError(
                f"yw_i={yw_i} not in yuewen_to_review: {self.yuewen_to_review}"
            )
        one_yw_is = [i - 1 for i in self.sync_groups[one_zw_i][1]]
        two_yw_is = [i - 1 for i in self.sync_groups[two_zw_i][1]]
        return SplitQuery(
            one_zhongwen=self.zhongwen.events[one_zw_i].text,
            one_yuewen_start="".join([self.yuewen.events[i].text for i in one_yw_is]),
            two_zhongwen=self.zhongwen.events[two_zw_i].text,
            two_yuewen_end="".join([self.yuewen.events[i].text for i in two_yw_is]),
            yuewen_to_split=self.yuewen.events[yw_i].text,
        )


class CantoneseAligner:
    """Runnable for getting sync groups between source and transcribed series."""

    def __init__(self, splitter: CantoneseSplitter) -> None:
        """Initialize.

        Arguments:
            splitter: Cantonese splitter.
        """
        self.splitter = splitter

    def group(
        self, zhongwen_subs: AudioSeries, yuewen_subs: AudioSeries
    ) -> CantoneseAlignmentOperation:
        op = CantoneseAlignmentOperation(zhongwen_subs, yuewen_subs)
        print(op)
        if len(op.yuewen_to_review) == 0:
            print("No 粤文 to review.")
            return op
        self._review(op)
        return op

    def _review(self, op: CantoneseAlignmentOperation):
        for yw_i1 in op.yuewen_to_review:  # 1-indexed to match SRT
            yw_i = yw_i1 - 1
            indexes_over_threshold = np.where(
                op.scaled_overlap[:, yw_i] > op.overlap_threshold
            )[0]

            if len(indexes_over_threshold) == 2:
                zw_one_i, zw_two_i = indexes_over_threshold
                query = op.get_split_query(zw_one_i, zw_two_i, yw_i1)
                print(query)
                answer = self.splitter(query)
            else:
                warning(
                    f"Unexpected number of indexes over threshold for yw_i={yw_i1}: "
                    f"{len(indexes_over_threshold)}"
                )
                print()
