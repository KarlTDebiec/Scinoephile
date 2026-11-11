#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Browser-facing OCR validation routes and edit semantics."""

from __future__ import annotations

from base64 import b64decode
from io import BytesIO
from pathlib import Path
from re import findall, search

from PIL import Image
from pytest import MonkeyPatch, mark

from scinoephile.image.bbox import Bbox
from scinoephile.web.ocr_validation.app import create_app
from scinoephile.web.ocr_validation.html_index import load_html_entries
from scinoephile.web.ocr_validation.session import OcrValidationSession
from test.helpers.ocr_validation import (
    clear_validation_data,
    make_ocr_html_dir,
    make_two_image_ocr_html_dir,
    patch_ocr_validation_bboxes,
    prepared_gap_session,
)

_HTMX = {"HX-Request": "true"}


def test_character_approval_advances_then_reuses_learned_dimensions(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Verify a box approval advances one row and can resolve related rows.

    Arguments:
        tmp_path: isolated image and validation data
        monkeypatch: deterministic bbox detection
    """
    images_path = make_two_image_ocr_html_dir(tmp_path, text_1="AB", text_2="A")
    patch_ocr_validation_bboxes(monkeypatch, [Bbox(0, 10, 0, 20), Bbox(20, 30, 0, 20)])
    session = _session(images_path, tmp_path)
    client = create_app(session).test_client()
    page = client.get("/?status=character")
    assert b"1. Check the box selection" in page.data
    assert b"2. Confirm the character" in page.data
    assert b">Characters need review</p>" in page.data
    assert b'id="sub-2"' in page.data

    approved = client.post(
        "/subtitles/0/concern/char?status=character",
        data={**_form_values(page.data), "action": "accept"},
        headers=_HTMX,
    )
    assert approved.status_code == 200
    assert b"<strong>B</strong>" in approved.data
    assert b'x="20"' in approved.data
    assert b'id="preview-0"' in approved.data
    assert b'hx-swap-oob="outerHTML"' in approved.data

    filtered = client.get("/?status=character", headers=_HTMX)
    assert b'id="sub-1"' in filtered.data
    assert b'id="sub-2"' not in filtered.data
    boxes = client.get("/?status=boxes", headers=_HTMX)
    assert b'id="sub-2"' in boxes.data
    assert b"leftover bboxes" in boxes.data
    assert b">Bounding boxes need review</p>" in boxes.data
    assert b'id="sub-1"' not in boxes.data


def test_character_selection_survives_paging_and_rejects_stale_approval(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Preserve selection while filtering and reject a decision for an older selection.

    Arguments:
        tmp_path: isolated image and validation data
        monkeypatch: deterministic bbox detection
    """
    images_path = make_ocr_html_dir(tmp_path, text="A")
    patch_ocr_validation_bboxes(monkeypatch, [Bbox(0, 5, 0, 20), Bbox(5, 10, 0, 20)])
    session = _session(images_path, tmp_path)
    session.manager.char_dims_by_n[2]["A"] = {(10, 20, 0, 5, 20), (20, 30, 6, 8, 22)}
    client = create_app(session).test_client()
    first_page = client.get("/")
    initial = _form_values(first_page.data)
    endpoint = "/subtitles/0/concern/char"
    expanded = client.post(
        endpoint, data={**initial, "action": "expand"}, headers=_HTMX
    )
    assert expanded.status_code == 200
    assert b"2 selected" in expanded.data
    assert b'title="Gap between boxes">0 px</span>' in expanded.data
    maps = findall(rb'src="data:image/png;base64,([^"]+)"', expanded.data)
    assert len(maps) == 2
    with (
        Image.open(BytesIO(b64decode(maps[0]))) as first,
        Image.open(BytesIO(b64decode(maps[1]))) as second,
    ):
        assert first.size == second.size == (100, 100)
        assert first.getpixel((10, 20)) == (33, 84, 198)
        assert first.getpixel((12, 22)) == (71, 168, 115)
        assert first.getpixel((13, 22)) == (185, 112, 117)
        assert first.getpixel((20, 30)) == (33, 84, 198)
        assert first.getpixel((19, 29)) == (185, 112, 117)
        assert second.getpixel((6, 19)) == (185, 112, 117)
        assert first.getpixel((5, 20)) == second.getpixel((5, 20)) == (0, 0, 0)

    filtered = client.get("/?status=character&q=1", headers=_HTMX)
    assert b"2 selected" in filtered.data
    assert not (tmp_path / "validation/char_dims_2.csv").exists()

    stale = client.post(endpoint, data={**initial, "action": "accept"}, headers=_HTMX)
    assert stale.status_code == 409
    assert stale.headers["HX-Retarget"] == "#messages"

    approved = client.post(
        endpoint, data={**_form_values(filtered.data), "action": "accept"}
    )
    assert approved.status_code == 303
    assert client.get(approved.location).status_code == 200
    assert (tmp_path / "validation/char_dims_2.csv").read_text(encoding="utf-8") == (
        "A,5,20,0,5,20\n"
    )


def test_opening_editor_saves_output_without_edits(tmp_path: Path):
    """Verify startup exports the SRT before serving the editor.

    Arguments:
        tmp_path: isolated image and validation data
    """
    images_path = make_ocr_html_dir(tmp_path, text="A")
    session = _session(images_path, tmp_path)
    session.prepare()
    assert "A" in (tmp_path / "validated.srt").read_text(encoding="utf-8")
    page = create_app(session).test_client().get("/")
    assert page.status_code == 200
    assert b"Exit Validation" not in page.data


def test_filters_and_pages_include_automatically_validated_rows(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Verify the default queue, All subtitles, text search, and page cursors.

    Arguments:
        tmp_path: isolated image and validation data
        monkeypatch: deterministic bbox detection
    """
    images_path = make_ocr_html_dir(tmp_path, text="A")
    index_path = images_path / "index.html"
    original = index_path.read_text(encoding="utf-8")
    line = next(line for line in original.splitlines() if line.startswith("#1:"))
    rows = []
    for number in range(1, 13):
        start = 1 + 7 * ((number - 1) // 2) + (number - 1) % 2
        rows.append(
            line.replace("#1:1,000->2,000", f"#{number}:{start},000->{start + 1},000")
        )
    index_path.write_text(original.replace(line, "\n".join(rows)), encoding="utf-8")
    patch_ocr_validation_bboxes(monkeypatch, [Bbox(0, 10, 0, 20)])
    session = _session(images_path, tmp_path)
    session.manager.char_dims_by_n[1]["A"] = {(10, 20)}
    client = create_app(session).test_client()

    review = client.get("/")
    assert b"No subtitles match these filters." in review.data
    assert b"12 of 12 validated" in review.data
    assert b'id="sub-1"' not in review.data
    first = client.get("/?status=all")
    assert b'id="block-1" class="subtitle-block"' in first.data
    assert b'id="sub-1"' in first.data
    assert b'id="sub-10"' in first.data
    assert b'id="sub-11"' not in first.data
    assert b'aria-label="Load more blocks"' in first.data
    next_page = client.get(
        "/?status=all&after=5", headers={**_HTMX, "HX-Target": "load-more"}
    )
    assert b'id="sub-10"' not in next_page.data
    assert b'id="sub-11"' in next_page.data
    assert b'id="sub-12"' in next_page.data
    assert b'aria-label="Load more blocks"' not in next_page.data
    assert b"<!DOCTYPE html>" not in next_page.data
    history = client.get(
        "/?status=all&after=5", headers={**_HTMX, "HX-History-Restore-Request": "true"}
    )
    assert b"<!DOCTYPE html>" in history.data
    assert b'id="sub-1"' in history.data
    assert b'id="sub-12"' in history.data
    found = client.get("/?status=all&q=block+6")
    assert b'id="sub-11"' in found.data
    assert b'id="sub-12"' in found.data
    assert b'id="sub-10"' not in found.data
    assert b"2 matching" in found.data


def test_ocr_page_serves_shared_assets_and_original_preview(tmp_path: Path):
    """Serve the shared shell and keep source pixels separate from SVG boxes.

    Arguments:
        tmp_path: isolated image and validation data
    """
    images_path = make_ocr_html_dir(tmp_path, text="A")
    client = create_app(
        _session(images_path, tmp_path), title="Film & Track"
    ).test_client()
    page = client.get("/?status=all")
    assert search(rb"<title>\s*Film &amp; Track\s*</title>", page.data)
    assert b"<h1>Film &amp; Track</h1>" in page.data
    assert b"<h1>Film &amp; Track</h1>" in client.get("/", headers=_HTMX).data
    assert b"/static/editor.css" in page.data
    assert b"/static/editor.js" in page.data
    assert b"/static/htmx.min.js" in page.data
    assert b"/ocr-validation-assets/ocr-validation.css" in page.data
    assert b"/ocr-validation-assets/ocr-validation.js" in page.data
    for asset in (
        "/static/editor.css",
        "/static/editor.js",
        "/static/icons/sync.svg",
        "/static/htmx.min.js",
        "/ocr-validation-assets/ocr-validation.css",
        "/ocr-validation-assets/ocr-validation.js",
    ):
        assert client.get(asset).status_code == 200

    preview = client.get("/subtitles/0/image.png")
    assert preview.mimetype == "image/png"
    with Image.open(BytesIO(preview.data)) as rendered:
        with Image.open(images_path / "0001.png") as source:
            assert rendered.tobytes() == source.tobytes()
    assert client.get("/subtitles/1/image.png").status_code == 404


@mark.parametrize(
    ("boxes", "status", "message"),
    [
        ([Bbox(0, 10, 0, 20)], "boxes", b"Ran out of bboxes"),
        ([Bbox(0, 10, 0, 20), Bbox(0, 10, 24, 44)], "spacing", b"expected"),
    ],
)
def test_review_filters_distinguish_missing_boxes_and_line_breaks(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    boxes: list[Bbox],
    status: str,
    message: bytes,
):
    """Keep box count and line break errors in their respective review queues.

    Arguments:
        tmp_path: isolated image and validation data
        monkeypatch: deterministic bbox detection
        boxes: detected bounding boxes
        status: filter that includes the concern
        message: message shown for the concern
    """
    images_path = make_ocr_html_dir(tmp_path, text="AB")
    patch_ocr_validation_bboxes(monkeypatch, boxes)
    client = create_app(prepared_gap_session(images_path, tmp_path)).test_client()

    assert message in client.get(f"/?status={status}").data
    for other_status in {"boxes", "character", "spacing"} - {status}:
        assert b'id="sub-1"' not in client.get(f"/?status={other_status}").data
    assert b'id="sub-1"' in client.get("/?status=needs-review").data


@mark.parametrize(
    ("gap", "labels", "cutoffs"),
    [
        (4, ("Auto adjacent <span>2 → 4", "Auto space <span>5 → 4"), (2, 4, 12, 20)),
        (15, ("Auto space <span>12 → 15", "Auto tab <span>19 → 15"), (2, 6, 15, 20)),
    ],
)
def test_spacing_choice_updates_text_and_hides_resolved_concern(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    gap: int,
    labels: tuple[str, str],
    cutoffs: tuple[int, int, int, int],
):
    """Preview the boundary changes and expand automatic spacing to the selected gap.

    Arguments:
        tmp_path: isolated image and validation data
        monkeypatch: deterministic bbox detection
        gap: measured gap in pixels
        labels: expected labels for the two gap choices
        cutoffs: expected cutoffs after choosing automatic space
    """
    images_path = make_ocr_html_dir(tmp_path, text="AB")
    patch_ocr_validation_bboxes(
        monkeypatch, [Bbox(0, 10, 0, 20), Bbox(10 + gap, 20 + gap, 0, 20)]
    )
    session = prepared_gap_session(images_path, tmp_path)
    client = create_app(session).test_client()
    page = client.get("/?status=spacing")
    assert b"<table" not in page.data
    assert b"Check spacing" not in page.data
    assert b">Spacing needs review</p>" in page.data
    assert b'id="sub-1"' not in client.get("/?status=character").data
    page_text = page.get_data(as_text=True)
    assert f'aria-label="Gap of {gap} pixels between “A” and “B”"' in page_text
    assert b'aria-describedby="spacing-key-0"' in page.data
    assert f"--gap-position: {gap / 2}%;" in page_text
    assert search(rb'--band-start: 1\.25%;\s+--band-end: 2\.75%"', page.data)
    legend = page_text.split('id="spacing-key-0">', 1)[1]
    after_legend = legend.split("</ul>", 1)[1]
    for label in labels:
        assert label in after_legend

    response = client.post(
        "/subtitles/0/concern/gap?status=spacing",
        data={**_form_values(page.data), "action": "space"},
        headers=_HTMX,
    )
    assert response.status_code == 200
    assert b'data-visible="false"' in response.data
    assert b"1 of 1 validated" in response.data
    assert b">Validated</p>" in response.data
    assert load_html_entries(images_path)[0].text == "A B"
    assert session.manager.char_pair_gaps[("A", "B")] == cutoffs


def test_text_edit_persists_newline_and_rejects_old_concern(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Persist a multiline edit and prevent approval of the concern it replaced.

    Arguments:
        tmp_path: isolated image and validation data
        monkeypatch: deterministic bbox detection
    """
    images_path = make_ocr_html_dir(tmp_path, text="AB")
    patch_ocr_validation_bboxes(monkeypatch, [Bbox(0, 10, 0, 20), Bbox(0, 10, 24, 44)])
    session = _session(images_path, tmp_path)
    client = create_app(session).test_client()
    page = client.get("/")
    original = _form_values(page.data)
    saved = client.post(
        "/subtitles/0/text", data={**original, "text": "C\r\nB"}, headers=_HTMX
    )
    assert saved.status_code == 200
    assert b"<strong>C</strong>" in saved.data
    assert load_html_entries(images_path)[0].text == "C\\NB"
    assert "C\nB" in (tmp_path / "validated.srt").read_text(encoding="utf-8")

    stale = client.post(
        "/subtitles/0/concern/char",
        data={**original, "action": "accept"},
        headers=_HTMX,
    )
    assert stale.status_code == 409
    assert not (tmp_path / "validation/char_dims_1.csv").exists()

    assert (
        client.post(
            "/subtitles/0/text", data={**original, "text": "stale"}, headers=_HTMX
        ).status_code
        == 409
    )
    assert load_html_entries(images_path)[0].text == "C\\NB"


def _form_values(html: bytes) -> dict[str, str]:
    """Read the first rendered mutation form's security and revision fields.

    Arguments:
        html: OCR document or concern fragment
    Returns:
        CSRF token and subtitle version
    """
    values = {}
    for name in ("csrf", "version"):
        match = search(rf'name="{name}"\s+value="([^"]+)"', html.decode())
        assert match is not None, name
        values[name] = match[1]
    return values


def _session(images_path: Path, tmp_path: Path) -> OcrValidationSession:
    """Load an OCR session with isolated output and no preapproved dimensions.

    Arguments:
        images_path: subtitle image directory
        tmp_path: directory for new validation data and output
    Returns:
        isolated validation session
    """
    session = OcrValidationSession.from_dir_path(
        images_path,
        validation_data_dir_path=tmp_path / "validation",
        outfile_path=tmp_path / "validated.srt",
    )
    clear_validation_data(session)
    return session
