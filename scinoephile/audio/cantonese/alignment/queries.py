#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Queries related to alignment of Cantonese audio."""

from __future__ import annotations

from scinoephile.audio.cantonese.alignment.alignment import Alignment
from scinoephile.audio.cantonese.distribution import DistributeQuery
from scinoephile.audio.cantonese.merging import MergeQuery
from scinoephile.audio.cantonese.proofing import ProofQuery
from scinoephile.audio.cantonese.shifting import ShiftQuery
from scinoephile.core import ScinoephileError
from scinoephile.core.abcs import Query


def get_distribute_query(
    alignment: Alignment,
    one_sg_idx: int,
    two_sg_idx: int,
    yw_idx: int,
) -> DistributeQuery:
    """Get distribute query for an alignment at provided indexes.

    Arguments:
        alignment: Nascent Cantonese alignment
        one_sg_idx: Index of sync group one
        two_sg_idx: Index of sync group two
        yw_idx: Index of 粤文 sub to distribute
    Returns:
        Query
    """
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

    # Get 中文
    one_zw_idxs = one_sg[0]
    if len(one_zw_idxs) != 1:
        raise ScinoephileError(
            f"Sync group {one_sg_idx} has {len(one_zw_idxs)} 中文 subs, expected 1."
        )
    one_zw_idx = one_zw_idxs[0]
    two_zw_idxs = two_sg[0]
    if len(two_zw_idxs) != 1:
        raise ScinoephileError(
            f"Sync group {two_sg_idx} has {len(two_zw_idxs)} 中文 subs, expected 1."
        )
    two_sg_idx = two_zw_idxs[0]
    if one_zw_idx + 1 != two_sg_idx:
        raise ScinoephileError(
            f"中文 indexes {one_zw_idx} and {two_sg_idx} are not consecutive."
        )
    one_zhongwen = alignment.zhongwen[one_sg_idx].text
    two_zhongwen = alignment.zhongwen[two_sg_idx].text

    # Get 粤文
    one_yw_idxs = one_sg[1]
    one_yuewen_start = "".join([alignment.yuewen[i].text for i in one_yw_idxs])
    two_yw_idxs = two_sg[1]
    two_yuewen_end = "".join([alignment.yuewen[i].text for i in two_yw_idxs])
    if yw_idx not in alignment.yuewen_to_distribute:
        raise ScinoephileError(
            f"Invalid 粤文 index {yw_idx} "
            f"not in yuewen_to_review: {alignment.yuewen_to_distribute}"
        )
    yuewen_to_split = alignment.yuewen[yw_idx].text

    # Return merge query
    return DistributeQuery(
        one_zhongwen=one_zhongwen,
        one_yuewen_start=one_yuewen_start,
        two_zhongwen=two_zhongwen,
        two_yuewen_end=two_yuewen_end,
        yuewen_to_distribute=yuewen_to_split,
    )


def get_shift_query(
    alignment: Alignment,
    one_sg_idx: int,
    two_sg_idx: int,
) -> ShiftQuery | None:
    """Get shift query for an alignment at provided indexes.

    Arguments:
        alignment: Nascent Cantonese alignment
        one_sg_idx: Index of sync group one
        two_sg_idx: Index of sync group two
    Returns:
        Query, or None if there are no 粤文 to shift
    """
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

    # Get 中文
    one_zw_idxs = one_sg[0]
    if len(one_zw_idxs) != 1:
        raise ScinoephileError(
            f"Sync group {one_sg_idx} has {len(one_zw_idxs)} 中文 subs, expected 1."
        )
    one_zw_idx = one_sg[0][0]
    two_zw_idxs = two_sg[0]
    if len(two_sg[0]) != 1:
        raise ScinoephileError(
            f"Sync group {two_sg_idx} has {len(two_zw_idxs)} 中文 subs, expected 1."
        )
    two_zw_idx = two_sg[0][0]
    if one_zw_idx + 1 != two_zw_idx:
        raise ScinoephileError(
            f"中文 indexes {one_zw_idx} and {two_zw_idx} are not consecutive."
        )
    one_zhongwen = alignment.zhongwen[one_zw_idx].text
    two_zhongwen = alignment.zhongwen[two_zw_idx].text

    # Get 粤文
    one_yw_idxs = one_sg[1]
    two_yw_idxs = two_sg[1]
    if len(one_yw_idxs) == 0 and len(two_yw_idxs) == 0:
        return None
    one_yuewen = "".join([alignment.yuewen[i].text for i in one_yw_idxs])
    two_yuewen = "".join([alignment.yuewen[i].text for i in two_yw_idxs])

    # Return shift query
    return ShiftQuery(
        one_zhongwen=one_zhongwen,
        one_yuewen=one_yuewen,
        two_zhongwen=two_zhongwen,
        two_yuewen=two_yuewen,
    )


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
    sync_group = alignment.sync_groups[sg_idx]

    # Get 中文
    zw_idxs = sync_group[0]
    if len(zw_idxs) != 1:
        raise ScinoephileError(
            f"Sync group {sg_idx} has {len(zw_idxs)} 中文 subs, expected 1."
        )
    zw_idx = sync_group[0][0]
    zhongwen = alignment.zhongwen[zw_idx].text

    # Get 粤文
    yw_idxs = sync_group[1]
    if len(yw_idxs) == 0:
        return None
    yuewen_to_merge = [alignment.yuewen[i].text for i in yw_idxs]

    # Return merge query
    return MergeQuery(zhongwen=zhongwen, yuewen_to_merge=yuewen_to_merge)


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
    sync_group = alignment.sync_groups[sg_idx]

    # Get 中文
    zw_idxs = sync_group[0]
    if len(zw_idxs) != 1:
        raise ScinoephileError(
            f"Sync group {sg_idx} has {len(zw_idxs)} 中文 subs, expected 1."
        )
    zw_idx = sync_group[0][0]
    zhongwen = alignment.zhongwen[zw_idx].text

    # Get 粤文
    yw_idxs = sync_group[1]
    if len(yw_idxs) > 1:
        raise ScinoephileError(
            f"Sync group {sg_idx} has {len(yw_idxs)} 粤文 subs, expected 0 or 1."
        )
    if len(yw_idxs) == 0:
        return None
    yuewen = alignment.yuewen[yw_idxs[0]].text

    # Return proof query
    return ProofQuery(zhongwen=zhongwen, yuewen=yuewen)


def get_translate_query(alignment: Alignment, query_cls: type[Query]) -> Query:
    """Get translation query for a nascent Cantonese alignment.

    Arguments:
        alignment: Nascent Cantonese alignment
        query_cls: Query class to instantiate
    Returns:
        Query instance
    Raises:
        ScinoephileError: If sync groups are malformed
    """
    if not issubclass(query_cls, Query):
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
    "get_translate_query",
]
