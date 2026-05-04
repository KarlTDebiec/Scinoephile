#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Constants used by the Kaifangcidian dictionary."""

from __future__ import annotations

from scinoephile.common import package_root
from scinoephile.core.dictionaries import DictionarySource

MAX_LOOKUP_LIMIT = 400

KAIFANGCIDIAN_BASE_URL = "https://www.kaifangcidian.com/yue/js"
KAIFANGCIDIAN_LICENSE_URL = "https://www.kaifangcidian.com/yue/cc/"
KAIFANGCIDIAN_SITE_URL = "https://www.kaifangcidian.com/han/yue"
KAIFANGCIDIAN_HZSG_URL = f"{KAIFANGCIDIAN_BASE_URL}/hzsg.js"
KAIFANGCIDIAN_JPSG_URL = f"{KAIFANGCIDIAN_BASE_URL}/jpsg.js"
KAIFANGCIDIAN_LG_URL = f"{KAIFANGCIDIAN_BASE_URL}/lg.js"

KAIFANGCIDIAN_LOCAL_DATA_DIR_PATH = package_root / "data/dictionaries/kaifangcidian"
KAIFANGCIDIAN_LOCAL_CSV_PATH = KAIFANGCIDIAN_LOCAL_DATA_DIR_PATH / "entries.csv"

KAIFANGCIDIAN_SOURCE = DictionarySource(
    name="開放粵語詞典",
    shortname="KFCD",
    version="website snapshot",
    description=(
        "Data derived from Kaifangcidian website dictionary JavaScript payloads."
    ),
    legal=(
        "Kaifangcidian resources are published under CC BY 3.0 unless otherwise "
        "noted; attribution and license link are required."
    ),
    link=KAIFANGCIDIAN_SITE_URL,
    update_url=KAIFANGCIDIAN_SITE_URL,
    other="website-js-export",
)

__all__ = [
    "KAIFANGCIDIAN_HZSG_URL",
    "KAIFANGCIDIAN_JPSG_URL",
    "KAIFANGCIDIAN_LICENSE_URL",
    "KAIFANGCIDIAN_LG_URL",
    "KAIFANGCIDIAN_LOCAL_CSV_PATH",
    "KAIFANGCIDIAN_LOCAL_DATA_DIR_PATH",
    "KAIFANGCIDIAN_SITE_URL",
    "KAIFANGCIDIAN_SOURCE",
    "MAX_LOOKUP_LIMIT",
]
