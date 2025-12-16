#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to many-to-many blockwise matters.

Many-to-many blockwise matters take in two subtitle Series with 1:1 pairing of
Subtitles, process them blockwise, and output a single Series.
"""

from __future__ import annotations

from .answer import ManyToManyBlockwiseAnswer
from .prompt import ManyToManyBlockwisePrompt
from .query import ManyToManyBlockwiseQuery
from .test_case import ManyToManyBlockwiseTestCase

__all__ = [
    "ManyToManyBlockwiseAnswer",
    "ManyToManyBlockwisePrompt",
    "ManyToManyBlockwiseQuery",
    "ManyToManyBlockwiseTestCase",
]
