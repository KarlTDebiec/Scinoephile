#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interfaces for Scinoephile.

Package hierarchy (modules may import from any above):
* helpers
* audit / dictionary / media / multi / ocr / process_cli / proofread_cli
  / translate_cli / utility / yue
* scinoephile_cli
"""

from __future__ import annotations

from .scinoephile_cli import ScinoephileCli

__all__ = ["ScinoephileCli"]
