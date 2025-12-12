#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for LLM queries."""

from __future__ import annotations

import json
from abc import ABC
from typing import ClassVar

from pydantic import BaseModel

from scinoephile.core.models import make_hashable

from .prompt import Prompt

__all__ = ["Query"]


class Query(BaseModel, ABC):
    """Abstract base class for LLM queries."""

    prompt_cls: ClassVar[type[Prompt]]
    """Text strings to be used for corresponding with LLM."""

    def __str__(self) -> str:
        """String representation."""
        return json.dumps(self.model_dump(), indent=2, ensure_ascii=False)

    @property
    def key(self) -> tuple:
        """Unique key for the query, with hashable values."""
        # noinspection PyTypeChecker
        return tuple(
            make_hashable(getattr(self, field))
            for field in sorted(type(self).model_fields)
        )

    @property
    def key_str(self) -> str:
        """Unique string key for the query."""
        return json.dumps(self.key, ensure_ascii=False)
