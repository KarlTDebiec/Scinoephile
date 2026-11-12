#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Request protection for the OCR validation editor."""

from __future__ import annotations

from pathlib import Path

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
def ocr_session(tmp_path: Path, monkeypatch: MonkeyPatch) -> OcrValidationSession:
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
    )
    clear_validation_data(session)
    return session


@fixture
def app(ocr_session: OcrValidationSession) -> Flask:
    """Provide an OCR editor using the isolated session.

    Arguments:
        ocr_session: validation session for the test subtitle
    """
    return create_app(ocr_session)


@parametrize(
    "endpoint",
    ["/subtitles/0/text", "/subtitles/0/concern/char", "/subtitles/0/concern/gap"],
)
def test_mutations_require_a_csrf_token(app: Flask, tmp_path: Path, endpoint: str):
    """Reject both native and HTMX forms without a session token.

    Arguments:
        app: real OCR validation app
        tmp_path: directory containing the original authored files
        endpoint: mutation route to protect
    """
    original = (tmp_path / "image/index.html").read_bytes()
    client = app.test_client()
    client.get("/")
    for headers in ({}, {"HX-Request": "true"}):
        response = client.post(endpoint, data={"csrf": "invalid"}, headers=headers)
        assert response.status_code == 403
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
def test_foreign_mutations_are_rejected_with_a_valid_token(
    app: Flask,
    ocr_session: OcrValidationSession,
    tmp_path: Path,
    headers: dict[str, str],
):
    """Reject foreign requests even when they have a valid CSRF token.

    Arguments:
        app: real OCR validation app
        ocr_session: current subtitle state
        tmp_path: directory containing authored files
        headers: foreign origin or browser fetch context
    """
    client = app.test_client()
    client.get("/")
    with client.session_transaction() as cookie:
        csrf = cookie["csrf"]
    response = client.post(
        "/subtitles/0/text",
        data={
            "text": "unauthorized",
            "csrf": csrf,
            "version": ocr_session.subtitle_row(0).version,
        },
        headers={"HX-Request": "true", **headers},
    )
    assert response.status_code == 403
    assert "unauthorized" not in (tmp_path / "image/index.html").read_text(
        encoding="utf-8"
    )


@parametrize("bind_host", ["127.0.0.1", "0.0.0.0", "::", "2001:db8::2"])
@parametrize(
    "host", ["attacker.example", "localhost.attacker.example", "[::2]", "[2001:db8::1]"]
)
def test_untrusted_hosts_are_rejected(
    ocr_session: OcrValidationSession, bind_host: str, host: str
):
    """Reject DNS rebinding hosts for documents and bundled scripts.

    Arguments:
        ocr_session: current subtitle state
        bind_host: explicitly configured bind host or wildcard address
        host: foreign Host header
    """
    client = create_app(ocr_session, host=bind_host).test_client()
    for route in ("/", "/static/htmx.min.js"):
        assert client.get(route, base_url=f"http://{host}").status_code == 400


@parametrize("endpoint", ["/", "/subtitles/0/image.png"])
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
    if endpoint == "/":
        assert index_path.read_bytes() != original
        assert " " in session.series.events[0].text
    else:
        assert index_path.read_bytes() == original


@parametrize(
    ("host", "base_url"),
    [
        ("127.0.0.1", "http://127.0.0.1:5000"),
        ("127.0.0.1", "http://[::1]:5000"),
        ("::1", "http://[::1]:5000"),
        ("[::1]", "http://[::1]:5000"),
        ("2001:db8::1", "http://[2001:db8::1]:5000"),
        ("[2001:db8::1]", "http://[2001:db8::1]:5000"),
        ("local.example", "http://local.example:5000"),
        ("LOCAL.EXAMPLE", "http://local.example:5000"),
        ("192.0.2.5", "http://192.0.2.5:5000"),
        ("0.0.0.0", "http://localhost:5000"),
        ("::", "http://[::1]:5000"),
    ],
)
def test_configured_hosts_accept_same_origin_edits(
    ocr_session: OcrValidationSession, host: str, base_url: str
):
    """Preserve configured hosts for normal HTMX edits.

    Arguments:
        ocr_session: current subtitle state
        host: configured bind host
        base_url: browser address for that server
    """
    client = create_app(ocr_session, host=host).test_client()
    assert client.get("/", base_url=base_url).status_code == 200
    with client.session_transaction(base_url=base_url) as cookie:
        csrf = cookie["csrf"]
    response = client.post(
        "/subtitles/0/text",
        data={
            "text": "B",
            "csrf": csrf,
            "version": ocr_session.subtitle_row(0).version,
        },
        base_url=base_url,
        headers={"HX-Request": "true", "Origin": base_url},
    )
    assert response.status_code == 200
    assert b'id="validation-0"' in response.data
    assert ocr_session.series.events[0].text == "B"


@parametrize("host", ["", "bad host", "user@localhost", "localhost:65536", "[::::]"])
def test_malformed_hosts_are_rejected(app: Flask, host: str):
    """Reject malformed Host headers before serving local documents or scripts.

    Arguments:
        app: real OCR validation app
        host: malformed Host header supplied without URL normalization
    """
    for route in ("/", "/static/htmx.min.js"):
        with app.test_request_context(route, environ_overrides={"HTTP_HOST": host}):
            assert app.full_dispatch_request().status_code == 400


def test_foreign_custom_header_preflight_is_not_authorized(app: Flask):
    """Keep browsers from authorizing foreign HTMX requests through CORS.

    Arguments:
        app: real OCR validation app
    """
    response = app.test_client().options(
        "/subtitles/0/text",
        headers={
            "Origin": "https://attacker.example",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "HX-Request",
        },
    )
    assert response.status_code == 403
    assert "Access-Control-Allow-Origin" not in response.headers
    assert "Access-Control-Allow-Headers" not in response.headers


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
    for response in (page, asset, client.post("/subtitles/0/text")):
        assert response.headers["Cache-Control"] == "no-store"
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
