#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CUHK dictionary package."""

from __future__ import annotations

from .builder import CuhkDictionaryBuilder
from .service import CuhkDictionaryService

__all__ = [
    "CuhkDictionaryBuilder",
    "CuhkDictionaryService",
]
