#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Constants used by the GZZJ dictionary."""

from __future__ import annotations

from scinoephile.dictionaries import DictionarySource

MAX_LOOKUP_LIMIT = 400

GZZJ_DOWNLOAD_URL = (
    "https://github.com/jyutnet/cantonese-books-data/tree/master/"
    "2004_%E5%BB%A3%E5%B7%9E%E8%A9%B1%E6%AD%A3%E9%9F%B3%E5%AD%97%E5%85%B8"
)

GZZJ_SOURCE = DictionarySource(
    name="廣州話正音字典",
    shortname="GZZJ",
    version="2004 第二版",
    description=(
        "Digital data derived from the 2004 second edition of 《廣州話正音字典》."
    ),
    legal=(
        "Users must obtain the upstream B01_資料.json file themselves; "
        "Scinoephile does not redistribute the source data."
    ),
    link=GZZJ_DOWNLOAD_URL,
    update_url=GZZJ_DOWNLOAD_URL,
    other="words",
)

__all__ = [
    "GZZJ_DOWNLOAD_URL",
    "GZZJ_SOURCE",
    "MAX_LOOKUP_LIMIT",
]
