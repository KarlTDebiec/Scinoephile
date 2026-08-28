#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Exceptions raised by MLX-Audio transcription."""

from __future__ import annotations

from scinoephile.audio.transcription.exceptions import TranscriptionRecognitionError

__all__ = ["MlxAudioTokenLimitError"]


class MlxAudioTokenLimitError(TranscriptionRecognitionError):
    """Raised when MLX-Audio exhausts its text-token generation budget."""
