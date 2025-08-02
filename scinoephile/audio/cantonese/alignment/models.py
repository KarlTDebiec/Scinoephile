#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Models related to translation of Cantonese audio."""

from __future__ import annotations

from pydantic import Field, create_model

from scinoephile.audio.cantonese.alignment.alignment import Alignment
from scinoephile.audio.cantonese.translation.abcs import TranslateTestCase
from scinoephile.core import ScinoephileError
from scinoephile.core.abcs import Answer, Query


def get_translate_query_model(size: int, missing: tuple[int, ...]) -> type[Query]:
    if any(m < 0 or m > size for m in missing):
        raise ScinoephileError(
            f"Missing indices must be in range 1 to {size}, got {missing}."
        )
    query_fields = {}
    for zw_idx in range(size):
        query_fields[f"zhongwen_{zw_idx + 1}"] = (
            str,
            Field(..., description=f"Known 中文 of text {zw_idx + 1}"),
        )
        if zw_idx not in missing:
            query_fields[f"yuewen_{zw_idx + 1}"] = (
                str,
                Field(..., description=f"Known 粤文 of text {zw_idx + 1}"),
            )
    return create_model(
        f"TranslateTestQuery_{size}_{'-'.join(map(str, [m + 1 for m in missing]))}",
        __base__=Query,
        **query_fields,
    )


def get_translate_answer_model(size: int, missing: tuple[int, ...]) -> type[Answer]:
    if any(m < 0 or m > size for m in missing):
        raise ScinoephileError(
            f"Missing indices must be in range 1 to {size}, got {missing}."
        )
    answer_fields = {}
    for zw_idx in range(size):
        if zw_idx in missing:
            answer_fields[f"yuewen_{zw_idx + 1}"] = (
                str,
                Field(..., description=f"Translated 粤文 of text {zw_idx + 1}"),
            )
    return create_model(
        f"TranslateTestAnswer_{size}_{'-'.join(map(str, [m + 1 for m in missing]))}",
        __base__=Answer,
        **answer_fields,
    )


def get_translate_test_case_model(
    size: int,
    missing: tuple[int, ...],
    query_model: type[Query] | None = None,
    answer_model: type[Answer] | None = None,
) -> type[TranslateTestCase[Query, Answer]]:
    if query_model is None:
        query_model = get_translate_query_model(size, missing)
    query_model = get_translate_query_model(size, missing)
    if answer_model is None:
        answer_model = get_translate_answer_model(size, missing)
    return create_model(
        f"TranslateTestCase_{size}_{'-'.join(map(str, [m + 1 for m in missing]))}",
        __base__=(
            query_model,
            answer_model,
            TranslateTestCase[query_model, answer_model],
        ),
    )


def get_translate_models(
    alignment: Alignment,
) -> tuple[type[Query], type[Answer], type[TranslateTestCase[Query, Answer]]] | None:
    """Get translation query, answer, and test case for a nascent Cantonese alignment.

    Arguments:
        alignment: Nascent Cantonese alignment
    Returns:
        Query, Answer, and TranslateTestCase types for translation
    Raises:
        ScinoephileError: If sync groups are malformed
    """
    sgs = alignment.sync_groups
    query_fields = {}
    answer_fields = {}

    size = len(sgs)
    if len(sgs) == 0:
        raise ScinoephileError("Alignment has no sync groups.")

    missing = []
    for sg_idx, sg in enumerate(sgs):
        # Get 中文
        zw_idxs = sg[0]
        if len(zw_idxs) != 1:
            raise ScinoephileError(
                f"Sync group {sg_idx} has {len(zw_idxs)} 中文 subs, expected 1."
            )
        zw_idx = zw_idxs[0]

        # Get 粤文
        yw_idxs = sg[1]
        if len(yw_idxs) == 0:
            missing.append(zw_idx)
        elif len(yw_idxs) != 1:
            raise ScinoephileError(
                f"Sync group {sg_idx} has {len(yw_idxs)} 粤文 subs, expected 1."
            )

    if missing:
        query_model = get_translate_query_model(size, tuple(missing))
        answer_model = get_translate_answer_model(size, tuple(missing))
        test_case_model = get_translate_test_case_model(
            size, tuple(missing), query_model, answer_model
        )
        return query_model, answer_model, test_case_model
    return None


__all__ = [
    "get_translate_answer_model",
    "get_translate_models",
    "get_translate_query_model",
    "get_translate_test_case_model",
]
