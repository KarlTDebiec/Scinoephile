#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Aligns transcribed 粤文 subs with official 中文 subs."""

from __future__ import annotations

from logging import info

import numpy as np

from scinoephile.audio import AudioSeries, AudioSubtitle
from scinoephile.audio.cantonese.cantonese_alignment import CantoneseAlignment
from scinoephile.audio.cantonese.cantonese_merger import CantoneseMerger
from scinoephile.audio.cantonese.cantonese_proofreader import CantoneseProofreader
from scinoephile.audio.cantonese.cantonese_splitter import CantoneseSplitter
from scinoephile.audio.transcription import get_merged_segment
from scinoephile.core import ScinoephileError


class CantoneseAligner:
    """Aligns transcribed 粤文 subs with official 中文 subs."""

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
        """Splits 粤文 text between two nascent 粤文 texts based on corresponding 中文."""
        self.merger = merger
        """Merges transcribed 粤文 text to match 中文 text punctuation and spacing."""
        self.proofreader = proofreader
        """Proofreads 粤文 text based on the corresponding 中文."""

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

        # Split 粤文 subtitles that overlap with two 中文 subtitles
        iteration = 0
        while len(alignment.yuewen_to_review) > 0:
            info(f"\nITERATION {iteration}")
            info(alignment)
            self._split(alignment)
            iteration += 1

        # TODO: Identify large differences in length between 中文 and 粤文 and prompt LLM
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
        query = alignment._get_split_query(one_zw_i, two_zw_i, yw_i)
        answer = self.splitter(query)
        alignment._apply_split(one_zw_i, two_zw_i, yw_i, answer)

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
            query = alignment._get_merge_query(zw_i, yw_is)
            answer = self.merger(query)

            updated_yuewen_events.append(
                AudioSubtitle(
                    start=alignment.yuewen[yw_is[0]].start,
                    end=alignment.yuewen[yw_is[-1]].end,
                    text=answer.yuewen_merged,
                    segment=get_merged_segment(
                        [alignment.yuewen[i].segment for i in yw_is]
                    ),
                )
            )
        updated_yuewen = AudioSeries()
        updated_yuewen.events = updated_yuewen_events
        alignment.yuewen = updated_yuewen

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
            query = alignment._get_proofread_query(i)
            answer = self.proofreader(query)
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
