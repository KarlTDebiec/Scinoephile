#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Chinese subtitle script analysis results."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["ZhoScriptAnalysisResult"]


@dataclass(frozen=True)
class ZhoScriptAnalysisResult:
    """Chinese subtitle stream script analysis result."""

    script: str | None = None
    """Detected script tag, when determined."""
    simplified_count: int = 0
    """Number of simplified-only Hanzi observed."""
    traditional_count: int = 0
    """Number of traditional-only Hanzi observed."""
    shared_count: int = 0
    """Number of non-decisive Hanzi observed."""
    sample_indexes: tuple[int, ...] = ()
    """Indexes sampled for OCR, if applicable."""
    ocr_languages: tuple[str, ...] = ()
    """OCR languages used, if applicable."""
    failure_reason: str | None = None
    """Reason script could not be determined."""
