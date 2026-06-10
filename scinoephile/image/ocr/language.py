#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""OCR engine language code conversion."""

from __future__ import annotations

from scinoephile.core import Language

__all__ = ["get_tesseract_language_code"]


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
