#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Constants used by Scinoephile command-line interfaces."""

from __future__ import annotations

__all__ = [
    "DEFAULT_CLI_LOCALE",
    "LOCALE_ALIASES",
    "SUPPORTED_CLI_LOCALES",
]

DEFAULT_CLI_LOCALE = "en"
SUPPORTED_CLI_LOCALES = ("en", "zh-hans", "zh-hant")

LOCALE_ALIASES = {
    "c": "en",
    "en": "en",
    "en_us": "en",
    "en-us": "en",
    "english": "en",
    "zh": "zh-hans",
    "zh_cn": "zh-hans",
    "zh-cn": "zh-hans",
    "zh_hans": "zh-hans",
    "zh-hans": "zh-hans",
    "zh_sg": "zh-hans",
    "zh-hk": "zh-hant",
    "zh_hk": "zh-hant",
    "zh_mo": "zh-hant",
    "zh-mo": "zh-hant",
    "zh_tw": "zh-hant",
    "zh-tw": "zh-hant",
    "zh_hant": "zh-hant",
    "zh-hant": "zh-hant",
}
