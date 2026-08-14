#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Exceptions raised by voice activity detection."""

from __future__ import annotations

from scinoephile.core.exceptions import ScinoephileError

__all__ = ["VoiceActivityError"]


class VoiceActivityError(ScinoephileError):
    """Raised when voice activity detection cannot produce usable output."""
