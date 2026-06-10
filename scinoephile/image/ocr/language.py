#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""OCR engine language code conversion."""

from __future__ import annotations

from scinoephile.core import Language

__all__ = [
    "get_lens_language_code",
    "get_paddle_language_code",
    "get_tesseract_language_code",
]


def get_lens_language_code(language: Language) -> str:
    """Get the Google Lens language code.

    Arguments:
        language: Scinoephile language
    Returns:
        Google Lens language code
    Raises:
        ValueError: if language is not supported by Google Lens OCR
    """
    if language is Language.eng:
        return "en"
    if language is Language.zho_hans:
        return "zh-CN"
    if language is Language.zho_hant:
        return "zh-TW"
    raise ValueError(f"{language} is not supported by Google Lens OCR")


def get_paddle_language_code(language: Language) -> str:
    """Get the PaddleOCR language code.

    Arguments:
        language: Scinoephile language
    Returns:
        PaddleOCR language code
    Raises:
        ValueError: if language is not supported by PaddleOCR
    """
    if language is Language.eng:
        return "en"
    if language is Language.zho_hans:
        return "ch"
    if language is Language.zho_hant:
        return "chinese_cht"
    raise ValueError(f"{language} is not supported by PaddleOCR")


def get_tesseract_language_code(language: Language) -> str:
    """Get the Tesseract language code.

    Arguments:
        language: Scinoephile language
    Returns:
        Tesseract language code
    Raises:
        ValueError: if language is not supported by Tesseract OCR
    """
    if language is Language.eng:
        return "eng"
    if language is Language.zho_hans:
        return "chi_sim"
    if language is Language.zho_hant:
        return "chi_tra"
    raise ValueError(f"{language} is not supported by Tesseract OCR")
