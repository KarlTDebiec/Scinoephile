#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Tesseract hOCR parsing."""

from __future__ import annotations

from scinoephile.image.ocr.tesseract.hocr import parse_tesseract_hocr


def test_parse_tesseract_hocr_extracts_words_by_line():
    """Test hOCR parser extracts word text line by line."""
    hocr = """
    <span class='ocr_line' id='line_1'>
      <span class='ocrx_word' id='word_1'>Hello</span>
      <span class='ocrx_word' id='word_2'>world</span>
    </span>
    <span class='ocr_line' id='line_2'>
      <span class='ocrx_word' id='word_3'>Again</span>
    </span>
    """

    assert parse_tesseract_hocr(hocr) == "Hello world\\NAgain"


def test_parse_tesseract_hocr_decodes_entities_and_keeps_italics():
    """Test hOCR parser decodes entities and normalizes emphasis tags."""
    hocr = """
    <span class='ocr_line' id='line_1'>
      <span class='ocrx_word' id='word_1'><em>Tom</em></span>
      <span class='ocrx_word' id='word_2'>&amp;</span>
      <span class='ocrx_word' id='word_3'>Jerry&#39;s</span>
    </span>
    """

    assert parse_tesseract_hocr(hocr) == "<i>Tom</i> & Jerry's"


def test_parse_tesseract_hocr_decodes_entities_once():
    """Test hOCR parser does not double-decode entities."""
    hocr = """
    <span class='ocr_line' id='line_1'>
      <span class='ocrx_word' id='word_1'>&amp;lt;tag&amp;gt;</span>
    </span>
    """

    assert parse_tesseract_hocr(hocr) == "&lt;tag&gt;"
