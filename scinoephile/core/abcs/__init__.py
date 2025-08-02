#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base classes (ABCs) for core code."""

from __future__ import annotations

from scinoephile.core.abcs.answer import Answer
from scinoephile.core.abcs.dynamic_test_case import DynamicTestCase
from scinoephile.core.abcs.llm_provider import LLMProvider
from scinoephile.core.abcs.llm_queryer import LLMQueryer
from scinoephile.core.abcs.query import Query
from scinoephile.core.abcs.test_case import TestCase

__all__ = [
    "Answer",
    "DynamicTestCase",
    "LLMProvider",
    "LLMQueryer",
    "Query",
    "TestCase",
]
