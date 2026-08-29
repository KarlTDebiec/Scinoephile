#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Whisper transcription normalization."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from pytest import LogCaptureFixture

from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.audio.transcription.transcribed_word import TranscribedWord
from scinoephile.audio.transcription.whisper.normalization import normalize_segments
from test.helpers import parametrize

_MODEL_NAME = "custom/model"
_SUBTITLE_CREDIT_TEXT = "字幕由 Amara.org 社群提供"
"""Representative terminal subtitle-credit hallucination."""


def _get_subtitle_credit_segments(
    no_speech_prob: float = 0.824,
) -> tuple[TranscribedSegment, TranscribedSegment]:
    """Get dialogue and subtitle-credit segments for normalization tests.

    Arguments:
        no_speech_prob: no-speech probability assigned to the credit segment
    Returns:
        dialogue and subtitle-credit segments
    """
    dialogue = TranscribedSegment(
        id=0,
        seek=0,
        start=0.0,
        end=1.0,
        text="對白",
        words=[TranscribedWord(text="對白", start=0.0, end=1.0, confidence=1.0)],
    )
    credit = TranscribedSegment(
        id=1,
        seek=0,
        start=1.0,
        end=1.5,
        text=_SUBTITLE_CREDIT_TEXT,
        no_speech_prob=no_speech_prob,
        words=[
            TranscribedWord(
                text=_SUBTITLE_CREDIT_TEXT, start=1.0, end=1.5, confidence=1.0
            )
        ],
    )
    return dialogue, credit


def _normalize_segments(
    segments: Sequence[TranscribedSegment],
    *,
    source: str,
    cache_path: Path | None,
    use_vad: bool,
    audio_duration_seconds: float | None = None,
) -> list[TranscribedSegment]:
    """Normalize segments using the test Whisper model context.

    Arguments:
        segments: raw transcription segments
        source: source of the segments, for logging
        cache_path: cache path associated with the segments, if any
        use_vad: whether Whisper VAD produced the segments
        audio_duration_seconds: complete source-audio duration, if known
    Returns:
        normalized transcription segments
    """
    return normalize_segments(
        segments,
        model_name=_MODEL_NAME,
        source=source,
        cache_path=cache_path,
        use_vad=use_vad,
        audio_duration_seconds=audio_duration_seconds,
    )


def test_normalize_transcription_segments_coalesces_malformed_duplicate_pair():
    """Test malformed empty-text and duplicate-text segments are coalesced."""
    segments = [
        TranscribedSegment(
            id=8,
            seek=11520,
            start=156.4,
            end=159.97,
            text="",
            tokens=[],
            temperature=0.0,
            avg_logprob=-1.45,
            compression_ratio=0.0,
            no_speech_prob=1.11e-6,
            words=[
                TranscribedWord(text="照", start=156.4, end=156.85, confidence=0.385),
                TranscribedWord(text="先生", start=156.85, end=157.19, confidence=0.99),
                TranscribedWord(
                    text="你就", start=157.19, end=158.31, confidence=0.686
                ),
            ],
        ),
        TranscribedSegment(
            id=9,
            seek=14520,
            start=156.4,
            end=161.29,
            text="照先生你就",
            tokens=[1, 2, 3],
            temperature=0.0,
            avg_logprob=-0.44,
            compression_ratio=0.76,
            no_speech_prob=1.53e-6,
            words=None,
        ),
    ]

    normalized_segments = _normalize_segments(
        segments, source="cache", cache_path=Path("/tmp/whisper.json"), use_vad=True
    )

    assert len(normalized_segments) == 1
    assert normalized_segments[0].id == 9
    assert normalized_segments[0].start == 156.4
    assert normalized_segments[0].end == 161.29
    assert normalized_segments[0].text == "照先生你就"
    assert normalized_segments[0].words is not None
    assert [word.text for word in normalized_segments[0].words] == [
        "照",
        "先生",
        "你就",
    ]


def test_normalize_transcription_segments_discards_terminal_credit_hallucination(
    caplog: LogCaptureFixture,
):
    """Test a terminal high-no-speech subtitle credit is discarded.

    Arguments:
        caplog: captured log records
    """
    dialogue, credit = _get_subtitle_credit_segments()

    normalized_segments = _normalize_segments(
        [dialogue, credit],
        source="cache",
        cache_path=Path("/tmp/whisper.json"),
        use_vad=False,
    )

    assert normalized_segments == [dialogue]
    assert "Discarding terminal Whisper subtitle-credit hallucination" in caplog.text


def test_normalize_transcription_segments_discards_coalesced_terminal_credit():
    """Test a repaired terminal subtitle-credit hallucination is discarded."""
    dialogue, credit = _get_subtitle_credit_segments()
    credit_with_words = credit.model_copy(update={"text": "", "no_speech_prob": 0.1})
    duplicate_credit = credit.model_copy(update={"id": 2, "words": None})

    normalized_segments = _normalize_segments(
        [dialogue, credit_with_words, duplicate_credit],
        source="whisper",
        cache_path=None,
        use_vad=False,
    )

    assert normalized_segments == [dialogue]


def test_normalize_transcription_segments_discards_split_terminal_credit():
    """Test a subtitle-credit hallucination split across segments is discarded."""
    dialogue, credit = _get_subtitle_credit_segments()
    credit_parts = []
    for part_idx, text in enumerate(("字幕由", "Amara.org", "社群提供"), start=1):
        start = float(part_idx)
        credit_parts.append(
            credit.model_copy(
                deep=True,
                update={
                    "id": part_idx,
                    "start": start,
                    "end": start + 0.5,
                    "text": text,
                    "words": [
                        TranscribedWord(
                            text=text, start=start, end=start + 0.5, confidence=1.0
                        )
                    ],
                },
            )
        )

    normalized_segments = _normalize_segments(
        [dialogue, *credit_parts], source="whisper", cache_path=None, use_vad=False
    )

    assert normalized_segments == [dialogue]


def test_normalize_transcription_segments_trims_credit_after_dialogue():
    """Test dialogue preceding a terminal subtitle credit is preserved."""
    text = "頂唔順啊！我個腿掛好痺啊！字幕由Amara.org社群提供"
    segment = TranscribedSegment(
        id=0,
        seek=0,
        start=0.0,
        end=2.5,
        text=text,
        tokens=[1, 2, 3],
        no_speech_prob=0.824,
        words=[
            TranscribedWord(text="頂唔順啊！", start=0.0, end=0.5, confidence=1.0),
            TranscribedWord(
                text="我個腿掛好痺啊！", start=0.5, end=1.0, confidence=1.0
            ),
            TranscribedWord(text="字幕由", start=1.0, end=1.5, confidence=1.0),
            TranscribedWord(text="Amara.org", start=1.5, end=2.0, confidence=1.0),
            TranscribedWord(text="社群提供", start=2.0, end=2.5, confidence=1.0),
        ],
    )

    normalized_segments = _normalize_segments(
        [segment], source="whisper", cache_path=None, use_vad=False
    )

    assert len(normalized_segments) == 1
    assert normalized_segments[0].text == "頂唔順啊！我個腿掛好痺啊！"
    assert normalized_segments[0].end == 1.0
    assert normalized_segments[0].tokens is None
    assert normalized_segments[0].words is not None
    assert [word.text for word in normalized_segments[0].words] == [
        "頂唔順啊！",
        "我個腿掛好痺啊！",
    ]


@parametrize(
    ("credit_idx", "no_speech_prob"),
    [(0, 0.824), (1, 0.1)],
    ids=("nonterminal", "plausible-speech"),
)
def test_normalize_transcription_segments_preserves_ambiguous_credit_segments(
    credit_idx: int, no_speech_prob: float
):
    """Test ambiguous subtitle-credit segments remain subject to validation.

    Arguments:
        credit_idx: index at which the credit-like segment appears
        no_speech_prob: no-speech probability assigned to the credit-like segment
    """
    dialogue, credit = _get_subtitle_credit_segments(no_speech_prob)
    segments = [dialogue, credit]
    if credit_idx == 0:
        segments.reverse()

    normalized_segments = _normalize_segments(
        segments, source="whisper", cache_path=None, use_vad=False
    )

    assert normalized_segments == segments


def test_normalize_transcription_segments_discards_invalid_terminal_credit():
    """Test a low-no-speech credit beyond the audio duration is discarded."""
    dialogue, credit = _get_subtitle_credit_segments(no_speech_prob=0.1)
    credit.end = 3.0

    normalized_segments = _normalize_segments(
        [dialogue, credit],
        source="cache",
        cache_path=Path("/tmp/whisper.json"),
        use_vad=False,
        audio_duration_seconds=1.5,
    )

    assert normalized_segments == [dialogue]


def test_normalize_transcription_segments_corrects_stale_window_compression():
    """Test retained window text replaces a stale decode compression score."""
    segments = [
        TranscribedSegment(
            id=0,
            seek=0,
            start=0.0,
            end=0.5,
            text="冇義氣呀",
            compression_ratio=4.8,
            words=[
                TranscribedWord(text="冇義氣呀", start=0.0, end=0.5, confidence=1.0)
            ],
        ),
        TranscribedSegment(
            id=1,
            seek=50,
            start=0.5,
            end=1.0,
            text="要命呀",
            compression_ratio=1.2,
            words=[TranscribedWord(text="要命呀", start=0.5, end=1.0, confidence=1.0)],
        ),
    ]

    normalized_segments = _normalize_segments(
        segments, source="cache", cache_path=None, use_vad=False
    )

    assert [segment.text for segment in normalized_segments] == ["冇義氣呀", "要命呀"]
    assert normalized_segments[0].compression_ratio is not None
    assert normalized_segments[0].compression_ratio < 2.4


def test_normalize_transcription_segments_discards_repetitive_window():
    """Test a genuinely repetitive window is discarded without losing others."""
    dialogue = TranscribedSegment(
        id=0,
        seek=0,
        start=0.0,
        end=0.5,
        text="問我班兄弟先",
        compression_ratio=2.8,
        words=[
            TranscribedWord(text="問我班兄弟先", start=0.0, end=0.5, confidence=1.0)
        ],
    )
    repetition = TranscribedSegment(
        id=1,
        seek=50,
        start=0.5,
        end=1.0,
        text="喇" * 100,
        compression_ratio=8.0,
        words=[TranscribedWord(text="喇" * 100, start=0.5, end=1.0, confidence=1.0)],
    )

    normalized_segments = _normalize_segments(
        [dialogue, repetition], source="cache", cache_path=None, use_vad=False
    )

    assert len(normalized_segments) == 1
    assert normalized_segments[0].text == dialogue.text
    assert normalized_segments[0].compression_ratio is not None
    assert normalized_segments[0].compression_ratio < 2.4
