#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Aligns transcription text to audio using a CTC model."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, cast

import numpy as np
from opencc import OpenCC
from pydub import AudioSegment

from scinoephile.audio.cache_namespace import AudioCacheNamespace
from scinoephile.audio.waveform import to_mono_int16
from scinoephile.core import Language
from scinoephile.core.cache.runtime import get_distribution_identity
from scinoephile.core.dependencies.transcription import (
    import_torch,
    import_transformers,
)
from scinoephile.core.ml import get_huggingface_snapshot_dir_path

from .cache import TranscriptionCache
from .exceptions import (
    TranscriptionAlignmentError,
    TranscriptionAlignmentIncompleteError,
)
from .transcribed_segment import TranscribedSegment
from .transcribed_word import TranscribedWord

__all__ = ["CtcAligner"]

if TYPE_CHECKING:
    from scinoephile.core.dependencies.transcription import CtcModel, CtcProcessor

_DEFAULT_MODEL_NAMES = {
    Language.eng: "facebook/wav2vec2-base-960h",
    Language.yue_hans: "ctl/wav2vec2-large-xlsr-cantonese",
    Language.yue_hant: "ctl/wav2vec2-large-xlsr-cantonese",
    Language.zho_hans: "jonatasgrosman/wav2vec2-large-xlsr-53-chinese-zh-cn",
    Language.zho_hant: "jonatasgrosman/wav2vec2-large-xlsr-53-chinese-zh-cn",
}
"""Default CTC model names keyed by transcription language."""

_DEFAULT_MODEL_REVISIONS = {
    "facebook/wav2vec2-base-960h": "22aad52d435eb6dbaf354bdad9b0da84ce7d6156",
    "ctl/wav2vec2-large-xlsr-cantonese": ("11cb21cb68b4ed15f4c6633494ae6cc90a89bc34"),
    "jonatasgrosman/wav2vec2-large-xlsr-53-chinese-zh-cn": (
        "99ccb2737be22b8bb50dcfcc39ad4d567fb90cfd"
    ),
}
"""Immutable Hugging Face revisions for the default CTC models."""

_SCRIPT_CONVERSION_CONFIGS = {
    (Language.yue_hans, _DEFAULT_MODEL_NAMES[Language.yue_hans]): "s2t",
    (Language.zho_hant, _DEFAULT_MODEL_NAMES[Language.zho_hant]): "t2s",
}
"""OpenCC configurations keyed by transcription language and CTC model name."""

_ALIGNMENT_VERSION = 1
"""Version of the CTC forced-alignment algorithm and output shaping."""


class CtcAligner:
    """Aligns transcription text to audio using a CTC model."""

    _models: ClassVar[dict[tuple[str, str | None, str], CtcModel]] = {}
    """Loaded models shared by model name, revision, and device."""

    _processors: ClassVar[dict[tuple[str, str | None], CtcProcessor]] = {}
    """Loaded processors shared by model name and revision."""

    def __init__(
        self,
        language: Language,
        model_name: str | None = None,
        device: str = "cpu",
        *,
        model_revision: str | None = None,
        cache_root_path: Path | None = None,
        overwrite_cache: bool = False,
    ):
        """Initialize.

        Arguments:
            language: transcription language
            model_name: optional Hugging Face CTC model name or local model path
            device: device identifier passed to the CTC model
            model_revision: optional immutable Hugging Face model revision
            cache_root_path: root directory beneath which to cache
            overwrite_cache: whether to replace matching cache files
        Raises:
            ValueError: if no default model is available for the language
        """
        self.language = language
        """Transcription language."""

        if model_name is None:
            try:
                model_name = _DEFAULT_MODEL_NAMES[language]
            except KeyError as exc:
                raise ValueError(
                    f"{language} is not supported by CTC alignment"
                ) from exc
            if model_revision is None:
                model_revision = _DEFAULT_MODEL_REVISIONS.get(model_name)
        self.model_name = model_name
        """Hugging Face CTC model name or local model path."""

        self.model_revision = model_revision
        """Immutable Hugging Face model revision, or None."""

        self._script_conversion_config = _SCRIPT_CONVERSION_CONFIGS.get(
            (language, model_name)
        )
        """OpenCC configuration for adapting text to the CTC model."""

        self.device = device
        """Device identifier passed to the CTC model."""

        self.cache = TranscriptionCache(
            cache_root_path,
            AudioCacheNamespace.TRANSCRIPTION_CTC,
            "ctc",
            "CTC-aligned",
            overwrite_cache,
        )
        """Persistent cache of forced-alignment results."""

        self._model: CtcModel | None = None
        """CTC model used for alignment."""

        self._processor: CtcProcessor | None = None
        """Processor associated with the CTC model."""

        self._model_dir_path: Path | None = None
        """Resolved local model directory path, or None before loading."""

    def __call__(self, audio: AudioSegment, text: str) -> list[TranscribedSegment]:
        """Align transcript text to source audio.

        Arguments:
            audio: source audio to align against
            text: transcription text
        Returns:
            timestamped transcription segments
        """
        return self.align(audio, text)

    @property
    def model(self) -> CtcModel:
        """Get the cached CTC model, loading it if needed.

        Returns:
            loaded CTC model
        """
        if self._model is None:
            model_key = (self.model_name, self.model_revision, self.device)
            cached_model = self._models.get(model_key)
            if cached_model is not None:
                self._model = cached_model
                return self._model

            transformers = import_transformers()
            model = self._load_pretrained(transformers.AutoModelForCTC.from_pretrained)
            if hasattr(model, "to"):
                model = model.to(self.device)
            if hasattr(model, "eval"):
                model.eval()
            self._model = model
            self._models[model_key] = model
        return self._model

    @property
    def processor(self) -> CtcProcessor:
        """Get the cached CTC processor, loading it if needed.

        Returns:
            loaded CTC processor
        """
        if self._processor is None:
            processor_key = (self.model_name, self.model_revision)
            cached_processor = self._processors.get(processor_key)
            if cached_processor is not None:
                self._processor = cached_processor
                return self._processor

            transformers = import_transformers()
            processor = self._load_pretrained(
                transformers.AutoProcessor.from_pretrained
            )
            self._processor = processor
            self._processors[processor_key] = processor
        return self._processor

    def align(self, audio: AudioSegment, text: str) -> list[TranscribedSegment]:
        """Align transcript text to source audio.

        Arguments:
            audio: source audio to align against
            text: transcription text
        Returns:
            timestamped transcription segments
        Raises:
            TranscriptionAlignmentError: if alignment cannot recover word timings
        """
        # Validate the transcription text
        transcript_text = text
        if not transcript_text.strip():
            raise TranscriptionAlignmentError("Cannot align empty transcript.")
        cache_identity = self._get_cache_identity(transcript_text)
        cached = self.cache.load(audio, cache_identity)
        if cached is not None:
            return cached[1]

        # Derive timing scale from the audio being aligned
        duration_seconds = len(audio) / 1000

        try:
            # Get model probabilities and tokens for supported transcript characters
            log_probs, token_ids, char_indices, blank_token_id = (
                self._get_alignment_inputs(audio, transcript_text)
            )

            # Find frame timings for supported characters
            if token_ids:
                path = self._get_best_path(log_probs, token_ids, blank_token_id)
                timed_chars = self._get_character_timings(
                    path, char_indices, log_probs.shape[0], duration_seconds
                )
            else:
                timed_chars = {}

            # Fill gaps for unsupported characters and build the aligned segment
            words = self._get_transcribed_words(
                transcript_text, timed_chars, duration_seconds
            )
            if not words:
                raise TranscriptionAlignmentError(
                    "CTC alignment did not produce timings."
                )
            segments = [
                TranscribedSegment(
                    id=0,
                    seek=0,
                    start=words[0].start,
                    end=words[-1].end,
                    text=transcript_text,
                    words=words,
                )
            ]
            self.cache.save(audio, cache_identity, segments)
            return segments
        except TranscriptionAlignmentError:
            raise
        except (ImportError, OSError, RuntimeError, ValueError) as exc:
            raise TranscriptionAlignmentError(
                f"Unable to run CTC transcription alignment: {exc}"
            ) from exc

    def _get_alignment_inputs(
        self, audio: AudioSegment, text: str
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
        processor = self.processor
        feature_extractor = getattr(processor, "feature_extractor", None)
        sampling_rate = getattr(feature_extractor, "sampling_rate", None)
        if not isinstance(sampling_rate, int) or sampling_rate <= 0:
            raise TranscriptionAlignmentError(
                "CTC aligner processor did not expose a valid sampling rate."
            )
        samples = self._get_audio_samples(audio, sampling_rate)
        processor_callable = cast(Callable[..., Mapping[str, Any]], processor)
        inputs = processor_callable(
            samples, sampling_rate=sampling_rate, return_tensors="pt"
        )
        if self.device != "cpu":
            inputs = {key: value.to(self.device) for key, value in inputs.items()}

        # Run CTC inference and normalize output for the alignment algorithm
        torch = import_torch()
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

    def _get_model_dir_path(self) -> Path:
        """Resolve the model to a local directory.

        Returns:
            local model directory path
        """
        if self._model_dir_path is not None:
            return self._model_dir_path

        configured_path = Path(self.model_name)
        if configured_path.is_dir():
            self._model_dir_path = configured_path
        else:
            self._model_dir_path = get_huggingface_snapshot_dir_path(
                self.model_name, self.model_revision
            )
        return self._model_dir_path

    def _get_cache_identity(self, text: str) -> dict[str, object]:
        """Get the configuration identifying reusable forced alignment.

        Arguments:
            text: transcription text aligned to the audio
        Returns:
            complete CTC alignment identity
        """
        return {
            "alignment_version": _ALIGNMENT_VERSION,
            "device": self.device,
            "language": self.language.code,
            "model_name": self.model_name,
            "model_revision": self.model_revision,
            "runtime": {
                "torch": get_distribution_identity("torch"),
                "transformers": get_distribution_identity("transformers"),
            },
            "script_conversion": self._script_conversion_config,
            "text": text,
        }

    def _load_pretrained(self, loader: Callable[..., Any]) -> Any:
        """Load a Hugging Face asset locally before allowing network access.

        Arguments:
            loader: Hugging Face ``from_pretrained`` callable
        Returns:
            loaded model or processor
        """
        model_dir_path = self._get_model_dir_path()
        return loader(model_dir_path, local_files_only=True)

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
        converted_text = None
        if self._script_conversion_config is not None:
            candidate_text = OpenCC(self._script_conversion_config).convert(text)
            if len(candidate_text) == len(text):
                converted_text = candidate_text
        alignment_text_end_idx = len(text.rstrip())
        for char_idx, char in enumerate(text):
            # Align one delimiter per internal whitespace run
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
    def _attach_boundary_text(
        run_text: str, words: list[TranscribedWord], has_next_timing: bool
    ) -> str | None:
        """Attach unaligned boundary punctuation or whitespace to a timed character.

        Arguments:
            run_text: unaligned text at a transcript boundary
            words: transcribed words built so far
            has_next_timing: whether an aligned character follows the run
        Returns:
            pending prefix text when handled, otherwise None
        """
        if (
            words
            and not has_next_timing
            and not any(char.isalnum() for char in run_text)
        ):
            words[-1].text += run_text
            return ""
        if not words and run_text.isspace():
            return run_text
        return None

    @staticmethod
    def _get_audio_samples(audio: AudioSegment, sampling_rate: int) -> np.ndarray:
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

    @staticmethod
    def _get_best_path(
        log_probs: np.ndarray, token_ids: Sequence[int], blank_token_id: int
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
            log_probs, token_ids, blank_token_id
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
            raise TranscriptionAlignmentIncompleteError(
                "CTC alignment did not reach all tokens."
            )
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
        char: str, converted_char: str | None, tokenizer: object
    ) -> int | None:
        """Get an aligner token ID for one transcript character.

        Arguments:
            char: transcript character
            converted_char: model-script character corresponding to the transcript
            tokenizer: Hugging Face tokenizer
        Returns:
            token ID, or None when the character cannot be aligned directly
        """
        # Resolve tokenizer metadata and token conversion
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

        # Build case variants in preference order
        candidates = list(dict.fromkeys((char, char.upper(), char.lower())))

        # Add the model-specific script variant without changing the output text
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

        # Return the first variant recognized by the tokenizer
        if not callable(convert_tokens_to_ids):
            return None
        for candidate in candidates:
            token_id = convert_tokens_to_ids(candidate)
            if isinstance(token_id, int) and token_id != unk_token_id:
                return token_id
        return None

    def _get_transcribed_words(
        self,
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
            run_text = text[run_start_idx:run_end_idx]

            # Attach boundary text to the nearest aligned character
            boundary_pending_text = CtcAligner._attach_boundary_text(
                run_text, words, char_idx < len(text)
            )
            if boundary_pending_text is not None:
                pending_text = boundary_pending_text
                continue

            previous_end = words[-1].end if words else 0.0
            next_start = duration_seconds
            if char_idx < len(text):
                next_timing = timed_chars.get(char_idx)
                if next_timing is not None:
                    next_start = next_timing[0]

            # Attach zero-duration internal text to an adjacent aligned character
            gap_seconds = max(next_start - previous_end, 0.0)
            if gap_seconds == 0.0:
                if not words:
                    pending_text = run_text
                    continue
                prefix_start_idx = next(
                    (
                        idx
                        for idx in range(len(run_text) - 1, -1, -1)
                        if run_text[idx].isspace()
                    ),
                    len(run_text),
                )
                words[-1].text += run_text[:prefix_start_idx]
                pending_text = run_text[prefix_start_idx:]
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

        if self.language is Language.eng:
            return self._group_english_words(words)
        return words

    @staticmethod
    def _group_english_words(
        character_words: Sequence[TranscribedWord],
    ) -> list[TranscribedWord]:
        """Group English character timings into whitespace-delimited words.

        Arguments:
            character_words: individually timed characters
        Returns:
            whitespace-delimited words with aggregate timings and confidence
        """
        # Group whitespace with the word that follows it
        word_parts: list[list[TranscribedWord]] = []
        for character_word in character_words:
            if (
                character_word.text[0].isspace()
                and word_parts
                and not all(part.text.isspace() for part in word_parts[-1])
            ):
                word_parts.append([])
            elif not word_parts:
                word_parts.append([])
            word_parts[-1].append(character_word)

        # Preserve trailing whitespace on the preceding word
        if (
            len(word_parts) > 1
            and word_parts[-1]
            and all(part.text.isspace() for part in word_parts[-1])
        ):
            word_parts[-2].extend(word_parts.pop())

        # Combine each group using duration-weighted character confidence
        words: list[TranscribedWord] = []
        for parts in word_parts:
            durations = [max(part.end - part.start, 0.0) for part in parts]
            total_duration = sum(durations)
            if total_duration > 0.0:
                confidence = (
                    sum(
                        part.confidence * duration
                        for part, duration in zip(parts, durations, strict=True)
                    )
                    / total_duration
                )
            else:
                confidence = sum(part.confidence for part in parts) / len(parts)
            words.append(
                TranscribedWord(
                    text="".join(part.text for part in parts),
                    start=parts[0].start,
                    end=parts[-1].end,
                    confidence=round(confidence, 3),
                )
            )
        return words

    @staticmethod
    def _validate_best_path_inputs(
        log_probs: np.ndarray, token_ids: Sequence[int], blank_token_id: int
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
