#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of FireRed language and audio-event adapters."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest
from pydub import AudioSegment

from scinoephile.audio.classification import (
    AudioClassificationInferenceError,
    AudioEvent,
    FireRedAudioEventDetector,
    FireRedLanguageIdentifier,
)


def test_cache_identities_use_installed_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """FireRed cache identities should use installed runtime metadata.

    Arguments:
        tmp_path: temporary cache root path
        monkeypatch: pytest monkeypatch fixture
    """
    runtime_identity = {
        "distribution": "fireredasr2s",
        "version": "test-version",
        "source_revision": "test-revision",
    }
    get_runtime_identity = Mock(return_value=runtime_identity)
    monkeypatch.setattr(
        "scinoephile.audio.classification.firered.get_distribution_identity",
        get_runtime_identity,
    )

    identifier = FireRedLanguageIdentifier(tmp_path)
    detector = FireRedAudioEventDetector(tmp_path)

    assert identifier._get_cache_identity([], 0.0)["runtime"] == runtime_identity
    assert detector._get_cache_identity(0.0)["runtime"] == runtime_identity
    assert get_runtime_identity.call_args_list == [
        call("fireredasr2s"),
        call("fireredasr2s"),
    ]


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


def test_language_identifier_preserves_short_tail_when_subdividing(tmp_path: Path):
    """Balanced subdivisions should preserve short tails of long intervals.

    Arguments:
        tmp_path: temporary cache root path
    """
    identifier = FireRedLanguageIdentifier(tmp_path)
    identifier._model = Mock(  # noqa: SLF001
        process=Mock(
            return_value=[
                {"uttid": "window_000000", "lang": "zh yue", "confidence": 0.9},
                {"uttid": "window_000001", "lang": "zh yue", "confidence": 0.9},
            ]
        )
    )

    result = identifier(AudioSegment.silent(duration=30_400), ((0, 30_400),))

    assert [(span.start, span.end) for span in result.spans] == [
        (0.0, 15.2),
        (15.2, 30.4),
    ]


def test_language_identifier_resolves_cached_model_without_network(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """A cached FireRedLID snapshot should be resolved without network access.

    Arguments:
        tmp_path: temporary cache root path
        monkeypatch: pytest monkeypatch fixture
    """
    get_snapshot_dir_path = Mock(return_value=Path("/cached/model"))
    model = object()
    model_factory = Mock(return_value=model)
    config = object()
    config_factory = Mock(return_value=config)
    monkeypatch.setattr(
        "scinoephile.audio.classification.firered.get_huggingface_snapshot_dir_path",
        get_snapshot_dir_path,
    )
    monkeypatch.setattr(
        "scinoephile.audio.classification.firered.import_firered_lid",
        Mock(
            return_value=(
                SimpleNamespace(from_pretrained=model_factory),
                config_factory,
            )
        ),
    )

    identifier = FireRedLanguageIdentifier(tmp_path)

    assert identifier._get_model() is model  # noqa: SLF001
    get_snapshot_dir_path.assert_called_once_with(
        "FireRedTeam/FireRedLID",
        "1bb4d285c8456429385d9c0810300df4297bc11b",
        ("cmvn.ark", "dict.txt", "model.pth.tar"),
    )
    model_factory.assert_called_once_with(Path("/cached/model"), config)


def test_language_identifier_rejects_incompatible_window_lengths(tmp_path: Path):
    """Window limits should allow subdivision without undersized windows.

    Arguments:
        tmp_path: temporary cache root path
    """
    with pytest.raises(ValueError, match="at least twice"):
        FireRedLanguageIdentifier(
            tmp_path, minimum_window_seconds=20.0, maximum_window_seconds=30.0
        )


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


def test_language_identifier_windows_intervals_and_applies_source_offset(
    tmp_path: Path,
):
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
