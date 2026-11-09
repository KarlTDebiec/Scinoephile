#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for independent proofreading audits."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.llms import Prompt

__all__ = ["ReviewAuditPrompt"]


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewAuditPrompt(Prompt):
    """Audit instructions and retry guidance for a proofread subtitle block."""
