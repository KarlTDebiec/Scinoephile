#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Separates vocals from audio using Demucs."""

from __future__ import annotations

import hashlib
from logging import getLogger
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torchaudio.functional
from demucs_infer.apply import apply_model
from demucs_infer.pretrained import get_model
from pydub import AudioSegment

from scinoephile.common.validation import val_output_dir_path
from scinoephile.core import ScinoephileError
from scinoephile.core.ml import get_torch_device

__all__ = ["DemucsSeparator"]

logger = getLogger(__name__)


class DemucsSeparator:
    """Separates vocals from audio using a Demucs model."""

    def __init__(
        self,
        model_name: str = "htdemucs_ft",
        *,
        cache_dir_path: Path | None = None,
    ):
        """Initialize.

        Arguments:
            model_name: Demucs model name used for source separation
            cache_dir_path: directory in which to cache separated vocals
        """
        self.model_name = model_name
        """Demucs model name used for source separation."""

        self.device = get_torch_device()
        """Torch device identifier used for inference."""

        self._model: Any | None = None
        """Cached Demucs model."""

        self.cache_dir_path = None
        """Optional directory in which to cache separated vocals."""
        if cache_dir_path is not None:
            self.cache_dir_path = val_output_dir_path(cache_dir_path)

    def __call__(self, audio: AudioSegment) -> AudioSegment:
        """Separate vocals from audio.

        Arguments:
            audio: audio to separate
        Returns:
            vocals-only audio
        """
        return self.separate_vocals(audio)

    def get_cached_vocals(self, cache_audio: AudioSegment) -> AudioSegment | None:
        """Get cached vocals separation for audio if available.

        Arguments:
            cache_audio: audio used for cache-key generation
        Returns:
            cached vocals-only audio, if present
        """
        cache_path = self._get_cache_path(cache_audio)
        if cache_path is None or not cache_path.exists():
            return None
        logger.info(f"Loaded Demucs vocals from cache: {cache_path}")
        vocals = AudioSegment.from_file(cache_path)
        cache_path.touch()
        return vocals

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

    def _separate_vocals_uncached(self, audio: AudioSegment) -> AudioSegment:
        """Separate vocals without consulting or updating the cache.

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

    def separate_vocals(self, audio: AudioSegment) -> AudioSegment:
        """Separate vocals from audio.

        Arguments:
            audio: audio to separate
        Returns:
            vocals-only audio
        """
        if (cached := self.get_cached_vocals(audio)) is not None:
            return cached

        vocals = self._separate_vocals_uncached(audio)
        cache_path = self._get_cache_path(audio)
        if cache_path is not None:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            vocals.export(cache_path, format="wav")
            logger.info(f"Saved Demucs vocals to cache: {cache_path}")
        return vocals

    def _get_cache_path(self, audio: AudioSegment) -> Path | None:
        """Get cache path based on hash of audio data and model configuration.

        Arguments:
            audio: audio used to derive the cache key
        Returns:
            path to cache file
        """
        if self.cache_dir_path is None:
            return None
        audio_sha256 = hashlib.sha256(audio.raw_data).hexdigest()
        cache_key = (
            f"{audio_sha256}_{self.model_name}_"
            f"channels-{audio.channels}_"
            f"frame_rate-{audio.frame_rate}_"
            f"sample_width-{audio.sample_width}"
        )
        cache_sha256 = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()
        return self.cache_dir_path / f"{cache_sha256}.wav"

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
                f"Demucs channel count {array.shape[0]} differed from input "
                f"channel count {channels}."
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
