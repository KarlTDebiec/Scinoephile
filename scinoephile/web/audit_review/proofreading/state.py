#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Settings and progress for the subtitle proofreading job."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.llms.providers.registry import DEFAULT_PROVIDER_NAME
from scinoephile.web.jobs import BackgroundJobState

__all__ = ["ProofreadingJobState"]


@dataclass(frozen=True)
class ProofreadingJobState(BackgroundJobState):
    """Snapshot of configuration and progress for one local run."""

    available: bool = True
    """Whether the configured subtitle output is absent."""
    provider: str = DEFAULT_PROVIDER_NAME
    """Selected provider name."""
    model: str = ""
    """Entered model override, blank for the provider default."""
    effort: str = ""
    """Requested reasoning effort, blank for the provider default."""
    rerun: bool = False
    """Whether the run replaces an existing proofreading output."""
