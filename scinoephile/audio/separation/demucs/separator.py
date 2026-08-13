#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Separates vocals from audio using Demucs."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from pydub import AudioSegment

from scinoephile.core.dependencies.transcription import (
    import_demucs_infer_apply,
    import_demucs_infer_pretrained,
    import_torch,
    import_torchaudio,
)
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.ml import get_torch_device

from .cache import DemucsCache

__all__ = ["DemucsSeparator"]

if TYPE_CHECKING:
    from scinoephile.core.dependencies.transcription import DemucsModel, TorchTensor

logger = getLogger(__name__)


class DemucsSeparator:
    """Separates vocals from audio using a Demucs model."""

    def __init__(
        self,
        model_name: str = "htdemucs_ft",
        cache_root_path: Path | None = None,
        overwrite_cache: bool = False,
    ):
        """Initialize.

        Arguments:
            model_name: Demucs model name used for source separation
            cache_root_path: root directory beneath which to cache
            overwrite_cache: whether to replace matching cache files
        """
        self.model_name = model_name
        """Demucs model name used for source separation."""

        self._device: str | None = None
        """Torch device identifier used for inference."""

        self._model: DemucsModel | None = None
        """Cached Demucs model."""

        self._cache = DemucsCache(cache_root_path, model_name, overwrite_cache)
        """Cache of vocals separated with the configured model."""

    def __call__(self, audio: AudioSegment) -> AudioSegment:
        """Separate vocals from audio.

        Arguments:
            audio: audio to separate
        Returns:
            vocals-only audio
        """
        return self.separate_vocals(audio)

    @property
    def cache_identity(self) -> dict[str, object]:
        """Get the Demucs model and runtime cache identity."""
        return self._cache.cache_identity

    @property
    def device(self) -> str:
        """Get torch device identifier."""
        if self._device is None:
            self._device = get_torch_device()
        return self._device

    @property
    def model(self) -> DemucsModel:
        """Get the cached Demucs model, loading it if needed.

        Returns:
            loaded Demucs model
        """
        if self._model is None:
            demucs_infer_pretrained = import_demucs_infer_pretrained()
            try:
                self._model = (
                    demucs_infer_pretrained.get_model(self.model_name)
                    .to(self.device)
                    .eval()
                )
            except Exception as exc:
                raise ScinoephileError(
                    f"Unable to load Demucs model '{self.model_name}'."
                ) from exc
        return self._model

    def separate_vocals(self, audio: AudioSegment) -> AudioSegment:
        """Separate vocals from audio.

        Arguments:
            audio: audio to separate
        Returns:
            vocals-only audio
        """
        # Load matching cached vocals before running separation
        cached_vocals = self._cache.load(audio)
        if cached_vocals is not None:
            return cached_vocals

        # Run separation and atomically update the cache
        vocals = self._separate_vocals(audio)
        self._cache.save(audio, vocals)
        return vocals

    def _separate_vocals(self, audio: AudioSegment) -> AudioSegment:
        """Separate vocals using Demucs.

        Arguments:
            audio: audio to separate
        Returns:
            vocals-only audio
        """
        # Normalize input samples and channel layout for Demucs
        normalized_audio = audio.set_sample_width(2)
        input_channels = normalized_audio.channels
        if input_channels == 1:
            normalized_audio = normalized_audio.set_channels(2)
        waveform = self._get_waveform(normalized_audio)

        # Resample input to the model's sample rate
        target_frame_rate = getattr(
            self.model, "samplerate", normalized_audio.frame_rate
        )
        if normalized_audio.frame_rate != target_frame_rate:
            torchaudio = import_torchaudio()
            waveform = torchaudio.functional.resample(
                waveform, normalized_audio.frame_rate, target_frame_rate
            )

        # Run source separation using the library's default shift behavior
        torch = import_torch()
        demucs_infer_apply = import_demucs_infer_apply()
        with torch.no_grad():
            try:
                sources = demucs_infer_apply.apply_model(
                    self.model,
                    waveform.unsqueeze(0).to(self.device),
                    device=self.device,
                )
            except Exception as exc:
                raise ScinoephileError("Demucs separation failed.") from exc

        # Select the vocals stem and restore the input sample rate
        source_names = tuple(getattr(self.model, "sources", ()))
        try:
            vocals_idx = source_names.index("vocals")
        except ValueError as exc:
            raise ScinoephileError(
                f"Demucs model '{self.model_name}' does not provide a vocals stem."
            ) from exc
        vocals = sources[0, vocals_idx].cpu()
        if target_frame_rate != normalized_audio.frame_rate:
            torchaudio = import_torchaudio()
            vocals = torchaudio.functional.resample(
                vocals, target_frame_rate, normalized_audio.frame_rate
            )

        # Restore the original channel layout and convert back to pydub
        return self._get_audio_segment(
            vocals, normalized_audio.frame_rate, input_channels
        )

    @staticmethod
    def _get_audio_segment(
        vocals: TorchTensor, frame_rate: int, channels: int
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
    def _get_waveform(audio: AudioSegment) -> TorchTensor:
        """Convert a pydub AudioSegment into a waveform tensor.

        Arguments:
            audio: audio segment to convert
        Returns:
            waveform tensor as [channels, time]
        """
        array = np.array(audio.get_array_of_samples(), dtype=np.int16)
        torch = import_torch()
        waveform = torch.from_numpy(
            array.reshape((-1, audio.channels)).T.astype(np.float32)
            / np.iinfo(np.int16).max
        )
        return waveform
