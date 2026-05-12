#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""hOCR parsing for Tesseract OCR."""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from html.parser import HTMLParser

__all__ = [
    "TesseractHocrWord",
    "parse_tesseract_hocr",
    "parse_tesseract_hocr_words",
    "transfer_tesseract_hocr_italics",
]


@dataclass(frozen=True)
class TesseractHocrWord:
    """A word parsed from Tesseract hOCR."""

    text: str
    """Recognized word text."""

    italic: bool = False
    """Whether the word was marked as italic."""


@dataclass(frozen=True)
class _TesseractHocrWordSpan:
    """A parsed hOCR word with its location in formatted text."""

    text: str
    """Recognized word text."""

    start: int
    """Start index in formatted text."""

    end: int
    """End index in formatted text."""

    italic: bool = False
    """Whether the word was marked as italic."""


class _TesseractHocrParser(HTMLParser):
    """Parser for Tesseract hOCR line and word spans."""

    def __init__(self):
        """Initialize."""
        super().__init__()
        self.lines: list[list[TesseractHocrWord]] = []
        self._current_line: list[TesseractHocrWord] | None = None
        self._current_word_italic = False
        self._current_word_parts: list[str] | None = None
        self._italic_depth = 0

    def handle_data(self, data: str):
        """Handle HTML text.

        Arguments:
            data: text content
        """
        if self._current_word_parts is not None:
            self._current_word_parts.append(data)
            if self._italic_depth > 0 and data.strip():
                self._current_word_italic = True

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
            self._current_word_italic = _title_indicates_italic(
                attr_by_name.get("title")
            )
        elif tag == "em" and self._current_word_parts is not None:
            self._open_italic()

    def _close_italic(self):
        """Close the current italic tag."""
        if self._current_word_parts is None:
            return

        if self._italic_depth > 0:
            self._italic_depth -= 1

    def _close_line(self):
        """Close the current hOCR line."""
        if self._current_line:
            self.lines.append(self._current_line)
        self._current_line = None

    def _close_word(self):
        """Close the current hOCR word."""
        if self._current_word_parts is None:
            return

        self._italic_depth = 0
        word = "".join(self._current_word_parts).strip()
        if word and self._current_line is not None:
            self._current_line.append(
                TesseractHocrWord(word, italic=self._current_word_italic)
            )
        self._current_word_parts = None
        self._current_word_italic = False

    def _open_italic(self):
        """Open an italic tag."""
        if self._current_word_parts is None:
            return

        self._italic_depth += 1


def parse_tesseract_hocr(html: str, *, word_separator: str = " ") -> str:
    """Parse Tesseract hOCR into subtitle text.

    Arguments:
        html: hOCR HTML
        word_separator: text with which to join hOCR word spans
    Returns:
        recognized text with ASS/SRT newline escapes
    """
    return _format_tesseract_hocr_words(
        parse_tesseract_hocr_words(html),
        word_separator=word_separator,
    )


def parse_tesseract_hocr_words(html: str) -> list[list[TesseractHocrWord]]:
    """Parse Tesseract hOCR into line-grouped words.

    Arguments:
        html: hOCR HTML
    Returns:
        line-grouped recognized words
    """
    parser = _TesseractHocrParser()
    parser.feed(html)
    return parser.lines


def transfer_tesseract_hocr_italics(primary_html: str, legacy_html: str) -> str:
    """Transfer legacy hOCR italics onto primary hOCR text.

    Italics are copied only for exact character matches in the alignment, so
    poor legacy OCR cannot mark unrelated primary text as italic.

    Arguments:
        primary_html: primary Tesseract hOCR HTML
        legacy_html: legacy-engine Tesseract hOCR HTML
    Returns:
        primary recognized text with transferred italic tags
    """
    primary_text, primary_words = _get_text_and_word_spans(
        parse_tesseract_hocr_words(primary_html)
    )
    _, legacy_words = _get_text_and_word_spans(parse_tesseract_hocr_words(legacy_html))
    primary_italic_mask = [False] * len(primary_text)
    primary_texts = [word.text for word in primary_words]
    legacy_texts = [word.text for word in legacy_words]
    matcher = SequenceMatcher(a=primary_texts, b=legacy_texts, autojunk=False)
    for (
        tag,
        primary_start,
        primary_end,
        legacy_start,
        legacy_end,
    ) in matcher.get_opcodes():
        if tag != "equal":
            continue
        for primary_index, legacy_index in zip(
            range(primary_start, primary_end),
            range(legacy_start, legacy_end),
            strict=True,
        ):
            legacy_word = legacy_words[legacy_index]
            if not legacy_word.italic:
                continue
            primary_word = primary_words[primary_index]
            primary_italic_mask[primary_word.start : primary_word.end] = [True] * (
                primary_word.end - primary_word.start
            )

    return _apply_italic_mask(primary_text, primary_italic_mask)


def _apply_italic_mask(text: str, italic_mask: list[bool]) -> str:
    """Apply an italic mask to text.

    Arguments:
        text: plain text
        italic_mask: character-level italic mask
    Returns:
        text with italic tags
    """
    parts: list[str] = []
    italic_open = False
    for character, italic in zip(text, italic_mask, strict=True):
        if italic and not italic_open:
            parts.append("<i>")
            italic_open = True
        elif not italic and italic_open:
            parts.append("</i>")
            italic_open = False
        parts.append(character)
    if italic_open:
        parts.append("</i>")
    return "".join(parts)


def _format_tesseract_hocr_words(
    lines: list[list[TesseractHocrWord]],
    *,
    word_separator: str = " ",
) -> str:
    """Format parsed hOCR words as subtitle text.

    Arguments:
        lines: line-grouped recognized words
        word_separator: text with which to join hOCR word spans
    Returns:
        recognized text with ASS/SRT newline escapes
    """
    formatted_lines = []
    for line in lines:
        formatted_words = []
        for word in line:
            if word.italic:
                formatted_words.append(f"<i>{word.text}</i>")
            else:
                formatted_words.append(word.text)
        line_text = word_separator.join(formatted_words).strip()
        if line_text:
            formatted_lines.append(line_text)
    return "\\N".join(formatted_lines)


def _get_text_and_word_spans(
    lines: list[list[TesseractHocrWord]],
) -> tuple[str, list[_TesseractHocrWordSpan]]:
    """Get formatted plain text and word spans.

    Arguments:
        lines: line-grouped recognized words
    Returns:
        plain text and word spans
    """
    text_parts: list[str] = []
    word_spans: list[_TesseractHocrWordSpan] = []
    text_length = 0
    for line_index, line in enumerate(lines):
        if line_index > 0:
            text_parts.append("\\N")
            text_length += 2
        for word_index, word in enumerate(line):
            if word_index > 0:
                text_parts.append(" ")
                text_length += 1
            start = text_length
            text_parts.append(word.text)
            text_length += len(word.text)
            word_spans.append(
                _TesseractHocrWordSpan(
                    text=word.text,
                    start=start,
                    end=start + len(word.text),
                    italic=word.italic,
                )
            )
    return "".join(text_parts), word_spans


def _title_indicates_italic(title: str | None) -> bool:
    """Determine whether Tesseract hOCR title metadata indicates italics.

    Arguments:
        title: hOCR title metadata
    Returns:
        whether title metadata indicates an italic font
    """
    if title is None:
        return False

    for field in title.split(";"):
        stripped_field = field.strip()
        if not stripped_field.startswith("x_font "):
            continue
        return "italic" in stripped_field.lower()
    return False
