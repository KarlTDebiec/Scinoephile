#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of FireRed language and audio-event adapters."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest
from pydub import AudioSegment

from scinoephile.audio.classification import (
    AudioClassificationInferenceError,
    AudioEvent,
    FireRedAudioEventDetector,
    FireRedLanguageIdentifier,
)


def test_audio_event_detector_applies_source_offset(tmp_path: Path):
    """FireRed mVAD timestamps should map from a selected slice to the source.

    Arguments:
        tmp_path: temporary cache root path
    """
    detector = FireRedAudioEventDetector(tmp_path)
    detector._model = Mock(  # noqa: SLF001
        detect=Mock(
            return_value=(
                {
                    "event2timestamps": {
                        "speech": [(0.1, 0.9)],
                        "singing": [(0.4, 0.8)],
                        "music": [(0.0, 1.0)],
                    }
                },
                None,
            )
        )
    )

    result = detector(AudioSegment.silent(duration=1_000), offset_seconds=20.0)

    assert [(span.event, span.start, span.end) for span in result.spans] == [
        (AudioEvent.MUSIC, 20.0, 21.0),
        (AudioEvent.SPEECH, 20.1, 20.9),
        (AudioEvent.SINGING, 20.4, 20.8),
    ]


def test_audio_event_detector_rejects_malformed_span(tmp_path: Path):
    """A malformed FireRed span should surface as an inference error.

    Arguments:
        tmp_path: temporary cache root path
    """
    detector = FireRedAudioEventDetector(tmp_path)
    detector._model = Mock(  # noqa: SLF001
        detect=Mock(
            return_value=(
                {
                    "event2timestamps": {
                        "speech": [(1.0, 0.0)],
                        "singing": [],
                        "music": [],
                    }
                },
                None,
            )
        )
    )

    with pytest.raises(AudioClassificationInferenceError, match="detection failed"):
        detector(AudioSegment.silent(duration=1_000))


def test_language_identifier_rejects_missing_model_output(tmp_path: Path):
    """A suppressed FireRedLID failure should surface as an inference error.

    Arguments:
        tmp_path: temporary cache root path
    """
    identifier = FireRedLanguageIdentifier(tmp_path)
    identifier._model = Mock(  # noqa: SLF001
        process=Mock(return_value=[{"uttid": "window_000000", "lang": ""}])
    )

    with pytest.raises(AudioClassificationInferenceError, match="no language"):
        identifier(AudioSegment.silent(duration=1_000), ((0, 1000),))


def test_language_identifier_reuses_cached_result(tmp_path: Path):
    """A matching language-identification request should not rerun inference.

    Arguments:
        tmp_path: temporary cache root path
    """
    audio = AudioSegment.silent(duration=1_000)
    first_identifier = FireRedLanguageIdentifier(tmp_path)
    first_identifier._model = Mock(  # noqa: SLF001
        process=Mock(
            return_value=[
                {"uttid": "window_000000", "lang": "zh yue", "confidence": 0.9}
            ]
        )
    )
    expected = first_identifier(audio, ((0, 1000),))

    second_identifier = FireRedLanguageIdentifier(tmp_path)
    second_identifier._model = Mock()  # noqa: SLF001

    assert second_identifier(audio, ((0, 1000),)) == expected
    second_identifier._model.process.assert_not_called()  # noqa: SLF001


def test_language_identifier_windows_vad_and_applies_source_offset(tmp_path: Path):
    """FireRedLID results should retain their selected source-timeline position.

    Arguments:
        tmp_path: temporary cache root path
    """
    identifier = FireRedLanguageIdentifier(tmp_path, batch_size=2)
    identifier._model = Mock(  # noqa: SLF001
        process=Mock(
            return_value=[
                {"uttid": "window_000000", "lang": "zh yue", "confidence": 0.9},
                {"uttid": "window_000001", "lang": "ja", "confidence": 0.8},
            ]
        )
    )

    result = identifier(
        AudioSegment.silent(duration=3_000),
        ((0, 1000), (1500, 2500)),
        offset_seconds=10.0,
    )

    assert [
        (span.start, span.end, span.language, span.confidence) for span in result.spans
    ] == [(10.0, 11.0, "zh-yue", 0.9), (11.5, 12.5, "ja", 0.8)]
