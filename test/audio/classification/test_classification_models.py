#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of typed source-wide audio-classification results."""

from __future__ import annotations

from scinoephile.audio.classification import (
    AudioEvent,
    AudioEventDetectionResult,
    AudioEventSpan,
    LanguageIdentificationResult,
    LanguageSpan,
)


def test_language_result_selects_greatest_overlap():
    """Language lookup should use the best-overlapping utterance window."""
    result = LanguageIdentificationResult(
        spans=[
            LanguageSpan(start=1.0, end=2.0, language="zh-yue", confidence=0.9),
            LanguageSpan(start=2.0, end=3.0, language="ja", confidence=0.8),
        ]
    )

    assert result.get_language(1.8, 2.1) == "zh-yue"
    assert result.get_language(2.1, 2.2) == "ja"
    assert result.get_language(3.1, 3.2) is None


def test_language_result_gets_confident_coverage_of_classified_speech():
    """Language coverage should use classified speech as its denominator."""
    result = LanguageIdentificationResult(
        spans=[
            LanguageSpan(start=1.0, end=2.0, language="zh-yue", confidence=0.9),
            LanguageSpan(start=2.0, end=3.0, language="ja", confidence=0.8),
        ]
    )

    assert result.get_coverage(1.5, 2.5, languages={"ja"}) == 0.5
    assert result.get_duration(1.5, 2.5, languages={"ja"}) == 0.5
    assert (
        result.get_coverage(1.5, 2.5, languages={"ja"}, minimum_confidence=0.85) == 0.0
    )
    assert result.get_coverage(3.0, 4.0, languages={"ja"}) == 0.0


def test_audio_event_result_preserves_overlapping_independent_labels():
    """Music and singing should remain independently queryable when overlapping."""
    result = AudioEventDetectionResult(
        spans=[
            AudioEventSpan(start=1.0, end=3.0, event=AudioEvent.MUSIC),
            AudioEventSpan(start=1.5, end=2.5, event=AudioEvent.SINGING),
        ]
    )

    assert result.has_event(AudioEvent.MUSIC, 1.9, 2.1)
    assert result.has_event(AudioEvent.SINGING, 1.9, 2.1)
    assert not result.has_event(AudioEvent.SPEECH, 1.9, 2.1)
    assert result.get_coverage(AudioEvent.MUSIC, 1.0, 3.0) == 1.0
    assert result.get_coverage(AudioEvent.SINGING, 1.0, 3.0) == 0.5
