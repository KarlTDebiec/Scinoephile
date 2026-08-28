#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Prepares audio and runs CTC model inference."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any, cast

import numpy as np
from pydub import AudioSegment

from scinoephile.audio.transcription.exceptions import TranscriptionAlignmentError
from scinoephile.audio.waveform import to_mono_int16
from scinoephile.core.dependencies.transcription import import_torch

from .tokenization import get_token_ids

__all__ = ["get_alignment_inputs", "get_audio_samples", "get_blank_token_id"]


def get_alignment_inputs(
    audio: AudioSegment,
    text: str,
    processor: object,
    model: object,
    device: str,
    script_conversion_config: str | None,
) -> tuple[np.ndarray, list[int], list[int], int]:
    """Get CTC log probabilities and transcript token mapping.

    Arguments:
        audio: source audio to align against
        text: transcription text
        processor: processor associated with the CTC model
        model: loaded CTC model
        device: device identifier passed to the CTC model
        script_conversion_config: optional OpenCC configuration for model input
    Returns:
        log probabilities, token IDs, text character indices, and blank token ID
    Raises:
        DependencyError: if CTC dependencies are unavailable
        TranscriptionAlignmentError: if transcript tokens cannot be prepared
    """
    # Prepare the audio and model inputs
    feature_extractor = getattr(processor, "feature_extractor", None)
    sampling_rate = getattr(feature_extractor, "sampling_rate", None)
    if not isinstance(sampling_rate, int) or sampling_rate <= 0:
        raise TranscriptionAlignmentError(
            "CTC aligner processor did not expose a valid sampling rate."
        )
    samples = get_audio_samples(audio, sampling_rate)
    processor_callable = cast(Callable[..., Mapping[str, Any]], processor)
    inputs = processor_callable(
        samples, sampling_rate=sampling_rate, return_tensors="pt"
    )
    if device != "cpu":
        inputs = {key: value.to(device) for key, value in inputs.items()}

    # Run CTC inference and normalize output for the alignment algorithm
    torch = import_torch()
    model_callable = cast(Callable[..., Any], model)
    with torch.no_grad():
        output = model_callable(**inputs)
        logits = output.logits[0]
        log_probs = logits.log_softmax(dim=-1).detach().cpu().numpy()

    blank_token_id = get_blank_token_id(model, processor)
    tokenizer = getattr(processor, "tokenizer", None)
    if tokenizer is None:
        raise TranscriptionAlignmentError("CTC aligner processor lacks a tokenizer.")
    token_ids, char_indices = get_token_ids(text, tokenizer, script_conversion_config)
    return log_probs, token_ids, char_indices, blank_token_id


def get_audio_samples(audio: AudioSegment, sampling_rate: int) -> np.ndarray:
    """Get audio samples for CTC alignment.

    Arguments:
        audio: audio to convert
        sampling_rate: sample rate expected by the CTC processor
    Returns:
        mono float32 samples at the requested rate
    Raises:
        TranscriptionAlignmentError: if audio contains no samples
    """
    samples = to_mono_int16(audio, sampling_rate).astype(np.float32)
    samples /= float(1 << 15)
    if samples.size == 0:
        raise TranscriptionAlignmentError("CTC alignment received empty audio.")
    return samples


def get_blank_token_id(model: object, processor: object) -> int:
    """Get the blank token ID used by a CTC model.

    Arguments:
        model: loaded CTC model
        processor: processor associated with the CTC model
    Returns:
        blank token ID
    Raises:
        TranscriptionAlignmentError: if no blank token ID is available
    """
    config = getattr(model, "config", None)
    value = getattr(config, "pad_token_id", None)
    if isinstance(value, int):
        return value

    tokenizer = getattr(processor, "tokenizer", None)
    value = getattr(tokenizer, "pad_token_id", None)
    if isinstance(value, int):
        return value

    raise TranscriptionAlignmentError("CTC aligner did not expose a blank token ID.")
