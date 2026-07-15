#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for shared workflow helpers."""

from __future__ import annotations

from logging import INFO, WARNING

from pytest import LogCaptureFixture

from scinoephile.core import Language
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.workflows.helpers import resolve_language


def test_resolve_language_logs_same_script_chinese_mismatch_at_info(
    caplog: LogCaptureFixture,
):
    """Log a same-script Chinese language mismatch at info level.

    Arguments:
        caplog: captured log records
    """
    series = Series(
        events=[
            Subtitle(text="他在這裡了"),
            Subtitle(text="她在這裡了"),
            Subtitle(text="這是他的"),
        ]
    )

    with caplog.at_level(INFO, logger="scinoephile.workflows.helpers"):
        language = resolve_language(series, Language.yue_hant)

    assert language is Language.yue_hant
    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == INFO


def test_resolve_language_logs_script_mismatch_at_warning(
    caplog: LogCaptureFixture,
):
    """Log a Chinese script mismatch at warning level.

    Arguments:
        caplog: captured log records
    """
    series = Series(
        events=[
            Subtitle(text="他在这里了"),
            Subtitle(text="她在这里了"),
            Subtitle(text="这是他的"),
        ]
    )

    language = resolve_language(series, Language.yue_hant)

    assert language is Language.yue_hant
    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == WARNING
