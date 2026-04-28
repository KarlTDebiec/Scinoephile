#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Data model for a persisted LLM test case."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["PersistedTestCase"]


@dataclass(frozen=True, slots=True)
class PersistedTestCase:
    """A persisted test case row loaded from SQLite."""

    test_case_id: str
    """Deterministic identifier derived from query+answer JSON."""
    difficulty: int
    """Difficulty level for filtering and prioritization."""
    prompt: bool
    """Whether the test case is included in the prompt."""
    verified: bool
    """Whether the test case answer has been verified."""
    query: dict
    """Query JSON."""
    answer: dict
    """Answer JSON."""
    source_paths: list[str]
    """Source JSON paths that contributed this test case."""
