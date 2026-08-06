#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of FireRed language and audio-event adapters."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

from pydub import AudioSegment

from scinoephile.audio.classification import (
    AudioEvent,
    FireRedAudioEventDetector,
    FireRedLanguageIdentifier,
)


def test_language_identifier_windows_vad_and_applies_source_offset(
    tmp_path: Path, monkeypatch
):
    """FireRedLID results should retain their selected source-timeline position."""
    monkeypatch.setattr(
        "scinoephile.audio.classification.firered._get_runtime_version", lambda: "test"
    )
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


def test_audio_event_detector_applies_source_offset(tmp_path: Path, monkeypatch):
    """FireRed mVAD timestamps should map from a selected slice to the source."""
    monkeypatch.setattr(
        "scinoephile.audio.classification.firered._get_runtime_version", lambda: "test"
    )
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
