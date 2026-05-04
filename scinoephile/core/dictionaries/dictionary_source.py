#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Model class for dictionary source metadata."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["DictionarySource"]


@dataclass(frozen=True)
class DictionarySource:
    """Metadata describing a dictionary source."""

    name: str
    """Full display name of the dictionary or dataset."""

    shortname: str
    """Concise identifier used in logs, filenames, or tables."""

    version: str
    """Source version or snapshot label for the metadata record."""

    description: str
    """Human-readable summary of the source contents or purpose."""

    legal: str
    """Licensing or copyright notice associated with the source."""

    link: str
    """Primary human-facing homepage for the source."""

    update_url: str
    """URL checked when refreshing or rebuilding source data."""

    other: str
    """Free-form notes for extra provenance or usage details."""
