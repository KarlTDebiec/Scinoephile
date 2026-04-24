#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Separates vocals from audio using Demucs."""

from __future__ import annotations

from logging import getLogger
from typing import Any

import numpy as np
import torch
import torchaudio.functional
from demucs_infer.apply import apply_model
from demucs_infer.pretrained import get_model
from pydub import AudioSegment

from scinoephile.core import ScinoephileError

logger = getLogger(__name__)


class DemucsSeparator:
    """Separates vocals from audio using a Demucs model."""

    def __init__(self, model_name: str = "htdemucs_ft", shifts: int = 0):
        """Initialize.

        Arguments:
            model_name: Demucs model name used for source separation
            shifts: number of random shift-averaging passes; set to 0 for
                deterministic output suitable for caching
        """
        self.model_name = model_name
        self.shifts = shifts
        self._model: Any | None = None

    @property
    def device(self) -> str:
        """Execution device for Demucs inference.

        Returns:
            device identifier
        """
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"

    @property
    def model(self) -> Any:
        """Get the cached Demucs model, loading it if needed.

        Returns:
            loaded Demucs model
        """
        if self._model is None:
            try:
                self._model = get_model(self.model_name).to(self.device).eval()
            except Exception as exc:
                raise ScinoephileError(
                    f"Unable to load Demucs model '{self.model_name}'."
                ) from exc
        return self._model

    def __call__(self, audio: AudioSegment) -> AudioSegment:
        """Separate vocals from audio.

        Arguments:
            audio: audio to separate
        Returns:
            vocals-only audio
        """
        return self.separate_vocals(audio)

    def separate_vocals(self, audio: AudioSegment) -> AudioSegment:
        """Separate vocals from audio.

        Arguments:
            audio: audio to separate
        Returns:
            vocals-only audio
        """
        normalized_audio = audio.set_sample_width(2)
        input_channels = normalized_audio.channels
        if input_channels == 1:
            normalized_audio = normalized_audio.set_channels(2)
        waveform = self._get_waveform(normalized_audio)
        target_frame_rate = getattr(
            self.model, "samplerate", normalized_audio.frame_rate
        )
        if normalized_audio.frame_rate != target_frame_rate:
            waveform = torchaudio.functional.resample(
                waveform, normalized_audio.frame_rate, target_frame_rate
            )

        with torch.no_grad():
            try:
                sources = apply_model(
                    self.model,
                    waveform.unsqueeze(0).to(self.device),
                    shifts=self.shifts,
                    device=self.device,
                )
            except Exception as exc:
                raise ScinoephileError("Demucs separation failed.") from exc

        source_names = tuple(getattr(self.model, "sources", ()))
        try:
            vocals_idx = source_names.index("vocals")
        except ValueError as exc:
            raise ScinoephileError(
                f"Demucs model '{self.model_name}' does not provide a vocals stem."
            ) from exc

        vocals = sources[0, vocals_idx].cpu()
        if target_frame_rate != normalized_audio.frame_rate:
            vocals = torchaudio.functional.resample(
                vocals, target_frame_rate, normalized_audio.frame_rate
            )

        return self._get_audio_segment(
            vocals=vocals,
            frame_rate=normalized_audio.frame_rate,
            channels=input_channels,
        )

    @staticmethod
    def _get_audio_segment(
        *,
        vocals: torch.Tensor,
        frame_rate: int,
        channels: int,
    ) -> AudioSegment:
        """Convert separated vocals waveform into a pydub AudioSegment.

        Arguments:
            vocals: separated vocals waveform as [channels, time]
            frame_rate: output frame rate
            channels: output channel count
        Returns:
            audio segment containing the separated vocals
        """
        array = vocals.numpy()
        if array.ndim != 2:
            raise ScinoephileError(
                f"Expected Demucs vocals to have 2 dimensions, found {array.ndim}."
            )
        if channels == 1 and array.shape[0] >= 1:
            array = array[:1]
        elif array.shape[0] != channels:
            logger.warning(
                "Demucs channel count %s differed from input channel count %s.",
                array.shape[0],
                channels,
            )
            channels = int(array.shape[0])

        clipped = np.clip(array, -1.0, 1.0)
        interleaved = (clipped.T.reshape(-1) * np.iinfo(np.int16).max).astype(np.int16)
        return AudioSegment(
            data=interleaved.tobytes(),
            sample_width=2,
            frame_rate=frame_rate,
            channels=channels,
        )

    @staticmethod
    def _get_waveform(audio: AudioSegment) -> torch.Tensor:
        """Convert a pydub AudioSegment into a waveform tensor.

        Arguments:
            audio: audio segment to convert
        Returns:
            waveform tensor as [channels, time]
        """
        array = np.array(audio.get_array_of_samples(), dtype=np.int16)
        waveform = torch.from_numpy(
            array.reshape((-1, audio.channels)).T.astype(np.float32)
            / np.iinfo(np.int16).max
        )
        return waveform
