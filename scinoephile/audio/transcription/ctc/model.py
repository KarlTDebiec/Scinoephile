#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runs CTC model inference and maps transcript text to model tokens."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, ClassVar, Protocol

import numpy as np
from opencc import OpenCC
from pydub import AudioSegment

from scinoephile.audio.transcription.exceptions import TranscriptionAlignmentError
from scinoephile.audio.waveform import to_mono_int16
from scinoephile.core.dependencies.transcription import (
    import_torch,
    import_transformers,
)
from scinoephile.core.ml import ModelSpec, get_huggingface_snapshot_dir_path

__all__ = ["CtcModel"]


class _LoadedCtcModel(Protocol):
    """Model interface used by CTC inference."""

    config: object
    """Model configuration."""

    def __call__(self, **kwargs: Any) -> Any:
        """Run CTC inference."""
        ...

    def eval(self) -> object:
        """Put the model in evaluation mode."""
        ...

    def to(self, device: str) -> _LoadedCtcModel:
        """Move the model to a device.

        Arguments:
            device: target device identifier
        Returns:
            model on the target device
        """
        ...


class _CtcProcessor(Protocol):
    """Processor interface used by CTC inference."""

    feature_extractor: object
    """Audio feature extractor."""

    tokenizer: object
    """CTC tokenizer."""

    def __call__(
        self, samples: np.ndarray, *, sampling_rate: int, return_tensors: str
    ) -> Mapping[str, Any]:
        """Prepare audio samples for CTC inference.

        Arguments:
            samples: normalized mono audio samples
            sampling_rate: sample rate of the audio samples
            return_tensors: tensor framework identifier
        Returns:
            model inputs
        """
        ...


class CtcModel:
    """Runs inference with a pinned Hugging Face CTC model."""

    _models: ClassVar[dict[tuple[ModelSpec, str], _LoadedCtcModel]] = {}
    """Loaded models shared by model specification and device."""

    _processors: ClassVar[dict[ModelSpec, _CtcProcessor]] = {}
    """Loaded processors shared by model specification."""

    def __init__(
        self, spec: ModelSpec, device: str, script_conversion_config: str | None
    ):
        """Initialize.

        Arguments:
            spec: CTC model specification
            device: device identifier passed to the CTC model
            script_conversion_config: optional OpenCC configuration for model input
        """
        self.spec = spec
        """CTC model specification."""

        self.device = device
        """Device identifier passed to the CTC model."""

        self.script_conversion_config = script_conversion_config
        """OpenCC configuration for adapting transcript text to the model."""

        self._model: _LoadedCtcModel | None = None
        """Loaded CTC model, or None before first use."""

        self._processor: _CtcProcessor | None = None
        """Loaded CTC processor, or None before first use."""

        self._model_dir_path: Path | None = None
        """Resolved local model directory path, or None before loading."""

    def __call__(
        self, audio: AudioSegment, text: str
    ) -> tuple[np.ndarray, list[int], list[int], int]:
        """Get CTC probabilities and transcript token mapping.

        Arguments:
            audio: source audio to recognize
            text: transcript text to map to model tokens
        Returns:
            log probabilities, token IDs, text character indices, and blank token ID
        Raises:
            ImportError: if CTC dependencies are unavailable
            TranscriptionAlignmentError: if model inputs cannot be prepared
        """
        processor = self._loaded_processor
        feature_extractor = getattr(processor, "feature_extractor", None)
        sampling_rate = getattr(feature_extractor, "sampling_rate", None)
        if not isinstance(sampling_rate, int) or sampling_rate <= 0:
            raise TranscriptionAlignmentError(
                "CTC aligner processor did not expose a valid sampling rate."
            )
        samples = self._get_audio_samples(audio, sampling_rate)
        inputs = processor(samples, sampling_rate=sampling_rate, return_tensors="pt")
        if self.device != "cpu":
            inputs = {key: value.to(self.device) for key, value in inputs.items()}

        torch = import_torch()
        with torch.no_grad():
            output = self._loaded_model(**inputs)
            logits = output.logits[0]
            log_probs = logits.log_softmax(dim=-1).detach().cpu().numpy()

        blank_token_id = self._get_blank_token_id()
        token_ids, char_indices = self._get_token_ids(text)
        return log_probs, token_ids, char_indices, blank_token_id

    @property
    def _loaded_model(self) -> _LoadedCtcModel:
        """Get the CTC model, loading it if needed.

        Returns:
            loaded CTC model
        """
        if self._model is None:
            model_key = (self.spec, self.device)
            cached_model = self._models.get(model_key)
            if cached_model is not None:
                self._model = cached_model
                return self._model

            transformers = import_transformers()
            model = self._load_pretrained(transformers.AutoModelForCTC.from_pretrained)
            model = model.to(self.device)
            model.eval()
            self._model = model
            self._models[model_key] = model
        return self._model

    @property
    def _loaded_processor(self) -> _CtcProcessor:
        """Get the CTC processor, loading it if needed.

        Returns:
            loaded CTC processor
        """
        if self._processor is None:
            cached_processor = self._processors.get(self.spec)
            if cached_processor is not None:
                self._processor = cached_processor
                return self._processor

            transformers = import_transformers()
            processor = self._load_pretrained(
                transformers.AutoProcessor.from_pretrained
            )
            self._processor = processor
            self._processors[self.spec] = processor
        return self._processor

    @staticmethod
    def _get_audio_samples(audio: AudioSegment, sampling_rate: int) -> np.ndarray:
        """Get audio samples for CTC inference.

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

    def _get_blank_token_id(self) -> int:
        """Get the blank token ID used by the CTC model.

        Returns:
            blank token ID
        Raises:
            TranscriptionAlignmentError: if no blank token ID is available
        """
        config = getattr(self._loaded_model, "config", None)
        value = getattr(config, "pad_token_id", None)
        if isinstance(value, int):
            return value

        tokenizer = getattr(self._loaded_processor, "tokenizer", None)
        value = getattr(tokenizer, "pad_token_id", None)
        if isinstance(value, int):
            return value

        raise TranscriptionAlignmentError(
            "CTC aligner did not expose a blank token ID."
        )

    def _get_model_dir_path(self) -> Path:
        """Resolve the model to a local directory.

        Returns:
            local model directory path
        """
        if self._model_dir_path is None:
            self._model_dir_path = get_huggingface_snapshot_dir_path(
                self.spec.name, self.spec.revision
            )
        return self._model_dir_path

    def _get_token_ids(self, text: str) -> tuple[list[int], list[int]]:
        """Get CTC token IDs and source text indices for supported characters.

        Arguments:
            text: transcription text
        Returns:
            token IDs and original character indices
        """
        tokenizer = getattr(self._loaded_processor, "tokenizer", None)
        if tokenizer is None:
            raise TranscriptionAlignmentError(
                "CTC aligner processor lacks a tokenizer."
            )

        token_ids: list[int] = []
        char_indices: list[int] = []
        converted_text = None
        if self.script_conversion_config is not None:
            candidate_text = OpenCC(self.script_conversion_config).convert(text)
            if len(candidate_text) == len(text):
                converted_text = candidate_text
        alignment_text_end_idx = len(text.rstrip())
        for char_idx, char in enumerate(text):
            if char.isspace() and (
                char_idx == 0
                or text[char_idx - 1].isspace()
                or char_idx >= alignment_text_end_idx
            ):
                continue
            converted_char = None
            if converted_text is not None:
                converted_char = converted_text[char_idx]
            token_id = self._get_token_id(char, converted_char, tokenizer)
            if token_id is None:
                continue
            token_ids.append(token_id)
            char_indices.append(char_idx)
        return token_ids, char_indices

    @staticmethod
    def _get_token_id(
        char: str, converted_char: str | None, tokenizer: object
    ) -> int | None:
        """Get a model token ID for one transcript character.

        Arguments:
            char: transcript character
            converted_char: model-script character corresponding to the transcript
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

        candidates = list(dict.fromkeys((char, char.upper(), char.lower())))
        if converted_char is not None:
            candidates.extend(
                candidate
                for candidate in (
                    converted_char,
                    converted_char.upper(),
                    converted_char.lower(),
                )
                if candidate not in candidates
            )

        if not callable(convert_tokens_to_ids):
            return None
        for candidate in candidates:
            token_id = convert_tokens_to_ids(candidate)
            if isinstance(token_id, int) and token_id != unk_token_id:
                return token_id
        return None

    def _load_pretrained(self, loader: Callable[..., Any]) -> Any:
        """Load a Hugging Face asset from its resolved local snapshot.

        Arguments:
            loader: Hugging Face from_pretrained callable
        Returns:
            loaded model or processor
        """
        return loader(self._get_model_dir_path(), local_files_only=True)
