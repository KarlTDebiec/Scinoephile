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
from scinoephile.audio.cantonese.alignment.models import get_translate_models
from scinoephile.audio.cantonese.alignment.queries import (
    get_distribute_query,
    get_merge_query,
    get_proof_query,
    get_shift_query,
    get_translate_query,
)
from scinoephile.audio.cantonese.distribution import DistributeAnswer, Distributor
from scinoephile.audio.cantonese.merging import MergeAnswer, Merger, MergeTestCase
from scinoephile.audio.cantonese.proofing import Proofer
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
    ):
        """Initialize.

        Arguments:
            distributor: Cantonese splitter
            shifter: Cantonese shifter
            merger: Cantonese merger
            proofer: Cantonese proofer
            translator: Cantonese translator
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

    def align(self, zhongwen_subs: AudioSeries, yuewen_subs: AudioSeries) -> Alignment:
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
            self._distribute(alignment)

            # Then shift 粤文 subtitles that remain misaligned after distribution
            print(f"SHIFTING ITERATION {iteration}")
            distribution_and_shifting_in_progress = self._shift(alignment)
            iteration += 1

        # TODO: Identify partnerless 中文 subtitles and prompt LLM for translation

        # Merge 粤文 subtitles to match 中文 punctuation and spacing
        self._merge(alignment)

        # Proofread 粤文 subtitles based on corresponding 中文 subtitles
        self._proof(alignment)

        self._translate(alignment)

        # Return final alignment
        print(f"\nFINAL RESULT:\n{alignment}")
        return alignment

    def _distribute(self, alignment: Alignment):
        """Distribute 粤文 subs.

        Arguments:
            alignment: Nascent alignment
        """
        iteration = 0
        while alignment.yuewen_to_distribute:
            info(f"\nITERATION {iteration}")
            info(alignment)
            self._distribute_one(alignment)
            iteration += 1

    def _distribute_one(self, alignment: Alignment):
        """Split 粤文 subs.

        Arguments:
            alignment: Nascent alignment
        """
        # Get sync group and yuewen indexes
        yw_idx = alignment.yuewen_to_distribute[0]
        zw_idxs = np.where(alignment.scaled_overlap[:, yw_idx] > 0.33)[0]

        # If 粤文 overlaps with nothing, just remove it
        if len(zw_idxs) == 0:
            yuewen = AudioSeries(audio=alignment.yuewen.audio)
            yuewen.events = (
                alignment.yuewen.events[:yw_idx] + alignment.yuewen.events[yw_idx + 1 :]
            )
            alignment.yuewen = yuewen
            alignment._sync_groups_override = None
            return

        # Other situations have not yet been encountered
        if len(zw_idxs) != 2:
            raise ScinoephileError(
                f"Situation not supported: 粤文 subtitle {yw_idx} overlaps with "
                f"{len(zw_idxs)} sync groups: {zw_idxs.tolist()}.\n{alignment}"
            )

        # TODO: Validate that zw_idxs map cleanly to sg_idxs
        one_sg_idx, two_sg_idx = zw_idxs

        # Run query
        query = get_distribute_query(alignment, one_sg_idx, two_sg_idx, yw_idx)
        try:
            answer = self.distributor(query)
        except ValidationError as exc:
            # TODO: Consider how this could be improved
            # TODO: Consider just deleting undistributable 粤文
            answer = DistributeAnswer(
                one_yuewen_to_append=query.yuewen_to_distribute,
                two_yuewen_to_prepend="",
            )
            test_case = query.to_test_case(answer)
            error(
                f"Error distributing 粤文 subtitle {yw_idx} between sync groups "
                f"{one_sg_idx} and {two_sg_idx}; distributing to first group.\n"
                f"Test case:\n"
                f"{test_case.source_str}\n"
                f"Exception:\n{exc}\n"
            )

        # If we only need to assign the 粤文 to one sync group, set override
        if answer.one_yuewen_to_append and not answer.two_yuewen_to_prepend:
            nascent_sync_groups = deepcopy(alignment.sync_groups)
            nascent_sync_groups[one_sg_idx][1].append(yw_idx)
            alignment._sync_groups_override = nascent_sync_groups
            return
        if not answer.one_yuewen_to_append and answer.two_yuewen_to_prepend:
            nascent_sync_groups = deepcopy(alignment.sync_groups)
            nascent_sync_groups[two_sg_idx][1].insert(0, yw_idx)
            alignment._sync_groups_override = nascent_sync_groups
            return

        # If we need to split the 粤文 text, we must then clear the override
        alignment.yuewen = get_series_with_sub_split_at_idx(
            alignment.yuewen, yw_idx, len(answer.one_yuewen_to_append)
        )
        alignment._sync_groups_override = None

    def _shift(self, alignment) -> bool:
        """Shift 粤文 text.

        Arguments:
            alignment: Nascent alignment
        """
        for one_sg_idx in range(len(alignment.sync_groups) - 1):
            two_sg_idx = one_sg_idx + 1

            # Run query
            query = get_shift_query(alignment, one_sg_idx, two_sg_idx)
            if query is None:
                info(f"Skipping sync groups {one_sg_idx} and {two_sg_idx} with no 粤文")
                continue
            # TODO: try / except
            answer = self.shifter(query)

            # If there is no change, continue
            if (
                query.one_yuewen == answer.one_yuewen_shifted
                and query.two_yuewen == answer.two_yuewen_shifted
            ):
                continue
            if self._shift_one(alignment, one_sg_idx, two_sg_idx, query, answer):
                return True
        return False

    def _shift_one(
        self,
        alignment: Alignment,
        one_sg_idx: int,
        two_sg_idx: int,
        query: ShiftQuery,
        answer: ShiftAnswer,
    ) -> bool:
        # Get sync groups
        if one_sg_idx < 0 or one_sg_idx >= len(alignment.sync_groups):
            raise ScinoephileError(
                f"Invalid sync group index {one_sg_idx} "
                f"for alignment with {len(alignment.sync_groups)} sync groups."
            )
        if two_sg_idx < 0 or two_sg_idx >= len(alignment.sync_groups):
            raise ScinoephileError(
                f"Invalid sync group index {two_sg_idx} "
                f"for alignment with {len(alignment.sync_groups)} sync groups."
            )
        if one_sg_idx + 1 != two_sg_idx:
            raise ScinoephileError(
                f"Sync groups {one_sg_idx} and {two_sg_idx} are not consecutive."
            )
        one_sg = alignment.sync_groups[one_sg_idx]
        two_sg = alignment.sync_groups[two_sg_idx]

        # Get 粤文
        one_yw_idxs = one_sg[1]
        two_yw_idxs = two_sg[1]

        # Shift 粤文 text
        one_yuewen = query.one_yuewen
        two_yuewen = query.two_yuewen
        one_yuewen_shifted = answer.one_yuewen_shifted
        two_yuewen_shifted = answer.two_yuewen_shifted
        nascent_sync_groups = deepcopy(alignment.sync_groups)
        # TODO: Review this logic and consider how to clarify
        if len(one_yuewen) < len(one_yuewen_shifted):
            # Calculate the number of characters we need to shift from two to one
            text_to_shift_from_two_to_one = one_yuewen_shifted[len(one_yuewen) :]
            n_chars_left_to_shift = len(text_to_shift_from_two_to_one)

            # Loop over subtitles currently in two
            for two_yw_idx in two_yw_idxs:
                yw = alignment.yuewen[two_yw_idx]

                if len(yw.text) <= n_chars_left_to_shift:
                    # Entire sub needs to be shifted from two to one
                    nascent_sync_groups[one_sg_idx][1].append(two_yw_idx)
                    nascent_sync_groups[two_sg_idx][1].remove(two_yw_idx)
                    n_chars_left_to_shift -= len(yw.text)
                else:
                    # Sub needs to be split, which means we need to restart after
                    alignment.yuewen = get_series_with_sub_split_at_idx(
                        alignment.yuewen, two_yw_idx, n_chars_left_to_shift
                    )
                    n_chars_left_to_shift -= len(yw.text[:n_chars_left_to_shift])
                    alignment._sync_groups_override = None
                    return True
                if n_chars_left_to_shift == 0:
                    break
        elif len(one_yuewen) > len(one_yuewen_shifted):
            # Calculate the number of characters we need to shift from one to two
            text_to_shift_from_one_to_two = one_yuewen[len(one_yuewen_shifted) :]
            n_chars_left_to_shift = len(text_to_shift_from_one_to_two)

            # Loop over subtitles currently in one
            for one_yw_idx in reversed(one_yw_idxs):
                yw = alignment.yuewen[one_yw_idx]

                if len(yw.text) <= n_chars_left_to_shift:
                    # Entire sub needs to be shifted from one to two
                    nascent_sync_groups[two_sg_idx][1].insert(0, one_yw_idx)
                    nascent_sync_groups[one_sg_idx][1].remove(one_yw_idx)
                    n_chars_left_to_shift -= len(yw.text)
                else:
                    # Sub needs to be split, which means we need to restart after
                    alignment.yuewen = get_series_with_sub_split_at_idx(
                        alignment.yuewen, one_yw_idx, n_chars_left_to_shift
                    )
                    n_chars_left_to_shift -= len(yw.text[:n_chars_left_to_shift])
                    alignment._sync_groups_override = None
                    return True
                if n_chars_left_to_shift == 0:
                    break

        else:
            raise ScinoephileError("Unexpected case.")
        alignment._sync_groups_override = nascent_sync_groups
        return False

    def _merge(self, alignment: Alignment):
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
            yw_subs = [alignment.yuewen[yw_i] for yw_i in yw_idxs]

            # If there is no punctuation, whitespace, or ambiguity, just copy over
            if zw.text == remove_punc_and_whitespace(zw.text) and len(yw_subs) == 1:
                # If the 中文 subtitle has no punctuation, and there is only one 粤文
                # subtitle, just copy it over
                yw_sub = yw_subs[0]
                yw_sub.start = zw.start
                yw_sub.end = zw.end
                nascent_yw.append(yw_sub)
                nascent_sg.append(([zw_idx], [len(nascent_yw) - 1]))
                continue

            # Query for 粤文 merge
            query = get_merge_query(alignment, sg_idx)
            if query is None:
                info(f"Skipping sync group {sg_idx} with no 粤文 subtitles")
                nascent_sg.append(([zw_idx], []))
                continue
            try:
                answer = self.merger(query)
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
            yw_sub = get_sub_merged(yw_subs, text=answer.yuewen_merged)
            yw_sub.start = zw.start
            yw_sub.end = zw.end

            # Update sync group
            nascent_yw.append(yw_sub)
            yw_idx = len(nascent_yw) - 1
            nascent_sg.append(([zw_idx], [yw_idx]))

        alignment.yuewen = nascent_yw
        alignment._sync_groups_override = nascent_sg

    def _proof(self, alignment: Alignment):
        """Proofread 粤文 subs.

        Arguments:
            alignment: Nascent alignment
        """
        for sg_idx in range(len(alignment.sync_groups)):
            query = get_proof_query(alignment, sg_idx)
            if query is None:
                info(f"Skipping sync group {sg_idx} with no 粤文 subtitles")
                continue
            answer = self.proofer(query)

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

        nascent_yuewen_subs = AudioSeries(audio=alignment.yuewen.audio)
        nascent_sync_groups = []
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
                nascent_sync_groups.append(sg)
                continue
            yw_idx = yw_idxs[0]
            yw = alignment.yuewen[yw_idx]
            if not yw.text:
                nascent_sync_groups.append(([zw_idx], []))
                offset -= 1
                continue
            nascent_yuewen_subs.append(yw)
            nascent_sync_groups.append(
                ([zw_idx], [yw_idx + offset for yw_idx in yw_idxs])
            )
        alignment.yuewen = nascent_yuewen_subs
        alignment._sync_groups_override = nascent_sync_groups

    def _translate(self, alignment: Alignment):
        """Translate 粤文 subs.

        Arguments:
            alignment: Nascent alignment
        """
        translate_models = get_translate_models(alignment)
        if translate_models is None:
            return
        query_cls, answer_cls, test_case_cls = translate_models
        query = get_translate_query(alignment, query_cls)
        answer = self.translator(query, answer_cls, test_case_cls)

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
