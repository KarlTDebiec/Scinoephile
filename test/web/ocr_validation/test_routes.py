#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of OCR validation web routes."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from flask import Flask
from PIL import Image
from pytest import MonkeyPatch

from scinoephile.image.bbox import Bbox
from scinoephile.web.ocr_validation.app import create_app
from scinoephile.web.ocr_validation.session import OcrValidationSession
from test.helpers.ocr_validation import (
    clear_validation_data,
    make_ocr_html_dir,
    patch_ocr_validation_bboxes,
    prepared_gap_session,
)


def test_index_renders_subtitle_list(tmp_path: Path):
    """Test the index route renders the subtitle list UI."""
    app = create_app(_session(tmp_path, text="recognized", include_done_subtitles=True))

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert b'<html lang="en">' in response.data
    assert b"https://unpkg.com/htmx.org" not in response.data
    assert b'src="/static/htmx.min.js"' in response.data
    assert b'class="subtitle"' in response.data
    assert b'id="sub-1"' in response.data
    assert b'href="#sub-1"' in response.data
    assert b"subtitle-number-1" not in response.data
    assert b"<figure" in response.data
    assert b" style=" not in response.data
    assert b"image-rendering: pixelated;" in response.data
    assert b"image-rendering: crisp-edges;" not in response.data
    assert b"#1</a>:" in response.data
    _assert_index_filter_toggle(response.data)
    _assert_index_subtitle_figure(response.data)
    _assert_index_textarea(response.data)
    assert b"<hr" in response.data


def test_static_htmx_asset_is_served(tmp_path: Path):
    """Test the web UI serves its vendored HTMX asset locally."""
    app = create_app(_session(tmp_path, text="recognized", include_done_subtitles=True))

    response = app.test_client().get("/static/htmx.min.js")

    assert response.status_code == 200
    assert b"htmx" in response.data.lower()


def test_index_renders_single_char_concern_image(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test character concerns render one focused image and table."""
    app = _char_concern_app(tmp_path, monkeypatch)

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert response.data.count(b'src="/subtitles/0/concern.png?v=char-dims-0-0-1"') == 1
    assert b'src="/subtitles/0/validation.png?v=' not in response.data
    assert b"<td>A</td>" in response.data
    assert b"<td>1</td>" in response.data
    assert b"<td>(10, 20)</td>" in response.data
    assert b'value="contract"' in response.data
    assert b'value="expand"' in response.data
    assert b'value="accept"' in response.data


def test_index_renders_char_concern_romanizations(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test character concern tables render romanizations below Hanzi."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="霆")
    patch_ocr_validation_bboxes(monkeypatch, [Bbox(0, 10, 0, 20)])
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    clear_validation_data(session)
    app = create_app(session)

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert b"<th>Char</th>" in response.data
    assert b"data-char" in response.data
    assert "霆".encode() in response.data
    assert "tíng".encode() in response.data
    assert "tìhng".encode() in response.data


def test_index_omits_romanizations_for_unrecognized_symbol(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test character concern tables skip romanization for non-Hanzi symbols."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="▼")
    patch_ocr_validation_bboxes(monkeypatch, [Bbox(0, 10, 0, 20)])
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    clear_validation_data(session)
    app = create_app(session)

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert "▼".encode() in response.data
    assert b"<td data-char>" not in response.data
    assert b"<small>" not in response.data


def test_index_reload_reassesses_cached_subtitles(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test index reloads rebuild cached validation states."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="A")
    patch_ocr_validation_bboxes(monkeypatch, [Bbox(0, 10, 0, 20)])
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    clear_validation_data(session)
    app = create_app(session)

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert b'id="sub-1"' in response.data

    session.manager.char_dims_by_n[1]["A"] = {(10, 20)}

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert b'id="sub-1"' not in response.data


def test_done_filter_route_toggles_ok_subtitles(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test the OK subtitle filter toggle updates the rendered list."""
    app = _done_app(tmp_path, monkeypatch)
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b'id="sub-1"' not in response.data
    assert b'name="include_done_subtitles" value="1"' in response.data
    assert b'aria-pressed="false"' in response.data
    assert b"Show Validated</button>" in response.data

    response = client.post(
        "/filters/done",
        data={"include_done_subtitles": "1"},
        headers={"HX-Request": "true"},
    )

    assert response.status_code == 200
    assert b"<!DOCTYPE html>" not in response.data
    assert b'id="sub-1"' in response.data
    assert b'name="include_done_subtitles" value="0"' in response.data
    assert b'aria-pressed="true"' in response.data
    assert b"Hide Validated</button>" in response.data

    response = client.post(
        "/filters/done",
        data={"include_done_subtitles": "0"},
        headers={"HX-Request": "true"},
    )

    assert response.status_code == 200
    assert b'id="sub-1"' not in response.data
    assert b'name="include_done_subtitles" value="1"' in response.data
    assert b'aria-pressed="false"' in response.data
    assert b"Show Validated</button>" in response.data


def test_exit_route_saves_output_and_shuts_down_server(tmp_path: Path):
    """Test exit route persists validation output and shuts down the server."""

    class FakeServer:
        """Fake server registered on the Flask app."""

        def __init__(self):
            """Initialize."""
            self.shutdown_called = False

        def shutdown(self):
            """Record shutdown."""
            self.shutdown_called = True

    html_dir_path = make_ocr_html_dir(tmp_path, text="recognized")
    outfile_path = tmp_path / "validated.srt"
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        outfile_path=outfile_path,
    )
    app = create_app(session)
    app.testing = True
    server = FakeServer()
    app.config["OCR_VALIDATION_SERVER"] = server

    response = app.test_client().post("/exit", headers={"HX-Request": "true"})

    assert response.status_code == 200
    assert b"Validation exited. You can close this tab." in response.data
    assert outfile_path.exists()
    assert server.shutdown_called


def test_char_concern_image_url_changes_after_accept(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test accepting one character returns a fresh next concern image URL."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="AB")
    patch_ocr_validation_bboxes(
        monkeypatch,
        [Bbox(0, 10, 0, 20), Bbox(20, 30, 0, 20)],
    )
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    clear_validation_data(session)
    app = create_app(session)

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert b'src="/subtitles/0/concern.png?v=char-dims-0-0-1"' in response.data

    response = app.test_client().post(
        "/subtitles/0/concern/char",
        data={"action": "accept", "n_bboxes": "1"},
        headers={"HX-Request": "true"},
    )

    assert response.status_code == 200
    assert b'src="/subtitles/0/concern.png?v=char-dims-1-1-1"' in response.data
    assert b'src="/subtitles/0/concern.png?v=char-dims-0-0-1"' not in response.data


def test_index_renders_space_gap_choice_table(tmp_path: Path, monkeypatch: MonkeyPatch):
    """Test adjacent-or-space concerns render both choice actions."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="霆所")
    patch_ocr_validation_bboxes(
        monkeypatch,
        [Bbox(0, 10, 0, 20), Bbox(50, 60, 0, 20)],
    )
    session = prepared_gap_session(
        html_dir_path,
        tmp_path,
        char_1="霆",
        char_2="所",
        cutoffs=(22, 89, 90, 200),
    )
    app = create_app(session)

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert (
        response.data.count(b'src="/subtitles/0/concern.png?v=space-gap-0-1-40"') == 1
    )
    assert b'src="/subtitles/0/validation.png?v=' not in response.data
    assert "霆".encode() in response.data
    assert "所".encode() in response.data
    assert b"<td>40</td>" in response.data
    assert b'value="adjacent"' in response.data
    assert b'value="space"' in response.data
    assert b"Adjacent</button>" in response.data
    assert b"Space</button>" in response.data


def test_validation_image_route_serves_bbox_png(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test validation row images are rendered with bbox overlays."""
    app = _done_app(tmp_path, monkeypatch)

    response = app.test_client().get("/subtitles/0/validation.png")

    assert response.status_code == 200
    assert response.mimetype == "image/png"
    image = Image.open(BytesIO(response.data))
    assert image.size == (4, 4)
    assert image.getpixel((0, 0)) == (255, 0, 0, 255)


def test_validation_image_route_rejects_missing_subtitle(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test validation image route rejects an out-of-range subtitle index."""
    app = _done_app(tmp_path, monkeypatch)

    response = app.test_client().get("/subtitles/1/validation.png")

    assert response.status_code == 404


def test_text_update_route_rewrites_row(tmp_path: Path):
    """Test text update route rewrites index.html and returns the row."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="old")
    app = create_app(OcrValidationSession.from_dir_path(html_dir_path))

    response = app.test_client().post(
        "/subtitles/0/text",
        data={"text-0": "new"},
        headers={"HX-Request": "true"},
    )

    assert response.status_code == 200
    assert b"new" in response.data
    assert "new" in (html_dir_path / "index.html").read_text(encoding="utf-8")


def test_text_update_route_rejects_missing_subtitle(tmp_path: Path):
    """Test text update route rejects an out-of-range subtitle index."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="old")
    app = create_app(OcrValidationSession.from_dir_path(html_dir_path))

    response = app.test_client().post(
        "/subtitles/1/text",
        data={"text": "new"},
        headers={"HX-Request": "true"},
    )

    assert response.status_code == 404


def test_concern_image_route_serves_png(tmp_path: Path, monkeypatch: MonkeyPatch):
    """Test current concern images are rendered as PNG responses."""
    app = _char_concern_app(tmp_path, monkeypatch)

    response = app.test_client().get("/subtitles/0/concern.png")

    assert response.status_code == 200
    assert response.mimetype == "image/png"


def test_concern_image_route_rejects_missing_subtitle(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test concern image route rejects an out-of-range subtitle index."""
    app = _char_concern_app(tmp_path, monkeypatch)

    response = app.test_client().get("/subtitles/1/concern.png")

    assert response.status_code == 404


def test_char_concern_route_resolves_row(tmp_path: Path, monkeypatch: MonkeyPatch):
    """Test resolving the final character concern omits the completed row."""
    app = _char_concern_app(tmp_path, monkeypatch)

    response = app.test_client().post(
        "/subtitles/0/concern/char",
        data={"action": "accept", "n_bboxes": "1"},
        headers={"HX-Request": "true"},
    )

    assert response.status_code == 200
    assert response.data == b""


def test_char_concern_route_rejects_invalid_action(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test character concern route rejects invalid actions."""
    app = _char_concern_app(tmp_path, monkeypatch)

    response = app.test_client().post(
        "/subtitles/0/concern/char",
        data={"action": "bogus", "n_bboxes": "1"},
        headers={"HX-Request": "true"},
    )

    assert response.status_code == 400


def test_char_concern_route_rejects_missing_subtitle(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test character concern route rejects an out-of-range subtitle index."""
    app = _char_concern_app(tmp_path, monkeypatch)

    response = app.test_client().post(
        "/subtitles/1/concern/char",
        data={"action": "accept", "n_bboxes": "1"},
        headers={"HX-Request": "true"},
    )

    assert response.status_code == 404


def test_gap_concern_route_resolves_row(tmp_path: Path, monkeypatch: MonkeyPatch):
    """Test resolving the final gap concern persists text and omits the row."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="AB")
    patch_ocr_validation_bboxes(
        monkeypatch,
        [Bbox(0, 10, 0, 20), Bbox(14, 24, 0, 20)],
    )
    session = prepared_gap_session(html_dir_path, tmp_path)
    app = create_app(session)

    response = app.test_client().post(
        "/subtitles/0/concern/gap",
        data={"action": "space"},
        headers={"HX-Request": "true"},
    )

    assert response.status_code == 200
    assert response.data == b""
    assert "A B" in (html_dir_path / "index.html").read_text(encoding="utf-8")


def test_gap_concern_route_rejects_invalid_action(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test gap concern route rejects invalid actions."""
    html_dir_path = make_ocr_html_dir(tmp_path, text="AB")
    patch_ocr_validation_bboxes(
        monkeypatch,
        [Bbox(0, 10, 0, 20), Bbox(14, 24, 0, 20)],
    )
    session = prepared_gap_session(html_dir_path, tmp_path)
    app = create_app(session)

    response = app.test_client().post(
        "/subtitles/0/concern/gap",
        data={"action": "bogus"},
        headers={"HX-Request": "true"},
    )

    assert response.status_code == 400


def test_gap_concern_route_rejects_missing_subtitle(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test gap concern route rejects an out-of-range subtitle index."""
    app = _char_concern_app(tmp_path, monkeypatch)

    response = app.test_client().post(
        "/subtitles/1/concern/gap",
        data={"action": "space"},
        headers={"HX-Request": "true"},
    )

    assert response.status_code == 404


def _char_concern_app(tmp_path: Path, monkeypatch: MonkeyPatch) -> Flask:
    """Create an app with one character dimension concern.

    Arguments:
        tmp_path: pytest temporary directory path
        monkeypatch: pytest monkeypatch fixture
    Returns:
        Flask app
    """
    html_dir_path = make_ocr_html_dir(tmp_path, text="A")
    patch_ocr_validation_bboxes(monkeypatch, [Bbox(0, 10, 0, 20)])
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    clear_validation_data(session)
    return create_app(session)


def _assert_index_filter_toggle(html: bytes):
    """Assert that the index renders the HTMX OK-subtitle filter toggle.

    Arguments:
        html: rendered response HTML
    """
    assert b'class="filter-toggle"' in html
    assert b'hx-post="/filters/done"' in html
    assert b'hx-post="/exit"' in html
    assert b'hx-target="body"' in html
    assert b'hx-swap="innerHTML"' in html
    assert b'name="include_done_subtitles" value="0"' in html
    assert b'aria-pressed="true"' in html
    assert b"Hide Validated</button>" in html
    assert b"Exit Validation</button>" in html


def _assert_index_subtitle_figure(html: bytes):
    """Assert that the index renders responsive subtitle images.

    Arguments:
        html: rendered response HTML
    """
    assert b"--subtitle-image-width: 2px" in html
    assert b'src="/subtitles/0/' in html
    assert b".png?v=" in html
    assert b'width="2"' in html
    assert b'height="2"' in html
    assert b'loading="eager"' in html


def _assert_index_textarea(html: bytes):
    """Assert that the index renders the subtitle edit textarea styling.

    Arguments:
        html: rendered response HTML
    """
    assert b'id="subtitle-text-0"' in html
    assert b'name="text-0"' in html
    assert b'autocomplete="off"' in html
    assert b'rows="1"' in html
    assert b'hx-post="/subtitles/0/text"' in html
    assert b'hx-trigger="blur changed"' in html
    assert b"--subtitle-text-color: rgb(255, 255, 255)" in html
    assert b"--subtitle-shadow-color: rgb(0, 0, 0)" in html
    assert b"--subtitle-font-size:" in html
    assert b"overflow: hidden" in html
    assert b'wrap="off"' in html


def _done_app(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    *,
    include_done_subtitles: bool = False,
) -> Flask:
    """Create an app with one subtitle that has no concerns.

    Arguments:
        tmp_path: pytest temporary directory path
        monkeypatch: pytest monkeypatch fixture
        include_done_subtitles: whether to include subtitles with no concerns
    Returns:
        Flask app
    """
    html_dir_path = make_ocr_html_dir(tmp_path, text="A")
    patch_ocr_validation_bboxes(monkeypatch, [Bbox(0, 10, 0, 20)])
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        include_done_subtitles=include_done_subtitles,
        cache_dir_path=tmp_path / "cache",
    )
    clear_validation_data(session)
    session.manager.char_dims_by_n[1]["A"] = {(10, 20)}
    return create_app(session)


def _session(
    tmp_path: Path,
    *,
    text: str,
    include_done_subtitles: bool = False,
) -> OcrValidationSession:
    """Create a basic OCR validation session.

    Arguments:
        tmp_path: pytest temporary directory path
        text: HTML subtitle text content
        include_done_subtitles: whether to include subtitles with no concerns
    Returns:
        OCR validation session
    """
    return OcrValidationSession.from_dir_path(
        make_ocr_html_dir(tmp_path, text=text),
        include_done_subtitles=include_done_subtitles,
    )
