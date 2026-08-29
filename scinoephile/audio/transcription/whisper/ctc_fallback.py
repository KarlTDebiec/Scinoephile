#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Aligns native Whisper output after timestamped decoding fails."""

from __future__ import annotations

from collections.abc import Sequence
from logging import getLogger
from pathlib import Path

from pydub import AudioSegment

from scinoephile.audio.transcription.ctc.aligner import CtcAligner
from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment

from .model import WhisperModel

__all__ = ["get_ctc_fallback_segments"]

logger = getLogger(__name__)


def get_ctc_fallback_segments(
    model: WhisperModel,
    ctc_aligner: CtcAligner,
    audio: AudioSegment,
    audio_path: Path,
    sample_len: int,
    timestamp_error: AssertionError,
    *,
    temperature: float | Sequence[float],
    condition_on_previous_text: bool,
) -> list[TranscribedSegment]:
    """Decode text natively and align it after Whisper timestamping fails.

    Arguments:
        model: configured executable Whisper model
        ctc_aligner: CTC aligner used to recover word timings
        audio: audio being transcribed
        audio_path: temporary audio file passed to native Whisper
        sample_len: maximum number of tokens decoded per Whisper window
        timestamp_error: assertion raised by Whisper Timestamped
        temperature: decoding temperature or fallback schedule
        condition_on_previous_text: whether to condition each decode window on the
            preceding window
    Returns:
        CTC-aligned native Whisper transcript
    Raises:
        TranscriptionAlignmentError: if CTC alignment fails
        TranscriptionEmptyError: if native Whisper returns empty text
        TranscriptionRecognitionError: if native Whisper fails or returns malformed
            output
    """
    logger.info(
        f"Retrying Whisper after timestamp alignment failed ({timestamp_error}) "
        f"using native decoding and CTC model {ctc_aligner.model.spec.name}"
    )
    result = model.transcribe_native(
        audio_path,
        temperature=temperature,
        condition_on_previous_text=condition_on_previous_text,
        sample_len=sample_len,
    )

    # Preserve the least favorable native quality signals across CTC timing
    quality_signals: dict[str, float] = {}
    avg_logprobs = [
        segment.avg_logprob
        for segment in result.segments
        if segment.avg_logprob is not None
    ]
    if avg_logprobs:
        quality_signals["avg_logprob"] = min(avg_logprobs)
    compression_ratios = [
        segment.compression_ratio
        for segment in result.segments
        if segment.compression_ratio is not None
    ]
    if compression_ratios:
        quality_signals["compression_ratio"] = max(compression_ratios)
    no_speech_probs = [
        segment.no_speech_prob
        for segment in result.segments
        if segment.no_speech_prob is not None
    ]
    if no_speech_probs:
        quality_signals["no_speech_prob"] = max(no_speech_probs)

    return [
        segment.model_copy(update=quality_signals)
        for segment in ctc_aligner(audio, result.text)
    ]
