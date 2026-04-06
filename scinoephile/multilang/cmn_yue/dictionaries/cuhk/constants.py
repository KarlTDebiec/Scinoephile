#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Constants used by the CUHK dictionary."""

from __future__ import annotations

import re

from scinoephile.core.dictionaries import DictionarySource
from scinoephile.core.paths import get_runtime_cache_dir_path

DEFAULT_DATABASE_PATH = get_runtime_cache_dir_path("dictionaries", "cuhk") / "cuhk.db"
MAX_LOOKUP_LIMIT = 400

BASE_URL = "https://apps.itsc.cuhk.edu.hk/hanyu/Page/"
TERMS_URL = "https://apps.itsc.cuhk.edu.hk/hanyu/Page/Terms.aspx"
CUHK_HOSTNAME = "apps.itsc.cuhk.edu.hk"
CUHK_TERMS_PATH = "/hanyu/Page/Terms.aspx"
CUHK_WORD_PATH = "/hanyu/Page/Word.aspx"
CUHK_SEARCH_PATH = "/hanyu/Page/Search.aspx"
CUHK_WORD_RESULT_PATHS = {CUHK_WORD_PATH, CUHK_SEARCH_PATH}
INVALID_FILENAME_CHARS_REGEX = re.compile(r"[\\/:*?\"<>|]")

PRIVATE_USE_AREA_REPLACEMENT_STRING = "☒"
LABEL_ID_REGEX = re.compile(r"MainContent_repeaterRecord_lbl詞彙類別_.*")
JYUTPING_LETTERS_ID_REGEX = re.compile(r"MainContent_repeaterRecord_lbl粵語拼音_.*")
JYUTPING_NUMBERS_ID_REGEX = re.compile(r"MainContent_repeaterRecord_lbl聲調_.*")
JYUTPING_NUMBERS_REGEX = re.compile(r"(?:\d\*)*(\d+)")
MEANING_ID_REGEX = re.compile(
    r"MainContent_repeaterRecord_repeaterTranslation_\d+_lblTranslation_.*"
)
REMARK_ID_REGEX = re.compile(r"MainContent_repeaterRecord_lblRemark_.*")
JYUTPING_TONE_MAP = {"7": "1", "8": "3", "9": "6"}

CUHK_SOURCE = DictionarySource(
    name="現代標準漢語與粵語對照資料庫",
    shortname="CUHK",
    version="2014",
    description=(
        "Comparative Database of Modern Standard Chinese and Cantonese "
        "(Chinese University of Hong Kong)."
    ),
    legal="(c) 2014 保留版權 香港中文大學 中國語言及文學系",
    link="https://apps.itsc.cuhk.edu.hk/hanyu/Page/Cover.aspx",
    update_url="",
    other="words",
)

__all__ = [
    "BASE_URL",
    "CUHK_HOSTNAME",
    "CUHK_SEARCH_PATH",
    "CUHK_SOURCE",
    "CUHK_TERMS_PATH",
    "CUHK_WORD_PATH",
    "CUHK_WORD_RESULT_PATHS",
    "DEFAULT_DATABASE_PATH",
    "INVALID_FILENAME_CHARS_REGEX",
    "JYUTPING_LETTERS_ID_REGEX",
    "JYUTPING_NUMBERS_ID_REGEX",
    "JYUTPING_NUMBERS_REGEX",
    "JYUTPING_TONE_MAP",
    "LABEL_ID_REGEX",
    "MAX_LOOKUP_LIMIT",
    "MEANING_ID_REGEX",
    "PRIVATE_USE_AREA_REPLACEMENT_STRING",
    "REMARK_ID_REGEX",
    "TERMS_URL",
]
