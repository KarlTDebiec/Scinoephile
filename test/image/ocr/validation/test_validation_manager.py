#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of OCR validation manager behavior."""

from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image
from pytest import LogCaptureFixture, MonkeyPatch

from scinoephile.image.bbox import Bbox
from scinoephile.image.ocr.validation import MAX_CHAR_DIM_BBOXES, ValidationManager
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle


def test_validate_confident_space_gap_updates_text(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    caplog: LogCaptureFixture,
):
    """Test confident space gap mismatches are corrected without warning."""
    monkeypatch.setattr(
        "scinoephile.image.ocr.validation.validation_manager.get_bboxes",
        lambda img: [Bbox(0, 10, 0, 20), Bbox(18, 28, 0, 20)],
    )
    manager = _prepared_manager(tmp_path)
    series = _series("AB")
    caplog.set_level(logging.WARNING)

    output = manager.validate(series)

    assert output.events[0].text == "A B"
    assert _warning_messages(caplog) == []


def test_validate_confident_adjacent_gap_updates_text(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    caplog: LogCaptureFixture,
):
    """Test confident adjacent gap mismatches are corrected without warning."""
    monkeypatch.setattr(
        "scinoephile.image.ocr.validation.validation_manager.get_bboxes",
        lambda img: [Bbox(0, 10, 0, 20), Bbox(11, 21, 0, 20)],
    )
    manager = _prepared_manager(tmp_path)
    series = _series("A B")
    caplog.set_level(logging.WARNING)

    output = manager.validate(series)

    assert output.events[0].text == "AB"
    assert _warning_messages(caplog) == []


def test_validate_confident_tab_gap_updates_newline_to_tab(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    caplog: LogCaptureFixture,
):
    """Test confident tab gap replaces an OCR newline without warning."""
    monkeypatch.setattr(
        "scinoephile.image.ocr.validation.validation_manager.get_bboxes",
        lambda img: [Bbox(0, 10, 0, 20), Bbox(32, 42, 0, 20)],
    )
    manager = _prepared_manager(tmp_path)
    series = _series("A\\NB")
    caplog.set_level(logging.WARNING)

    output = manager.validate(series)

    assert output.events[0].text == "A    B"
    assert _warning_messages(caplog) == []


def test_validate_ambiguous_gap_warns_without_updating_text(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    caplog: LogCaptureFixture,
):
    """Test ambiguous gaps warn and leave the subtitle text unchanged."""
    monkeypatch.setattr(
        "scinoephile.image.ocr.validation.validation_manager.get_bboxes",
        lambda img: [Bbox(0, 10, 0, 20), Bbox(14, 24, 0, 20)],
    )
    manager = _prepared_manager(tmp_path)
    series = _series("AB")
    caplog.set_level(logging.WARNING)

    output = manager.validate(series)

    assert output.events[0].text == "AB"
    assert _warning_messages(caplog) == [
        "Sub    1 | Char  1 | AB | 'A,B' -> 4 | "
        "question about adjacent or space gap, observed ''"
    ]


def _prepared_manager(tmp_path: Path) -> ValidationManager:
    """Create a validation manager prepared for A/B gap tests.

    Arguments:
        tmp_path: pytest temporary directory path
    Returns:
        prepared validation manager
    """
    manager = ValidationManager(cache_dir_path=tmp_path / "cache")
    manager.char_dims_by_n = {n: {} for n in range(1, MAX_CHAR_DIM_BBOXES + 1)}
    manager.char_dims_by_n[1]["A"] = {(10, 20)}
    manager.char_dims_by_n[1]["B"] = {(10, 20)}
    manager.char_grp_dims_by_n = {}
    manager.char_pair_gaps = {("A", "B"): (2, 6, 12, 20)}
    return manager


def _series(text: str) -> ImageSeries:
    """Create a one-subtitle image series.

    Arguments:
        text: subtitle text
    Returns:
        one-subtitle image series
    """
    return ImageSeries(
        events=[
            ImageSubtitle(
                start=1000,
                end=2000,
                img=Image.new("LA", (40, 24), (255, 255)),
                text=text,
            )
        ]
    )


def _warning_messages(caplog: LogCaptureFixture) -> list[str]:
    """Get warning messages from a log capture fixture.

    Arguments:
        caplog: pytest log capture fixture
    Returns:
        warning messages
    """
    return [
        record.getMessage()
        for record in caplog.records
        if record.levelno == logging.WARNING
    ]
