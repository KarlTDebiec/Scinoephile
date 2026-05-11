#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle analysis data types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NotRequired, TypedDict

__all__ = [
    "ImageSubtitleManifest",
    "SubtitleScriptAnalysis",
    "SubtitleStreamStats",
]


class ImageSubtitleManifest(TypedDict):
    """Rendered image subtitle cache manifest."""

    version: int
    """Manifest schema version."""
    event_count: int
    """Number of subtitle events."""
    image_count: int
    """Number of cached image files."""
    first_start_ms: NotRequired[int | None]
    """First subtitle start time in milliseconds."""
    last_end_ms: NotRequired[int | None]
    """Last subtitle end time in milliseconds."""
    artifact_name: NotRequired[str]
    """Source artifact filename."""
    artifact_size: NotRequired[int]
    """Source artifact size in bytes."""


@dataclass(frozen=True)
class SubtitleScriptAnalysis:
    """Subtitle stream script analysis result."""

    script: str | None
    """Detected script tag, when determined."""
    simplified_count: int
    """Number of simplified-only Hanzi observed."""
    traditional_count: int
    """Number of traditional-only Hanzi observed."""
    shared_count: int
    """Number of non-decisive Hanzi observed."""
    sample_indexes: tuple[int, ...] = ()
    """Indexes sampled for OCR, if applicable."""
    ocr_languages: tuple[str, ...] = ()
    """OCR languages used, if applicable."""
    failure_reason: str | None = None
    """Reason script could not be determined."""


@dataclass(frozen=True)
class SubtitleStreamStats:
    """Derived subtitle stream statistics."""

    event_count: int
    """Number of subtitle events."""
    first_start_ms: int | None
    """First subtitle start time in milliseconds."""
    last_end_ms: int | None
    """Last subtitle end time in milliseconds."""
