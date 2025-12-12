#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to models related to Cantonese audio."""

from __future__ import annotations

from scinoephile.audio.cantonese.review import ReviewAnswer, ReviewQuery, ReviewTestCase
from scinoephile.audio.cantonese.translation import (
    TranslationAnswer,
    TranslationQuery,
    TranslationTestCase,
)
from scinoephile.core import ScinoephileError

from .alignment import Alignment

__all__ = [
    "get_review_models",
    "get_translate_models",
]


def get_review_models(
    alignment: Alignment,
) -> tuple[type[ReviewQuery], type[ReviewAnswer], type[ReviewTestCase]]:
    """Get review query, answer, and test case for a nascent Cantonese alignment.

    Arguments:
        alignment: Nascent Cantonese alignment
    Returns:
        ReviewQuery, ReviewAnswer, and ReviewTestCase types for review
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
    test_case_cls = ReviewTestCase.get_test_case_cls(size)
    query_cls = test_case_cls.query_cls
    answer_cls = test_case_cls.answer_cls
    return query_cls, answer_cls, test_case_cls


def get_translate_models(
    alignment: Alignment,
) -> (
    tuple[type[TranslationQuery], type[TranslationAnswer], type[TranslationTestCase]]
    | None
):
    """Get translation query, answer, and test case for a nascent Cantonese alignment.

    Arguments:
        alignment: Nascent Cantonese alignment
    Returns:
        TranslationQuery, TranslationAnswer, and TranslationTestCase types for
        translation, or None if no translation is needed
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
        test_case_cls = TranslationTestCase.get_test_case_cls(size, missing)
        query_cls = test_case_cls.query_cls
        answer_cls = test_case_cls.answer_cls
        return query_cls, answer_cls, test_case_cls

    return None
