#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for LLM queries."""

from __future__ import annotations

import json
from abc import ABC
from typing import ClassVar

from .models import LLMModel, make_hashable
from .prompt import Prompt

__all__ = ["Query"]


class Query(LLMModel, ABC):
    """ABC for LLM queries."""

    prompt: ClassVar[Prompt]
    """Text for LLM correspondence."""

    def __str__(self) -> str:
        """String representation."""
        return json.dumps(
            self.model_dump(by_alias=True),
            indent=2,
            ensure_ascii=False,
        )

    @property
    def key(self) -> tuple:
        """Unique key for the query, with hashable values."""
        data = self.model_dump(mode="json")
        return tuple(
            make_hashable(data[field]) for field in sorted(type(self).model_fields)
        )

    @property
    def key_str(self) -> str:
        """Unique string key for the query."""
        return json.dumps(self.key, ensure_ascii=False)
