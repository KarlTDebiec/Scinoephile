#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Chinese language tag helpers."""

from __future__ import annotations

__all__ = ["get_zho_script_language", "is_zho_language"]

_ZHO_LANGUAGE_CODES = {"chi", "zho", "yue"}
"""Language codes treated as Chinese for script analysis."""


def get_zho_script_language(language: str, script: str | None) -> str:
    """Return the language tag to use after Chinese script analysis.

    Arguments:
        language: original language tag
        script: detected Chinese script tag, if determined
    Returns:
        Chinese language tag with script information
    """
    if script is not None:
        return script
    return f"{language.split('-', 1)[0]}-Unknown"


def is_zho_language(language: str | None) -> bool:
    """Return whether a language tag should be treated as Chinese.

    Arguments:
        language: language tag, if available
    Returns:
        whether the language tag is Chinese
    """
    if language is None:
        return False
    return language.split("-", 1)[0].lower() in _ZHO_LANGUAGE_CODES
