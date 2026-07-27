#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Demucs vocal separation for transcription preprocessing.

Package hierarchy (modules may import from any above):
* cache
* separator
"""

from __future__ import annotations

from .separator import DemucsSeparator

__all__ = ["DemucsSeparator"]
