#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Whisper transcription.

Package hierarchy (modules may import from any above):
* model_spec / normalization / types
* model
* ctc_fallback
* transcriber
"""

from __future__ import annotations

from .model import WhisperModel
from .model_spec import WhisperModelSpec
from .transcriber import WhisperTranscriber

__all__ = ["WhisperModel", "WhisperModelSpec", "WhisperTranscriber"]
