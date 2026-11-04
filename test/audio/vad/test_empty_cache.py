#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Regressions for recovering empty or truncated voice activity cache entries."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import numpy as np
from pydub import AudioSegment
from pytest import LogCaptureFixture

from scinoephile.analysis.transcription.artifact import AlignmentSource
from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.vad import (
    SpeechBlockSplitter,
    VoiceActivityCache,
    VoiceActivityDetector,
    VoiceActivityTrace,
)
from scinoephile.core import Language
from scinoephile.core.cache.identity import CacheIdentity
from scinoephile.workflows.transcription_pipeline import (
    AudioAnalysisMode,
    TranscriptionPipeline,
)
from test.helpers import parametrize


@parametrize("payload", [b"", b"\x93NUMPY"])
def test_empty_or_truncated_vad_cache_is_discarded(
    tmp_path: Path, caplog: LogCaptureFixture, payload: bytes
):
    """Treat an incomplete archive as a cache miss and remove the unusable file.

    Arguments:
        tmp_path: temporary cache root
        caplog: fixture capturing the invalid-entry diagnostic
        payload: incomplete cache file contents
    """
    cache = VoiceActivityCache(tmp_path)
    audio = AudioSegment.silent(duration=1000, frame_rate=16000)
    cache_identity: CacheIdentity = {"implementation": "test"}
    cache_path = cache.get_path(audio, cache_identity)
    cache_path.write_bytes(payload)

    assert cache.load(audio, cache_identity) is None
    assert not cache_path.exists()
    assert "Discarded invalid voice activity trace cache" in caplog.text
    assert cache.load(audio, cache_identity) is None


def test_pipeline_regenerates_and_reuses_an_empty_vad_cache(tmp_path: Path):
    """Infer once after an empty cache entry and reuse the complete replacement.

    Arguments:
        tmp_path: temporary cache root
    """
    audio_series = AudioSeries(AudioSegment.silent(duration=1000, frame_rate=16000))
    cache = VoiceActivityCache(tmp_path)
    detector = Mock(spec=VoiceActivityDetector)
    cache_identity: CacheIdentity = {"implementation": "test"}
    detector.trace_cache_identity = cache_identity
    detector.get_trace.return_value = VoiceActivityTrace(
        np.ones(10, dtype=np.float32), start_ms=50, step_ms=100, duration_ms=1000
    )
    transcriber = Mock()
    transcriber.transcribers = {"source": Mock()}
    pipeline = TranscriptionPipeline(
        language=Language.yue_hant,
        transcriber=transcriber,
        alignment_sources=(
            AlignmentSource(name="source", backend="test", model="test"),
        ),
        audio_event_mode=AudioAnalysisMode.OFF,
        diarization_mode=AudioAnalysisMode.OFF,
        language_identification_mode=AudioAnalysisMode.OFF,
        block_splitter=SpeechBlockSplitter(),
        block_vad_cache=cache,
        block_vad_detector=detector,
    )
    cache_path = cache.get_path(audio_series.audio, cache_identity)
    cache_path.touch()

    blocks = pipeline.plan_blocks(audio_series)
    repeated_blocks = pipeline.plan_blocks(audio_series)

    assert blocks
    assert repeated_blocks == blocks
    assert cache_path.stat().st_size > 0
    detector.get_trace.assert_called_once_with(audio_series.audio)
