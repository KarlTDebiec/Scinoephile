#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Model class for dictionary source metadata."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "DictionarySource",
]


@dataclass(frozen=True)
class DictionarySource:
    """Metadata describing a dictionary source."""

    name: str
    shortname: str
    version: str
    description: str
    legal: str
    link: str
    update_url: str
    other: str
