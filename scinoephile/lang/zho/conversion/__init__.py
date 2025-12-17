#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to 中文 text conversion."""

from __future__ import annotations

from copy import deepcopy
from functools import cache

from opencc import OpenCC

from scinoephile.core.series import Series

from .opencc_config import OpenCCConfig

__all__ = [
    "OpenCCConfig",
    "get_zho_converted",
    "get_zho_converter",
    "get_zho_text_converted",
]

conversion_exclusions = {
    "嗰": "𠮶",
    "纔": "才",
    "喫": "吃",
}


def get_zho_converted(
    series: Series,
    config: OpenCCConfig = OpenCCConfig.t2s,
    apply_exclusions: bool = True,
) -> Series:
    """Get 中文 converted between character sets.

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
def get_zho_converter(config: OpenCCConfig) -> OpenCC:
    """Get OpenCC converter for 中文 character set conversion.

    Arguments:
        config: OpenCC configuration
    Returns:
        OpenCC converter instance, from cache if available
    """
    return OpenCC(config)


def get_zho_text_converted(
    text: str, config: OpenCCConfig, apply_exclusions: bool = True
) -> str:
    """Get 中文 text converted between character sets.

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
        if config in (
            OpenCCConfig.t2s,
            OpenCCConfig.tw2s,
            OpenCCConfig.hk2s,
            OpenCCConfig.tw2sp,
        ):
            for trad_char, simp_char in conversion_exclusions.items():
                if trad_char in text and simp_char in converted_text:
                    converted_text = converted_text.replace(simp_char, trad_char)
        if config in (
            OpenCCConfig.s2t,
            OpenCCConfig.s2tw,
            OpenCCConfig.s2hk,
            OpenCCConfig.s2twp,
        ):
            for trad_char, simp_char in conversion_exclusions.items():
                if simp_char in text and trad_char in converted_text:
                    converted_text = converted_text.replace(trad_char, simp_char)

    return converted_text
