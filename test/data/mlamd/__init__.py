#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MLAMD."""

from __future__ import annotations

import pytest
from PIL import Image

from scinoephile.audio.testing import MergeTestCase, SplitTestCase
from scinoephile.image import ImageSeries
from scinoephile.testing import test_data_root

input_dir = test_data_root / "mlamd" / "input"
output_dir = test_data_root / "mlamd" / "output"


# region 简体中文
@pytest.fixture
def mlamd_zho_hans() -> ImageSeries:
    """MLAMD 简体中文 image series."""
    try:
        return ImageSeries.load(output_dir / "zho-Hans")
    except FileNotFoundError:
        return ImageSeries.load(input_dir / "zho-Hans.sup")


@pytest.fixture()
def mlamd_zho_hans_image() -> Image.Image:
    """MLAMD 简体中文 image."""
    return Image.open(output_dir / "zho-Hans" / "0001.png")


@pytest.fixture
def mlamd_zho_hans_validation_directory() -> str:
    """MLAMD 简体中文 validation directory."""
    return output_dir / "zho-Hans_validation"


# endregion


# region 繁体中文
@pytest.fixture
def mlamd_zho_hant() -> ImageSeries:
    """MLAMD 繁体中文 image series."""
    try:
        return ImageSeries.load(output_dir / "zho-Hant")
    except FileNotFoundError:
        return ImageSeries.load(input_dir / "zho-Hant.sup")


@pytest.fixture()
def mlamd_zho_hant_image() -> Image.Image:
    """MLAMD 繁体中文 image."""
    return Image.open(output_dir / "zho-Hant" / "0001.png")


@pytest.fixture
def mlamd_zho_hant_validation_directory() -> str:
    """MLAMD 繁体中文 validation directory."""
    return output_dir / "zho-Hant_validation"


# endregion


# region English
@pytest.fixture
def mlamd_eng() -> ImageSeries:
    """MLAMD English image series."""
    try:
        return ImageSeries.load(output_dir / "eng")
    except FileNotFoundError:
        return ImageSeries.load(input_dir / "eng.sup")


@pytest.fixture()
def mlamd_eng_image() -> Image.Image:
    """MLAMD English image."""
    return Image.open(output_dir / "eng" / "0001.png")


@pytest.fixture
def mlamd_eng_validation_directory() -> str:
    """MLAMD English validation directory."""
    return output_dir / "eng_validation"


# endregion


# region 粤文 Splitting Test Cases
mlamd_split_test_cases = [
    SplitTestCase(  # Block 1
        one_zhongwen="再右拐窝打老道向女人街方向飞⋯",
        one_yuewen_start="再右转抹返出去窝打炉道",
        two_zhongwen="飞呀，飞⋯",
        two_yuewen_end="飞下",
        yuewen_to_split="向女人街方向飞下下",
        one_yuewen_to_append="向女人街方向飞下下",
        two_yuewen_to_prepend="",
        include_in_prompt=True,
    ),
    SplitTestCase(
        one_zhongwen="飞呀，飞⋯",
        one_yuewen_start="飞下",
        two_zhongwen="胶兜最后飞进广华医院候产房",
        two_yuewen_end="最后胶兜飞咗入广华医院嘅后产房",
        yuewen_to_split="飞下",
        one_yuewen_to_append="飞下",
        two_yuewen_to_prepend="",
        include_in_prompt=True,
    ),
    SplitTestCase(
        one_zhongwen="或者读书唔叻，工作叻呢？",
        one_yuewen_start="或者读书唔叻",
        two_zhongwen="又或者⋯",
        two_yuewen_end="又或者呢",
        yuewen_to_split="出嚟做嘢叻啦",
        one_yuewen_to_append="出嚟做嘢叻啦",
        two_yuewen_to_prepend="",
    ),
    SplitTestCase(
        one_zhongwen="唔聪明唔靓仔也算了，只要福星高照",
        one_yuewen_start="就算唔系咁聪明同咁靓仔",
        two_zhongwen="一世够运，逢凶化吉！",
        two_yuewen_end="一世救运乜嘢事都逢凶化㗎喇",
        yuewen_to_split="只要复星高照",
        one_yuewen_to_append="只要复星高照",
        two_yuewen_to_prepend="",
    ),
    SplitTestCase(  # Block 3
        one_zhongwen="麦太，没见面一阵",
        one_yuewen_start="咦麦太",
        two_zhongwen="怎么小腿粗起来了？",
        two_yuewen_end="个脚刮囊粗咗咁多呀",
        yuewen_to_split="咩唔见你一排",
        one_yuewen_to_append="咩唔见你一排",
        two_yuewen_to_prepend="",
    ),
    SplitTestCase(
        one_zhongwen="怎么不试一试好彩酒楼对面",
        one_yuewen_start="",
        two_zhongwen="旧中侨国货楼上的⋯",
        two_yuewen_end="",
        yuewen_to_split="点解唔试下好彩走楼斜对面",
        one_yuewen_to_append="点解唔试下好彩走楼斜对面",
        two_yuewen_to_prepend="",
    ),
    SplitTestCase(
        one_zhongwen="春田花花幼稚园，师资优良⋯",
        one_yuewen_start="春田花花幼稚园",
        two_zhongwen="而且还有西人教英文！",
        two_yuewen_end="仲系西人教英文添㗎",
        yuewen_to_split="诗诗优良",
        one_yuewen_to_append="诗诗优良",
        two_yuewen_to_prepend="",
    ),
    SplitTestCase(
        one_zhongwen="西人教英文？",
        one_yuewen_start="咦",
        two_zhongwen="是呀！",
        two_yuewen_end="",
        yuewen_to_split="西人教英文",
        one_yuewen_to_append="西人教英文",
        two_yuewen_to_prepend="",
    ),
    SplitTestCase(  # Block 4
        one_zhongwen="横看竖看也不像发哥伟仔的一个⋯",
        one_yuewen_start="即系横睇掂睇都唔似发哥或者",
        two_zhongwen="就是我，麦兜",
        two_yuewen_end="就系我麦兜",
        yuewen_to_split="位仔𠮶个呢",
        one_yuewen_to_append="位仔𠮶个呢",
        two_yuewen_to_prepend="",
    ),
    SplitTestCase(
        one_zhongwen="这么多年来⋯",
        one_yuewen_start="",
        two_zhongwen="我其实不大明白他的说话",
        two_yuewen_end="我其实唔系好知佢噏文",
        yuewen_to_split="所以咁多年嚟",
        one_yuewen_to_append="所以咁多年嚟",
        two_yuewen_to_prepend="",
    ),
    # SplitTestCase(
    #     one_zhongwen="荔芋火鸭礼！　　荔芋火鸭礼！",
    #     one_yuewen_start="",
    #     two_zhongwen="忘记校训九十七⋯　　忘记校训九十七⋯",
    #     two_yuewen_end="",
    #     yuewen_to_split="湾吉校坟交涉设",
    #     one_yuewen_to_append="",
    #     two_yuewen_to_prepend="",
    # ),
    # SplitTestCase(
    #     one_zhongwen="也不能忘记校训九十八！",
    #     one_yuewen_start="",
    #     two_zhongwen="也不能忘记校训九十八！",
    #     two_yuewen_end="",
    #     yuewen_to_split="都唔好湾吉校坟交涉白",
    #     one_yuewen_to_append="",
    #     two_yuewen_to_prepend="",
    # ),
    # SplitTestCase(
    #     one_zhongwen="好！各位同学⋯",
    #     one_yuewen_start="",
    #     two_zhongwen="今天的早会主要是跟大家分享",
    #     two_yuewen_end="",
    #     yuewen_to_split="𠮶个位同学",
    #     one_yuewen_to_append="",
    #     two_yuewen_to_prepend="",
    # ),
    SplitTestCase(
        one_zhongwen="今天的早会主要是跟大家分享",
        one_yuewen_start="",
        two_zhongwen="一个重要主题：",
        two_yuewen_end="",
        yuewen_to_split="今次座会系要同大家分享一个可重要嘅主题",
        one_yuewen_to_append="今次座会系要同大家分享",
        two_yuewen_to_prepend="一个可重要嘅主题",
    ),
]
"""MLAMD 粤文 splitting test cases."""

# endregion

# region 粤文 Merging Test Cases

mlamd_merge_test_cases = [
    MergeTestCase(
        zhongwen="沿荔枝角道直出大角咀道",
        yuewen_to_merge=["沿住荔枝角度", "直出大角咀度"],
        yuewen_merged="沿住荔枝角度直出大角咀度",
    ),
    MergeTestCase(
        zhongwen="经好彩酒家左转花园街乐园牛丸王⋯",
        yuewen_to_merge=["经过好彩走家", "再左转返出花园街", "乐园牛园望对上"],
        yuewen_merged="经过好彩走家再左转返出花园街乐园牛园望对上⋯",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="转呀，转⋯再更正一下：",
        yuewen_to_merge=["转下", "转下", "都系唔好"],
        yuewen_merged="转下，转下⋯都系唔好：",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="直出亚皆老街跨过火车桥右转太平道",
        yuewen_to_merge=["都系出返去阿佳路街飞过火车桥", "右转入太平道"],
        yuewen_merged="都系出返去阿佳路街飞过火车桥右转入太平道",
    ),
    MergeTestCase(
        zhongwen="再右拐窝打老道向女人街方向飞⋯",
        yuewen_to_merge=["再右转抹返出去窝打炉道", "向女人街方向飞下下"],
        yuewen_merged="再右转抹返出去窝打炉道向女人街方向飞下下⋯",
    ),
    MergeTestCase(
        zhongwen="飞呀，飞⋯",
        yuewen_to_merge=["飞下", "飞下"],
        yuewen_merged="飞下，飞下⋯",
    ),
    MergeTestCase(
        zhongwen="更正：左边额角上⋯",
        yuewen_to_merge=["都系唔好", "左边云晶对上"],
        yuewen_merged="都系唔好：左边云晶对上⋯",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="转呀，转⋯",
        yuewen_to_merge=["转下", "转下", "转下噉"],
        yuewen_merged="转下，转下，转下噉⋯",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="希望他好聪明，读书好叻！",
        yuewen_to_merge=["希望佢好聪明", "读书好叻"],
        yuewen_merged="希望佢好聪明，读书好叻！",
    ),
    MergeTestCase(
        zhongwen="或者读书唔叻，工作叻呢？",
        yuewen_to_merge=["或者读书唔叻", "出嚟做嘢叻啦"],
        yuewen_merged="或者读书唔叻，出嚟做嘢叻啦？",
    ),
    MergeTestCase(
        zhongwen="胶兜仍然在转，毫无点头迹象",
        yuewen_to_merge=["胶兜依然系噉喺度转", "好似一啲应承嘅迹象都冇"],
        yuewen_merged="胶兜依然系噉喺度转，好似一啲应承嘅迹象都冇",
    ),
    MergeTestCase(
        zhongwen="赶忙趁胶兜落地前另许一个愿望：",
        yuewen_to_merge=["嗱嗱嗱喺胶兜未落地之前", "起过另外一个愿望"],
        yuewen_merged="嗱嗱嗱喺胶兜未落地之前起过另外一个愿望：",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="唔聪明唔靓仔也算了，只要福星高照",
        yuewen_to_merge=["就算唔系咁聪明同咁靓仔", "只要复星高照"],
        yuewen_merged="就算唔系咁聪明同咁靓仔，只要复星高照",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="一世够运，逢凶化吉！",
        yuewen_to_merge=["一世救运", "乜嘢事都逢凶化㗎啦"],
        yuewen_merged="一世救运，乜嘢事都逢凶化㗎啦！",
    ),
    MergeTestCase(
        zhongwen="虽是说像梁朝伟周润发也行运定了",
        yuewen_to_merge=["虽然似梁朝伟真运发", "都唔返去冒位嘅"],
        yuewen_merged="虽然似梁朝伟真运发都唔返去冒位嘅",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="嘀督？嘀督，就是答应了",
        yuewen_to_merge=["滴嘟", "滴嘟㖞", "即系应承啦"],
        yuewen_merged="滴嘟？滴嘟㖞，即系应承啦",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="麦太想，这次走运了！",
        yuewen_to_merge=["麦太心谂", "今次冇死喇"],
        yuewen_merged="麦太心谂，今次冇死喇！",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="叻仔？好运？",
        yuewen_to_merge=["叻仔", "好揾"],
        yuewen_merged="叻仔？好揾？",
    ),
    MergeTestCase(
        zhongwen="不行，胶胶声，多难听！",
        yuewen_to_merge=["都系唔好", "胶胶声咁难听"],
        yuewen_merged="都系唔好，胶胶声，咁难听！",
        include_in_prompt=True,
    ),
]
"""MLAMD 粤文 merging test cases."""


# endregion

___all__ = [
    "mlamd_zho_hans",
    "mlamd_zho_hans_image",
    "mlamd_zho_hans_validation_directory",
    "mlamd_zho_hant",
    "mlamd_zho_hant_image",
    "mlamd_zho_hant_validation_directory",
    "mlamd_eng",
    "mlamd_eng_image",
    "mlamd_eng_validation_directory",
    "mlamd_merge_test_cases",
    "mlamd_split_test_cases",
]
