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

_S2T_EXCLUDED_CHARS = {
    "吃",  # keep modern 吃; avoid literary 喫
    "吓",  # keep Cantonese 吓 particle/verb; avoid 嚇 "frighten"
    "晒",  # keep Cantonese 晒 result particle; avoid 曬 "sun-dry"
    "才",  # keep modern 才; avoid older adverbial 纔
    "托",  # keep 拜托 and Cantonese 托; avoid 託
    "蒙",  # keep Cantonese/colloquial 蒙; avoid weather adjective 濛
    "准",  # keep permission-context 准; avoid 準
    "群",  # keep modern 群; avoid older variant 羣
    "郁",  # keep Cantonese 郁 "move"; avoid 鬱 "depressed"
    "床",  # keep modern 床; avoid older variant 牀
    "台",  # keep platform/stage/address 台; avoid 臺
    "痴",  # keep common 白痴 form 痴; avoid 癡
    "升",  # keep 升仙 form 升; avoid 昇
    "仆",  # keep Cantonese 仆街 form 仆; avoid 僕 "servant"
    "秘",  # keep modern 秘; avoid older variant 祕
    "克",  # keep 克制 form 克; avoid 剋
    "借",  # keep fixture-style 借助 form 借; avoid 藉
    "了",  # keep 了解 form 了; avoid 瞭
    "里",  # keep distance character 里; avoid 裏 "inside"
    "咸",  # keep Cantonese food-term 咸; avoid 鹹
    "虱",  # keep modern/Hong Kong 虱; avoid 蝨
    "响",  # keep Cantonese locative/verb 响; avoid 響
    "峰",  # keep modern 峰; avoid older variant 峯
    "扑",  # keep Cantonese 扑 "hit"; avoid 撲
    "伙",  # keep 伙記 and 家伙 form 伙; avoid 夥
    "干",  # keep valid traditional 干 uses; avoid blanket 幹
    "粽",  # keep modern/Hong Kong 粽; avoid 糉
    "洒",  # keep fixture-style 瀟洒 form 洒; avoid 灑
    "卺",  # keep 合卺 form 卺; avoid rare variant 巹
    "皂",  # keep 青紅皂白 form 皂; avoid 皁
    "娘",  # keep kinship/profanity 娘; avoid 孃
    "灶",  # keep modern 灶; avoid older variant 竈
    "唇",  # keep modern 唇; avoid 脣
    "刮",  # keep shaving/scraping 刮; avoid 颳 "wind blows"
    "幸",  # keep 薄幸 form 幸; avoid 倖
    "岩",  # keep 金剛岩 and Cantonese 岩; avoid 巖 "cliff"
    "杰",  # keep Cantonese 杰; avoid 傑 "outstanding"
    "厘",  # keep Hong Kong 無厘頭 form 厘; avoid 釐
    "注",  # keep 注定 form 注; avoid 註 "annotation"
    "制",  # keep 制定 form 制; avoid 製 "manufacture"
    "喂",  # keep interjection 喂; avoid 餵 "feed"
}
"""Characters to preserve when converting simplified Chinese toward traditional."""

# Inactive fixture artifacts seen during s2t no-op discovery:
# "丑",  # inactive: expected 醜 "ugly"
#        # found: test/data/tmm/output/zho-Hant_ocr/fuse_clean_validate.srt:35
# "边",  # inactive: simplified 边 in Hant OCR output
#        # found: test/data/acopopb/output/yue-Hant_ocr/
#        # fuse_clean_validate.srt:5071
# "嘘",  # inactive: simplified 嘘 where Hant 噓 is expected
#        # found: test/data/acoptc/output/yue-Hant_ocr/
#        # fuse_clean_validate.srt:3899
# "只",  # inactive: classifier should be traditional 隻
#        # found: test/data/tmm/output/zho-Hant_ocr/fuse_clean_validate.srt:2376
# "面",  # inactive: noodle should be 麵
#        # found: test/data/acopopb/output/yue-Hant_ocr/
#        # fuse_clean_validate.srt:679
# "云",  # inactive: likely OCR/review artifact in Cantonese "呢云"
#        # found: test/data/acopopb/output/yue-Hant_ocr/
#        # fuse_clean_validate.srt:1787
# "羡",  # inactive: simplified 羡 where traditional 羨 is expected
#        # found: test/data/tmm/output/yue-Hant_ocr/fuse_clean_validate.srt:2611
# "家",  # inactive: existing test expects 傢伙, not 家伙
#        # found: test/data/tmm/output/yue-Hant_ocr/fuse_clean_validate.srt:4695

_T2S_EXCLUDED_CHARS = {
    "喎",  # keep Cantonese sentence particle 喎; avoid 㖞
    "嗰",  # keep Cantonese demonstrative 嗰; avoid 𠮶
    "搵",  # keep Cantonese 搵 "look for"; avoid 揾
    "痾",  # keep Cantonese 痾 "defecate"; avoid 疴
    "藉",  # keep simplified-text 藉此 form 藉; avoid 借
    "劏",  # keep Cantonese 劏 "slaughter"; avoid 㓥
    "捱",  # keep fixture lexical 捱; avoid generic 挨
    "噚",  # keep Cantonese 噚; avoid 㖊
    "燶",  # keep Cantonese 燶 "burnt"; avoid 㶶
    "餸",  # keep Cantonese 餸 "dish"; avoid 𩠌
    "剎",  # keep 一剎那 form 剎; avoid 刹
    "覆",  # keep 答覆 lexical form 覆; avoid 复
    "唓",  # keep Cantonese interjection 唓; avoid 𪠳
}
"""Characters to preserve when converting traditional Chinese toward simplified."""

# Inactive fixture artifacts seen during t2s no-op discovery:
# "擺",  # inactive: traditional 擺 in Hans OCR output
#        # found: test/data/acoptc/output/yue-Hans_ocr/
#        # fuse_clean_validate.srt:811
# "換",  # inactive: traditional 換 in Hans OCR output
#        # found: test/data/acoptc/output/yue-Hans_ocr/
#        # fuse_clean_validate.srt:3003
# "決",  # inactive: traditional 決 in Hans OCR output
#        # found: test/data/acopopb/output/yue-Hans_ocr/
#        # fuse_clean_validate.srt:63
# "綁",  # inactive: traditional 綁 in Hans OCR output
#        # found: test/data/acopopb/output/yue-Hans_ocr/
#        # fuse_clean_validate.srt:1639
# "帶",  # inactive: traditional 帶 in Hans OCR output
#        # found: test/data/acoptc/output/yue-Hans_ocr/
#        # fuse_clean_validate.srt:2675
# "豬",  # inactive: traditional 豬 in Hans OCR output
#        # found: test/data/acoptc/output/yue-Hans_ocr/
#        # fuse_clean_validate.srt:5603
# "潚",  # inactive: likely OCR artifact for 瀟/潇 in 瀟洒
#        # found: test/data/acopopb/input/zho-Hans.srt:2067
# "涼",  # inactive: traditional 涼 in Hans OCR output
#        # found: test/data/acopopb/output/yue-Hans_ocr/
#        # fuse_clean_validate.srt:775
# "幫",  # inactive: traditional 幫 in Hans OCR output
#        # found: test/data/acopopb/output/yue-Hans_ocr/
#        # fuse_clean_validate.srt:1043
# "蹤",  # inactive: traditional 蹤 in Hans OCR output
#        # found: test/data/acopopb/output/yue-Hans_ocr/
#        # fuse_clean_validate.srt:2123
# "內",  # inactive: traditional 內 in Hans OCR output
#        # found: test/data/acopopb/output/yue-Hans_ocr/
#        # fuse_clean_validate.srt:3195
# "瀟",  # inactive: traditional 瀟 in Hans OCR output
#        # found: test/data/acopopb/output/zho-Hans_ocr/
#        # fuse_clean_validate.srt:2083
# "靚",  # inactive: traditional 靚 where simplified 靓 is expected
#        # found: test/data/acoptc/output/yue-Hans_ocr/fuse_clean_validate.srt:3
# "鑼",  # inactive: likely OCR for 攞 rather than simplified 锣
#        # found: test/data/acoptc/output/yue-Hans_ocr/
#        # fuse_clean_validate.srt:3983
# "齋",  # inactive: traditional 齋 in Hans OCR output
#        # found: test/data/acoptc/output/yue-Hans_ocr/
#        # fuse_clean_validate.srt:5243
# "慘",  # inactive: traditional 慘 in Hans OCR output
#        # found: test/data/tmm/output/zho-Hans_ocr/fuse_clean_validate.srt:339
# "黃",  # inactive: traditional 黃 in Hans OCR output
#        # found: test/data/tmm/output/zho-Hans_ocr/fuse_clean_validate.srt:1751
# "噓",  # inactive: traditional 噓 in Hans OCR output
#        # found: test/data/tmm/output/zho-Hans_ocr/fuse_clean_validate.srt:6107
# "癲",  # inactive: traditional 癲 in Hans OCR output
#        # found: test/data/tmm/output/zho-Hans_ocr/fuse_clean_validate.srt:6147


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

    excluded_chars: set[str] = set()
    if apply_exclusions:
        if config in SIMPLIFIED_CONFIGS:
            excluded_chars = _T2S_EXCLUDED_CHARS
        if config in TRADITIONAL_CONFIGS:
            excluded_chars = _S2T_EXCLUDED_CHARS

    if excluded_chars and len(converted_text) == len(text):
        converted_chars = list(converted_text)
        for index, char in enumerate(text):
            if char in excluded_chars:
                converted_chars[index] = char
        converted_text = "".join(converted_chars)

    return converted_text
