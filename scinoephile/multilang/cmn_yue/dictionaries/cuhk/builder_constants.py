#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Constants shared by CUHK dictionary builder classes."""

from __future__ import annotations

import importlib
import re

from ..dictionary_source import DictionarySource

hkscs_converter = None
try:  # pragma: no cover - optional dependency
    hkscs_converter = importlib.import_module("hkscs_unicode_converter").converter
except ImportError:
    # Fallback to raw CUHK text when HK-SCS converter is unavailable.
    pass

BASE_URL = "https://apps.itsc.cuhk.edu.hk/hanyu/Page/"
TERMS_URL = "https://apps.itsc.cuhk.edu.hk/hanyu/Page/Terms.aspx"
CUHK_HOSTNAME = "apps.itsc.cuhk.edu.hk"
CUHK_TERMS_PATH = "/hanyu/Page/Terms.aspx"
CUHK_WORD_PATH = "/hanyu/Page/Word.aspx"
CUHK_SEARCH_PATH = "/hanyu/Page/Search.aspx"
CUHK_WORD_RESULT_PATHS = {CUHK_WORD_PATH, CUHK_SEARCH_PATH}

PRIVATE_USE_AREA_REGEX = re.compile(r"[\ue000-\uf8ff]")
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
INVALID_FILENAME_CHARS_REGEX = re.compile(r"[\\/:*?\"<>|]")

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
