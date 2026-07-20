#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for guided-transcription test-data generation."""

from __future__ import annotations

from logging import INFO, WARNING, getLogger
from pathlib import Path
from unittest.mock import Mock

from pytest import LogCaptureFixture, MonkeyPatch, mark, param

import test.data.transcription as transcription_data
from scinoephile.core import Language
from scinoephile.core.subtitles import Series, Subtitle


def test_get_reference_for_guide_blocks_limits_reference_prefix():
    """Limit an evaluation reference using the selected guide blocks."""
    guide = Series(
        events=[
            Subtitle(start=0, end=1_000, text="一"),
            Subtitle(start=5_000, end=6_000, text="二"),
        ]
    )
    reference = Series(
        events=[
            Subtitle(start=100, end=500, text="甲"),
            Subtitle(start=999, end=1_500, text="乙"),
            Subtitle(start=1_000, end=2_000, text="丙"),
            Subtitle(start=5_500, end=6_000, text="丁"),
        ]
    )

    limited = transcription_data.get_reference_for_guide_blocks(
        reference,
        guide,
        1,
    )

    assert [subtitle.text for subtitle in limited] == ["甲", "乙"]


@mark.parametrize(
    ("language", "guide_language", "detected_language", "expected_log_level"),
    [
        param(
            Language.yue_hans,
            Language.zho_hans,
            Language.zho_hans,
            INFO,
            id="yue-hans-from-zho-hans",
        ),
        param(
            Language.yue_hant,
            Language.zho_hant,
            Language.zho_hant,
            INFO,
            id="yue-hant-from-zho-hant",
        ),
        param(
            Language.yue_hant,
            Language.zho_hant,
            Language.zho_hans,
            WARNING,
            id="different-script",
        ),
        param(
            Language.eng,
            Language.zho_hant,
            Language.zho_hant,
            WARNING,
            id="non-cantonese",
        ),
    ],
)
def test_process_transcription_orders_stages_and_relogs_expected_mismatch(
    tmp_path: Path,
    caplog: LogCaptureFixture,
    monkeypatch: MonkeyPatch,
    language: Language,
    guide_language: Language,
    detected_language: Language,
    expected_log_level: int,
):
    """Run stages in order and relog only same-script Yue-to-Zho detection.

    Arguments:
        tmp_path: temporary pipeline directory
        caplog: captured log records
        monkeypatch: pytest monkeypatch fixture
        language: transcription language
        guide_language: guide subtitle language
        detected_language: language reported for the fresh transcription
        expected_log_level: expected mismatch log level
    """
    reference = Series(events=[Subtitle(start=0, end=1_000, text="佢喺度")])
    guide = Series(events=[Subtitle(start=0, end=1_000, text="他在這裡")])
    reference_path = tmp_path / "reference.srt"
    guide_path = tmp_path / "guide.srt"
    reference.save(reference_path)
    guide.save(guide_path)
    stage_order: list[str] = []
    stage_audio = Mock(
        side_effect=lambda *args, **kwargs: stage_order.append("audio") or reference
    )
    transcribe = Mock(
        side_effect=lambda *args, **kwargs: (
            stage_order.append("transcribe") or reference
        )
    )
    mismatch_message = (
        f"Explicit language {language.code} does not "
        f"match detected language {detected_language.code}; "
        f"using {language.code}"
    )
    language_logger = getLogger("scinoephile.workflows.helpers")
    clean = Mock(
        side_effect=lambda *args, **kwargs: (
            stage_order.append("clean")
            or language_logger.warning(mismatch_message)
            or reference
        )
    )
    review = Mock(
        side_effect=lambda *args, **kwargs: stage_order.append("review") or reference
    )
    translate = Mock(
        side_effect=lambda *args, **kwargs: stage_order.append("translate") or reference
    )
    monkeypatch.setattr(
        transcription_data,
        "resolve_language",
        Mock(side_effect=lambda series, explicit_language: explicit_language),
    )
    monkeypatch.setattr(transcription_data, "_stage_audio_series", stage_audio)
    monkeypatch.setattr(
        transcription_data,
        "_load_or_transcribe_series_guided",
        transcribe,
    )
    monkeypatch.setattr(transcription_data, "load_or_clean_series", clean)
    monkeypatch.setattr(
        transcription_data,
        "_load_or_review_series_guided",
        review,
    )
    monkeypatch.setattr(
        transcription_data,
        "_load_or_translate_series_gaps",
        translate,
    )

    with caplog.at_level(INFO):
        output = transcription_data.process_transcription(
            tmp_path,
            guide_path,
            reference_path=reference_path,
            language=language,
            guide_language=guide_language,
            additional_context="Movie-specific context",
        )

    assert output is reference
    assert stage_order == ["audio", "transcribe", "clean", "review", "translate"]
    assert transcribe.call_args.kwargs["transcription_kw"] == {
        "additional_context": "Movie-specific context"
    }
    assert review.call_args.kwargs["reviewer_kw"] == {
        "additional_context": "Movie-specific context"
    }
    assert translate.call_args.kwargs["translator_kw"] == {
        "additional_context": "Movie-specific context"
    }
    mismatch_records = [
        record for record in caplog.records if record.getMessage() == mismatch_message
    ]
    assert len(mismatch_records) == 1
    assert mismatch_records[0].levelno == expected_log_level


def test_process_transcription_can_stop_after_cleaning(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Skip guided review and gap translation when they are disabled.

    Arguments:
        tmp_path: temporary pipeline directory
        monkeypatch: pytest monkeypatch fixture
    """
    reference = Series(events=[Subtitle(start=0, end=1_000, text="佢喺度")])
    reference_path = tmp_path / "reference.srt"
    guide_path = tmp_path / "guide.srt"
    reference.save(reference_path)
    reference.save(guide_path)
    review = Mock()
    translate = Mock()
    monkeypatch.setattr(
        transcription_data,
        "resolve_language",
        Mock(side_effect=lambda series, explicit_language: explicit_language),
    )
    monkeypatch.setattr(
        transcription_data,
        "_stage_audio_series",
        Mock(return_value=reference),
    )
    monkeypatch.setattr(
        transcription_data,
        "_load_or_transcribe_series_guided",
        Mock(return_value=reference),
    )
    monkeypatch.setattr(
        transcription_data,
        "load_or_clean_series",
        Mock(return_value=reference),
    )
    monkeypatch.setattr(
        transcription_data,
        "_load_or_review_series_guided",
        review,
    )
    monkeypatch.setattr(
        transcription_data,
        "_load_or_translate_series_gaps",
        translate,
    )

    output = transcription_data.process_transcription(
        tmp_path,
        guide_path,
        reference_path=reference_path,
        language=Language.yue_hant,
        guide_language=Language.zho_hant,
        run_review_and_translation=False,
    )

    assert output is reference
    review.assert_not_called()
    translate.assert_not_called()
