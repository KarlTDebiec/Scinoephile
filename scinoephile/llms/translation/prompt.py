#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for translation matters."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.core.llms import Prompt

__all__ = ["TranslationPrompt"]


class TranslationPrompt(Prompt, ABC):
    """Text for LLM correspondence for translation matters."""

    __slots__ = ()

    # Query fields
    input_pfx: ClassVar[str] = "input_"
    """Prefix for input fields in query."""

    input_desc_tpl: ClassVar[str] = "Input {idx}"
    """Description template for input fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "output_"
    """Prefix for output fields in answer."""

    output_desc_tpl: ClassVar[str] = "Output {idx}"
    """Description template for output fields in answer."""

    # Query fields
    def input(self, idx: int) -> str:
        """Name of input field in query."""
        return f"{self.input_pfx}{idx}"

    def input_desc(self, idx: int) -> str:
        """Description of input field in query."""
        return self.input_desc_tpl.format(idx=idx)

    # Answer fields
    def output(self, idx: int) -> str:
        """Name of output field in answer."""
        return f"{self.output_pfx}{idx}"

    def output_desc(self, idx: int) -> str:
        """Description of output field in answer."""
        return self.output_desc_tpl.format(idx=idx)
