#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Exceptions raised by source-wide audio classification."""

from __future__ import annotations

from scinoephile.core import ScinoephileError

__all__ = ["AudioClassificationError", "AudioClassificationInferenceError"]


class AudioClassificationError(ScinoephileError):
    """Base exception for source-wide audio classification failures."""


class AudioClassificationInferenceError(AudioClassificationError):
    """Raised when an audio-classification model cannot run successfully."""
