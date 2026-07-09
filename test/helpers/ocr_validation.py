#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared helpers for OCR validation tests."""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from pytest import MonkeyPatch

from scinoephile.image.bbox import Bbox
from scinoephile.web.ocr_validation.session import OcrValidationSession

__all__ = [
    "clear_validation_data",
    "make_ocr_html_dir",
    "make_two_image_ocr_html_dir",
    "patch_ocr_validation_bboxes",
    "prepared_gap_session",
]


def clear_validation_data(session: OcrValidationSession):
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


def make_ocr_html_dir(
    tmp_path: Path,
    *,
    text: str,
    image_pixels: list[tuple[int, int]] | None = None,
) -> Path:
    """Create an OCR image HTML directory with one subtitle image.

    Arguments:
        tmp_path: pytest temporary directory path
        text: HTML subtitle text content
        image_pixels: optional LA pixels for the generated subtitle image
    Returns:
        OCR image HTML directory path
    """
    html_dir_path = tmp_path / "image"
    html_dir_path.mkdir()
    image = Image.new("LA", (2, 2))
    if image_pixels is None:
        image_pixels = [(255, 255), (0, 255), (255, 255), (0, 255)]
    image.putdata(image_pixels)
    image.save(html_dir_path / "0001.png")
    _write_html_index(
        html_dir_path,
        [
            (
                1,
                "1,000",
                "2,000",
                "0001.png",
                text,
            )
        ],
    )
    return html_dir_path


def make_two_image_ocr_html_dir(tmp_path: Path, *, text_1: str, text_2: str) -> Path:
    """Create an OCR image HTML directory with two subtitle images.

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
    _write_html_index(
        html_dir_path,
        [
            (1, "1,000", "2,000", "0001.png", text_1),
            (2, "3,000", "4,000", "0002.png", text_2),
        ],
    )
    return html_dir_path


def patch_ocr_validation_bboxes(
    monkeypatch: MonkeyPatch,
    bboxes: list[Bbox],
    *,
    target: str = "scinoephile.web.ocr_validation.session.get_bboxes",
):
    """Patch OCR validation bbox detection to return fixed bboxes.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        bboxes: bboxes to return from the patched detector
        target: import path to patch
    """

    def get_bboxes(image: Image.Image) -> list[Bbox]:
        """Return configured bboxes."""
        _ = image
        return list(bboxes)

    monkeypatch.setattr(target, get_bboxes)


def prepared_gap_session(
    html_dir_path: Path,
    tmp_path: Path,
    *,
    char_1: str = "A",
    char_2: str = "B",
    cutoffs: tuple[int, int, int, int] = (2, 6, 12, 20),
) -> OcrValidationSession:
    """Create a session prepared to reach gap validation.

    Arguments:
        html_dir_path: OCR image HTML directory path
        tmp_path: pytest temporary directory path
        char_1: first character in the validated pair
        char_2: second character in the validated pair
        cutoffs: gap cutoffs for the character pair
    Returns:
        prepared OCR validation session
    """
    session = OcrValidationSession.from_dir_path(
        html_dir_path,
        cache_dir_path=tmp_path / "cache",
    )
    clear_validation_data(session)
    session.manager.char_dims_by_n[1][char_1] = {(10, 20)}
    session.manager.char_dims_by_n[1][char_2] = {(10, 20)}
    session.manager.char_pair_gaps[(char_1, char_2)] = cutoffs
    return session


def _write_html_index(html_dir_path: Path, rows: list[tuple[int, str, str, str, str]]):
    """Write an OCR image HTML index.

    Arguments:
        html_dir_path: OCR image HTML directory path
        rows: subtitle rows as number, start, end, image name, and text
    """
    body_rows: list[str] = []
    for number, start, end, image_name, text in rows:
        body_rows.append(
            f"#{number}:{start}->{end}"
            "<div>"
            f"<img src='{image_name}' />"
            "<br /><div>"
            f"{text}</div></div><br /><hr />"
        )
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
                *body_rows,
                "</body>",
                "</html>",
            ]
        ),
        encoding="utf-8",
    )
