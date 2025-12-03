#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for README translation; may also be used for few-shot prompt."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.abcs import TestCase

from .answer import TranslateAnswer
from .query import TranslateQuery

__all__ = ["TranslateTestCase"]


class TranslateTestCase(
    TranslateQuery, TranslateAnswer, TestCase[TranslateQuery, TranslateAnswer]
):
    """Test case for README translation; may also be used for few-shot prompt."""

    answer_cls: ClassVar[type[TranslateAnswer]] = TranslateAnswer
    """Answer class for this test case."""
    query_cls: ClassVar[type[TranslateQuery]] = TranslateQuery
    """Query class for this test case."""
