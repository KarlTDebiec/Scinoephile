#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for LLM queries."""

from __future__ import annotations

import json
from abc import ABC
from functools import cached_property

from pydantic import BaseModel

from scinoephile.core.models import make_hashable


class Query(BaseModel, ABC):
    """Abstract base class for LLM queries."""

    def __str__(self) -> str:
        """String representation."""
        return json.dumps(self.model_dump(), indent=2, ensure_ascii=False)

    @cached_property
    def query_key(self) -> tuple:
        """Unique key for the query, with hashable values."""
        return tuple(make_hashable(getattr(self, field)) for field in self.model_fields)

    @cached_property
    def query_key_str(self) -> str:
        """Unique string key for the query."""
        return json.dumps(self.query_key, ensure_ascii=False)
