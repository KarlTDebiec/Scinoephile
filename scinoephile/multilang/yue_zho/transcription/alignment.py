#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Nascent alignment between standard Chinese and written Cantonese subtitles."""

from __future__ import annotations

from pprint import pformat

import numpy as np

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.core import ScinoephileError
from scinoephile.core.llms import TestCase
from scinoephile.core.pairs import get_pair_strings
from scinoephile.core.subtitles import Series
from scinoephile.core.synchronization import (
    SyncGroup,
    get_overlap_string,
    get_sync_groups_string,
    get_sync_overlap_matrix,
)
from scinoephile.llms.dual_pair import DualPairManager

from .deliniation import YueVsZhoYueHansDeliniationPrompt
from .punctuation import YueVsZhoYueHansPunctuationPrompt, YueZhoPunctuationManager

__all__ = ["Alignment"]


class Alignment:
    """Nascent alignment between standard Chinese and written Cantonese subtitles."""

    def __init__(self, zhongwen: Series, yuewen: AudioSeries):
        """Initialize.

        Arguments:
            zhongwen: standard Chinese subs
            yuewen: written Cantonese subs
        """
        self._zhongwen = zhongwen
        self._yuewen = yuewen

        self._sync_groups_override = None

    def __str__(self) -> str:
        """String representation."""
        zhongwen_str, yuewen_str = get_pair_strings(self.zhongwen, self.yuewen)
        string = f"MANDARIN:\n{zhongwen_str}"
        string += f"\nCANTONESE:\n{yuewen_str}"
        string += f"\nOVERLAP:\n{get_overlap_string(self.overlap)}"
        if self._sync_groups_override:
            string += "\nSYNC GROUPS (OVERRIDDEN):"
        else:
            string += "\nSYNC GROUPS:"
        string += f"\n{get_sync_groups_string(self.sync_groups)}"
        string += f"\nTO REVIEW:\n{pformat([i + 1 for i in self.yuewen_to_distribute])}"
        return string

    @property
    def overlap(self) -> np.ndarray:
        """Overlap matrix between standard Chinese and written Cantonese."""
        overlap = get_sync_overlap_matrix(self.zhongwen, self.yuewen)
        return overlap

    @property
    def scaled_overlap(self) -> np.ndarray:
        """Scaled overlap matrix between standard Chinese and written Cantonese."""
        scaled_overlap = self.overlap.copy()
        column_maxes = scaled_overlap.max(axis=0)
        column_maxes[column_maxes == 0] = 1
        scaled_overlap /= column_maxes
        return scaled_overlap

    @property
    def sync_groups(self) -> list[SyncGroup]:
        """Sync groups between standard Chinese and written Cantonese."""
        if self._sync_groups_override:
            # TODO: Validate that override is consistent with current series
            # TODO: Consider clearing automatically when zhongwen or yuewen change
            # TODO: Make public setter for _sync_groups_override
            return self._sync_groups_override

        # Each sync group must be one standard Chinese sub and zero or more written
        # Cantonese subs.
        nascent_sync_groups = [([i], []) for i, _ in enumerate(self.zhongwen)]

        # For each written Cantonese sub, find the corresponding standard Chinese sub
        # and add it to the sync group.
        for yw_idx in range(len(self.yuewen)):
            sg_idx = np.argmax(self.overlap[:, yw_idx])
            nascent_sync_groups[sg_idx][1].append(yw_idx)

        return nascent_sync_groups

    @property
    def yuewen(self) -> AudioSeries:
        """Written Cantonese series."""
        return self._yuewen

    @yuewen.setter
    def yuewen(self, value: AudioSeries):
        """Set written Cantonese series and clear cached values.

        Arguments:
            value: written Cantonese series
        """
        self._yuewen = value

    @property
    def yuewen_all_assigned_to_sync_groups(self) -> bool:
        """Whether all written Cantonese subs are assigned to sync groups."""
        yw_idxs = set([yw_idx for sg in self.sync_groups for yw_idx in sg[1]])
        return yw_idxs == set(range(len(self.yuewen)))

    @property
    def yuewen_to_distribute(self) -> list[int]:
        """Written Cantonese indices in need of distribution."""
        yw_idxs = set([yw_idx for sg in self.sync_groups for yw_idx in sg[1]])
        return sorted(set(range(len(self.yuewen))) - yw_idxs)

    @property
    def zhongwen(self) -> AudioSeries | Series:
        """Standard Chinese series."""
        return self._zhongwen

    @zhongwen.setter
    def zhongwen(self, value: AudioSeries | Series):
        """Set standard Chinese series and clear cached values.

        Arguments:
            value: standard Chinese series
        """
        self._zhongwen = value

    @property
    def zhongwen_all_assigned_to_sync_groups(self) -> bool:
        """Whether all standard Chinese subs are assigned to sync groups."""
        zw_idxs = set([zw_idx for sg in self.sync_groups for zw_idx in sg[0]])
        return zw_idxs == set(range(len(self.zhongwen)))

    def get_deliniation_test_case(self, sg_1_idx: int) -> TestCase | None:
        """Get deliniation query for a sync group index.

        Arguments:
            sg_1_idx: Index of sync group 1
        Returns:
            Query, or None if there are no written Cantonese subs to shift
        """
        # Get sync group 1
        if sg_1_idx < 0 or sg_1_idx >= len(self.sync_groups):
            raise ScinoephileError(
                f"Invalid sync group index {sg_1_idx} "
                f"for alignment with {len(self.sync_groups)} sync groups."
            )
        sg_1 = self.sync_groups[sg_1_idx]

        # Get sync group 2
        sg_2_idx = sg_1_idx + 1
        if sg_2_idx < 0 or sg_2_idx >= len(self.sync_groups):
            raise ScinoephileError(
                f"Invalid sync group index {sg_2_idx} "
                f"for alignment with {len(self.sync_groups)} sync groups."
            )
        sg_2 = self.sync_groups[sg_2_idx]

        # Get standard Chinese 1
        sg_1_zw_idxs = sg_1[0]
        if len(sg_1_zw_idxs) != 1:
            raise ScinoephileError(
                f"Sync group {sg_1_idx} has {len(sg_1_zw_idxs)} "
                "standard Chinese subs, expected 1."
            )
        sg_1_zw_idx = sg_1[0][0]
        zw_1 = self.zhongwen[sg_1_zw_idx].text

        # Get standard Chinese 2
        sg_2_zw_idxs = sg_2[0]
        if len(sg_2[0]) != 1:
            raise ScinoephileError(
                f"Sync group {sg_2_idx} has {len(sg_2_zw_idxs)} "
                "standard Chinese subs, expected 1."
            )
        sg_2_zw_idx = sg_2[0][0]
        if sg_1_zw_idx + 1 != sg_2_zw_idx:
            raise ScinoephileError(
                f"standard Chinese indexes {sg_1_zw_idx} and {sg_2_zw_idx} "
                "are not consecutive."
            )
        zw_2 = self.zhongwen[sg_2_zw_idx].text

        # Get written Cantonese 1
        sg_1_yw_idxs = sg_1[1]
        yw_1 = "".join([self.yuewen[i].text for i in sg_1_yw_idxs])

        # Get written Cantonese 2
        sg_2_yw_idxs = sg_2[1]
        yw_2 = "".join([self.yuewen[i].text for i in sg_2_yw_idxs])

        # Return
        if len(sg_1_yw_idxs) == 0 and len(sg_2_yw_idxs) == 0:
            return None
        test_case_cls = DualPairManager.get_test_case_cls(
            prompt_cls=YueVsZhoYueHansDeliniationPrompt
        )
        query_kwargs = {
            test_case_cls.prompt_cls.src_1_sub_1: zw_1,
            test_case_cls.prompt_cls.src_2_sub_1: yw_1,
            test_case_cls.prompt_cls.src_1_sub_2: zw_2,
            test_case_cls.prompt_cls.src_2_sub_2: yw_2,
        }
        # noinspection PyArgumentList
        test_case = test_case_cls(query=test_case_cls.query_cls(**query_kwargs))
        return test_case

    def get_punctuation_test_case(self, sg_idx: int) -> TestCase | None:
        """Get punctuation query for a sync group.

        Arguments:
            sg_idx: Index of sync group
        Returns:
            test case, or None if there are no written Cantonese subs to punctuate
        """
        # Get sync group
        if sg_idx < 0 or sg_idx >= len(self.sync_groups):
            raise ScinoephileError(
                f"Invalid sync group index {sg_idx} "
                f"for alignment with {len(self.sync_groups)} sync groups."
            )
        sg = self.sync_groups[sg_idx]

        # Get standard Chinese
        zw_idxs = sg[0]
        if len(zw_idxs) != 1:
            raise ScinoephileError(
                f"Sync group {sg_idx} has {len(zw_idxs)} "
                "standard Chinese subs, expected 1."
            )
        zw_idx = sg[0][0]
        zw = self.zhongwen[zw_idx].text

        # Get written Cantonese
        yw_idxs = sg[1]
        if len(yw_idxs) == 0:
            return None
        yws = [self.yuewen[i].text for i in yw_idxs]

        # Return punctuate query
        test_case_cls = YueZhoPunctuationManager.get_test_case_cls(
            prompt_cls=YueVsZhoYueHansPunctuationPrompt
        )
        query_kwargs = {
            test_case_cls.prompt_cls.src_2: zw,
            test_case_cls.prompt_cls.src_1: yws,
        }
        # noinspection PyArgumentList
        test_case = test_case_cls(query=test_case_cls.query_cls(**query_kwargs))
        return test_case
