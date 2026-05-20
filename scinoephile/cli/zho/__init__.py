#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Chinese command-line interfaces.

Package hierarchy (modules may import from any above):
* zho_process_cli / zho_translate_vs_eng_cli / zho_translate_vs_yue_cli
* zho_cli
"""

from __future__ import annotations

from .zho_cli import ZhoCli
from .zho_process_cli import ZhoProcessCli
from .zho_translate_vs_eng_cli import ZhoTranslateVsEngCli
from .zho_translate_vs_yue_cli import ZhoTranslateVsYueCli

__all__ = [
    "ZhoCli",
    "ZhoProcessCli",
    "ZhoTranslateVsEngCli",
    "ZhoTranslateVsYueCli",
]
