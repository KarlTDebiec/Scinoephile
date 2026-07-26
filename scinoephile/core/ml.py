#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Machine learning helpers."""

from __future__ import annotations

from collections.abc import Callable
from functools import cache
from typing import TYPE_CHECKING, Any

__all__ = [
    "get_torch_device",
    "get_torch_module",
    "get_torchaudio_resampler",
]

if TYPE_CHECKING:
    from torch import Tensor


@cache
def get_torch_device() -> str:
    """Get torch device identifier.

    Returns:
        torch device identifier
    """
    torch = get_torch_module()
    if torch.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


@cache
def get_torch_module() -> Any:
    """Import torch on demand."""
    try:
        import torch  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            "Torch support requires optional transcription dependencies. "
            "Install scinoephile with the 'transcription' extra."
        ) from exc
    return torch


@cache
def get_torchaudio_resampler() -> Callable[[Tensor, int, int], Tensor]:
    """Import the Torchaudio resampling function on demand.

    Returns:
        Torchaudio resampling function
    """
    try:
        from torchaudio.functional import resample  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            "Torchaudio support requires optional transcription dependencies. "
            "Install scinoephile with the 'transcription' extra."
        ) from exc
    return resample
