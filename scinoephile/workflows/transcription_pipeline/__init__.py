#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Complete reference-free multi-source transcription workflow.

Package hierarchy (modules may import from any above):
* pipeline
* factory
"""

from __future__ import annotations

from .factory import get_transcription_pipeline
from .pipeline import TranscriptionPipeline

__all__ = ["TranscriptionPipeline", "get_transcription_pipeline"]
