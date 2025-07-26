#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Queries related to alignment of Cantonese audio."""

from __future__ import annotations

from pydantic import BaseModel, Field

from scinoephile.audio.cantonese.alignment import Alignment
from scinoephile.core import ScinoephileError


def get_translate_query_and_answer(
    alignment: Alignment,
) -> tuple(type[BaseModel], type[BaseModel]):
    """Get translation query for an alignment.

    Arguments:
        alignment: Nascent Cantonese alignment
    Returns:
        Query and Answer types for translation
    Raises:
        ScinoephileError: If sync groups are malformed
    """
    sgs = alignment.sync_groups
    query_fields = {}
    answer_fields = {}
    for sg_idx, sg in enumerate(sgs):
        # Get 中文
        zw_idxs = sg[0]
        if len(zw_idxs) != 1:
            raise ValueError(
                f"Sync group {sg_idx} has {len(zw_idxs)} 中文 subs, expected 1."
            )
        zw_idx = zw_idxs[0]
        zhongwen = alignment.zhongwen[zw_idx].text
        query_fields[f"zhongwen_{zw_idx}"] = (
            Field(..., description="Known 中文 of text one"),
            zhongwen[zw_idx],
        )

        # Get 粤文
        yw_idxs = sg[1]
        if len(yw_idxs) == 0:
            answer_fields[f"yuewen_{zw_idx}"] = Field(
                ..., description="Translated 粤文 of text one"
            )
        if len(yw_idxs) > 1:
            raise ScinoephileError(
                f"Sync group {sg_idx} has {len(yw_idxs)} 粤文 subs, expected 1."
            )
        query_fields[f"yuewen_{yw_idxs[0]}"] = (
            Field(..., description="Known 粤文 of text one"),
            alignment.yuewen[yw_idxs[0]].text,
        )
