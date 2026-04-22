#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Dictionary build command-line interfaces."""

from __future__ import annotations

from .dictionary_build_cli import DictionaryBuildCli
from .dictionary_build_cuhk_cli import DictionaryBuildCuhkCli
from .dictionary_build_gzzj_cli import DictionaryBuildGzzjCli
from .dictionary_build_kaifangcidian_cli import DictionaryBuildKaifangcidianCli

__all__ = [
    "DictionaryBuildCli",
    "DictionaryBuildCuhkCli",
    "DictionaryBuildGzzjCli",
    "DictionaryBuildKaifangcidianCli",
]
