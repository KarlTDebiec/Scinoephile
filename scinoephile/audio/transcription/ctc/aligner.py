#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Aligns transcription text to audio using a CTC model."""

from __future__ import annotations

from pathlib import Path

from opencc import OpenCC
from pydub import AudioSegment

from scinoephile.audio.cache_namespace import AudioCacheNamespace
from scinoephile.audio.transcription.cache import TranscriptionCache
from scinoephile.audio.transcription.exceptions import TranscriptionAlignmentError
from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.core import Language
from scinoephile.core.cache.identity import CacheIdentity
from scinoephile.core.cache.runtime import get_distribution_identity
from scinoephile.core.ml import ModelSpec
from scinoephile.core.script import OpenCCConfig

from .model import CtcModel
from .model_spec import CANTONESE_MODEL, CHINESE_MODEL, ENGLISH_MODEL, CtcModelSpec
from .path import get_best_path, get_character_timings
from .text import get_transcribed_words

__all__ = ["CtcAligner"]

_DEFAULT_MODEL_SPECS = {
    Language.eng: ENGLISH_MODEL,
    Language.yue_hans: CANTONESE_MODEL,
    Language.yue_hant: CANTONESE_MODEL,
    Language.zho_hans: CHINESE_MODEL,
    Language.zho_hant: CHINESE_MODEL,
}
"""Default CTC model specifications keyed by transcription language."""

_ALIGNMENT_VERSION = 1
"""Version of the CTC forced-alignment algorithm and output shaping."""


class CtcAligner:
    """Aligns transcription text to audio using a CTC model."""

    def __init__(
        self,
        language: Language,
        spec: ModelSpec | None = None,
        device: str | None = None,
        *,
        cache_root_path: Path | None = None,
        overwrite_cache: bool = False,
    ):
        """Initialize.

        Arguments:
            language: transcription language
            spec: optional CTC model specification
            device: Torch device, or None to select the available accelerator
            cache_root_path: root directory beneath which to cache
            overwrite_cache: whether to replace matching cache files
        Raises:
            ValueError: if no default model is available for the language
        """
        self.language = language
        """Transcription language."""

        if spec is None:
            try:
                spec = _DEFAULT_MODEL_SPECS[language]
            except KeyError as exc:
                raise ValueError(
                    f"{language} is not supported by CTC alignment"
                ) from exc

        self._script_conversion_config: OpenCCConfig | None = None
        """Conversion from transcript script to model tokenizer script."""
        if isinstance(spec, CtcModelSpec):
            if language.script == "Hans" and spec.script == "Hant":
                self._script_conversion_config = OpenCCConfig.s2t
            elif language.script == "Hant" and spec.script == "Hans":
                self._script_conversion_config = OpenCCConfig.t2s

        self.model = CtcModel(spec, device)
        """CTC model used to obtain token probabilities."""

        self.cache = TranscriptionCache(
            cache_root_path,
            AudioCacheNamespace.TRANSCRIPTION_CTC,
            "ctc",
            "CTC-aligned",
            overwrite_cache,
        )
        """Persistent cache of forced-alignment results."""

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
        if not text.strip():
            raise TranscriptionAlignmentError("Cannot align empty transcript.")
        cache_identity = self._get_cache_identity(text)
        cached = self.cache.load(audio, cache_identity)
        if cached is not None:
            return cached[1]

        duration_seconds = len(audio) / 1000
        try:
            model_text = None
            if self._script_conversion_config is not None:
                candidate_text = OpenCC(self._script_conversion_config.code).convert(
                    text
                )
                if len(candidate_text) == len(text):
                    model_text = candidate_text
            result = self.model(audio, text, model_text)
            if result.token_ids:
                path = get_best_path(
                    result.log_probs, result.token_ids, result.blank_token_id
                )
                timed_chars = get_character_timings(
                    path,
                    result.char_indices,
                    result.log_probs.shape[0],
                    duration_seconds,
                )
            else:
                timed_chars = {}

            words = get_transcribed_words(
                self.language, text, timed_chars, duration_seconds
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
                    text=text,
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

    @property
    def cache_config_identity(self) -> CacheIdentity:
        """Get the cache identity of this CTC aligner's configuration."""
        script_conversion = None
        runtime = {
            "torch": get_distribution_identity("torch"),
            "transformers": get_distribution_identity("transformers"),
        }
        if self._script_conversion_config is not None:
            script_conversion = self._script_conversion_config.code
            runtime["opencc"] = get_distribution_identity("opencc")
        return {
            "alignment_version": _ALIGNMENT_VERSION,
            "device": self.model.device,
            "language": self.language.code,
            "model_name": self.model.spec.name,
            "model_revision": self.model.spec.revision,
            "runtime": runtime,
            "script_conversion": script_conversion,
        }

    def _get_cache_identity(self, text: str) -> CacheIdentity:
        """Get the configuration identifying reusable forced alignment.

        Arguments:
            text: transcription text aligned to the audio
        Returns:
            complete CTC alignment identity
        """
        return {**self.cache_config_identity, "text": text}
