#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Exceptions raised by the subtitle audit editor."""

from __future__ import annotations

__all__ = ["InvalidReviewSubtitleError"]


class InvalidReviewSubtitleError(ValueError):
    """A proofreading correction cannot be represented as one SRT subtitle."""
