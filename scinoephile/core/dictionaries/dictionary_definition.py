#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Model class for dictionary definitions."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["DictionaryDefinition"]


@dataclass(frozen=True)
class DictionaryDefinition:
    """Definition metadata tied to a dictionary entry."""

    text: str
    """Definition text associated with the dictionary entry."""

    label: str = ""
    """Optional part-of-speech or usage label for the definition."""
