#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runnable for getting sync groups between source and transcribed series."""

from __future__ import annotations

from pprint import pformat

import numpy as np

from scinoephile.audio import AudioSeries, AudioSubtitle
from scinoephile.audio.cantonese.models import (
    MergeQuery,
    ProofreadQuery,
    SplitAnswer,
    SplitQuery,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.pairs import get_pair_strings
from scinoephile.core.synchronization import (
    SyncGroup,
    get_overlap_string,
    get_sync_groups_string,
    get_sync_overlap_matrix,
)


class CantoneseAlignment:
    def __init__(
        self,
        zhongwen: AudioSeries,
        yuewen: AudioSeries,
        cutoff: float = 0.33,
    ) -> None:
        """Initialize.

        Arguments:
            zhongwen: 中文 subs
            yuewen: 粤文 subs
            cutoff: Cutoff for overlap between 中文 and 粤文 for inclusion in sync group
        """
        self._zhongwen = zhongwen
        self._yuewen = yuewen
        self.cutoff = cutoff

        self._overlap = None
        self._scaled_overlap = None
        self._sync_groups = None
        self._yuewen_to_review = None

    def __str__(self):
        """String representation."""
        zhongwen_str, yuewen_str = get_pair_strings(self.zhongwen, self.yuewen)
        string = f"MANDARIN:\n{zhongwen_str}"
        string += f"\nCANTONESE:\n{yuewen_str}"
        string += f"\nOVERLAP:\n{get_overlap_string(self.overlap)}"
        string += f"\nSYNC GROUPS:\n{get_sync_groups_string(self.sync_groups)}"
        string += f"\nTO REVIEW:\n{pformat([i + 1 for i in self.yuewen_to_review])}"
        return string

    @property
    def overlap(self) -> np.ndarray:
        """Overlap matrix between 中文 and 粤文."""
        if self._overlap is None:
            self._overlap = get_sync_overlap_matrix(self.zhongwen, self.yuewen)
        return self._overlap

    @property
    def scaled_overlap(self) -> np.ndarray:
        """Scaled overlap matrix between 中文 and 粤文."""
        if self._scaled_overlap is None:
            scaled_overlap = self.overlap.copy()
            column_maxes = scaled_overlap.max(axis=0)
            column_maxes[column_maxes == 0] = 1
            scaled_overlap /= column_maxes
            self._scaled_overlap = scaled_overlap
        return self._scaled_overlap

    @property
    def sync_groups(self) -> list[SyncGroup]:
        """Sync groups between 中文 and 粤文."""
        if self._sync_groups is None:
            self._init_sync_groups()
        return self._sync_groups

    @property
    def yuewen(self) -> AudioSeries:
        """粤文 series."""
        return self._yuewen

    @yuewen.setter
    def yuewen(self, value: AudioSeries) -> None:
        """Set 粤文 series and clear cached values.

        Arguments:
            value: 粤文 series
        """
        self._yuewen = value
        self._clear_cache()

    @property
    def yuewen_to_review(self) -> list[int]:
        """粤文 indices in need of review."""
        if self._yuewen_to_review is None:
            self._init_sync_groups()
        return self._yuewen_to_review

    @property
    def zhongwen(self) -> AudioSeries:
        """中文 series."""
        return self._zhongwen

    @zhongwen.setter
    def zhongwen(self, value: AudioSeries) -> None:
        """Set 中文 series and clear cached values.

        Arguments:
            value: 中文 series
        """
        self._zhongwen = value
        self._clear_cache()

    def _apply_split(
        self, one_zw_i: int, two_zw_i: int, yw_i: int, answer: SplitAnswer
    ):
        if not answer.one_yuewen_to_append and not answer.two_yuewen_to_prepend:
            raise ScinoephileError()
        if answer.one_yuewen_to_append and not answer.two_yuewen_to_prepend:
            self.sync_groups[one_zw_i][1].append(yw_i)
            self.yuewen_to_review.remove(yw_i)
            return
        if not answer.one_yuewen_to_append and answer.two_yuewen_to_prepend:
            self.sync_groups[two_zw_i][1].insert(0, yw_i)
            self.yuewen_to_review.remove(yw_i)
            return
        # Split yuewen event into two parts
        # Need to make sure timings make it here.
        print()
        sub_to_split = self.yuewen[yw_i]
        # Figure out where subtitle 1 should start
        one_start = sub_to_split.start
        # Figure out where subtitle 1 should end
        split_i = len(answer.one_yuewen_to_append) - 1
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
            # TODO: segment
        )
        two = AudioSubtitle(
            start=two_start,
            end=two_end,
            text=answer.two_yuewen_to_prepend,
            # TODO: segment
        )
        updated_series = AudioSeries()
        updated_events = self.yuewen[:yw_i]
        updated_events.append(one)
        updated_events.append(two)
        updated_events.extend(self.yuewen[yw_i + 1 :])
        updated_series.events = updated_events
        self.yuewen = updated_series

    def _clear_cache(self) -> None:
        """Clear cached values."""
        self._overlap = None
        self._scaled_overlap = None
        self._sync_groups = None
        self._yuewen_to_review = None

    def _get_merge_query(self, zw_i: int, yw_is: list[int]) -> MergeQuery:
        """Get merge query for given indices.

        Arguments:
            zw_i: Index of 中文 sub
            yw_is: Indices of 粤文 subs to merge
        Returns:
            Query for merging 粤文
        """
        return MergeQuery(
            zhongwen=self.zhongwen[zw_i].text,
            yuewen_to_merge=[self.yuewen[i].text for i in yw_is],
        )

    def _get_split_query(self, one_zw_i: int, two_zw_i: int, yw_i: int) -> SplitQuery:
        """Get split query for given indices.

        Arguments:
            one_zw_i: Index of 中文 sub one
            two_zw_i: Index of 中文 sub two
            yw_i: Index of 粤文 sub to split
        Returns:
            Query for splitting 粤文
        """
        if yw_i not in self.yuewen_to_review:
            raise ScinoephileError(
                f"yw_i={yw_i} not in yuewen_to_review: {self.yuewen_to_review}"
            )
        one_yw_is = [i for i in self.sync_groups[one_zw_i][1]]
        two_yw_is = [i for i in self.sync_groups[two_zw_i][1]]
        return SplitQuery(
            one_zhongwen=self.zhongwen[one_zw_i].text,
            one_yuewen_start="".join([self.yuewen[i].text for i in one_yw_is]),
            two_zhongwen=self.zhongwen[two_zw_i].text,
            two_yuewen_end="".join([self.yuewen[i].text for i in two_yw_is]),
            yuewen_to_split=self.yuewen[yw_i].text,
        )

    def _get_proofread_query(self, i: int) -> ProofreadQuery:
        """Get proofread query for given 中文/粤文 index.

        Arguments:
            i: Index of 中文/粤文 sub to proofread
        Returns:
            Query for proofreading 粤文
        """
        return ProofreadQuery(
            zhongwen=self.zhongwen[i].text,
            yuewen=self.yuewen[i].text,
        )

    def _init_sync_groups(self):
        """Initialize nascent sync groups and list of 粤文 to review."""
        # Each sync group must be one 中文 and zero or more 粤文.
        nascent_sync_groups = []
        for zw_i in range(len(self.zhongwen)):
            nascent_sync_groups.append(([zw_i], []))

        # For each 粤文, find the corresponding 中文 and add it to the sync group.
        yuewen_to_review = []
        for yw_i in range(len(self.yuewen)):
            rank = np.argsort(self.scaled_overlap[:, yw_i])[::-1]
            zw_is = np.where(self.scaled_overlap[:, yw_i] > self.cutoff)[0]

            if len(zw_is) == 1:
                nascent_sync_groups[zw_is[0]][1].append(yw_i)
            else:
                yuewen_to_review.append(yw_i)

        self._sync_groups = nascent_sync_groups
        self._yuewen_to_review = yuewen_to_review
