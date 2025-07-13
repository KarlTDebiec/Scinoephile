#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for LLM queries."""

from __future__ import annotations

import json
from abc import ABC

from pydantic import BaseModel


class Query(BaseModel, ABC):
    """Abstract base class for LLM queries."""

    def __str__(self) -> str:
        """String representation."""
        return json.dumps(self.model_dump(), indent=2, ensure_ascii=False)
