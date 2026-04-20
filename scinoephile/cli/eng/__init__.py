#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""English command-line interfaces."""

from __future__ import annotations

from .eng_cli import EngCli
from .eng_fuse_cli import EngFuseCli
from .eng_validate_ocr_cli import EngValidateOcrCli

__all__ = [
    "EngCli",
    "EngFuseCli",
    "EngValidateOcrCli",
]
