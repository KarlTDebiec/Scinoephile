#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Voice activity detection provider contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import StrEnum
from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING

from .intervals import get_threshold_speech_intervals
from .trace import VoiceActivityTrace

__all__ = ["VadImplementation", "VadProvider"]

if TYPE_CHECKING:
    from pydub import AudioSegment


class VadImplementation(StrEnum):
    """Voice activity detection implementations."""

    PYANNOTE = "pyannote"
    """Use pyannote's speaker-segmentation model as a speech detector."""
    SILERO = "silero"
    """Use the official Silero VAD runtime."""
    TEN = "ten"
    """Use the official TEN VAD runtime."""


class VadProvider(ABC):
    """Provider of implementation-specific voice activity detection."""

    implementation: VadImplementation
    """Voice activity detection implementation."""

    sample_rate: int
    """Input sample rate expected by the implementation."""

    @property
    @abstractmethod
    def cache_identity(self) -> dict[str, object]:
        """Get the model, runtime, and inference configuration identity."""
        raise NotImplementedError()

    def get_speech_intervals(
        self,
        trace: VoiceActivityTrace,
        *,
        threshold: float,
        min_speech_duration_seconds: float,
        min_silence_duration_seconds: float,
        padding_seconds: float,
    ) -> list[tuple[int, int]]:
        """Derive configured binary speech intervals from a model-score trace.

        Arguments:
            trace: frame-level voice activity model scores
            threshold: minimum model score treated as speech
            min_speech_duration_seconds: minimum retained speech duration
            min_silence_duration_seconds: minimum silence separating intervals
            padding_seconds: context retained around detected speech
        Returns:
            speech start and end offsets in milliseconds
        """
        return get_threshold_speech_intervals(
            trace,
            threshold=threshold,
            min_speech_duration_seconds=min_speech_duration_seconds,
            min_silence_duration_seconds=min_silence_duration_seconds,
            padding_seconds=padding_seconds,
        )

    @abstractmethod
    def get_trace(self, audio: AudioSegment) -> VoiceActivityTrace:
        """Infer frame-level voice activity scores.

        Arguments:
            audio: source audio
        Returns:
            model scores aligned to the source timeline
        """
        raise NotImplementedError()

    @staticmethod
    def _get_distribution_identity(distribution_name: str) -> dict[str, str]:
        """Get an installed distribution's name and version.

        Arguments:
            distribution_name: installed distribution name
        Returns:
            distribution name and installed version
        """
        try:
            distribution_version = version(distribution_name)
        except PackageNotFoundError:
            distribution_version = "unavailable"
        return {"distribution": distribution_name, "version": distribution_version}
