#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Dictionary command-line interfaces."""

from __future__ import annotations

from .dictionary_cli import DictionaryCli
from .dictionary_search_cli import DictionarySearchCli

__all__ = ["DictionaryCli", "DictionarySearchCli"]
