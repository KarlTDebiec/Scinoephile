#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for complete reference-free transcription orchestration."""

from __future__ import annotations

from unittest.mock import Mock

import numpy as np
from pydub import AudioSegment

from scinoephile.analysis.alignment.timed_msa.aligner import Aligner
from scinoephile.analysis.alignment.timed_msa.alignment import Alignment
from scinoephile.analysis.alignment.timed_msa.models import Column, Token
from scinoephile.analysis.transcription.artifact import AlignmentSource
from scinoephile.audio.classification.models import AudioClassificationMode
from scinoephile.audio.diarization.models import DiarizationMode
from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.transcription import TranscribedSegment, TranscribedWord
from scinoephile.audio.vad import SpeechBlock, SpeechBlockSettings, VoiceActivityTrace
from scinoephile.core import Language
from scinoephile.lang.yue.transcription.token_similarity import YueTokenSimilarity
from scinoephile.workflows.transcription_pipeline import TranscriptionPipeline

_SOURCE_CACHE_KEY_SHA256S = {"one": "1" * 64, "two": "2" * 64}
"""Selected ASR cache keys used by the pipeline fixture."""
_QUERY_KEY_SHA256S = ("3" * 64,)
"""Semantic processor query keys used by the pipeline fixture."""


def test_process_builds_subtitles_alignment_and_run_manifest():
    """One selected block should produce mutually linked portable outputs."""
    audio = AudioSegment.silent(duration=1_000)
    audio_series = AudioSeries(audio)
    trace = VoiceActivityTrace(
        np.ones(10), start_ms=50.0, step_ms=100.0, duration_ms=1_000
    )
    block = SpeechBlock(
        index=0, start_ms=100, end_ms=900, buffered_start_ms=0, buffered_end_ms=1_000
    )
    block_splitter = Mock(return_value=[block])
    block_splitter.settings = SpeechBlockSettings()
    block_vad_detector = Mock()
    block_vad_detector.cache_identity = {"implementation": "test"}
    block_vad_detector.trace_cache_identity = {"implementation": "test"}
    block_vad_detector.get_speech_intervals.return_value = [(100, 900)]
    block_vad_cache = Mock()
    block_vad_cache.load.return_value = trace

    word = TranscribedWord(text="甲", start=0.2, end=0.4, confidence=1.0)
    segment = TranscribedSegment(
        id=0, seek=0, start=0.2, end=0.4, text="甲", words=[word]
    )
    transcriber = Mock()
    transcriber.transcribe_block.return_value = [segment]
    transcriber.aligner = Aligner(YueTokenSimilarity())
    transcriber.last_lexical_alignment = Alignment(
        source_names=("one", "two"),
        columns=(Column((Token("甲", 0.2, 0.4), Token("甲", 0.2, 0.4))),),
    )
    transcriber.last_source_errors = {}
    transcriber.last_source_cache_key_sha256s = _SOURCE_CACHE_KEY_SHA256S
    transcriber.last_query_key_sha256s = _QUERY_KEY_SHA256S
    transcriber.last_timing_sources = {0: "source"}
    transcriber.processor.prune_test_cases = False
    transcriber.processor.test_case_cls.operation = "transcription"
    transcriber.processor.prompt.name = "test"
    transcriber.processor.queryer.provider.cache_identity = {"implementation": "test"}
    transcriber.processor.queryer.system_prompt = "test prompt"
    transcriber.processor.queryer.no_op = True

    pipeline = TranscriptionPipeline(
        language=Language.yue_hant,
        transcriber=transcriber,
        alignment_sources=(
            AlignmentSource(name="one", backend="test", model="one"),
            AlignmentSource(name="two", backend="test", model="two"),
        ),
        audio_event_mode=AudioClassificationMode.OFF,
        diarization_mode=DiarizationMode.OFF,
        language_identification_mode=AudioClassificationMode.OFF,
        block_splitter=block_splitter,
        block_vad_cache=block_vad_cache,
        block_vad_detector=block_vad_detector,
    )

    output = pipeline.process(audio_series)

    assert [(event.start, event.end, event.text) for event in output.events] == [
        (0, 900, "甲")
    ]
    assert pipeline.last_alignment_artifact is not None
    assert pipeline.last_run_manifest is not None
    assert pipeline.last_run_manifest.alignment_sha256 == (
        pipeline.last_alignment_artifact.sha256
    )
    assert pipeline.last_run_manifest.blocks[0].source_cache_key_sha256s == (
        _SOURCE_CACHE_KEY_SHA256S
    )
    assert pipeline.last_run_manifest.blocks[0].query_key_sha256s == _QUERY_KEY_SHA256S
    assert pipeline.last_run_manifest.processor.no_op
