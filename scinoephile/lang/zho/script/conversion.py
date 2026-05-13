#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to standard Chinese text conversion."""

from __future__ import annotations

from copy import deepcopy
from functools import cache

from opencc import OpenCC

from scinoephile.common.described_enum import DescribedEnum
from scinoephile.core.subtitles import Series

__all__ = [
    "OpenCCConfig",
    "SIMPLIFIED_CONFIGS",
    "TRADITIONAL_CONFIGS",
    "get_zho_converted",
    "get_zho_converter",
    "get_zho_text_converted",
]

_conversion_exclusions = {
    "嗰": "𠮶",
    "纔": "才",
    "喫": "吃",
    "臺": "台",
    "嚇": "吓",
    "牀": "床",
    "註": "注",
    "裏": "里",
    "託": "托",
    "瞭": "了",
    "剋": "克",
    "夥": "伙",
    "製": "制",
}
"""Characters for which OpenCC's conversion is undesirable in this package."""


class OpenCCConfig(DescribedEnum):
    """OpenCC configuration names for standard Chinese character set conversion."""

    s2t = ("s2t", "Simplified Chinese to Traditional Chinese.")
    """Simplified Chinese to Traditional Chinese."""
    t2s = ("t2s", "Traditional Chinese to Simplified Chinese.")
    """Traditional Chinese to Simplified Chinese."""
    s2tw = ("s2tw", "Simplified Chinese to Traditional Chinese (Taiwan).")
    """Simplified Chinese to Traditional Chinese for Taiwan."""
    tw2s = ("tw2s", "Traditional Chinese (Taiwan) to Simplified Chinese.")
    """Traditional Chinese for Taiwan to Simplified Chinese."""
    s2hk = ("s2hk", "Simplified Chinese to Traditional Chinese (Hong Kong).")
    """Simplified Chinese to Traditional Chinese for Hong Kong."""
    hk2s = ("hk2s", "Traditional Chinese (Hong Kong) to Simplified Chinese.")
    """Traditional Chinese for Hong Kong to Simplified Chinese."""
    s2twp = (
        "s2twp",
        "Simplified Chinese to Traditional Chinese (Taiwan) with Taiwanese idiom.",
    )
    """Simplified Chinese to Traditional Chinese for Taiwan with Taiwanese idiom."""
    tw2sp = (
        "tw2sp",
        "Traditional Chinese (Taiwan) to Simplified Chinese with Mainland idiom.",
    )
    """Traditional Chinese for Taiwan to Simplified Chinese with Mainland idiom."""
    t2tw = ("t2tw", "Traditional Chinese (OpenCC) to Taiwan Standard.")
    """Traditional Chinese in OpenCC standard to Taiwan standard."""
    hk2t = ("hk2t", "Traditional Chinese (Hong Kong) to Traditional Chinese.")
    """Traditional Chinese for Hong Kong to Traditional Chinese."""
    t2hk = ("t2hk", "Traditional Chinese (OpenCC) to Hong Kong variant.")
    """Traditional Chinese in OpenCC standard to Hong Kong variant."""
    t2jp = (
        "t2jp",
        "Traditional Chinese Characters (Kyujitai) to New Japanese Kanji (Shinjitai).",
    )
    """Traditional Chinese characters to new Japanese kanji."""
    jp2t = (
        "jp2t",
        "New Japanese Kanji (Shinjitai) to Traditional Chinese Characters (Kyujitai).",
    )
    """New Japanese kanji to traditional Chinese characters."""
    tw2t = ("tw2t", "Traditional Chinese (Taiwan) to Traditional Chinese.")
    """Traditional Chinese for Taiwan to Traditional Chinese."""


SIMPLIFIED_CONFIGS = {
    OpenCCConfig.t2s,
    OpenCCConfig.tw2s,
    OpenCCConfig.hk2s,
    OpenCCConfig.tw2sp,
}
"""OpenCC configurations that convert text toward simplified Chinese."""

TRADITIONAL_CONFIGS = {
    OpenCCConfig.s2t,
    OpenCCConfig.s2tw,
    OpenCCConfig.s2hk,
    OpenCCConfig.s2twp,
    OpenCCConfig.t2tw,
    OpenCCConfig.hk2t,
    OpenCCConfig.t2hk,
    OpenCCConfig.tw2t,
    OpenCCConfig.t2jp,
    OpenCCConfig.jp2t,
}
"""OpenCC configurations that convert text toward traditional Chinese."""


def get_zho_converted(
    series: Series,
    config: OpenCCConfig = OpenCCConfig.t2s,
    apply_exclusions: bool = True,
) -> Series:
    """Get standard Chinese converted between character sets.

    Arguments:
        series: Series to convert
        config: OpenCC configuration
        apply_exclusions: whether to apply conversion exclusions
    Returns:
        converted series
    """
    series = deepcopy(series)
    for event in series:
        event.text = get_zho_text_converted(
            event.text, config, apply_exclusions=apply_exclusions
        )
    return series


@cache
def get_zho_converter(config: OpenCCConfig | str) -> OpenCC:
    """Get OpenCC converter for standard Chinese character set conversion.

    Arguments:
        config: OpenCC configuration
    Returns:
        OpenCC converter instance, from cache if available
    """
    config_code = config.code if isinstance(config, OpenCCConfig) else config
    return OpenCC(config_code)


def get_zho_text_converted(
    text: str, config: OpenCCConfig, apply_exclusions: bool = True
) -> str:
    """Get standard Chinese text converted between character sets.

    Arguments:
        text: text to convert
        config: OpenCC configuration for conversion
        apply_exclusions: whether to apply conversion exclusions
    Returns:
        converted text
    """
    converter = get_zho_converter(config)
    converted_text = converter.convert(text)

    if apply_exclusions:
        if config in SIMPLIFIED_CONFIGS:
            for trad_char, simp_char in _conversion_exclusions.items():
                if trad_char in text and simp_char in converted_text:
                    converted_text = converted_text.replace(simp_char, trad_char)
        if config in TRADITIONAL_CONFIGS:
            for trad_char, simp_char in _conversion_exclusions.items():
                if simp_char in text and trad_char in converted_text:
                    converted_text = converted_text.replace(trad_char, simp_char)

    return converted_text
