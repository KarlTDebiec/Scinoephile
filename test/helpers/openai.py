#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""OpenAI client fixtures for offline provider tests."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

__all__ = ["DummyOpenAI"]


class DummyOpenAI:
    """Dummy OpenAI client capturing constructor kwargs."""

    def __init__(self, **kwargs: Any):
        """Initialize and capture kwargs."""
        self.kwargs = kwargs
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=None))
        self.beta = SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(parse=None))
        )
