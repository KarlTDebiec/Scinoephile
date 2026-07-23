#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Transcribes audio using MiMo ASR plus forced timestamp alignment."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from collections.abc import Mapping, Sequence
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from scinoephile.common.file import get_temp_file_path
from scinoephile.common.validation import val_output_dir_path

from .base_transcriber import BaseTranscriber
from .forced_alignment import TranscriptionAlignmentError, align_mimo_transcription
from .mimo_runtime import (
    MIMO_MLX_MODEL_NAME,
    MIMO_MODEL_NAME,
    MIMO_TOKENIZER_NAME,
    MimoRuntime,
)
from .mimo_worker import transcribe_with_mimo
from .transcribed_segment import TranscribedSegment
from .transcribed_word import TranscribedWord

__all__ = [
    "MIMO_MLX_MODEL_NAME",
    "MIMO_MODEL_NAME",
    "MIMO_TOKENIZER_NAME",
    "MimoTranscriptEmptyError",
    "MimoTranscriber",
    "MimoTranscriptionError",
    "MimoRuntime",
    "MimoRuntimeUnsupportedError",
    "MimoWorkerError",
]

if TYPE_CHECKING:
    from pydub import AudioSegment

logger = getLogger(__name__)

_LOW_INFORMATION_CHARACTERS = frozenset("啊呀吖哦噢嗯嘶")
"""Standalone vocalizations rejected as unusable fallback transcripts."""

_VAD_CACHE_VERSION = "silero-v1"
"""Cache identity for the current MiMo VAD implementation."""

_VAD_MIN_SILENCE_DURATION_SECONDS = 1.0
"""Minimum silence separating MiMo speech intervals."""

_VAD_PADDING_SECONDS = 0.5
"""Context retained around each MiMo speech interval."""

_VAD_SAMPLE_RATE = 16000
"""Sample rate expected by the Silero VAD model."""


class MimoTranscriptionError(RuntimeError):
    """Raised when MiMo transcription cannot produce timestamped output."""


class MimoTranscriptEmptyError(MimoTranscriptionError):
    """Raised when MiMo returns no transcript text."""


class MimoRuntimeUnsupportedError(MimoTranscriptionError):
    """Raised when the requested MiMo runtime is not supported."""


class MimoWorkerError(MimoTranscriptionError):
    """Raised when MiMo inference fails or returns malformed output."""


class MimoTranscriber:
    """Transcribes audio using MiMo ASR and a timestamp alignment stage."""

    def __init__(
        self,
        model_name: str = MIMO_MODEL_NAME,
        tokenizer_name: str = MIMO_TOKENIZER_NAME,
        mimo_runtime: MimoRuntime | str = MimoRuntime.AUTO,
        language: str = "yue",
        max_tokens: int | None = None,
        chunk_duration_seconds: float | None = None,
        chunk_overlap_seconds: float = 1.0,
        cache_dir_path: Path | None = None,
        aligner_backend: str = "whisperx",
        aligner_language: str = "zh",
        aligner_model_name: str | None = None,
        aligner_worker_command: Sequence[str] | None = None,
        aligner_worker_timeout_seconds: float | None = None,
        worker_command: Sequence[str] | None = None,
        worker_timeout_seconds: float | None = None,
        use_demucs: bool = False,
        use_vad: bool = False,
        fallback_without_vad: bool = False,
        audio_tag: str = "",
        fallback_backend: BaseTranscriber | None = None,
    ):
        """Initialize.

        Arguments:
            model_name: MiMo ASR model name or local model path
            tokenizer_name: MiMo audio tokenizer name or local tokenizer path
            mimo_runtime: runtime implementation used for MiMo inference
            language: requested transcription language metadata
            max_tokens: optional maximum number of MiMo text tokens to generate
            chunk_duration_seconds: optional chunk duration for MiMo inference
            chunk_overlap_seconds: context overlap applied to each MiMo chunk
            cache_dir_path: directory in which to cache
            aligner_backend: timestamp alignment backend
            aligner_language: language code used by the alignment backend
            aligner_model_name: optional alignment model name
            aligner_worker_command: optional command that runs timestamp alignment
            aligner_worker_timeout_seconds: optional aligner timeout in seconds
            worker_command: optional subprocess command that runs MiMo
            worker_timeout_seconds: optional worker timeout in seconds
            use_demucs: whether Demucs preprocessing was applied
            use_vad: whether to remove non-speech audio using Silero VAD
            fallback_without_vad: whether to retry unfiltered audio after VAD failure
            audio_tag: optional MiMo audio tag such as <chinese> or <english>
            fallback_backend: optional backend to call when MiMo or alignment fails
        """
        self.model_name = model_name
        self.tokenizer_name = tokenizer_name
        self.mimo_runtime = MimoRuntime(mimo_runtime)
        self.language = language
        self.max_tokens = max_tokens
        self.chunk_duration_seconds = chunk_duration_seconds
        self.chunk_overlap_seconds = chunk_overlap_seconds
        if self.max_tokens is not None and self.max_tokens <= 0:
            raise ValueError("MiMo max tokens must be positive.")
        if self.chunk_duration_seconds is not None and self.chunk_duration_seconds <= 0:
            raise ValueError("MiMo chunk duration must be positive.")
        if self.chunk_overlap_seconds < 0:
            raise ValueError("MiMo chunk overlap must be non-negative.")
        self.aligner_backend = aligner_backend
        self.aligner_language = aligner_language
        self.aligner_model_name = aligner_model_name
        self.aligner_worker_command = (
            tuple(aligner_worker_command)
            if aligner_worker_command is not None
            else None
        )
        self.aligner_worker_timeout_seconds = aligner_worker_timeout_seconds
        self.worker_command = (
            tuple(worker_command) if worker_command is not None else None
        )
        self.worker_timeout_seconds = worker_timeout_seconds
        self.use_demucs = use_demucs
        self.use_vad = use_vad
        self.fallback_without_vad = fallback_without_vad
        if self.fallback_without_vad and not self.use_vad:
            raise ValueError("MiMo cannot fall back from VAD when VAD is disabled.")
        self.audio_tag = audio_tag
        self.fallback_backend = fallback_backend
        self.cache_dir_path = None
        if cache_dir_path is not None:
            self.cache_dir_path = val_output_dir_path(cache_dir_path)

    def __call__(
        self, audio: AudioSegment, *, cache_audio: AudioSegment | None = None
    ) -> list[TranscribedSegment]:
        """Transcribe audio.

        Arguments:
            audio: audio to transcribe
            cache_audio: optional audio used for cache-key generation
        Returns:
            transcription, split into timestamped segments
        """
        return self.transcribe(audio, cache_audio=cache_audio)

    def get_cached_transcription(
        self, cache_audio: AudioSegment
    ) -> list[TranscribedSegment] | None:
        """Get cached transcription for audio if available.

        Arguments:
            cache_audio: audio used for cache-key generation
        Returns:
            cached transcription, if present
        """
        cache_path = self._get_cache_path(cache_audio)
        if cache_path is None or not cache_path.exists():
            return None

        logger.info(f"Loaded MiMo transcription from cache: {cache_path}")
        with cache_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        if isinstance(payload, Mapping):
            raw_segments = payload.get("segments")
        else:
            raw_segments = payload
        if not isinstance(raw_segments, list):
            raise MimoWorkerError(f"Malformed MiMo cache payload: {cache_path}")
        segments = [TranscribedSegment.model_validate(s) for s in raw_segments]
        cache_path.touch()
        return segments

    def transcribe(
        self, audio: AudioSegment, *, cache_audio: AudioSegment | None = None
    ) -> list[TranscribedSegment]:
        """Transcribe audio.

        Arguments:
            audio: audio to transcribe
            cache_audio: optional audio used for cache-key generation
        Returns:
            transcription, split into timestamped segments
        """
        cache_audio = cache_audio or audio
        if (segments := self.get_cached_transcription(cache_audio)) is not None:
            return segments

        try:
            segments = self._transcribe_uncached(audio)
        except (MimoTranscriptionError, TranscriptionAlignmentError) as exc:
            if self.fallback_backend is None:
                raise
            logger.warning(f"Falling back after MiMo transcription failure: {exc}")
            return self.fallback_backend(audio, cache_audio=cache_audio)

        cache_path = self._get_cache_path(cache_audio)
        if cache_path is not None:
            with cache_path.open("w", encoding="utf-8") as file:
                json.dump(
                    self._get_cache_payload(segments),
                    file,
                    ensure_ascii=False,
                    indent=2,
                )
            logger.info(f"Saved MiMo transcription to cache: {cache_path}")

        return segments

    def _get_cache_path(self, audio: AudioSegment) -> Path | None:
        """Get cache path based on hash of audio data and MiMo configuration.

        Arguments:
            audio: audio used to derive the cache key
        Returns:
            path to cache file
        """
        if self.cache_dir_path is None:
            return None

        audio_sha256 = hashlib.sha256(audio.raw_data).hexdigest()
        effective_runtime = self._get_effective_mimo_runtime()
        effective_model_name = self._get_effective_model_name()
        vad_key = _VAD_CACHE_VERSION if self.use_vad else "off"
        cache_key = (
            f"{audio_sha256}_backend-mimo_"
            f"runtime-{effective_runtime}_"
            f"model-{effective_model_name}_tokenizer-{self.tokenizer_name}_"
            f"language-{self.language}_audio-tag-{self.audio_tag}_"
            f"max-tokens-{self.max_tokens or 'default'}_"
            f"chunk-duration-{self.chunk_duration_seconds or 'off'}_"
            f"chunk-overlap-{self.chunk_overlap_seconds}_"
            f"aligner-{self.aligner_backend}_"
            f"aligner-language-{self.aligner_language}_"
            f"aligner-model-{self.aligner_model_name or 'default'}_"
            f"aligner-worker-{self.aligner_worker_command or 'in-process'}_"
            f"demucs-{'on' if self.use_demucs else 'off'}_"
            f"vad-{vad_key}_"
            f"fallback-without-vad-"
            f"{'on' if self.fallback_without_vad else 'off'}_"
            f"fallback-{'on' if self.fallback_backend is not None else 'off'}"
        )
        cache_sha256 = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()
        return self.cache_dir_path / f"{cache_sha256}.json"

    def _get_cache_payload(
        self, segments: Sequence[TranscribedSegment]
    ) -> dict[str, object]:
        """Get JSON-serializable MiMo cache payload.

        Arguments:
            segments: timestamped segments to cache
        Returns:
            cache payload
        """
        return {
            "backend": "mimo",
            "model_name": self._get_effective_model_name(),
            "tokenizer_name": self.tokenizer_name,
            "runtime": self._get_effective_mimo_runtime(),
            "language": self.language,
            "audio_tag": self.audio_tag,
            "max_tokens": self.max_tokens,
            "chunk_duration_seconds": self.chunk_duration_seconds,
            "chunk_overlap_seconds": self.chunk_overlap_seconds,
            "aligner_backend": self.aligner_backend,
            "aligner_language": self.aligner_language,
            "aligner_model_name": self.aligner_model_name,
            "aligner_worker_command": self.aligner_worker_command,
            "use_vad": self.use_vad,
            "fallback_without_vad": self.fallback_without_vad,
            "segments": [segment.model_dump() for segment in segments],
        }

    def _get_worker_command(self) -> Sequence[str]:
        """Get command used to run the MiMo worker.

        Returns:
            worker command
        """
        if self.worker_command is not None:
            return self.worker_command
        return [
            sys.executable,
            str(Path(__file__).with_name("mimo_worker.py")),
        ]

    def _get_effective_mimo_runtime(self) -> MimoRuntime:
        """Get the runtime used for this platform when auto mode is selected.

        Returns:
            concrete MiMo runtime
        """
        if self.mimo_runtime != MimoRuntime.AUTO:
            return self.mimo_runtime
        if platform.system() == "Darwin" and platform.machine() in {"arm64", "aarch64"}:
            return MimoRuntime.MLX
        raise MimoRuntimeUnsupportedError(
            "MiMo support currently requires Apple Silicon MLX. "
            "CUDA support is not included in this initial implementation."
        )

    def _get_effective_model_name(self) -> str:
        """Get the model name resolved for the selected runtime.

        Returns:
            model name or local model path
        """
        if self.model_name != MIMO_MODEL_NAME:
            return self.model_name
        if self._get_effective_mimo_runtime() == MimoRuntime.MLX:
            return MIMO_MLX_MODEL_NAME
        return self.model_name

    def _get_mimo_request(self, audio_path: Path) -> dict[str, object]:
        """Get a MiMo runtime request payload for an audio file.

        Arguments:
            audio_path: temporary WAV path to transcribe
        Returns:
            MiMo runtime request payload
        """
        request: dict[str, object] = {
            "audio_path": str(audio_path),
            "model_name": self._get_effective_model_name(),
            "tokenizer_name": self.tokenizer_name,
            "runtime": self._get_effective_mimo_runtime(),
            "language": self.language,
            "audio_tag": self.audio_tag,
        }
        if self.max_tokens is not None:
            request["max_tokens"] = self.max_tokens
        return request

    @staticmethod
    def _get_vad_speech_intervals(audio: AudioSegment) -> list[tuple[int, int]]:
        """Get padded speech intervals using Whisper's Silero VAD implementation.

        Arguments:
            audio: source audio
        Returns:
            speech start and end offsets in milliseconds
        Raises:
            MimoTranscriptionError: if Silero VAD is unavailable or fails
        """
        try:
            import torch  # noqa: PLC0415
            from whisper_timestamped.transcribe import (  # noqa: E501, PLC0415
                get_vad_segments,
            )
        except ImportError as exc:
            raise MimoTranscriptionError(
                "MiMo VAD requires the optional transcription dependencies."
            ) from exc

        normalized_audio = (
            audio.set_channels(1).set_frame_rate(_VAD_SAMPLE_RATE).set_sample_width(2)
        )
        samples = (
            np.array(
                normalized_audio.get_array_of_samples(),
                dtype=np.float32,
            )
            / np.iinfo(np.int16).max
        )
        audio_tensor = torch.from_numpy(samples)
        try:
            raw_intervals = get_vad_segments(
                audio_tensor,
                sample_rate=_VAD_SAMPLE_RATE,
                output_sample=False,
                min_silence_duration=_VAD_MIN_SILENCE_DURATION_SECONDS,
                dilatation=_VAD_PADDING_SECONDS,
                method="silero",
            )
        except (AssertionError, OSError, RuntimeError, ValueError) as exc:
            raise MimoTranscriptionError(f"Unable to run MiMo VAD: {exc}") from exc

        intervals = []
        for raw_interval in raw_intervals:
            start = raw_interval.get("start")
            end = raw_interval.get("end")
            if not isinstance(start, int | float) or not isinstance(end, int | float):
                raise MimoTranscriptionError("MiMo VAD returned malformed timestamps.")
            start_ms = max(0, round(float(start) * 1000))
            end_ms = min(len(audio), round(float(end) * 1000))
            if end_ms > start_ms:
                intervals.append((start_ms, end_ms))
        return intervals

    def _get_worker_env(self) -> Mapping[str, str]:
        """Get environment variables for worker subprocesses.

        Returns:
            subprocess environment with this source tree on PYTHONPATH
        """
        env = os.environ.copy()
        source_root_path = Path(__file__).resolve().parents[3]
        python_paths = [str(source_root_path)]
        if current_pythonpath := env.get("PYTHONPATH"):
            python_paths.extend(current_pythonpath.split(os.pathsep))
        env["PYTHONPATH"] = os.pathsep.join(python_paths)
        return env

    def _run_in_process(self, audio_path: Path) -> dict[str, object]:
        """Run MiMo in the current Python process.

        Arguments:
            audio_path: temporary WAV path to transcribe
        Returns:
            MiMo output payload
        Raises:
            MimoWorkerError: if in-process MiMo fails
        """
        try:
            return transcribe_with_mimo(self._get_mimo_request(audio_path))
        except (ImportError, OSError, RuntimeError, ValueError) as exc:
            raise MimoWorkerError(f"Unable to run MiMo in-process: {exc}") from exc

    def _run_mimo(self, audio_path: Path) -> dict[str, object]:
        """Run MiMo using the configured execution mode.

        Arguments:
            audio_path: temporary WAV path to transcribe
        Returns:
            MiMo output payload
        """
        if self.worker_command is not None:
            return self._run_worker(audio_path)
        return self._run_in_process(audio_path)

    def _run_worker(self, audio_path: Path) -> dict[str, object]:
        """Run the MiMo worker process for one audio file.

        Arguments:
            audio_path: temporary WAV path to transcribe
        Returns:
            worker output payload
        Raises:
            MimoWorkerError: if the worker fails or returns malformed output
        """
        request = self._get_mimo_request(audio_path)
        try:
            result = subprocess.run(
                self._get_worker_command(),
                input=json.dumps(request, ensure_ascii=False),
                text=True,
                capture_output=True,
                check=False,
                timeout=self.worker_timeout_seconds,
                env=self._get_worker_env(),
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise MimoWorkerError(f"Unable to run MiMo worker: {exc}") from exc
        if result.returncode != 0:
            raise MimoWorkerError(
                f"MiMo worker exited with status {result.returncode}: "
                f"{result.stderr.strip()}"
            )
        return self._parse_worker_stdout(result.stdout)

    @staticmethod
    def _parse_worker_stdout(stdout_text: str) -> dict[str, object]:
        """Parse worker stdout, accepting logging before the final JSON line.

        Arguments:
            stdout_text: worker stdout
        Returns:
            parsed worker payload
        Raises:
            MimoWorkerError: if no JSON object is found
        """
        for line in reversed(stdout_text.splitlines()):
            stripped_line = line.strip()
            if not stripped_line:
                continue
            try:
                payload = json.loads(stripped_line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                return payload
        raise MimoWorkerError("MiMo worker did not return a JSON object.")

    def _transcribe_audio_window(
        self,
        audio: AudioSegment,
    ) -> list[TranscribedSegment]:
        """Run MiMo transcription and timestamp alignment for one audio window.

        Arguments:
            audio: audio to transcribe
        Returns:
            timestamped transcription segments
        Raises:
            MimoTranscriptionError: if MiMo returns unusable text
            TranscriptionAlignmentError: if forced alignment fails
        """
        with get_temp_file_path(suffix=".wav") as temp_audio_path:
            audio.export(temp_audio_path, format="wav")
            worker_payload = self._run_mimo(temp_audio_path)
            text = worker_payload.get("text")
            if not isinstance(text, str) or not text.strip():
                raise MimoTranscriptEmptyError("MiMo returned empty transcript.")
            content_characters = {char for char in text if char.isalnum()}
            if content_characters and content_characters <= _LOW_INFORMATION_CHARACTERS:
                raise MimoTranscriptionError(
                    f"MiMo returned only low-information vocalizations: {text!r}"
                )
            duration_seconds = worker_payload.get("duration_seconds")
            if isinstance(duration_seconds, int | float):
                duration = float(duration_seconds)
            else:
                duration = len(audio) / 1000
            return align_mimo_transcription(
                temp_audio_path,
                text,
                duration_seconds=duration,
                aligner_backend=self.aligner_backend,
                aligner_language=self.aligner_language,
                aligner_model_name=self.aligner_model_name,
                aligner_worker_command=self.aligner_worker_command,
                aligner_worker_timeout_seconds=self.aligner_worker_timeout_seconds,
            )

    def _transcribe_chunked_audio(
        self,
        audio: AudioSegment,
    ) -> list[TranscribedSegment]:
        """Run MiMo transcription over shorter overlapping chunks.

        Arguments:
            audio: audio to transcribe
        Returns:
            timestamped transcription segments
        """
        assert self.chunk_duration_seconds is not None
        chunk_duration_ms = int(round(self.chunk_duration_seconds * 1000))
        chunk_overlap_ms = int(round(self.chunk_overlap_seconds * 1000))
        segments: list[TranscribedSegment] = []

        core_start_ms = 0
        while core_start_ms < len(audio):
            core_end_ms = min(len(audio), core_start_ms + chunk_duration_ms)
            window_start_ms = max(0, core_start_ms - chunk_overlap_ms)
            window_end_ms = min(len(audio), core_end_ms + chunk_overlap_ms)
            window_audio = audio[window_start_ms:window_end_ms]
            window_segments = self._transcribe_audio_window(window_audio)
            segments.extend(
                self._get_offset_core_segments(
                    window_segments,
                    offset_seconds=window_start_ms / 1000,
                    core_start_seconds=core_start_ms / 1000,
                    core_end_seconds=core_end_ms / 1000,
                    start_id=len(segments),
                )
            )
            core_start_ms = core_end_ms

        return segments

    def _transcribe_uncached(self, audio: AudioSegment) -> list[TranscribedSegment]:
        """Run MiMo transcription and timestamp alignment without cache lookup.

        Arguments:
            audio: audio to transcribe
        Returns:
            timestamped transcription segments
        Raises:
            MimoTranscriptionError: if MiMo returns unusable text
            TranscriptionAlignmentError: if forced alignment fails
        """
        if self.use_vad:
            try:
                return self._transcribe_vad_audio(audio)
            except (MimoTranscriptionError, TranscriptionAlignmentError) as exc:
                if not self.fallback_without_vad:
                    raise
                logger.info(
                    f"Retrying MiMo without VAD after the VAD attempt failed: {exc}"
                )
        return self._transcribe_unfiltered_audio(audio)

    def _transcribe_unfiltered_audio(
        self,
        audio: AudioSegment,
    ) -> list[TranscribedSegment]:
        """Transcribe audio without applying VAD.

        Arguments:
            audio: audio to transcribe
        Returns:
            timestamped transcription segments
        """
        if self.chunk_duration_seconds is None:
            return self._transcribe_audio_window(audio)
        if len(audio) <= int(round(self.chunk_duration_seconds * 1000)):
            return self._transcribe_audio_window(audio)
        return self._transcribe_chunked_audio(audio)

    def _transcribe_vad_audio(
        self,
        audio: AudioSegment,
    ) -> list[TranscribedSegment]:
        """Transcribe detected speech and restore original-audio timestamps.

        Arguments:
            audio: original audio containing speech and non-speech regions
        Returns:
            timestamped transcription segments on the original audio timeline
        Raises:
            MimoTranscriptEmptyError: if VAD finds no speech
        """
        speech_intervals = self._get_vad_speech_intervals(audio)
        if not speech_intervals:
            raise MimoTranscriptEmptyError("MiMo VAD found no speech.")

        logger.info(
            f"MiMo VAD retained {len(speech_intervals)} speech interval(s) "
            f"from {len(audio) / 1000:.2f}s of audio"
        )
        speech_audio = audio[0:0]
        for start_ms, end_ms in speech_intervals:
            speech_audio += audio[start_ms:end_ms]

        speech_segments = self._transcribe_unfiltered_audio(speech_audio)
        return self._restore_vad_timestamps(speech_segments, speech_intervals)

    @staticmethod
    def _restore_vad_timestamps(
        segments: Sequence[TranscribedSegment],
        speech_intervals: Sequence[tuple[int, int]],
    ) -> list[TranscribedSegment]:
        """Map speech-only word timings back to the original audio timeline.

        Arguments:
            segments: transcription timed against concatenated speech audio
            speech_intervals: original-audio speech intervals in milliseconds
        Returns:
            segments split and timed against the original audio
        Raises:
            TranscriptionAlignmentError: if aligned output lacks word timings
        """
        compressed_intervals = []
        compressed_start_ms = 0
        for original_start_ms, original_end_ms in speech_intervals:
            duration_ms = original_end_ms - original_start_ms
            compressed_end_ms = compressed_start_ms + duration_ms
            compressed_intervals.append(
                (
                    compressed_start_ms,
                    compressed_end_ms,
                    original_start_ms,
                    original_end_ms,
                )
            )
            compressed_start_ms = compressed_end_ms

        output_segments: list[TranscribedSegment] = []
        current_interval_idx = -1
        current_words: list[TranscribedWord] = []

        def append_current_segment():
            """Append accumulated words as one original-timeline segment."""
            nonlocal current_words
            if not current_words:
                return
            output_segments.append(
                TranscribedSegment(
                    id=len(output_segments),
                    seek=0,
                    start=current_words[0].start,
                    end=current_words[-1].end,
                    text="".join(word.text for word in current_words),
                    words=current_words,
                )
            )
            current_words = []

        for segment in segments:
            if not segment.words:
                raise TranscriptionAlignmentError(
                    "MiMo VAD cannot restore a segment without word timings."
                )
            for word in segment.words:
                word_start_ms = round(word.start * 1000)
                word_end_ms = round(word.end * 1000)
                word_midpoint_ms = (word_start_ms + word_end_ms) / 2
                interval_idx = len(compressed_intervals) - 1
                for candidate_idx, compressed_interval in enumerate(
                    compressed_intervals
                ):
                    if word_midpoint_ms <= compressed_interval[1]:
                        interval_idx = candidate_idx
                        break

                if interval_idx != current_interval_idx:
                    append_current_segment()
                    current_interval_idx = interval_idx

                (
                    interval_compressed_start_ms,
                    interval_compressed_end_ms,
                    interval_original_start_ms,
                    interval_original_end_ms,
                ) = compressed_intervals[interval_idx]
                mapped_start_ms = interval_original_start_ms + max(
                    0,
                    min(
                        word_start_ms - interval_compressed_start_ms,
                        interval_compressed_end_ms - interval_compressed_start_ms,
                    ),
                )
                mapped_end_ms = interval_original_start_ms + max(
                    0,
                    min(
                        word_end_ms - interval_compressed_start_ms,
                        interval_compressed_end_ms - interval_compressed_start_ms,
                    ),
                )
                mapped_end_ms = min(mapped_end_ms, interval_original_end_ms)
                current_words.append(
                    word.model_copy(
                        update={
                            "start": mapped_start_ms / 1000,
                            "end": mapped_end_ms / 1000,
                        }
                    )
                )

        append_current_segment()
        return output_segments

    @staticmethod
    def _get_offset_core_segments(
        segments: Sequence[TranscribedSegment],
        *,
        offset_seconds: float,
        core_start_seconds: float,
        core_end_seconds: float,
        start_id: int,
    ) -> list[TranscribedSegment]:
        """Offset chunk-local segments and keep only core-window segments.

        Arguments:
            segments: chunk-local timestamped segments
            offset_seconds: offset from chunk-local time to original audio time
            core_start_seconds: inclusive start of non-overlap core
            core_end_seconds: exclusive end of non-overlap core
            start_id: first segment id to assign
        Returns:
            offset segments whose midpoint falls inside the core window
        """
        offset_segments = []
        for segment in segments:
            global_start = segment.start + offset_seconds
            global_end = segment.end + offset_seconds
            midpoint = (global_start + global_end) / 2
            if midpoint < core_start_seconds or midpoint >= core_end_seconds:
                continue

            words = None
            if segment.words is not None:
                words = [
                    word.model_copy(
                        update={
                            "start": word.start + offset_seconds,
                            "end": word.end + offset_seconds,
                        }
                    )
                    for word in segment.words
                ]
            offset_segments.append(
                segment.model_copy(
                    update={
                        "id": start_id + len(offset_segments),
                        "start": global_start,
                        "end": global_end,
                        "words": words,
                    }
                )
            )
        return offset_segments
