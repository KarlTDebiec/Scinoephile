#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Aligns transcription text to audio using a CTC model."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from pydub import AudioSegment

from scinoephile.audio.cache_namespace import AudioCacheNamespace
from scinoephile.audio.transcription.cache import TranscriptionCache
from scinoephile.audio.transcription.exceptions import TranscriptionAlignmentError
from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.core import Language
from scinoephile.core.cache.identity import CacheIdentity
from scinoephile.core.cache.runtime import get_distribution_identity
from scinoephile.core.dependencies.transcription import import_transformers
from scinoephile.core.ml import get_huggingface_snapshot_dir_path

from .model import get_alignment_inputs
from .path import get_best_path, get_character_timings
from .text import get_transcribed_words

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
    "ctl/wav2vec2-large-xlsr-cantonese": "11cb21cb68b4ed15f4c6633494ae6cc90a89bc34",
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
        Raises:
            DependencyError: if CTC dependencies are unavailable
            TranscriptionAlignmentError: if alignment cannot recover word timings
        """
        return self.align(audio, text)

    @property
    def model(self) -> CtcModel:
        """Get the cached CTC model, loading it if needed.

        Returns:
            loaded CTC model
        Raises:
            DependencyError: if CTC dependencies are unavailable
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
        Raises:
            DependencyError: if CTC dependencies are unavailable
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
            DependencyError: if CTC dependencies are unavailable
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
            log_probs, token_ids, char_indices, blank_token_id = get_alignment_inputs(
                audio,
                transcript_text,
                self.processor,
                self.model,
                self.device,
                self._script_conversion_config,
            )

            # Find frame timings for supported characters
            if token_ids:
                path = get_best_path(log_probs, token_ids, blank_token_id)
                timed_chars = get_character_timings(
                    path, char_indices, log_probs.shape[0], duration_seconds
                )
            else:
                timed_chars = {}

            # Fill gaps for unsupported characters and build the aligned segment
            words = get_transcribed_words(
                self.language, transcript_text, timed_chars, duration_seconds
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

    def _get_cache_identity(self, text: str) -> CacheIdentity:
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

    def _load_pretrained(self, loader: Callable[..., Any]) -> Any:
        """Load a Hugging Face asset locally before allowing network access.

        Arguments:
            loader: Hugging Face `from_pretrained` callable
        Returns:
            loaded model or processor
        """
        model_dir_path = self._get_model_dir_path()
        return loader(model_dir_path, local_files_only=True)
