#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to README translation."""

from __future__ import annotations

from .answer import TranslateAnswer
from .query import TranslateQuery
from .test_case import TranslateTestCase
from .translator import Translator

__all__ = [
    "TranslateAnswer",
    "TranslateQuery",
    "TranslateTestCase",
    "Translator",
]
