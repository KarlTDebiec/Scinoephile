#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Constants used by the Wiktionary dictionary."""

from __future__ import annotations

from scinoephile.common import package_root
from scinoephile.core.dictionaries import DictionarySource

MAX_LOOKUP_LIMIT = 400

WIKTIONARY_SITE_URL = "https://en.wiktionary.org/wiki/Wiktionary:Main_Page"
WIKTIONARY_KAIKKI_URL = "https://kaikki.org/dictionary/Chinese/"
WIKTIONARY_KAIKKI_JSONL_URL = (
    "https://kaikki.org/dictionary/Chinese/kaikki.org-dictionary-Chinese.jsonl"
)
WIKTIONARY_LICENSE_URL = "https://en.wiktionary.org/wiki/Wiktionary:Copyrights#Creative_Commons_Attribution-ShareAlike_4.0_International_License"

WIKTIONARY_LOCAL_DATA_DIR_PATH = package_root / "data/dictionaries/wiktionary"
WIKTIONARY_LOCAL_JSONL_PATH = WIKTIONARY_LOCAL_DATA_DIR_PATH / "entries.jsonl"

WIKTIONARY_SOURCE = DictionarySource(
    name="Wiktionary (Kaikki Chinese dump)",
    shortname="WKT",
    version="Kaikki snapshot",
    description=(
        "Data derived from Kaikki JSONL exports of Chinese entries from Wiktionary."
    ),
    legal=(
        "Wiktionary content is available under CC BY-SA; attribution and share-alike "
        "requirements apply."
    ),
    link=WIKTIONARY_SITE_URL,
    update_url=WIKTIONARY_KAIKKI_URL,
    other="kaikki-jsonl-first-pass",
)

__all__ = [
    "MAX_LOOKUP_LIMIT",
    "WIKTIONARY_KAIKKI_URL",
    "WIKTIONARY_KAIKKI_JSONL_URL",
    "WIKTIONARY_LICENSE_URL",
    "WIKTIONARY_LOCAL_DATA_DIR_PATH",
    "WIKTIONARY_LOCAL_JSONL_PATH",
    "WIKTIONARY_SITE_URL",
    "WIKTIONARY_SOURCE",
]
