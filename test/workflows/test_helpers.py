#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for shared workflow helpers."""

from __future__ import annotations

from logging import INFO, WARNING

from pytest import LogCaptureFixture, MonkeyPatch

import scinoephile.workflows.helpers as workflow_helpers
from scinoephile.core import Language
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.workflows.clean import clean_series


def test_resolve_language_warns_for_default_yue_zho_mismatch(
    caplog: LogCaptureFixture,
    monkeypatch: MonkeyPatch,
):
    """Warn for a Cantonese and Mandarin mismatch by default.

    Arguments:
        caplog: captured log records
        monkeypatch: pytest monkeypatch fixture
    """
    monkeypatch.setattr(
        workflow_helpers,
        "get_series_language",
        lambda _: Language.zho_hant,
    )

    language = workflow_helpers.resolve_language(Series(), Language.yue_hant)

    assert language is Language.yue_hant
    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == WARNING


def test_clean_series_logs_opted_detected_language_at_info(
    caplog: LogCaptureFixture,
    monkeypatch: MonkeyPatch,
):
    """Log an explicitly opted detected-language mismatch at info.

    Arguments:
        caplog: captured log records
        monkeypatch: pytest monkeypatch fixture
    """
    monkeypatch.setattr(
        workflow_helpers,
        "get_series_language",
        lambda _: Language.zho_hant,
    )
    series = Series(events=[Subtitle(text="佢喺度")])

    with caplog.at_level(INFO, logger=workflow_helpers.__name__):
        clean_series(
            series,
            language=Language.yue_hant,
            informational_detected_language=Language.zho_hant,
        )

    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == INFO


def test_clean_series_warns_for_non_opted_detected_language(
    caplog: LogCaptureFixture,
    monkeypatch: MonkeyPatch,
):
    """Warn when detection differs from the one informational opt-in.

    Arguments:
        caplog: captured log records
        monkeypatch: pytest monkeypatch fixture
    """
    monkeypatch.setattr(
        workflow_helpers,
        "get_series_language",
        lambda _: Language.zho_hans,
    )
    series = Series(events=[Subtitle(text="佢喺度")])

    clean_series(
        series,
        language=Language.yue_hant,
        informational_detected_language=Language.zho_hant,
    )

    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == WARNING
