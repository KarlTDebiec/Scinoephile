#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Complete reference-free multi-source transcription workflow.

Package hierarchy (modules may import from any above):
* models
* pipeline
* factory
"""

from __future__ import annotations

from .models import AudioAnalysisMode
from .pipeline import TranscriptionPipeline

__all__ = ["AudioAnalysisMode", "TranscriptionPipeline"]
