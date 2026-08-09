#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""MLX-Audio transcription and timestamp alignment.

Package hierarchy (modules may import from any above):
* backend
* transcriber
"""

from __future__ import annotations

from .backend import MlxAudioModel
from .transcriber import MlxAudioTranscriber

__all__ = ["MlxAudioModel", "MlxAudioTranscriber"]
