#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base classes related to 粤文 translation."""

from __future__ import annotations

from scinoephile.audio.cantonese.translation.abcs.translate_answer import (
    TranslateAnswer,
)
from scinoephile.audio.cantonese.translation.abcs.translate_query import TranslateQuery
from scinoephile.audio.cantonese.translation.abcs.translate_test_case import (
    TranslateTestCase,
)

__all__ = [
    "TranslateAnswer",
    "TranslateQuery",
    "TranslateTestCase",
]
