#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
# ruff: noqa: PLC0415
"""Lazy access to optional transcription dependencies."""

from __future__ import annotations

from collections.abc import Callable
from types import ModuleType
from typing import TYPE_CHECKING

__all__ = [
    "import_demucs_infer_apply",
    "import_demucs_infer_pretrained",
    "import_huggingface_hub",
    "import_huggingface_hub_utils",
    "import_mlx_audio_stt_load",
    "import_torch",
    "import_torchaudio",
    "import_transformers",
    "import_whisper_timestamped",
    "import_whisper_timestamped_transcribe",
]

if TYPE_CHECKING:
    from demucs_infer.apply import BagOfModels, Model
    from torch import Tensor
    from transformers import PreTrainedModel, ProcessorMixin
    from whisper import Whisper

    type CtcModel = PreTrainedModel
    type CtcProcessor = ProcessorMixin
    type DemucsModel = BagOfModels | Model
    type TorchTensor = Tensor
    type WhisperModel = Whisper

_TRANSCRIPTION_EXTRA_MESSAGE = (
    "Transcription support requires optional transcription dependencies. "
    "Install scinoephile with the 'transcription' extra."
)


def import_demucs_infer_apply() -> ModuleType:
    """Import the Demucs model application module on demand.

    Returns:
        Demucs model application module
    """
    try:
        import demucs_infer.apply as demucs_infer_apply
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return demucs_infer_apply


def import_demucs_infer_pretrained() -> ModuleType:
    """Import the Demucs pretrained-model module on demand.

    Returns:
        Demucs pretrained-model module
    """
    try:
        import demucs_infer.pretrained as demucs_infer_pretrained
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return demucs_infer_pretrained


def import_huggingface_hub() -> ModuleType:
    """Import Hugging Face Hub on demand.

    Returns:
        Hugging Face Hub module
    """
    try:
        import huggingface_hub
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return huggingface_hub


def import_huggingface_hub_utils() -> ModuleType:
    """Import Hugging Face Hub utilities on demand.

    Returns:
        Hugging Face Hub utilities module
    """
    try:
        import huggingface_hub.utils as huggingface_hub_utils
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return huggingface_hub_utils


def import_mlx_audio_stt_load() -> Callable[..., object]:
    """Import the MLX-Audio STT model loader on demand.

    Returns:
        MLX-Audio model loader
    """
    try:
        from mlx_audio.stt import load
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return load


def import_torch() -> ModuleType:
    """Import Torch on demand.

    Returns:
        Torch module
    """
    try:
        import torch
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return torch


def import_torchaudio() -> ModuleType:
    """Import Torchaudio on demand.

    Returns:
        Torchaudio module
    """
    try:
        import torchaudio
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return torchaudio


def import_transformers() -> ModuleType:
    """Import Transformers on demand.

    Returns:
        Transformers module
    """
    try:
        import transformers
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return transformers


def import_whisper_timestamped() -> ModuleType:
    """Import Whisper Timestamped on demand.

    Returns:
        Whisper Timestamped module
    """
    try:
        import whisper_timestamped
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return whisper_timestamped


def import_whisper_timestamped_transcribe() -> ModuleType:
    """Import the Whisper Timestamped transcription module on demand.

    Returns:
        Whisper Timestamped transcription module
    """
    try:
        import whisper_timestamped.transcribe as whisper_timestamped_transcribe
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return whisper_timestamped_transcribe
