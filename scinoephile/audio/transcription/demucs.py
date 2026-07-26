#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Lazy access to the optional Demucs dependency."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

__all__ = [
    "get_demucs_apply_model",
    "get_demucs_model_loader",
]

if TYPE_CHECKING:
    from demucs_infer.apply import BagOfModels, Model
    from torch import Tensor

    type DemucsModel = BagOfModels | Model

_TRANSCRIPTION_EXTRA_MESSAGE = (
    "Demucs separation support requires optional transcription dependencies. "
    "Install scinoephile with the 'transcription' extra."
)


def get_demucs_apply_model() -> Callable[..., Tensor]:
    """Import the Demucs model application function on demand.

    Returns:
        Demucs model application function
    """
    try:
        from demucs_infer.apply import apply_model  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return apply_model


def get_demucs_model_loader() -> Callable[[str], DemucsModel]:
    """Import the Demucs model loader on demand.

    Returns:
        Demucs model loader
    """
    try:
        from demucs_infer.pretrained import get_model  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return get_model
