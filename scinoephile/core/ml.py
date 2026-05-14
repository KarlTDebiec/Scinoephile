#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Machine learning helpers."""

from __future__ import annotations

from functools import cache

__all__ = ["get_torch_device"]


@cache
def get_torch_device() -> str:
    """Get torch device identifier.

    Returns:
        torch device identifier
    """
    try:
        import torch  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            "Torch device detection requires optional ML runtime dependencies. "
            "Install scinoephile with the 'transcription' or 'demucs' extra."
        ) from exc

    if torch.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"
