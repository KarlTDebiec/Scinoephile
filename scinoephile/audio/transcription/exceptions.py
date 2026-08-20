#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Exceptions raised by audio transcription backends."""

from __future__ import annotations

from scinoephile.core.exceptions import ScinoephileError

__all__ = [
    "TranscriptionRecognitionTokenLimitError",
    "TranscriptionAlignmentError",
    "TranscriptionAlignmentIncompleteError",
    "TranscriptionEmptyError",
    "TranscriptionError",
    "TranscriptionRecognitionError",
]


class TranscriptionError(ScinoephileError):
    """Raised when a transcription backend cannot produce usable output."""


class TranscriptionAlignmentError(TranscriptionError):
    """Raised when transcription output cannot be timestamp-aligned."""


class TranscriptionAlignmentIncompleteError(TranscriptionAlignmentError):
    """Raised when CTC alignment cannot consume every transcript token."""


class TranscriptionEmptyError(TranscriptionError):
    """Raised when a transcription backend returns no transcript text."""


class TranscriptionRecognitionError(TranscriptionError):
    """Raised when transcription recognition fails or returns malformed output."""


class TranscriptionRecognitionTokenLimitError(TranscriptionRecognitionError):
    """Raised when transcription exhausts its generation token limit."""
