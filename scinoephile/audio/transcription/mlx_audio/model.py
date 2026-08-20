#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""MLX-Audio speech-to-text model definitions."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.language import Language

__all__ = [
    "FIRERED_ASR2_MODEL",
    "GLM_ASR_MODEL",
    "MIMO_MODEL",
    "MlxAudioModel",
    "QWEN3_ASR_MODEL",
    "SENSEVOICE_MODEL",
]


@dataclass
class MlxAudioModel:
    """Complete definition of one MLX-Audio STT model."""

    model_name: str
    """Hugging Face model name or local model path."""
    family_name: str
    """Stable model-family name used in cache identities."""
    model_type: str
    """Model type passed to the MLX-Audio loader."""
    languages: dict[Language, str | None]
    """Model-specific language values keyed by Scinoephile language."""
    model_revision: str
    """Required immutable model revision."""
    audio_tokenizer_model_name: str | None = None
    """Auxiliary Hugging Face audio-tokenizer name, when required."""
    audio_tokenizer_model_revision: str | None = None
    """Immutable auxiliary audio-tokenizer revision, when required."""
    default_max_tokens: int | None = None
    """Default maximum generated tokens, or None for the model's native behavior."""
    max_tokens_argument: str | None = "max_tokens"
    """MLX-Audio generation-limit parameter, or None when unsupported."""
    max_safe_audio_duration_seconds: float | None = None
    """Maximum safe audio duration per inference, or None when unrestricted."""


FIRERED_ASR2_MODEL = MlxAudioModel(
    model_name="mlx-community/FireRedASR2-AED-mlx",
    family_name="firered-asr2",
    model_type="fireredasr2",
    languages=dict.fromkeys(Language),
    model_revision="f3212eacfa49b851130b97c63653c8e06ee09bdb",
    max_tokens_argument="max_len",
)
"""Default MLX FireRedASR2-AED model."""

GLM_ASR_MODEL = MlxAudioModel(
    model_name="mlx-community/GLM-ASR-Nano-2512-8bit",
    family_name="glm-asr",
    model_type="glm",
    languages=dict.fromkeys(Language),
    model_revision="fa36e850714806d8e50aac6573a8c0177d2e5e1a",
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
    model_revision="69813f0d57fb9bb5328735c4e907a4558b47d341",
    audio_tokenizer_model_name="mlx-community/MiMo-Audio-Tokenizer",
    audio_tokenizer_model_revision="6d451ed9a73024b4d33b87afa69e0dfd40d8f306",
    default_max_tokens=256,
    max_safe_audio_duration_seconds=55.0,
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
    model_revision="89e96d92ba34aca20b3e29fb10cc284097d1219f",
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
    model_revision="8ddd966bd96243cff196422f81f0c5d955814792",
    max_tokens_argument=None,
)
"""Default MLX SenseVoiceSmall model."""
