#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Reusable subtitle items for LLM test cases."""

from __future__ import annotations

from pydantic import Field

from .models import LLMModel

__all__ = [
    "AnnotatedTestCaseSubtitle",
    "TestCaseSubtitle",
]


class TestCaseSubtitle(LLMModel):
    """Indexed subtitle text in an LLM test case."""

    index: int = Field(ge=1)
    """One-based subtitle index."""
    text: str = Field(max_length=1000)
    """Subtitle text."""


class AnnotatedTestCaseSubtitle(TestCaseSubtitle):
    """Indexed subtitle text with an explanatory note."""

    text: str = Field(min_length=1, max_length=1000)
    """Full annotated subtitle text."""
    note: str = Field(min_length=1, max_length=1000)
    """Note concerning the subtitle text."""
