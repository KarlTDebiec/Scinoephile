#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Aligns transcription text to audio using a CTC model."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import TYPE_CHECKING, Any, ClassVar, cast

import numpy as np
from opencc import OpenCC
from pydub import AudioSegment

from .exceptions import TranscriptionAlignmentError
from .transcribed_segment import TranscribedSegment
from .transcribed_word import TranscribedWord

__all__ = ["CtcAligner"]

if TYPE_CHECKING:
    from transformers import PreTrainedModel, ProcessorMixin


class CtcAligner:
    """Aligns transcription text to audio using a CTC model."""

    _components: ClassVar[
        dict[tuple[str, str], tuple[ProcessorMixin, PreTrainedModel]]
    ] = {}
    """Loaded processors and models shared by model name and device."""

    def __init__(
        self,
        model_name: str = "jonatasgrosman/wav2vec2-large-xlsr-53-chinese-zh-cn",
        device: str = "cpu",
    ):
        """Initialize.

        Arguments:
            model_name: Hugging Face CTC model name or local model path
            device: device identifier passed to the CTC model
        """
        self.model_name = model_name
        """Hugging Face CTC model name or local model path."""

        self.device = device
        """Device identifier passed to the CTC model."""

        self._model: PreTrainedModel | None = None
        """CTC model used for alignment."""

        self._processor: ProcessorMixin | None = None
        """Processor associated with the CTC model."""

    def __call__(
        self,
        audio: AudioSegment,
        text: str,
    ) -> list[TranscribedSegment]:
        """Align transcript text to source audio.

        Arguments:
            audio: source audio to align against
            text: transcription text
        Returns:
            timestamped transcription segments
        """
        return self.align(audio, text)

    @property
    def model(self) -> PreTrainedModel:
        """Get the cached CTC model, loading it if needed.

        Returns:
            loaded CTC model
        """
        self._load_components()
        assert self._model is not None
        return self._model

    @property
    def processor(self) -> ProcessorMixin:
        """Get the cached CTC processor, loading it if needed.

        Returns:
            loaded CTC processor
        """
        self._load_components()
        assert self._processor is not None
        return self._processor

    def align(
        self,
        audio: AudioSegment,
        text: str,
    ) -> list[TranscribedSegment]:
        """Align transcript text to source audio.

        Arguments:
            audio: source audio to align against
            text: transcription text
        Returns:
            timestamped transcription segments
        Raises:
            TranscriptionAlignmentError: if alignment cannot recover word timings
        """
        # Validate and normalize the transcription text
        transcript_text = text.strip()
        if not transcript_text:
            raise TranscriptionAlignmentError("Cannot align empty transcript.")

        # Derive timing scale from the audio being aligned
        duration_seconds = len(audio) / 1000

        try:
            # Get model probabilities and tokens for supported transcript characters
            log_probs, token_ids, char_indices, blank_token_id = (
                self._get_alignment_inputs(audio, transcript_text)
            )

            # Find frame timings for supported characters
            if token_ids:
                path = self._get_best_path(
                    log_probs,
                    token_ids,
                    blank_token_id,
                )
                timed_chars = self._get_character_timings(
                    path,
                    char_indices,
                    log_probs.shape[0],
                    duration_seconds,
                )
            else:
                timed_chars = {}

            # Fill gaps for unsupported characters and build the aligned segment
            words = self._get_transcribed_words(
                transcript_text,
                timed_chars,
                duration_seconds,
            )
            if not words:
                raise TranscriptionAlignmentError(
                    "CTC alignment did not produce timings."
                )
            return [
                TranscribedSegment(
                    id=0,
                    seek=0,
                    start=words[0].start,
                    end=words[-1].end,
                    text=transcript_text,
                    words=words,
                )
            ]
        except TranscriptionAlignmentError:
            raise
        except (ImportError, OSError, RuntimeError, ValueError) as exc:
            raise TranscriptionAlignmentError(
                f"Unable to run CTC transcription alignment: {exc}"
            ) from exc

    def _get_alignment_inputs(
        self,
        audio: AudioSegment,
        text: str,
    ) -> tuple[np.ndarray, list[int], list[int], int]:
        """Get CTC log probabilities and transcript token mapping.

        Arguments:
            audio: source audio to align against
            text: transcription text
        Returns:
            log probabilities, token IDs, text character indices, and blank token ID
        Raises:
            ImportError: if CTC dependencies are unavailable
            TranscriptionAlignmentError: if transcript tokens cannot be prepared
        """
        # Prepare the audio and model inputs
        samples = self._get_audio_samples(audio)
        processor_callable = cast(Callable[..., Mapping[str, Any]], self.processor)
        inputs = processor_callable(samples, sampling_rate=16000, return_tensors="pt")
        if self.device != "cpu":
            inputs = {key: value.to(self.device) for key, value in inputs.items()}

        # Run CTC inference and normalize output for the alignment algorithm
        torch = self._import_torch()
        model_callable = cast(Callable[..., Any], self.model)
        with torch.no_grad():
            output = model_callable(**inputs)
            logits = output.logits[0]
            log_probs = logits.log_softmax(dim=-1).detach().cpu().numpy()

        blank_token_id = self._get_blank_token_id()
        token_ids, char_indices = self._get_token_ids(text)
        return log_probs, token_ids, char_indices, blank_token_id

    def _get_blank_token_id(self) -> int:
        """Get the blank token ID used by the CTC model.

        Returns:
            blank token ID
        Raises:
            TranscriptionAlignmentError: if no blank token ID is available
        """
        config = getattr(self.model, "config", None)
        value = getattr(config, "pad_token_id", None)
        if isinstance(value, int):
            return value

        tokenizer = getattr(self.processor, "tokenizer", None)
        value = getattr(tokenizer, "pad_token_id", None)
        if isinstance(value, int):
            return value

        raise TranscriptionAlignmentError(
            "CTC aligner did not expose a blank token ID."
        )

    def _get_token_ids(self, text: str) -> tuple[list[int], list[int]]:
        """Get CTC token IDs and source text indices for supported characters.

        Arguments:
            text: transcription text
        Returns:
            token IDs and original character indices
        Raises:
            TranscriptionAlignmentError: if the processor lacks a tokenizer
        """
        tokenizer = getattr(self.processor, "tokenizer", None)
        if tokenizer is None:
            raise TranscriptionAlignmentError(
                "CTC aligner processor lacks a tokenizer."
            )

        # Map supported characters to model tokens while retaining source positions
        token_ids: list[int] = []
        char_indices: list[int] = []
        script_converter = OpenCC("t2s")
        for char_idx, char in enumerate(text):
            token_id = self._get_token_id(char, script_converter, tokenizer)
            if token_id is None:
                continue
            token_ids.append(token_id)
            char_indices.append(char_idx)
        return token_ids, char_indices

    def _load_components(self):
        """Load or reuse the configured CTC processor and model.

        Raises:
            ImportError: if Hugging Face CTC dependencies are unavailable
        """
        if self._processor is not None and self._model is not None:
            return

        # Reuse components loaded by another aligner instance
        component_key = (self.model_name, self.device)
        cached_components = self._components.get(component_key)
        if cached_components is not None:
            self._processor, self._model = cached_components
            return

        # Load the processor and model lazily to preserve optional dependencies
        try:
            from transformers import (  # noqa: PLC0415
                AutoModelForCTC,
                AutoProcessor,
            )
        except ImportError as exc:
            raise ImportError(
                "CTC timestamp alignment requires transformers and torch dependencies."
            ) from exc
        processor = AutoProcessor.from_pretrained(self.model_name)
        model = AutoModelForCTC.from_pretrained(self.model_name)

        # Prepare the model for inference and retain both components
        if hasattr(model, "to"):
            model = model.to(self.device)
        if hasattr(model, "eval"):
            model.eval()
        self._processor = processor
        self._model = model
        self._components[component_key] = (processor, model)

    @staticmethod
    def _get_audio_samples(audio: AudioSegment) -> np.ndarray:
        """Get audio samples for CTC alignment.

        Arguments:
            audio: audio to convert
        Returns:
            mono 16 kHz float32 samples
        Raises:
            TranscriptionAlignmentError: if audio contains no samples
        """
        # Normalize audio to the format expected by the CTC processor
        normalized_audio = (
            audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
        )
        samples = (
            np.array(normalized_audio.get_array_of_samples(), dtype=np.float32)
            / 32768.0
        )
        if samples.size == 0:
            raise TranscriptionAlignmentError("CTC alignment received empty audio.")
        return samples

    @staticmethod
    def _get_best_path(
        log_probs: np.ndarray,
        token_ids: Sequence[int],
        blank_token_id: int,
    ) -> list[tuple[int, int, float]]:
        """Get the best CTC path through a transcript-token trellis.

        Arguments:
            log_probs: frame-by-token log probabilities
            token_ids: target token IDs
            blank_token_id: model blank token ID
        Returns:
            path entries as transcript token index, frame index, and probability
        Raises:
            TranscriptionAlignmentError: if no complete path can be found
        """
        frame_count = CtcAligner._validate_best_path_inputs(
            log_probs,
            token_ids,
            blank_token_id,
        )

        # Insert required blanks between adjacent repeated labels
        alignment_token_ids: list[int] = []
        path_token_indices: list[int] = []
        for token_idx, token_id in enumerate(token_ids):
            if token_id < 0 or token_id >= log_probs.shape[1]:
                raise TranscriptionAlignmentError(
                    "CTC target token ID is out of range."
                )
            if token_idx > 0 and token_id == token_ids[token_idx - 1]:
                alignment_token_ids.append(blank_token_id)
                path_token_indices.append(token_idx - 1)
            alignment_token_ids.append(token_id)
            path_token_indices.append(token_idx)

        # Initialize and populate the alignment trellis
        alignment_token_count = len(alignment_token_ids)
        trellis = np.empty((frame_count + 1, alignment_token_count + 1))
        trellis[0, 0] = 0.0
        trellis[1:, 0] = np.cumsum(log_probs[:, blank_token_id])
        trellis[0, -alignment_token_count:] = -np.inf
        trellis[-alignment_token_count:, 0] = np.inf
        for frame_idx in range(frame_count):
            stay_scores = trellis[frame_idx, 1:] + log_probs[frame_idx, blank_token_id]
            token_log_probs = log_probs[frame_idx, alignment_token_ids]
            change_scores = trellis[frame_idx, :-1] + token_log_probs
            trellis[frame_idx + 1, 1:] = np.maximum(stay_scores, change_scores)

        # Select the best completed alignment
        final_column = trellis[:, alignment_token_count]
        if np.all(np.isneginf(final_column)):
            raise TranscriptionAlignmentError("CTC alignment did not reach all tokens.")
        frame_idx = int(np.argmax(final_column))

        # Backtrack through the trellis to recover token frame spans
        alignment_token_idx = alignment_token_count
        path: list[tuple[int, int, float]] = []
        for trellis_frame_idx in range(frame_idx, 0, -1):
            token_id = alignment_token_ids[alignment_token_idx - 1]
            stay_score = (
                trellis[trellis_frame_idx - 1, alignment_token_idx]
                + log_probs[trellis_frame_idx - 1, blank_token_id]
            )
            change_score = (
                trellis[trellis_frame_idx - 1, alignment_token_idx - 1]
                + log_probs[trellis_frame_idx - 1, token_id]
            )
            if change_score > stay_score:
                score_token_id = token_id
            else:
                score_token_id = blank_token_id
            path.append(
                (
                    path_token_indices[alignment_token_idx - 1],
                    trellis_frame_idx - 1,
                    float(np.exp(log_probs[trellis_frame_idx - 1, score_token_id])),
                )
            )
            if change_score > stay_score:
                alignment_token_idx -= 1
                if alignment_token_idx == 0:
                    break
        else:
            raise TranscriptionAlignmentError("CTC alignment backtrack failed.")

        path.reverse()
        return path

    @staticmethod
    def _get_character_timings(
        path: Sequence[tuple[int, int, float]],
        char_indices: Sequence[int],
        frame_count: int,
        duration_seconds: float,
    ) -> dict[int, tuple[float, float, float]]:
        """Convert a CTC path into original-text character timings.

        Arguments:
            path: CTC alignment path
            char_indices: original text indices for path token indices
            frame_count: number of audio frames represented by the CTC output
            duration_seconds: source audio duration in seconds
        Returns:
            character index mapped to start, end, and confidence
        Raises:
            TranscriptionAlignmentError: if path entries are inconsistent
        """
        if frame_count == 0:
            raise TranscriptionAlignmentError("CTC alignment received no audio frames.")
        frame_duration = duration_seconds / frame_count

        # Collapse consecutive frames assigned to each transcript character
        timed_chars: dict[int, tuple[float, float, float]] = {}
        path_idx = 0
        while path_idx < len(path):
            segment_end_idx = path_idx
            while (
                segment_end_idx < len(path)
                and path[path_idx][0] == path[segment_end_idx][0]
            ):
                segment_end_idx += 1

            token_idx = path[path_idx][0]
            if token_idx < 0 or token_idx >= len(char_indices):
                raise TranscriptionAlignmentError(
                    "CTC path token index is out of range."
                )
            char_idx = char_indices[token_idx]
            start = path[path_idx][1] * frame_duration
            end = (path[segment_end_idx - 1][1] + 1) * frame_duration
            confidence = sum(item[2] for item in path[path_idx:segment_end_idx]) / (
                segment_end_idx - path_idx
            )
            timed_chars[char_idx] = (
                round(start, 3),
                round(end, 3),
                round(confidence, 3),
            )
            path_idx = segment_end_idx
        return timed_chars

    @staticmethod
    def _get_token_id(
        char: str,
        script_converter: OpenCC,
        tokenizer: object,
    ) -> int | None:
        """Get an aligner token ID for one transcript character.

        Arguments:
            char: transcript character
            script_converter: converter from Traditional Chinese to the model's script
            tokenizer: Hugging Face tokenizer
        Returns:
            token ID, or None when the character cannot be aligned directly
        """
        if char.isspace():
            return None

        # Build case and script variants in preference order
        unk_token_id = getattr(tokenizer, "unk_token_id", None)
        candidates = list(dict.fromkeys((char, char.upper(), char.lower())))
        simplified = script_converter.convert(char)
        if len(simplified) == 1:
            candidates.extend(
                candidate
                for candidate in (
                    simplified,
                    simplified.upper(),
                    simplified.lower(),
                )
                if candidate not in candidates
            )

        # Return the first variant recognized by the tokenizer
        convert_tokens_to_ids = getattr(tokenizer, "convert_tokens_to_ids", None)
        if not callable(convert_tokens_to_ids):
            return None
        for candidate in candidates:
            token_id = convert_tokens_to_ids(candidate)
            if isinstance(token_id, int) and token_id != unk_token_id:
                return token_id
        return None

    @staticmethod
    def _get_transcribed_words(
        text: str,
        timed_chars: Mapping[int, tuple[float, float, float]],
        duration_seconds: float,
    ) -> list[TranscribedWord]:
        """Build transcribed words covering aligned and unaligned characters.

        Arguments:
            text: transcription text
            timed_chars: character index mapped to start, end, and confidence
            duration_seconds: source audio duration in seconds
        Returns:
            transcribed words covering every source character
        """
        words: list[TranscribedWord] = []
        pending_text = ""
        char_idx = 0
        while char_idx < len(text):
            # Add a directly aligned character and any pending prefix
            timing = timed_chars.get(char_idx)
            if timing is not None:
                start, end, confidence = timing
                words.append(
                    TranscribedWord(
                        text=f"{pending_text}{text[char_idx]}",
                        start=start,
                        end=end,
                        confidence=confidence,
                    )
                )
                pending_text = ""
                char_idx += 1
                continue

            # Find the next run of characters unsupported by the CTC model
            run_start_idx = char_idx
            while char_idx < len(text) and char_idx not in timed_chars:
                char_idx += 1
            run_end_idx = char_idx
            previous_end = words[-1].end if words else 0.0
            next_start = duration_seconds
            if char_idx < len(text):
                next_timing = timed_chars.get(char_idx)
                if next_timing is not None:
                    next_start = next_timing[0]

            # Attach zero-duration internal text to an adjacent aligned character
            gap_seconds = max(next_start - previous_end, 0.0)
            if gap_seconds == 0.0:
                run_text = text[run_start_idx:run_end_idx]
                if words and char_idx < len(text):
                    whitespace_idxs = [
                        idx for idx, char in enumerate(run_text) if char.isspace()
                    ]
                    if whitespace_idxs:
                        prefix_start_idx = whitespace_idxs[-1]
                        words[-1].text += run_text[:prefix_start_idx]
                        pending_text = run_text[prefix_start_idx:]
                    else:
                        words[-1].text += run_text
                elif words:
                    words[-1].text += run_text
                else:
                    pending_text = run_text
                continue

            # Distribute available time evenly across otherwise unaligned characters
            run_length = run_end_idx - run_start_idx
            char_duration = gap_seconds / run_length
            for offset, unaligned_char_idx in enumerate(
                range(run_start_idx, run_end_idx)
            ):
                start = previous_end + (offset * char_duration)
                end = previous_end + ((offset + 1) * char_duration)
                words.append(
                    TranscribedWord(
                        text=text[unaligned_char_idx],
                        start=start,
                        end=end,
                        confidence=0.0,
                    )
                )

        return words

    @staticmethod
    def _import_torch() -> Any:
        """Get the torch module.

        Returns:
            imported torch module
        Raises:
            ImportError: if torch is unavailable
        """
        try:
            import torch  # noqa: PLC0415
        except ImportError as exc:
            raise ImportError(
                "CTC timestamp alignment requires transformers and torch dependencies."
            ) from exc
        return torch

    @staticmethod
    def _validate_best_path_inputs(
        log_probs: np.ndarray,
        token_ids: Sequence[int],
        blank_token_id: int,
    ) -> int:
        """Validate CTC path inputs.

        Arguments:
            log_probs: frame-by-token log probabilities
            token_ids: target token IDs
            blank_token_id: model blank token ID
        Returns:
            frame count
        Raises:
            TranscriptionAlignmentError: if CTC inputs are malformed
        """
        if log_probs.ndim != 2:
            raise TranscriptionAlignmentError("CTC log probabilities must be 2D.")
        frame_count = log_probs.shape[0]
        if frame_count == 0:
            raise TranscriptionAlignmentError("CTC alignment received no audio frames.")
        if not token_ids:
            raise TranscriptionAlignmentError(
                "CTC alignment received no target tokens."
            )
        if blank_token_id < 0 or blank_token_id >= log_probs.shape[1]:
            raise TranscriptionAlignmentError("CTC blank token ID is out of range.")
        return frame_count
