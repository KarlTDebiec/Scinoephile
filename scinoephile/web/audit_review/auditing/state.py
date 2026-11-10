#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Settings and progress for the subtitle audit job."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.llms.providers.registry import DEFAULT_PROVIDER_NAME
from scinoephile.web.jobs import BackgroundJobState

__all__ = ["AuditingJobState"]


@dataclass(frozen=True)
class AuditingJobState(BackgroundJobState):
    """Immutable configuration and progress for the independent audit card."""

    available: bool = False
    """Whether proofreading exists and unaudited subtitles remain."""
    has_output: bool = False
    """Whether persisted audit findings exist and a new full run would replace them."""
    provider: str = DEFAULT_PROVIDER_NAME
    """Registered provider selected in the form."""
    model: str = ""
    """Model override, blank for the provider default."""
    effort: str = ""
    """Reasoning override, blank for the provider default."""
    rerun: bool = False
    """Whether this run replaces existing findings across the entire file."""
