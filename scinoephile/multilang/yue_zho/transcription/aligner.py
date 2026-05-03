#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Aligns transcribed written Cantonese subs with official standard Chinese subs."""

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
from scinoephile.common.validation import val_input_dir_path
from scinoephile.core import ScinoephileError
from scinoephile.core.llms import (
    Answer,
    Query,
    Queryer,
    TestCase,
)
from scinoephile.core.llms.utils import save_test_cases_to_json
from scinoephile.core.ml import get_torch_device
from scinoephile.core.subtitles import Series
from scinoephile.core.synchronization import get_sync_groups_string
from scinoephile.core.text import remove_punc_and_whitespace

from .alignment import Alignment
from .deliniation import (
    YueVsZhoYueHansDeliniationPrompt as YueZhoHansDelineationPrompt,
)
from .punctuation import YueVsZhoYueHansPunctuationPrompt

__all__ = ["Aligner"]


logger = getLogger(__name__)


class Aligner:
    """Aligns transcribed written Cantonese subs with official standard Chinese subs."""

    def __init__(
        self,
        deliniation_queryer: Queryer,
        punctuation_queryer: Queryer,
        test_case_dir_path: Path | None = None,
    ):
        """Initialize.

        Arguments:
            deliniation_queryer: queryer for delineation
            punctuation_queryer: queryer for punctuation
            test_case_dir_path: directory where encountered test cases are written
        """
        self.punctuation_queryer = punctuation_queryer
        """Punctuates written Cantonese from corresponding standard Chinese."""
        self.deliniation_queryer = deliniation_queryer
        """Shifts written Cantonese between adjacent subtitles from standard Chinese."""
        self.test_case_dir_path = None
        if test_case_dir_path is not None:
            self.test_case_dir_path = val_input_dir_path(test_case_dir_path)

    def align(self, zhongwen_subs: Series, yuewen_subs: AudioSeries) -> Alignment:
        """Align written Cantonese subtitles with standard Chinese subtitles.

        Presently, this does the following:
          * Assigns written Cantonese subtitles to sync groups with standard Chinese
            subtitles based on overlap
          * If a written Cantonese subtitle overlaps with two standard Chinese
            subtitles, asks LLM to distribute
          * At the end of this, each sync group should have one standard Chinese
            subtitle and zero or more written Cantonese subtitles
          * Combines and punctuates written Cantonese subtitles using LLM to match
            standard Chinese punctuation and spacing
        It needs to also do the following:
          * If there is a discrepancy in the length of the standard Chinese and
            concatenated written Cantonese subtitles, prompt the LLM with one known
            standard Chinese subtitle and two known written Cantonese subtitles and ask
            whether written Cantonese should be shifted.
          * If a standard Chinese subtitle has no partner written Cantonese subtitle,
            prompt LLM with preceding and following written Cantonese subtitles and ask
            whether they should be shifted.
        """
        alignment = Alignment(zhongwen_subs, yuewen_subs)

        # Delineation may involve moving a whole written Cantonese subtitle from one
        # sync group to another, or it may involve splitting a written Cantonese
        # subtitle into two written Cantonese subtitles. Each time a written
        # Cantonese subtitle is split, delineation is implicitly restarted by
        # clearing the sync-group override.
        delineation_in_progress = True
        while delineation_in_progress:
            delineation_in_progress = self._delineate(alignment)

        # Punctuate written Cantonese subtitles to match standard Chinese punctuation
        # and spacing.
        self._punctuate(alignment)

        # Return final alignment
        return alignment

    def _delineate(self, alignment: Alignment) -> bool:
        """Delineate written Cantonese text.

        Arguments:
            alignment: Nascent alignment
        """
        for sg_1_idx in range(len(alignment.sync_groups) - 1):
            # Run query
            test_case = alignment.get_deliniation_test_case(sg_1_idx)
            if test_case is None:
                logger.info(
                    f"Skipping sync groups {sg_1_idx} and {sg_1_idx + 1} "
                    "with no written Cantonese"
                )
                continue
            # TODO: try/except and return original written Cantonese on error
            # (not yet encountered).
            test_case: TestCase = self.deliniation_queryer.call(test_case)

            # If there is no change, continue
            query = test_case.query
            answer = test_case.answer
            if answer is None:
                message = "Delineation query returned no answer."
                logger.error(message)
                raise ScinoephileError(message)
            prompt_cls: type[YueZhoHansDelineationPrompt] = getattr(
                test_case, "prompt_cls"
            )
            yuewen_1_shifted = getattr(answer, prompt_cls.src_2_sub_1_shifted, None)
            yuewen_2_shifted = getattr(answer, prompt_cls.src_2_sub_2_shifted, None)
            if yuewen_1_shifted == "" and yuewen_2_shifted == "":
                continue
            if self._delineate_one(alignment, sg_1_idx, query, answer):
                return True
        return False

    def _delineate_one(
        self,
        alignment: Alignment,
        sg_1_idx: int,
        query: Query,
        answer: Answer,
    ) -> bool:
        """Delineate text between one sync-group pair when LLM output requires it.

        Arguments:
            alignment: current alignment being updated
            sg_1_idx: index of the first sync group in the pair
            query: LLM query payload for the pair
            answer: LLM answer payload for the pair
        Returns:
            whether delineation requires restarting group traversal
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

        # Get written Cantonese
        prompt_cls: type[YueZhoHansDelineationPrompt] = getattr(query, "prompt_cls")
        yw_1_idxs = sg_1[1]
        yw_2_idxs = sg_2[1]
        yw_1 = getattr(query, prompt_cls.src_2_sub_1, "")
        yw_2 = getattr(query, prompt_cls.src_2_sub_2, "")
        yw_1_shifted = getattr(answer, prompt_cls.src_2_sub_1_shifted, "")
        yw_2_shifted = getattr(answer, prompt_cls.src_2_sub_2_shifted, "")

        # Shift written Cantonese
        nascent_sg = deepcopy(alignment.sync_groups)

        # Case: written Cantonese text needs to be shifted from standard Chinese 2
        # to standard Chinese 1
        if len(yw_1) < len(yw_1_shifted):
            # Calculate the number of characters we need to shift from 2 to 1
            text_to_shift_from_2_to_1 = yw_1_shifted[len(yw_1) :]
            n_chars_remaining_to_shift = len(text_to_shift_from_2_to_1)

            # Loop over subtitles currently in sync group 2
            for yw_2_idx in yw_2_idxs:
                yw = alignment.yuewen[yw_2_idx]

                # Case: A sub in written Cantonese 2 overlaps partially with standard
                # Chinese 1 and 2
                # Action: Split sub into two subs, and return True to indicate that
                #   delineation must be restarted
                if len(yw.text) > n_chars_remaining_to_shift:
                    alignment.yuewen = get_series_with_sub_split_at_idx(
                        alignment.yuewen, yw_2_idx, n_chars_remaining_to_shift
                    )
                    # Must restart delineation after splitting a subtitle
                    alignment._sync_groups_override = None
                    return True

                # Case: A sub in written Cantonese 2 overlaps with standard Chinese 1
                # and not standard Chinese 2
                # Action: Shift sub from sync group 2 to 1
                nascent_sg[sg_1_idx][1].append(yw_2_idx)
                nascent_sg[sg_2_idx][1].remove(yw_2_idx)
                n_chars_remaining_to_shift -= len(yw.text)

                # Case: Delineation is complete
                # Action: Set sync groups and return False to indicate completion
                if n_chars_remaining_to_shift == 0:
                    alignment._sync_groups_override = nascent_sg
                    return False

        # Case: written Cantonese text needs to be shifted from standard Chinese 1
        # to standard Chinese 2
        # Action: Shift written Cantonese text from sync group 1 to sync group 2
        if len(yw_2) < len(yw_2_shifted):
            # Calculate the number of characters we need to shift from 1 to 2
            text_to_shift_from_1_to_2 = yw_2_shifted[: len(yw_2_shifted) - len(yw_2)]
            n_chars_remaining_to_shift = len(text_to_shift_from_1_to_2)

            # Loop over subtitles currently in sync group 1
            for yw_1_idx in reversed(yw_1_idxs):
                yw = alignment.yuewen[yw_1_idx]

                # Case: A sub in written Cantonese 1 overlaps partially with standard
                # Chinese 1 and 2
                # Action: Split sub into two subs, and return True to indicate that
                #   delineation must be restarted
                if len(yw.text) > n_chars_remaining_to_shift:
                    alignment.yuewen = get_series_with_sub_split_at_idx(
                        alignment.yuewen,
                        yw_1_idx,
                        len(yw.text) - n_chars_remaining_to_shift,
                    )
                    # Must restart delineation after splitting a subtitle
                    alignment._sync_groups_override = None
                    return True

                # Case: A sub in written Cantonese 1 overlaps with standard Chinese 2
                # and not standard Chinese 1
                # Action: Shift sub from sync group 1 to 2
                nascent_sg[sg_1_idx][1].remove(yw_1_idx)
                nascent_sg[sg_2_idx][1].insert(0, yw_1_idx)
                n_chars_remaining_to_shift -= len(yw.text)

                # Case: Delineation is complete
                # Action: Set sync groups and return False to indicate completion
                if n_chars_remaining_to_shift == 0:
                    alignment._sync_groups_override = nascent_sg
                    return False

        raise ScinoephileError(
            f"Unexpected case:\nQuery:\n{query}\n with Answer:\n{answer}\n"
        )

    def _punctuate(self, alignment: Alignment):
        """Punctuate written Cantonese subs.

        Arguments:
            alignment: Nascent alignment
        """
        if not alignment.zhongwen_all_assigned_to_sync_groups:
            raise ScinoephileError(
                f"Not all standard Chinese subtitles are in a sync group:\n"
                f"SYNC GROUPS:\n{get_sync_groups_string(alignment.sync_groups)}"
            )
        if not alignment.yuewen_all_assigned_to_sync_groups:
            raise ScinoephileError(
                f"Not all written Cantonese subtitles are in a sync group:\n"
                f"SYNC GROUPS:\n{get_sync_groups_string(alignment.sync_groups)}"
            )

        nascent_yw = AudioSeries(audio=alignment.yuewen.audio)
        nascent_sg = []
        for sg_idx in range(len(alignment.sync_groups)):
            # Get sync group
            sg = alignment.sync_groups[sg_idx]

            # Get standard Chinese
            zw_idxs = sg[0]
            zw_idx = zw_idxs[0]
            zw = alignment.zhongwen[zw_idx]

            # Get written Cantonese
            yw_idxs = sg[1]
            yws: list[AudioSubtitle] = [
                alignment.yuewen.events[yw_i] for yw_i in yw_idxs
            ]

            # If there is no punctuation, whitespace, or ambiguity, just copy over
            if zw.text == remove_punc_and_whitespace(zw.text) and len(yws) == 1:
                # If the standard Chinese subtitle has no punctuation, and there is only
                # one written Cantonese subtitle, just copy it over.
                yw = yws[0]
                yw.start = zw.start
                yw.end = zw.end
                nascent_yw.append(yw)
                nascent_sg.append(([zw_idx], [len(nascent_yw) - 1]))
                continue

            # Query for written Cantonese punctuation
            test_case = alignment.get_punctuation_test_case(sg_idx)
            if test_case is None:
                logger.info(
                    f"Skipping sync group {sg_idx} with no written Cantonese subtitles"
                )
                nascent_sg.append(([zw_idx], []))
                continue
            try:
                test_case = self.punctuation_queryer.call(test_case)
            except ValidationError as exc:
                # TODO: Consider how this could be improved
                logger.error(
                    f"Error punctuating sync group {sg_idx}; concatenating.\n"
                    f"Test case:\n"
                    f"{test_case}\n"
                    f"Exception:\n{exc}"
                )
            prompt_cls: type[YueVsZhoYueHansPunctuationPrompt] = getattr(
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

    def update_all_test_cases(self):
        """Update all test cases for the specified block."""
        if self.test_case_dir_path is None:
            return

        deliniation_output_path = (
            self.test_case_dir_path / "deliniation" / f"{get_torch_device()}.json"
        )
        save_test_cases_to_json(
            deliniation_output_path,
            list(self.deliniation_queryer.encountered_test_cases.values()),
        )
        punctuation_output_path = (
            self.test_case_dir_path / "punctuation" / f"{get_torch_device()}.json"
        )
        save_test_cases_to_json(
            punctuation_output_path,
            list(self.punctuation_queryer.encountered_test_cases.values()),
        )
