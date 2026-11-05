#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Request protection in the actual HTMX OCR application."""

from __future__ import annotations

import json
from pathlib import Path

from bs4 import BeautifulSoup, Tag
from flask import Flask
from pytest import MonkeyPatch, fixture

from scinoephile.image.bbox import Bbox
from scinoephile.web.ocr_validation.app import create_app
from scinoephile.web.ocr_validation.session import OcrValidationSession
from test.helpers import parametrize
from test.helpers.ocr_validation import (
    clear_validation_data,
    make_ocr_html_dir,
    patch_ocr_validation_bboxes,
    prepared_gap_session,
)


@fixture
def app(tmp_path: Path, monkeypatch: MonkeyPatch) -> Flask:
    """Provide the real OCR app with isolated authored and validation data.

    Arguments:
        tmp_path: temporary directory for all output
        monkeypatch: fixture selecting deterministic character boxes
    """
    image_dir_path = make_ocr_html_dir(tmp_path, text="A")
    patch_ocr_validation_bboxes(monkeypatch, [Bbox(0, 10, 0, 20)])
    session = OcrValidationSession.from_dir_path(
        image_dir_path,
        validation_data_dir_path=tmp_path / "validation",
        outfile_path=tmp_path / "output.srt",
        include_done_subtitles=True,
    )
    clear_validation_data(session)
    return create_app(session)


@parametrize(
    "endpoint",
    [
        "/subtitles/0/text",
        "/subtitles/0/concern/char",
        "/subtitles/0/concern/gap",
        "/filters/done",
        "/exit",
    ],
)
def test_mutations_require_the_browser_session_token(
    app: Flask, tmp_path: Path, endpoint: str
):
    """Reject missing or invalid tokens before editing, saving, or shutdown.

    Arguments:
        app: real OCR validation app
        tmp_path: directory containing the original authored files
        endpoint: mutation route to protect
    """
    original = (tmp_path / "image/index.html").read_bytes()
    client = app.test_client()
    client.get("/")
    for token in ("", "wrong", "错"):
        assert client.post(endpoint, headers={"X-CSRF-Token": token}).status_code == 403
    assert (tmp_path / "image/index.html").read_bytes() == original
    assert not (tmp_path / "output.srt").exists()
    assert not (tmp_path / "validation").exists()


@parametrize(
    "headers",
    [
        {"Origin": "https://attacker.example"},
        {"Origin": "null"},
        {"Origin": "http://localhost:12345"},
        {"Sec-Fetch-Site": "cross-site"},
        {"Sec-Fetch-Site": "same-site"},
    ],
)
def test_foreign_mutations_are_rejected_even_with_a_valid_token(
    app: Flask, tmp_path: Path, headers: dict[str, str]
):
    """Reject foreign requests even when they supply a valid browser token.

    Arguments:
        app: real OCR validation app
        tmp_path: directory containing authored files
        headers: foreign origin or browser fetch context
    """
    client = app.test_client()
    page = client.get("/")
    response = client.post(
        "/subtitles/0/text",
        data={"text-0": "unauthorized"},
        headers={**_csrf_headers(page.get_data(as_text=True)), **headers},
    )
    assert response.status_code == 403
    assert "unauthorized" not in (tmp_path / "image/index.html").read_text(
        encoding="utf-8"
    )


@parametrize("host", ["attacker.example", "localhost.attacker.example"])
def test_untrusted_hosts_are_rejected(app: Flask, host: str):
    """Reject DNS rebinding hosts for documents and bundled scripts.

    Arguments:
        app: real OCR validation app
        host: foreign Host header
    """
    for route in ("/", "/static/htmx.min.js"):
        assert (
            app.test_client().get(route, base_url=f"http://{host}").status_code == 400
        )


@parametrize("endpoint", ["/", "/subtitles/0/validation.png"])
@parametrize(
    "headers",
    [
        {"Origin": "https://attacker.example"},
        {"Origin": "null"},
        {"Origin": "http://localhost:12345"},
        {"Sec-Fetch-Site": "cross-site"},
        {"Sec-Fetch-Site": "same-site"},
    ],
)
def test_foreign_gets_cannot_persist_validation_results(
    tmp_path: Path, monkeypatch: MonkeyPatch, endpoint: str, headers: dict[str, str]
):
    """Reject foreign GETs before scanning can rewrite authored subtitle text.

    Arguments:
        tmp_path: directory for authored and validation data
        monkeypatch: fixture selecting deterministic character boxes
        endpoint: document or image route that scans validation state
        headers: foreign origin or browser fetch context
    """
    image_dir_path = make_ocr_html_dir(tmp_path, text="AB")
    patch_ocr_validation_bboxes(monkeypatch, [Bbox(0, 10, 0, 20), Bbox(20, 30, 0, 20)])
    session = prepared_gap_session(image_dir_path, tmp_path)
    client = create_app(session).test_client()
    index_path = image_dir_path / "index.html"
    original = index_path.read_bytes()

    assert client.get(endpoint, headers=headers).status_code == 403
    assert index_path.read_bytes() == original
    assert session.series.events[0].text == "AB"
    assert not (tmp_path / "validation-data").exists()

    allowed = client.get(
        endpoint,
        headers={"Origin": "http://localhost", "Sec-Fetch-Site": "same-origin"},
    )
    assert allowed.status_code == 200
    assert index_path.read_bytes() != original
    assert " " in session.series.events[0].text


@parametrize(
    ("host", "base_url"),
    [
        ("127.0.0.1", "http://127.0.0.1:5000"),
        ("::1", "http://[::1]:5000"),
        ("local.example", "http://local.example:5000"),
        ("192.0.2.5", "http://192.0.2.5:5000"),
        ("0.0.0.0", "http://localhost:5000"),
        ("::", "http://[::1]:5000"),
    ],
)
def test_configured_hosts_accept_same_origin_edits(
    app: Flask, host: str, base_url: str
):
    """Preserve configured hosts for normal HTMX edits.

    Arguments:
        app: real app supplying the OCR session
        host: configured bind host
        base_url: browser address for that server
    """
    client = create_app(app.config["OCR_VALIDATION_SESSION"], host=host).test_client()
    page = client.get("/", base_url=base_url)
    response = client.post(
        "/subtitles/0/text",
        data={"text-0": "B"},
        base_url=base_url,
        headers={**_csrf_headers(page.get_data(as_text=True)), "Origin": base_url},
    )
    assert response.status_code == 200
    assert b'id="subtitle-0"' in response.data
    assert app.config["OCR_VALIDATION_SESSION"].series.events[0].text == "B"


def test_tokens_are_bound_to_the_browser_session(app: Flask):
    """Reject a token copied from a different browser session.

    Arguments:
        app: real OCR validation app
    """
    first = app.test_client()
    second = app.test_client()
    headers = _csrf_headers(first.get("/").get_data(as_text=True))
    second.get("/")
    assert second.post("/filters/done", headers=headers).status_code == 403


def test_htmx_keeps_box_selection_until_approval(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Keep a selected two-box character across protected HTMX updates.

    Arguments:
        tmp_path: directory for authored and validation data
        monkeypatch: fixture selecting two parts of one character
    """
    image_dir_path = make_ocr_html_dir(tmp_path, text="A")
    patch_ocr_validation_bboxes(monkeypatch, [Bbox(0, 5, 0, 20), Bbox(5, 10, 0, 20)])
    session = OcrValidationSession.from_dir_path(
        image_dir_path, validation_data_dir_path=tmp_path / "validation"
    )
    clear_validation_data(session)
    client = create_app(session).test_client()
    headers = _csrf_headers(client.get("/").get_data(as_text=True))

    expanded = client.post(
        "/subtitles/0/concern/char",
        data={"action": "expand", "n_bboxes": "1"},
        headers=headers,
    )
    assert expanded.status_code == 200
    assert b'name="n_bboxes" value="2"' in expanded.data

    approved = client.post(
        "/subtitles/0/concern/char",
        data={"action": "accept", "n_bboxes": "2"},
        headers=headers,
    )
    assert approved.status_code == 200
    assert (tmp_path / "validation/char_dims_2.csv").read_text(encoding="utf-8") == (
        "A,5,20,0,5,20\n"
    )


def test_security_headers_cover_documents_assets_and_rejections(app: Flask):
    """Protect rendered data and prevent framing of the editor.

    Arguments:
        app: real OCR validation app
    """
    client = app.test_client()
    page = client.get("/", headers={"Sec-Fetch-Site": "none"})
    assert page.status_code == 200
    asset = client.get("/static/htmx.min.js", headers={"Sec-Fetch-Site": "same-origin"})
    assert asset.status_code == 200
    for response in (page, asset, client.post("/exit")):
        assert response.headers["Cache-Control"] == "no-store"
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]


def _csrf_headers(html: str) -> dict[str, str]:
    """Read the inherited headers actually supplied to HTMX by the page.

    Arguments:
        html: rendered editor page
    Returns:
        HTMX request headers with the browser's protection token
    """
    root = BeautifulSoup(html, "html.parser").find("html")
    assert isinstance(root, Tag)
    encoded = root.get("hx-headers")
    assert isinstance(encoded, str)
    token = json.loads(encoded)["X-CSRF-Token"]
    assert isinstance(token, str) and token
    return {"HX-Request": "true", "X-CSRF-Token": token}
