#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for guided transcription processing."""

from __future__ import annotations

from logging import INFO, WARNING
from typing import cast
from unittest.mock import ANY, Mock, patch

from pydub import AudioSegment
from pydub.generators import Sine
from pytest import LogCaptureFixture, approx, raises

from scinoephile.audio.subtitles import AudioSeries, AudioSubtitle, get_sub_split_at_idx
from scinoephile.audio.transcription import (
    DemucsMode,
    MlxAudioTranscriber,
    TranscribedSegment,
    TranscribedWord,
    TranscriptionError,
    VadMode,
)
from scinoephile.audio.transcription.mlx_audio.model import MIMO_MODEL
from scinoephile.audio.transcription.whisper.model import WhisperModel
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.transcription.aligner import TranscriptionAligner
from scinoephile.lang.transcription.alignment import TranscriptionAlignment
from scinoephile.lang.transcription.transcriber import (
    GuidedTranscriber,
    MlxAudioTimingMode,
    TranscriptionModel,
    get_segment_split_on_phrase_timings,
)


def _get_transcriber(
    *,
    model: TranscriptionModel = TranscriptionModel.WHISPER,
    demucs_mode: DemucsMode = DemucsMode.OFF,
    vad_mode: VadMode = VadMode.OFF,
    overwrite_cache: bool = False,
    mlx_audio_timing_mode: MlxAudioTimingMode = MlxAudioTimingMode.CTC_UNIT,
    strip_generated_punctuation: bool = False,
) -> tuple[GuidedTranscriber, Mock]:
    """Get a transcriber with a passthrough alignment mock.

    Arguments:
        model: supported transcription model
        demucs_mode: Demucs preprocessing mode
        vad_mode: voice activity detection mode
        overwrite_cache: whether to replace matching transcription cache files
        mlx_audio_timing_mode: granularity of MLX-Audio CTC timing units
        strip_generated_punctuation: whether to remove generated punctuation before
            guided alignment
    Returns:
        transcriber and alignment mock
    """
    aligner = Mock(spec=TranscriptionAligner)
    aligner.align.side_effect = TranscriptionAlignment
    aligner.delineation_processor = Mock()
    aligner.delineation_processor.prune_test_cases = False
    aligner.punctuation_processor = Mock()
    aligner.punctuation_processor.prune_test_cases = False
    mlx_audio_transcriber = None
    audio_model = WhisperModel("test/model", {Language.eng: "en"})
    if model is not TranscriptionModel.WHISPER:
        mlx_audio_transcriber = Mock(spec=MlxAudioTranscriber)
        audio_model = MIMO_MODEL
    return (
        GuidedTranscriber(
            language=Language.eng,
            guide_language=Language.zho_hans,
            audio_model=audio_model,
            aligner=aligner,
            demucs_mode=demucs_mode,
            vad_mode=vad_mode,
            overwrite_cache=overwrite_cache,
            mlx_audio_transcriber=mlx_audio_transcriber,
            mlx_audio_timing_mode=mlx_audio_timing_mode,
            strip_generated_punctuation=strip_generated_punctuation,
        ),
        aligner,
    )


def _get_segment(
    *,
    segment_id: int = 0,
    start: float = 0.1,
    end: float = 0.2,
    text: str = "hello",
    compression_ratio: float | None = None,
    with_words: bool = False,
) -> TranscribedSegment:
    """Get a minimal transcribed segment.

    Arguments:
        segment_id: segment identifier
        start: segment start in seconds
        end: segment end in seconds
        text: segment text
        compression_ratio: gzip compression ratio reported by Whisper
        with_words: whether to include word-level timings
    Returns:
        transcribed segment
    """
    words = None
    if with_words:
        words = [TranscribedWord(text=text, start=start, end=end, confidence=1.0)]
    return TranscribedSegment(
        id=segment_id,
        seek=0,
        start=start,
        end=end,
        text=text,
        compression_ratio=compression_ratio,
        words=words,
    )


def test_segments_are_usable_rejects_repetitive_whisper_output():
    """Test highly compressible Whisper loops are unusable for alignment."""
    segments = [_get_segment(compression_ratio=16.24, with_words=True)]

    assert not GuidedTranscriber._segments_are_usable(segments)


def test_segments_are_usable_reports_missing_word_timings_concisely(
    caplog: LogCaptureFixture,
):
    """Test missing word timings emit concise segment rejection logs.

    Arguments:
        caplog: captured log records
    """
    caplog.set_level(WARNING, logger="scinoephile.lang.transcription.transcriber")

    assert not GuidedTranscriber._segments_are_usable([_get_segment(segment_id=7)])
    assert caplog.messages == [
        "Rejecting transcription: Segment 7 has no word timings."
    ]


def test_segments_are_usable_rejects_nonpositive_word_duration():
    """Test text-bearing words must remain positive after ms conversion."""
    segment = _get_segment(start=4.02, end=4.04, text=" 啊", compression_ratio=1.0)
    segment.words = [
        TranscribedWord(text=" ", start=4.02, end=4.04, confidence=1.0),
        TranscribedWord(text="啊", start=4.04, end=4.04, confidence=1.0),
    ]

    assert not GuidedTranscriber._segments_are_usable([segment])


def test_segments_are_usable_rejects_timestamp_beyond_audio():
    """Test Whisper timestamps extending beyond source audio are unusable."""
    segments = [_get_segment(end=12.0, compression_ratio=1.0, with_words=True)]

    assert not GuidedTranscriber._segments_are_usable(segments, audio_duration=10.0)


def test_segments_are_usable_accepts_partial_guided_tail():
    """Test guide coverage does not determine transcription validity."""
    segments = [_get_segment(end=4.0, compression_ratio=1.0, with_words=True)]

    assert GuidedTranscriber._segments_are_usable(segments, audio_duration=10.0)


def test_missing_guided_tail_runs_focused_recovery():
    """Test a missing guided tail triggers normalized focused recovery."""
    transcriber, _ = _get_transcriber(vad_mode=VadMode.OFF)
    initial_segments = [_get_segment(end=4.0, compression_ratio=1.0, with_words=True)]
    recovered_segments = [
        _get_segment(
            start=0.2, end=0.8, text="tail", compression_ratio=1.0, with_words=True
        )
    ]
    recovered_segments[0].no_speech_prob = 0.1
    transcriber.transcriber = Mock(return_value=initial_segments)
    transcriber.transcriber.get_cached_transcription.return_value = initial_segments
    transcriber.recovery_transcriber = Mock()
    transcriber.tail_recovery_transcriber = Mock(return_value=recovered_segments)
    audio = Sine(440).to_audio_segment(duration=10000).apply_gain(-20.0)

    output = transcriber._transcribe_block_audio(audio, expected_last_start=8.0)

    assert output[:1] == initial_segments
    assert output[1].text == "tail"
    assert output[1].start == 5.2
    assert output[1].end == 5.8
    normalized_tail_audio = transcriber.tail_recovery_transcriber.call_args.args[0]
    transcriber.tail_recovery_transcriber.assert_called_once_with(
        normalized_tail_audio, is_usable=ANY
    )
    assert transcriber.tail_recovery_transcriber.call_args.kwargs["is_usable"](
        recovered_segments
    )
    assert len(normalized_tail_audio) == 5000
    assert normalized_tail_audio.max_dBFS == approx(-1.0, abs=0.01)


def test_missing_guided_tail_keeps_base_after_unusable_recovery():
    """Test unusable focused-tail output leaves the base transcription intact."""
    transcriber, _ = _get_transcriber(vad_mode=VadMode.OFF)
    initial_segments = [_get_segment(end=4.0, compression_ratio=1.0, with_words=True)]
    repetitive_segments = [_get_segment(compression_ratio=16.24, with_words=True)]
    transcriber.transcriber = Mock()
    transcriber.transcriber.get_cached_transcription.return_value = initial_segments
    transcriber.tail_recovery_transcriber = Mock(return_value=[])
    audio = Sine(440).to_audio_segment(duration=10000).apply_gain(-20.0)

    output = transcriber._transcribe_block_audio(audio, expected_last_start=8.0)

    assert output == initial_segments
    normalized_tail_audio = transcriber.tail_recovery_transcriber.call_args.args[0]
    assert len(normalized_tail_audio) == 5000
    assert normalized_tail_audio.max_dBFS == approx(-1.0, abs=0.01)
    transcriber.tail_recovery_transcriber.assert_called_once_with(
        normalized_tail_audio, is_usable=ANY
    )
    assert not transcriber.tail_recovery_transcriber.call_args.kwargs["is_usable"](
        repetitive_segments
    )


def test_missing_guided_tail_keeps_valid_base_without_credible_recovery():
    """Test implausible tail recovery does not invalidate a valid base transcript."""
    transcriber, _ = _get_transcriber(vad_mode=VadMode.OFF)
    initial_segments = [_get_segment(end=4.0, compression_ratio=1.0, with_words=True)]
    stretched_segment = _get_segment(
        end=5.0, text="x", compression_ratio=1.0, with_words=True
    )
    stretched_segment.no_speech_prob = 0.1
    no_speech_segment = _get_segment(
        segment_id=1,
        start=5.1,
        end=5.2,
        text="tail",
        compression_ratio=1.0,
        with_words=True,
    )
    no_speech_segment.no_speech_prob = 0.9
    transcriber.transcriber = Mock()
    transcriber.transcriber.get_cached_transcription.return_value = initial_segments
    transcriber.tail_recovery_transcriber = Mock(
        return_value=[stretched_segment, no_speech_segment]
    )
    audio = Sine(440).to_audio_segment(duration=10000).apply_gain(-20.0)

    output = transcriber._transcribe_block_audio(audio, expected_last_start=8.0)

    assert output == initial_segments


def test_usable_standard_cache_skips_inference():
    """Test a usable standard cache returns without running either transcriber."""
    transcriber, _ = _get_transcriber()
    segments = [_get_segment(compression_ratio=1.0, with_words=True)]
    transcriber.transcriber = Mock()
    transcriber.transcriber.get_cached_transcription.return_value = segments
    transcriber.recovery_transcriber = Mock()

    output = transcriber._transcribe_block_audio(AudioSegment.silent(duration=1000))

    assert output == segments
    transcriber.transcriber.assert_not_called()
    transcriber.recovery_transcriber.get_cached_transcription.assert_not_called()
    transcriber.recovery_transcriber.assert_not_called()


def test_usable_recovery_cache_skips_inference():
    """Test defensive cache preflight completes before standard inference."""
    transcriber, _ = _get_transcriber()
    segments = [_get_segment(compression_ratio=1.0, with_words=True)]
    transcriber.transcriber = Mock()
    transcriber.transcriber.get_cached_transcription.return_value = None
    transcriber.recovery_transcriber = Mock()
    transcriber.recovery_transcriber.get_cached_transcription.return_value = segments

    output = transcriber._transcribe_block_audio(AudioSegment.silent(duration=1000))

    assert output == segments
    transcriber.transcriber.assert_not_called()
    transcriber.recovery_transcriber.assert_not_called()


def test_standard_transcriber_runs_shared_fallbacks():
    """Test guided transcription delegates standard retries to one transcriber."""
    transcriber, _ = _get_transcriber()
    audio = AudioSegment.silent(duration=1000)
    segments = [_get_segment(compression_ratio=1.0, with_words=True)]
    transcriber.transcriber = Mock(return_value=segments)
    transcriber.transcriber.get_cached_transcription.return_value = None
    transcriber.recovery_transcriber = Mock()
    transcriber.recovery_transcriber.get_cached_transcription.return_value = None

    output = transcriber._transcribe_block_audio(audio)

    assert output == segments
    transcriber.transcriber.assert_called_once_with(audio, is_usable=ANY)
    transcriber.recovery_transcriber.assert_not_called()


def test_unusable_standard_output_uses_defensive_recovery():
    """Test exhausted standard retries lead to defensive decoding."""
    transcriber, _ = _get_transcriber()
    audio = AudioSegment.silent(duration=1000)
    segments = [_get_segment(compression_ratio=1.0, with_words=True)]
    transcriber.transcriber = Mock(return_value=[])
    transcriber.transcriber.get_cached_transcription.return_value = None
    transcriber.recovery_transcriber = Mock(return_value=segments)
    transcriber.recovery_transcriber.get_cached_transcription.return_value = None

    output = transcriber._transcribe_block_audio(audio)

    assert output == segments
    transcriber.recovery_transcriber.assert_called_once_with(audio, is_usable=ANY)


def test_standard_error_uses_defensive_recovery():
    """Test standard backend errors do not prevent defensive decoding."""
    transcriber, _ = _get_transcriber()
    audio = AudioSegment.silent(duration=1000)
    segments = [_get_segment(compression_ratio=1.0, with_words=True)]
    transcriber.transcriber = Mock(side_effect=TranscriptionError("failed"))
    transcriber.transcriber.get_cached_transcription.return_value = None
    transcriber.recovery_transcriber = Mock(return_value=segments)
    transcriber.recovery_transcriber.get_cached_transcription.return_value = None

    assert transcriber._transcribe_block_audio(audio) == segments


def test_all_unusable_candidates_leave_gap_for_translation():
    """Test exhausted standard and defensive retries leave an empty block."""
    transcriber, _ = _get_transcriber()
    transcriber.transcriber = Mock(return_value=[])
    transcriber.transcriber.get_cached_transcription.return_value = None
    transcriber.recovery_transcriber = Mock(return_value=[])
    transcriber.recovery_transcriber.get_cached_transcription.return_value = None

    output = transcriber._transcribe_block_audio(AudioSegment.silent(duration=1000))

    assert output == []


def test_mlx_audio_backend_delegates_to_shared_transcriber():
    """Test guided transcription delegates retries to one MLX-Audio instance."""
    transcriber, _ = _get_transcriber(
        model=TranscriptionModel.MIMO,
        demucs_mode=DemucsMode.AUTO,
        vad_mode=VadMode.AUTO,
    )
    repetitive_segments = [_get_segment(compression_ratio=16.24, with_words=True)]
    usable_segments = [_get_segment(text="mlx-audio", with_words=True)]
    assert transcriber.mlx_audio_transcriber is not None
    mlx_audio = cast(Mock, transcriber.mlx_audio_transcriber)
    mlx_audio.return_value = usable_segments
    audio = AudioSegment.silent(duration=1000)

    output = transcriber._transcribe_block_audio(audio)

    assert output == usable_segments
    assert mlx_audio.call_count == 1
    assert mlx_audio.call_args.args == (audio,)
    is_usable = mlx_audio.call_args.kwargs["is_usable"]
    assert not is_usable(repetitive_segments)
    assert is_usable(usable_segments)
    assert transcriber.recovery_transcriber is None
    assert transcriber.tail_recovery_transcriber is None


def test_failed_mlx_audio_backend_leaves_gap_for_translation():
    """Test an MLX-Audio failure preserves downstream gap translation behavior."""
    transcriber, _ = _get_transcriber(
        model=TranscriptionModel.MIMO, overwrite_cache=True
    )
    assert transcriber.mlx_audio_transcriber is not None
    mlx_audio = cast(Mock, transcriber.mlx_audio_transcriber)
    mlx_audio.side_effect = TranscriptionError("MLX-Audio failed")
    audio = AudioSegment.silent(duration=1000)

    assert transcriber._transcribe_block_audio(audio) == []
    assert mlx_audio.call_count == 1
    assert mlx_audio.call_args.args == (audio,)
    assert set(mlx_audio.call_args.kwargs) == {"is_usable"}


def test_overwrite_cache_is_owned_by_transcriber_caches():
    """Test guided cache overwrite is owned by each configured cache."""
    transcriber, _ = _get_transcriber(overwrite_cache=True)
    assert transcriber.recovery_transcriber is not None
    assert transcriber.tail_recovery_transcriber is not None
    assert transcriber.transcriber._cache.overwrite
    assert transcriber.recovery_transcriber._cache.overwrite
    assert transcriber.tail_recovery_transcriber._cache.overwrite
    audio = AudioSegment.silent(duration=1000)
    segments = [_get_segment(compression_ratio=1.0, with_words=True)]
    transcriber.transcriber = Mock(return_value=segments)
    transcriber.transcriber.get_cached_transcription.return_value = None
    transcriber.recovery_transcriber = Mock()
    transcriber.recovery_transcriber.get_cached_transcription.return_value = None

    assert transcriber._transcribe_block_audio(audio) == segments
    transcriber.transcriber.get_cached_transcription.assert_called_once_with(
        audio, is_usable=ANY
    )
    transcriber.recovery_transcriber.get_cached_transcription.assert_called_once_with(
        audio, is_usable=ANY
    )
    transcriber.transcriber.assert_called_once_with(audio, is_usable=ANY)


def test_process_block_preserves_raw_segments_and_uses_buffered_offset():
    """Test generic processing preserves segments and anchors buffered audio."""
    transcriber, aligner = _get_transcriber()
    audio_block = AudioSeries(
        audio=AudioSegment.silent(duration=1000),
        events=[AudioSubtitle(start=1000, end=1500, text="reference")],
    )
    audio_block.buffered_start = 250
    reference_block = Series(events=[Subtitle(start=1000, end=1500, text="reference")])
    segment = _get_segment()

    with patch.object(
        transcriber, "_transcribe_block_audio", return_value=[segment]
    ) as transcribe_block_audio:
        output = transcriber.process_block(audio_block, reference_block)

    assert len(output) == 1
    assert output[0].text == "hello"
    assert output[0].start == 350
    assert output[0].end == 450
    transcribe_block_audio.assert_called_once_with(
        audio_block.audio, expected_last_start=0.75
    )
    aligner.update_all_test_cases.assert_not_called()


def test_process_block_applies_configured_segment_splitter():
    """Test language specs may split raw Whisper segments."""
    transcriber, aligner = _get_transcriber()
    transcriber.segment_splitter = Mock(
        return_value=[
            _get_segment(segment_id=0, end=0.15, text="one"),
            _get_segment(segment_id=1, start=0.15, text="two"),
        ]
    )
    audio_block = AudioSeries(
        audio=AudioSegment.silent(duration=1000),
        events=[AudioSubtitle(start=0, end=1000, text="reference")],
    )
    audio_block.buffered_start = 0
    reference_block = Series(events=[Subtitle(start=0, end=1000, text="reference")])
    segment = _get_segment()

    with patch.object(transcriber, "_transcribe_block_audio", return_value=[segment]):
        transcriber.process_block(audio_block, reference_block)

    transcriber.segment_splitter.assert_called_once_with(segment)
    transcription = aligner.align.call_args.args[1]
    assert [subtitle.text for subtitle in transcription] == ["one", "two"]


def test_process_block_strips_generated_punctuation_after_timing():
    """Test guided alignment can omit sentence but retain lexical punctuation."""
    transcriber, aligner = _get_transcriber(strip_generated_punctuation=True)
    audio_block = AudioSeries(
        audio=AudioSegment.silent(duration=1000),
        events=[AudioSubtitle(start=0, end=1000, text="reference")],
    )
    audio_block.buffered_start = 0
    reference_block = Series(events=[Subtitle(start=0, end=1000, text="reference")])
    segment = _get_segment(text="你好！0.01、don't、re-entry，", with_words=True)

    with patch.object(transcriber, "_transcribe_block_audio", return_value=[segment]):
        transcriber.process_block(audio_block, reference_block)

    transcription = aligner.align.call_args.args[1]
    assert [subtitle.text for subtitle in transcription] == ["你好0.01don'tre-entry"]
    assert transcription[0].segment.text == transcription[0].text
    assert [word.text for word in transcription[0].segment.words or []] == [
        "你好0.01don'tre-entry"
    ]


def test_process_block_synchronizes_stripped_punctuation_with_word_timings():
    """Test stripped text indexes continue to target matching timed characters."""
    transcriber, aligner = _get_transcriber(
        model=TranscriptionModel.MIMO,
        mlx_audio_timing_mode=MlxAudioTimingMode.SEGMENT,
        strip_generated_punctuation=True,
    )
    audio_block = AudioSeries(
        audio=AudioSegment.silent(duration=1000),
        events=[AudioSubtitle(start=0, end=1000, text="reference")],
    )
    audio_block.buffered_start = 0
    reference_block = Series(events=[Subtitle(start=0, end=1000, text="reference")])
    text = "甲，乙丙"
    segment = TranscribedSegment(
        id=0,
        seek=0,
        start=0.1,
        end=0.5,
        text=text,
        words=[
            TranscribedWord(
                text=character,
                start=(word_idx + 1) / 10,
                end=(word_idx + 2) / 10,
                confidence=1.0,
            )
            for word_idx, character in enumerate(text)
        ],
    )

    with patch.object(transcriber, "_transcribe_block_audio", return_value=[segment]):
        transcriber.process_block(audio_block, reference_block)

    subtitle = aligner.align.call_args.args[1][0]
    assert subtitle.text == "甲乙丙"
    assert subtitle.segment.text == subtitle.text
    assert "".join(word.text for word in subtitle.segment.words or []) == subtitle.text

    first, second = get_sub_split_at_idx(subtitle, 2)
    assert first.text == first.segment.text == "甲乙"
    assert "".join(word.text for word in first.segment.words or []) == "甲乙"
    assert first.end == 400
    assert second.text == second.segment.text == "丙"
    assert "".join(word.text for word in second.segment.words or []) == "丙"
    assert second.start == 400


def test_process_block_splits_mlx_audio_segments_on_ctc_unit_timings():
    """Test MLX-Audio CTC timing units reach reference-guided alignment."""
    transcriber, aligner = _get_transcriber(model=TranscriptionModel.MIMO)
    audio_block = AudioSeries(
        audio=AudioSegment.silent(duration=1000),
        events=[AudioSubtitle(start=0, end=1000, text="reference")],
    )
    audio_block.buffered_start = 0
    reference_block = Series(
        events=[
            Subtitle(start=0, end=500, text="參考一"),
            Subtitle(start=500, end=1000, text="參考二"),
        ]
    )
    segment = TranscribedSegment(
        id=0,
        seek=0,
        start=0.1,
        end=0.8,
        text="甲乙",
        words=[
            TranscribedWord(text="甲", start=0.1, end=0.2, confidence=1.0),
            TranscribedWord(text="乙", start=0.7, end=0.8, confidence=1.0),
        ],
    )

    with patch.object(transcriber, "_transcribe_block_audio", return_value=[segment]):
        transcriber.process_block(audio_block, reference_block)

    transcription = aligner.align.call_args.args[1]
    assert [subtitle.text for subtitle in transcription] == ["甲", "乙"]
    assert [(subtitle.start, subtitle.end) for subtitle in transcription] == [
        (100, 200),
        (700, 800),
    ]
    assert [subtitle.segment.id for subtitle in transcription] == [0, 1]
    alignment = TranscriptionAlignment(reference_block, transcription)
    assert alignment.sync_groups == [([0], [0]), ([1], [1])]


def test_process_block_retains_complete_mlx_audio_segments():
    """Test segment timing mode retains MLX-Audio segment granularity."""
    transcriber, aligner = _get_transcriber(
        model=TranscriptionModel.MIMO, mlx_audio_timing_mode=MlxAudioTimingMode.SEGMENT
    )
    audio_block = AudioSeries(
        audio=AudioSegment.silent(duration=1000),
        events=[AudioSubtitle(start=0, end=1000, text="reference")],
    )
    audio_block.buffered_start = 0
    reference_block = Series(events=[Subtitle(start=0, end=1000, text="參考")])
    segment = TranscribedSegment(
        id=4,
        seek=0,
        start=0.1,
        end=0.8,
        text="甲乙",
        words=[
            TranscribedWord(text="甲", start=0.1, end=0.2, confidence=1.0),
            TranscribedWord(text="乙", start=0.7, end=0.8, confidence=1.0),
        ],
    )

    with patch.object(transcriber, "_transcribe_block_audio", return_value=[segment]):
        transcriber.process_block(audio_block, reference_block)

    transcription = aligner.align.call_args.args[1]
    assert [subtitle.text for subtitle in transcription] == ["甲乙"]
    assert [(subtitle.start, subtitle.end) for subtitle in transcription] == [
        (100, 800)
    ]
    assert transcription[0].segment.id == 0


def test_process_block_groups_mlx_audio_segments_on_phrase_timings():
    """Test phrase timing groups use punctuation before it may be stripped."""
    transcriber, aligner = _get_transcriber(
        model=TranscriptionModel.MIMO,
        mlx_audio_timing_mode=MlxAudioTimingMode.PHRASE,
        strip_generated_punctuation=True,
    )
    audio_block = AudioSeries(
        audio=AudioSegment.silent(duration=1500),
        events=[AudioSubtitle(start=0, end=1500, text="reference")],
    )
    audio_block.buffered_start = 0
    reference_block = Series(
        events=[
            Subtitle(start=0, end=500, text="參考一"),
            Subtitle(start=500, end=1500, text="參考二"),
        ]
    )
    text = "甲乙。丙丁戊己庚辛壬癸"
    words = [
        TranscribedWord(
            text=character, start=word_idx / 10, end=(word_idx + 1) / 10, confidence=1.0
        )
        for word_idx, character in enumerate(text)
    ]
    segment = TranscribedSegment(
        id=0, seek=0, start=0.0, end=len(text) / 10, text=text, words=words
    )

    with patch.object(transcriber, "_transcribe_block_audio", return_value=[segment]):
        transcriber.process_block(audio_block, reference_block)

    transcription = aligner.align.call_args.args[1]
    assert [subtitle.text for subtitle in transcription] == ["甲乙", "丙丁戊己庚辛壬癸"]
    assert [(subtitle.start, subtitle.end) for subtitle in transcription] == [
        (0, 300),
        (300, 1100),
    ]


def test_phrase_timing_groups_split_on_ctc_hold_time_and_size():
    """Test acoustic holds and maximum size both produce phrase boundaries."""
    text = "甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未"
    words = []
    start = 0.0
    for word_idx, character in enumerate(text):
        duration = 0.1
        if word_idx == 2:
            duration = 0.7
        words.append(
            TranscribedWord(
                text=character, start=start, end=start + duration, confidence=1.0
            )
        )
        start += duration
    segment = TranscribedSegment(
        id=0, seek=0, start=0.0, end=start, text=text, words=words
    )

    output = get_segment_split_on_phrase_timings(segment)

    assert [item.text for item in output] == [
        "甲乙丙",
        "丁戊己庚辛壬癸",
        "子丑寅卯辰巳午未",
    ]
    assert [item.start for item in output] == approx([0.0, 0.9, 1.6])
    assert [item.end for item in output] == approx([0.9, 1.6, 2.4])


def test_process_uses_exclusive_stop_index(caplog: LogCaptureFixture):
    """Test stop_at_idx excludes that block while logs use one-based numbers.

    Arguments:
        caplog: captured log records
    """
    transcriber, aligner = _get_transcriber()
    caplog.set_level(INFO, logger="scinoephile.lang.transcription.transcriber")
    audio_series = AudioSeries(
        audio=AudioSegment.silent(duration=6000),
        events=[
            AudioSubtitle(start=0, end=1000, text="one"),
            AudioSubtitle(start=5000, end=6000, text="two"),
        ],
    )
    reference_series = Series(
        events=[
            Subtitle(start=0, end=1000, text="one"),
            Subtitle(start=5000, end=6000, text="two"),
        ]
    )

    with patch.object(
        transcriber,
        "process_block",
        side_effect=lambda audio_block, reference_block: audio_block,
    ) as process_block:
        output = transcriber.process(audio_series, reference_series, stop_at_idx=1)

    assert process_block.call_count == 1
    assert len(output) == 1
    assert output[0].text == "one"
    assert "BLOCK 1:" in caplog.text
    assert "BLOCK 0:" not in caplog.text
    aligner.update_all_test_cases.assert_called_once_with()


def test_process_uses_inclusive_start_index(caplog: LogCaptureFixture):
    """Test start_at_idx excludes earlier blocks while preserving global numbering.

    Arguments:
        caplog: captured log records
    """
    transcriber, _ = _get_transcriber()
    caplog.set_level(INFO, logger="scinoephile.lang.transcription.transcriber")
    audio_series = AudioSeries(
        audio=AudioSegment.silent(duration=6000),
        events=[
            AudioSubtitle(start=0, end=1000, text="one"),
            AudioSubtitle(start=5000, end=6000, text="two"),
        ],
    )
    reference_series = Series(
        events=[
            Subtitle(start=0, end=1000, text="one"),
            Subtitle(start=5000, end=6000, text="two"),
        ]
    )

    with patch.object(
        transcriber,
        "process_block",
        side_effect=lambda audio_block, reference_block: audio_block,
    ) as process_block:
        output = transcriber.process(audio_series, reference_series, start_at_idx=1)

    assert process_block.call_count == 1
    assert len(output) == 1
    assert output[0].text == "two"
    assert "BLOCK 2:" in caplog.text
    assert "BLOCK 1:" not in caplog.text


def test_process_rejects_mismatched_block_counts():
    """Test guided transcription requires corresponding block structures."""
    transcriber, _ = _get_transcriber()
    audio_series = AudioSeries(
        audio=AudioSegment.silent(duration=6000),
        events=[AudioSubtitle(start=0, end=1000, text="one")],
    )
    reference_series = Series(
        events=[
            Subtitle(start=0, end=1000, text="one"),
            Subtitle(start=5000, end=6000, text="two"),
        ]
    )

    with raises(ScinoephileError, match="Audio has 1 blocks"):
        transcriber.process(audio_series, reference_series)


def test_process_rejects_partial_range_when_pruning_test_cases():
    """Test pruning requires processing every block."""
    transcriber, aligner = _get_transcriber()
    aligner.delineation_processor.prune_test_cases = True
    audio_series = AudioSeries(
        audio=AudioSegment.silent(duration=6000),
        events=[
            AudioSubtitle(start=0, end=1000, text="one"),
            AudioSubtitle(start=5000, end=6000, text="two"),
        ],
    )
    reference_series = Series(
        events=[
            Subtitle(start=0, end=1000, text="one"),
            Subtitle(start=5000, end=6000, text="two"),
        ]
    )

    with raises(ValueError, match="Cannot prune test cases"):
        transcriber.process(audio_series, reference_series, stop_at_idx=1)

    aligner.update_all_test_cases.assert_not_called()


def test_process_does_not_save_test_cases_after_failure():
    """Test test cases are not persisted when processing fails."""
    transcriber, aligner = _get_transcriber()
    audio_series = AudioSeries(
        audio=AudioSegment.silent(duration=1000),
        events=[AudioSubtitle(start=0, end=1000, text="one")],
    )
    reference_series = Series(events=[Subtitle(start=0, end=1000, text="one")])

    with (
        patch.object(
            transcriber,
            "process_block",
            side_effect=ScinoephileError("transcription failed"),
        ),
        raises(ScinoephileError, match="transcription failed"),
    ):
        transcriber.process(audio_series, reference_series)

    aligner.update_all_test_cases.assert_not_called()


def test_process_rejects_negative_stop_index():
    """Test guided transcription rejects negative stop indexes."""
    transcriber, _ = _get_transcriber()
    audio_series = AudioSeries(
        audio=AudioSegment.silent(duration=1000),
        events=[AudioSubtitle(start=0, end=1000, text="one")],
    )
    reference_series = Series(events=[Subtitle(start=0, end=1000, text="one")])

    with raises(ValueError, match="greater than or equal to 0"):
        transcriber.process(audio_series, reference_series, stop_at_idx=-1)
