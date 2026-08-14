#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Configuration models for complete transcription pipelines."""

from __future__ import annotations

from enum import StrEnum

__all__ = ["AudioAnalysisMode"]


class AudioAnalysisMode(StrEnum):
    """Optional source-wide audio-analysis behavior."""

    AUTO = "auto"
    """Use analysis when available and continue without it after failure."""
    ON = "on"
    """Require successful analysis."""
    OFF = "off"
    """Do not run analysis."""
