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
        zhongwen_one_input="再右拐窝打老道向女人街方向飞⋯",
        yuewen_one_input="再右转抹返出去窝打炉道",
        yuewen_one_overlap=1.0,
        zhongwen_two_input="飞呀，飞⋯",
        yuewen_two_input="飞下",
        yuewen_two_overlap=0.42,
        yuewen_ambiguous_input="向女人街方向飞下下",
        yuewen_one_output="向女人街方向飞下下",
        yuewen_two_output="",
        include_in_prompt=True,
    ),
    SplitTestCase(
        zhongwen_one_input="飞呀，飞⋯",
        yuewen_one_input="飞下",
        yuewen_one_overlap=1.0,
        zhongwen_two_input="胶兜最后飞进广华医院候产房",
        yuewen_two_input="最后胶兜飞咗入广华医院嘅后产房",
        yuewen_two_overlap=0.4,
        yuewen_ambiguous_input="飞下",
        yuewen_one_output="飞下",
        yuewen_two_output="",
        include_in_prompt=True,
    ),
    SplitTestCase(
        zhongwen_one_input="或者读书唔叻，工作叻呢？",
        yuewen_one_input="或者读书唔叻",
        yuewen_one_overlap=1.0,
        zhongwen_two_input="又或者⋯",
        yuewen_two_input="又或者呢",
        yuewen_two_overlap=0.42,
        yuewen_ambiguous_input="出嚟做嘢叻啦",
        yuewen_one_output="出嚟做嘢叻啦",
        yuewen_two_output="",
        include_in_prompt=False,
    ),
    SplitTestCase(
        zhongwen_one_input="唔聪明唔靓仔也算了，只要福星高照",
        yuewen_one_input="就算唔系咁聪明同咁靓仔",
        yuewen_one_overlap=1.0,
        zhongwen_two_input="一世够运，逢凶化吉！",
        yuewen_two_input="一世救运乜嘢事都逢凶化㗎喇",
        yuewen_two_overlap=0.41,
        yuewen_ambiguous_input="只要复星高照",
        yuewen_one_output="只要复星高照",
        yuewen_two_output="",
        include_in_prompt=False,
    ),
    SplitTestCase(  # Block 3
        zhongwen_one_input="麦太，没见面一阵",
        yuewen_one_input="咦麦太",
        yuewen_one_overlap=0.35,
        zhongwen_two_input="怎么小腿粗起来了？",
        yuewen_two_input="个脚刮囊粗咗咁多呀",
        yuewen_two_overlap=1.0,
        yuewen_ambiguous_input="咩唔见你一排",
        yuewen_one_output="咩唔见你一排",
        yuewen_two_output="",
        include_in_prompt=False,
    ),
    SplitTestCase(
        zhongwen_one_input="怎么不试一试好彩酒楼对面",
        yuewen_one_input="",
        yuewen_one_overlap=1.0,
        zhongwen_two_input="旧中侨国货楼上的⋯",
        yuewen_two_input="",
        yuewen_two_overlap=0.58,
        yuewen_ambiguous_input="点解唔试下好彩走楼斜对面",
        yuewen_one_output="点解唔试下好彩走楼斜对面",
        yuewen_two_output="",
        include_in_prompt=False,
    ),
    SplitTestCase(
        zhongwen_one_input="春田花花幼稚园，师资优良⋯",
        yuewen_one_input="春田花花幼稚园",
        yuewen_one_overlap=0.7,
        zhongwen_two_input="而且还有西人教英文！",
        yuewen_two_input="仲系西人教英文添㗎",
        yuewen_two_overlap=1.0,
        yuewen_ambiguous_input="诗诗优良",
        yuewen_one_output="诗诗优良",
        yuewen_two_output="",
        include_in_prompt=False,
    ),
    SplitTestCase(
        zhongwen_one_input="西人教英文？",
        yuewen_one_input="咦",
        yuewen_one_overlap=0.75,
        zhongwen_two_input="是呀！",
        yuewen_two_input="",
        yuewen_two_overlap=1.0,
        yuewen_ambiguous_input="西人教英文",
        yuewen_one_output="西人教英文",
        yuewen_two_output="",
        include_in_prompt=False,
    ),
    SplitTestCase(  # Block 4
        zhongwen_one_input="横看竖看也不像发哥伟仔的一个⋯",
        yuewen_one_input="即系横睇掂睇都唔似发哥或者",
        yuewen_one_overlap=0.39,
        zhongwen_two_input="就是我，麦兜",
        yuewen_two_input="就系我麦兜",
        yuewen_two_overlap=1.0,
        yuewen_ambiguous_input="位仔𠮶个呢",
        yuewen_one_output="位仔𠮶个呢",
        yuewen_two_output="",
        include_in_prompt=False,
    ),
    SplitTestCase(
        zhongwen_one_input="这么多年来⋯",
        yuewen_one_input="",
        yuewen_one_overlap=1.0,
        zhongwen_two_input="我其实不大明白他的说话",
        yuewen_two_input="我其实唔系好知佢噏文",
        yuewen_two_overlap=0.46,
        yuewen_ambiguous_input="所以咁多年嚟",
        yuewen_one_output="所以咁多年嚟",
        yuewen_two_output="",
        include_in_prompt=False,
    ),
    # SplitTestCase(
    #     zhongwen_one_input="荔芋火鸭礼！　　荔芋火鸭礼！",
    #     yuewen_one_input="",
    #     yuewen_one_overlap=1.0,
    #     zhongwen_two_input="忘记校训九十七⋯　　忘记校训九十七⋯",
    #     yuewen_two_input="",
    #     yuewen_two_overlap=0.6,
    #     yuewen_ambiguous_input="湾吉校坟交涉设",
    #     yuewen_one_output="",
    #     yuewen_two_output="",
    #     include_in_prompt=False,
    # ),
    # SplitTestCase(
    #     zhongwen_one_input="也不能忘记校训九十八！",
    #     yuewen_one_input="",
    #     yuewen_one_overlap=1.0,
    #     zhongwen_two_input="也不能忘记校训九十八！",
    #     yuewen_two_input="",
    #     yuewen_two_overlap=0.62,
    #     yuewen_ambiguous_input="都唔好湾吉校坟交涉白",
    #     yuewen_one_output="",
    #     yuewen_two_output="",
    #     include_in_prompt=False,
    # ),
    # SplitTestCase(
    #     zhongwen_one_input="好！各位同学⋯",
    #     yuewen_one_input="",
    #     yuewen_one_overlap=1.0,
    #     zhongwen_two_input="今天的早会主要是跟大家分享",
    #     yuewen_two_input="",
    #     yuewen_two_overlap=0.62,
    #     yuewen_ambiguous_input="𠮶个位同学",
    #     yuewen_one_output="",
    #     yuewen_two_output="",
    #     include_in_prompt=False,
    # ),
    SplitTestCase(
        zhongwen_one_input="今天的早会主要是跟大家分享",
        yuewen_one_input="",
        yuewen_one_overlap=0.75,
        zhongwen_two_input="一个重要主题：",
        yuewen_two_input="",
        yuewen_two_overlap=1.0,
        yuewen_ambiguous_input="今次座会系要同大家分享一个可重要嘅主题",
        yuewen_one_output="今次座会系要同大家分享",
        yuewen_two_output="一个可重要嘅主题",
        include_in_prompt=False,
    ),
]
"""MLAMD 粤文 splitting test cases."""

# endregion

# region 粤文 Merging Test Cases

mlamd_merge_test_cases = [
    MergeTestCase(
        zhongwen_input="沿荔枝角道直出大角咀道",
        yuewen_input=["沿住荔枝角度", "直出大角咀度"],
        yuewen_output="沿住荔枝角度直出大角咀度",
    ),
    MergeTestCase(
        zhongwen_input="经好彩酒家左转花园街乐园牛丸王⋯",
        yuewen_input=["经过好彩走家", "再左转返出花园街", "乐园牛园望对上"],
        yuewen_output="经过好彩走家再左转返出花园街乐园牛园望对上⋯",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen_input="转呀，转⋯再更正一下：",
        yuewen_input=["转下", "转下", "都系唔好"],
        yuewen_output="转下，转下⋯都系唔好：",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen_input="直出亚皆老街跨过火车桥右转太平道",
        yuewen_input=["都系出返去阿佳路街飞过火车桥", "右转入太平道"],
        yuewen_output="都系出返去阿佳路街飞过火车桥右转入太平道",
    ),
    MergeTestCase(
        zhongwen_input="再右拐窝打老道向女人街方向飞⋯",
        yuewen_input=["再右转抹返出去窝打炉道", "向女人街方向飞下下"],
        yuewen_output="再右转抹返出去窝打炉道向女人街方向飞下下⋯",
    ),
    MergeTestCase(
        zhongwen_input="飞呀，飞⋯",
        yuewen_input=["飞下", "飞下"],
        yuewen_output="飞下，飞下⋯",
    ),
    MergeTestCase(
        zhongwen_input="更正：左边额角上⋯",
        yuewen_input=["都系唔好", "左边云晶对上"],
        yuewen_output="都系唔好：左边云晶对上⋯",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen_input="转呀，转⋯",
        yuewen_input=["转下", "转下", "转下噉"],
        yuewen_output="转下，转下，转下噉⋯",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen_input="希望他好聪明，读书好叻！",
        yuewen_input=["希望佢好聪明", "读书好叻"],
        yuewen_output="希望佢好聪明，读书好叻！",
    ),
    MergeTestCase(
        zhongwen_input="或者读书唔叻，工作叻呢？",
        yuewen_input=["或者读书唔叻", "出嚟做嘢叻啦"],
        yuewen_output="或者读书唔叻，出嚟做嘢叻啦？",
    ),
    MergeTestCase(
        zhongwen_input="胶兜仍然在转，毫无点头迹象",
        yuewen_input=["胶兜依然系噉喺度转", "好似一啲应承嘅迹象都冇"],
        yuewen_output="胶兜依然系噉喺度转，好似一啲应承嘅迹象都冇",
    ),
    MergeTestCase(
        zhongwen_input="赶忙趁胶兜落地前另许一个愿望：",
        yuewen_input=["嗱嗱嗱喺胶兜未落地之前", "起过另外一个愿望"],
        yuewen_output="嗱嗱嗱喺胶兜未落地之前起过另外一个愿望：",
        include_in_prompt=True,
    ),
    MergeTestCase(  # Difficult
        zhongwen_input="唔聪明唔靓仔也算了，只要福星高照",
        yuewen_input=["就算唔系咁聪明同咁靓仔", "只要复星高照"],
        yuewen_output="就算唔系咁聪明同咁靓仔，只要复星高照",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen_input="一世够运，逢凶化吉！",
        yuewen_input=["一世救运", "乜嘢事都逢凶化㗎啦"],
        yuewen_output="一世救运，乜嘢事都逢凶化㗎啦！",
    ),
    MergeTestCase(
        zhongwen_input="虽是说像梁朝伟周润发也行运定了",
        yuewen_input=["虽然似梁朝伟真运发", "都唔返去冒位嘅"],
        yuewen_output="虽然似梁朝伟真运发都唔返去冒位嘅",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen_input="嘀督？嘀督，就是答应了",
        yuewen_input=["滴嘟", "滴嘟㖞", "即系应承啦"],
        yuewen_output="滴嘟？滴嘟㖞，即系应承啦",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen_input="麦太想，这次走运了！",
        yuewen_input=["麦太心谂", "今次冇死喇"],
        yuewen_output="麦太心谂，今次冇死喇！",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen_input="叻仔？好运？",
        yuewen_input=["叻仔", "好揾"],
        yuewen_output="叻仔？好揾？",
    ),
    MergeTestCase(
        zhongwen_input="不行，胶胶声，多难听！",
        yuewen_input=["都系唔好", "胶胶声咁难听"],
        yuewen_output="都系唔好，胶胶声，咁难听！",
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
