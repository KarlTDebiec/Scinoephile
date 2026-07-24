#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Exceptions raised by audio transcription backends."""

from __future__ import annotations

from scinoephile.core.exceptions import ScinoephileError

__all__ = [
    "EmptyTranscriptError",
    "TranscriptionAlignmentError",
    "TranscriptionError",
    "TranscriptionInferenceError",
]


class TranscriptionError(ScinoephileError):
    """Raised when a transcription backend cannot produce usable output."""


class EmptyTranscriptError(TranscriptionError):
    """Raised when a transcription backend returns no transcript text."""


class TranscriptionAlignmentError(TranscriptionError):
    """Raised when transcription output cannot be timestamp-aligned."""


class TranscriptionInferenceError(TranscriptionError):
    """Raised when transcription inference fails or returns malformed output."""
