#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for LLM test cases."""

from __future__ import annotations

import json
from abc import ABC
from typing import ClassVar

from pydantic import BaseModel

from .prompt import Prompt

__all__ = ["TestCase"]


class TestCase(BaseModel, ABC):
    """ABC for LLM test cases."""

    __test__ = False
    """Inform pytest not to collect this class as a test case."""

    prompt_cls: ClassVar[type[Prompt]]
    """Text for LLM correspondence."""

    def __str__(self) -> str:
        """String representation."""
        return json.dumps(self.model_dump(), indent=2, ensure_ascii=False)
