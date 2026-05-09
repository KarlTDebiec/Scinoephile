#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Chinese script analysis."""

from __future__ import annotations

from .analysis import get_zho_script_analysis
from .result import ZhoScriptAnalysis

__all__ = ["ZhoScriptAnalysis", "get_zho_script_analysis"]
