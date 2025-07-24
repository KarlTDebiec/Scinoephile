#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Aligns transcribed 粤文 subs with official 中文 subs."""

from __future__ import annotations

from logging import info

import numpy as np

from scinoephile.audio import AudioSeries, AudioSubtitle
from scinoephile.audio.cantonese.cantonese_alignment import CantoneseAlignment
from scinoephile.audio.cantonese.cantonese_merger import CantoneseMerger
from scinoephile.audio.cantonese.cantonese_proofer import CantoneseProofer
from scinoephile.audio.cantonese.cantonese_shifter import CantoneseShifter
from scinoephile.audio.cantonese.cantonese_splitter import CantoneseSplitter
from scinoephile.audio.transcription import get_segment_merged
from scinoephile.core import ScinoephileError


class CantoneseAligner:
    """Aligns transcribed 粤文 subs with official 中文 subs."""

    def __init__(
        self,
        merger: CantoneseMerger,
        proofer: CantoneseProofer,
        shifter: CantoneseShifter,
        splitter: CantoneseSplitter,
    ) -> None:
        """Initialize.

        Arguments:
            splitter: Cantonese splitter
            merger: Cantonese merger
            proofer: Cantonese proofer
        """
        self.merger = merger
        """Merges transcribed 粤文 text to match 中文 text punctuation and spacing."""
        self.proofer = proofer
        """Proofreads 粤文 text based on the corresponding 中文."""
        self.shifter = shifter
        """Shifts 粤文 text between adjacent subtitles based on corresponding 中文."""
        self.splitter = splitter
        """Splits 粤文 text between two nascent 粤文 texts based on corresponding 中文."""

    def align(
        self, zhongwen_subs: AudioSeries, yuewen_subs: AudioSeries
    ) -> CantoneseAlignment:
        """Align 粤文 subtitles with 中文 subtitles.

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
        alignment = CantoneseAlignment(zhongwen_subs, yuewen_subs)

        # Shift 粤文 subtitles to match 中文 subtitles
        need_to_run_shift = True
        while need_to_run_shift:
            # Split 粤文 subtitles that overlap with two 中文 subtitles
            iteration = 0
            while len(alignment.yuewen_to_review) > 0:
                info(f"\nITERATION {iteration}")
                info(alignment)
                self._split(alignment)
                iteration += 1

            need_to_run_shift = self._shift(alignment)

        # TODO: Identify partnerless 中文 subtitles and prompt LLM

        # Merge 粤文 subtitles to match 中文 punctuation and spacing
        self._merge(alignment)

        # Proofread 粤文 subtitles based on corresponding 中文 subtitles
        self._proofread(alignment)

        # Return final alignment
        info(f"\nFINAL RESULT:\n{alignment}")
        return alignment

    def _split(self, alignment: CantoneseAlignment) -> None:
        """Split 粤文 subs.

        Arguments:
            alignment: Nascent alignment
        """
        yw_i = alignment.yuewen_to_review[0]
        zw_is = np.where(alignment.scaled_overlap[:, yw_i] > alignment.cutoff)[0]

        if len(zw_is) != 2:
            raise ScinoephileError(
                f"Situation not yet supported: {len(zw_is)} zhongwen subs "
                f"for yw_i={yw_i}:\n{alignment}"
            )

        one_zw_i, two_zw_i = zw_is
        query = alignment.get_split_query(one_zw_i, two_zw_i, yw_i)
        answer = self.splitter(query)
        alignment.apply_split(one_zw_i, two_zw_i, yw_i, answer)

    def _merge(self, alignment: CantoneseAlignment) -> None:
        """Merge 粤文 subs.

        Arguments:
            alignment: Nascent alignment
        """
        updated_yuewen_events = []
        for sync_group in alignment.sync_groups:
            zw_is, yw_is = sync_group
            zw_i = zw_is[0]
            if len(yw_is) == 0:
                continue
            query = alignment.get_merge_query(zw_i, yw_is)
            answer = self.merger(query)

            updated_yuewen_events.append(
                AudioSubtitle(
                    start=alignment.yuewen[yw_is[0]].start,
                    end=alignment.yuewen[yw_is[-1]].end,
                    text=answer.yuewen_merged,
                    segment=get_segment_merged(
                        [alignment.yuewen[i].segment for i in yw_is]
                    ),
                )
            )
        updated_yuewen = AudioSeries()
        updated_yuewen.events = updated_yuewen_events
        alignment.merged = True
        alignment.yuewen = updated_yuewen

    def _shift(self, alignment) -> bool:
        """Shift 粤文 text.

        Arguments:
            alignment: Nascent alignment
        """
        updated_yuewen_events = []
        for i in range(len(alignment.sync_groups) - 1):
            one_sync_group = alignment.sync_groups[i]
            two_sync_group = alignment.sync_groups[i + 1]
            if len(one_sync_group[0]) != 1:
                raise ScinoephileError(
                    f"Sync group not as expected:\n{one_sync_group}\n{alignment}"
                )
            if len(two_sync_group[0]) != 1:
                raise ScinoephileError(
                    f"Sync group not as expected:\n{two_sync_group}\n{alignment}"
                )
            one_zw_i = one_sync_group[0][0]
            one_yw_is = one_sync_group[1]
            two_zw_i = two_sync_group[0][0]
            two_yw_is = two_sync_group[1]
            if len(one_yw_is) == 0 and len(two_yw_is) == 0:
                continue
            query = alignment.get_shift_query(one_zw_i, two_zw_i, one_yw_is, two_yw_is)
            answer = self.shifter(query)
            if (
                query.one_yuewen == answer.one_yuewen_shifted
                and query.two_yuewen == answer.two_yuewen_shifted
            ):
                continue
            need_to_restart = alignment.apply_shift(
                one_zw_i, two_zw_i, one_yw_is, two_yw_is, query, answer
            )
            if need_to_restart:
                info("Need to restart shifting")
                return True
        return False

    def _proofread(self, alignment: CantoneseAlignment) -> None:
        """Proofread 粤文 text.

        Arguments:
            alignment: Nascent alignment
        """
        updated_yuewen_events = []
        for sync_group in alignment.sync_groups:
            if (
                len(sync_group[0]) != 1
                or len(sync_group[1]) != 1
                or sync_group[0][0] != sync_group[1][0]
            ):
                raise ScinoephileError(
                    f"Sync group not as expected:\n{sync_group}\n{alignment}"
                )
            i = sync_group[0][0]
            query = alignment.get_proofread_query(i)
            answer = self.proofer(query)
            updated_yuewen_events.append(
                AudioSubtitle(
                    start=alignment.yuewen[i].start,
                    end=alignment.yuewen[i].end,
                    text=answer.yuewen_proofread,
                    segment=alignment.yuewen[i].segment,
                )
            )
        updated_yuewen = AudioSeries()
        updated_yuewen.events = updated_yuewen_events
        alignment.yuewen = updated_yuewen
