#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Common transcription backend interface."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from .transcribed_segment import TranscribedSegment

__all__ = ["BaseTranscriber"]

if TYPE_CHECKING:
    from pydub import AudioSegment


class BaseTranscriber(Protocol):
    """Common interface for timestamped transcription backends."""

    def __call__(
        self, audio: AudioSegment, *, cache_audio: AudioSegment | None = None
    ) -> list[TranscribedSegment]:
        """Transcribe audio.

        Arguments:
            audio: audio to transcribe
            cache_audio: optional audio used for cache-key generation
        Returns:
            transcription, split into timestamped segments
        """
        ...

    def get_cached_transcription(
        self, cache_audio: AudioSegment
    ) -> list[TranscribedSegment] | None:
        """Get cached transcription for audio if available.

        Arguments:
            cache_audio: audio used for cache-key generation
        Returns:
            cached transcription, if present
        """
        ...

    def transcribe(
        self, audio: AudioSegment, *, cache_audio: AudioSegment | None = None
    ) -> list[TranscribedSegment]:
        """Transcribe audio.

        Arguments:
            audio: audio to transcribe
            cache_audio: optional audio used for cache-key generation
        Returns:
            transcription, split into timestamped segments
        """
        ...
