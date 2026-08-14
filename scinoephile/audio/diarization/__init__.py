#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Source-wide speaker diarization.

Package hierarchy (modules may import from any above):
* exceptions / models
* cache
* pyannote
"""

from __future__ import annotations

from .cache import SpeakerDiarizationCache
from .exceptions import (
    SpeakerDiarizationAuthorizationError,
    SpeakerDiarizationDependencyError,
    SpeakerDiarizationError,
    SpeakerDiarizationInferenceError,
)
from .models import SpeakerDiarizationResult, SpeakerTurn
from .pyannote import PyannoteDiarizer

__all__ = [
    "PyannoteDiarizer",
    "SpeakerDiarizationAuthorizationError",
    "SpeakerDiarizationCache",
    "SpeakerDiarizationDependencyError",
    "SpeakerDiarizationError",
    "SpeakerDiarizationInferenceError",
    "SpeakerDiarizationResult",
    "SpeakerTurn",
]
