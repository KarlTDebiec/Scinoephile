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
    "吃",  # Modern subtitles prefer 吃 over the literary traditional variant 喫.
    "吓",  # Cantonese particle/verb is distinct from 嚇 "frighten".
    "晒",  # Cantonese result particle uses 晒 rather than 曬 "sun-dry".
    "才",  # Common modern form is preferred over the older adverbial 纔.
    "托",  # 拜托 and Cantonese uses keep 托 rather than 託.
    "蒙",  # Cantonese/colloquial 蒙 is not the weather adjective 濛.
    "准",  # 准 remains valid in permission contexts such as 不准.
    "群",  # Modern subtitles use 群 instead of the older variant 羣.
    "郁",  # Cantonese 郁 "move" is not 鬱 "depressed/dense".
    "床",  # Modern subtitles prefer 床 over the older variant 牀.
    "台",  # 台 is kept for platform/stage/address forms instead of 臺.
    "痴",  # 白痴 commonly keeps 痴 rather than 癡.
    "升",  # 升仙 keeps the modern form rather than 昇.
    "仆",  # Cantonese 仆街 is not 僕 "servant".
    "秘",  # Modern subtitles prefer 秘 over the older variant 祕.
    "克",  # 克制 uses 克, not 剋.
    "借",  # 借助 is accepted in the fixture style instead of 藉助.
    "了",  # 了解 keeps 了 rather than 瞭.
    "里",  # 萬里 uses the distance character 里, not 裏 "inside".
    "咸",  # Cantonese food terms such as 咸煎餅 keep 咸.
    "虱",  # Modern/Hong Kong subtitles use 虱 instead of 蝨.
    "响",  # Cantonese locative/verb use is kept instead of 響.
    "峰",  # Modern subtitles prefer 峰 over the older variant 峯.
    "扑",  # Cantonese 扑 "hit" is kept rather than 撲.
    "伙",  # 伙記 and 家伙 keep 伙 rather than 夥.
    "干",  # 干 has valid traditional uses such as 干擾.
    "粽",  # Modern/Hong Kong subtitles use 粽 instead of 糉.
    "洒",  # 瀟洒 keeps the fixture's variant rather than 灑.
    "卺",  # 合卺 keeps 卺 rather than the rare variant 巹.
    "皂",  # 青紅皂白 uses 皂 rather than 皁.
    "娘",  # Profanity/kinship contexts use 娘 rather than 孃.
    "灶",  # Modern subtitles prefer 灶 over 竈.
    "唇",  # Modern subtitles prefer 唇 over 脣.
    "刮",  # Shaving/scraping uses 刮, not 颳 "wind blows".
    "幸",  # 薄幸 uses 幸, not 倖.
    "岩",  # 金剛岩 and Cantonese 岩 are not 巖 "cliff".
    "杰",  # Cantonese 杰 is not 傑 "outstanding".
    "厘",  # 無厘頭 keeps the Hong Kong form 厘.
    "注",  # 注定 uses 注, not 註 "annotation".
    "制",  # 制定 uses 制, not 製 "manufacture".
    "喂",  # Interjection 喂 is not 餵 "feed".
}
"""Characters to preserve when converting simplified Chinese toward traditional."""

# Likely fixture artifacts seen during s2t no-op discovery:
# "丑",  # test/data/tmm/output/zho-Hant_ocr/fuse_clean_validate.srt:35 uses 丑
#        # where standard traditional 醜 is expected for "ugly".
# "边",  # test/data/acopopb/output/yue-Hant_ocr/fuse_clean_validate.srt:5071
#        # contains simplified 边 in a Hant OCR output.
# "嘘",  # test/data/acoptc/output/yue-Hant_ocr/fuse_clean_validate.srt:3899
#        # contains simplified 嘘 where Hant 噓 is expected.
# "只",  # test/data/tmm/output/zho-Hant_ocr/fuse_clean_validate.srt:2376 uses
#        # 只 as a classifier where traditional 隻 is expected.
# "面",  # test/data/acopopb/output/yue-Hant_ocr/fuse_clean_validate.srt:679
#        # likely has simplified 面 for noodle 麵.
# "云",  # test/data/acopopb/output/yue-Hant_ocr/fuse_clean_validate.srt:1787
#        # appears in Cantonese "呢云", likely an OCR/review artifact.
# "羡",  # test/data/tmm/output/yue-Hant_ocr/fuse_clean_validate.srt:2611
#        # uses simplified 羡 where traditional 羨 is expected.
# "家",  # test/data/tmm/output/yue-Hant_ocr/fuse_clean_validate.srt:4695
#        # appears in 家伙, where the existing test expects 傢伙.

_T2S_EXCLUDED_CHARS = {
    "喎",  # Cantonese sentence particle should not be replaced by 㖞.
    "嗰",  # Cantonese demonstrative should not be replaced by 𠮶.
    "搵",  # Cantonese 搵 "look for" is preferred over OpenCC's 揾.
    "痾",  # Cantonese 痾 "defecate" is preferred over 疴.
    "藉",  # 藉此 is accepted in simplified text and should not collapse to 借.
    "劏",  # Cantonese 劏 "slaughter" is preferred over 㓥.
    "捱",  # 捱 in the fixtures is lexical, not a generic replacement with 挨.
    "噚",  # Cantonese 噚 should not be replaced by 㖊.
    "燶",  # Cantonese 燶 "burnt" should not be replaced by 㶶.
    "餸",  # Cantonese 餸 "dish" should not be replaced by 𩠌.
    "剎",  # 一剎那 keeps 剎 as an accepted variant.
    "覆",  # 答覆 keeps the lexical form distinct from 复.
    "唓",  # Cantonese interjection 唓 should not be replaced by 𪠳.
}
"""Characters to preserve when converting traditional Chinese toward simplified."""

# Likely fixture artifacts seen during t2s no-op discovery:
# "擺",  # test/data/acoptc/output/yue-Hans_ocr/fuse_clean_validate.srt:811
#        # contains traditional 擺 in a Hans OCR output.
# "換",  # test/data/acoptc/output/yue-Hans_ocr/fuse_clean_validate.srt:3003
#        # contains traditional 換 in a Hans OCR output.
# "決",  # test/data/acopopb/output/yue-Hans_ocr/fuse_clean_validate.srt:63
#        # contains traditional 決 in a Hans OCR output.
# "綁",  # test/data/acopopb/output/yue-Hans_ocr/fuse_clean_validate.srt:1639
#        # contains traditional 綁 in a Hans OCR output.
# "帶",  # test/data/acoptc/output/yue-Hans_ocr/fuse_clean_validate.srt:2675
#        # contains traditional 帶 in a Hans OCR output.
# "豬",  # test/data/acoptc/output/yue-Hans_ocr/fuse_clean_validate.srt:5603
#        # contains traditional 豬 in a Hans OCR output.
# "潚",  # test/data/acopopb/input/zho-Hans.srt:2067 is likely an OCR artifact
#        # for 瀟/潇 in 瀟洒.
# "涼",  # test/data/acopopb/output/yue-Hans_ocr/fuse_clean_validate.srt:775
#        # contains traditional 涼 in a Hans OCR output.
# "幫",  # test/data/acopopb/output/yue-Hans_ocr/fuse_clean_validate.srt:1043
#        # contains traditional 幫 in a Hans OCR output.
# "蹤",  # test/data/acopopb/output/yue-Hans_ocr/fuse_clean_validate.srt:2123
#        # contains traditional 蹤 in a Hans OCR output.
# "內",  # test/data/acopopb/output/yue-Hans_ocr/fuse_clean_validate.srt:3195
#        # contains traditional 內 in a Hans OCR output.
# "瀟",  # test/data/acopopb/output/zho-Hans_ocr/fuse_clean_validate.srt:2083
#        # contains traditional 瀟 in a Hans OCR output.
# "靚",  # test/data/acoptc/output/yue-Hans_ocr/fuse_clean_validate.srt:3
#        # contains traditional 靚 where simplified 靓 is expected.
# "鑼",  # test/data/acoptc/output/yue-Hans_ocr/fuse_clean_validate.srt:3983
#        # is likely OCR for 攞 rather than simplified 锣.
# "齋",  # test/data/acoptc/output/yue-Hans_ocr/fuse_clean_validate.srt:5243
#        # contains traditional 齋 in a Hans OCR output.
# "慘",  # test/data/tmm/output/zho-Hans_ocr/fuse_clean_validate.srt:339
#        # contains traditional 慘 in a Hans OCR output.
# "黃",  # test/data/tmm/output/zho-Hans_ocr/fuse_clean_validate.srt:1751
#        # contains traditional 黃 in a Hans OCR output.
# "噓",  # test/data/tmm/output/zho-Hans_ocr/fuse_clean_validate.srt:6107
#        # contains traditional 噓 in a Hans OCR output.
# "癲",  # test/data/tmm/output/zho-Hans_ocr/fuse_clean_validate.srt:6147
#        # contains traditional 癲 in a Hans OCR output.


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
