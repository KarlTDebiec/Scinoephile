#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Machine learning helpers."""

from __future__ import annotations

from functools import cache

import torch

__all__ = ["get_torch_device"]


@cache
def get_torch_device() -> str:
    """Get torch device identifier.

    Returns:
        torch device identifier
    """
    if torch.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"
