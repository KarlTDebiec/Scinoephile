#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for guided translation."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.core.llms import Prompt

__all__ = ["GuidedTranslationPrompt"]


class GuidedTranslationPrompt(Prompt, ABC):
    """Text for guided translation blocks."""

    __slots__ = ()

    # Query fields
    src_1_pfx: ClassVar[str] = "source_one_"
    """Prefix for source one fields in query."""

    src_1_desc_tpl: ClassVar[str] = "Subtitle {idx} text from source one"
    """Description template for source one fields in query."""

    src_2_pfx: ClassVar[str] = "source_two_"
    """Prefix for source two fields in query."""

    src_2_desc_tpl: ClassVar[str] = "Subtitle {idx} text from source two"
    """Description template for source two fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "output_"
    """Prefix for output fields in answer."""

    output_desc_tpl: ClassVar[str] = (
        "Subtitle {idx} generated for source one subtitle {idx}"
    )
    """Description template for output fields in answer."""

    def output(self, idx: int) -> str:
        """Name of output field in answer."""
        return f"{self.output_pfx}{idx}"

    def output_desc(self, idx: int) -> str:
        """Description of output subtitle field in answer."""
        return self.output_desc_tpl.format(idx=idx)

    def src_1(self, idx: int) -> str:
        """Name of source one field in query."""
        return f"{self.src_1_pfx}{idx}"

    def src_1_desc(self, idx: int) -> str:
        """Description of source one field in query."""
        return self.src_1_desc_tpl.format(idx=idx)

    def src_2(self, idx: int) -> str:
        """Name of source two field in query."""
        return f"{self.src_2_pfx}{idx}"

    def src_2_desc(self, idx: int) -> str:
        """Description of source two field in query."""
        return self.src_2_desc_tpl.format(idx=idx)
