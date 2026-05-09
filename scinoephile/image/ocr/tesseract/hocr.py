#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""hOCR parsing for Tesseract OCR."""

from __future__ import annotations

from html.parser import HTMLParser

__all__ = ["parse_tesseract_hocr"]


class _TesseractHocrParser(HTMLParser):
    """Parser for Tesseract hOCR line and word spans."""

    def __init__(self):
        """Initialize."""
        super().__init__()
        self.lines: list[list[str]] = []
        self._current_line: list[str] | None = None
        self._current_word_parts: list[str] | None = None
        self._italic_depth = 0

    def handle_data(self, data: str):
        """Handle HTML text.

        Arguments:
            data: text content
        """
        if self._current_word_parts is not None:
            self._current_word_parts.append(data)

    def handle_endtag(self, tag: str):
        """Handle an HTML end tag.

        Arguments:
            tag: tag name
        """
        if tag == "em" and self._current_word_parts is not None:
            self._close_italic()
        elif tag == "span" and self._current_word_parts is not None:
            self._close_word()
        elif tag == "span" and self._current_line is not None:
            self._close_line()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        """Handle an HTML start tag.

        Arguments:
            tag: tag name
            attrs: tag attributes
        """
        attr_by_name = dict(attrs)
        classes = set((attr_by_name.get("class") or "").split())
        if tag == "span" and {"ocr_line", "ocr_header"} & classes:
            self._current_line = []
        elif tag == "span" and "ocrx_word" in classes:
            self._current_word_parts = []
        elif tag == "em" and self._current_word_parts is not None:
            self._open_italic()

    def _close_italic(self):
        """Close the current italic tag."""
        if self._current_word_parts is None:
            return

        if self._italic_depth > 0:
            self._italic_depth -= 1
            self._current_word_parts.append("</i>")

    def _close_line(self):
        """Close the current hOCR line."""
        if self._current_line:
            self.lines.append(self._current_line)
        self._current_line = None

    def _close_word(self):
        """Close the current hOCR word."""
        if self._current_word_parts is None:
            return

        while self._italic_depth > 0:
            self._close_italic()
        word = "".join(self._current_word_parts).strip()
        if word and self._current_line is not None:
            self._current_line.append(word)
        self._current_word_parts = None

    def _open_italic(self):
        """Open an italic tag."""
        if self._current_word_parts is None:
            return

        self._italic_depth += 1
        self._current_word_parts.append("<i>")


def parse_tesseract_hocr(html: str) -> str:
    """Parse Tesseract hOCR into subtitle text.

    Arguments:
        html: hOCR HTML
    Returns:
        recognized text with ASS/SRT newline escapes
    """
    parser = _TesseractHocrParser()
    parser.feed(html)
    lines = [" ".join(line) for line in parser.lines]
    return "\\N".join(line.strip() for line in lines if line.strip())
