#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for Scinoephile.

This module may import from: common, core, lang
"""

from __future__ import annotations

from scinoephile.cli.analysis_cli import AnalysisCli
from scinoephile.cli.analysis_diff_cli import AnalysisDiffCli
from scinoephile.cli.dictionary_build_cli import DictionaryBuildCli
from scinoephile.cli.dictionary_build_cuhk_cli import DictionaryBuildCuhkCli
from scinoephile.cli.dictionary_build_gzzj_cli import DictionaryBuildGzzjCli
from scinoephile.cli.dictionary_cli import DictionaryCli
from scinoephile.cli.dictionary_search_cli import DictionarySearchCli
from scinoephile.cli.eng_cli import EngCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.sync_cli import SyncCli
from scinoephile.cli.timewarp_cli import TimewarpCli
from scinoephile.cli.zho_cli import ZhoCli

__all__ = [
    "AnalysisCli",
    "AnalysisDiffCli",
    "DictionaryCli",
    "DictionaryBuildCli",
    "DictionaryBuildCuhkCli",
    "DictionaryBuildGzzjCli",
    "DictionarySearchCli",
    "EngCli",
    "ScinoephileCli",
    "SyncCli",
    "TimewarpCli",
    "ZhoCli",
]
