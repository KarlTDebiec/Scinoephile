#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Individual subtitle with audio."""

from __future__ import annotations

from dataclasses import fields
from typing import Any

from scinoephile.core import Subtitle
from pydub import AudioSegment


class AudioSubtitle(Subtitle):
    """Individual subtitle with audio."""

    def __init__(self, aud: AudioSegment, **kwargs: Any) -> None:
        """Initialize.

        Arguments:
            audio: Audio of subtitle
            **kwargs: Additional keyword arguments
        """
        super_field_names = {f.name for f in fields(Subtitle)}
        super_kwargs = {k: v for k, v in kwargs.items() if k in super_field_names}
        super().__init__(**super_kwargs)

        self.aud = aud

    @property
    def aud(self) -> AudioSegment:
        """Audio of subtitle."""
        return self._aud

    @aud.setter
    def aud(self, aud: AudioSegment) -> None:
        """Set audio of subtitle.

        Arguments:
            aud: Audio of subtitle
        """
        self._aud = aud
