#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Separates vocals from audio using Demucs."""

from __future__ import annotations

import hashlib
from logging import getLogger
from pathlib import Path
from typing import Any

import numpy as np
from pydub import AudioSegment

from scinoephile.common.validation import val_output_dir_path
from scinoephile.core import ScinoephileError
from scinoephile.core.ml import get_torch_device

__all__ = ["DemucsSeparator"]

logger = getLogger(__name__)

_TRANSCRIPTION_EXTRA_MESSAGE = (
    "Demucs separation support requires optional transcription dependencies. "
    "Install scinoephile with the 'transcription' extra."
)


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

        self._device: str | None = None
        """Torch device identifier used for inference."""

        self._model: Any | None = None
        """Cached Demucs model."""

        self.cache_dir_path = None
        """Optional directory in which to cache separated vocals."""
        if cache_dir_path is not None:
            self.cache_dir_path = val_output_dir_path(cache_dir_path)

    def __call__(
        self,
        audio: AudioSegment,
        *,
        overwrite_cache: bool = False,
    ) -> AudioSegment:
        """Separate vocals from audio.

        Arguments:
            audio: audio to separate
            overwrite_cache: whether to replace a matching cached separation
        Returns:
            vocals-only audio
        """
        return self.separate_vocals(audio, overwrite_cache=overwrite_cache)

    @property
    def device(self) -> str:
        """Get torch device identifier."""
        if self._device is None:
            self._device = get_torch_device()
        return self._device

    @property
    def model(self) -> Any:
        """Get the cached Demucs model, loading it if needed.

        Returns:
            loaded Demucs model
        """
        if self._model is None:
            get_model = self._import_demucs_infer_get_model()
            try:
                self._model = get_model(self.model_name).to(self.device).eval()
            except Exception as exc:
                raise ScinoephileError(
                    f"Unable to load Demucs model '{self.model_name}'."
                ) from exc
        return self._model

    def get_cached_vocals(
        self,
        cache_audio: AudioSegment,
        *,
        overwrite_cache: bool = False,
    ) -> AudioSegment | None:
        """Get cached vocals separation for audio if available.

        Arguments:
            cache_audio: audio used for cache-key generation
            overwrite_cache: whether to remove a matching cached separation
        Returns:
            cached vocals-only audio, if present
        """
        cache_path = self._get_cache_path(cache_audio)
        if cache_path is None or not cache_path.exists():
            return None
        if overwrite_cache:
            cache_path.unlink()
            logger.info(f"Removed Demucs vocals cache: {cache_path}")
            return None
        logger.info(f"Loaded Demucs vocals from cache: {cache_path}")
        vocals = AudioSegment.from_file(cache_path)
        cache_path.touch()
        return vocals

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
            torchaudio_functional = self._import_torchaudio_functional()
            waveform = torchaudio_functional.resample(
                waveform, normalized_audio.frame_rate, target_frame_rate
            )

        torch = self._import_torch()
        apply_model = self._import_demucs_infer_apply_model()
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
            torchaudio_functional = self._import_torchaudio_functional()
            vocals = torchaudio_functional.resample(
                vocals, target_frame_rate, normalized_audio.frame_rate
            )

        return self._get_audio_segment(
            vocals=vocals,
            frame_rate=normalized_audio.frame_rate,
            channels=input_channels,
        )

    def separate_vocals(
        self,
        audio: AudioSegment,
        *,
        overwrite_cache: bool = False,
    ) -> AudioSegment:
        """Separate vocals from audio.

        Arguments:
            audio: audio to separate
            overwrite_cache: whether to replace a matching cached separation
        Returns:
            vocals-only audio
        """
        if (
            cached := self.get_cached_vocals(
                audio,
                overwrite_cache=overwrite_cache,
            )
        ) is not None:
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
        vocals: Any,
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
    def _import_demucs_infer_apply_model() -> Any:
        """Import Demucs apply_model on demand."""
        try:
            from demucs_infer.apply import (  # noqa: E501, PLC0415
                apply_model,
            )
        except ImportError as exc:
            raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
        return apply_model

    @staticmethod
    def _import_demucs_infer_get_model() -> Any:
        """Import Demucs model loader on demand."""
        try:
            from demucs_infer.pretrained import (  # noqa: E501, PLC0415
                get_model,
            )
        except ImportError as exc:
            raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
        return get_model

    @staticmethod
    def _import_torch() -> Any:
        """Import torch on demand."""
        try:
            import torch  # noqa: PLC0415
        except ImportError as exc:
            raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
        return torch

    @staticmethod
    def _import_torchaudio_functional() -> Any:
        """Import torchaudio.functional on demand."""
        try:
            from torchaudio import (  # noqa: PLC0415
                functional,
            )
        except ImportError as exc:
            raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
        return functional

    @staticmethod
    def _get_waveform(audio: AudioSegment) -> Any:
        """Convert a pydub AudioSegment into a waveform tensor.

        Arguments:
            audio: audio segment to convert
        Returns:
            waveform tensor as [channels, time]
        """
        array = np.array(audio.get_array_of_samples(), dtype=np.int16)
        torch = DemucsSeparator._import_torch()
        waveform = torch.from_numpy(
            array.reshape((-1, audio.channels)).T.astype(np.float32)
            / np.iinfo(np.int16).max
        )
        return waveform
