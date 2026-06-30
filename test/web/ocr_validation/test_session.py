#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of OCR validation web session state."""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from pytest import MonkeyPatch, raises

from scinoephile.core import ScinoephileError
from scinoephile.image.bbox import Bbox
from scinoephile.image.subtitles import ImageSeries
from scinoephile.web.ocr_validation.concerns import (
    CharDimsConcern,
    ConcernKind,
    ErrorConcern,
    GapConcern,
    ValidationStatus,
)
from scinoephile.web.ocr_validation.session import OcrValidationSession
from test.helpers.ocr_validation import (
    clear_validation_data,
    make_ocr_html_dir,
    make_two_image_ocr_html_dir,
    patch_ocr_validation_bboxes,
    prepared_gap_session,
)


def test_session_loads_rows_from_html_index(tmp_path: Path):
    """Test session row loading from an OCR image HTML directory."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="recognized")

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


def test_session_requires_index_html_file(tmp_path: Path):
    """Test session construction rejects a non-file index.html path."""
    html_dir_path = tmp_path / "image"
    html_dir_path.mkdir()
    (html_dir_path / "index.html").mkdir()

    with raises(ScinoephileError, match="Expected .*index\\.html to be a file"):
        OcrValidationSession.from_dir_path(html_dir_path)


def test_session_wraps_image_series_load_errors(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
):
    """Test session construction wraps image series loading errors.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    html_dir_path = make_ocr_html_dir(tmp_path, text="recognized")

    def fake_load(path: Path) -> ImageSeries:
        """Fake image subtitle loading failure."""
        raise ValueError(f"{path} could not be loaded")

    monkeypatch.setattr(
        "scinoephile.web.ocr_validation.session.ImageSeries.load",
        fake_load,
    )

    with raises(
        ScinoephileError,
        match="Unable to initialize OCR validation session from .*could not be loaded",
    ) as excinfo:
        OcrValidationSession.from_dir_path(html_dir_path)

    assert isinstance(excinfo.value.__cause__, ValueError)


def test_concern_kind_excludes_done_state():
    """Test concern kind only models validation concerns, not row status."""
    assert "DONE" not in ConcernKind.__members__


def test_session_uses_one_font_size_for_series(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test editable font size is detected once for the whole series."""
    html_dir_path = make_two_image_ocr_html_dir(tmp_path, text_1="A", text_2="B")

    def mock_get_bboxes(img: Image.Image) -> list[Bbox]:
        """Return bboxes that vary by image width."""
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
    clear_validation_data(session)

    rows = session.subtitle_rows()

    assert rows[0].text_font_size_css == "60px"
    assert rows[1].text_font_size_css == "60px"
    assert rows[0].text_letter_spacing_css == "0px"
    assert rows[1].text_letter_spacing_css == "0px"


def test_session_uses_cjk_letter_spacing(tmp_path: Path):
    """Test editable text keeps subtitle letter spacing for CJK text."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="姐")
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        include_done_subtitles=True,
        cache_dir_path=tmp_path / "cache",
    )
    clear_validation_data(session)

    row = session.subtitle_row(0)

    assert row.text_letter_spacing_css == "10px"


def test_session_rebuilds_raw_bboxes_for_validation_state(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test web validation state ignores stale pre-merged bboxes."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="A")
    raw_bboxes = [
        Bbox(0, 23, 0, 61),
        Bbox(35, 40, 1, 61),
        Bbox(43, 58, 18, 38),
    ]
    patch_ocr_validation_bboxes(monkeypatch, raw_bboxes)
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        include_done_subtitles=True,
        cache_dir_path=tmp_path / "cache",
    )
    clear_validation_data(session)
    session.series.events[0].bboxes = [Bbox(0, 58, 0, 61)]

    row = session.subtitle_row(0)

    assert isinstance(row.concern, CharDimsConcern)
    assert row.concern.dims == (23, 61)
    assert row.concern.max_n_bboxes == 3


def test_session_omits_done_rows_from_list_by_default(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test session row lists omit subtitles with no concerns by default."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="A")
    patch_ocr_validation_bboxes(monkeypatch, [Bbox(0, 10, 0, 20)])
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    clear_validation_data(session)
    session.manager.char_dims_by_n[1]["A"] = {(10, 20)}

    rows = session.subtitle_rows()

    assert rows == []


def test_session_includes_done_rows_in_list_when_enabled(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test the internal toggle can include subtitles with no concerns."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="A")
    patch_ocr_validation_bboxes(monkeypatch, [Bbox(0, 10, 0, 20)])
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        include_done_subtitles=True,
        cache_dir_path=tmp_path / "cache",
    )
    clear_validation_data(session)
    session.manager.char_dims_by_n[1]["A"] = {(10, 20)}

    rows = session.subtitle_rows()

    assert len(rows) == 1
    assert rows[0].status == ValidationStatus.DONE
    assert rows[0].concern is None


def test_session_update_text_rewrites_index(tmp_path: Path):
    """Test session text updates persist to index.html and the outfile."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="recognized")
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


def test_session_does_not_write_outfile_on_init(tmp_path: Path):
    """Test session construction does not write the validated outfile."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="recognized")
    outfile_path = tmp_path / "validated.srt"

    OcrValidationSession.from_dir_path(html_dir_path, outfile_path=outfile_path)

    assert not outfile_path.exists()


def test_session_reports_char_dims_concern(tmp_path: Path, monkeypatch: MonkeyPatch):
    """Test unknown character dimensions produce a bbox concern."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="A")
    patch_ocr_validation_bboxes(monkeypatch, [Bbox(0, 10, 0, 20)])
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    clear_validation_data(session)

    row = session.subtitle_row(0)

    assert row.status == ValidationStatus.NEEDS_ACTION
    assert isinstance(row.concern, CharDimsConcern)
    assert row.concern.kind == ConcernKind.CHAR_DIMS
    assert row.concern.char == "A"
    assert row.concern.dims == (10, 20)


def test_session_reports_error_status_when_validation_cannot_continue(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test unrecoverable validation concerns produce an error row status."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="A")
    patch_ocr_validation_bboxes(monkeypatch, [])
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    clear_validation_data(session)

    row = session.subtitle_row(0)

    assert row.status == ValidationStatus.ERROR
    assert isinstance(row.concern, ErrorConcern)


def test_accept_char_dims_marks_single_char_done(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test accepting character dimensions resolves a single-character subtitle."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="A")
    patch_ocr_validation_bboxes(monkeypatch, [Bbox(0, 10, 0, 20)])
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    clear_validation_data(session)

    row = session.resolve_char_concern(0, action="accept", n_bboxes=1)

    assert row.status == ValidationStatus.DONE
    assert row.concern is None
    assert (tmp_path / "cache" / "char_dims_1.csv").read_text(
        encoding="utf-8"
    ) == "A,10,20\n"


def test_contract_char_dims_reduces_selection(tmp_path: Path, monkeypatch: MonkeyPatch):
    """Test contracting character dimensions reduces the selected bbox count."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="A")
    patch_ocr_validation_bboxes(
        monkeypatch,
        [Bbox(0, 10, 0, 20), Bbox(10, 20, 0, 20)],
    )
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    clear_validation_data(session)

    row = session.resolve_char_concern(0, action="expand", n_bboxes=1)

    assert isinstance(row.concern, CharDimsConcern)
    assert row.concern.n_bboxes == 2
    assert row.concern.can_contract

    row = session.resolve_char_concern(0, action="contract", n_bboxes=2)

    assert isinstance(row.concern, CharDimsConcern)
    assert row.concern.n_bboxes == 1
    assert not row.concern.can_contract


def test_session_reports_space_gap_concern(tmp_path: Path, monkeypatch: MonkeyPatch):
    """Test ambiguous adjacent-or-space gaps produce a space concern."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="AB")
    patch_ocr_validation_bboxes(
        monkeypatch,
        [Bbox(0, 10, 0, 20), Bbox(14, 24, 0, 20)],
    )
    session = prepared_gap_session(html_dir_path, tmp_path)

    row = session.subtitle_row(0)

    assert row.status == ValidationStatus.NEEDS_ACTION
    assert isinstance(row.concern, GapConcern)
    assert row.concern.kind == ConcernKind.SPACE_GAP
    assert row.concern.char_1 == "A"
    assert row.concern.char_2 == "B"
    assert row.concern.gap == 4
    assert row.concern.space_prompt_display == "2-6"
    assert row.concern.tab_prompt_display == "12-20"


def test_space_gap_choice_updates_index_text(tmp_path: Path, monkeypatch: MonkeyPatch):
    """Test resolving a space gap writes the expected space into index.html."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="AB")
    patch_ocr_validation_bboxes(
        monkeypatch,
        [Bbox(0, 10, 0, 20), Bbox(14, 24, 0, 20)],
    )
    session = prepared_gap_session(html_dir_path, tmp_path)

    row = session.resolve_gap_concern(0, action="space")

    assert row.text == "A B"
    assert row.status == ValidationStatus.DONE
    assert row.concern is None
    assert session.manager.char_pair_gaps[("A", "B")] == (2, 4, 12, 20)
    assert "A B" in (html_dir_path / "index.html").read_text(encoding="utf-8")


def test_existing_space_gap_does_not_update_cutoffs(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test stale whitespace does not train ambiguous gap cutoffs."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="A B")
    patch_ocr_validation_bboxes(
        monkeypatch,
        [Bbox(0, 10, 0, 20), Bbox(14, 24, 0, 20)],
    )
    session = prepared_gap_session(html_dir_path, tmp_path)

    row = session.subtitle_row(0)

    assert row.status == ValidationStatus.NEEDS_ACTION
    assert isinstance(row.concern, GapConcern)
    assert row.concern.kind == ConcernKind.SPACE_GAP
    assert session.manager.char_pair_gaps[("A", "B")] == (2, 6, 12, 20)


def test_punctuation_ellipsis_gap_reports_existing_space_concern(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test punctuation before ellipsis keeps stale whitespace as a concern."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="！ ⋯")
    patch_ocr_validation_bboxes(
        monkeypatch,
        [Bbox(0, 10, 0, 20), Bbox(67, 77, 0, 20)],
    )
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    clear_validation_data(session)
    session.manager.char_dims_by_n[1]["！"] = {(10, 20)}
    session.manager.char_dims_by_n[1]["⋯"] = {(10, 20)}

    row = session.subtitle_row(0)

    assert row.text == "！ ⋯"
    assert row.status == ValidationStatus.NEEDS_ACTION
    assert isinstance(row.concern, GapConcern)
    assert row.concern.kind == ConcernKind.SPACE_GAP
    assert row.concern.char_1 == "！"
    assert row.concern.char_2 == "⋯"
    assert row.concern.gap == 57
    assert session.manager.char_pair_gaps[("！", "⋯")] == (8, 89, 90, 200)
    assert "！ ⋯" in (html_dir_path / "index.html").read_text(encoding="utf-8")


def test_known_adjacent_gap_mismatch_updates_text_without_concern(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test known adjacent gaps with wrong text update without a user concern."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="臭　　和")
    patch_ocr_validation_bboxes(
        monkeypatch,
        [Bbox(0, 10, 0, 20), Bbox(21, 31, 0, 20)],
    )
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    clear_validation_data(session)
    session.manager.char_dims_by_n[1]["臭"] = {(10, 20)}
    session.manager.char_dims_by_n[1]["和"] = {(10, 20)}
    session.manager.char_pair_gaps[("臭", "和")] = (22, 41, 90, 200)

    row = session.subtitle_row(0)

    assert row.text == "臭和"
    assert row.status == ValidationStatus.DONE
    assert row.concern is None
    assert session.manager.char_pair_gaps[("臭", "和")] == (22, 41, 90, 200)
    assert "臭和" in (html_dir_path / "index.html").read_text(encoding="utf-8")


def test_fullwidth_latin_gap_uses_default_cutoffs(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test fullwidth Latin characters use default full-width gap cutoffs."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="你Ｋ")
    patch_ocr_validation_bboxes(
        monkeypatch,
        [Bbox(0, 10, 0, 20), Bbox(18, 28, 0, 20)],
    )
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    clear_validation_data(session)
    session.manager.char_dims_by_n[1]["你"] = {(10, 20)}
    session.manager.char_dims_by_n[1]["Ｋ"] = {(10, 20)}

    row = session.subtitle_row(0)

    assert row.status == ValidationStatus.DONE
    assert row.concern is None
    assert session.manager.char_pair_gaps[("你", "Ｋ")] == (22, 89, 90, 200)


def test_adjacent_gap_choice_updates_cutoff(tmp_path: Path, monkeypatch: MonkeyPatch):
    """Test adjacent choice for an ambiguous gap updates the gap cutoffs."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="白了")
    patch_ocr_validation_bboxes(
        monkeypatch,
        [Bbox(0, 10, 0, 20), Bbox(14, 24, 0, 20)],
    )
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    clear_validation_data(session)
    session.manager.char_dims_by_n[1]["白"] = {(10, 20)}
    session.manager.char_dims_by_n[1]["了"] = {(10, 20)}
    session.manager.char_pair_gaps[("白", "了")] = (2, 6, 12, 20)

    row = session.subtitle_row(0)

    assert isinstance(row.concern, GapConcern)
    assert row.concern.kind == ConcernKind.SPACE_GAP
    assert row.concern.gap == 4
    assert row.concern.observed == ""
    assert row.concern.expected == "　"

    row = session.resolve_gap_concern(0, action="adjacent")

    assert row.text == "白了"
    assert row.status == ValidationStatus.DONE
    assert row.concern is None
    assert session.manager.char_pair_gaps[("白", "了")] == (4, 6, 12, 20)


def test_boundary_space_gap_updates_cutoff_without_concern(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test boundary space text updates cutoffs without a user concern."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="A B")
    patch_ocr_validation_bboxes(
        monkeypatch,
        [Bbox(0, 10, 0, 20), Bbox(15, 25, 0, 20)],
    )
    session = prepared_gap_session(html_dir_path, tmp_path)

    row = session.subtitle_row(0)

    assert row.text == "A B"
    assert row.status == ValidationStatus.DONE
    assert row.concern is None
    assert session.manager.char_pair_gaps[("A", "B")] == (2, 5, 12, 20)
    assert "A B" in (html_dir_path / "index.html").read_text(encoding="utf-8")


def test_boundary_tab_gap_updates_cutoff_without_concern(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test boundary tab text updates cutoffs without a user concern."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="A    B")
    patch_ocr_validation_bboxes(
        monkeypatch,
        [Bbox(0, 10, 0, 20), Bbox(29, 39, 0, 20)],
    )
    session = prepared_gap_session(html_dir_path, tmp_path)

    row = session.subtitle_row(0)

    assert row.text == "A    B"
    assert row.status == ValidationStatus.DONE
    assert row.concern is None
    assert session.manager.char_pair_gaps[("A", "B")] == (2, 6, 12, 19)
    assert "A    B" in (html_dir_path / "index.html").read_text(encoding="utf-8")


def test_known_space_gap_mismatch_updates_text_without_concern(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test known space gaps with wrong text update without a user concern."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="呀 你")
    patch_ocr_validation_bboxes(
        monkeypatch,
        [Bbox(0, 10, 0, 20), Bbox(51, 61, 0, 20)],
    )
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    clear_validation_data(session)
    session.manager.char_dims_by_n[1]["呀"] = {(10, 20)}
    session.manager.char_dims_by_n[1]["你"] = {(10, 20)}
    session.manager.char_pair_gaps[("呀", "你")] = (22, 40, 90, 200)

    row = session.subtitle_row(0)

    assert row.text == "呀　你"
    assert row.status == ValidationStatus.DONE
    assert row.concern is None
    assert session.manager.char_pair_gaps[("呀", "你")] == (22, 40, 90, 200)
    assert "呀　你" in (html_dir_path / "index.html").read_text(encoding="utf-8")


def test_known_tab_gap_mismatch_updates_text_without_concern(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test known tab gaps with wrong text update without a user concern."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="AB")
    patch_ocr_validation_bboxes(
        monkeypatch,
        [Bbox(0, 10, 0, 20), Bbox(32, 42, 0, 20)],
    )
    session = prepared_gap_session(html_dir_path, tmp_path)

    row = session.subtitle_row(0)

    assert row.text == "A    B"
    assert row.status == ValidationStatus.DONE
    assert row.concern is None
    assert session.manager.char_pair_gaps[("A", "B")] == (2, 6, 12, 20)
    assert "A    B" in (html_dir_path / "index.html").read_text(encoding="utf-8")


def test_known_tab_gap_replaces_newline_without_concern(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test known tab gaps with newline text update without a user concern."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="A<br />B")
    patch_ocr_validation_bboxes(
        monkeypatch,
        [Bbox(0, 10, 0, 20), Bbox(32, 42, 0, 20)],
    )
    session = prepared_gap_session(html_dir_path, tmp_path)

    row = session.subtitle_row(0)

    assert row.text == "A    B"
    assert row.status == ValidationStatus.DONE
    assert row.concern is None
    assert session.manager.char_pair_gaps[("A", "B")] == (2, 6, 12, 20)
    assert "A    B" in (html_dir_path / "index.html").read_text(encoding="utf-8")


def test_tab_gap_choice_updates_index_text(tmp_path: Path, monkeypatch: MonkeyPatch):
    """Test resolving a tab gap writes expected wide spacing into index.html."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="AB")
    patch_ocr_validation_bboxes(
        monkeypatch,
        [Bbox(0, 10, 0, 20), Bbox(25, 35, 0, 20)],
    )
    session = prepared_gap_session(html_dir_path, tmp_path)

    row = session.resolve_gap_concern(0, action="tab")

    assert row.text == "A    B"
    assert row.status == ValidationStatus.DONE
    assert row.concern is None
    assert session.manager.char_pair_gaps[("A", "B")] == (2, 6, 12, 15)
    assert "A    B" in (html_dir_path / "index.html").read_text(encoding="utf-8")
