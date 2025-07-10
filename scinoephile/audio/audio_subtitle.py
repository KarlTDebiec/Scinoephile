#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Individual subtitle with audio."""

from __future__ import annotations

from dataclasses import fields
from typing import Any
from warnings import catch_warnings, filterwarnings

with catch_warnings():
    filterwarnings("ignore", category=SyntaxWarning)
    from pydub import AudioSegment

from scinoephile.audio.models.transcribed_segment import TranscribedSegment
from scinoephile.core import Subtitle


class AudioSubtitle(Subtitle):
    """Individual subtitle with audio."""

    def __init__(
        self,
        audio: AudioSegment | None = None,
        segment: TranscribedSegment | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize.

        Arguments:
            audio: Audio
            segment: Transcribed segment
            **kwargs: Additional keyword arguments
        """
        super_field_names = {f.name for f in fields(Subtitle)}
        super_kwargs = {k: v for k, v in kwargs.items() if k in super_field_names}
        super().__init__(**super_kwargs)

        self._audio = audio
        self._segment = segment

    @property
    def audio(self) -> AudioSegment:
        """Audio of subtitle."""
        return self._audio

    @audio.setter
    def audio(self, audio: AudioSegment) -> None:
        """Set audio of subtitle.

        Arguments:
            audio: Audio of subtitle
        """
        self._audio = audio

    @property
    def segment(self) -> TranscribedSegment:
        """Transcribed segment of subtitle."""
        return self._segment

    @segment.setter
    def segment(self, segment: TranscribedSegment) -> None:
        """Set transcribed segment of subtitle.

        Arguments:
            segment: Transcribed segment of subtitle
        """
        self._segment = segment
