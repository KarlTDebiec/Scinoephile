#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Chinese command-line interfaces."""

from __future__ import annotations

from .zho_cli import ZhoCli
from .zho_fuse_cli import ZhoFuseCli
from .zho_process_cli import ZhoProcessCli
from .zho_validate_ocr_cli import ZhoValidateOcrCli

__all__ = ["ZhoCli", "ZhoFuseCli", "ZhoProcessCli", "ZhoValidateOcrCli"]
