#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Aligns transcribed 粤文 subs with official 中文 subs."""

from __future__ import annotations

from copy import deepcopy
from logging import error, info

import numpy as np
from pydantic import ValidationError

from scinoephile.audio import (
    AudioSeries,
    get_series_with_sub_split_at_idx,
    get_sub_merged,
)
from scinoephile.audio.cantonese.alignment.alignment import Alignment
from scinoephile.audio.cantonese.alignment.models import (
    get_review_models,
    get_translate_models,
)
from scinoephile.audio.cantonese.alignment.queries import (
    get_distribute_query,
    get_merge_query,
    get_proof_query,
    get_review_query,
    get_shift_query,
    get_translate_query,
)
from scinoephile.audio.cantonese.distribution import DistributeAnswer, Distributor
from scinoephile.audio.cantonese.merging import MergeAnswer, Merger, MergeTestCase
from scinoephile.audio.cantonese.proofing import Proofer
from scinoephile.audio.cantonese.review import Reviewer
from scinoephile.audio.cantonese.shifting import ShiftAnswer, Shifter, ShiftQuery
from scinoephile.audio.cantonese.translation import Translator
from scinoephile.core import ScinoephileError
from scinoephile.core.synchronization import get_sync_groups_string
from scinoephile.core.text import remove_punc_and_whitespace


class Aligner:
    """Aligns transcribed 粤文 subs with official 中文 subs."""

    def __init__(
        self,
        distributor: Distributor,
        shifter: Shifter,
        merger: Merger,
        proofer: Proofer,
        translator: Translator,
        reviewer: Reviewer,
    ):
        """Initialize.

        Arguments:
            distributor: Cantonese splitter
            shifter: Cantonese shifter
            merger: Cantonese merger
            proofer: Cantonese proofer
            translator: Cantonese translator
            reviewer: Cantonese reviewer
        """
        self.merger = merger
        """Merges transcribed 粤文 text based on corresponding 中文."""
        self.proofer = proofer
        """Proofreads 粤文 text based on the corresponding 中文."""
        self.shifter = shifter
        """Shifts 粤文 text between adjacent subtitles based on corresponding 中文."""
        self.distributor = distributor
        """Distributes 粤文 text based on corresponding 中文."""
        self.translator = translator
        """Translates 粤文 text based on corresponding 中文."""
        self.reviewer = reviewer
        """Reviews 粤文 text based on corresponding 中文 subtitles."""

    async def align(
        self, zhongwen_subs: AudioSeries, yuewen_subs: AudioSeries
    ) -> Alignment:
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
        alignment = Alignment(zhongwen_subs, yuewen_subs)

        # Distribute and shift 粤文 subtitles to match 中文 subtitles
        # Each round of this loop first distributes 粤文 subtitles that overlap with
        # multiple 中文 subtitles, and then shifts 粤文 subtitle text that remains
        # misaligned after distribution.
        # Distribution may involve simply assigning a 粤文 subtitle to one of the two
        # 中文 subtitles with which it partially overlaps, or it may involve splitting
        # the 粤文 subtitle into two 粤文 subtitles, to be paired with the two 中文
        # subtitles. Each time a 粤文 subtitle is split, distribution is implicitly
        # restarted by clearing the sync group override; via the on-the-fly calculation
        # of the overlap matrix, sync_groups, and 粤文 to review.
        # Distribution stops automatically when all 粤文 subtitles have been assigned
        # to sync groups, i.e., when there are no more 粤文 subtitles to distribute.
        # Similarly, shifting may involve simply shifting a whole 粤文 subtitle from one
        # sync group to another, or it may involve splitting a 粤文 subtitle into two
        # 粤文 subtitles. As with distribution, each time a 粤文 subtitle is split,
        # shifting is implicitly restarted by clearing the sync group override.
        distribution_and_shifting_in_progress = True
        iteration = 0
        while distribution_and_shifting_in_progress:
            # First distribute 粤文 subtitles that overlap with multiple 中文 subtitles
            await self._distribute(alignment)

            # Then shift 粤文 subtitles that remain misaligned after distribution
            distribution_and_shifting_in_progress = await self._shift(alignment)
            iteration += 1

        # Merge 粤文 subtitles to match 中文 punctuation and spacing
        await self._merge(alignment)

        # Proofread 粤文 subtitles based on corresponding 中文 subtitles
        await self._proof(alignment)

        # Translate 中文 subtitles for which no 粤文 was transcribed
        await self._translate(alignment)

        # Review 粤文 subtitles
        await self._review(alignment)

        # Return final alignment
        return alignment

    async def _distribute(self, alignment: Alignment):
        """Distribute 粤文 subs.

        Arguments:
            alignment: Nascent alignment
        """
        iteration = 0
        while alignment.yuewen_to_distribute:
            info(f"\nITERATION {iteration}")
            info(alignment)
            await self._distribute_one(alignment)
            iteration += 1

    async def _distribute_one(self, alignment: Alignment):
        """Split 粤文 subs.

        Arguments:
            alignment: Nascent alignment
        """
        # Get sync group and yuewen indexes
        yw_idx = alignment.yuewen_to_distribute[0]
        zw_idxs = np.where(alignment.scaled_overlap[:, yw_idx] > 0.33)[0]

        # Case: 粤文 overlaps with nothing
        # Action: just remove it
        if len(zw_idxs) == 0:
            yw = AudioSeries(audio=alignment.yuewen.audio)
            yw.events = (
                alignment.yuewen.events[:yw_idx] + alignment.yuewen.events[yw_idx + 1 :]
            )
            alignment.yuewen = yw
            alignment._sync_groups_override = None
            return

        # Case: 粤文 overlaps with more than 2 中文
        # Action: Raise; this has not yet been encountered
        if len(zw_idxs) != 2:
            raise ScinoephileError(
                f"Situation not supported: 粤文 subtitle {yw_idx} overlaps with "
                f"{len(zw_idxs)} sync groups: {zw_idxs.tolist()}.\n{alignment}"
            )

        # Case: 粤文 overlaps with two sync groups
        # Action: Query to distribute 粤文 between sync groups
        sg_1_idx, sg_2_idx = zw_idxs
        query = get_distribute_query(alignment, sg_1_idx, sg_2_idx, yw_idx)
        try:
            answer = await self.distributor.call(query)
        except ValidationError as exc:
            answer = DistributeAnswer(
                yuewen_1_to_append=query.yuewen_to_distribute,
                yuewen_2_to_prepend="",
            )
            test_case = query.to_test_case(answer)
            error(
                f"Error distributing 粤文 subtitle {yw_idx} between sync groups "
                f"{sg_1_idx} and {sg_2_idx}; distributing to first group.\n"
                f"Test case:\n"
                f"{test_case.source_str}\n"
                f"Exception:\n{exc}\n"
            )

        # Case: 粤文 should be assigned to sync group 1
        # Action: Append 粤文 to sync group 1 and set override
        if answer.yuewen_1_to_append and not answer.yuewen_2_to_prepend:
            nascent_sg = deepcopy(alignment.sync_groups)
            nascent_sg[sg_1_idx][1].append(yw_idx)
            alignment._sync_groups_override = nascent_sg
            return

        # Case: 粤文 should be assigned to sync group 2
        # Action: Prepend 粤文 to sync group 2 and set override
        if not answer.yuewen_1_to_append and answer.yuewen_2_to_prepend:
            nascent_sg = deepcopy(alignment.sync_groups)
            nascent_sg[sg_2_idx][1].insert(0, yw_idx)
            alignment._sync_groups_override = nascent_sg
            return

        # Case: 粤文 should be split between two sync groups
        # Action: Split 粤文 as specified in the answer; clear sync group override
        alignment.yuewen = get_series_with_sub_split_at_idx(
            alignment.yuewen, yw_idx, len(answer.yuewen_1_to_append)
        )
        alignment._sync_groups_override = None

    async def _shift(self, alignment) -> bool:
        """Shift 粤文 text.

        Arguments:
            alignment: Nascent alignment
        """
        for sg_1_idx in range(len(alignment.sync_groups) - 1):
            # Run query
            query = get_shift_query(alignment, sg_1_idx)
            if query is None:
                info(f"Skipping sync groups {sg_1_idx} and {sg_1_idx + 1} with no 粤文")
                continue
            # TODO: try/expect and return original 粤文 on error; not yet encountered
            answer = await self.shifter.call(query)

            # If there is no change, continue
            if (
                query.yuewen_1 == answer.yuewen_1_shifted
                and query.yuewen_2 == answer.yuewen_2_shifted
            ):
                continue
            if self._shift_one(alignment, sg_1_idx, query, answer):
                return True
        return False

    def _shift_one(
        self,
        alignment: Alignment,
        sg_1_idx: int,
        query: ShiftQuery,
        answer: ShiftAnswer,
    ) -> bool:
        # Get sync group 1
        if sg_1_idx < 0 or sg_1_idx >= len(alignment.sync_groups):
            raise ScinoephileError(
                f"Invalid sync group index {sg_1_idx} "
                f"for alignment with {len(alignment.sync_groups)} sync groups."
            )
        sg_1 = alignment.sync_groups[sg_1_idx]

        # Get sync group 2
        sg_2_idx = sg_1_idx + 1
        if sg_2_idx < 0 or sg_2_idx >= len(alignment.sync_groups):
            raise ScinoephileError(
                f"Invalid sync group index {sg_2_idx} "
                f"for alignment with {len(alignment.sync_groups)} sync groups."
            )
        sg_2 = alignment.sync_groups[sg_2_idx]

        # Get 粤文
        yw_1_idxs = sg_1[1]
        yw_2_idxs = sg_2[1]
        yw_1 = query.yuewen_1
        yw_2 = query.yuewen_2
        yw_1_shifted = answer.yuewen_1_shifted
        yw_2_shifted = answer.yuewen_2_shifted

        # Shift 粤文
        nascent_sg = deepcopy(alignment.sync_groups)

        # Case: 粤文 text needs to be shifted from 中文 2 to 中文 1
        if len(yw_1) < len(yw_1_shifted):
            # Calculate the number of characters we need to shift from 2 to 1
            text_to_shift_from_2_to_1 = yw_1_shifted[len(yw_1) :]
            n_chars_remaining_to_shift = len(text_to_shift_from_2_to_1)

            # Loop over subtitles currently in sync group 2
            for yw_2_idx in yw_2_idxs:
                yw = alignment.yuewen[yw_2_idx]

                # Case: A sub in 粤文 2 overlaps partialy with 中文 1 and 2
                # Action: Split sub into two subs, and return True to indicate that
                #   shifting must be restarted
                if len(yw.text) > n_chars_remaining_to_shift:
                    alignment.yuewen = get_series_with_sub_split_at_idx(
                        alignment.yuewen, yw_2_idx, n_chars_remaining_to_shift
                    )
                    # Must restart shifting after splitting a sub
                    alignment._sync_groups_override = None
                    return True

                # Case: A sub in 粤文 2 overlaps with 中文 1 and not 中文 2
                # Action: Shift sub from sync group 2 to 1
                nascent_sg[sg_1_idx][1].append(yw_2_idx)
                nascent_sg[sg_2_idx][1].remove(yw_2_idx)
                n_chars_remaining_to_shift -= len(yw.text)

                # Case: We are done shifting
                # Action: Set sync groups and return False to indicate completion
                if n_chars_remaining_to_shift == 0:
                    alignment._sync_groups_override = nascent_sg
                    return False

        # Case: 粤文 text needs to be shifted from 中文 1 to 中文 2
        # Action: Shift 粤文 text from sync group 1 to sync group 2
        if len(yw_2) < len(yw_2_shifted):
            # Calculate the number of characters we need to shift from 1 to 2
            text_to_shift_from_1_to_2 = yw_2_shifted[: len(yw_2_shifted) - len(yw_2)]
            n_chars_remaining_to_shift = len(text_to_shift_from_1_to_2)

            # Loop over subtitles currently in sync group 1
            for yw_1_idx in reversed(yw_1_idxs):
                yw = alignment.yuewen[yw_1_idx]

                # Case: A sub in 粤文 1 overlaps partially with 中文 1 and 2
                # Action: Split sub into two subs, and return True to indicate that
                #   shifting must be restarted
                if len(yw.text) > n_chars_remaining_to_shift:
                    alignment.yuewen = get_series_with_sub_split_at_idx(
                        alignment.yuewen,
                        yw_1_idx,
                        len(yw.text) - n_chars_remaining_to_shift,
                    )
                    # Must restart shifting after splitting a subtitle
                    alignment._sync_groups_override = None
                    return True

                # Case: A sub in 粤文 1 overlaps with 中文 2 and not 中文 1
                # Action: Shift sub from sync group 1 to 2
                nascent_sg[sg_1_idx][1].remove(yw_1_idx)
                nascent_sg[sg_2_idx][1].insert(0, yw_1_idx)
                n_chars_remaining_to_shift -= len(yw.text)

                # Case: We are done shifting
                # Action: Set sync groups and return False to indicate completion
                if n_chars_remaining_to_shift == 0:
                    alignment._sync_groups_override = nascent_sg
                    return False

        raise ScinoephileError(
            f"Unexpected case for Query:\n{query}\n with Answer:\n{answer}\n"
        )

    async def _merge(self, alignment: Alignment):
        """Merge 粤文 subs.

        Arguments:
            alignment: Nascent alignment
        """
        if not alignment.zhongwen_all_assigned_to_sync_groups:
            raise ScinoephileError(
                f"Not all 中文 subtitles are in a sync group:\n"
                f"SYNC GROUPS:\n{get_sync_groups_string(alignment.sync_groups)}"
            )
        if not alignment.yuewen_all_assigned_to_sync_groups:
            raise ScinoephileError(
                f"Not all 粤文 subtitles are in a sync group:\n"
                f"SYNC GROUPS:\n{get_sync_groups_string(alignment.sync_groups)}"
            )

        nascent_yw = AudioSeries(audio=alignment.yuewen.audio)
        nascent_sg = []
        for sg_idx in range(len(alignment.sync_groups)):
            # Get sync group
            sg = alignment.sync_groups[sg_idx]

            # Get 中文
            zw_idxs = sg[0]
            zw_idx = zw_idxs[0]
            zw = alignment.zhongwen[zw_idx]

            # Get 粤文
            yw_idxs = sg[1]
            yws = [alignment.yuewen[yw_i] for yw_i in yw_idxs]

            # If there is no punctuation, whitespace, or ambiguity, just copy over
            if zw.text == remove_punc_and_whitespace(zw.text) and len(yws) == 1:
                # If the 中文 subtitle has no punctuation, and there is only one 粤文
                # subtitle, just copy it over
                yw = yws[0]
                yw.start = zw.start
                yw.end = zw.end
                nascent_yw.append(yw)
                nascent_sg.append(([zw_idx], [len(nascent_yw) - 1]))
                continue

            # Query for 粤文 merge
            query = get_merge_query(alignment, sg_idx)
            if query is None:
                info(f"Skipping sync group {sg_idx} with no 粤文 subtitles")
                nascent_sg.append(([zw_idx], []))
                continue
            try:
                answer = await self.merger.call(query)
            except ValidationError as exc:
                # TODO: Consider how this could be improved
                answer = MergeAnswer(yuewen_merged="".join(query.yuewen_to_merge))
                test_case = MergeTestCase.from_query_and_answer(query, answer)
                error(
                    f"Error merging sync group {sg_idx}; concatenating.\n"
                    f"Test case:\n"
                    f"{test_case.source_str}\n"
                    f"Exception:\n{exc}"
                )
            yw = get_sub_merged(yws, text=answer.yuewen_merged)
            yw.start = zw.start
            yw.end = zw.end

            # Update sync group
            nascent_yw.append(yw)
            yw_idx = len(nascent_yw) - 1
            nascent_sg.append(([zw_idx], [yw_idx]))

        alignment.yuewen = nascent_yw
        alignment._sync_groups_override = nascent_sg

    async def _proof(self, alignment: Alignment):
        """Proofread 粤文 subs.

        Arguments:
            alignment: Nascent alignment
        """
        for sg_idx in range(len(alignment.sync_groups)):
            query = get_proof_query(alignment, sg_idx)
            if query is None:
                info(f"Skipping sync group {sg_idx} with no 粤文 subtitles")
                continue
            answer = await self.proofer.call(query)

            # Get sync group
            sg = alignment.sync_groups[sg_idx]

            # Get 粤文
            yw_idxs = sg[1]
            if len(yw_idxs) != 1:
                raise ScinoephileError(
                    f"Expected one 粤文 subtitle in sync group {sg_idx}, "
                    f"but found {len(yw_idxs)}: {yw_idxs}"
                )
            yw_idx = yw_idxs[0]
            if query.yuewen == answer.yuewen_proofread:
                continue
            alignment.yuewen[yw_idx].text = answer.yuewen_proofread

        nascent_yw = AudioSeries(audio=alignment.yuewen.audio)
        nascent_sg = []
        offset = 0
        for sg_idx, sg in enumerate(alignment.sync_groups):
            zw_idxs = sg[0]
            zw_idx = zw_idxs[0]
            if len(zw_idxs) != 1:
                raise ScinoephileError(
                    f"Sync group {sg_idx} has {len(zw_idxs)} 中文 subs, expected 1."
                )
            yw_idxs = sg[1]
            if not yw_idxs:
                nascent_sg.append(sg)
                continue
            yw_idx = yw_idxs[0]
            yw = alignment.yuewen[yw_idx]
            if not yw.text:
                nascent_sg.append(([zw_idx], []))
                offset -= 1
                continue
            nascent_yw.append(yw)
            nascent_sg.append(([zw_idx], [yw_idx + offset for yw_idx in yw_idxs]))
        alignment.yuewen = nascent_yw
        alignment._sync_groups_override = nascent_sg

    async def _translate(self, alignment: Alignment):
        """Translate 粤文 subs.

        Arguments:
            alignment: Nascent alignment
        """
        # Get models
        models = get_translate_models(alignment)
        if models is None:
            return
        query_cls, answer_cls, test_case_cls = models

        # Query for 粤文 translation
        query = get_translate_query(alignment, query_cls)
        answer = await self.translator.call(query, answer_cls, test_case_cls)

        # Update 粤文
        nascent_yw = AudioSeries(audio=alignment.yuewen.audio)
        nascent_sg = []
        for sg_idx, sg in enumerate(alignment.sync_groups):
            # Get 中文
            zw_idxs = sg[0]
            zw_idx = zw_idxs[0]
            if len(zw_idxs) != 1:
                raise ScinoephileError(
                    f"Sync group {sg_idx} has {len(zw_idxs)} 中文 subs, expected 1."
                )
            zw = alignment.zhongwen[zw_idx]

            # Get 粤文
            yw_idxs = sg[1]
            if yw_idxs:
                yw_idx = yw_idxs[0]
                if len(yw_idxs) != 1:
                    raise ScinoephileError(
                        f"Sync group {sg_idx} has {len(yw_idxs)} 粤文 subs, expected 1."
                    )
                yw = alignment.yuewen[yw_idx]
            else:
                yw_key = f"yuewen_{zw_idx + 1}"
                yw_text = getattr(answer, yw_key)
                yw = deepcopy(zw)
                yw.text = yw_text
            nascent_yw.append(yw)
            yw_idx = len(nascent_yw) - 1
            nascent_sg.append(([zw_idx], [yw_idx]))
        alignment.yuewen = nascent_yw
        alignment._sync_groups_override = nascent_sg

    async def _review(self, alignment: Alignment):
        """Review 粤文 subs.

        Arguments:
            alignment: Nascent alignment
        """
        models = get_review_models(alignment)
        query_cls, answer_cls, test_case_cls = models

        # Query for 粤文 review
        query = get_review_query(alignment, query_cls)
        answer = await self.reviewer.call(query, answer_cls, test_case_cls)

        # Update 粤文
        nascent_yw = AudioSeries(audio=alignment.yuewen.audio)
        nascent_sg = []
        for sg_idx, sg in enumerate(alignment.sync_groups):
            # Get 中文
            zw_idxs = sg[0]
            if len(zw_idxs) != 1:
                raise ScinoephileError(
                    f"Sync group {sg_idx} has {len(zw_idxs)} 中文 subs, expected 1."
                )
            zw_idx = zw_idxs[0]

            # Get 粤文
            yw_idxs = sg[1]
            if len(yw_idxs) != 1:
                raise ScinoephileError(
                    f"Sync group {sg_idx} has {len(yw_idxs)} 粤文 subs, expected 1."
                )
            yw_idx = yw_idxs[0]
            yw = alignment.yuewen[yw_idx]
            yw_key = f"yuewen_{zw_idx + 1}"
            yw.text = getattr(answer, yw_key, yw.text)
            nascent_yw.append(yw)
            yw_idx = len(nascent_yw) - 1
            nascent_sg.append(([zw_idx], [yw_idx]))
        alignment.yuewen = nascent_yw
        alignment._sync_groups_override = nascent_sg
