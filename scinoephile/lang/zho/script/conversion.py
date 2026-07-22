#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to standard Chinese text conversion."""

from __future__ import annotations

from collections.abc import Iterable
from copy import deepcopy
from functools import cache

from opencc import OpenCC

from scinoephile.common.described_enum import DescribedEnum
from scinoephile.core.subtitles import Series

__all__ = [
    "OpenCCConfig",
    "S2T_EXCLUSIONS",
    "SIMPLIFIED_CONFIGS",
    "T2S_EXCLUSIONS",
    "TRADITIONAL_CONFIGS",
    "get_zho_character_variants",
    "get_zho_converted",
    "get_zho_converter",
    "get_zho_text_converted",
]

S2T_EXCLUSIONS: set[str] = {
    "吃",  # keep modern 吃; avoid literary 喫
    "吓",  # keep Cantonese 吓 particle/verb; avoid 嚇 "frighten"
    "晒",  # keep Cantonese 晒 result particle; avoid 曬 "sun-dry"
    "群",  # keep modern 群; avoid older variant 羣
    "床",  # keep modern 床; avoid older variant 牀
    "台",  # keep platform/stage/address 台; avoid 臺
    "痴",  # keep common 白痴 form 痴; avoid 癡
    "秘",  # keep modern 秘; avoid older variant 祕
    "虱",  # keep modern/Hong Kong 虱; avoid 蝨
    "峰",  # keep modern 峰; avoid older variant 峯
    "粽",  # keep modern/Hong Kong 粽; avoid 糉
    "卺",  # keep 合卺 form 卺; avoid rare variant 巹
    "皂",  # keep 青紅皂白 form 皂; avoid 皁
    "灶",  # keep modern 灶; avoid older variant 竈
    "唇",  # keep modern 唇; avoid 脣
    "岩",  # keep rock/Cantonese 岩; avoid blanket 巖
    "不准",  # permission sense in subtitles; avoid blanket 準
    "丑了",  # preserve subtitle idiom 丑大/丑了; avoid 醜陋 sense
    "丑大",  # preserve subtitle idiom 丑大/丑了; avoid 醜陋 sense
    "了解",  # modern 了解; avoid older 瞭解 in subtitles
    "才不",  # modern adverbial 才; avoid older 纔
    "才可",  # modern adverbial 才; avoid older 纔
    "才回",  # modern adverbial 才; avoid older 纔
    "才好",  # modern adverbial 才; avoid older 纔
    "才怪",  # modern adverbial 才; avoid older 纔
    "才跟",  # modern adverbial 才; avoid older 纔
    "才是",  # modern adverbial 才; avoid older 纔
    "才行",  # modern adverbial 才; avoid older 纔
    "才要",  # modern adverbial 才; avoid older 纔
    "才有",  # modern adverbial 才; avoid older 纔
    "合卺",  # fixed wedding term; avoid rare variant 巹
    "呢云",  # Cantonese OCR phrase; avoid weather/cloud 雲
    "克制",  # 克 is "restrain"; avoid 剋 "overcome/defeat"
    "准你",  # permission sense; avoid blanket 準
    "准用",  # permission sense; avoid blanket 準
    "准講",  # permission sense; avoid blanket 準
    "准打",  # permission sense; avoid blanket 準
    "准擅自",  # permission sense; avoid blanket 準
    "准再",  # permission sense; avoid blanket 準
    "准進入",  # permission sense; avoid blanket 準
    "准進",  # permission sense; avoid blanket 準
    "准許",  # permission sense; avoid blanket 準
    "准我",  # permission sense; avoid blanket 準
    "借助",  # 借 means "borrow/use"; avoid 藉 "by means of"
    "刮了",  # shaving/scraping sense; avoid 颳 "wind blows"
    "刮得",  # shaving/scraping sense; avoid 颳 "wind blows"
    "升仙",  # "ascend to immortality"; avoid 昇 "rise"
    "又升仙",  # "ascend to immortality"; avoid 昇 "rise"
    "响出邊",  # Cantonese locative 响; avoid 響 "sound"
    "响邊",  # Cantonese locative 响; avoid 響 "sound"
    "响凡間",  # Cantonese locative 响; avoid 響 "sound"
    "咸煎餅",  # Cantonese food spelling; avoid 鹹 normalization
    "咸的",  # subtitle uses colloquial 咸; avoid 鹹 normalization
    "食咸定甜",  # Cantonese food contrast; avoid 鹹 normalization
    "唔准",  # Cantonese permission sense; avoid blanket 準
    "唔好郁",  # Cantonese 郁 "move"; avoid 鬱 "depressed"
    "唔郁",  # Cantonese 郁 "move"; avoid 鬱 "depressed"
    "亂郁",  # Cantonese 郁 "move"; avoid 鬱 "depressed"
    "咪郁",  # Cantonese 郁 "move"; avoid 鬱 "depressed"
    "想郁",  # Cantonese 郁 "move"; avoid 鬱 "depressed"
    "郁佢",  # Cantonese 郁 "move/attack"; avoid 鬱 "depressed"
    "郁來郁去",  # Cantonese repeated movement; avoid 鬱
    "郁得",  # Cantonese 郁 "move"; avoid 鬱 "depressed"
    "郁手",  # Cantonese phrase "start fighting"; avoid 鬱
    "郁親",  # Cantonese 郁 "move"; avoid 鬱 "depressed"
    "郁就",  # Cantonese 郁 "move"; avoid 鬱 "depressed"
    "郁嘅",  # Cantonese 郁 "move"; avoid 鬱 "depressed"
    "扑嘛",  # Cantonese 扑 "hit"; avoid 撲 "pounce"
    "嚟扑",  # Cantonese 扑 "hit"; avoid 撲 "pounce"
    "燒到扑",  # Cantonese result phrase; avoid 撲 "pounce"
    "家伙",  # subtitle lexeme 家伙; avoid 傢伙 furniture radical
    "幹你娘的",  # profanity phrase keeps 娘; avoid 孃
    "干擾",  # legal/source text uses 干擾; avoid 幹擾
    "拜托",  # fixture spelling for "please"; avoid 拜託
    "散伙",  # group-dispersal phrase; avoid 夥 variant
    "無厘頭",  # Hong Kong phrase keeps 厘, not 釐
    "杰啦",  # Cantonese adjective in fixture; avoid 傑 "outstanding"
    "注定",  # fate sense; avoid 註 "annotation"
    "洒你",  # fixture keeps 瀟洒-style 洒; avoid 灑
    "瀟洒",  # accepted variant of 瀟灑 in fixtures
    "薄幸",  # fixed term; avoid 倖 "fortunate by chance"
    "萬里",  # distance unit 里; avoid 裏 "inside"
    "聰明了",  # aspect/result 了; avoid 瞭
    "剛才看",  # modern 剛才; avoid older 剛纔
    "還有只蟑螂",  # fixture classifier phrase uses 只; avoid 隻
    "那只九官鳥",  # fixture uses 只; avoid classifier 隻
    "仆你",  # Cantonese profanity 仆街 family; avoid 僕 "servant"
    "伙記",  # Cantonese waiter/worker term; avoid 夥 variant
    "碗面",  # Cantonese/HK noodle spelling; avoid 麵/麪
    "喂你",  # interjection/address 喂; avoid 餵 "feed"
    "蒙蒙",  # character name/baby-talk; avoid 濛濛 "misty"
    "香港制定",  # 制定 means "formulate"; avoid 製 "manufacture"
}
"""Text spans to preserve when converting simplified Chinese toward traditional."""

T2S_EXCLUSIONS: set[str] = {
    "嗰",  # 𠮶
    "劏",  # 㓥
    "餸",  # 𩠌
    "唓",  # 𪠳
}
"""Text spans to preserve when converting traditional Chinese toward simplified."""


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

    if apply_exclusions and config in SIMPLIFIED_CONFIGS:
        return _get_zho_text_converted_with_exclusions(text, converter, T2S_EXCLUSIONS)
    if apply_exclusions and config in TRADITIONAL_CONFIGS:
        return _get_zho_text_converted_with_exclusions(text, converter, S2T_EXCLUSIONS)
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
