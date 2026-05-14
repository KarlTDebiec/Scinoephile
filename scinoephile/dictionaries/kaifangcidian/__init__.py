#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Kaifangcidian dictionary package.

Package hierarchy (modules may import from any above):
* constants
* downloader / parser
* service
"""

from __future__ import annotations

from .service import KaifangcidianDictionaryService

__all__ = ["KaifangcidianDictionaryService"]
