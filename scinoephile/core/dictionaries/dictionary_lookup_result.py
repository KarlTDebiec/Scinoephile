#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Model class for one source-tagged dictionary lookup result."""

from __future__ import annotations

from dataclasses import dataclass

from .dictionary_entry import DictionaryEntry
from .dictionary_source import DictionarySource

__all__ = [
    "DictionaryLookupResult",
]


@dataclass(frozen=True)
class DictionaryLookupResult:
    """One dictionary lookup result paired with source metadata."""

    source_id: str
    """Normalized source identifier used for filtering and display."""

    source: DictionarySource
    """Dictionary source metadata associated with the result."""

    entry: DictionaryEntry
    """Dictionary entry returned from the source."""
