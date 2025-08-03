#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Models related to translation of Cantonese audio."""

from __future__ import annotations

from scinoephile.audio.cantonese.alignment.alignment import Alignment
from scinoephile.audio.cantonese.review.abcs import ReviewTestCase
from scinoephile.audio.cantonese.translation.abcs import TranslateTestCase
from scinoephile.core import ScinoephileError
from scinoephile.core.abcs import Answer, Query


def get_review_models(
    alignment: Alignment,
) -> tuple[type[Query], type[Answer], type[ReviewTestCase[Query, Answer]]]:
    """Get review query, answer, and test case for a nascent Cantonese alignment.

    Arguments:
        alignment: Nascent Cantonese alignment
    Returns:
        Query, Answer, and ReviewTestCase types for review
    Raises:
        ScinoephileError: If sync groups are malformed
    """
    sgs = alignment.sync_groups

    # Validate sync groups
    size = len(sgs)
    if len(sgs) == 0:
        raise ScinoephileError("Alignment has no sync groups.")
    for sg_idx, sg in enumerate(sgs):
        # Validate 中文
        zw_idxs = sg[0]
        if len(zw_idxs) != 1:
            raise ScinoephileError(
                f"Sync group {sg_idx} has {len(zw_idxs)} 中文 subs, expected 1."
            )
        # Validate 粤文
        yw_idxs = sg[1]
        if len(yw_idxs) != 1:
            raise ScinoephileError(
                f"Sync group {sg_idx} has {len(yw_idxs)} 粤文 subs, expected 1."
            )

    # Get classes
    query_cls = ReviewTestCase.get_query_cls(size)
    answer_cls = ReviewTestCase.get_answer_cls(size)
    test_case_cls = ReviewTestCase.get_test_case_cls(size, query_cls, answer_cls)
    return query_cls, answer_cls, test_case_cls


def get_translate_models(
    alignment: Alignment,
) -> tuple[type[Query], type[Answer], type[TranslateTestCase[Query, Answer]]] | None:
    """Get translation query, answer, and test case for a nascent Cantonese alignment.

    Arguments:
        alignment: Nascent Cantonese alignment
    Returns:
        Query, Answer, and TranslateTestCase types for translation, or None if no
        translation is needed
    Raises:
        ScinoephileError: If sync groups are malformed
    """
    sgs = alignment.sync_groups

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

    # Get classes
    if missing:
        missing = tuple(missing)
        query_cls = TranslateTestCase.get_query_cls(size, missing)
        answer_cls = TranslateTestCase.get_answer_cls(size, missing)
        test_case_cls = TranslateTestCase.get_test_case_cls(
            size, missing, query_cls, answer_cls
        )
        return query_cls, answer_cls, test_case_cls

    return None


__all__ = [
    "get_review_models",
    "get_translate_models",
]
