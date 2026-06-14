#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of YueTranscriber internals."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import cast
from unittest.mock import Mock, patch

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.transcription import (
    DemucsSeparator,
    TranscribedSegment,
    TranscribedWord,
    WhisperTranscriber,
)
from scinoephile.core.subtitles import Series
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.multilang.yue_zho.transcription.aligner import Aligner
from scinoephile.multilang.yue_zho.transcription.deliniation import (
    YueDeliniationVsZhoPromptYueHans,
)
from scinoephile.multilang.yue_zho.transcription.punctuation import (
    YuePunctuationVsZhoPromptYueHans,
)
from scinoephile.multilang.yue_zho.transcription.transcriber import (
    DemucsMode,
    VADMode,
    YueTranscriber,
)


def test_transcribe_block_audio_applies_demucs_before_vad_retry(tmp_path):
    """Test block transcription applies Demucs before VAD retry."""
    transcriber = _get_yue_transcriber(tmp_path, demucs_mode=DemucsMode.ON)
    separated_audio = Mock(raw_data=b"separated-audio")
    demucs_separator = _RecordingSeparator(separated_audio)
    vad_transcriber = _RecordingTranscriber(
        output_segments=[_get_transcribed_segment("   ", include_words=False)]
    )
    no_vad_transcriber = _RecordingTranscriber(
        output_segments=[_get_transcribed_segment("你好")]
    )
    transcriber.demucs_separator = cast(DemucsSeparator, demucs_separator)
    transcriber.vad_transcriber = cast(WhisperTranscriber, vad_transcriber)
    transcriber.no_vad_transcriber = cast(WhisperTranscriber, no_vad_transcriber)

    input_audio = Mock(raw_data=b"raw-audio")

    output = transcriber._transcribe_block_audio(input_audio)

    assert output == [_get_transcribed_segment("你好")]
    assert demucs_separator.input_audio == [input_audio]
    assert vad_transcriber.input_audio == [separated_audio]
    assert no_vad_transcriber.input_audio == [separated_audio]


def test_transcribe_block_audio_uses_vad_cache_before_demucs(tmp_path):
    """Test VAD cache hit short-circuits before Demucs preprocessing."""
    transcriber = _get_yue_transcriber(
        tmp_path,
        demucs_mode=DemucsMode.ON,
        vad_mode=VADMode.ON,
    )
    demucs_separator = _RecordingSeparator(Mock(raw_data=b"separated-audio"))
    transcriber.demucs_separator = cast(DemucsSeparator, demucs_separator)
    transcriber.no_vad_transcriber = None

    input_audio = Mock(raw_data=b"raw-audio")
    cached_segments = [_get_transcribed_segment("cached")]
    vad_transcriber = _RecordingTranscriber(cached_segments=cached_segments)
    transcriber.vad_transcriber = cast(WhisperTranscriber, vad_transcriber)

    output = transcriber._transcribe_block_audio(input_audio)

    assert output == cached_segments
    assert demucs_separator.input_audio == []
    assert vad_transcriber.input_audio == []


def test_transcribe_block_audio_auto_uses_no_vad_cache_when_vad_cache_misses(tmp_path):
    """Test AUTO mode uses usable no-VAD cache after a VAD-cache miss."""
    transcriber = _get_yue_transcriber(tmp_path)
    cached_segments = [_get_transcribed_segment("cached-no-vad")]
    vad_transcriber = _RecordingTranscriber()
    no_vad_transcriber = _RecordingTranscriber(cached_segments=cached_segments)
    transcriber.vad_transcriber = cast(WhisperTranscriber, vad_transcriber)
    transcriber.no_vad_transcriber = cast(WhisperTranscriber, no_vad_transcriber)

    input_audio = Mock(raw_data=b"raw-audio")

    output = transcriber._transcribe_block_audio(input_audio)

    assert output == cached_segments
    assert vad_transcriber.input_audio == []
    assert no_vad_transcriber.input_audio == []


def test_get_whisper_transcriber_sets_use_demucs(tmp_path):
    """Test Whisper transcriber cache keys distinguish Demucs mode."""
    transcriber = _get_yue_transcriber(tmp_path, demucs_mode=DemucsMode.ON)

    whisper_transcriber = transcriber._get_whisper_transcriber(use_vad=True)

    assert whisper_transcriber.use_demucs is True


def test_process_block_leaves_text_unchanged_without_conversion(tmp_path):
    """Test process_block skips OpenCC conversion by default."""
    transcriber = _get_yue_transcriber(tmp_path)
    aligner = _RecordingAligner()
    transcriber.aligner = cast(Aligner, aligner)
    expected_series = Mock(spec=AudioSeries)
    aligner.output_series = expected_series
    segments = [TranscribedSegment(id=0, seek=0, start=0.0, end=1.0, text="學校")]
    yuewen_block = Mock(spec=AudioSeries)
    yuewen_block.audio = Mock()
    yuewen_block.__getitem__ = Mock(return_value=SimpleNamespace(start=1.25))
    zhongwen_block = Mock(spec=Series)
    interim_series = Mock()

    with patch.object(
        YueTranscriber,
        "_transcribe_block_audio",
        return_value=segments,
    ):
        with patch(
            "scinoephile.multilang.yue_zho.transcription.transcriber.get_series_from_segments",
            return_value=interim_series,
        ):
            with patch(
                "scinoephile.multilang.yue_zho.transcription.transcriber.get_segment_zho_converted",
                side_effect=AssertionError("conversion should not run"),
            ):
                output_series = transcriber.process_block(yuewen_block, zhongwen_block)

    assert output_series is expected_series
    assert aligner.inputs == [(zhongwen_block, interim_series)]
    assert aligner.update_count == 1


def test_process_block_converts_text_when_requested(tmp_path):
    """Test process_block applies OpenCC conversion when configured."""
    transcriber = _get_yue_transcriber(tmp_path, convert=OpenCCConfig.hk2s)
    aligner = _RecordingAligner()
    transcriber.aligner = cast(Aligner, aligner)
    expected_series = Mock(spec=AudioSeries)
    aligner.output_series = expected_series
    segments = [TranscribedSegment(id=0, seek=0, start=0.0, end=1.0, text="學校")]
    converted_segments = [Mock()]
    converted_inputs: list[tuple[TranscribedSegment, OpenCCConfig]] = []
    series_inputs: list[tuple[list[object], object, float]] = []
    yuewen_block = Mock(spec=AudioSeries)
    yuewen_block.audio = Mock()
    yuewen_block.__getitem__ = Mock(return_value=SimpleNamespace(start=0.5))
    zhongwen_block = Mock(spec=Series)

    def convert_segment(segment: TranscribedSegment, config: OpenCCConfig) -> object:
        """Record conversion inputs."""
        converted_inputs.append((segment, config))
        return converted_segments[0]

    def get_series_from_converted_segments(
        segments: list[object],
        *,
        audio: object,
        offset: float,
    ) -> Mock:
        """Record series construction inputs."""
        series_inputs.append((segments, audio, offset))
        return Mock()

    with patch.object(
        YueTranscriber,
        "_transcribe_block_audio",
        return_value=segments,
    ):
        with patch(
            "scinoephile.multilang.yue_zho.transcription.transcriber.get_series_from_segments",
            side_effect=get_series_from_converted_segments,
        ):
            with patch(
                "scinoephile.multilang.yue_zho.transcription.transcriber.get_segment_zho_converted",
                side_effect=convert_segment,
            ):
                output_series = transcriber.process_block(yuewen_block, zhongwen_block)

    assert output_series is expected_series
    assert converted_inputs == [(segments[0], OpenCCConfig.hk2s)]
    assert series_inputs == [(converted_segments, yuewen_block.audio, 0.5)]


class _FakeQueryer:
    """Fake queryer for cheap YueTranscriber construction."""

    def __init__(self, **kwargs: object):
        """Initialize."""


class _RecordingAligner:
    """Recording aligner fake."""

    def __init__(self):
        """Initialize."""
        self.inputs: list[tuple[Series, AudioSeries]] = []
        self.output_series = Mock(spec=AudioSeries)
        self.update_count = 0

    def align(self, zhongwen: Series, yuewen: AudioSeries) -> SimpleNamespace:
        """Record alignment inputs."""
        self.inputs.append((zhongwen, yuewen))
        return SimpleNamespace(yuewen=self.output_series)

    def update_all_test_cases(self):
        """Record test case updates."""
        self.update_count += 1


class _RecordingSeparator:
    """Recording Demucs separator fake."""

    def __init__(self, output_audio: object | None = None):
        """Initialize.

        Arguments:
            output_audio: separated audio to return
        """
        self.input_audio: list[object] = []
        self.output_audio = output_audio or Mock(raw_data=b"separated-audio")

    def __call__(self, audio: object) -> object:
        """Record input audio."""
        self.input_audio.append(audio)
        return self.output_audio


class _RecordingTranscriber:
    """Recording Whisper transcriber fake."""

    def __init__(
        self,
        *,
        cached_segments: list[TranscribedSegment] | None = None,
        output_segments: list[TranscribedSegment] | None = None,
    ):
        """Initialize.

        Arguments:
            cached_segments: cached segments to return
            output_segments: transcribed segments to return
        """
        self.cached_segments = cached_segments
        self.output_segments = output_segments or []
        self.cache_audio: list[object] = []
        self.input_audio: list[object] = []

    def __call__(
        self, audio: object, *, cache_audio: object
    ) -> list[TranscribedSegment]:
        """Record transcription input."""
        self.input_audio.append(audio)
        self.cache_audio.append(cache_audio)
        return self.output_segments

    def get_cached_transcription(
        self, cache_audio: object
    ) -> list[TranscribedSegment] | None:
        """Record cache lookup input."""
        self.cache_audio.append(cache_audio)
        return self.cached_segments


def _get_yue_transcriber(
    tmp_path: Path,
    *,
    demucs_mode: DemucsMode = DemucsMode.OFF,
    vad_mode: VADMode = VADMode.AUTO,
    convert: OpenCCConfig | None = None,
) -> YueTranscriber:
    """Get a cheaply constructed YueTranscriber.

    Arguments:
        tmp_path: temporary test case directory path
        demucs_mode: Demucs preprocessing mode
        vad_mode: Whisper voice activity detection mode
        convert: OpenCC conversion config
    Returns:
        configured transcriber
    """
    with patch(
        "scinoephile.multilang.yue_zho.transcription.transcriber.Queryer.get_queryer_cls",
        return_value=_FakeQueryer,
    ):
        with patch(
            "scinoephile.multilang.yue_zho.transcription.transcriber.Aligner",
            return_value=_RecordingAligner(),
        ):
            with patch(
                "scinoephile.multilang.yue_zho.transcription.transcriber.DemucsSeparator",
                return_value=_RecordingSeparator(),
            ):
                return YueTranscriber(
                    model_name="custom/model",
                    demucs_mode=demucs_mode,
                    vad_mode=vad_mode,
                    provider=Mock(),
                    convert=convert,
                    additional_context=None,
                    deliniation_prompt_cls=YueDeliniationVsZhoPromptYueHans,
                    punctuation_prompt_cls=YuePunctuationVsZhoPromptYueHans,
                    test_case_directory_path=tmp_path,
                    deliniation_test_cases=[],
                    punctuation_test_cases=[],
                )


def _get_transcribed_segment(
    text: str, *, include_words: bool = True
) -> TranscribedSegment:
    """Get a transcribed segment for test assertions.

    Arguments:
        text: segment text
        include_words: whether to include word timings matching text
    Returns:
        transcribed segment
    """
    words = None
    if include_words:
        words = [
            TranscribedWord(text=text, start=0.0, end=1.0, confidence=1.0),
        ]
    return TranscribedSegment(
        id=0,
        seek=0,
        start=0.0,
        end=1.0,
        text=text,
        words=words,
    )
