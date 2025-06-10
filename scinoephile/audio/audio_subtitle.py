# Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
# and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Individual subtitle with audio clip."""
from __future__ import annotations

from dataclasses import fields
from typing import Any

from pydub.audio_segment import AudioSegment

from scinoephile.core import Subtitle


class AudioSubtitle(Subtitle):
    """Individual subtitle with audio clip."""

    def __init__(self, audio: AudioSegment, **kwargs: Any) -> None:
        """Initialize.

        Arguments:
            audio: Audio segment for this subtitle
            **kwargs: Additional keyword arguments
        """
        super_field_names = {f.name for f in fields(Subtitle)}
        super_kwargs = {k: v for k, v in kwargs.items() if k in super_field_names}
        super().__init__(**super_kwargs)

        self.audio = audio
