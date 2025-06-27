#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Individual subtitle with audio."""

from __future__ import annotations

from dataclasses import fields
from typing import Any

from pydub import AudioSegment

from scinoephile.core import Subtitle


class AudioSubtitle(Subtitle):
    """Individual subtitle with audio."""

    def __init__(self, audio: AudioSegment, **kwargs: Any) -> None:
        """Initialize.

        Arguments:
            audio: Audio of subtitle
            **kwargs: Additional keyword arguments
        """
        super_field_names = {f.name for f in fields(Subtitle)}
        super_kwargs = {k: v for k, v in kwargs.items() if k in super_field_names}
        super().__init__(**super_kwargs)

        self.audio = audio

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
