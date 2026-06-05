#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of OCR validation web session state."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from scinoephile.image.bbox import Bbox
from scinoephile.web.ocr_validation.concerns import (
    CharDimsConcern,
    ConcernKind,
    GapConcern,
)
from scinoephile.web.ocr_validation.session import OcrValidationSession


def test_session_loads_rows_from_html_index(tmp_path: Path):
    """Test session row loading from an OCR image HTML directory."""
    html_dir_path = _make_html_dir(tmp_path, text="recognized")

    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        include_done_subtitles=True,
        dev=False,
    )

    rows = session.subtitle_rows()
    assert len(rows) == 1
    assert rows[0].number == 1
    assert rows[0].start == "1,000"
    assert rows[0].end == "2,000"
    assert rows[0].image_width == 2
    assert rows[0].image_height == 2
    assert rows[0].text == "recognized"


def test_session_uses_one_font_size_for_series(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test editable font size is detected once for the whole series."""
    html_dir_path = _make_two_image_html_dir(tmp_path, text_1="A", text_2="B")

    def mock_get_bboxes(img: Image.Image) -> list[Bbox]:
        if img.width == 2:
            return [Bbox(0, 10, 0, 52)]
        return [
            Bbox(0, 10, 0, 60),
            Bbox(12, 22, 0, 60),
        ]

    monkeypatch.setattr(
        "scinoephile.image.subtitles.series.get_bboxes",
        mock_get_bboxes,
    )
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        include_done_subtitles=True,
        cache_dir_path=tmp_path / "cache",
    )
    _clear_validation_data(session)

    rows = session.subtitle_rows()

    assert rows[0].text_font_size_css == "60px"
    assert rows[1].text_font_size_css == "60px"


def test_session_rebuilds_raw_bboxes_for_validation_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test web validation state ignores stale pre-merged bboxes."""
    html_dir_path = _make_html_dir(tmp_path, text="A")
    raw_bboxes = [
        Bbox(0, 23, 0, 61),
        Bbox(35, 40, 1, 61),
        Bbox(43, 58, 18, 38),
    ]
    monkeypatch.setattr(
        "scinoephile.web.ocr_validation.session.get_bboxes",
        lambda img: raw_bboxes.copy(),
    )
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        include_done_subtitles=True,
        cache_dir_path=tmp_path / "cache",
    )
    _clear_validation_data(session)
    session.series.events[0].bboxes = [Bbox(0, 58, 0, 61)]

    row = session.subtitle_row(0)

    assert isinstance(row.concern, CharDimsConcern)
    assert row.concern.dims == (23, 61)
    assert row.concern.max_n_bboxes == 3


def test_session_omits_done_rows_from_list_by_default(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test session row lists omit subtitles with no concerns by default."""
    html_dir_path = _make_html_dir(tmp_path, text="A")
    monkeypatch.setattr(
        "scinoephile.web.ocr_validation.session.get_bboxes",
        lambda img: [Bbox(0, 10, 0, 20)],
    )
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    _clear_validation_data(session)
    session.manager.char_dims_by_n[1]["A"] = {(10, 20)}

    rows = session.subtitle_rows()

    assert rows == []


def test_session_includes_done_rows_in_list_when_enabled(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test the internal toggle can include subtitles with no concerns."""
    html_dir_path = _make_html_dir(tmp_path, text="A")
    monkeypatch.setattr(
        "scinoephile.web.ocr_validation.session.get_bboxes",
        lambda img: [Bbox(0, 10, 0, 20)],
    )
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        include_done_subtitles=True,
        cache_dir_path=tmp_path / "cache",
    )
    _clear_validation_data(session)
    session.manager.char_dims_by_n[1]["A"] = {(10, 20)}

    rows = session.subtitle_rows()

    assert len(rows) == 1
    assert rows[0].concern.kind == ConcernKind.DONE


def test_session_update_text_rewrites_index(tmp_path: Path):
    """Test session text updates persist to index.html and the outfile."""
    html_dir_path = _make_html_dir(tmp_path, text="recognized")
    outfile_path = tmp_path / "validated.srt"
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        outfile_path=outfile_path,
    )

    row = session.update_text(0, "validated\\Nline")

    assert row.text == "validated\\Nline"
    assert "validated<br />line" in (html_dir_path / "index.html").read_text(
        encoding="utf-8"
    )
    assert "validated" in outfile_path.read_text(encoding="utf-8")
    assert "line" in outfile_path.read_text(encoding="utf-8")


def test_session_reports_char_dims_concern(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test unknown character dimensions produce a bbox concern."""
    html_dir_path = _make_html_dir(tmp_path, text="A")
    monkeypatch.setattr(
        "scinoephile.web.ocr_validation.session.get_bboxes",
        lambda img: [Bbox(0, 10, 0, 20)],
    )
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    _clear_validation_data(session)

    row = session.subtitle_row(0)

    assert row.concern.kind == ConcernKind.CHAR_DIMS
    assert isinstance(row.concern, CharDimsConcern)
    assert row.concern.char == "A"
    assert row.concern.dims == (10, 20)


def test_accept_char_dims_marks_single_char_done(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test accepting character dimensions resolves a single-character subtitle."""
    html_dir_path = _make_html_dir(tmp_path, text="A")
    monkeypatch.setattr(
        "scinoephile.web.ocr_validation.session.get_bboxes",
        lambda img: [Bbox(0, 10, 0, 20)],
    )
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    _clear_validation_data(session)

    row = session.resolve_char_concern(0, action="accept", n_bboxes=1)

    assert row.concern.kind == ConcernKind.DONE
    assert (tmp_path / "cache" / "char_dims_1.csv").read_text(
        encoding="utf-8"
    ) == "A,10,20\n"


def test_contract_char_dims_reduces_selection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test contracting character dimensions reduces the selected bbox count."""
    html_dir_path = _make_html_dir(tmp_path, text="A")
    monkeypatch.setattr(
        "scinoephile.web.ocr_validation.session.get_bboxes",
        lambda img: [Bbox(0, 10, 0, 20), Bbox(10, 20, 0, 20)],
    )
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    _clear_validation_data(session)

    row = session.resolve_char_concern(0, action="expand", n_bboxes=1)

    assert isinstance(row.concern, CharDimsConcern)
    assert row.concern.n_bboxes == 2
    assert row.concern.can_contract

    row = session.resolve_char_concern(0, action="contract", n_bboxes=2)

    assert isinstance(row.concern, CharDimsConcern)
    assert row.concern.n_bboxes == 1
    assert not row.concern.can_contract


def test_session_reports_space_gap_concern(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test ambiguous adjacent-or-space gaps produce a space concern."""
    html_dir_path = _make_html_dir(tmp_path, text="AB")
    monkeypatch.setattr(
        "scinoephile.web.ocr_validation.session.get_bboxes",
        lambda img: [Bbox(0, 10, 0, 20), Bbox(14, 24, 0, 20)],
    )
    session = _prepared_gap_session(html_dir_path, tmp_path)

    row = session.subtitle_row(0)

    assert row.concern.kind == ConcernKind.SPACE_GAP
    assert isinstance(row.concern, GapConcern)
    assert row.concern.char_1 == "A"
    assert row.concern.char_2 == "B"
    assert row.concern.gap == 4
    assert row.concern.space_prompt_display == "2-6"
    assert row.concern.tab_prompt_display == "12-20"


def test_space_gap_choice_updates_index_text(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test resolving a space gap writes the expected space into index.html."""
    html_dir_path = _make_html_dir(tmp_path, text="AB")
    monkeypatch.setattr(
        "scinoephile.web.ocr_validation.session.get_bboxes",
        lambda img: [Bbox(0, 10, 0, 20), Bbox(14, 24, 0, 20)],
    )
    session = _prepared_gap_session(html_dir_path, tmp_path)

    row = session.resolve_gap_concern(0, action="space")

    assert row.text == "A B"
    assert row.concern.kind == ConcernKind.DONE
    assert session.manager.char_pair_gaps[("A", "B")] == (2, 4, 12, 20)
    assert "A B" in (html_dir_path / "index.html").read_text(encoding="utf-8")


def test_known_adjacent_gap_mismatch_updates_text_without_concern(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test known adjacent gaps with wrong text update without a user concern."""
    html_dir_path = _make_html_dir(tmp_path, text="臭　　和")
    monkeypatch.setattr(
        "scinoephile.web.ocr_validation.session.get_bboxes",
        lambda img: [Bbox(0, 10, 0, 20), Bbox(21, 31, 0, 20)],
    )
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    _clear_validation_data(session)
    session.manager.char_dims_by_n[1]["臭"] = {(10, 20)}
    session.manager.char_dims_by_n[1]["和"] = {(10, 20)}
    session.manager.char_pair_gaps[("臭", "和")] = (22, 41, 90, 200)

    row = session.subtitle_row(0)

    assert row.text == "臭和"
    assert row.concern.kind == ConcernKind.DONE
    assert session.manager.char_pair_gaps[("臭", "和")] == (22, 41, 90, 200)
    assert "臭和" in (html_dir_path / "index.html").read_text(encoding="utf-8")


def test_adjacent_gap_choice_updates_cutoff(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test adjacent choice for an ambiguous gap updates the gap cutoffs."""
    html_dir_path = _make_html_dir(tmp_path, text="白了")
    monkeypatch.setattr(
        "scinoephile.web.ocr_validation.session.get_bboxes",
        lambda img: [Bbox(0, 10, 0, 20), Bbox(14, 24, 0, 20)],
    )
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    _clear_validation_data(session)
    session.manager.char_dims_by_n[1]["白"] = {(10, 20)}
    session.manager.char_dims_by_n[1]["了"] = {(10, 20)}
    session.manager.char_pair_gaps[("白", "了")] = (2, 6, 12, 20)

    row = session.subtitle_row(0)

    assert row.concern.kind == ConcernKind.SPACE_GAP
    assert isinstance(row.concern, GapConcern)
    assert row.concern.gap == 4
    assert row.concern.observed == ""
    assert row.concern.expected == "　"

    row = session.resolve_gap_concern(0, action="adjacent")

    assert row.text == "白了"
    assert row.concern.kind == ConcernKind.DONE
    assert session.manager.char_pair_gaps[("白", "了")] == (4, 6, 12, 20)


def test_matching_space_gap_updates_cutoff_without_concern(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test matching space text updates cutoffs without a user concern."""
    html_dir_path = _make_html_dir(tmp_path, text="A B")
    monkeypatch.setattr(
        "scinoephile.web.ocr_validation.session.get_bboxes",
        lambda img: [Bbox(0, 10, 0, 20), Bbox(14, 24, 0, 20)],
    )
    session = _prepared_gap_session(html_dir_path, tmp_path)

    row = session.subtitle_row(0)

    assert row.text == "A B"
    assert row.concern.kind == ConcernKind.DONE
    assert session.manager.char_pair_gaps[("A", "B")] == (2, 4, 12, 20)
    assert "A B" in (html_dir_path / "index.html").read_text(encoding="utf-8")


def test_matching_tab_gap_updates_cutoff_without_concern(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test matching tab text updates cutoffs without a user concern."""
    html_dir_path = _make_html_dir(tmp_path, text="A    B")
    monkeypatch.setattr(
        "scinoephile.web.ocr_validation.session.get_bboxes",
        lambda img: [Bbox(0, 10, 0, 20), Bbox(25, 35, 0, 20)],
    )
    session = _prepared_gap_session(html_dir_path, tmp_path)

    row = session.subtitle_row(0)

    assert row.text == "A    B"
    assert row.concern.kind == ConcernKind.DONE
    assert session.manager.char_pair_gaps[("A", "B")] == (2, 6, 12, 15)
    assert "A    B" in (html_dir_path / "index.html").read_text(encoding="utf-8")


def test_known_space_gap_mismatch_updates_text_without_concern(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test known space gaps with wrong text update without a user concern."""
    html_dir_path = _make_html_dir(tmp_path, text="呀 你")
    monkeypatch.setattr(
        "scinoephile.web.ocr_validation.session.get_bboxes",
        lambda img: [Bbox(0, 10, 0, 20), Bbox(51, 61, 0, 20)],
    )
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    _clear_validation_data(session)
    session.manager.char_dims_by_n[1]["呀"] = {(10, 20)}
    session.manager.char_dims_by_n[1]["你"] = {(10, 20)}
    session.manager.char_pair_gaps[("呀", "你")] = (22, 40, 90, 200)

    row = session.subtitle_row(0)

    assert row.text == "呀　你"
    assert row.concern.kind == ConcernKind.DONE
    assert session.manager.char_pair_gaps[("呀", "你")] == (22, 40, 90, 200)
    assert "呀　你" in (html_dir_path / "index.html").read_text(encoding="utf-8")


def test_known_tab_gap_mismatch_updates_text_without_concern(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test known tab gaps with wrong text update without a user concern."""
    html_dir_path = _make_html_dir(tmp_path, text="AB")
    monkeypatch.setattr(
        "scinoephile.web.ocr_validation.session.get_bboxes",
        lambda img: [Bbox(0, 10, 0, 20), Bbox(32, 42, 0, 20)],
    )
    session = _prepared_gap_session(html_dir_path, tmp_path)

    row = session.subtitle_row(0)

    assert row.text == "A    B"
    assert row.concern.kind == ConcernKind.DONE
    assert session.manager.char_pair_gaps[("A", "B")] == (2, 6, 12, 20)
    assert "A    B" in (html_dir_path / "index.html").read_text(encoding="utf-8")


def test_tab_gap_choice_updates_index_text(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test resolving a tab gap writes expected wide spacing into index.html."""
    html_dir_path = _make_html_dir(tmp_path, text="AB")
    monkeypatch.setattr(
        "scinoephile.web.ocr_validation.session.get_bboxes",
        lambda img: [Bbox(0, 10, 0, 20), Bbox(25, 35, 0, 20)],
    )
    session = _prepared_gap_session(html_dir_path, tmp_path)

    row = session.resolve_gap_concern(0, action="tab")

    assert row.text == "A    B"
    assert row.concern.kind == ConcernKind.DONE
    assert session.manager.char_pair_gaps[("A", "B")] == (2, 6, 12, 15)
    assert "A    B" in (html_dir_path / "index.html").read_text(encoding="utf-8")


def _prepared_gap_session(
    html_dir_path: Path,
    tmp_path: Path,
    *,
    cutoffs: tuple[int, int, int, int] = (2, 6, 12, 20),
) -> OcrValidationSession:
    """Create a session prepared to reach gap validation for A/B.

    Arguments:
        html_dir_path: OCR image HTML directory path
        tmp_path: pytest temporary directory path
        cutoffs: gap cutoffs for A/B
    Returns:
        prepared OCR validation session
    """
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    _clear_validation_data(session)
    session.manager.char_dims_by_n[1]["A"] = {(10, 20)}
    session.manager.char_dims_by_n[1]["B"] = {(10, 20)}
    session.manager.char_pair_gaps[("A", "B")] = cutoffs
    return session


def _clear_validation_data(session: OcrValidationSession):
    """Clear loaded OCR validation data for deterministic tests.

    Arguments:
        session: OCR validation session
    """
    session.manager.char_dims_by_n = {n: {} for n in range(1, 6)}
    session.manager.cache_char_dims_by_n = {n: {} for n in range(1, 6)}
    session.manager.char_grp_dims_by_n = {}
    session.manager.cache_char_grp_dims_by_n = {}
    session.manager.char_pair_gaps = {}
    session.manager.cache_char_pair_gaps = {}


def _make_html_dir(tmp_path: Path, *, text: str) -> Path:
    """Create an OCR image HTML directory.

    Arguments:
        tmp_path: pytest temporary directory path
        text: HTML subtitle text content
    Returns:
        OCR image HTML directory path
    """
    html_dir_path = tmp_path / "image"
    html_dir_path.mkdir()
    Image.new("LA", (2, 2), (255, 255)).save(html_dir_path / "0001.png")
    (html_dir_path / "index.html").write_text(
        "\n".join(
            [
                "<!DOCTYPE html>",
                "<html>",
                "<head>",
                '   <meta charset="UTF-8" />',
                "   <title>Subtitle images</title>",
                "</head>",
                "<body>",
                "#1:1,000->2,000"
                "<div style='text-align:center'>"
                "<img src='0001.png' />"
                "<br /><div style='font-size:22px; background-color:WhiteSmoke'>"
                f"{text}</div></div><br /><hr />",
                "</body>",
                "</html>",
            ]
        ),
        encoding="utf-8",
    )
    return html_dir_path


def _make_two_image_html_dir(tmp_path: Path, *, text_1: str, text_2: str) -> Path:
    """Create an OCR image HTML directory with two subtitles.

    Arguments:
        tmp_path: pytest temporary directory path
        text_1: first HTML subtitle text content
        text_2: second HTML subtitle text content
    Returns:
        OCR image HTML directory path
    """
    html_dir_path = tmp_path / "image"
    html_dir_path.mkdir()
    Image.new("LA", (2, 2), (255, 255)).save(html_dir_path / "0001.png")
    Image.new("LA", (3, 3), (255, 255)).save(html_dir_path / "0002.png")
    (html_dir_path / "index.html").write_text(
        "\n".join(
            [
                "<!DOCTYPE html>",
                "<html>",
                "<head>",
                '   <meta charset="UTF-8" />',
                "   <title>Subtitle images</title>",
                "</head>",
                "<body>",
                "#1:1,000->2,000"
                "<div style='text-align:center'>"
                "<img src='0001.png' />"
                "<br /><div style='font-size:22px; background-color:WhiteSmoke'>"
                f"{text_1}</div></div><br /><hr />",
                "#2:3,000->4,000"
                "<div style='text-align:center'>"
                "<img src='0002.png' />"
                "<br /><div style='font-size:22px; background-color:WhiteSmoke'>"
                f"{text_2}</div></div><br /><hr />",
                "</body>",
                "</html>",
            ]
        ),
        encoding="utf-8",
    )
    return html_dir_path
