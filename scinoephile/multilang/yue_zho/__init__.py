#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 粤文/中文 text."""

from __future__ import annotations

from .proofreading import get_yue_proofread_vs_zho
from .review import get_yue_reviewed_vs_zho
from .transcription import get_yue_transcribed_vs_zho
from .translation import get_yue_translated_vs_zho

__all__ = [
    "get_yue_proofread_vs_zho",
    "get_yue_reviewed_vs_zho",
    "get_yue_transcribed_vs_zho",
    "get_yue_translated_vs_zho",
]
