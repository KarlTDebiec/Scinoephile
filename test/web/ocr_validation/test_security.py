#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Request protection and ordinary browser forms in the actual OCR application."""

from __future__ import annotations

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
    """Provide the real OCR app with one unapproved character and isolated output.

    Arguments:
        tmp_path: temporary directory for all authored and validation data
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
    """Reject missing and invalid tokens before any mutation or shutdown runs.

    Arguments:
        app: real OCR validation app
        tmp_path: temporary directory containing the original authored files
        endpoint: mutation route to protect
    """
    original = (tmp_path / "image/index.html").read_bytes()
    client = app.test_client()
    client.get("/")
    for data in ({}, {"csrf_token": "wrong"}, {"csrf_token": "错"}):
        response = client.post(endpoint, data=data)
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
    ],
)
def test_foreign_mutations_are_rejected_even_with_a_valid_token(
    app: Flask, tmp_path: Path, headers: dict[str, str]
):
    """Reject cross-origin requests before they can persist subtitle edits.

    Arguments:
        app: real OCR validation app
        tmp_path: temporary directory containing the original authored files
        headers: foreign origin or browser fetch context
    """
    client = app.test_client()
    page = client.get("/")
    data = _form_data(page.get_data(as_text=True), "/subtitles/0/text")
    data["text-0"] = "unauthorized"

    response = client.post("/subtitles/0/text", data=data, headers=headers)

    assert response.status_code == 403
    assert "unauthorized" not in (tmp_path / "image/index.html").read_text(
        encoding="utf-8"
    )
    assert not (tmp_path / "output.srt").exists()


@parametrize("host", ["attacker.example", "localhost.attacker.example"])
def test_untrusted_hosts_are_rejected(app: Flask, host: str):
    """Reject DNS rebinding hosts for both documents and browser assets.

    Arguments:
        app: real OCR validation app
        host: foreign Host header
    """
    client = app.test_client()
    for route in ("/", "/static/htmx.min.js"):
        response = client.get(route, base_url=f"http://{host}")
        assert response.status_code == 400


@parametrize("endpoint", ["/", "/subtitles/0/validation.png"])
@parametrize(
    "headers",
    [
        {"Origin": "https://attacker.example"},
        {"Origin": "null"},
        {"Origin": "http://localhost:12345"},
        {"Sec-Fetch-Site": "cross-site"},
    ],
)
def test_foreign_gets_cannot_persist_validation_results(
    tmp_path: Path, monkeypatch: MonkeyPatch, endpoint: str, headers: dict[str, str]
):
    """Reject foreign GETs before automatic gap scanning can rewrite authored text.

    Arguments:
        tmp_path: temporary directory for authored and validation data
        monkeypatch: fixture selecting deterministic character boxes
        endpoint: document or image route that scans subtitle validation state
        headers: foreign origin or browser fetch context
    """
    image_dir_path = make_ocr_html_dir(tmp_path, text="AB")
    patch_ocr_validation_bboxes(monkeypatch, [Bbox(0, 10, 0, 20), Bbox(20, 30, 0, 20)])
    session = prepared_gap_session(image_dir_path, tmp_path)
    client = create_app(session).test_client()
    index_path = image_dir_path / "index.html"
    original = index_path.read_bytes()

    response = client.get(endpoint, headers=headers)

    assert response.status_code == 403
    assert index_path.read_bytes() == original
    assert session.series.events[0].text == "AB"
    assert not (tmp_path / "validation-data").exists()
    allowed = client.get(endpoint, headers={"Origin": "http://localhost"})
    assert allowed.status_code == 200
    assert index_path.read_bytes() != original
    assert session.series.events[0].text.replace(" ", "") == "AB"
    assert " " in session.series.events[0].text


@parametrize(
    "headers", [{}, {"Origin": "http://localhost"}, {"Sec-Fetch-Site": "same-origin"}]
)
def test_local_asset_gets_remain_accessible(app: Flask, headers: dict[str, str]):
    """Allow headerless navigation and same-origin requests for bundled assets.

    Arguments:
        app: real OCR validation app
        headers: initial navigation or same-origin browser headers
    """
    assert (
        app.test_client().get("/static/htmx.min.js", headers=headers).status_code == 200
    )


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
def test_configured_hosts_accept_same_origin_forms(
    app: Flask, host: str, base_url: str
):
    """Preserve concrete CLI host choices and loopback access on wildcard binds.

    Arguments:
        app: real OCR validation app supplying an isolated domain session
        host: configured bind address or hostname
        base_url: browser address matching the intended server
    """
    configured = create_app(app.config["OCR_VALIDATION_SESSION"], host=host)
    client = configured.test_client()
    page = client.get("/", base_url=base_url)
    assert page.status_code == 200
    data = _form_data(page.get_data(as_text=True), "/filters/done")

    response = client.post(
        "/filters/done", data=data, base_url=base_url, headers={"Origin": base_url}
    )

    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.data
    assert client.get("/", base_url="http://attacker.example").status_code == 400


def test_tokens_are_bound_to_the_browser_session(app: Flask):
    """Reject one browser's token in a different browser session.

    Arguments:
        app: real OCR validation app
    """
    first = app.test_client()
    second = app.test_client()
    page = first.get("/")
    data = _form_data(page.get_data(as_text=True), "/filters/done")
    second.get("/")

    assert second.post("/filters/done", data=data).status_code == 403


def test_local_servers_do_not_overwrite_each_others_session_cookies(app: Flask):
    """Keep two local server sessions usable in one browser's shared cookie store.

    Arguments:
        app: first local OCR application
    """
    other = create_app(app.config["OCR_VALIDATION_SESSION"])
    first_browser = app.test_client()
    second_browser = other.test_client()
    page = first_browser.get("/")
    first_name = app.config["SESSION_COOKIE_NAME"]
    first_cookie = first_browser.get_cookie(first_name)
    assert first_cookie is not None
    second_browser.set_cookie(first_name, first_cookie.value)
    second_browser.get("/")
    second_name = other.config["SESSION_COOKIE_NAME"]
    second_cookie = second_browser.get_cookie(second_name)
    assert second_cookie is not None
    first_browser.set_cookie(second_name, second_cookie.value)

    response = first_browser.post(
        "/filters/done", data=_form_data(page.get_data(as_text=True), "/filters/done")
    )
    assert response.status_code == 200


def test_oversized_edits_are_rejected_before_persistence(app: Flask, tmp_path: Path):
    """Bound mutation payloads even when a browser supplies a valid session token.

    Arguments:
        app: real OCR validation app
        tmp_path: temporary directory containing the original authored files
    """
    client = app.test_client()
    page = client.get("/")
    data = _form_data(page.get_data(as_text=True), "/subtitles/0/text")
    data["text-0"] = "x" * 65536
    response = client.post("/subtitles/0/text", data=data)
    assert response.status_code == 413
    assert not (tmp_path / "output.srt").exists()


def test_security_headers_cover_documents_assets_and_rejections(app: Flask):
    """Keep local data uncached and constrain executable and framed content.

    Arguments:
        app: real OCR validation app
    """
    client = app.test_client()
    page = client.get("/")
    for response in (page, client.get("/static/htmx.min.js"), client.post("/exit")):
        assert response.headers["Cache-Control"] == "no-store"
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "script-src 'self'" in response.headers["Content-Security-Policy"]
        assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
        assert "form-action 'self'" in response.headers["Content-Security-Policy"]
    cookie = page.headers.get("Set-Cookie", "")
    assert "HttpOnly" in cookie
    assert "SameSite=Strict" in cookie


def test_every_mutation_form_has_an_ordinary_post_action_and_token(app: Flask):
    """Render protected native forms alongside progressive HTMX behavior.

    Arguments:
        app: real OCR validation app
    """
    page = app.test_client().get("/")
    soup = BeautifulSoup(page.get_data(as_text=True), "html.parser")
    forms = soup.find_all("form")
    assert len(forms) == 4
    for form in forms:
        assert form.get("method") == "post"
        assert form.get("action") == form.get("hx-post")
        token = form.find("input", attrs={"name": "csrf_token"})
        assert isinstance(token, Tag)
        assert token.get("value")
    textarea = soup.find("textarea")
    assert isinstance(textarea, Tag)
    assert textarea.get("hx-include") == "closest form"


def test_ordinary_text_filter_and_exit_forms_work_without_javascript(
    app: Flask, tmp_path: Path
):
    """Persist native form edits and return a full document before ordinary exit.

    Arguments:
        app: real OCR validation app
        tmp_path: temporary directory for the edited output
    """
    client = app.test_client()
    page = client.get("/")
    data = _form_data(page.get_data(as_text=True), "/subtitles/0/text")
    data["text-0"] = "B"
    saved = client.post("/subtitles/0/text", data=data, follow_redirects=True)
    assert saved.history[0].status_code == 303
    assert b"<!DOCTYPE html>" in saved.data
    assert "B" in (tmp_path / "output.srt").read_text(encoding="utf-8")
    filtered = client.post(
        "/filters/done", data=_form_data(saved.get_data(as_text=True), "/filters/done")
    )
    assert filtered.status_code == 200
    assert b"<!DOCTYPE html>" in filtered.data
    exited = client.post(
        "/exit", data=_form_data(filtered.get_data(as_text=True), "/exit")
    )
    assert exited.status_code == 200
    assert b"Validation exited" in exited.data


def test_ordinary_character_approval_form_works_without_javascript(
    app: Flask, tmp_path: Path
):
    """Accept a displayed character concern using only its native form controls.

    Arguments:
        app: real OCR validation app
        tmp_path: temporary directory for approved character data
    """
    client = app.test_client()
    page = client.get("/")
    data = _form_data(page.get_data(as_text=True), "/subtitles/0/concern/char")
    data["action"] = "accept"
    response = client.post(
        "/subtitles/0/concern/char", data=data, follow_redirects=True
    )
    assert response.history[0].status_code == 303
    assert b"<!DOCTYPE html>" in response.data
    assert (tmp_path / "validation/char_dims_1.csv").read_text(encoding="utf-8") == (
        "A,10,20\n"
    )


def test_ordinary_spacing_form_works_without_javascript(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Resolve a spacing concern using its ordinary POST action and session token.

    Arguments:
        tmp_path: temporary directory for authored and validation data
        monkeypatch: fixture selecting deterministic character boxes
    """
    image_dir_path = make_ocr_html_dir(tmp_path, text="AB")
    patch_ocr_validation_bboxes(monkeypatch, [Bbox(0, 10, 0, 20), Bbox(14, 24, 0, 20)])
    session = prepared_gap_session(image_dir_path, tmp_path)
    client = create_app(session).test_client()
    page = client.get("/")
    data = _form_data(page.get_data(as_text=True), "/subtitles/0/concern/gap")
    data["action"] = "space"
    response = client.post("/subtitles/0/concern/gap", data=data, follow_redirects=True)
    assert response.history[0].status_code == 303
    assert b"<!DOCTYPE html>" in response.data
    assert "A B" in (image_dir_path / "index.html").read_text(encoding="utf-8")


def _form_data(html: str, action: str) -> dict[str, str]:
    """Read the hidden controls actually supplied by a rendered ordinary form.

    Arguments:
        html: full HTML document from the app
        action: ordinary mutation URL identifying the form
    Returns:
        hidden form values, including the browser session's CSRF token
    """
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form", attrs={"action": action})
    assert isinstance(form, Tag)
    data = {}
    for control in form.find_all("input", attrs={"type": "hidden"}):
        name = control.get("name")
        value = control.get("value")
        assert isinstance(name, str)
        assert isinstance(value, str)
        data[name] = value
    assert data["csrf_token"]
    return data
