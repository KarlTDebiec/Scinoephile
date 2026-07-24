#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of audio transcription exceptions."""

from __future__ import annotations

from scinoephile.audio.transcription import (
    TranscriptionAlignmentError,
    TranscriptionEmptyError,
    TranscriptionError,
    TranscriptionInferenceError,
)


def test_specialized_transcription_errors_share_base_class():
    """Test backend-neutral transcription errors share one catchable base class."""
    assert issubclass(TranscriptionEmptyError, TranscriptionError)
    assert issubclass(TranscriptionAlignmentError, TranscriptionError)
    assert issubclass(TranscriptionInferenceError, TranscriptionError)
