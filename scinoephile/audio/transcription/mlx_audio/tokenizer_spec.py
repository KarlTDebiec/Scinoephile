#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""MLX-Audio tokenizer specifications."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["MIMO_AUDIO_TOKENIZER", "MlxAudioTokenizerSpec"]


@dataclass(frozen=True, slots=True)
class MlxAudioTokenizerSpec:
    """Complete specification of one MLX-Audio tokenizer."""

    name: str
    """Hugging Face model name."""
    revision: str
    """Required immutable model revision."""


MIMO_AUDIO_TOKENIZER = MlxAudioTokenizerSpec(
    name="mlx-community/MiMo-Audio-Tokenizer",
    revision="6d451ed9a73024b4d33b87afa69e0dfd40d8f306",
)
"""Default MLX MiMo audio-tokenizer specification."""
