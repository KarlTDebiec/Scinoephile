#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runs CTC model inference."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, cast

import numpy as np
from pydub import AudioSegment

from scinoephile.audio.transcription.exceptions import TranscriptionAlignmentError
from scinoephile.audio.waveform import to_mono_int16
from scinoephile.core.dependencies.transcription import (
    import_torch,
    import_transformers,
)
from scinoephile.core.ml import (
    ModelSpec,
    get_huggingface_snapshot_dir_path,
    get_torch_device,
)

from .tokenization import get_token_ids
from .types import CtcResult

__all__ = ["CtcModel"]

if TYPE_CHECKING:
    from transformers import PreTrainedModel, ProcessorMixin


class CtcModel:
    """Configured executable Hugging Face CTC model."""

    def __init__(self, spec: ModelSpec, device: str | None = None):
        """Initialize.

        Arguments:
            spec: CTC model specification
            device: Torch device, or None to select the available accelerator
        """
        self.spec = spec
        """CTC model specification."""

        self._device = device
        """Explicit Torch device, or None to select one when first needed."""

    def __call__(
        self, audio: AudioSegment, text: str, model_text: str | None = None
    ) -> CtcResult:
        """Get CTC probabilities and transcript token mapping.

        Arguments:
            audio: source audio to recognize
            text: transcript text to map to model tokens
            model_text: transcript converted to the model tokenizer's script
        Returns:
            CTC model output prepared for alignment
        Raises:
            DependencyError: if CTC dependencies are unavailable
            TranscriptionAlignmentError: if audio, model, or processor configuration
                is invalid
        """
        # Prepare audio samples
        sampling_rate = self.processor.feature_extractor.sampling_rate
        samples = to_mono_int16(audio, sampling_rate).astype(np.float32)
        samples /= 32768.0
        if samples.size == 0:
            raise TranscriptionAlignmentError("CTC alignment received empty audio.")

        # Prepare model inputs
        inputs = self.processor(
            samples, sampling_rate=sampling_rate, return_tensors="pt"
        )
        if self.device != "cpu":
            inputs = {key: value.to(self.device) for key, value in inputs.items()}

        # Run model inference
        torch = import_torch()
        with torch.no_grad():
            output = self.model(**inputs)
            logits = output.logits[0]
            log_probs = logits.log_softmax(dim=-1).detach().cpu().numpy()

        # Get token IDs and character indices
        blank_token_id = cast(int, self.model.config.pad_token_id)
        token_ids, char_indices = get_token_ids(
            text, self.processor.tokenizer, model_text
        )
        return CtcResult(
            log_probs=log_probs,
            token_ids=token_ids,
            char_indices=char_indices,
            blank_token_id=blank_token_id,
        )

    @cached_property
    def device(self) -> str:
        """Get the Torch device used for inference."""
        if self._device is not None:
            return self._device
        return get_torch_device()

    @cached_property
    def model(self) -> PreTrainedModel:
        """Load and get the configured CTC model.

        Returns:
            loaded CTC model
        Raises:
            DependencyError: if CTC dependencies are unavailable
            TranscriptionAlignmentError: if the model lacks a valid blank token ID
        """
        transformers = import_transformers()
        model_dir_path = get_huggingface_snapshot_dir_path(
            self.spec.name, self.spec.revision
        )
        model = transformers.AutoModelForCTC.from_pretrained(
            model_dir_path, local_files_only=True
        ).to(self.device)
        model.eval()
        if not isinstance(model.config.pad_token_id, int):
            raise TranscriptionAlignmentError(
                "CTC aligner model did not expose a blank token ID."
            )
        return model

    @cached_property
    def processor(self) -> ProcessorMixin:
        """Load and get the configured CTC processor.

        Returns:
            loaded CTC processor
        Raises:
            DependencyError: if CTC dependencies are unavailable
            TranscriptionAlignmentError: if the processor lacks a valid sampling rate
        """
        transformers = import_transformers()
        model_dir_path = get_huggingface_snapshot_dir_path(
            self.spec.name, self.spec.revision
        )
        processor = transformers.AutoProcessor.from_pretrained(
            model_dir_path, local_files_only=True
        )
        sampling_rate = processor.feature_extractor.sampling_rate
        if not isinstance(sampling_rate, int) or sampling_rate <= 0:
            raise TranscriptionAlignmentError(
                "CTC aligner processor did not expose a valid sampling rate."
            )
        return processor
