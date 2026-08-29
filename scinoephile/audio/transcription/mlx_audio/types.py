#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Structural types used by MLX-Audio speech recognition."""

from __future__ import annotations

from typing import Protocol

__all__ = ["MlxAudioResult", "MlxAudioRuntimeModel"]


class MlxAudioResult(Protocol):
    """Structural result returned by MLX-Audio recognition."""

    text: str
    """Transcript text."""

    generation_tokens: int
    """Number of generated text tokens."""


class MlxAudioRuntimeModel(Protocol):
    """Loaded MLX-Audio model capable of speech recognition."""

    def generate(self, audio: str, **kwargs: object) -> MlxAudioResult:
        """Recognize speech in an audio file and return the result.

        Arguments:
            audio: audio file path
            **kwargs: model-specific generation arguments
        Returns:
            speech recognition result
        """
        ...
