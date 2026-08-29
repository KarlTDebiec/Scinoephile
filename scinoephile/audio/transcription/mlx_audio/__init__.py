#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""MLX-Audio transcription and timestamp alignment.

Package hierarchy (modules may import from any above):
* exceptions / tokenization / timing / types
* model_spec
* model
* transcriber
"""

from __future__ import annotations

from .model import MlxAudioModel
from .model_spec import (
    FIRERED_ASR2_MODEL,
    GLM_ASR_MODEL,
    MIMO_MODEL,
    QWEN3_ASR_MODEL,
    SENSEVOICE_MODEL,
    MlxAudioModelSpec,
)
from .transcriber import MlxAudioTranscriber

__all__ = [
    "FIRERED_ASR2_MODEL",
    "GLM_ASR_MODEL",
    "MIMO_MODEL",
    "MlxAudioModel",
    "MlxAudioModelSpec",
    "MlxAudioTranscriber",
    "QWEN3_ASR_MODEL",
    "SENSEVOICE_MODEL",
]
