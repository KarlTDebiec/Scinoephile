#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Nascent alignment between 中文 and 粤文 subtitles."""

from __future__ import annotations

from pprint import pformat

import numpy as np

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.core import ScinoephileError
from scinoephile.llms.base import TestCase
from scinoephile.llms.dual_pair import DualPairManager
from scinoephile.multilang.pairs import get_pair_strings
from scinoephile.multilang.synchronization import (
    SyncGroup,
    get_overlap_string,
    get_sync_groups_string,
    get_sync_overlap_matrix,
)
from scinoephile.multilang.yue_zho.transcription.merging import (
    YueZhoHansMergingPrompt,
    YueZhoMergingManager,
)
from scinoephile.multilang.yue_zho.transcription.shifting import (
    YueZhoHansShiftingPrompt,
)

__all__ = ["Alignment"]


class Alignment:
    """Nascent alignment between 中文 and 粤文 subtitles."""

    def __init__(self, zhongwen: AudioSeries, yuewen: AudioSeries):
        """Initialize.

        Arguments:
            zhongwen: 中文 subs
            yuewen: 粤文 subs
        """
        self._zhongwen = zhongwen
        self._yuewen = yuewen

        self._sync_groups_override = None

    def __str__(self):
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
        """Overlap matrix between 中文 and 粤文."""
        overlap = get_sync_overlap_matrix(self.zhongwen, self.yuewen)
        return overlap

    @property
    def scaled_overlap(self) -> np.ndarray:
        """Scaled overlap matrix between 中文 and 粤文."""
        scaled_overlap = self.overlap.copy()
        column_maxes = scaled_overlap.max(axis=0)
        column_maxes[column_maxes == 0] = 1
        scaled_overlap /= column_maxes
        return scaled_overlap

    @property
    def sync_groups(self) -> list[SyncGroup]:
        """Sync groups between 中文 and 粤文."""
        if self._sync_groups_override:
            # TODO: Validate that override is consistent with current series
            # TODO: Consider clearing automatically when zhongwen or yuewen change
            # TODO: Make public setter for _sync_groups_override
            return self._sync_groups_override

        # Each sync group must be one 中文 and zero or more 粤文.
        nascent_sync_groups = [([i], []) for i, _ in enumerate(self.zhongwen)]

        # For each 粤文, find the corresponding 中文 and add it to the sync group.
        for yw_idx in range(len(self.yuewen)):
            sg_idx = np.argmax(self.overlap[:, yw_idx])
            nascent_sync_groups[sg_idx][1].append(yw_idx)

        return nascent_sync_groups

    @property
    def yuewen(self) -> AudioSeries:
        """粤文 series."""
        return self._yuewen

    @yuewen.setter
    def yuewen(self, value: AudioSeries):
        """Set 粤文 series and clear cached values.

        Arguments:
            value: 粤文 series
        """
        self._yuewen = value

    @property
    def yuewen_all_assigned_to_sync_groups(self) -> bool:
        """Whether all 粤文 subs are assigned to sync groups."""
        yw_idxs = set([yw_idx for sg in self.sync_groups for yw_idx in sg[1]])
        return yw_idxs == set(range(len(self.yuewen)))

    @property
    def yuewen_to_distribute(self) -> list[int]:
        """粤文 indices in need of distribution."""
        yw_idxs = set([yw_idx for sg in self.sync_groups for yw_idx in sg[1]])
        return sorted(set(range(len(self.yuewen))) - yw_idxs)

    @property
    def zhongwen(self) -> AudioSeries:
        """中文 series."""
        return self._zhongwen

    @zhongwen.setter
    def zhongwen(self, value: AudioSeries):
        """Set 中文 series and clear cached values.

        Arguments:
            value: 中文 series
        """
        self._zhongwen = value

    @property
    def zhongwen_all_assigned_to_sync_groups(self) -> bool:
        """Whether all 中文 subs are assigned to sync groups."""
        zw_idxs = set([zw_idx for sg in self.sync_groups for zw_idx in sg[0]])
        return zw_idxs == set(range(len(self.zhongwen)))

    def get_shifting_test_case(self, sg_1_idx: int) -> TestCase | None:
        """Get shifting query for a sync group index.

        Arguments:
            sg_1_idx: Index of sync group 1
        Returns:
            Query, or None if there are no 粤文 to shift
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

        # Get 中文 1
        sg_1_zw_idxs = sg_1[0]
        if len(sg_1_zw_idxs) != 1:
            raise ScinoephileError(
                f"Sync group {sg_1_idx} has {len(sg_1_zw_idxs)} 中文 subs, expected 1."
            )
        sg_1_zw_idx = sg_1[0][0]
        zw_1 = self.zhongwen[sg_1_zw_idx].text

        # Get 中文 2
        sg_2_zw_idxs = sg_2[0]
        if len(sg_2[0]) != 1:
            raise ScinoephileError(
                f"Sync group {sg_2_idx} has {len(sg_2_zw_idxs)} 中文 subs, expected 1."
            )
        sg_2_zw_idx = sg_2[0][0]
        if sg_1_zw_idx + 1 != sg_2_zw_idx:
            raise ScinoephileError(
                f"中文 indexes {sg_1_zw_idx} and {sg_2_zw_idx} are not consecutive."
            )
        zw_2 = self.zhongwen[sg_2_zw_idx].text

        # Get 粤文 1
        sg_1_yw_idxs = sg_1[1]
        yw_1 = "".join([self.yuewen[i].text for i in sg_1_yw_idxs])

        # Get 粤文 2
        sg_2_yw_idxs = sg_2[1]
        yw_2 = "".join([self.yuewen[i].text for i in sg_2_yw_idxs])

        # Return
        if len(sg_1_yw_idxs) == 0 and len(sg_2_yw_idxs) == 0:
            return None
        test_case_cls = DualPairManager.get_test_case_cls(
            prompt_cls=YueZhoHansShiftingPrompt
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

    def get_merging_test_case(self, sg_idx: int) -> TestCase | None:
        """Get merging query for a sync group.

        Arguments:
            sg_idx: Index of sync group
        Returns:
            Query, or None if there are no 粤文 to merge
        """
        # Get sync group
        if sg_idx < 0 or sg_idx >= len(self.sync_groups):
            raise ScinoephileError(
                f"Invalid sync group index {sg_idx} "
                f"for alignment with {len(self.sync_groups)} sync groups."
            )
        sg = self.sync_groups[sg_idx]

        # Get 中文
        zw_idxs = sg[0]
        if len(zw_idxs) != 1:
            raise ScinoephileError(
                f"Sync group {sg_idx} has {len(zw_idxs)} 中文 subs, expected 1."
            )
        zw_idx = sg[0][0]
        zw = self.zhongwen[zw_idx].text

        # Get 粤文
        yw_idxs = sg[1]
        if len(yw_idxs) == 0:
            return None
        yws = [self.yuewen[i].text for i in yw_idxs]

        # Return merge query
        test_case_cls = YueZhoMergingManager.get_test_case_cls(
            prompt_cls=YueZhoHansMergingPrompt
        )
        query_kwargs = {
            test_case_cls.prompt_cls.src_2: zw,
            test_case_cls.prompt_cls.src_1: yws,
        }
        # noinspection PyArgumentList
        test_case = test_case_cls(query=test_case_cls.query_cls(**query_kwargs))
        return test_case
