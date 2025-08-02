#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for LLM test cases whose fields are dynamically created."""

from abc import ABC

from scinoephile.core.abcs.answer import Answer
from scinoephile.core.abcs.query import Query
from scinoephile.core.abcs.test_case import TestCase


class DynamicTestCase[TQuery: Query, TAnswer: Answer](TestCase[TQuery, TAnswer], ABC):
    """Abstract base class for LLM test cases whose fields are dynamically created."""
