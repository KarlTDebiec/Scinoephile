#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runs CTC model inference and maps transcript text to model tokens."""

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
        processor = self.processor
        feature_extractor = getattr(processor, "feature_extractor", None)
        sampling_rate = getattr(feature_extractor, "sampling_rate", None)
        if not isinstance(sampling_rate, int) or sampling_rate <= 0:
            raise TranscriptionAlignmentError(
                "CTC aligner processor did not expose a valid sampling rate."
            )

        samples = to_mono_int16(audio, sampling_rate).astype(np.float32)
        samples /= float(1 << 15)
        if samples.size == 0:
            raise TranscriptionAlignmentError("CTC alignment received empty audio.")
        inputs = processor(samples, sampling_rate=sampling_rate, return_tensors="pt")
        if self.device != "cpu":
            inputs = {key: value.to(self.device) for key, value in inputs.items()}

        torch = import_torch()
        loaded_model = self.loaded_model
        with torch.no_grad():
            output = loaded_model(**inputs)
            logits = output.logits[0]
            log_probs = logits.log_softmax(dim=-1).detach().cpu().numpy()

        config = getattr(loaded_model, "config", None)
        blank_token_id = getattr(config, "pad_token_id", None)
        if not isinstance(blank_token_id, int):
            tokenizer = getattr(processor, "tokenizer", None)
            blank_token_id = getattr(tokenizer, "pad_token_id", None)
        if not isinstance(blank_token_id, int):
            raise TranscriptionAlignmentError(
                "CTC aligner did not expose a blank token ID."
            )

        token_ids, char_indices = self._get_token_ids(text, model_text)
        return log_probs, token_ids, char_indices, blank_token_id

    @cached_property
    def loaded_model(self) -> Any:
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

    def _get_token_ids(
        self, text: str, model_text: str | None = None
    ) -> tuple[list[int], list[int]]:
        """Get CTC token IDs and source text indices for supported characters.

        Arguments:
            text: transcription text
            model_text: transcript converted to the model tokenizer's script
        Returns:
            token IDs and original character indices
        """
        tokenizer = getattr(self.processor, "tokenizer", None)
        if tokenizer is None:
            raise TranscriptionAlignmentError(
                "CTC aligner processor lacks a tokenizer."
            )

        token_ids: list[int] = []
        char_indices: list[int] = []
        alignment_text_end_idx = len(text.rstrip())
        for char_idx, char in enumerate(text):
            if char.isspace() and (
                char_idx == 0
                or text[char_idx - 1].isspace()
                or char_idx >= alignment_text_end_idx
            ):
                continue
            model_char = None
            if model_text is not None:
                model_char = model_text[char_idx]
            token_id = self._get_token_id(char, model_char, tokenizer)
            if token_id is None:
                continue
            token_ids.append(token_id)
            char_indices.append(char_idx)
        return token_ids, char_indices

    @staticmethod
    def _get_token_id(
        char: str, model_char: str | None, tokenizer: object
    ) -> int | None:
        """Get a model token ID for one transcript character.

        Arguments:
            char: transcript character
            model_char: model-script character corresponding to the transcript
            tokenizer: Hugging Face tokenizer
        Returns:
            token ID, or None when the character cannot be aligned directly
        """
        unk_token_id = getattr(tokenizer, "unk_token_id", None)
        convert_tokens_to_ids = getattr(tokenizer, "convert_tokens_to_ids", None)
        if char.isspace():
            word_delimiter_token_id = getattr(
                tokenizer, "word_delimiter_token_id", None
            )
            if (
                isinstance(word_delimiter_token_id, int)
                and word_delimiter_token_id != unk_token_id
            ):
                return word_delimiter_token_id

            word_delimiter_token = getattr(tokenizer, "word_delimiter_token", None)
            if isinstance(word_delimiter_token, str) and callable(
                convert_tokens_to_ids
            ):
                token_id = convert_tokens_to_ids(word_delimiter_token)
                if isinstance(token_id, int) and token_id != unk_token_id:
                    return token_id
            return None

        candidates = [char, char.upper(), char.lower()]
        if model_char is not None:
            candidates.extend([model_char, model_char.upper(), model_char.lower()])

        if not callable(convert_tokens_to_ids):
            return None
        for candidate in dict.fromkeys(candidates):
            token_id = convert_tokens_to_ids(candidate)
            if isinstance(token_id, int) and token_id != unk_token_id:
                return token_id
        return None
