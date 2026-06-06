#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interfaces for Scinoephile.

Package hierarchy (modules may import from any above):
* conversion / helpers / multi
* dictionary / eng / media / ocr / utility / yue / zho
* scinoephile_cli
"""

from __future__ import annotations

from .scinoephile_cli import ScinoephileCli

__all__ = ["ScinoephileCli"]
