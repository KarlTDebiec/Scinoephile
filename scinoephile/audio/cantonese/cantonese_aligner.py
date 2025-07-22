#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runnable for getting sync groups between source and transcribed series."""

from __future__ import annotations

from logging import info
from pprint import pformat

import numpy as np

from scinoephile.audio import AudioSeries, AudioSubtitle
from scinoephile.audio.cantonese.cantonese_merger import CantoneseMerger
from scinoephile.audio.cantonese.cantonese_proofreader import CantoneseProofreader
from scinoephile.audio.cantonese.cantonese_splitter import CantoneseSplitter
from scinoephile.audio.cantonese.models import (
    MergeQuery,
    ProofreadQuery,
    SplitAnswer,
    SplitQuery,
)
from scinoephile.audio.models import (
    TranscribedSegment,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.pairs import get_pair_strings
from scinoephile.core.synchronization import (
    SyncGroup,
    get_overlap_string,
    get_sync_groups_string,
    get_sync_overlap_matrix,
)


class CantoneseAlignmentOperation:
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

    def apply_split_answer(
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

    def get_merge_query(self, zw_i: int, yw_is: list[int]) -> MergeQuery:
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

    def get_split_query(self, one_zw_i: int, two_zw_i: int, yw_i: int) -> SplitQuery:
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

    def get_proofread_query(self, i: int) -> ProofreadQuery:
        """Get proofread query for given 中文/粤文 index.

        Arguments:
            i: Index of 中文 and 粤文 sub to proofread
        Returns:
            Query for proofreading 粤文
        """
        return ProofreadQuery(
            zhongwen=self.zhongwen[i].text,
            yuewen=self.yuewen[i].text,
        )


class CantoneseAligner:
    """Runnable for getting sync groups between source and transcribed series."""

    def __init__(
        self,
        splitter: CantoneseSplitter,
        merger: CantoneseMerger,
        proofreader: CantoneseProofreader,
    ) -> None:
        """Initialize.

        Arguments:
            splitter: Cantonese splitter
            merger: Cantonese merger
            proofreader: Cantonese proofreader
        """
        self.splitter = splitter
        self.merger = merger
        self.proofreader = proofreader

    def group(
        self, zhongwen_subs: AudioSeries, yuewen_subs: AudioSeries
    ) -> CantoneseAlignmentOperation:
        """Reviews 粤文 subtitles to align with 中文 subtitles.

        Presently, this does the following:
          * Assigns 粤文 subtitles to sync groups with 中文 subtitles based on overlap
          * If a 粤文 subtitle overlaps with two 中文 subtitles, asks LLM to distribute
          * At the end of this each sync group should have one 中文 subtitle and
          * zero or more 粤文 subtitles
          * Merges 粤文 subtitles using LLM to match 中文 punctuation and spacing
          * Proofreads 粤文 subtitles using LLM
        It needs to also do the following:
        * If there is a discrepancy in the length of the 中文 and concatenated 粤文
          subtitles, prompt LLM with known one 中文 and two 中文 subtitles and ask
          if 粤文 should be shifted.
        * If a 中文 subtitle has no partner 粤文 subtitle, prompt LLM with preceding
          and following 粤文 subtitles and ask if they should be shifted.
        """
        op = CantoneseAlignmentOperation(zhongwen_subs, yuewen_subs)
        iteration = 0
        while len(op.yuewen_to_review) > 0:
            info(f"\nITERATION {iteration}")
            info(op)
            self._split(op)
            iteration += 1
        self._merge(op)
        self._proofread(op)
        info(f"\nFINAL RESULT:\n{op}")
        return op

    def _split(self, op: CantoneseAlignmentOperation) -> None:
        yw_i = op.yuewen_to_review[0]
        zw_is = np.where(op.scaled_overlap[:, yw_i] > op.cutoff)[0]

        if len(zw_is) != 2:
            raise ScinoephileError(
                f"Situation not yet supported: {len(zw_is)} zhongwen subs "
                f"for yw_i={yw_i}:\n{op}"
            )

        one_zw_i, two_zw_i = zw_is
        query = op.get_split_query(one_zw_i, two_zw_i, yw_i)
        answer = self.splitter(query)
        op.apply_split_answer(one_zw_i, two_zw_i, yw_i, answer)

    def _merge(self, op: CantoneseAlignmentOperation) -> None:
        """Merge 粤文 text to match 中文 text punctuation and spacing."""
        updated_yuewen_events = []
        for sync_group in op.sync_groups:
            zw_is, yw_is = sync_group
            zw_i = zw_is[0]
            if len(yw_is) == 0:
                continue
            query = op.get_merge_query(zw_i, yw_is)
            answer = self.merger(query)

            updated_yuewen_events.append(
                AudioSubtitle(
                    start=op.yuewen[yw_is[0]].start,
                    end=op.yuewen[yw_is[-1]].end,
                    text=answer.yuewen_merged,
                    segment=self.get_merged_segment(
                        [op.yuewen[i].segment for i in yw_is]
                    ),
                )
            )
        updated_yuewen = AudioSeries()
        updated_yuewen.events = updated_yuewen_events
        op.yuewen = updated_yuewen

    def _proofread(self, op: CantoneseAlignmentOperation) -> None:
        """Proofread 粤文 text."""
        updated_yuewen_events = []
        for sync_group in op.sync_groups:
            if (
                len(sync_group[0]) != 1
                or len(sync_group[1]) != 1
                or sync_group[0][0] != sync_group[1][0]
            ):
                raise ScinoephileError(
                    f"Sync group not as expected:\n{sync_group}\n{op}"
                )
            i = sync_group[0][0]
            query = op.get_proofread_query(i)
            answer = self.proofreader(query)
            updated_yuewen_events.append(
                AudioSubtitle(
                    start=op.yuewen[i].start,
                    end=op.yuewen[i].end,
                    text=answer.yuewen_proofread,
                    segment=op.yuewen[i].segment,
                )
            )
        updated_yuewen = AudioSeries()
        updated_yuewen.events = updated_yuewen_events
        op.yuewen = updated_yuewen

    @staticmethod
    def get_merged_segment(segments: list[TranscribedSegment]) -> TranscribedSegment:
        """Merge transcribed segments into a single segment.

        Arguments:
            segments: Segments to merge
        Returns:
            Merged segment
        """
        if len(segments) == 1:
            return segments[0]
        return TranscribedSegment(
            id=segments[0].id,
            seek=segments[0].seek,
            start=segments[0].start,
            end=segments[-1].end,
            text="".join([s.text for s in segments]),
            words=[word for segment in segments for word in segment.words],
        )
