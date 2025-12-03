#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Nascent alignment between 中文 and 粤文 subtitles."""

from __future__ import annotations

from pprint import pformat

import numpy as np

from scinoephile.audio import (
    AudioSeries,
)
from scinoephile.core.pairs import get_pair_strings
from scinoephile.core.synchronization import (
    SyncGroup,
    get_overlap_string,
    get_sync_groups_string,
    get_sync_overlap_matrix,
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
