#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of OCR validation manager behavior."""

from __future__ import annotations

import logging
from copy import deepcopy
from pathlib import Path

from PIL import Image
from pytest import LogCaptureFixture, MonkeyPatch, mark

from scinoephile.image.bbox import Bbox
from scinoephile.image.ocr.validation import MAX_CHAR_DIM_BBOXES, ValidationManager
from scinoephile.image.ocr.validation.char_cursor import CharCursor
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle


def test_validate_confident_space_gap_updates_text(
    tmp_path: Path, monkeypatch: MonkeyPatch, caplog: LogCaptureFixture
):
    """Test confident space gap mismatches are corrected without warning.

    Arguments:
        tmp_path: temporary directory path
        monkeypatch: pytest monkeypatch fixture
        caplog: pytest log-capture fixture
    """
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
    tmp_path: Path, monkeypatch: MonkeyPatch, caplog: LogCaptureFixture
):
    """Test confident adjacent gap mismatches are corrected without warning.

    Arguments:
        tmp_path: temporary directory path
        monkeypatch: pytest monkeypatch fixture
        caplog: pytest log-capture fixture
    """
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
    tmp_path: Path, monkeypatch: MonkeyPatch, caplog: LogCaptureFixture
):
    """Test confident tab gap replaces an OCR newline without warning.

    Arguments:
        tmp_path: temporary directory path
        monkeypatch: pytest monkeypatch fixture
        caplog: pytest log-capture fixture
    """
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
    tmp_path: Path, monkeypatch: MonkeyPatch, caplog: LogCaptureFixture
):
    """Test ambiguous gaps warn and leave the subtitle text unchanged.

    Arguments:
        tmp_path: temporary directory path
        monkeypatch: pytest monkeypatch fixture
        caplog: pytest log-capture fixture
    """
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


@mark.parametrize(
    ("char", "boxes", "expected"),
    [
        (
            "怕",
            [
                Bbox(0, 6, 12, 29),
                Bbox(11, 14, 0, 55),
                Bbox(18, 23, 12, 23),
                Bbox(28, 56, 0, 55),
            ],
            4,
        ),
        ("副", [Bbox(0, 34, 2, 54), Bbox(39, 54, 0, 54), Bbox(65, 122, 0, 55)], 2),
        (
            "利",
            [
                Bbox(0, 30, 0, 55),
                Bbox(36, 39, 7, 40),
                Bbox(41, 53, 0, 55),
                Bbox(65, 121, 0, 55),
            ],
            3,
        ),
        ("怕", [Bbox(0, 6, 20, 70), Bbox(12, 100, 0, 100), Bbox(120, 220, 0, 100)], 2),
        ("怕", [Bbox(0, 6, 0, 55), Bbox(30, 85, 0, 55)], 1),
        ("怕", [Bbox(50, 56, 0, 55), Bbox(0, 50, 75, 130)], 1),
        ("怕", [Bbox(0, 6, 0, 55), Bbox(10, 60, 75, 130)], 1),
        ("怕", [Bbox(0, 20, 0, 55), Bbox(25, 70, 0, 55)], 1),
        ("怕", [Bbox(0, 55, 0, 55), Bbox(57, 63, 0, 55)], 1),
        ("A", [Bbox(0, 6, 0, 55), Bbox(8, 55, 0, 55)], 1),
        ("，", [Bbox(0, 6, 0, 55), Bbox(8, 55, 0, 55)], 1),
    ],
)
def test_suggest_hanzi_components_without_approving(
    tmp_path: Path, char: str, boxes: list[Bbox], expected: int
):
    """Suggest components without crossing glyph boundaries or approving them.

    Arguments:
        tmp_path: temporary directory path
        char: character being reviewed
        boxes: detected component rectangles
        expected: initial number of selected rectangles
    """
    manager = _prepared_manager(tmp_path)
    sub = _series(char).events[0]
    sub.bboxes = list(boxes)
    cursor = CharCursor(sub=sub, sub_idx=0)
    before_dims = deepcopy(manager.char_dims_by_n)

    assert manager.suggest_char_n_bboxes(cursor) == expected
    assert cursor.char_idx == cursor.bbox_idx == 0
    assert sub.bboxes == boxes
    assert manager.char_dims_by_n == before_dims
    assert not (tmp_path / "cache" / "char_dims_1.csv").exists()


def test_suggest_respects_known_narrow_hanzi(tmp_path: Path):
    """Keep an intentionally narrow Hanzi from swallowing the next character.

    Arguments:
        tmp_path: temporary directory path
    """
    manager = _prepared_manager(tmp_path)
    manager.char_dims_by_n[1]["丨"] = {(6, 55)}
    sub = _series("丨怕").events[0]
    sub.bboxes = [Bbox(0, 6, 0, 55), Bbox(8, 55, 0, 55)]

    assert manager.suggest_char_n_bboxes(CharCursor(sub=sub, sub_idx=0)) == 1


def _prepared_manager(tmp_path: Path) -> ValidationManager:
    """Create a validation manager prepared for A/B gap tests.

    Arguments:
        tmp_path: pytest temporary directory path
    Returns:
        prepared validation manager
    """
    manager = ValidationManager(validation_data_dir_path=tmp_path / "cache")
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
