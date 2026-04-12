#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared test cases for script and romanization detection helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DetectionCase:
    """Test case for script and romanization detection helpers.

    Attributes:
        text: input text to classify
        is_accented_pinyin: expected accented pinyin classification
        is_numbered_pinyin: expected numbered pinyin classification
        is_accented_yale: expected accented Yale classification
        is_numbered_jyutping: expected numbered Jyutping classification
        is_simplified: expected simplified Chinese classification
        is_traditional: expected traditional Chinese classification
    """

    text: str
    """Input text to classify."""

    is_accented_pinyin: bool
    """Expected accented pinyin classification."""

    is_numbered_pinyin: bool
    """Expected numbered pinyin classification."""

    is_accented_yale: bool
    """Expected accented Yale classification."""

    is_numbered_jyutping: bool
    """Expected numbered Jyutping classification."""

    is_simplified: bool
    """Expected simplified Chinese classification."""

    is_traditional: bool
    """Expected traditional Chinese classification."""


DETECTION_CASES: list[DetectionCase] = [
    DetectionCase(
        text="nǐ hǎo",
        is_accented_pinyin=True,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    DetectionCase(
        text="lüè",
        is_accented_pinyin=True,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    DetectionCase(
        text="ni3 hao3",
        is_accented_pinyin=False,
        is_numbered_pinyin=True,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    DetectionCase(
        text="lu:e4",
        is_accented_pinyin=False,
        is_numbered_pinyin=True,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    DetectionCase(
        text="lv4",
        is_accented_pinyin=False,
        is_numbered_pinyin=True,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    DetectionCase(
        text="ni hao",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    DetectionCase(
        text="néih hóu",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=True,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    DetectionCase(
        text="gwóngdūngwá",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=True,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    DetectionCase(
        text="nei5 hou2",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=True,
        is_simplified=False,
        is_traditional=False,
    ),
    DetectionCase(
        text="gwong2 dung1 waa2",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=True,
        is_simplified=False,
        is_traditional=False,
    ),
    DetectionCase(
        text="简体中文",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=True,
        is_traditional=False,
    ),
    DetectionCase(
        text="汉字",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=True,
        is_traditional=False,
    ),
    DetectionCase(
        text="繁體中文",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=True,
    ),
    DetectionCase(
        text="漢字",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=True,
    ),
    DetectionCase(
        text="中文",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=True,
        is_traditional=True,
    ),
    DetectionCase(
        text="",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
]
