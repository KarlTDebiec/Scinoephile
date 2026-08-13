#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Exceptions raised by speaker diarization backends."""

from __future__ import annotations

from scinoephile.core.exceptions import ScinoephileError

__all__ = [
    "SpeakerDiarizationAuthorizationError",
    "SpeakerDiarizationDependencyError",
    "SpeakerDiarizationError",
    "SpeakerDiarizationInferenceError",
]


class SpeakerDiarizationError(ScinoephileError):
    """Raised when speaker diarization cannot produce usable output."""


class SpeakerDiarizationAuthorizationError(SpeakerDiarizationError):
    """Raised when Hugging Face has not authorized the configured model."""


class SpeakerDiarizationDependencyError(SpeakerDiarizationError):
    """Raised when optional speaker diarization dependencies are unavailable."""


class SpeakerDiarizationInferenceError(SpeakerDiarizationError):
    """Raised when speaker diarization inference fails or is malformed."""
