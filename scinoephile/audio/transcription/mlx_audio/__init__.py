#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""MLX-Audio speech-to-text inference.

Package hierarchy (modules may import from any above):
* backend
"""

from __future__ import annotations

from .backend import (
    MIMO_MODEL_NAME,
    QWEN3_ASR_MODEL_NAME,
    MlxAudioBackend,
    MlxAudioInferenceResult,
)

__all__ = [
    "MIMO_MODEL_NAME",
    "QWEN3_ASR_MODEL_NAME",
    "MlxAudioBackend",
    "MlxAudioInferenceResult",
]
