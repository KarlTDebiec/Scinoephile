#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""MLX-Audio transcription and timestamp alignment.

Package hierarchy (modules may import from any above):
* forced_alignment / inference
* transcriber
"""

from __future__ import annotations

from .inference import MlxAudioInferenceResult
from .transcriber import (
    MlxAudioModelProfile,
    MlxAudioTranscriber,
)

__all__ = [
    "MlxAudioInferenceResult",
    "MlxAudioModelProfile",
    "MlxAudioTranscriber",
]
