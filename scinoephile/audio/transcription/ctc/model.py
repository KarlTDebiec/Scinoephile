#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runs CTC model inference."""

from __future__ import annotations

from functools import cached_property
from typing import Any

import numpy as np
from pydub import AudioSegment

from scinoephile.audio.transcription.exceptions import TranscriptionAlignmentError
from scinoephile.audio.waveform import to_mono_int16
from scinoephile.core.dependencies.transcription import (
    import_torch,
    import_transformers,
)
from scinoephile.core.ml import ModelSpec, get_huggingface_snapshot_dir_path

from .tokenization import get_token_ids

__all__ = ["CtcModel"]


class CtcModel:
    """Configured executable Hugging Face CTC model."""

    def __init__(self, spec: ModelSpec, device: str):
        """Initialize.

        Arguments:
            spec: CTC model specification
            device: device identifier passed to the CTC model
        """
        self.spec = spec
        """CTC model specification."""

        self.device = device
        """Device identifier passed to the CTC model."""

    def __call__(
        self, audio: AudioSegment, text: str, model_text: str | None = None
    ) -> tuple[np.ndarray, list[int], list[int], int]:
        """Get CTC probabilities and transcript token mapping.

        Arguments:
            audio: source audio to recognize
            text: transcript text to map to model tokens
            model_text: transcript converted to the model tokenizer's script
        Returns:
            log probabilities, token IDs, text character indices, and blank token ID
        Raises:
            ImportError: if CTC dependencies are unavailable
            TranscriptionAlignmentError: if model inputs cannot be prepared
        """
        feature_extractor = getattr(self.processor, "feature_extractor", None)
        sampling_rate = getattr(feature_extractor, "sampling_rate", None)
        if not isinstance(sampling_rate, int) or sampling_rate <= 0:
            raise TranscriptionAlignmentError(
                "CTC aligner processor did not expose a valid sampling rate."
            )

        samples = to_mono_int16(audio, sampling_rate).astype(np.float32)
        samples /= float(1 << 15)
        if samples.size == 0:
            raise TranscriptionAlignmentError("CTC alignment received empty audio.")
        inputs = self.processor(
            samples, sampling_rate=sampling_rate, return_tensors="pt"
        )
        if self.device != "cpu":
            inputs = {key: value.to(self.device) for key, value in inputs.items()}

        torch = import_torch()
        with torch.no_grad():
            output = self.model(**inputs)
            logits = output.logits[0]
            log_probs = logits.log_softmax(dim=-1).detach().cpu().numpy()

        config = getattr(self.model, "config", None)
        blank_token_id = getattr(config, "pad_token_id", None)
        tokenizer = getattr(self.processor, "tokenizer", None)
        if not isinstance(blank_token_id, int):
            blank_token_id = getattr(tokenizer, "pad_token_id", None)
        if not isinstance(blank_token_id, int):
            raise TranscriptionAlignmentError(
                "CTC aligner did not expose a blank token ID."
            )

        if tokenizer is None:
            raise TranscriptionAlignmentError(
                "CTC aligner processor lacks a tokenizer."
            )
        token_ids, char_indices = get_token_ids(text, tokenizer, model_text)
        return log_probs, token_ids, char_indices, blank_token_id

    @cached_property
    def model(self) -> Any:
        """Load and get the configured CTC model.

        Returns:
            loaded CTC model
        """
        transformers = import_transformers()
        model_dir_path = get_huggingface_snapshot_dir_path(
            self.spec.name, self.spec.revision
        )
        model = transformers.AutoModelForCTC.from_pretrained(
            model_dir_path, local_files_only=True
        ).to(self.device)
        model.eval()
        return model

    @cached_property
    def processor(self) -> Any:
        """Load and get the configured CTC processor.

        Returns:
            loaded CTC processor
        """
        transformers = import_transformers()
        model_dir_path = get_huggingface_snapshot_dir_path(
            self.spec.name, self.spec.revision
        )
        return transformers.AutoProcessor.from_pretrained(
            model_dir_path, local_files_only=True
        )
