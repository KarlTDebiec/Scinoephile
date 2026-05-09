#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Chinese script analysis result."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["ZhoScriptAnalysis"]


@dataclass(frozen=True)
class ZhoScriptAnalysis:
    """Chinese script analysis result."""

    script: str | None
    """Detected BCP-47 Chinese script tag, when determined."""
    simplified_count: int
    """Number of simplified-only Hanzi observed."""
    traditional_count: int
    """Number of traditional-only Hanzi observed."""
    shared_count: int
    """Number of Hanzi that do not distinguish simplified from traditional."""
