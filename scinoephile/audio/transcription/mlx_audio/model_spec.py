#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""MLX-Audio speech-to-text model specifications."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.language import Language
from scinoephile.core.ml import ModelSpec

__all__ = [
    "FIRERED_ASR2_MODEL",
    "GLM_ASR_MODEL",
    "MIMO_AUDIO_TOKENIZER",
    "MIMO_MODEL",
    "MlxAudioModelSpec",
    "QWEN3_ASR_MODEL",
    "SENSEVOICE_MODEL",
]

MIMO_AUDIO_TOKENIZER = ModelSpec(
    name="mlx-community/MiMo-Audio-Tokenizer",
    revision="6d451ed9a73024b4d33b87afa69e0dfd40d8f306",
)
"""Default MLX MiMo audio-tokenizer specification."""


@dataclass(frozen=True, slots=True)
class MlxAudioModelSpec(ModelSpec):
    """Complete specification of one MLX-Audio STT model."""

    model_type: str
    """Model type passed to the MLX-Audio loader."""
    languages: dict[Language, str | None]
    """Model-specific language values keyed by Scinoephile language."""
    tokenizer: ModelSpec | None = None
    """Auxiliary audio-tokenizer specification, when required."""
    max_tokens: int | None = None
    """Maximum generated tokens, or None for the model's native behavior."""
    max_tokens_arg: str | None = "max_tokens"
    """MLX-Audio generation-limit argument name, or None when unsupported."""
    max_safe_audio_duration_seconds: float | None = None
    """Maximum safe audio duration per inference, or None when unrestricted."""

    def __post_init__(self):
        """Validate the model definition."""
        if self.max_tokens is not None:
            if self.max_tokens <= 0:
                raise ValueError("MLX-Audio max tokens must be positive.")
            if self.max_tokens_arg is None:
                raise ValueError(
                    f"MLX-Audio {self.model_type} does not support a generation token "
                    "limit."
                )
        if (
            self.max_safe_audio_duration_seconds is not None
            and self.max_safe_audio_duration_seconds <= 0
        ):
            raise ValueError("MLX-Audio max safe audio duration must be positive.")


FIRERED_ASR2_MODEL = MlxAudioModelSpec(
    name="mlx-community/FireRedASR2-AED-mlx",
    model_type="fireredasr2",
    languages=dict.fromkeys(Language),
    revision="f3212eacfa49b851130b97c63653c8e06ee09bdb",
    max_tokens_arg="max_len",
)
"""Default MLX FireRedASR2-AED model."""

GLM_ASR_MODEL = MlxAudioModelSpec(
    name="mlx-community/GLM-ASR-Nano-2512-8bit",
    model_type="glm",
    languages=dict.fromkeys(Language),
    revision="fa36e850714806d8e50aac6573a8c0177d2e5e1a",
    max_tokens=128,
)
"""Default MLX GLM-ASR-Nano-2512 model."""

MIMO_MODEL = MlxAudioModelSpec(
    name="mlx-community/MiMo-V2.5-ASR-MLX",
    model_type="mimo",
    languages={
        Language.eng: "en",
        Language.yue_hans: "zh",
        Language.yue_hant: "zh",
        Language.zho_hans: "zh",
        Language.zho_hant: "zh",
    },
    revision="69813f0d57fb9bb5328735c4e907a4558b47d341",
    tokenizer=MIMO_AUDIO_TOKENIZER,
    max_tokens=256,
    max_safe_audio_duration_seconds=55.0,
)
"""Default MLX MiMo model."""

QWEN3_ASR_MODEL = MlxAudioModelSpec(
    name="mlx-community/Qwen3-ASR-0.6B-8bit",
    model_type="qwen3_asr",
    languages={
        Language.eng: "English",
        Language.yue_hans: "Cantonese",
        Language.yue_hant: "Cantonese",
        Language.zho_hans: "Chinese",
        Language.zho_hant: "Chinese",
    },
    revision="89e96d92ba34aca20b3e29fb10cc284097d1219f",
    max_tokens=8192,
)
"""Default MLX Qwen3-ASR model."""

SENSEVOICE_MODEL = MlxAudioModelSpec(
    name="mlx-community/SenseVoiceSmall",
    model_type="sensevoice",
    languages={
        Language.eng: "en",
        Language.yue_hans: "yue",
        Language.yue_hant: "yue",
        Language.zho_hans: "zh",
        Language.zho_hant: "zh",
    },
    revision="8ddd966bd96243cff196422f81f0c5d955814792",
    max_tokens_arg=None,
)
"""Default MLX SenseVoiceSmall model."""
