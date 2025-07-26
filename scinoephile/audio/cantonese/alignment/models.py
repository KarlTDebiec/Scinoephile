#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Models related to alignment of Cantonese audio."""

from __future__ import annotations

from pydantic import Field, create_model

from scinoephile.audio.cantonese.alignment.alignment import Alignment
from scinoephile.core import ScinoephileError
from scinoephile.core.abcs import Answer, Query, TestCase


def get_translate_models(
    alignment: Alignment,
) -> tuple[type[Query], type[Answer], type[TestCase[Query, Answer]]]:
    """Get translation query, answer, and test case for a nascent Cantonese alignment.

    Arguments:
        alignment: Nascent Cantonese alignment
    Returns:
        Query, Answer, and TestCase types for translation
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
            raise ScinoephileError(
                f"Sync group {sg_idx} has {len(zw_idxs)} 中文 subs, expected 1."
            )
        zw_idx = zw_idxs[0]
        query_fields[f"zhongwen_{zw_idx + 1}"] = (
            str,
            Field(..., description=f"Known 中文 of text {zw_idx + 1}"),
        )

        # Get 粤文
        yw_idxs = sg[1]
        if len(yw_idxs) == 0:
            answer_fields[f"yuewen_{zw_idx + 1}"] = (
                str,
                Field(..., description=f"Translated 粤文 of text {zw_idx + 1}"),
            )
        elif len(yw_idxs) == 1:
            query_fields[f"yuewen_{zw_idx + 1}"] = (
                str,
                Field(..., description=f"Known 粤文 of text {zw_idx + 1}"),
            )
        else:
            raise ScinoephileError(
                f"Sync group {sg_idx} has {len(yw_idxs)} 粤文 subs, expected 1."
            )

    query_model = create_model("TranslateQuery", __base__=Query, **query_fields)
    answer_model = create_model("TranslateAnswer", __base__=Answer, **answer_fields)
    test_case_model = create_model(
        "TranslateTestCase",
        __base__=TestCase[query_model, answer_model],
        include_in_prompt=(
            bool,
            Field(
                False, description="Whether to include test case in prompt examples."
            ),
        ),
        **query_fields,
        **answer_fields,
    )
    return query_model, answer_model, test_case_model


__all__ = [
    "get_translate_models",
]
