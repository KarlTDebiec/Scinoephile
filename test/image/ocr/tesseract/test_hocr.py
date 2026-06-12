#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Tesseract hOCR parsing."""

from __future__ import annotations

from scinoephile.image.ocr.tesseract.hocr import (
    parse_tesseract_hocr,
    transfer_tesseract_hocr_italics,
)


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


def test_parse_tesseract_hocr_supports_empty_word_separator():
    """Test hOCR parser can join word spans without spaces."""
    hocr = """
    <span class='ocr_line' id='line_1'>
      <span class='ocrx_word' id='word_1'>在</span>
      <span class='ocrx_word' id='word_2'>麦</span>
      <span class='ocrx_word' id='word_3'>太</span>
    </span>
    """

    assert parse_tesseract_hocr(hocr, word_separator="") == "在麦太"


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


def test_parse_tesseract_hocr_collapses_adjacent_italic_words():
    """Test hOCR parser includes separators between adjacent italic words."""
    hocr = """
    <span class='ocr_line' id='line_1'>
      <span class='ocrx_word' id='word_1'><em>Gusteau's</em></span>
      <span class='ocrx_word' id='word_2'><em>restaurant</em></span>
      <span class='ocrx_word' id='word_3'>is</span>
      <span class='ocrx_word' id='word_4'><em>booked</em></span>
      <span class='ocrx_word' id='word_5'><em>solid.</em></span>
    </span>
    """

    assert parse_tesseract_hocr(hocr) == (
        "<i>Gusteau's restaurant</i> is <i>booked solid.</i>"
    )


def test_parse_tesseract_hocr_detects_italic_font_metadata():
    """Test hOCR parser detects Tesseract italic font metadata."""
    hocr = """
    <span class='ocr_line' id='line_1'>
      <span class='ocrx_word' id='word_1'
            title='bbox 0 0 20 20; x_font URW_Bookman_L_Italic; x_fsize 57'>
        music
      </span>
    </span>
    """

    assert parse_tesseract_hocr(hocr) == "<i>music</i>"


def test_parse_tesseract_hocr_decodes_entities_once():
    """Test hOCR parser does not double-decode entities."""
    hocr = """
    <span class='ocr_line' id='line_1'>
      <span class='ocrx_word' id='word_1'>&amp;lt;tag&amp;gt;</span>
    </span>
    """

    assert parse_tesseract_hocr(hocr) == "&lt;tag&gt;"


def test_transfer_tesseract_hocr_italics_applies_legacy_emphasis():
    """Test legacy hOCR emphasis can be applied to primary hOCR text."""
    primary_hocr = """
    <span class='ocr_line' id='line_1'>
      <span class='ocrx_word' id='word_1'>Hey,</span>
      <span class='ocrx_word' id='word_2'>let's</span>
      <span class='ocrx_word' id='word_3'>go</span>
    </span>
    """
    legacy_hocr = """
    <span class='ocr_line' id='line_1'>
      <span class='ocrx_word' id='word_1'><em>Hey,</em></span>
      <span class='ocrx_word' id='word_2'>let's</span>
      <span class='ocrx_word' id='word_3'>go</span>
    </span>
    """

    assert transfer_tesseract_hocr_italics(primary_hocr, legacy_hocr) == (
        "<i>Hey,</i> let's go"
    )


def test_transfer_tesseract_hocr_italics_collapses_adjacent_words():
    """Test transferred italics include spaces between adjacent italic words."""
    primary_hocr = """
    <span class='ocr_line' id='line_1'>
      <span class='ocrx_word' id='word_1'>booked</span>
      <span class='ocrx_word' id='word_2'>five</span>
      <span class='ocrx_word' id='word_3'>months</span>
      <span class='ocrx_word' id='word_4'>in</span>
      <span class='ocrx_word' id='word_5'>advance.</span>
    </span>
    """
    legacy_hocr = """
    <span class='ocr_line' id='line_1'>
      <span class='ocrx_word' id='word_1'><em>booked</em></span>
      <span class='ocrx_word' id='word_2'>five</span>
      <span class='ocrx_word' id='word_3'><em>months</em></span>
      <span class='ocrx_word' id='word_4'><em>in</em></span>
      <span class='ocrx_word' id='word_5'><em>advance.</em></span>
    </span>
    """

    assert transfer_tesseract_hocr_italics(primary_hocr, legacy_hocr) == (
        "<i>booked</i> five <i>months in advance.</i>"
    )


def test_transfer_tesseract_hocr_italics_ignores_mismatched_legacy_text():
    """Test legacy emphasis is not copied across mismatched OCR text."""
    primary_hocr = """
    <span class='ocr_line' id='line_1'>
      <span class='ocrx_word' id='word_1'>Hey,</span>
      <span class='ocrx_word' id='word_2'>let's</span>
      <span class='ocrx_word' id='word_3'>go</span>
    </span>
    """
    legacy_hocr = """
    <span class='ocr_line' id='line_1'>
      <span class='ocrx_word' id='word_1'><em>Pawn</em></span>
      <span class='ocrx_word' id='word_2'>let's</span>
      <span class='ocrx_word' id='word_3'>go</span>
    </span>
    """

    assert transfer_tesseract_hocr_italics(primary_hocr, legacy_hocr) == (
        "Hey, let's go"
    )


def test_transfer_tesseract_hocr_italics_ignores_partial_word_matches():
    """Test legacy emphasis is not copied across partial word matches."""
    primary_hocr = """
    <span class='ocr_line' id='line_1'>
      <span class='ocrx_word' id='word_1'>Hey,</span>
      <span class='ocrx_word' id='word_2'>let's</span>
      <span class='ocrx_word' id='word_3'>go</span>
    </span>
    """
    legacy_hocr = """
    <span class='ocr_line' id='line_1'>
      <span class='ocrx_word' id='word_1'><em>Hella</em></span>
      <span class='ocrx_word' id='word_2'>let's</span>
      <span class='ocrx_word' id='word_3'>go</span>
    </span>
    """

    assert transfer_tesseract_hocr_italics(primary_hocr, legacy_hocr) == (
        "Hey, let's go"
    )
