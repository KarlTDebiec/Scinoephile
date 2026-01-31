#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for Scinoephile.

This module may import from: common, core, lang
"""

from __future__ import annotations

from scinoephile.cli.eng_cli import EngCli
from scinoephile.cli.eng_zho_cli import EngZhoCli
from scinoephile.cli.eng_zho_sync_cli import EngZhoSyncCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.zho_cli import ZhoCli

__all__ = [
    "EngCli",
    "EngZhoCli",
    "EngZhoSyncCli",
    "ScinoephileCli",
    "ZhoCli",
]
