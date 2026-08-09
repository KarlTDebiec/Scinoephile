#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""MLX-Audio speech-to-text model definitions."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from scinoephile.core.language import Language

__all__ = [
    "FIRERED_ASR2_MODEL",
    "GLM_ASR_MODEL",
    "MIMO_MODEL",
    "MlxAudioModel",
    "QWEN3_ASR_MODEL",
    "SENSEVOICE_MODEL",
]


@dataclass(frozen=True, slots=True)
class MlxAudioModel:
    """Complete definition of one MLX-Audio STT model."""

    model_name: str
    """Hugging Face model name or local model path."""
    family_name: str
    """Stable model-family name used in cache metadata."""
    model_type: str
    """Model type passed to the MLX-Audio loader."""
    languages: Mapping[Language, str | None]
    """Model-specific language values keyed by Scinoephile language."""
    default_max_tokens: int | None = None
    """Default maximum generated tokens, or None for the model's native behavior."""
    max_tokens_argument: str | None = "max_tokens"
    """MLX-Audio generation-limit parameter, or None when unsupported."""
    token_limit_guard_duration_seconds: float | None = None
    """Maximum guarded window duration, or None when no guard is required."""

    def __post_init__(self):
        """Freeze languages and validate the default generation limit."""
        object.__setattr__(self, "languages", MappingProxyType(dict(self.languages)))
        self.get_max_tokens()

    def get_max_tokens(self, max_tokens: int | None = None) -> int | None:
        """Get and validate the effective generation limit.

        Arguments:
            max_tokens: optional generation-limit override
        Returns:
            effective generation limit
        Raises:
            ValueError: if the limit is invalid or unsupported
        """
        if max_tokens is None:
            max_tokens = self.default_max_tokens
        if max_tokens is None:
            return None
        if max_tokens <= 0:
            raise ValueError("MLX-Audio max tokens must be positive.")
        if self.max_tokens_argument is None:
            raise ValueError(
                f"MLX-Audio {self.family_name} does not support a generation token "
                "limit."
            )
        return max_tokens


FIRERED_ASR2_MODEL = MlxAudioModel(
    model_name="mlx-community/FireRedASR2-AED-mlx",
    family_name="firered-asr2",
    model_type="fireredasr2",
    languages=dict.fromkeys(Language),
    max_tokens_argument="max_len",
)
"""Default MLX FireRedASR2-AED model."""

GLM_ASR_MODEL = MlxAudioModel(
    model_name="mlx-community/GLM-ASR-Nano-2512-8bit",
    family_name="glm-asr",
    model_type="glm",
    languages=dict.fromkeys(Language),
    default_max_tokens=128,
)
"""Default MLX GLM-ASR-Nano-2512 model."""

MIMO_MODEL = MlxAudioModel(
    model_name="mlx-community/MiMo-V2.5-ASR-MLX",
    family_name="mimo",
    model_type="mimo",
    languages={
        Language.eng: "en",
        Language.yue_hans: "zh",
        Language.yue_hant: "zh",
        Language.zho_hans: "zh",
        Language.zho_hant: "zh",
    },
    default_max_tokens=256,
    token_limit_guard_duration_seconds=55.0,
)
"""Default MLX MiMo model."""

QWEN3_ASR_MODEL = MlxAudioModel(
    model_name="mlx-community/Qwen3-ASR-0.6B-8bit",
    family_name="qwen3-asr",
    model_type="qwen3_asr",
    languages={
        Language.eng: "English",
        Language.yue_hans: "Cantonese",
        Language.yue_hant: "Cantonese",
        Language.zho_hans: "Chinese",
        Language.zho_hant: "Chinese",
    },
    default_max_tokens=8192,
)
"""Default MLX Qwen3-ASR model."""

SENSEVOICE_MODEL = MlxAudioModel(
    model_name="mlx-community/SenseVoiceSmall",
    family_name="sensevoice",
    model_type="sensevoice",
    languages={
        Language.eng: "en",
        Language.yue_hans: "yue",
        Language.yue_hant: "yue",
        Language.zho_hans: "zh",
        Language.zho_hant: "zh",
    },
    max_tokens_argument=None,
)
"""Default MLX SenseVoiceSmall model."""
