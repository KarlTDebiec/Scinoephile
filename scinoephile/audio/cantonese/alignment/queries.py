#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Queries related to alignment of Cantonese audio."""

from __future__ import annotations

from scinoephile.audio.cantonese.merging import MergingTestCase
from scinoephile.audio.cantonese.proofing import ProofingTestCase2
from scinoephile.audio.cantonese.review import ReviewTestCase2
from scinoephile.audio.cantonese.shifting import ShiftingTestCase2
from scinoephile.audio.cantonese.translation import TranslationTestCase2
from scinoephile.core import ScinoephileError

from .alignment import Alignment

__all__ = [
    "get_shifting_query",
    "get_merging_query",
    "get_proofing_query",
    "get_review_test_case",
    "get_translation_query",
]


def get_shifting_query(alignment: Alignment, sg_1_idx: int) -> ShiftingTestCase2 | None:
    """Get shifting query for an alignment at provided sync group index.

    Arguments:
        alignment: Nascent Cantonese alignment
        sg_1_idx: Index of sync group 1
    Returns:
        Query, or None if there are no 粤文 to shift
    """
    # Get sync grou 1
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

    # Get 中文 1
    sg_1_zw_idxs = sg_1[0]
    if len(sg_1_zw_idxs) != 1:
        raise ScinoephileError(
            f"Sync group {sg_1_idx} has {len(sg_1_zw_idxs)} 中文 subs, expected 1."
        )
    sg_1_zw_idx = sg_1[0][0]
    zw_1 = alignment.zhongwen[sg_1_zw_idx].text

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
    zw_2 = alignment.zhongwen[sg_2_zw_idx].text

    # Get 粤文 1
    sg_1_yw_idxs = sg_1[1]
    yw_1 = "".join([alignment.yuewen[i].text for i in sg_1_yw_idxs])

    # Get 粤文 2
    sg_2_yw_idxs = sg_2[1]
    yw_2 = "".join([alignment.yuewen[i].text for i in sg_2_yw_idxs])

    # Return
    if len(sg_1_yw_idxs) == 0 and len(sg_2_yw_idxs) == 0:
        return None
    test_case_cls: type[ShiftingTestCase2] = ShiftingTestCase2.get_test_case_cls()
    # noinspection PyArgumentList
    test_case = test_case_cls(
        query=test_case_cls.query_cls(
            zhongwen_1=zw_1, yuewen_1=yw_1, zhongwen_2=zw_2, yuewen_2=yw_2
        )
    )
    return test_case


def get_merging_query(alignment: Alignment, sg_idx: int) -> MergingTestCase | None:
    """Get merging query for an alignment's sync group.

    Arguments:
        alignment: Nascent Cantonese alignment
        sg_idx: Index of sync group
    Returns:
        Query, or None if there are no 粤文 to merge
    """
    # Get sync group
    if sg_idx < 0 or sg_idx >= len(alignment.sync_groups):
        raise ScinoephileError(
            f"Invalid sync group index {sg_idx} "
            f"for alignment with {len(alignment.sync_groups)} sync groups."
        )
    sg = alignment.sync_groups[sg_idx]

    # Get 中文
    zw_idxs = sg[0]
    if len(zw_idxs) != 1:
        raise ScinoephileError(
            f"Sync group {sg_idx} has {len(zw_idxs)} 中文 subs, expected 1."
        )
    zw_idx = sg[0][0]
    zw = alignment.zhongwen[zw_idx].text

    # Get 粤文
    yw_idxs = sg[1]
    if len(yw_idxs) == 0:
        return None
    yws = [alignment.yuewen[i].text for i in yw_idxs]

    # Return merge query
    test_case_cls: type[MergingTestCase] = MergingTestCase.get_test_case_cls()
    # noinspection PyArgumentList
    test_case = test_case_cls(
        query=test_case_cls.query_cls(zhongwen=zw, yuewen_to_merge=yws)
    )
    return test_case


def get_proofing_query(alignment: Alignment, sg_idx: int) -> ProofingTestCase2 | None:
    """Get proofing query for an alignment's sync group.

    Arguments:
        alignment: Nascent Cantonese alignment
        sg_idx: Index of sync group
    Returns:
        Query, or None if there are no 粤文 to proof
    """
    # Get sync group
    if sg_idx < 0 or sg_idx >= len(alignment.sync_groups):
        raise ScinoephileError(
            f"Invalid sync group index {sg_idx} "
            f"for alignment with {len(alignment.sync_groups)} sync groups."
        )
    sg = alignment.sync_groups[sg_idx]

    # Get 中文
    zw_idxs = sg[0]
    if len(zw_idxs) != 1:
        raise ScinoephileError(
            f"Sync group {sg_idx} has {len(zw_idxs)} 中文 subs, expected 1."
        )
    zw_idx = sg[0][0]
    zw = alignment.zhongwen[zw_idx].text

    # Get 粤文
    yw_idxs = sg[1]
    if len(yw_idxs) > 1:
        raise ScinoephileError(
            f"Sync group {sg_idx} has {len(yw_idxs)} 粤文 subs, expected 0 or 1."
        )
    if len(yw_idxs) == 0:
        return None
    yw = alignment.yuewen[yw_idxs[0]].text

    # Return proof query
    test_case_cls: type[ProofingTestCase2] = ProofingTestCase2.get_test_case_cls()
    # noinspection PyArgumentList
    test_case = test_case_cls(query=test_case_cls.query_cls(zhongwen=zw, yuewen=yw))
    return test_case


def get_review_test_case(
    alignment: Alignment, test_case_cls: type[ReviewTestCase2]
) -> ReviewTestCase2:
    """Get review query for a nascent Cantonese alignment.

    Arguments:
        alignment: Nascent Cantonese alignment
        test_case_cls: ReviewQuery class to instantiate
    Returns:
        Query instance
    Raises:
        ScinoephileError: If sync groups are malformed
    """
    kwargs = {}
    for sg in alignment.sync_groups:
        # Get 中文
        zw_idxs = sg[0]
        if len(zw_idxs) != 1:
            raise ScinoephileError(
                f"Sync group {sg} has {len(zw_idxs)} 中文 subs, expected 1."
            )
        zw_idx = zw_idxs[0]
        kwargs[f"zhongwen_{zw_idx + 1}"] = alignment.zhongwen[zw_idx].text

        # Get 粤文
        yw_idxs = sg[1]
        if len(yw_idxs) != 1:
            raise ScinoephileError(
                f"Sync group {sg} has {len(yw_idxs)} 粤文 subs, expected 1."
            )
        yw_idx = yw_idxs[0]
        kwargs[f"yuewen_{zw_idx + 1}"] = alignment.yuewen[yw_idx].text

    test_case = test_case_cls(query=test_case_cls.query_cls(**kwargs))
    return test_case


def get_translation_query(
    alignment: Alignment, test_case_cls: type[TranslationTestCase2]
) -> TranslationTestCase2:
    """Get translation query for a nascent Cantonese alignment.

    Arguments:
        alignment: Nascent Cantonese alignment
        test_case_cls: TranslationQuery class to instantiate
    Returns:
        Query instance
    Raises:
        ScinoephileError: If sync groups are malformed
    """
    kwargs = {}
    for sg in alignment.sync_groups:
        # Get 中文
        zw_idxs = sg[0]
        if len(zw_idxs) != 1:
            raise ScinoephileError(
                f"Sync group {sg} has {len(zw_idxs)} 中文 subs, expected 1."
            )
        zw_idx = zw_idxs[0]
        kwargs[f"zhongwen_{zw_idx + 1}"] = alignment.zhongwen[zw_idx].text

        # Get 粤文
        yw_idxs = sg[1]
        if len(yw_idxs) == 0:
            continue
        elif len(yw_idxs) != 1:
            raise ScinoephileError(
                f"Sync group {sg} has {len(yw_idxs)} 粤文 subs, expected 0 or 1."
            )
        yw_idx = yw_idxs[0]
        kwargs[f"yuewen_{zw_idx + 1}"] = alignment.yuewen[yw_idx].text

    test_case = test_case_cls(query=test_case_cls.query_cls(**kwargs))
    return test_case
