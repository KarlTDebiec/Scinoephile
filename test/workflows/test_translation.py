#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of translation workflow."""

from __future__ import annotations

from logging import WARNING

from pytest import LogCaptureFixture, MonkeyPatch, raises

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.workflows import translation


def test_translate_series_rejects_unsupported_pair():
    """Test translation workflow rejects unsupported language pairs."""
    with raises(ScinoephileError, match="Unsupported translation pair: eng to eng"):
        translation.translate_series(
            source=Series(),
            source_language=Language.eng,
            target_language=Language.eng,
        )


def test_translate_series_requires_target_language():
    """Test regular translation requires a target language."""
    with raises(ScinoephileError, match="--target-language is required"):
        translation.translate_series(
            source=Series(),
            source_language=Language.eng,
        )


def test_translate_series_runs_registered_regular_operation(
    monkeypatch: MonkeyPatch,
):
    """Test regular translation operation routing.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    source = Series()
    output = Series()
    translate_args: list[tuple[Series, Language, Language, dict[str, object]]] = []

    def get_translated(
        route_source: Series,
        source_language: Language,
        target_language: Language,
        **kwargs: object,
    ) -> Series:
        """Record translation arguments."""
        translate_args.append((route_source, source_language, target_language, kwargs))
        return output

    monkeypatch.setattr(translation, "get_translated", get_translated)

    result = translation.translate_series(
        source=source,
        source_language=Language.eng,
        target_language=Language.yue_hant,
        additional_context="context",
    )

    assert result is output
    assert translate_args == [
        (
            source,
            Language.eng,
            Language.yue_hant,
            {"provider": None, "additional_context": "context"},
        )
    ]


def test_translate_series_guided_detects_languages(monkeypatch: MonkeyPatch):
    """Test guided translation detects source and target languages.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    source = Series()
    target = Series()
    output = Series()
    translate_args: list[tuple[Series, Series, Language, Language]] = []

    def get_guided_translated(
        route_source: Series,
        route_target: Series,
        source_language: Language,
        target_language: Language,
        **kwargs: object,
    ) -> Series:
        """Record translation arguments."""
        translate_args.append(
            (route_source, route_target, source_language, target_language)
        )
        return output

    def get_series_language(series: Series) -> Language | None:
        """Return languages by subtitle series identity."""
        if series is source:
            return Language.zho_hans
        if series is target:
            return Language.eng
        return None

    monkeypatch.setattr(translation, "get_guided_translated", get_guided_translated)
    monkeypatch.setattr(translation, "get_series_language", get_series_language)

    result = translation.translate_series_guided(
        source=source,
        target=target,
    )

    assert result is output
    assert translate_args == [(source, target, Language.zho_hans, Language.eng)]


def test_translate_series_warns_when_explicit_source_language_mismatches_detection(
    caplog: LogCaptureFixture,
    monkeypatch: MonkeyPatch,
):
    """Test explicit source language mismatch warnings are emitted by workflow.

    Arguments:
        caplog: pytest log capture fixture
        monkeypatch: pytest monkeypatch fixture
    """
    source = Series()
    output = Series()

    def get_translated(
        route_source: Series,
        source_language: Language,
        target_language: Language,
        **kwargs: object,
    ) -> Series:
        """Return a fake output."""
        return output

    monkeypatch.setattr(translation, "get_translated", get_translated)
    monkeypatch.setattr(translation, "get_series_language", lambda series: Language.eng)

    with caplog.at_level(WARNING):
        result = translation.translate_series(
            source=source,
            source_language=Language.zho_hans,
            target_language=Language.yue_hans,
        )

    assert result is output
    assert (
        "Explicit language zho-Hans does not match detected language eng; "
        "using zho-Hans"
    ) in caplog.text
