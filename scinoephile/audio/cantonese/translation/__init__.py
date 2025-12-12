#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to Cantonese audio transcription translation."""

from __future__ import annotations

from .answer2 import TranslationAnswer2
from .prompt2 import TranslationPrompt2
from .query2 import TranslationQuery2
from .test_case2 import TranslationTestCase2

__all__ = [
    "TranslationAnswer2",
    "TranslationPrompt2",
    "TranslationQuery2",
    "TranslationTestCase2",
]
