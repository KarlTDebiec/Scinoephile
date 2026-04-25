#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Backend detection for audio transcription."""

from __future__ import annotations

from functools import cache

import torch


@cache
def get_backend() -> str:
    """Get Whisper / torch backend name.

    Returns:
        backend name
    """
    if torch.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"
