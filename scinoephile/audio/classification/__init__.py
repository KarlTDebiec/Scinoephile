#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Source-wide spoken-language and audio-event classification.

Package hierarchy (modules may import from any above):
* exceptions / models
* cache
* firered
"""

from __future__ import annotations

from .cache import AudioClassificationCache
from .exceptions import (
    AudioClassificationDependencyError,
    AudioClassificationError,
    AudioClassificationInferenceError,
)
from .firered import FireRedAudioEventDetector, FireRedLanguageIdentifier
from .models import (
    AudioEvent,
    AudioEventDetectionResult,
    AudioEventSpan,
    LanguageIdentificationResult,
    LanguageSpan,
)

__all__ = [
    "AudioClassificationCache",
    "AudioClassificationDependencyError",
    "AudioClassificationError",
    "AudioClassificationInferenceError",
    "AudioEvent",
    "AudioEventDetectionResult",
    "AudioEventSpan",
    "FireRedAudioEventDetector",
    "FireRedLanguageIdentifier",
    "LanguageIdentificationResult",
    "LanguageSpan",
]
