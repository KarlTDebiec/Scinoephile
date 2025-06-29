#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Payload for audio transcription."""

from __future__ import annotations

from typing import TYPE_CHECKING, NotRequired, TypedDict

from scinoephile.audio.models.transcribed_segment import TranscribedSegment
from scinoephile.core.synchronization import SyncGroup

if TYPE_CHECKING:
    from scinoephile.audio import AudioSeries


class TranscriptionPayload(TypedDict):
    """Payload for audio transcription."""

    source: AudioSeries
    """Source series."""
    segments: NotRequired[list[TranscribedSegment]]
    """Transcribed segments."""
    series: NotRequired[AudioSeries | None]
    """Transcribed series."""
    sync_groups: NotRequired[SyncGroup]
    """Sync groups."""
