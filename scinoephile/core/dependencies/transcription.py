#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
# ruff: noqa: PLC0415
"""Lazy access to optional transcription dependencies."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import TYPE_CHECKING, TypedDict

__all__ = [
    "import_demucs_infer_apply_model",
    "import_demucs_infer_get_model",
    "import_huggingface_hub_snapshot_download",
    "import_huggingface_hub_utils_validate_repo_id",
    "import_torch_cuda_is_available",
    "import_torch_from_numpy",
    "import_torch_mps_is_available",
    "import_torch_no_grad",
    "import_torchaudio_functional_resample",
    "import_transformers_auto_model_for_ctc",
    "import_transformers_auto_processor",
    "import_whisper_timestamped_load_model",
    "import_whisper_timestamped_transcribe",
    "import_whisper_timestamped_transcribe_get_vad_segments",
]

if TYPE_CHECKING:
    from demucs_infer.apply import BagOfModels, Model
    from torch import Tensor
    from transformers import (
        AutoModelForCTC,
        AutoProcessor,
        PreTrainedModel,
        ProcessorMixin,
    )
    from whisper import Whisper

    type CtcModel = PreTrainedModel
    type CtcProcessor = ProcessorMixin
    type DemucsModel = BagOfModels | Model
    type TorchTensor = Tensor
    type WhisperModel = Whisper


class _WhisperTranscriptionResult(TypedDict):
    """Whisper transcription result used by Scinoephile."""

    segments: list[dict[str, object]]
    """Transcription segment dictionaries."""


class _WhisperVadSegment(TypedDict):
    """Whisper VAD speech interval."""

    start: int | float
    """Speech start time in seconds or samples, depending on output mode."""

    end: int | float
    """Speech end time in seconds or samples, depending on output mode."""


_TRANSCRIPTION_EXTRA_MESSAGE = (
    "Transcription support requires optional transcription dependencies. "
    "Install scinoephile with the 'transcription' extra."
)


def import_demucs_infer_apply_model() -> Callable[..., Tensor]:
    """Import the Demucs model application function on demand.

    Returns:
        Demucs model application function
    """
    try:
        from demucs_infer.apply import apply_model
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return apply_model


def import_demucs_infer_get_model() -> Callable[[str], DemucsModel]:
    """Import the Demucs model loader on demand.

    Returns:
        Demucs model loader
    """
    try:
        from demucs_infer.pretrained import get_model
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return get_model


def import_huggingface_hub_snapshot_download() -> Callable[..., str]:
    """Import the Hugging Face snapshot downloader on demand.

    Returns:
        snapshot download function
    """
    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return snapshot_download


def import_huggingface_hub_utils_validate_repo_id() -> Callable[[str], None]:
    """Import the Hugging Face repository ID validator on demand.

    Returns:
        repository ID validator
    """
    try:
        from huggingface_hub.utils import validate_repo_id
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return validate_repo_id


def import_torch_mps_is_available() -> Callable[[], bool]:
    """Import the Torch MPS availability check on demand.

    Returns:
        Torch MPS availability check
    """
    try:
        from torch.mps import is_available
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return is_available


def import_torch_cuda_is_available() -> Callable[[], bool]:
    """Import the Torch CUDA availability check on demand.

    Returns:
        Torch CUDA availability check
    """
    try:
        from torch.cuda import is_available
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return is_available


def import_torch_from_numpy() -> Callable[..., Tensor]:
    """Import the Torch NumPy conversion function on demand.

    Returns:
        Torch NumPy conversion function
    """
    try:
        from torch import from_numpy
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return from_numpy


def import_torch_no_grad() -> Callable[[], AbstractContextManager[None]]:
    """Import the Torch gradient-disabling context manager on demand.

    Returns:
        Torch gradient-disabling context manager
    """
    try:
        from torch import no_grad
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return no_grad


def import_torchaudio_functional_resample() -> Callable[[Tensor, int, int], Tensor]:
    """Import the Torchaudio resampling function on demand.

    Returns:
        Torchaudio resampling function
    """
    try:
        from torchaudio.functional import resample
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return resample


def import_transformers_auto_model_for_ctc() -> type[AutoModelForCTC]:
    """Import the Hugging Face CTC model factory on demand.

    Returns:
        CTC model factory
    """
    try:
        from transformers import AutoModelForCTC
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return AutoModelForCTC


def import_transformers_auto_processor() -> type[AutoProcessor]:
    """Import the Hugging Face processor factory on demand.

    Returns:
        processor factory
    """
    try:
        from transformers import AutoProcessor
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return AutoProcessor


def import_whisper_timestamped_load_model() -> Callable[..., WhisperModel]:
    """Import the Whisper model loader on demand.

    Returns:
        Whisper model loader
    """
    try:
        from whisper_timestamped import load_model
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return load_model


def import_whisper_timestamped_transcribe() -> Callable[
    ..., _WhisperTranscriptionResult
]:
    """Import the Whisper transcription function on demand.

    Returns:
        Whisper transcription function
    """
    try:
        from whisper_timestamped import transcribe
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return transcribe


def import_whisper_timestamped_transcribe_get_vad_segments() -> Callable[
    ..., list[_WhisperVadSegment]
]:
    """Import the Whisper Silero VAD segmenter on demand.

    Returns:
        voice activity detection function
    """
    try:
        from whisper_timestamped.transcribe import get_vad_segments
    except ImportError as exc:
        raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
    return get_vad_segments
