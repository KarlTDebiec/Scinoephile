#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for README translation; may also be used for few-shot prompt."""

from __future__ import annotations

from scinoephile.core.abcs import TestCase
from scinoephile.documentation.translation.translate_answer import TranslateAnswer
from scinoephile.documentation.translation.translate_query import TranslateQuery


class TranslateTestCase(
    TranslateQuery, TranslateAnswer, TestCase[TranslateQuery, TranslateAnswer]
):
    """Test case for README translation; may also be used for few-shot prompt."""
