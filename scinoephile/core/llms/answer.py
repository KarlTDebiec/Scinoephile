#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for LLM answers."""

from __future__ import annotations

import json
from abc import ABC
from typing import ClassVar

from .models import LLMModel
from .prompt import Prompt

__all__ = ["Answer"]


class Answer(LLMModel, ABC):
    """ABC for LLM answers."""

    prompt: ClassVar[Prompt]
    """Text for LLM correspondence."""

    def __str__(self) -> str:
        """String representation."""
        return json.dumps(
            self.model_dump(by_alias=True),
            indent=2,
            ensure_ascii=False,
        )
