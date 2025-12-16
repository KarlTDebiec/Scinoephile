#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to subtitle review using LLMs.

Review takes in two series with 1:1 correspondence, processes them blockwise, and yields
a revised version of the first series.
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
