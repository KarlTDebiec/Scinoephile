#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Voice activity detection provider contract."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

__all__ = ["VadProvider"]

if TYPE_CHECKING:
    from pydub import AudioSegment

    from .trace import VoiceActivityTrace


class VadProvider(Protocol):
    """Provider capable of inferring a frame-level voice activity trace."""

    def get_trace(self, audio: AudioSegment) -> VoiceActivityTrace:
        """Infer frame-level voice activity scores.

        Arguments:
            audio: source audio
        Returns:
            model scores aligned to the source timeline
        """
        ...
