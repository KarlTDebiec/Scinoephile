#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Character error rate result classes."""

from __future__ import annotations

from .line_cer import LineCER
from .series_cer import SeriesCER

__all__ = [
    "LineCER",
    "SeriesCER",
]
