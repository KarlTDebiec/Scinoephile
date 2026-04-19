#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Aligns transcribed 粤文 subs with official 中文 subs."""

from __future__ import annotations

from copy import deepcopy
from logging import getLogger
from pathlib import Path

from pydantic import ValidationError

from scinoephile.audio.subtitles import (
    AudioSeries,
    AudioSubtitle,
    get_series_with_sub_split_at_idx,
    get_sub_merged,
)
from scinoephile.audio.transcription import get_backend
from scinoephile.common.validation import val_input_dir_path
from scinoephile.core import ScinoephileError
from scinoephile.core.llms import (
    Answer,
    Query,
    Queryer,
    TestCase,
    save_test_cases_to_json,
)
from scinoephile.core.subtitles import Series
from scinoephile.core.synchronization import get_sync_groups_string
from scinoephile.core.text import remove_punc_and_whitespace

from .alignment import Alignment
from .punctuating import YueZhoHansPunctuatingPrompt
from .shifting import YueZhoHansShiftingPrompt

__all__ = ["Aligner"]


logger = getLogger(__name__)


class Aligner:
    """Aligns transcribed 粤文 subs with official 中文 subs."""

    def __init__(
        self,
        shifting_queryer: Queryer,
        punctuating_queryer: Queryer,
    ):
        """Initialize.

        Arguments:
            shifting_queryer: queryer for shifting
            punctuating_queryer: queryer for punctuating
        """
        self.punctuating_queryer = punctuating_queryer
        """Punctuates transcribed 粤文 text based on corresponding 中文."""
        self.shifting_queryer = shifting_queryer
        """Shifts 粤文 text between adjacent subtitles based on corresponding 中文."""

    def align(self, zhongwen_subs: Series, yuewen_subs: AudioSeries) -> Alignment:
        """Align 粤文 subtitles with 中文 subtitles.

        Presently, this does the following:
          * Assigns 粤文 subtitles to sync groups with 中文 subtitles based on overlap
          * If a 粤文 subtitle overlaps with two 中文 subtitles, asks LLM to distribute
          * At the end of this each sync group should have one 中文 subtitle and
          * zero or more 粤文 subtitles
          * Punctuates 粤文 subtitles using LLM to match 中文 punctuation and spacing
        It needs to also do the following:
        * If there is a discrepancy in the length of the 中文 and concatenated 粤文
          subtitles, prompt LLM with known one 中文 and two 中文 subtitles and ask
          if 粤文 should be shifted.
        * If a 中文 subtitle has no partner 粤文 subtitle, prompt LLM with preceding
          and following 粤文 subtitles and ask if they should be shifted.
        """
        alignment = Alignment(zhongwen_subs, yuewen_subs)

        # Shifting may involve simply shifting a whole 粤文 subtitle from one sync group
        # to another, or it may involve splitting a 粤文 subtitle into two 粤文
        # subtitles. Each time a 粤文 subtitle is split, shifting is implicitly
        # restarted by clearing the sync group override.
        shifting_in_progress = True
        while shifting_in_progress:
            shifting_in_progress = self._shift(alignment)

        # Punctuate 粤文 subtitles to match 中文 punctuation and spacing
        self._punctuate(alignment)

        # Return final alignment
        return alignment

    def _shift(self, alignment) -> bool:
        """Shift 粤文 text.

        Arguments:
            alignment: Nascent alignment
        """
        for sg_1_idx in range(len(alignment.sync_groups) - 1):
            # Run query
            test_case = alignment.get_shifting_test_case(sg_1_idx)
            if test_case is None:
                logger.info(
                    f"Skipping sync groups {sg_1_idx} and {sg_1_idx + 1} with no 粤文"
                )
                continue
            # TODO: try/expect and return original 粤文 on error (not yet encountered)
            test_case: TestCase = self.shifting_queryer.call(test_case)

            # If there is no change, continue
            query = test_case.query
            answer = test_case.answer
            prompt_cls: type[YueZhoHansShiftingPrompt] = getattr(
                test_case, "prompt_cls"
            )
            yuewen_1_shifted = getattr(answer, prompt_cls.src_2_sub_1_shifted, None)
            yuewen_2_shifted = getattr(answer, prompt_cls.src_2_sub_2_shifted, None)
            if yuewen_1_shifted == "" and yuewen_2_shifted == "":
                continue
            if self._shift_one(alignment, sg_1_idx, query, answer):
                return True
        return False

    def _shift_one(
        self,
        alignment: Alignment,
        sg_1_idx: int,
        query: Query,
        answer: Answer,
    ) -> bool:
        """Shift text between one sync-group pair when LLM output requires it.

        Arguments:
            alignment: current alignment being updated
            sg_1_idx: index of the first sync group in the pair
            query: LLM query payload for the pair
            answer: LLM answer payload for the pair
        Returns:
            whether shifting requires restarting group traversal
        """
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
        prompt_cls: type[YueZhoHansShiftingPrompt] = getattr(query, "prompt_cls")
        yw_1_idxs = sg_1[1]
        yw_2_idxs = sg_2[1]
        yw_1 = getattr(query, prompt_cls.src_2_sub_1, "")
        yw_2 = getattr(query, prompt_cls.src_2_sub_2, "")
        yw_1_shifted = getattr(answer, prompt_cls.src_2_sub_1_shifted, "")
        yw_2_shifted = getattr(answer, prompt_cls.src_2_sub_2_shifted, "")

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
            f"Unexpected case:\nQuery:\n{query}\n with Answer:\n{answer}\n"
        )

    def _punctuate(self, alignment: Alignment):
        """Punctuate 粤文 subs.

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
            yws: list[AudioSubtitle] = [
                alignment.yuewen.events[yw_i] for yw_i in yw_idxs
            ]

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

            # Query for 粤文 punctuate
            test_case = alignment.get_punctuating_test_case(sg_idx)
            if test_case is None:
                logger.info(f"Skipping sync group {sg_idx} with no 粤文 subtitles")
                nascent_sg.append(([zw_idx], []))
                continue
            try:
                test_case = self.punctuating_queryer.call(test_case)
            except ValidationError as exc:
                # TODO: Consider how this could be improved
                logger.error(
                    f"Error punctuating sync group {sg_idx}; concatenating.\n"
                    f"Test case:\n"
                    f"{test_case}\n"
                    f"Exception:\n{exc}"
                )
            prompt_cls: type[YueZhoHansPunctuatingPrompt] = getattr(
                test_case, "prompt_cls"
            )
            yuewen_punctuated = getattr(test_case.answer, prompt_cls.output, None)
            yw = get_sub_merged(yws, text=yuewen_punctuated)
            yw.start = zw.start
            yw.end = zw.end

            # Update sync group
            nascent_yw.append(yw)
            yw_idx = len(nascent_yw) - 1
            nascent_sg.append(([zw_idx], [yw_idx]))

        alignment.yuewen = nascent_yw
        alignment._sync_groups_override = nascent_sg

    def update_all_test_cases(self, test_root: Path | str):
        """Update all test cases for the specified block.

        Arguments:
            test_root: Path to root directory of test cases
        """
        test_root = val_input_dir_path(test_root)
        backend = get_backend()

        save_test_cases_to_json(
            test_root
            / "multilang"
            / "yue_zho"
            / "transcription"
            / "shifting"
            / f"{backend}.json",
            list(self.shifting_queryer.encountered_test_cases.values()),
        )
        save_test_cases_to_json(
            test_root
            / "multilang"
            / "yue_zho"
            / "transcription"
            / "punctuating"
            / f"{backend}.json",
            list(self.punctuating_queryer.encountered_test_cases.values()),
        )
