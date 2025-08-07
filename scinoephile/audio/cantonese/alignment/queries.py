#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Queries related to alignment of Cantonese audio."""

from __future__ import annotations

from scinoephile.audio.cantonese.alignment.alignment import Alignment
from scinoephile.audio.cantonese.distribution import DistributeQuery
from scinoephile.audio.cantonese.merging import MergeQuery
from scinoephile.audio.cantonese.proofing import ProofQuery
from scinoephile.audio.cantonese.review.abcs import ReviewQuery
from scinoephile.audio.cantonese.shifting import ShiftQuery
from scinoephile.audio.cantonese.translation.abcs import TranslateQuery
from scinoephile.core import ScinoephileError


def get_distribute_query(
    alignment: Alignment, sg_1_idx: int, sg_2_idx: int, yw_idx: int
) -> DistributeQuery:
    """Get distribute query for an alignment at provided indexes.

    Arguments:
        alignment: Nascent Cantonese alignment
        sg_1_idx: Index of sync group 1
        sg_2_idx: Index of sync group 2
        yw_idx: Index of 粤文 sub to distribute
    Returns:
        Query
    """
    # Get sync groups
    if sg_1_idx < 0 or sg_1_idx >= len(alignment.sync_groups):
        raise ScinoephileError(
            f"Invalid sync group index {sg_1_idx} "
            f"for alignment with {len(alignment.sync_groups)} sync groups."
        )
    if sg_2_idx < 0 or sg_2_idx >= len(alignment.sync_groups):
        raise ScinoephileError(
            f"Invalid sync group index {sg_2_idx} "
            f"for alignment with {len(alignment.sync_groups)} sync groups."
        )
    if sg_1_idx + 1 != sg_2_idx:
        raise ScinoephileError(
            f"Sync groups {sg_1_idx} and {sg_2_idx} are not consecutive."
        )
    sg_1 = alignment.sync_groups[sg_1_idx]
    sg_2 = alignment.sync_groups[sg_2_idx]

    # Get 中文 1
    sg_1_zw_idxs = sg_1[0]
    if len(sg_1_zw_idxs) != 1:
        raise ScinoephileError(
            f"Sync group {sg_1_idx} has {len(sg_1_zw_idxs)} 中文 subs, expected 1."
        )
    sg_1_zw_idx = sg_1_zw_idxs[0]
    zw_1 = alignment.zhongwen[sg_1_zw_idx].text

    # Get 中文 2
    sg_2_zw_idxs = sg_2[0]
    if len(sg_2_zw_idxs) != 1:
        raise ScinoephileError(
            f"Sync group {sg_2_idx} has {len(sg_2_zw_idxs)} 中文 subs, expected 1."
        )
    sg_2_zw_idx = sg_2_zw_idxs[0]
    if sg_1_zw_idx + 1 != sg_2_zw_idx:
        raise ScinoephileError(
            f"中文 indexes {sg_1_zw_idx} and {sg_2_zw_idx} are not consecutive."
        )
    zw_2 = alignment.zhongwen[sg_2_zw_idx].text

    # Get 粤文 1
    sg_1_yw_idxs = sg_1[1]
    yw_1_start = "".join([alignment.yuewen[i].text for i in sg_1_yw_idxs])

    # Get 粤文 2
    sg_2_yw_idxs = sg_2[1]
    yw_2_end = "".join([alignment.yuewen[i].text for i in sg_2_yw_idxs])

    # Get 粤文 to distribute
    if yw_idx not in alignment.yuewen_to_distribute:
        raise ScinoephileError(
            f"Invalid 粤文 index {yw_idx} "
            f"not in yuewen_to_review: {alignment.yuewen_to_distribute}"
        )
    yw_to_distribute = alignment.yuewen[yw_idx].text

    # Return merge query
    return DistributeQuery(
        zhongwen_1=zw_1,
        yuewen_1_start=yw_1_start,
        zhongwen_2=zw_2,
        yuewen_2_end=yw_2_end,
        yuewen_to_distribute=yw_to_distribute,
    )


def get_shift_query(alignment: Alignment, sg_1_idx: int) -> ShiftQuery | None:
    """Get shift query for an alignment at provided sync group index.

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
    return ShiftQuery(zhongwen_1=zw_1, yuewen_1=yw_1, zhongwen_2=zw_2, yuewen_2=yw_2)


def get_merge_query(
    alignment: Alignment,
    sg_idx: int,
) -> MergeQuery | None:
    """Get merge query for an alignment's sync group.

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
    return MergeQuery(zhongwen=zw, yuewen_to_merge=yws)


def get_proof_query(
    alignment: Alignment,
    sg_idx: int,
) -> ProofQuery | None:
    """Get proof query for an alignment's sync group.

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
    return ProofQuery(zhongwen=zw, yuewen=yw)


def get_review_query(alignment: Alignment, query_cls: type[ReviewQuery]) -> ReviewQuery:
    """Get review query for a nascent Cantonese alignment.

    Arguments:
        alignment: Nascent Cantonese alignment
        query_cls: ReviewQuery class to instantiate
    Returns:
        Query instance
    Raises:
        ScinoephileError: If sync groups are malformed
    """
    if not issubclass(query_cls, ReviewQuery):
        raise ScinoephileError("query_cls must be a subclass of Query.")

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

    return query_cls(**kwargs)


def get_translate_query(
    alignment: Alignment, query_cls: type[TranslateQuery]
) -> TranslateQuery:
    """Get translation query for a nascent Cantonese alignment.

    Arguments:
        alignment: Nascent Cantonese alignment
        query_cls: TranslateQuery class to instantiate
    Returns:
        Query instance
    Raises:
        ScinoephileError: If sync groups are malformed
    """
    if not issubclass(query_cls, TranslateQuery):
        raise ScinoephileError("query_cls must be a subclass of TranslateQuery.")

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

    return query_cls(**kwargs)


__all__ = [
    "get_distribute_query",
    "get_shift_query",
    "get_merge_query",
    "get_proof_query",
    "get_review_query",
    "get_translate_query",
]
