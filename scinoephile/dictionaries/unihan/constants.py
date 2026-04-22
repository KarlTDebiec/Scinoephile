#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Constants used by the Unihan dictionary."""

from __future__ import annotations

from scinoephile.common import package_root
from scinoephile.dictionaries import DictionarySource

MAX_LOOKUP_LIMIT = 400

UNIHAN_SITE_URL = "https://www.unicode.org/charts/unihan.html"
UNIHAN_LICENSE_URL = "https://www.unicode.org/license.html"
UNIHAN_COPYRIGHT_URL = "https://www.unicode.org/copyright.html"
UNIHAN_ZIP_URL = "https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip"

UNIHAN_REQUIRED_SOURCE_FILENAMES: tuple[str, str, str] = (
    "Unihan_DictionaryLikeData.txt",
    "Unihan_Readings.txt",
    "Unihan_Variants.txt",
)

UNIHAN_LOCAL_DATA_DIR_PATH = package_root / "data" / "dictionaries" / "unihan"

UNIHAN_SOURCE = DictionarySource(
    name="Unihan Database",
    shortname="UNI",
    version="UCD latest snapshot",
    description=(
        "Data derived from Unicode Unihan files for variants, readings, and "
        "dictionary-like metadata."
    ),
    legal=(
        "Unicode data and software are subject to the Unicode Terms of Use and "
        "License Agreement."
    ),
    link=UNIHAN_SITE_URL,
    update_url=UNIHAN_ZIP_URL,
    other="variants-readings-cangjie",
)

__all__ = [
    "MAX_LOOKUP_LIMIT",
    "UNIHAN_COPYRIGHT_URL",
    "UNIHAN_LICENSE_URL",
    "UNIHAN_LOCAL_DATA_DIR_PATH",
    "UNIHAN_REQUIRED_SOURCE_FILENAMES",
    "UNIHAN_SITE_URL",
    "UNIHAN_SOURCE",
    "UNIHAN_ZIP_URL",
]
