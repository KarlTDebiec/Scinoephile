#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to standard Chinese text conversion."""

from __future__ import annotations

from collections.abc import Iterable
from copy import deepcopy
from functools import cache

from opencc import OpenCC

from scinoephile.core.script import SIMPLIFIED_CONFIGS, OpenCCConfig
from scinoephile.core.subtitles import Series

__all__ = [
    "S2HK_EXCLUSIONS",
    "T2S_EXCLUSIONS",
    "get_zho_character_variants",
    "get_zho_converted",
    "get_zho_converter",
    "get_zho_text_converted",
]

S2HK_EXCLUSIONS: set[str] = {
    "吓",  # 嚇
    "响",  # 響
    "床",  # 牀
    "扑",  # 撲
    "搵",  # 揾
    "晒",  # 曬
    "群",  # 羣
    "萬里長城",  # 萬裏長城
    "說",  # 説
    "郁",  # 鬱
}
"""Text spans to preserve when converting simplified Chinese toward Hong Kong."""

T2S_EXCLUSIONS: set[str] = {
    "劏",  # 㓥
    "唓",  # 𪠳
    "嗰",  # 𠮶
    "餸",  # 𩠌
}
"""Text spans to preserve when converting traditional Chinese toward simplified."""


def get_zho_character_variants(texts: Iterable[str]) -> tuple[str, ...]:
    """Get characters and their simplified/traditional variants.

    Arguments:
        texts: text strings containing characters to expand
    Returns:
        sorted individual characters and their script variants
    """
    text = "".join(texts)
    variants = set(text)
    variants.update(get_zho_converter(OpenCCConfig.s2t).convert(text))
    variants.update(get_zho_converter(OpenCCConfig.t2s).convert(text))
    return tuple(sorted(variants))


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
def get_zho_converter(config: OpenCCConfig) -> OpenCC:
    """Get OpenCC converter for standard Chinese character set conversion.

    Arguments:
        config: OpenCC configuration
    Returns:
        OpenCC converter instance, from cache if available
    """
    return OpenCC(config.code)


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

    if apply_exclusions and config in SIMPLIFIED_CONFIGS:
        return _get_zho_text_converted_with_exclusions(text, converter, T2S_EXCLUSIONS)
    if apply_exclusions and config == OpenCCConfig.s2hk:
        return _get_zho_text_converted_with_exclusions(text, converter, S2HK_EXCLUSIONS)
    return converter.convert(text)


def _get_zho_text_converted_with_exclusions(
    text: str, converter: OpenCC, exclusions: set[str]
) -> str:
    """Convert text while applying longest-match source text exclusions.

    Arguments:
        text: text to convert
        converter: OpenCC converter
        exclusions: source text spans to preserve
    Returns:
        converted text
    """
    converted_parts: list[str] = []
    ordered_exclusions = sorted(exclusions, key=len, reverse=True)
    segment_start = 0
    index = 0

    while index < len(text):
        match = next(
            (source for source in ordered_exclusions if text.startswith(source, index)),
            None,
        )
        if match is None:
            index += 1
            continue

        source = match
        if segment_start < index:
            converted_parts.append(converter.convert(text[segment_start:index]))
        converted_parts.append(source)
        index += len(source)
        segment_start = index

    if segment_start < len(text):
        converted_parts.append(converter.convert(text[segment_start:]))

    return "".join(converted_parts)
