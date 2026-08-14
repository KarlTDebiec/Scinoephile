#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Reference-free fusion of timestamped transcription sources.

Package hierarchy (modules may import from any above):
* timing
* transcriber
* factory
"""

from __future__ import annotations

from .transcriber import MultiSourceTranscriber

__all__ = ["MultiSourceTranscriber"]
