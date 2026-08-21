#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Aligns transcription text to audio using a CTC model."""

from __future__ import annotations

from pathlib import Path

from pydub import AudioSegment

from scinoephile.audio.cache_namespace import AudioCacheNamespace
from scinoephile.audio.transcription.cache import TranscriptionCache
from scinoephile.audio.transcription.exceptions import TranscriptionAlignmentError
from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.core import Language
from scinoephile.core.cache.runtime import get_distribution_identity
from scinoephile.core.ml import ModelSpec

from .model import CtcModel
from .path import get_best_path, get_character_timings
from .text import get_transcribed_words

__all__ = ["CtcAligner"]

_ENGLISH_MODEL = ModelSpec(
    name="facebook/wav2vec2-base-960h",
    revision="22aad52d435eb6dbaf354bdad9b0da84ce7d6156",
)
"""Default English CTC model specification."""

_CANTONESE_MODEL = ModelSpec(
    name="ctl/wav2vec2-large-xlsr-cantonese",
    revision="11cb21cb68b4ed15f4c6633494ae6cc90a89bc34",
)
"""Default Cantonese CTC model specification."""

_CHINESE_MODEL = ModelSpec(
    name="jonatasgrosman/wav2vec2-large-xlsr-53-chinese-zh-cn",
    revision="99ccb2737be22b8bb50dcfcc39ad4d567fb90cfd",
)
"""Default Chinese CTC model specification."""

_DEFAULT_MODEL_SPECS = {
    Language.eng: _ENGLISH_MODEL,
    Language.yue_hans: _CANTONESE_MODEL,
    Language.yue_hant: _CANTONESE_MODEL,
    Language.zho_hans: _CHINESE_MODEL,
    Language.zho_hant: _CHINESE_MODEL,
}
"""Default CTC model specifications keyed by transcription language."""

_SCRIPT_CONVERSION_CONFIGS = {
    (Language.yue_hans, _CANTONESE_MODEL): "s2t",
    (Language.zho_hant, _CHINESE_MODEL): "t2s",
}
"""OpenCC configurations keyed by transcription language and CTC model."""

_ALIGNMENT_VERSION = 1
"""Version of the CTC forced-alignment algorithm and output shaping."""


class CtcAligner:
    """Aligns transcription text to audio using a CTC model."""

    def __init__(
        self,
        language: Language,
        model_spec: ModelSpec | None = None,
        device: str = "cpu",
        *,
        cache_root_path: Path | None = None,
        overwrite_cache: bool = False,
    ):
        """Initialize.

        Arguments:
            language: transcription language
            model_spec: optional CTC model specification
            device: device identifier passed to the CTC model
            cache_root_path: root directory beneath which to cache
            overwrite_cache: whether to replace matching cache files
        Raises:
            ValueError: if no default model is available for the language
        """
        self.language = language
        """Transcription language."""

        if model_spec is None:
            try:
                model_spec = _DEFAULT_MODEL_SPECS[language]
            except KeyError as exc:
                raise ValueError(
                    f"{language} is not supported by CTC alignment"
                ) from exc
        self.model_spec = model_spec
        """CTC model specification."""

        self.device = device
        """Device identifier passed to the CTC model."""

        self._script_conversion_config = _SCRIPT_CONVERSION_CONFIGS.get(
            (language, model_spec)
        )
        """OpenCC configuration for adapting text to the CTC model."""

        self.model = CtcModel(model_spec, device, self._script_conversion_config)
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
        """
        return self.align(audio, text)

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
        transcript_text = text
        if not transcript_text.strip():
            raise TranscriptionAlignmentError("Cannot align empty transcript.")
        cache_identity = self._get_cache_identity(transcript_text)
        cached = self.cache.load(audio, cache_identity)
        if cached is not None:
            return cached[1]

        duration_seconds = len(audio) / 1000
        try:
            log_probs, token_ids, char_indices, blank_token_id = self.model(
                audio, transcript_text
            )
            if token_ids:
                path = get_best_path(log_probs, token_ids, blank_token_id)
                timed_chars = get_character_timings(
                    path, char_indices, log_probs.shape[0], duration_seconds
                )
            else:
                timed_chars = {}

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
            "model_name": self.model_spec.name,
            "model_revision": self.model_spec.revision,
            "runtime": {
                "torch": get_distribution_identity("torch"),
                "transformers": get_distribution_identity("transformers"),
            },
            "script_conversion": self._script_conversion_config,
            "text": text,
        }
