#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runtime choices and model defaults for MiMo transcription."""

from __future__ import annotations

from enum import StrEnum

__all__ = [
    "MIMO_MLX_MODEL_NAME",
    "MIMO_MODEL_NAME",
    "MIMO_TOKENIZER_NAME",
    "MimoRuntime",
]

MIMO_MLX_MODEL_NAME = "mlx-community/MiMo-V2.5-ASR-MLX"
"""Default Apple Silicon MLX MiMo ASR model name."""

MIMO_MODEL_NAME = MIMO_MLX_MODEL_NAME
"""Default MiMo ASR model name."""

MIMO_TOKENIZER_NAME = "XiaomiMiMo/MiMo-Audio-Tokenizer"
"""Default MiMo audio tokenizer model name."""


class MimoRuntime(StrEnum):
    """Runtime implementations for MiMo ASR."""

    AUTO = "auto"
    """Use MLX on supported Apple Silicon machines."""
    MLX = "mlx"
    """Use the Apple Silicon MLX MiMo runtime."""
