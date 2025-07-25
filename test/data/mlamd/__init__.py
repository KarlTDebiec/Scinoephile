#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MLAMD."""

from __future__ import annotations

from logging import debug, info

import pytest
from PIL import Image

from scinoephile.audio.cantonese.distribution import DistributeTestCase
from scinoephile.audio.cantonese.merging import MergeTestCase
from scinoephile.audio.cantonese.proofing import ProofTestCase
from scinoephile.audio.cantonese.shifting import ShiftTestCase
from scinoephile.common.logs import set_logging_verbosity
from scinoephile.core import ScinoephileError
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


# region 粤文 Distribute Test Cases
distribute_test_cases_block_0 = [
    DistributeTestCase(
        one_zhongwen="再右拐窝打老道向女人街方向飞⋯",
        one_yuewen_start="再右转抹返出去窝打炉道",
        two_zhongwen="飞呀，飞⋯",
        two_yuewen_end="飞下",
        yuewen_to_distribute="向女人街方向飞下下",
        one_yuewen_to_append="向女人街方向飞下下",
        two_yuewen_to_prepend="",
        include_in_prompt=True,
    ),
    DistributeTestCase(
        one_zhongwen="飞呀，飞⋯",
        one_yuewen_start="飞下",
        two_zhongwen="胶兜最后飞进广华医院候产房",
        two_yuewen_end="最后胶兜飞咗入广华医院嘅后产房",
        yuewen_to_distribute="飞下",
        one_yuewen_to_append="飞下",
        two_yuewen_to_prepend="",
        include_in_prompt=True,
    ),
    DistributeTestCase(
        one_zhongwen="或者读书唔叻，工作叻呢？",
        one_yuewen_start="或者读书唔叻",
        two_zhongwen="又或者⋯",
        two_yuewen_end="又或者呢",
        yuewen_to_distribute="出嚟做嘢叻啦",
        one_yuewen_to_append="出嚟做嘢叻啦",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="唔聪明唔靓仔也算了，只要福星高照",
        one_yuewen_start="就算唔系咁聪明同咁靓仔",
        two_zhongwen="一世够运，逢凶化吉！",
        two_yuewen_end="一世救运乜嘢事都逢凶化㗎喇",
        yuewen_to_distribute="只要复星高照",
        one_yuewen_to_append="只要复星高照",
        two_yuewen_to_prepend="",
    ),
]
distribute_test_cases_block_1 = []
distribute_test_cases_block_2 = [
    DistributeTestCase(
        one_zhongwen="怎么不试一试好彩酒楼对面",
        one_yuewen_start="",
        two_zhongwen="旧中侨国货楼上的⋯",
        two_yuewen_end="",
        yuewen_to_distribute="点解唔试下好彩走楼斜对面",
        one_yuewen_to_append="点解唔试下好彩走楼斜对面",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="春田花花幼稚园，师资优良⋯",
        one_yuewen_start="春田花花幼稚园",
        two_zhongwen="而且还有西人教英文！",
        two_yuewen_end="仲系西人教英文添㗎",
        yuewen_to_distribute="诗诗优良",
        one_yuewen_to_append="诗诗优良",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="旧中侨国货楼上的⋯",
        one_yuewen_start="",
        two_zhongwen="春田花花幼稚园？",
        two_yuewen_end="春田花花幼稚园呢",
        yuewen_to_distribute="旧中桥百货公司楼上𠮶间",
        one_yuewen_to_append="旧中桥百货公司楼上𠮶间",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="银城美食广场附近的⋯",
        one_yuewen_start="",
        two_zhongwen="春田花花幼稚园？",
        two_yuewen_end="春田花花幼稚园呀",
        yuewen_to_distribute="银城美食广场附近𠮶间",
        one_yuewen_to_append="银城美食广场附近𠮶间",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="西人教英文？",
        one_yuewen_start="咦",
        two_zhongwen="是呀！",
        two_yuewen_end="",
        yuewen_to_distribute="西人教英文",
        one_yuewen_to_append="西人教英文",
        two_yuewen_to_prepend="",
    ),
]
distribute_test_cases_block_3 = [
    DistributeTestCase(
        one_zhongwen="横看竖看也不像发哥伟仔的一个⋯",
        one_yuewen_start="即系横睇掂睇都唔似发哥或者",
        two_zhongwen="就是我，麦兜",
        two_yuewen_end="就系我麦兜",
        yuewen_to_distribute="位仔𠮶个呢",
        one_yuewen_to_append="位仔𠮶个呢",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="这么多年来⋯",
        one_yuewen_start="",
        two_zhongwen="我其实不大明白他的说话",
        two_yuewen_end="我其实唔系好知佢噏文",
        yuewen_to_distribute="所以咁多年嚟",
        one_yuewen_to_append="所以咁多年嚟",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="荔芋火鸭礼！　　荔芋火鸭礼！",
        one_yuewen_start="",
        two_zhongwen="忘记校训九十七⋯　　忘记校训九十七⋯",
        two_yuewen_end="",
        yuewen_to_distribute="湾吉校坟交涉设",
        one_yuewen_to_append="湾吉校坟交涉设",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="也不能忘记校训九十八！",
        one_yuewen_start="",
        two_zhongwen="也不能忘记校训九十八！",
        two_yuewen_end="",
        yuewen_to_distribute="都唔好湾吉校坟交涉白",
        one_yuewen_to_append="都唔好湾吉校坟交涉白",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="好！各位同学⋯",
        one_yuewen_start="",
        two_zhongwen="今天的早会主要是跟大家分享",
        two_yuewen_end="",
        yuewen_to_distribute="𠮶个位同学",
        one_yuewen_to_append="𠮶个位同学",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="今天的早会主要是跟大家分享",
        one_yuewen_start="",
        two_zhongwen="一个重要主题：",
        two_yuewen_end="",
        yuewen_to_distribute="今次座会系要同大家分享一个可重要嘅主题",
        one_yuewen_to_append="今次座会系要同大家分享",
        two_yuewen_to_prepend="一个可重要嘅主题",
    ),
]
distribute_test_cases_block_4 = [
    DistributeTestCase(
        one_zhongwen="⋯还有一个很疼我们",
        one_yuewen_start="",
        two_zhongwen="就是有点游魂的Miss Chan",
        two_yuewen_end="不过就有少少失魂嘅班主有MissChan",
        yuewen_to_distribute="仲有一个好疼我哋",
        one_yuewen_to_append="仲有一个好疼我哋",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="菇时同学！　　到！",
        one_yuewen_start="到Boosie同学",
        two_zhongwen="得巴同学！　　到！",
        two_yuewen_end="德巴同学",
        yuewen_to_distribute="到",
        one_yuewen_to_append="到",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="得巴同学！　　到！",
        one_yuewen_start="德巴同学",
        two_zhongwen="阿May同学！　　到！",
        two_yuewen_end="阿May同学到",
        yuewen_to_distribute="到",
        one_yuewen_to_append="到",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="阿June同学！　　到！",
        one_yuewen_start="阿June同学",
        two_zhongwen="阿May同学！　　到！",
        two_yuewen_end="阿May同学到",
        yuewen_to_distribute="到",
        one_yuewen_to_append="到",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="麦唛同学！　　到！",
        one_yuewen_start="到麦麦同学",
        two_zhongwen="菇时同学！　　到！",
        two_yuewen_end="Boosie同学到",
        yuewen_to_distribute="到",
        one_yuewen_to_append="到",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="还有谁没点过吗？",
        one_yuewen_start="到好",
        two_zhongwen="麦兜！",
        two_yuewen_end="猫",
        yuewen_to_distribute="仲有边个未点",
        one_yuewen_to_append="仲有边个未点",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="我好像觉得呢⋯",
        one_yuewen_start="即系呢",
        two_zhongwen="有什么人在喊我似的",
        two_yuewen_end="好似有人嗌紧我个名噉嘅",
        yuewen_to_distribute="我个心总系仁住仁住",
        one_yuewen_to_append="我个心总系仁住仁住",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="妈妈说吃橙可通大便",
        one_yuewen_start="妈妈话食橙会通大",
        two_zhongwen="「疴」这个我明白，可是「烂﹣煮」呢？",
        two_yuewen_end="噢呢个我明白但系橙呢",
        yuewen_to_distribute="变",
        one_yuewen_to_append="变",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="还有这个「芭﹣娜﹣娜」香蕉",
        one_yuewen_start="仲有呢个啊芭拉娜啊",
        two_zhongwen="为什么雨伞又会是「暗﹣芭﹣娜﹣娜」呢？",
        two_yuewen_end="点解雨姐会叫做暗芭拉娜呢",
        yuewen_to_distribute="香蕉啊",
        one_yuewen_to_append="香蕉啊",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="再念大学⋯",
        one_yuewen_start="",
        two_zhongwen="当我大学毕业的时候",
        two_yuewen_end="等我大学毕业𠮶阵",
        yuewen_to_distribute="再入埋大学",
        one_yuewen_to_append="再入埋大学",
        two_yuewen_to_prepend="",
    ),
]
distribute_test_cases_block_5 = []
distribute_test_cases_block_6 = []
distribute_test_cases_block_7 = []
distribute_test_cases_block_8 = []
distribute_test_cases_block_9 = []
distribute_test_cases_block_10 = []
distribute_test_cases_block_11 = []
distribute_test_cases_block_12 = []
distribute_test_cases_block_13 = []
distribute_test_cases_block_14 = []
distribute_test_cases_block_15 = []
distribute_test_cases_block_16 = []
distribute_test_cases_block_17 = []
distribute_test_cases_block_18 = []
distribute_test_cases_block_19 = []
distribute_test_cases_block_20 = []
distribute_test_cases_block_21 = []
distribute_test_cases_block_22 = []
distribute_test_cases_block_23 = []
distribute_test_cases_block_24 = []
distribute_test_cases_block_25 = []
distribute_test_cases_block_26 = []
distribute_test_cases_block_27 = []
distribute_test_cases_block_28 = []
distribute_test_cases_block_29 = []
distribute_test_cases_block_30 = []
distribute_test_cases_block_31 = []
distribute_test_cases_block_32 = []
distribute_test_cases_block_33 = []
distribute_test_cases_block_34 = []
distribute_test_cases_block_35 = []
distribute_test_cases_block_36 = []
distribute_test_cases_block_37 = []
distribute_test_cases_block_38 = []
distribute_test_cases_block_39 = []
distribute_test_cases_block_40 = []
distribute_test_cases_block_41 = []
distribute_test_cases_block_42 = []
distribute_test_cases_block_43 = []
distribute_test_cases_block_44 = []
distribute_test_cases_block_45 = []
distribute_test_cases_block_46 = []
distribute_test_cases_block_47 = []
distribute_test_cases_block_48 = []
distribute_test_cases_block_49 = []
distribute_test_cases_block_50 = []
distribute_test_cases_block_51 = []
distribute_test_cases_block_52 = []
distribute_test_cases_block_53 = []
distribute_test_cases_block_54 = []
distribute_test_cases_block_55 = []
distribute_test_cases_block_56 = []
distribute_test_cases_block_57 = []
distribute_test_cases_block_58 = []
distribute_test_cases_block_59 = []
distribute_test_cases_block_60 = []
distribute_test_cases_block_61 = []
distribute_test_cases_block_62 = []
distribute_test_cases_block_63 = []
distribute_test_cases_block_64 = []
distribute_test_cases_block_65 = []
distribute_test_cases_block_66 = []
distribute_test_cases_block_67 = []
distribute_test_cases_block_68 = []
distribute_test_cases_block_69 = []
distribute_test_cases_block_70 = [
    DistributeTestCase(
        one_zhongwen="特餐？特餐有什么吃？",
        one_yuewen_start="特餐",
        two_zhongwen="特餐即是午餐呀",
        two_yuewen_end="特餐就即系午餐啰",
        yuewen_to_distribute="特餐有咩食㗎",
        one_yuewen_to_append="特餐有咩食㗎",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="午餐又吃什么呢？",
        one_yuewen_start="",
        two_zhongwen="都是晚餐那些吧",
        two_yuewen_end="",
        yuewen_to_distribute="午餐食乜嘢㗎",
        one_yuewen_to_append="午餐食乜嘢㗎",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="都是晚餐那些吧",
        one_yuewen_start="",
        two_zhongwen="什么是晚餐？",
        two_yuewen_end="",
        yuewen_to_distribute="都系晚餐𠮶啲嘢啰",
        one_yuewen_to_append="都系晚餐𠮶啲嘢啰",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="什么是晚餐？",
        one_yuewen_start="",
        two_zhongwen="跟快餐一样",
        two_yuewen_end="",
        yuewen_to_distribute="咁乜嘢系晚餐呀",
        one_yuewen_to_append="咁乜嘢系晚餐呀",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="跟快餐一样",
        one_yuewen_start="",
        two_zhongwen="快餐吃什么？",
        two_yuewen_end="",
        yuewen_to_distribute="同快餐一样啰",
        one_yuewen_to_append="同快餐一样啰",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="快餐吃什么？",
        one_yuewen_start="",
        two_zhongwen="唉，快餐不就是常餐",
        two_yuewen_end="系快餐就即系上餐啰",
        yuewen_to_distribute="咁快餐食咩㗎",
        one_yuewen_to_append="咁快餐食咩㗎",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="妈妈，改快餐吧",
        one_yuewen_start="妈妈",
        two_zhongwen="快餐有什么？",
        two_yuewen_end="",
        yuewen_to_distribute="不如改快餐啦",
        one_yuewen_to_append="不如改快餐啦",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="快餐有什么？",
        one_yuewen_start="",
        two_zhongwen="快餐即是常餐",
        two_yuewen_end="快餐即系上餐",
        yuewen_to_distribute="快餐有咩㗎",
        one_yuewen_to_append="快餐有咩㗎",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="常餐又有什么呢？",
        one_yuewen_start="",
        two_zhongwen="常餐即是午餐",
        two_yuewen_end="上餐就即系午餐啰",
        yuewen_to_distribute="咁上餐有咩㗎",
        one_yuewen_to_append="咁上餐有咩㗎",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="那么午餐又有什么吃？",
        one_yuewen_start="哎呀",
        two_zhongwen="午餐跟晚餐一样",
        two_yuewen_end="",
        yuewen_to_distribute="咁午餐有咩食呀",
        one_yuewen_to_append="咁午餐有咩食呀",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="午餐跟晚餐一样",
        one_yuewen_start="",
        two_zhongwen="晚餐呢？",
        two_yuewen_end="",
        yuewen_to_distribute="午餐同晚餐一样㗎",
        one_yuewen_to_append="午餐同晚餐一样㗎",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="晚餐呢？",
        one_yuewen_start="",
        two_zhongwen="晚餐不就是特餐",
        two_yuewen_end="",
        yuewen_to_distribute="咁晚餐呢",
        one_yuewen_to_append="咁晚餐呢",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="晚餐不就是特餐",
        one_yuewen_start="",
        two_zhongwen="不是说特餐卖光了吗？",
        two_yuewen_end="咁你头先又话冇特餐",
        yuewen_to_distribute="晚餐就即系特餐啰",
        one_yuewen_to_append="晚餐就即系特餐啰",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="特餐卖光了，要试试快餐吗？都一样的",
        one_yuewen_start="系呀特餐系卖晒呀咁你试唔试下个快餐啦",
        two_zhongwen="来两份快餐吧",
        two_yuewen_end="咁两份快餐啦",
        yuewen_to_distribute="一样嘅啫",
        one_yuewen_to_append="一样嘅啫",
        two_yuewen_to_prepend="",
    ),
]
distribute_test_cases_block_71 = [
    DistributeTestCase(
        one_zhongwen="太过分了吧？你们究竟有吃的没？",
        one_yuewen_start="嚟唔嚟普啲呀",
        two_zhongwen="午餐吧，午餐精采呀",
        two_yuewen_end="午餐啦",
        yuewen_to_distribute="噉你哋究竟有啲咩餐呀",
        one_yuewen_to_append="噉你哋究竟有啲咩餐呀",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="跟晚餐一样精采",
        one_yuewen_start="点好嘢法呀",
        two_zhongwen="晚餐又怎样呢？",
        two_yuewen_end="",
        yuewen_to_distribute="同晚餐一样咁好嘢",
        one_yuewen_to_append="同晚餐一样咁好嘢",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="晚餐又怎样呢？",
        one_yuewen_start="",
        two_zhongwen="跟常餐一样精采",
        two_yuewen_end="",
        yuewen_to_distribute="噉晚餐又点好嘢法呀",
        one_yuewen_to_append="噉晚餐又点好嘢法呀",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="跟常餐一样精采",
        one_yuewen_start="",
        two_zhongwen="常餐又怎样呢？",
        two_yuewen_end="",
        yuewen_to_distribute="同上餐一样咁好嘢啰",
        one_yuewen_to_append="同上餐一样咁好嘢啰",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="常餐又怎样呢？",
        one_yuewen_start="",
        two_zhongwen="常餐早卖光了，你说精采不？",
        two_yuewen_end="上餐上餐一早卖晒啦你话好唔好嘢",
        yuewen_to_distribute="噉上餐又点好嘢法呀",
        one_yuewen_to_append="噉上餐又点好嘢法呀",
        two_yuewen_to_prepend="",
    ),
]
distribute_test_cases_block_72 = [
    DistributeTestCase(
        one_zhongwen="对不起，午餐卖光了",
        one_yuewen_start="唔好意思",
        two_zhongwen="要试试我们的晚餐吗？都一样的",
        two_yuewen_end="试唔试下我哋嘅晚餐啦",
        yuewen_to_distribute="午餐卖晒",
        one_yuewen_to_append="午餐卖晒",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="唉，说是说晚餐，还不就是午餐？",
        one_yuewen_start="系个名叫晚餐啫",
        two_zhongwen="好吧好吧，拜托！两份晚餐！快！",
        two_yuewen_end="好啦好啦怕咗你啦要两份晚餐啦",
        yuewen_to_distribute="其实唔系真系午餐",
        one_yuewen_to_append="其实唔系真系午餐",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="好吧好吧，拜托！两份晚餐！快！",
        one_yuewen_start="好啦好啦怕咗你啦要两份晚餐啦",
        two_zhongwen="要快吗？那得吃快餐了！",
        two_yuewen_end="想快想快就要快餐啊",
        yuewen_to_distribute="快啲手啊",
        one_yuewen_to_append="快啲手啊",
        two_yuewen_to_prepend="",
    ),
]
mlamd_distribute_test_cases: list[DistributeTestCase] = sum(
    (globals()[f"distribute_test_cases_block_{i}"] for i in range(73)), []
)
"""MLAMD 粤文 distribution test cases."""
# endregion


# region 粤文 Shift Test Cases
shift_test_cases_block_0 = [
    ShiftTestCase(
        one_zhongwen="在麦太即将临盆的时候",
        one_yuewen="就喺麦太快要临盘嘅时候",
        two_zhongwen="一只胶兜在九龙上空飞过",
        two_yuewen="有一个胶兜喺九龙上空飞过",
        one_yuewen_shifted="就喺麦太快要临盘嘅时候",
        two_yuewen_shifted="有一个胶兜喺九龙上空飞过",
    ),
    ShiftTestCase(
        one_zhongwen="一只胶兜在九龙上空飞过",
        one_yuewen="有一个胶兜喺九龙上空飞过",
        two_zhongwen="沿荔枝角道直出大角咀道",
        two_yuewen="沿住荔枝角度直出大角咀度",
        one_yuewen_shifted="有一个胶兜喺九龙上空飞过",
        two_yuewen_shifted="沿住荔枝角度直出大角咀度",
    ),
    ShiftTestCase(
        one_zhongwen="沿荔枝角道直出大角咀道",
        one_yuewen="沿住荔枝角度直出大角咀度",
        two_zhongwen="经好彩酒家左转花园街乐园牛丸王⋯",
        two_yuewen="经过好彩走家再左转返出花园街乐园牛园望对上",
        one_yuewen_shifted="沿住荔枝角度直出大角咀度",
        two_yuewen_shifted="经过好彩走家再左转返出花园街乐园牛园望对上",
    ),
    ShiftTestCase(
        one_zhongwen="经好彩酒家左转花园街乐园牛丸王⋯",
        one_yuewen="经过好彩走家再左转返出花园街乐园牛园望对上",
        two_zhongwen="更正一下：",
        two_yuewen="都系唔好",
        one_yuewen_shifted="经过好彩走家再左转返出花园街乐园牛园望对上",
        two_yuewen_shifted="都系唔好",
    ),
    ShiftTestCase(
        one_zhongwen="更正一下：",
        one_yuewen="都系唔好",
        two_zhongwen="先到街市大楼妹记鱼腩粥外边",
        two_yuewen="先去街市大楼𠮶间妹记鱼腩粥𠮶度",
        one_yuewen_shifted="都系唔好",
        two_yuewen_shifted="先去街市大楼𠮶间妹记鱼腩粥𠮶度",
    ),
    ShiftTestCase(
        one_zhongwen="先到街市大楼妹记鱼腩粥外边",
        one_yuewen="先去街市大楼𠮶间妹记鱼腩粥𠮶度",
        two_zhongwen="转呀，转⋯再更正一下：",
        two_yuewen="转下转下都系唔好",
        one_yuewen_shifted="先去街市大楼𠮶间妹记鱼腩粥𠮶度",
        two_yuewen_shifted="转下转下都系唔好",
    ),
    ShiftTestCase(
        one_zhongwen="转呀，转⋯再更正一下：",
        one_yuewen="转下转下都系唔好",
        two_zhongwen="直出亚皆老街跨过火车桥右转太平道",
        two_yuewen="都系出返去阿街路街飞过火车桥右转入太平道",
        one_yuewen_shifted="转下转下都系唔好",
        two_yuewen_shifted="都系出返去阿街路街飞过火车桥右转入太平道",
        include_in_prompt=True,
    ),
    ShiftTestCase(
        one_zhongwen="直出亚皆老街跨过火车桥右转太平道",
        one_yuewen="都系出返去阿街路街飞过火车桥右转入太平道",
        two_zhongwen="再右拐窝打老道向女人街方向飞⋯",
        two_yuewen="再右转抹返出去窝打炉道向女人街方向飞下下",
        one_yuewen_shifted="都系出返去阿街路街飞过火车桥右转入太平道",
        two_yuewen_shifted="再右转抹返出去窝打炉道向女人街方向飞下下",
    ),
    ShiftTestCase(
        one_zhongwen="再右拐窝打老道向女人街方向飞⋯",
        one_yuewen="再右转抹返出去窝打炉道向女人街方向飞下下",
        two_zhongwen="飞呀，飞⋯",
        two_yuewen="飞下飞下",
        one_yuewen_shifted="再右转抹返出去窝打炉道向女人街方向飞下下",
        two_yuewen_shifted="飞下飞下",
        include_in_prompt=True,
    ),
    ShiftTestCase(
        one_zhongwen="飞呀，飞⋯",
        one_yuewen="飞下飞下",
        two_zhongwen="胶兜最后飞进广华医院候产房",
        two_yuewen="最后胶兜飞咗入广华医院嘅后产房",
        one_yuewen_shifted="飞下飞下",
        two_yuewen_shifted="最后胶兜飞咗入广华医院嘅后产房",
    ),
    ShiftTestCase(
        one_zhongwen="胶兜最后飞进广华医院候产房",
        one_yuewen="最后胶兜飞咗入广华医院嘅后产房",
        two_zhongwen="也就是在麦太右边额角上⋯",
        two_yuewen="亦即系麦太右边云晶对上",
        one_yuewen_shifted="最后胶兜飞咗入广华医院嘅后产房",
        two_yuewen_shifted="亦即系麦太右边云晶对上",
    ),
    ShiftTestCase(
        one_zhongwen="也就是在麦太右边额角上⋯",
        one_yuewen="亦即系麦太右边云晶对上",
        two_zhongwen="更正：左边额角上⋯",
        two_yuewen="都系唔好左边云晶对上",
        one_yuewen_shifted="亦即系麦太右边云晶对上",
        two_yuewen_shifted="都系唔好左边云晶对上",
    ),
    ShiftTestCase(
        one_zhongwen="更正：左边额角上⋯",
        one_yuewen="都系唔好左边云晶对上",
        two_zhongwen="转呀，转⋯",
        two_yuewen="转下转下转下噉",
        one_yuewen_shifted="都系唔好左边云晶对上",
        two_yuewen_shifted="转下转下转下噉",
    ),
    ShiftTestCase(
        one_zhongwen="转呀，转⋯",
        one_yuewen="转下转下转下噉",
        two_zhongwen="麦太认定这是异像",
        two_yuewen="麦太认定呢个系异象",
        one_yuewen_shifted="转下转下转下噉",
        two_yuewen_shifted="麦太认定呢个系异象",
    ),
    ShiftTestCase(
        one_zhongwen="麦太认定这是异像",
        one_yuewen="麦太认定呢个系异象",
        two_zhongwen="于是向额角上的胶兜许愿",
        two_yuewen="于是向云晶对上嘅胶兜许愿",
        one_yuewen_shifted="麦太认定呢个系异象",
        two_yuewen_shifted="于是向云晶对上嘅胶兜许愿",
    ),
    ShiftTestCase(
        one_zhongwen="于是向额角上的胶兜许愿",
        one_yuewen="于是向云晶对上嘅胶兜许愿",
        two_zhongwen="脑海中同时出现即将诞生的儿子容貌⋯",
        two_yuewen="而脑入面亦即时出现咗快要出世个仔嘅样",
        one_yuewen_shifted="于是向云晶对上嘅胶兜许愿",
        two_yuewen_shifted="而脑入面亦即时出现咗快要出世个仔嘅样",
    ),
    ShiftTestCase(
        one_zhongwen="脑海中同时出现即将诞生的儿子容貌⋯",
        one_yuewen="而脑入面亦即时出现咗快要出世个仔嘅样",
        two_zhongwen="希望他好聪明，读书好叻！",
        two_yuewen="希望佢好聪明读书好叻",
        one_yuewen_shifted="而脑入面亦即时出现咗快要出世个仔嘅样",
        two_yuewen_shifted="希望佢好聪明读书好叻",
    ),
    ShiftTestCase(
        one_zhongwen="希望他好聪明，读书好叻！",
        one_yuewen="希望佢好聪明读书好叻",
        two_zhongwen="胶兜对麦太的愿望似乎没有反应",
        two_yuewen="胶兜对麦太嘅愿望似乎冇咩表示",
        one_yuewen_shifted="希望佢好聪明读书好叻",
        two_yuewen_shifted="胶兜对麦太嘅愿望似乎冇咩表示",
    ),
    ShiftTestCase(
        one_zhongwen="胶兜对麦太的愿望似乎没有反应",
        one_yuewen="胶兜对麦太嘅愿望似乎冇咩表示",
        two_zhongwen="于是她向胶兜补充说：",
        two_yuewen="于是佢对住胶兜补充噉话",
        one_yuewen_shifted="胶兜对麦太嘅愿望似乎冇咩表示",
        two_yuewen_shifted="于是佢对住胶兜补充噉话",
    ),
    ShiftTestCase(
        one_zhongwen="于是她向胶兜补充说：",
        one_yuewen="于是佢对住胶兜补充噉话",
        two_zhongwen="或者读书唔叻，工作叻呢？",
        two_yuewen="或者读书唔叻出嚟做嘢叻啦",
        one_yuewen_shifted="于是佢对住胶兜补充噉话",
        two_yuewen_shifted="或者读书唔叻出嚟做嘢叻啦",
    ),
    ShiftTestCase(
        one_zhongwen="或者读书唔叻，工作叻呢？",
        one_yuewen="或者读书唔叻出嚟做嘢叻啦",
        two_zhongwen="又或者⋯",
        two_yuewen="又或者呢",
        one_yuewen_shifted="或者读书唔叻出嚟做嘢叻啦",
        two_yuewen_shifted="又或者呢",
    ),
    ShiftTestCase(
        one_zhongwen="又或者⋯",
        one_yuewen="又或者呢",
        two_zhongwen="又或者好靓仔，好靓仔",
        two_yuewen="又或者系好靓仔好靓仔",
        one_yuewen_shifted="又或者呢",
        two_yuewen_shifted="又或者系好靓仔好靓仔",
        include_in_prompt=True,
    ),
    ShiftTestCase(
        one_zhongwen="跟周润发，梁朝伟那么靓仔！",
        one_yuewen="好似周润发同埋梁朝伟咁靓仔",
        two_zhongwen="胶兜仍然在转，毫无点头迹象",
        two_yuewen="胶兜依然系噉喺度转好似一啲应承嘅迹象都冇",
        one_yuewen_shifted="好似周润发同埋梁朝伟咁靓仔",
        two_yuewen_shifted="胶兜依然系噉喺度转好似一啲应承嘅迹象都冇",
    ),
    ShiftTestCase(
        one_zhongwen="胶兜仍然在转，毫无点头迹象",
        one_yuewen="胶兜依然系噉喺度转好似一啲应承嘅迹象都冇",
        two_zhongwen="麦太一时心虚",
        two_yuewen="麦太一时心虚",
        one_yuewen_shifted="胶兜依然系噉喺度转好似一啲应承嘅迹象都冇",
        two_yuewen_shifted="麦太一时心虚",
    ),
    ShiftTestCase(
        one_zhongwen="麦太一时心虚",
        one_yuewen="麦太一时心虚",
        two_zhongwen="赶忙趁胶兜落地前另许一个愿望：",
        two_yuewen="嗱嗱嗱喺胶兜未落地之前起过另外一个愿望",
        one_yuewen_shifted="麦太一时心虚",
        two_yuewen_shifted="嗱嗱嗱喺胶兜未落地之前起过另外一个愿望",
    ),
    ShiftTestCase(
        one_zhongwen="赶忙趁胶兜落地前另许一个愿望：",
        one_yuewen="嗱嗱嗱喺胶兜未落地之前起过另外一个愿望",
        two_zhongwen="唔聪明唔靓仔也算了，只要福星高照",
        two_yuewen="就算唔系咁聪明同咁靓仔只要复星高照",
        one_yuewen_shifted="嗱嗱嗱喺胶兜未落地之前起过另外一个愿望",
        two_yuewen_shifted="就算唔系咁聪明同咁靓仔只要复星高照",
    ),
    ShiftTestCase(
        one_zhongwen="唔聪明唔靓仔也算了，只要福星高照",
        one_yuewen="就算唔系咁聪明同咁靓仔只要复星高照",
        two_zhongwen="一世够运，逢凶化吉！",
        two_yuewen="一世救运乜嘢事都逢凶化㗎喇",
        one_yuewen_shifted="就算唔系咁聪明同咁靓仔只要复星高照",
        two_yuewen_shifted="一世救运乜嘢事都逢凶化㗎喇",
        include_in_prompt=True,
    ),
    ShiftTestCase(
        one_zhongwen="一世够运，逢凶化吉！",
        one_yuewen="一世救运乜嘢事都逢凶化㗎喇",
        two_zhongwen="靠自己能力解决事情当然最好",
        two_yuewen="佢靠自己有料解决啲嘢就梗系好啦",
        one_yuewen_shifted="一世救运乜嘢事都逢凶化㗎喇",
        two_yuewen_shifted="佢靠自己有料解决啲嘢就梗系好啦",
    ),
    ShiftTestCase(
        one_zhongwen="靠自己能力解决事情当然最好",
        one_yuewen="佢靠自己有料解决啲嘢就梗系好啦",
        two_zhongwen="不过运气还是很重要的",
        two_yuewen="不过运气都好紧要㖞",
        one_yuewen_shifted="佢靠自己有料解决啲嘢就梗系好啦",
        two_yuewen_shifted="不过运气都好紧要㖞",
    ),
    ShiftTestCase(
        one_zhongwen="不过运气还是很重要的",
        one_yuewen="不过运气都好紧要㖞",
        two_zhongwen="虽是说像梁朝伟周润发也行运定了",
        two_yuewen="虽然似梁朝伟周润发都唔返去冒运行",
        one_yuewen_shifted="不过运气都好紧要㖞",
        two_yuewen_shifted="虽然似梁朝伟周润发都唔返去冒运行",
    ),
    ShiftTestCase(
        one_zhongwen="虽是说像梁朝伟周润发也行运定了",
        one_yuewen="虽然似梁朝伟周润发都唔返去冒运行",
        two_zhongwen="但总得要叻仔呀！",
        two_yuewen="但系都要叻仔先得㗎",
        one_yuewen_shifted="虽然似梁朝伟周润发都唔返去冒运行",
        two_yuewen_shifted="但系都要叻仔先得㗎",
    ),
]
shift_test_cases_block_1 = [
    ShiftTestCase(
        one_zhongwen="最后，胶兜「嘀督」一声落地",
        one_yuewen="最后胶兜滴嘟一声咁落地",
        two_zhongwen="嘀督？嘀督，就是答应了",
        two_yuewen="滴嘟滴嘟㖞即系应承啦",
        one_yuewen_shifted="最后胶兜滴嘟一声咁落地",
        two_yuewen_shifted="滴嘟滴嘟㖞即系应承啦",
    ),
    ShiftTestCase(
        one_zhongwen="嘀督？嘀督，就是答应了",
        one_yuewen="滴嘟滴嘟㖞即系应承啦",
        two_zhongwen="麦太想，这次走运了！",
        two_yuewen="麦太心谂今次冇死喇",
        one_yuewen_shifted="滴嘟滴嘟㖞即系应承啦",
        two_yuewen_shifted="麦太心谂今次冇死喇",
    ),
    ShiftTestCase(
        one_zhongwen="麦太想，这次走运了！",
        one_yuewen="麦太心谂今次冇死喇",
        two_zhongwen="可是答应了些什么呢？",
        two_yuewen="但你应承咗啲咩呢",
        one_yuewen_shifted="麦太心谂今次冇死喇",
        two_yuewen_shifted="但你应承咗啲咩呢",
    ),
    ShiftTestCase(
        one_zhongwen="可是答应了些什么呢？",
        one_yuewen="但你应承咗啲咩呢",
        two_zhongwen="叻仔？好运？",
        two_yuewen="叻仔好运",
        one_yuewen_shifted="但你应承咗啲咩呢",
        two_yuewen_shifted="叻仔好运",
    ),
    ShiftTestCase(
        one_zhongwen="叻仔？好运？",
        one_yuewen="叻仔好运",
        two_zhongwen="还是似周润发？",
        two_yuewen="定系话自周人烦啊",
        one_yuewen_shifted="叻仔好运",
        two_yuewen_shifted="定系话自周人烦啊",
    ),
    ShiftTestCase(
        one_zhongwen="还是似周润发？",
        one_yuewen="定系话自周人烦啊",
        two_zhongwen="为了纪念这赐福的胶兜",
        two_yuewen="为咗纪念呢个赤幅嘅胶兜",
        one_yuewen_shifted="定系话自周人烦啊",
        two_yuewen_shifted="为咗纪念呢个赤幅嘅胶兜",
    ),
    ShiftTestCase(
        one_zhongwen="为了纪念这赐福的胶兜",
        one_yuewen="为咗纪念呢个赤幅嘅胶兜",
        two_zhongwen="麦太决定把儿子命名麦胶",
        two_yuewen="麦太决定将个仔嘅名叫做麦胶",
        one_yuewen_shifted="为咗纪念呢个赤幅嘅胶兜",
        two_yuewen_shifted="麦太决定将个仔嘅名叫做麦胶",
    ),
    ShiftTestCase(
        one_zhongwen="麦太决定把儿子命名麦胶",
        one_yuewen="麦太决定将个仔嘅名叫做麦胶",
        two_zhongwen="不行，胶胶声，多难听！",
        two_yuewen="都系唔好胶胶声咁难听",
        one_yuewen_shifted="麦太决定将个仔嘅名叫做麦胶",
        two_yuewen_shifted="都系唔好胶胶声咁难听",
    ),
    ShiftTestCase(
        one_zhongwen="不行，胶胶声，多难听！",
        one_yuewen="都系唔好胶胶声咁难听",
        two_zhongwen="还是唤他麦兜！",
        two_yuewen="不如叫麦兜啦",
        one_yuewen_shifted="都系唔好胶胶声咁难听",
        two_yuewen_shifted="不如叫麦兜啦",
    ),
    ShiftTestCase(
        one_zhongwen="还是唤他麦兜！",
        one_yuewen="不如叫麦兜啦",
        two_zhongwen="各位⋯",
        two_yuewen="各位",
        one_yuewen_shifted="不如叫麦兜啦",
        two_yuewen_shifted="各位",
    ),
    ShiftTestCase(
        one_zhongwen="各位⋯",
        one_yuewen="各位",
        two_zhongwen="我就是险些给定名麦胶的小朋友⋯",
        two_yuewen="我就系呢个差少少就叫做麦胶嘅小朋友",
        one_yuewen_shifted="各位",
        two_yuewen_shifted="我就系呢个差少少就叫做麦胶嘅小朋友",
    ),
    ShiftTestCase(
        one_zhongwen="我就是险些给定名麦胶的小朋友⋯",
        one_yuewen="我就系呢个差少少就叫做麦胶嘅小朋友",
        two_zhongwen="麦兜！",
        two_yuewen="麦兜",
        one_yuewen_shifted="我就系呢个差少少就叫做麦胶嘅小朋友",
        two_yuewen_shifted="麦兜",
    ),
]
shift_test_cases_block_2 = [
    ShiftTestCase(
        one_zhongwen="麦太，没见面一阵",
        one_yuewen="咦麦太",
        two_zhongwen="怎么小腿粗起来了？",
        two_yuewen="咩唔见你一排个脚刮囊粗咗咁多呀",
        one_yuewen_shifted="咦麦太咩唔见你一排",
        two_yuewen_shifted="个脚刮囊粗咗咁多呀",
    ),
    ShiftTestCase(
        one_zhongwen="怎么小腿粗起来了？",
        one_yuewen="个脚刮囊粗咗咁多呀",
        two_zhongwen="可怜呀，每天扑来扑去⋯",
        two_yuewen="鬼咩",
        one_yuewen_shifted="个脚刮囊粗咗咁多呀",
        two_yuewen_shifted="鬼咩",
        include_in_prompt=True,
    ),
    ShiftTestCase(
        one_zhongwen="可怜呀，每天扑来扑去⋯",
        one_yuewen="鬼咩",
        two_zhongwen="替儿子找幼稚园！",
        two_yuewen="日日扑嚟扑去同我仔揾幼稚园吖嘛",
        one_yuewen_shifted="鬼咩日日扑嚟扑去",
        two_yuewen_shifted="同我仔揾幼稚园吖嘛",
        include_in_prompt=True,
    ),
    ShiftTestCase(
        one_zhongwen="替儿子找幼稚园！",
        one_yuewen="同我仔揾幼稚园吖嘛",
        two_zhongwen="怎么不试一试好彩酒楼对面",
        two_yuewen="点解唔试下好彩走楼斜对面",
        one_yuewen_shifted="同我仔揾幼稚园吖嘛",
        two_yuewen_shifted="点解唔试下好彩走楼斜对面",
    ),
    ShiftTestCase(
        one_zhongwen="怎么不试一试好彩酒楼对面",
        one_yuewen="点解唔试下好彩走楼斜对面",
        two_zhongwen="旧中侨国货楼上的⋯",
        two_yuewen="",
        one_yuewen_shifted="点解唔试下好彩走楼斜对面",
        two_yuewen_shifted="",
    ),
    ShiftTestCase(  # NEXT ROUND
        one_zhongwen="怎么不试一试好彩酒楼对面",
        one_yuewen="点解唔试下好彩走楼斜对面",
        two_zhongwen="旧中侨国货楼上的⋯",
        two_yuewen="旧中桥百货公司楼上𠮶间",
        one_yuewen_shifted="点解唔试下好彩走楼斜对面",
        two_yuewen_shifted="旧中桥百货公司楼上𠮶间",
    ),
    ShiftTestCase(
        one_zhongwen="旧中侨国货楼上的⋯",
        one_yuewen="",
        two_zhongwen="春田花花幼稚园？",
        two_yuewen="旧中桥百货公司楼上𠮶间春田花花幼稚园呢",
        one_yuewen_shifted="旧中桥百货公司楼上𠮶间",
        two_yuewen_shifted="春田花花幼稚园呢",
        include_in_prompt=True,
    ),
    ShiftTestCase(  # NEXT ROUND
        one_zhongwen="旧中侨国货楼上的⋯",
        one_yuewen="旧中桥百货公司楼上𠮶间",
        two_zhongwen="春田花花幼稚园？",
        two_yuewen="春田花花幼稚园呢",
        one_yuewen_shifted="旧中桥百货公司楼上𠮶间",
        two_yuewen_shifted="春田花花幼稚园呢",
    ),
    ShiftTestCase(
        one_zhongwen="春田花花幼稚园？",
        one_yuewen="春田花花幼稚园呢",
        two_zhongwen="就是座落界限街南昌街交界⋯",
        two_yuewen="就系坐落喺界限街同南昌街交界",
        one_yuewen_shifted="春田花花幼稚园呢",
        two_yuewen_shifted="就系坐落喺界限街同南昌街交界",
    ),
    ShiftTestCase(
        one_zhongwen="就是座落界限街南昌街交界⋯",
        one_yuewen="就系坐落喺界限街同南昌街交界",
        two_zhongwen="银城美食广场附近的⋯",
        two_yuewen="",
        one_yuewen_shifted="就系坐落喺界限街同南昌街交界",
        two_yuewen_shifted="",
    ),
    ShiftTestCase(  # NEXT ROUND
        one_zhongwen="就是座落界限街南昌街交界⋯",
        one_yuewen="就系坐落喺界限街同南昌街交界",
        two_zhongwen="银城美食广场附近的⋯",
        two_yuewen="银城美食广场附近𠮶间",
        one_yuewen_shifted="就系坐落喺界限街同南昌街交界",
        two_yuewen_shifted="银城美食广场附近𠮶间",
    ),
    ShiftTestCase(
        one_zhongwen="银城美食广场附近的⋯",
        one_yuewen="",
        two_zhongwen="春田花花幼稚园？",
        two_yuewen="银城美食广场附近𠮶间春田花花幼稚园呀",
        one_yuewen_shifted="银城美食广场附近𠮶间",
        two_yuewen_shifted="春田花花幼稚园呀",
    ),
    ShiftTestCase(  # NEXT ROUND
        one_zhongwen="银城美食广场附近的⋯",
        one_yuewen="银城美食广场附近𠮶间",
        two_zhongwen="春田花花幼稚园？",
        two_yuewen="春田花花幼稚园呀",
        one_yuewen_shifted="银城美食广场附近𠮶间",
        two_yuewen_shifted="春田花花幼稚园呀",
    ),
    ShiftTestCase(
        one_zhongwen="春田花花幼稚园？",
        one_yuewen="春田花花幼稚园呀",
        two_zhongwen="对！深水埗地铁站步行不用10分钟！",
        two_yuewen="系呀深水埗地铁站口行过去唔使十分钟呀",
        one_yuewen_shifted="春田花花幼稚园呀",
        two_yuewen_shifted="系呀深水埗地铁站口行过去唔使十分钟呀",
    ),
    ShiftTestCase(
        one_zhongwen="对！深水埗地铁站步行不用10分钟！",
        one_yuewen="系呀深水埗地铁站口行过去唔使十分钟呀",
        two_zhongwen="春田花花幼稚园，师资优良⋯",
        two_yuewen="春田花花幼稚园诗诗优良",
        one_yuewen_shifted="系呀深水埗地铁站口行过去唔使十分钟呀",
        two_yuewen_shifted="春田花花幼稚园诗诗优良",
    ),
    ShiftTestCase(
        one_zhongwen="春田花花幼稚园，师资优良⋯",
        one_yuewen="春田花花幼稚园诗诗优良",
        two_zhongwen="而且还有西人教英文！",
        two_yuewen="仲系西人教英文添㗎",
        one_yuewen_shifted="春田花花幼稚园诗诗优良",
        two_yuewen_shifted="仲系西人教英文添㗎",
    ),
    ShiftTestCase(
        one_zhongwen="而且还有西人教英文！",
        one_yuewen="仲系西人教英文添㗎",
        two_zhongwen="西人教英文？",
        two_yuewen="咦西人教英文",
        one_yuewen_shifted="仲系西人教英文添㗎",
        two_yuewen_shifted="咦西人教英文",
        include_in_prompt=True,
    ),
    ShiftTestCase(
        one_zhongwen="西人教英文？",
        one_yuewen="咦西人教英文",
        two_zhongwen="是呀！",
        two_yuewen="",
        one_yuewen_shifted="咦西人教英文",
        two_yuewen_shifted="",
        include_in_prompt=True,
    ),
    ShiftTestCase(
        one_zhongwen="是呀！",
        one_yuewen="",
        two_zhongwen="春田花花，确有好多西人呀！",
        two_yuewen="系呀春田花花真系好多西人㗎",
        one_yuewen_shifted="系呀",
        two_yuewen_shifted="春田花花真系好多西人㗎",
        include_in_prompt=True,
    ),
]
shift_test_cases_block_3 = [
    ShiftTestCase(
        one_zhongwen="〝鹅闷是春天滴化！〞",
        one_yuewen="",
        two_zhongwen="这个猪样白兔小朋友⋯",
        two_yuewen="呢个扮紧白兔猪样嘅小朋友",
        one_yuewen_shifted="",
        two_yuewen_shifted="呢个扮紧白兔猪样嘅小朋友",
        include_in_prompt=True,
    ),
    ShiftTestCase(
        one_zhongwen="这个猪样白兔小朋友⋯",
        one_yuewen="呢个扮紧白兔猪样嘅小朋友",
        two_zhongwen="横看竖看也不像发哥伟仔的一个⋯",
        two_yuewen="即系横睇掂睇都唔似发哥或者位仔𠮶个呢",
        one_yuewen_shifted="呢个扮紧白兔猪样嘅小朋友",
        two_yuewen_shifted="即系横睇掂睇都唔似发哥或者位仔𠮶个呢",
    ),
    ShiftTestCase(
        one_zhongwen="横看竖看也不像发哥伟仔的一个⋯",
        one_yuewen="即系横睇掂睇都唔似发哥或者位仔𠮶个呢",
        two_zhongwen="就是我，麦兜",
        two_yuewen="就系我麦兜",
        one_yuewen_shifted="即系横睇掂睇都唔似发哥或者位仔𠮶个呢",
        two_yuewen_shifted="就系我麦兜",
    ),
    ShiftTestCase(
        one_zhongwen="就是我，麦兜",
        one_yuewen="就系我麦兜",
        two_zhongwen="这是我就读的幼稚园",
        two_yuewen="呢间就系我读嘅幼稚园",
        one_yuewen_shifted="就系我麦兜",
        two_yuewen_shifted="呢间就系我读嘅幼稚园",
    ),
    ShiftTestCase(
        one_zhongwen="这是我就读的幼稚园",
        one_yuewen="呢间就系我读嘅幼稚园",
        two_zhongwen="校长是潮州人",
        two_yuewen="校长系潮州人",
        one_yuewen_shifted="呢间就系我读嘅幼稚园",
        two_yuewen_shifted="校长系潮州人",
    ),
    ShiftTestCase(
        one_zhongwen="校长是潮州人",
        one_yuewen="校长系潮州人",
        two_zhongwen="可能是潮州口音的关系",
        two_yuewen="可能仲系讲紧潮州话嘅",
        one_yuewen_shifted="校长系潮州人",
        two_yuewen_shifted="可能仲系讲紧潮州话嘅",
    ),
    ShiftTestCase(
        one_zhongwen="可能是潮州口音的关系",
        one_yuewen="可能仲系讲紧潮州话嘅",
        two_zhongwen="这么多年来⋯",
        two_yuewen="所以咁多年嚟",
        one_yuewen_shifted="可能仲系讲紧潮州话嘅",
        two_yuewen_shifted="所以咁多年嚟",
    ),
    ShiftTestCase(
        one_zhongwen="这么多年来⋯",
        one_yuewen="所以咁多年嚟",
        two_zhongwen="我其实不大明白他的说话",
        two_yuewen="我其实唔系好知佢噏文",
        one_yuewen_shifted="所以咁多年嚟",
        two_yuewen_shifted="我其实唔系好知佢噏文",
    ),
    ShiftTestCase(
        one_zhongwen="我其实不大明白他的说话",
        one_yuewen="我其实唔系好知佢噏文",
        two_zhongwen="蛋挞！　　蛋挞！",
        two_yuewen="大湖荒岩宅",
        one_yuewen_shifted="我其实唔系好知佢噏文",
        two_yuewen_shifted="大湖荒岩宅",
    ),
    ShiftTestCase(  # REVIEW
        one_zhongwen="蛋挞！　　蛋挞！",
        one_yuewen="大湖荒岩宅",
        two_zhongwen="荔芋火鸭礼！　　荔芋火鸭礼！",
        two_yuewen="湾吉校坟交涉设",
        one_yuewen_shifted="大湖荒岩宅",
        two_yuewen_shifted="湾吉校坟交涉设",
    ),
    ShiftTestCase(  # REVIEW
        one_zhongwen="荔芋火鸭礼！　　荔芋火鸭礼！",
        one_yuewen="湾吉校坟交涉设",
        two_zhongwen="忘记校训九十七⋯　　忘记校训九十七⋯",
        two_yuewen="",
        one_yuewen_shifted="湾吉校坟交涉设",
        two_yuewen_shifted="",
    ),
    ShiftTestCase(
        one_zhongwen="忘记校训九十七⋯　　忘记校训九十七⋯",
        one_yuewen="",
        two_zhongwen="也不能忘记校训九十八！",
        two_yuewen="都唔好湾吉校坟交涉白",
        one_yuewen_shifted="",
        two_yuewen_shifted="都唔好湾吉校坟交涉白",
    ),
    ShiftTestCase(
        one_zhongwen="也不能忘记校训九十八！",
        one_yuewen="都唔好湾吉校坟交涉白",
        two_zhongwen="也不能忘记校训九十八！",
        two_yuewen="",
        one_yuewen_shifted="都唔好湾吉校坟交涉白",
        two_yuewen_shifted="",
    ),
    ShiftTestCase(
        one_zhongwen="也不能忘记校训九十八！",
        one_yuewen="",
        two_zhongwen="好！各位同学⋯",
        two_yuewen="𠮶个位同学",
        one_yuewen_shifted="",
        two_yuewen_shifted="𠮶个位同学",
        include_in_prompt=True,
    ),
    ShiftTestCase(
        one_zhongwen="好！各位同学⋯",
        one_yuewen="𠮶个位同学",
        two_zhongwen="今天的早会主要是跟大家分享",
        two_yuewen="今次座会系要同大家分享",
        one_yuewen_shifted="𠮶个位同学",
        two_yuewen_shifted="今次座会系要同大家分享",
    ),
    ShiftTestCase(
        one_zhongwen="今天的早会主要是跟大家分享",
        one_yuewen="今次座会系要同大家分享",
        two_zhongwen="一个重要主题：",
        two_yuewen="一个可重要嘅主题",
        one_yuewen_shifted="今次座会系要同大家分享",
        two_yuewen_shifted="一个可重要嘅主题",
    ),
    ShiftTestCase(
        one_zhongwen="一个重要主题：",
        one_yuewen="一个可重要嘅主题",
        two_zhongwen="小朋友，这个月你们交过学费没有？",
        two_yuewen="小朋友你哋今个月交咗学费咩呀",
        one_yuewen_shifted="一个可重要嘅主题",
        two_yuewen_shifted="小朋友你哋今个月交咗学费咩呀",
    ),
    ShiftTestCase(
        one_zhongwen="小朋友，这个月你们交过学费没有？",
        one_yuewen="小朋友你哋今个月交咗学费咩呀",
        two_zhongwen="交过了！",
        two_yuewen="交",
        one_yuewen_shifted="小朋友你哋今个月交咗学费咩呀",
        two_yuewen_shifted="交",
        include_in_prompt=True,
    ),
    ShiftTestCase(
        one_zhongwen="交过了！",
        one_yuewen="交",
        two_zhongwen="太好了！大家去上堂吧",
        two_yuewen="哎好在噉大家可以返去上堂喇",
        one_yuewen_shifted="交",
        two_yuewen_shifted="哎好在噉大家可以返去上堂喇",
    ),
]
shift_test_cases_block_4 = [
    ShiftTestCase(
        one_zhongwen="你们可能觉得这间幼稚园很烂",
        one_yuewen="你哋可能觉得呢间幼稚园好逗利",
        two_zhongwen="可是，对我和我一班同学",
        two_yuewen="但系对于我同埋我班同学仔嚟讲",
        one_yuewen_shifted="你哋可能觉得呢间幼稚园好逗利",
        two_yuewen_shifted="但系对于我同埋我班同学仔嚟讲",
    ),
    ShiftTestCase(
        one_zhongwen="可是，对我和我一班同学",
        one_yuewen="但系对于我同埋我班同学仔嚟讲",
        two_zhongwen="这儿是我们最快乐，最美丽的乐园⋯",
        two_yuewen="呢度系我哋最快乐最美丽嘅乐园",
        one_yuewen_shifted="但系对于我同埋我班同学仔嚟讲",
        two_yuewen_shifted="呢度系我哋最快乐最美丽嘅乐园",
    ),
    ShiftTestCase(
        one_zhongwen="这儿是我们最快乐，最美丽的乐园⋯",
        one_yuewen="呢度系我哋最快乐最美丽嘅乐园",
        two_zhongwen="⋯还有一个很疼我们",
        two_yuewen="仲有一个好疼我哋",
        one_yuewen_shifted="呢度系我哋最快乐最美丽嘅乐园",
        two_yuewen_shifted="仲有一个好疼我哋",
    ),
    ShiftTestCase(
        one_zhongwen="⋯还有一个很疼我们",
        one_yuewen="仲有一个好疼我哋",
        two_zhongwen="就是有点游魂的Miss Chan",
        two_yuewen="不过就有少少失魂嘅班主有MissChan",
        one_yuewen_shifted="仲有一个好疼我哋",
        two_yuewen_shifted="不过就有少少失魂嘅班主有MissChan",
    ),
    ShiftTestCase(
        one_zhongwen="就是有点游魂的Miss Chan",
        one_yuewen="不过就有少少失魂嘅班主有MissChan",
        two_zhongwen="她的志愿是做第二个王菲",
        two_yuewen="佢嘅志愿系做下一个王妃",
        one_yuewen_shifted="不过就有少少失魂嘅班主有MissChan",
        two_yuewen_shifted="佢嘅志愿系做下一个王妃",
    ),
    ShiftTestCase(
        one_zhongwen="她的志愿是做第二个王菲",
        one_yuewen="佢嘅志愿系做下一个王妃",
        two_zhongwen="做第二个陈慧琳也可以",
        two_yuewen="或者系做下一个陈维林都得",
        one_yuewen_shifted="佢嘅志愿系做下一个王妃",
        two_yuewen_shifted="或者系做下一个陈维林都得",
    ),
    ShiftTestCase(
        one_zhongwen="做第二个陈慧琳也可以",
        one_yuewen="或者系做下一个陈维林都得",
        two_zhongwen="我们现在开始点名",
        two_yuewen="好喇我哋而家开始点名",
        one_yuewen_shifted="或者系做下一个陈维林都得",
        two_yuewen_shifted="好喇我哋而家开始点名",
    ),
    ShiftTestCase(
        one_zhongwen="我们现在开始点名",
        one_yuewen="好喇我哋而家开始点名",
        two_zhongwen="麦唛同学！　　到！",
        two_yuewen="麦麦同学",
        one_yuewen_shifted="好喇我哋而家开始点名",
        two_yuewen_shifted="麦麦同学",
    ),
    ShiftTestCase(
        one_zhongwen="麦唛同学！　　到！",
        one_yuewen="麦麦同学",
        two_zhongwen="亚辉同学！　　到！",
        two_yuewen="到阿辉同学",
        one_yuewen_shifted="麦麦同学到",
        two_yuewen_shifted="阿辉同学",
        include_in_prompt=True,
    ),
    ShiftTestCase(
        one_zhongwen="亚辉同学！　　到！",
        one_yuewen="阿辉同学",
        two_zhongwen="菇时同学！　　到！",
        two_yuewen="到Boosie同学到",
        one_yuewen_shifted="阿辉同学到",
        two_yuewen_shifted="Boosie同学到",
        include_in_prompt=False,
    ),
    ShiftTestCase(
        one_zhongwen="菇时同学！　　到！",
        one_yuewen="Boosie同学到",
        two_zhongwen="得巴同学！　　到！",
        two_yuewen="德巴同学到",
        one_yuewen_shifted="Boosie同学到",
        two_yuewen_shifted="德巴同学到",
        include_in_prompt=False,
    ),
    ShiftTestCase(
        one_zhongwen="得巴同学！　　到！",
        one_yuewen="德巴同学到",
        two_zhongwen="阿May同学！　　到！",
        two_yuewen="阿May同学到",
        one_yuewen_shifted="德巴同学到",
        two_yuewen_shifted="阿May同学到",
        include_in_prompt=False,
    ),
    ShiftTestCase(
        one_zhongwen="阿May同学！　　到！",
        one_yuewen="阿May同学到",
        two_zhongwen="阿June同学！　　到！",
        two_yuewen="阿June同学到",
        one_yuewen_shifted="阿May同学到",
        two_yuewen_shifted="阿June同学到",
        include_in_prompt=False,
    ),
    ShiftTestCase(
        one_zhongwen="阿June同学！　　到！",
        one_yuewen="阿June同学到",
        two_zhongwen="阿May同学！　　到！",
        two_yuewen="阿May同学到",
        one_yuewen_shifted="阿June同学到",
        two_yuewen_shifted="阿May同学到",
        include_in_prompt=False,
    ),
    ShiftTestCase(
        one_zhongwen="阿May同学！　　到！",
        one_yuewen="阿May同学到",
        two_zhongwen="麦唛同学！　　到！",
        two_yuewen="麦麦同学到",
        one_yuewen_shifted="阿May同学到",
        two_yuewen_shifted="麦麦同学到",
        include_in_prompt=False,
    ),
    ShiftTestCase(
        one_zhongwen="麦唛同学！　　到！",
        one_yuewen="麦麦同学到",
        two_zhongwen="阿May同学！",
        two_yuewen="",
        one_yuewen_shifted="麦麦同学到",
        two_yuewen_shifted="",
        include_in_prompt=False,
    ),
    ShiftTestCase(
        one_zhongwen="阿May同学！",
        one_yuewen="",
        two_zhongwen="Miss Chan，我点过两次了！",
        two_yuewen="阿May同学MissChan你点咗我两次喇",
        one_yuewen_shifted="阿May同学",
        two_yuewen_shifted="MissChan你点咗我两次喇",
        include_in_prompt=False,
    ),
    ShiftTestCase(
        one_zhongwen="Miss Chan，我点过两次了！",
        one_yuewen="MissChan你点咗我两次喇",
        two_zhongwen="呀，真的吗？",
        two_yuewen="啊系咩",
        one_yuewen_shifted="MissChan你点咗我两次喇",
        two_yuewen_shifted="啊系咩",
        include_in_prompt=False,
    ),
    ShiftTestCase(
        one_zhongwen="呀，真的吗？",
        one_yuewen="啊系咩",
        two_zhongwen="校长早晨！",
        two_yuewen="",
        one_yuewen_shifted="啊系咩",
        two_yuewen_shifted="",
        include_in_prompt=False,
    ),
    ShiftTestCase(
        one_zhongwen="校长再见！",
        one_yuewen="",
        two_zhongwen="我们现在继续点名",
        two_yuewen="好我哋而家继续点名",
        one_yuewen_shifted="",
        two_yuewen_shifted="好我哋而家继续点名",
        include_in_prompt=True,
    ),
    ShiftTestCase(
        one_zhongwen="我们现在继续点名",
        one_yuewen="好我哋而家继续点名",
        two_zhongwen="阿June同学！　　到！",
        two_yuewen="阿June同学",
        one_yuewen_shifted="好我哋而家继续点名",
        two_yuewen_shifted="阿June同学",
        include_in_prompt=False,
    ),
    ShiftTestCase(
        one_zhongwen="阿June同学！　　到！",
        one_yuewen="阿June同学",
        two_zhongwen="亚辉同学！　　到！",
        two_yuewen="到阿辉同学",
        one_yuewen_shifted="阿June同学到",
        two_yuewen_shifted="阿辉同学",
        include_in_prompt=False,
    ),
    ShiftTestCase(
        one_zhongwen="亚辉同学！　　到！",
        one_yuewen="阿辉同学",
        two_zhongwen="得巴同学！　　到！",
        two_yuewen="到德巴同学到",
        one_yuewen_shifted="阿辉同学到",
        two_yuewen_shifted="德巴同学到",
        include_in_prompt=False,
    ),
    ShiftTestCase(
        one_zhongwen="得巴同学！　　到！",
        one_yuewen="德巴同学到",
        two_zhongwen="阿May同学！　　到！",
        two_yuewen="阿May同学",
        one_yuewen_shifted="德巴同学到",
        two_yuewen_shifted="阿May同学",
        include_in_prompt=True,
    ),
    ShiftTestCase(
        one_zhongwen="阿May同学！　　到！",
        one_yuewen="阿May同学",
        two_zhongwen="麦唛同学！　　到！",
        two_yuewen="到麦麦同学到",
        one_yuewen_shifted="阿May同学到",
        two_yuewen_shifted="麦麦同学到",
        include_in_prompt=True,
    ),
    ShiftTestCase(
        one_zhongwen="麦唛同学！　　到！",
        one_yuewen="麦麦同学到",
        two_zhongwen="菇时同学！　　到！",
        two_yuewen="Boosie同学到",
        one_yuewen_shifted="麦麦同学到",
        two_yuewen_shifted="Boosie同学到",
        include_in_prompt=False,
    ),
    ShiftTestCase(
        one_zhongwen="菇时同学！　　到！",
        one_yuewen="Boosie同学到",
        two_zhongwen="菇时同学！　　到！",
        two_yuewen="川明同学",
        one_yuewen_shifted="Boosie同学到",
        two_yuewen_shifted="川明同学",
        include_in_prompt=False,
    ),
    ShiftTestCase(
        one_zhongwen="菇时同学！　　到！",
        one_yuewen="川明同学",
        two_zhongwen="还有谁没点过吗？",
        two_yuewen="到好仲有边个未点",
        one_yuewen_shifted="川明同学到",
        two_yuewen_shifted="好仲有边个未点",
        include_in_prompt=False,
    ),
    ShiftTestCase(
        one_zhongwen="还有谁没点过吗？",
        one_yuewen="好仲有边个未点",
        two_zhongwen="麦兜！",
        two_yuewen="猫",
        one_yuewen_shifted="好仲有边个未点",
        two_yuewen_shifted="猫",
        include_in_prompt=False,
    ),
    ShiftTestCase(
        one_zhongwen="麦兜！",
        one_yuewen="猫",
        two_zhongwen="麦兜同学！",
        two_yuewen="噢麦兜同学",
        one_yuewen_shifted="猫噢",
        two_yuewen_shifted="麦兜同学",
        include_in_prompt=False,
    ),
    ShiftTestCase(
        one_zhongwen="麦兜同学！",
        one_yuewen="麦兜同学",
        two_zhongwen="麦兜同学！",
        two_yuewen="麦兜同学",
        one_yuewen_shifted="麦兜同学",
        two_yuewen_shifted="麦兜同学",
        include_in_prompt=False,
    ),
    ShiftTestCase(
        one_zhongwen="麦兜同学！",
        one_yuewen="麦兜同学",
        two_zhongwen="麦唛呀，即是呢⋯",
        two_yuewen="妈妈啊麦兜同学",
        one_yuewen_shifted="麦兜同学",
        two_yuewen_shifted="妈妈啊麦兜同学",
        include_in_prompt=False,
    ),
    ShiftTestCase(
        one_zhongwen="麦唛呀，即是呢⋯",
        one_yuewen="妈妈啊麦兜同学",
        two_zhongwen="我好像觉得呢⋯",
        two_yuewen="即系呢我个心总系仁住仁住",
        one_yuewen_shifted="妈妈啊麦兜同学即系呢",
        two_yuewen_shifted="我个心总系仁住仁住",
        include_in_prompt=False,
    ),
    ShiftTestCase(
        one_zhongwen="我好像觉得呢⋯",
        one_yuewen="我个心总系仁住仁住",
        two_zhongwen="有什么人在喊我似的",
        two_yuewen="好似有人嗌紧我个名噉嘅",
        one_yuewen_shifted="我个心总系仁住仁住",
        two_yuewen_shifted="好似有人嗌紧我个名噉嘅",
    ),
    ShiftTestCase(
        one_zhongwen="有什么人在喊我似的",
        one_yuewen="好似有人嗌紧我个名噉嘅",
        two_zhongwen="你们不要以为我心散",
        two_yuewen="你哋唔好以为我心散啊",
        one_yuewen_shifted="好似有人嗌紧我个名噉嘅",
        two_yuewen_shifted="你哋唔好以为我心散啊",
    ),
    ShiftTestCase(
        one_zhongwen="你们不要以为我心散",
        one_yuewen="你哋唔好以为我心散啊",
        two_zhongwen="其实我正在思考一个学术问题：",
        two_yuewen="其实我系喺度思考紧一啲学术性嘅问题",
        one_yuewen_shifted="你哋唔好以为我心散啊",
        two_yuewen_shifted="其实我系喺度思考紧一啲学术性嘅问题",
    ),
    ShiftTestCase(
        one_zhongwen="其实我正在思考一个学术问题：",
        one_yuewen="其实我系喺度思考紧一啲学术性嘅问题",
        two_zhongwen="橙，为什么会是「疴﹣烂﹣煮」呢？",
        two_yuewen="点解橙叫Orange呢",
        one_yuewen_shifted="其实我系喺度思考紧一啲学术性嘅问题",
        two_yuewen_shifted="点解橙叫Orange呢",
    ),
    ShiftTestCase(
        one_zhongwen="橙，为什么会是「疴﹣烂﹣煮」呢？",
        one_yuewen="点解橙叫Orange呢",
        two_zhongwen="妈妈说吃橙可通大便",
        two_yuewen="妈妈话食橙会通大变",
        one_yuewen_shifted="点解橙叫Orange呢",
        two_yuewen_shifted="妈妈话食橙会通大变",
    ),
    ShiftTestCase(
        one_zhongwen="妈妈说吃橙可通大便",
        one_yuewen="妈妈话食橙会通大变",
        two_zhongwen="「疴」这个我明白，可是「烂﹣煮」呢？",
        two_yuewen="噢呢个我明白但系橙呢",
        one_yuewen_shifted="妈妈话食橙会通大变",
        two_yuewen_shifted="噢呢个我明白但系橙呢",
    ),
    ShiftTestCase(
        one_zhongwen="「疴」这个我明白，可是「烂﹣煮」呢？",
        one_yuewen="噢呢个我明白但系橙呢",
        two_zhongwen="还有这个「芭﹣娜﹣娜」香蕉",
        two_yuewen="仲有呢个啊芭拉娜啊香蕉啊",
        one_yuewen_shifted="噢呢个我明白但系橙呢",
        two_yuewen_shifted="仲有呢个啊芭拉娜啊香蕉啊",
    ),
    ShiftTestCase(
        one_zhongwen="还有这个「芭﹣娜﹣娜」香蕉",
        one_yuewen="仲有呢个啊芭拉娜啊香蕉啊",
        two_zhongwen="为什么雨伞又会是「暗﹣芭﹣娜﹣娜」呢？",
        two_yuewen="点解雨姐会叫做暗芭拉娜呢",
        one_yuewen_shifted="仲有呢个啊芭拉娜啊香蕉啊",
        two_yuewen_shifted="点解雨姐会叫做暗芭拉娜呢",
    ),
    ShiftTestCase(
        one_zhongwen="为什么雨伞又会是「暗﹣芭﹣娜﹣娜」呢？",
        one_yuewen="点解雨姐会叫做暗芭拉娜呢",
        two_zhongwen="我「暗」的「暗」掉一条蕉",
        two_yuewen="嗱我暗啦噉我暗𠮶条香蕉",
        one_yuewen_shifted="点解雨姐会叫做暗芭拉娜呢",
        two_yuewen_shifted="嗱我暗啦噉我暗𠮶条香蕉",
    ),
    ShiftTestCase(
        one_zhongwen="我「暗」的「暗」掉一条蕉",
        one_yuewen="嗱我暗啦噉我暗𠮶条香蕉",
        two_zhongwen="至多是疴烂煮，怎么会下起雨来呢？",
        two_yuewen="至多会Orange啫点解会搞到落雨呢",
        one_yuewen_shifted="嗱我暗啦噉我暗𠮶条香蕉",
        two_yuewen_shifted="至多会Orange啫点解会搞到落雨呢",
    ),
    ShiftTestCase(
        one_zhongwen="至多是疴烂煮，怎么会下起雨来呢？",
        one_yuewen="至多会Orange啫点解会搞到落雨呢",
        two_zhongwen="这世界还有很多事情我弄不明白",
        two_yuewen="呢个世界仲有好多嘢我谂唔明",
        one_yuewen_shifted="至多会Orange啫点解会搞到落雨呢",
        two_yuewen_shifted="呢个世界仲有好多嘢我谂唔明",
    ),
    ShiftTestCase(
        one_zhongwen="这世界还有很多事情我弄不明白",
        one_yuewen="呢个世界仲有好多嘢我谂唔明",
        two_zhongwen="但我不害怕",
        two_yuewen="不过我唔怕",
        one_yuewen_shifted="呢个世界仲有好多嘢我谂唔明",
        two_yuewen_shifted="不过我唔怕",
    ),
    ShiftTestCase(
        one_zhongwen="但我不害怕",
        one_yuewen="不过我唔怕",
        two_zhongwen="我想，有天我念完幼稚园",
        two_yuewen="我谂到我读完幼稚园",
        one_yuewen_shifted="不过我唔怕",
        two_yuewen_shifted="我谂到我读完幼稚园",
    ),
    ShiftTestCase(
        one_zhongwen="我想，有天我念完幼稚园",
        one_yuewen="我谂到我读完幼稚园",
        two_zhongwen="升小学，上中学",
        two_yuewen="识埋小学上到中学",
        one_yuewen_shifted="我谂到我读完幼稚园",
        two_yuewen_shifted="识埋小学上到中学",
    ),
    ShiftTestCase(
        one_zhongwen="升小学，上中学",
        one_yuewen="识埋小学上到中学",
        two_zhongwen="再念大学⋯",
        two_yuewen="再入埋大学",
        one_yuewen_shifted="识埋小学上到中学",
        two_yuewen_shifted="再入埋大学",
    ),
    ShiftTestCase(
        one_zhongwen="再念大学⋯",
        one_yuewen="再入埋大学",
        two_zhongwen="当我大学毕业的时候",
        two_yuewen="等我大学毕业𠮶阵",
        one_yuewen_shifted="再入埋大学",
        two_yuewen_shifted="等我大学毕业𠮶阵",
    ),
    ShiftTestCase(
        one_zhongwen="当我大学毕业的时候",
        one_yuewen="等我大学毕业𠮶阵",
        two_zhongwen="我知道我会明白一切！",
        two_yuewen="我谂我乜都会明白晒",
        one_yuewen_shifted="等我大学毕业𠮶阵",
        two_yuewen_shifted="我谂我乜都会明白晒",
    ),
    ShiftTestCase(
        one_zhongwen="我知道我会明白一切！",
        one_yuewen="我谂我乜都会明白晒",
        two_zhongwen="那时候⋯",
        two_yuewen="到𠮶阵",
        one_yuewen_shifted="我谂我乜都会明白晒",
        two_yuewen_shifted="到𠮶阵",
    ),
    ShiftTestCase(
        one_zhongwen="那时候⋯",
        one_yuewen="到𠮶阵",
        two_zhongwen="我买所房子给妈妈！",
        two_yuewen="我买层楼畀我妈妈",
        one_yuewen_shifted="到𠮶阵",
        two_yuewen_shifted="我买层楼畀我妈妈",
    ),
]
shift_test_cases_block_5 = []
shift_test_cases_block_6 = []
shift_test_cases_block_7 = []
shift_test_cases_block_8 = []
shift_test_cases_block_9 = []
shift_test_cases_block_10 = []
shift_test_cases_block_11 = []
shift_test_cases_block_12 = []
shift_test_cases_block_13 = []
shift_test_cases_block_14 = []
shift_test_cases_block_15 = []
shift_test_cases_block_16 = []
shift_test_cases_block_17 = []
shift_test_cases_block_18 = []
shift_test_cases_block_19 = []
shift_test_cases_block_20 = []
shift_test_cases_block_21 = []
shift_test_cases_block_22 = []
shift_test_cases_block_23 = []
shift_test_cases_block_24 = []
shift_test_cases_block_25 = []
shift_test_cases_block_26 = []
shift_test_cases_block_27 = []
shift_test_cases_block_28 = []
shift_test_cases_block_29 = []
shift_test_cases_block_30 = []
shift_test_cases_block_31 = []
shift_test_cases_block_32 = []
shift_test_cases_block_33 = []
shift_test_cases_block_34 = []
shift_test_cases_block_35 = []
shift_test_cases_block_36 = []
shift_test_cases_block_37 = []
shift_test_cases_block_38 = []
shift_test_cases_block_39 = []
shift_test_cases_block_40 = []
shift_test_cases_block_41 = []
shift_test_cases_block_42 = []
shift_test_cases_block_43 = []
shift_test_cases_block_44 = []
shift_test_cases_block_45 = []
shift_test_cases_block_46 = []
shift_test_cases_block_47 = []
shift_test_cases_block_48 = []
shift_test_cases_block_49 = []
shift_test_cases_block_50 = []
shift_test_cases_block_51 = []
shift_test_cases_block_52 = []
shift_test_cases_block_53 = []
shift_test_cases_block_54 = []
shift_test_cases_block_55 = []
shift_test_cases_block_56 = []
shift_test_cases_block_57 = []
shift_test_cases_block_58 = []
shift_test_cases_block_59 = []
shift_test_cases_block_60 = []
shift_test_cases_block_61 = []
shift_test_cases_block_62 = []
shift_test_cases_block_63 = []
shift_test_cases_block_64 = []
shift_test_cases_block_65 = []
shift_test_cases_block_66 = []
shift_test_cases_block_67 = []
shift_test_cases_block_68 = []
shift_test_cases_block_69 = []
shift_test_cases_block_70 = [
    ShiftTestCase(
        one_zhongwen="对不起，常餐卖光了",
        one_yuewen="唔好意思上餐卖晒",
        two_zhongwen="那改要特餐吧",
        two_yuewen="咁改要特餐啦",
        one_yuewen_shifted="唔好意思上餐卖晒",
        two_yuewen_shifted="咁改要特餐啦",
    ),
    ShiftTestCase(
        one_zhongwen="那改要特餐吧",
        one_yuewen="咁改要特餐啦",
        two_zhongwen="特餐？特餐有什么吃？",
        two_yuewen="特餐特餐有咩食㗎",
        one_yuewen_shifted="咁改要特餐啦",
        two_yuewen_shifted="特餐特餐有咩食㗎",
    ),
    ShiftTestCase(
        one_zhongwen="特餐？特餐有什么吃？",
        one_yuewen="特餐特餐有咩食㗎",
        two_zhongwen="特餐即是午餐呀",
        two_yuewen="特餐就即系午餐啰",
        one_yuewen_shifted="特餐特餐有咩食㗎",
        two_yuewen_shifted="特餐就即系午餐啰",
    ),
    ShiftTestCase(
        one_zhongwen="特餐即是午餐呀",
        one_yuewen="特餐就即系午餐啰",
        two_zhongwen="午餐又吃什么呢？",
        two_yuewen="午餐食乜嘢㗎",
        one_yuewen_shifted="特餐就即系午餐啰",
        two_yuewen_shifted="午餐食乜嘢㗎",
    ),
    ShiftTestCase(
        one_zhongwen="午餐又吃什么呢？",
        one_yuewen="午餐食乜嘢㗎",
        two_zhongwen="都是晚餐那些吧",
        two_yuewen="都系晚餐𠮶啲嘢啰",
        one_yuewen_shifted="午餐食乜嘢㗎",
        two_yuewen_shifted="都系晚餐𠮶啲嘢啰",
    ),
    ShiftTestCase(
        one_zhongwen="都是晚餐那些吧",
        one_yuewen="都系晚餐𠮶啲嘢啰",
        two_zhongwen="什么是晚餐？",
        two_yuewen="咁乜嘢系晚餐呀",
        one_yuewen_shifted="都系晚餐𠮶啲嘢啰",
        two_yuewen_shifted="咁乜嘢系晚餐呀",
    ),
    ShiftTestCase(
        one_zhongwen="什么是晚餐？",
        one_yuewen="咁乜嘢系晚餐呀",
        two_zhongwen="跟快餐一样",
        two_yuewen="同快餐一样啰",
        one_yuewen_shifted="咁乜嘢系晚餐呀",
        two_yuewen_shifted="同快餐一样啰",
    ),
    ShiftTestCase(
        one_zhongwen="跟快餐一样",
        one_yuewen="同快餐一样啰",
        two_zhongwen="快餐吃什么？",
        two_yuewen="咁快餐食咩㗎",
        one_yuewen_shifted="同快餐一样啰",
        two_yuewen_shifted="咁快餐食咩㗎",
    ),
    ShiftTestCase(
        one_zhongwen="快餐吃什么？",
        one_yuewen="咁快餐食咩㗎",
        two_zhongwen="唉，快餐不就是常餐",
        two_yuewen="系快餐就即系上餐啰",
        one_yuewen_shifted="咁快餐食咩㗎",
        two_yuewen_shifted="系快餐就即系上餐啰",
    ),
    ShiftTestCase(
        one_zhongwen="唉，快餐不就是常餐",
        one_yuewen="系快餐就即系上餐啰",
        two_zhongwen="常餐不是卖光了吗？",
        two_yuewen="咁你头先又话冇上餐",
        one_yuewen_shifted="系快餐就即系上餐啰",
        two_yuewen_shifted="咁你头先又话冇上餐",
    ),
    ShiftTestCase(
        one_zhongwen="常餐不是卖光了吗？",
        one_yuewen="咁你头先又话冇上餐",
        two_zhongwen="对，常餐卖光了，要吃特餐吗？",
        two_yuewen="系呀上餐就系卖晒呀咁你试唔试下特餐啦",
        one_yuewen_shifted="咁你头先又话冇上餐系呀上餐就系卖晒呀",
        two_yuewen_shifted="咁你试唔试下特餐啦",
    ),
    ShiftTestCase(
        one_zhongwen="对，常餐卖光了，要吃特餐吗？",
        one_yuewen="咁你试唔试下特餐啦",
        two_zhongwen="来两份特餐吧",
        two_yuewen="两份特餐啦",
        one_yuewen_shifted="咁你试唔试下特餐啦",
        two_yuewen_shifted="两份特餐啦",
    ),
    ShiftTestCase(
        one_zhongwen="来两份特餐吧",
        one_yuewen="两份特餐啦",
        two_zhongwen="对不起，特餐卖光了",
        two_yuewen="唔好意思特餐卖晒嘅",
        one_yuewen_shifted="两份特餐啦",
        two_yuewen_shifted="唔好意思特餐卖晒嘅",
    ),
    ShiftTestCase(
        one_zhongwen="对不起，特餐卖光了",
        one_yuewen="唔好意思特餐卖晒嘅",
        two_zhongwen="妈妈，改快餐吧",
        two_yuewen="妈妈不如改快餐啦",
        one_yuewen_shifted="唔好意思特餐卖晒嘅",
        two_yuewen_shifted="妈妈不如改快餐啦",
    ),
    ShiftTestCase(
        one_zhongwen="妈妈，改快餐吧",
        one_yuewen="妈妈不如改快餐啦",
        two_zhongwen="快餐有什么？",
        two_yuewen="快餐有咩㗎",
        one_yuewen_shifted="妈妈不如改快餐啦",
        two_yuewen_shifted="快餐有咩㗎",
    ),
    ShiftTestCase(
        one_zhongwen="快餐有什么？",
        one_yuewen="快餐有咩㗎",
        two_zhongwen="快餐即是常餐",
        two_yuewen="快餐即系上餐",
        one_yuewen_shifted="快餐有咩㗎",
        two_yuewen_shifted="快餐即系上餐",
    ),
    ShiftTestCase(
        one_zhongwen="快餐即是常餐",
        one_yuewen="快餐即系上餐",
        two_zhongwen="常餐又有什么呢？",
        two_yuewen="咁上餐有咩㗎",
        one_yuewen_shifted="快餐即系上餐",
        two_yuewen_shifted="咁上餐有咩㗎",
    ),
    ShiftTestCase(
        one_zhongwen="常餐又有什么呢？",
        one_yuewen="咁上餐有咩㗎",
        two_zhongwen="常餐即是午餐",
        two_yuewen="上餐就即系午餐啰",
        one_yuewen_shifted="咁上餐有咩㗎",
        two_yuewen_shifted="上餐就即系午餐啰",
    ),
    ShiftTestCase(
        one_zhongwen="常餐即是午餐",
        one_yuewen="上餐就即系午餐啰",
        two_zhongwen="那么午餐又有什么吃？",
        two_yuewen="哎呀咁午餐有咩食呀",
        one_yuewen_shifted="上餐就即系午餐啰",
        two_yuewen_shifted="哎呀咁午餐有咩食呀",
    ),
    ShiftTestCase(
        one_zhongwen="那么午餐又有什么吃？",
        one_yuewen="哎呀咁午餐有咩食呀",
        two_zhongwen="午餐跟晚餐一样",
        two_yuewen="午餐同晚餐一样㗎",
        one_yuewen_shifted="哎呀咁午餐有咩食呀",
        two_yuewen_shifted="午餐同晚餐一样㗎",
    ),
    ShiftTestCase(
        one_zhongwen="午餐跟晚餐一样",
        one_yuewen="午餐同晚餐一样㗎",
        two_zhongwen="晚餐呢？",
        two_yuewen="咁晚餐呢",
        one_yuewen_shifted="午餐同晚餐一样㗎",
        two_yuewen_shifted="咁晚餐呢",
    ),
    ShiftTestCase(
        one_zhongwen="晚餐呢？",
        one_yuewen="咁晚餐呢",
        two_zhongwen="晚餐不就是特餐",
        two_yuewen="晚餐就即系特餐啰",
        one_yuewen_shifted="咁晚餐呢",
        two_yuewen_shifted="晚餐就即系特餐啰",
    ),
    ShiftTestCase(
        one_zhongwen="晚餐不就是特餐",
        one_yuewen="晚餐就即系特餐啰",
        two_zhongwen="不是说特餐卖光了吗？",
        two_yuewen="咁你头先又话冇特餐",
        one_yuewen_shifted="晚餐就即系特餐啰",
        two_yuewen_shifted="咁你头先又话冇特餐",
    ),
    ShiftTestCase(
        one_zhongwen="不是说特餐卖光了吗？",
        one_yuewen="咁你头先又话冇特餐",
        two_zhongwen="特餐卖光了，要试试快餐吗？都一样的",
        two_yuewen="系呀特餐系卖晒呀咁你试唔试下个快餐啦一样嘅啫",
        one_yuewen_shifted="咁你头先又话冇特餐",
        two_yuewen_shifted="系呀特餐系卖晒呀咁你试唔试下个快餐啦一样嘅啫",
    ),
    ShiftTestCase(
        one_zhongwen="特餐卖光了，要试试快餐吗？都一样的",
        one_yuewen="系呀特餐系卖晒呀咁你试唔试下个快餐啦一样嘅啫",
        two_zhongwen="来两份快餐吧",
        two_yuewen="咁两份快餐啦",
        one_yuewen_shifted="系呀特餐系卖晒呀咁你试唔试下个快餐啦一样嘅啫",
        two_yuewen_shifted="咁两份快餐啦",
    ),
]
shift_test_cases_block_71 = [
    ShiftTestCase(
        one_zhongwen="对不起，没快餐了",
        one_yuewen="唔好意思冇快餐呀",
        two_zhongwen="太过分了吧？你们究竟有吃的没？",
        two_yuewen="嚟唔嚟普啲呀噉你哋究竟有啲咩餐呀",
        one_yuewen_shifted="唔好意思冇快餐呀",
        two_yuewen_shifted="嚟唔嚟普啲呀噉你哋究竟有啲咩餐呀",
    ),
    ShiftTestCase(
        one_zhongwen="太过分了吧？你们究竟有吃的没？",
        one_yuewen="嚟唔嚟普啲呀噉你哋究竟有啲咩餐呀",
        two_zhongwen="午餐吧，午餐精采呀",
        two_yuewen="午餐啦",
        one_yuewen_shifted="嚟唔嚟普啲呀噉你哋究竟有啲咩餐呀",
        two_yuewen_shifted="午餐啦",
    ),
    ShiftTestCase(
        one_zhongwen="午餐吧，午餐精采呀",
        one_yuewen="午餐啦",
        two_zhongwen="怎么个精采法？",
        two_yuewen="午餐好嘢呀",
        one_yuewen_shifted="午餐啦",
        two_yuewen_shifted="午餐好嘢呀",
    ),
    ShiftTestCase(
        one_zhongwen="怎么个精采法？",
        one_yuewen="午餐好嘢呀",
        two_zhongwen="跟晚餐一样精采",
        two_yuewen="点好嘢法呀同晚餐一样咁好嘢",
        one_yuewen_shifted="午餐好嘢呀点好嘢法呀",
        two_yuewen_shifted="同晚餐一样咁好嘢",
    ),
    ShiftTestCase(
        one_zhongwen="跟晚餐一样精采",
        one_yuewen="同晚餐一样咁好嘢",
        two_zhongwen="晚餐又怎样呢？",
        two_yuewen="噉晚餐又点好嘢法呀",
        one_yuewen_shifted="同晚餐一样咁好嘢",
        two_yuewen_shifted="噉晚餐又点好嘢法呀",
    ),
    ShiftTestCase(
        one_zhongwen="晚餐又怎样呢？",
        one_yuewen="噉晚餐又点好嘢法呀",
        two_zhongwen="跟常餐一样精采",
        two_yuewen="同上餐一样咁好嘢啰",
        one_yuewen_shifted="噉晚餐又点好嘢法呀",
        two_yuewen_shifted="同上餐一样咁好嘢啰",
    ),
    ShiftTestCase(
        one_zhongwen="跟常餐一样精采",
        one_yuewen="同上餐一样咁好嘢啰",
        two_zhongwen="常餐又怎样呢？",
        two_yuewen="噉上餐又点好嘢法呀",
        one_yuewen_shifted="同上餐一样咁好嘢啰",
        two_yuewen_shifted="噉上餐又点好嘢法呀",
    ),
    ShiftTestCase(
        one_zhongwen="常餐又怎样呢？",
        one_yuewen="噉上餐又点好嘢法呀",
        two_zhongwen="常餐早卖光了，你说精采不？",
        two_yuewen="上餐上餐一早卖晒啦你话好唔好嘢",
        one_yuewen_shifted="噉上餐又点好嘢法呀",
        two_yuewen_shifted="上餐上餐一早卖晒啦你话好唔好嘢",
    ),
    ShiftTestCase(
        one_zhongwen="常餐早卖光了，你说精采不？",
        one_yuewen="上餐上餐一早卖晒啦你话好唔好嘢",
        two_zhongwen="好吧好吧！两份午餐好了",
        two_yuewen="好啦好啦要两份午餐啦",
        one_yuewen_shifted="上餐上餐一早卖晒啦你话好唔好嘢",
        two_yuewen_shifted="好啦好啦要两份午餐啦",
    ),
]
shift_test_cases_block_72 = [
    ShiftTestCase(
        one_zhongwen="对不起，午餐卖光了",
        one_yuewen="唔好意思午餐卖晒",
        two_zhongwen="要试试我们的晚餐吗？都一样的",
        two_yuewen="试唔试下我哋嘅晚餐啦",
        one_yuewen_shifted="唔好意思午餐卖晒",
        two_yuewen_shifted="试唔试下我哋嘅晚餐啦",
    ),
    ShiftTestCase(
        one_zhongwen="要试试我们的晚餐吗？都一样的",
        one_yuewen="试唔试下我哋嘅晚餐啦",
        two_zhongwen="光天白日，吃什么鬼晚餐？",
        two_yuewen="一样嘅啫日光日白食乜鬼嘢晚餐啊",
        one_yuewen_shifted="试唔试下我哋嘅晚餐啦一样嘅啫",
        two_yuewen_shifted="日光日白食乜鬼嘢晚餐啊",
    ),
    ShiftTestCase(
        one_zhongwen="光天白日，吃什么鬼晚餐？",
        one_yuewen="日光日白食乜鬼嘢晚餐啊",
        two_zhongwen="唉，说是说晚餐，还不就是午餐？",
        two_yuewen="系个名叫晚餐啫其实唔系真系午餐",
        one_yuewen_shifted="日光日白食乜鬼嘢晚餐啊",
        two_yuewen_shifted="系个名叫晚餐啫其实唔系真系午餐",
    ),
    ShiftTestCase(
        one_zhongwen="唉，说是说晚餐，还不就是午餐？",
        one_yuewen="系个名叫晚餐啫其实唔系真系午餐",
        two_zhongwen="好吧好吧，拜托！两份晚餐！快！",
        two_yuewen="好啦好啦怕咗你啦要两份晚餐啦快啲手啊",
        one_yuewen_shifted="系个名叫晚餐啫其实唔系真系午餐",
        two_yuewen_shifted="好啦好啦怕咗你啦要两份晚餐啦快啲手啊",
    ),
    ShiftTestCase(
        one_zhongwen="好吧好吧，拜托！两份晚餐！快！",
        one_yuewen="好啦好啦怕咗你啦要两份晚餐啦快啲手啊",
        two_zhongwen="要快吗？那得吃快餐了！",
        two_yuewen="想快想快就要快餐啊",
        one_yuewen_shifted="好啦好啦怕咗你啦要两份晚餐啦快啲手啊",
        two_yuewen_shifted="想快想快就要快餐啊",
    ),
]
mlamd_shift_test_cases: list[ShiftTestCase] = sum(
    (globals()[f"shift_test_cases_block_{i}"] for i in range(73)), []
)
"""MLAMD 粤文 shiting test cases."""
# endregion


# region 粤文 Merge Test Cases
merge_test_cases_block_0 = [
    MergeTestCase(
        zhongwen="在麦太即将临盆的时候",
        yuewen_to_merge=["就喺麦太快要临盘嘅时候"],
        yuewen_merged="就喺麦太快要临盘嘅时候",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="一只胶兜在九龙上空飞过",
        yuewen_to_merge=["有一个胶兜喺九龙上空飞过"],
        yuewen_merged="有一个胶兜喺九龙上空飞过",
    ),
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
        zhongwen="更正一下：",
        yuewen_to_merge=["都系唔好"],
        yuewen_merged="都系唔好：",
    ),
    MergeTestCase(
        zhongwen="先到街市大楼妹记鱼腩粥外边",
        yuewen_to_merge=["先去街市大楼𠮶间妹记鱼腩粥𠮶度"],
        yuewen_merged="先去街市大楼𠮶间妹记鱼腩粥𠮶度",
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
        yuewen_to_merge=["都系出返去阿街路街飞过火车桥", "右转入太平道"],
        yuewen_merged="都系出返去阿街路街飞过火车桥右转入太平道",
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
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="胶兜最后飞进广华医院候产房",
        yuewen_to_merge=["最后胶兜飞咗入广华医院嘅后产房"],
        yuewen_merged="最后胶兜飞咗入广华医院嘅后产房",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="也就是在麦太右边额角上⋯",
        yuewen_to_merge=["亦即系麦太右边云晶对上"],
        yuewen_merged="亦即系麦太右边云晶对上⋯",
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
        zhongwen="麦太认定这是异像",
        yuewen_to_merge=["麦太认定呢个系异象"],
        yuewen_merged="麦太认定呢个系异象",
    ),
    MergeTestCase(
        zhongwen="于是向额角上的胶兜许愿",
        yuewen_to_merge=["于是向云晶对上嘅胶兜许愿"],
        yuewen_merged="于是向云晶对上嘅胶兜许愿",
    ),
    MergeTestCase(
        zhongwen="脑海中同时出现即将诞生的儿子容貌⋯",
        yuewen_to_merge=["而脑入面亦即时出现咗快要出世个仔嘅样"],
        yuewen_merged="而脑入面亦即时出现咗快要出世个仔嘅样⋯",
    ),
    MergeTestCase(
        zhongwen="希望他好聪明，读书好叻！",
        yuewen_to_merge=["希望佢好聪明", "读书好叻"],
        yuewen_merged="希望佢好聪明，读书好叻！",
    ),
    MergeTestCase(
        zhongwen="胶兜对麦太的愿望似乎没有反应",
        yuewen_to_merge=["胶兜对麦太嘅愿望似乎冇咩表示"],
        yuewen_merged="胶兜对麦太嘅愿望似乎冇咩表示",
    ),
    MergeTestCase(
        zhongwen="于是她向胶兜补充说：",
        yuewen_to_merge=["于是佢对住胶兜补充噉话"],
        yuewen_merged="于是佢对住胶兜补充噉话：",
    ),
    MergeTestCase(
        zhongwen="或者读书唔叻，工作叻呢？",
        yuewen_to_merge=["或者读书唔叻", "出嚟做嘢叻啦"],
        yuewen_merged="或者读书唔叻，出嚟做嘢叻啦？",
    ),
    MergeTestCase(
        zhongwen="又或者⋯",
        yuewen_to_merge=["又或者呢"],
        yuewen_merged="又或者呢⋯",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="又或者好靓仔，好靓仔",
        yuewen_to_merge=["又或者系好靓仔好靓仔"],
        yuewen_merged="又或者系好靓仔，好靓仔",
    ),
    MergeTestCase(
        zhongwen="跟周润发，梁朝伟那么靓仔！",
        yuewen_to_merge=["好似周润发同埋梁朝伟咁靓仔"],
        yuewen_merged="好似周润发，同埋梁朝伟咁靓仔！",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="胶兜仍然在转，毫无点头迹象",
        yuewen_to_merge=["胶兜依然系噉喺度转", "好似一啲应承嘅迹象都冇"],
        yuewen_merged="胶兜依然系噉喺度转，好似一啲应承嘅迹象都冇",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="麦太一时心虚",
        yuewen_to_merge=["麦太一时心虚"],
        yuewen_merged="麦太一时心虚",
    ),
    MergeTestCase(
        zhongwen="赶忙趁胶兜落地前另许一个愿望：",
        yuewen_to_merge=["嗱嗱嗱喺胶兜未落地之前起过另外一个愿望"],
        yuewen_merged="嗱嗱嗱喺胶兜未落地之前起过另外一个愿望：",
    ),
    MergeTestCase(
        zhongwen="唔聪明唔靓仔也算了，只要福星高照",
        yuewen_to_merge=["就算唔系咁聪明同咁靓仔", "只要复星高照"],
        yuewen_merged="就算唔系咁聪明同咁靓仔，只要复星高照",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="一世够运，逢凶化吉！",
        yuewen_to_merge=["一世救运", "乜嘢事都逢凶化㗎喇"],
        yuewen_merged="一世救运，乜嘢事都逢凶化㗎喇！",
    ),
    MergeTestCase(
        zhongwen="靠自己能力解决事情当然最好",
        yuewen_to_merge=["佢靠自己有料解决啲嘢就梗系好啦"],
        yuewen_merged="佢靠自己有料解决啲嘢就梗系好啦",
    ),
    MergeTestCase(
        zhongwen="不过运气还是很重要的",
        yuewen_to_merge=["不过运气都好紧要㖞"],
        yuewen_merged="不过运气都好紧要㖞",
    ),
    MergeTestCase(
        zhongwen="虽是说像梁朝伟周润发也行运定了",
        yuewen_to_merge=["虽然似梁朝伟周润发都唔返去冒运行"],
        yuewen_merged="虽然似梁朝伟周润发都唔返去冒运行",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="但总得要叻仔呀！",
        yuewen_to_merge=["但系都要叻仔先得㗎"],
        yuewen_merged="但系都要叻仔先得㗎！",
    ),
]
merge_test_cases_block_1 = [
    MergeTestCase(
        zhongwen="最后，胶兜「嘀督」一声落地",
        yuewen_to_merge=["最后胶兜滴嘟一声咁落地"],
        yuewen_merged="最后，胶兜「滴嘟」一声咁落地",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="嘀督？嘀督，就是答应了",
        yuewen_to_merge=["滴嘟", "滴嘟㖞", "即系应承啦"],
        yuewen_merged="滴嘟？滴嘟㖞，即系应承啦",
    ),
    MergeTestCase(  # DIFFICULT; FAILS EVEN THOUGH INCLUDED IN PROMPT
        zhongwen="麦太想，这次走运了！",
        yuewen_to_merge=["麦太心谂", "今次冇死喇"],
        yuewen_merged="麦太心谂，今次冇死喇！",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="可是答应了些什么呢？",
        yuewen_to_merge=["但你应承咗啲咩呢"],
        yuewen_merged="但你应承咗啲咩呢？",
    ),
    MergeTestCase(
        zhongwen="叻仔？好运？",
        yuewen_to_merge=["叻仔", "好运"],
        yuewen_merged="叻仔？好运？",
    ),
    MergeTestCase(
        zhongwen="还是似周润发？",
        yuewen_to_merge=["定系话自周人烦啊"],
        yuewen_merged="定系话自周人烦啊？",
    ),
    MergeTestCase(
        zhongwen="为了纪念这赐福的胶兜",
        yuewen_to_merge=["为咗纪念呢个赤幅嘅胶兜"],
        yuewen_merged="为咗纪念呢个赤幅嘅胶兜",
    ),
    MergeTestCase(
        zhongwen="麦太决定把儿子命名麦胶",
        yuewen_to_merge=["麦太决定将个仔嘅名叫做麦胶"],
        yuewen_merged="麦太决定将个仔嘅名叫做麦胶",
    ),
    MergeTestCase(
        zhongwen="不行，胶胶声，多难听！",
        yuewen_to_merge=["都系唔好", "胶胶声咁难听"],
        yuewen_merged="都系唔好，胶胶声，咁难听！",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="还是唤他麦兜！",
        yuewen_to_merge=["不如叫麦兜啦"],
        yuewen_merged="不如叫麦兜啦！",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="各位⋯",
        yuewen_to_merge=["各位"],
        yuewen_merged="各位⋯",
    ),
    MergeTestCase(
        zhongwen="我就是险些给定名麦胶的小朋友⋯",
        yuewen_to_merge=["我就系呢个差少少就叫做麦胶嘅小朋友"],
        yuewen_merged="我就系呢个差少少就叫做麦胶嘅小朋友⋯",
    ),
    MergeTestCase(
        zhongwen="麦兜！",
        yuewen_to_merge=["麦兜"],
        yuewen_merged="麦兜！",
    ),
]
merge_test_cases_block_2 = [
    MergeTestCase(
        zhongwen="麦太，没见面一阵",
        yuewen_to_merge=["咦", "麦太", "咩唔见你一排"],
        yuewen_merged="咦，麦太，咩唔见你一排",
    ),
    MergeTestCase(
        zhongwen="怎么小腿粗起来了？",
        yuewen_to_merge=["个脚刮囊粗咗咁多呀"],
        yuewen_merged="个脚刮囊粗咗咁多呀？",
    ),
    MergeTestCase(
        zhongwen="可怜呀，每天扑来扑去⋯",
        yuewen_to_merge=["鬼咩", "日日扑嚟扑去"],
        yuewen_merged="鬼咩，日日扑嚟扑去⋯",
    ),
    MergeTestCase(
        zhongwen="替儿子找幼稚园！",
        yuewen_to_merge=["同我仔揾幼稚园吖嘛"],
        yuewen_merged="同我仔揾幼稚园吖嘛！",
    ),
    MergeTestCase(
        zhongwen="怎么不试一试好彩酒楼对面",
        yuewen_to_merge=["点解唔试下好彩走楼斜对面"],
        yuewen_merged="点解唔试下好彩走楼斜对面",
    ),
    MergeTestCase(
        zhongwen="旧中侨国货楼上的⋯",
        yuewen_to_merge=["旧中桥百货公司楼上𠮶间"],
        yuewen_merged="旧中桥百货公司楼上𠮶间⋯",
    ),
    MergeTestCase(
        zhongwen="春田花花幼稚园？",
        yuewen_to_merge=["春田花花幼稚园呢"],
        yuewen_merged="春田花花幼稚园呢？",
    ),
    MergeTestCase(
        zhongwen="就是座落界限街南昌街交界⋯",
        yuewen_to_merge=["就系坐落喺界限街同南昌街交界"],
        yuewen_merged="就系坐落喺界限街同南昌街交界⋯",
    ),
    MergeTestCase(
        zhongwen="银城美食广场附近的⋯",
        yuewen_to_merge=["银城美食广场附近𠮶间"],
        yuewen_merged="银城美食广场附近𠮶间⋯",
    ),
    MergeTestCase(
        zhongwen="春田花花幼稚园？",
        yuewen_to_merge=["春田花花幼稚园呀"],
        yuewen_merged="春田花花幼稚园呀？",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="对！深水埗地铁站步行不用10分钟！",
        yuewen_to_merge=["系呀", "深水埗地铁站口行过去唔使十分钟呀"],
        yuewen_merged="系呀！深水埗地铁站口行过去唔使十分钟呀！",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="春田花花幼稚园，师资优良⋯",
        yuewen_to_merge=["春田花花幼稚园", "诗诗优良"],
        yuewen_merged="春田花花幼稚园，诗诗优良⋯",
    ),
    MergeTestCase(
        zhongwen="而且还有西人教英文！",
        yuewen_to_merge=["仲系西人教英文添㗎"],
        yuewen_merged="仲系西人教英文添㗎！",
    ),
    MergeTestCase(
        zhongwen="西人教英文？",
        yuewen_to_merge=["咦", "西人教英文"],
        yuewen_merged="咦，西人教英文？",
    ),
    MergeTestCase(
        zhongwen="是呀！",
        yuewen_to_merge=["系呀"],
        yuewen_merged="系呀！",
    ),
    MergeTestCase(
        zhongwen="春田花花，确有好多西人呀！",
        yuewen_to_merge=["春田花花", "真系好多西人㗎"],
        yuewen_merged="春田花花，真系好多西人㗎！",
    ),
]
merge_test_cases_block_3 = [
    MergeTestCase(
        zhongwen="这个猪样白兔小朋友⋯",
        yuewen_to_merge=["呢个扮紧白兔猪样嘅小朋友"],
        yuewen_merged="呢个扮紧白兔猪样嘅小朋友⋯",
    ),
    MergeTestCase(
        zhongwen="横看竖看也不像发哥伟仔的一个⋯",
        yuewen_to_merge=["即系横睇掂睇都唔似发哥或者", "位仔𠮶个呢"],
        yuewen_merged="即系横睇掂睇都唔似发哥或者位仔𠮶个呢⋯",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="就是我，麦兜",
        yuewen_to_merge=["就系我", "麦兜"],
        yuewen_merged="就系我，麦兜",
    ),
    MergeTestCase(
        zhongwen="这是我就读的幼稚园",
        yuewen_to_merge=["呢间就系我读嘅幼稚园"],
        yuewen_merged="呢间就系我读嘅幼稚园",
    ),
    MergeTestCase(
        zhongwen="校长是潮州人",
        yuewen_to_merge=["校长系潮州人"],
        yuewen_merged="校长系潮州人",
    ),
    MergeTestCase(
        zhongwen="可能是潮州口音的关系",
        yuewen_to_merge=["可能仲系讲紧潮州话嘅"],
        yuewen_merged="可能仲系讲紧潮州话嘅",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="这么多年来⋯",
        yuewen_to_merge=["所以咁多年嚟"],
        yuewen_merged="所以咁多年嚟⋯",
    ),
    MergeTestCase(
        zhongwen="我其实不大明白他的说话",
        yuewen_to_merge=["我其实唔系好知佢噏文"],
        yuewen_merged="我其实唔系好知佢噏文",
    ),
    MergeTestCase(
        zhongwen="蛋挞！　　蛋挞！",
        yuewen_to_merge=["大湖荒岩宅"],
        yuewen_merged="大湖荒岩宅",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="荔芋火鸭礼！　　荔芋火鸭礼！",
        yuewen_to_merge=["湾吉校坟交涉设"],
        yuewen_merged="湾吉校坟交涉设",
    ),
    MergeTestCase(
        zhongwen="也不能忘记校训九十八！",
        yuewen_to_merge=["都唔好湾吉校坟交涉白"],
        yuewen_merged="都唔好湾吉校坟交涉白！",
    ),
    MergeTestCase(
        zhongwen="好！各位同学⋯",
        yuewen_to_merge=["𠮶个位同学"],
        yuewen_merged="𠮶个位同学⋯",
    ),
    MergeTestCase(
        zhongwen="今天的早会主要是跟大家分享",
        yuewen_to_merge=["今次座会系要同大家分享"],
        yuewen_merged="今次座会系要同大家分享",
    ),
    MergeTestCase(
        zhongwen="一个重要主题：",
        yuewen_to_merge=["一个可重要嘅主题"],
        yuewen_merged="一个可重要嘅主题：",
    ),
    MergeTestCase(  # DIFFICULT; FAILS EVEN THOUGH INCLUDED IN PROMPT
        zhongwen="小朋友，这个月你们交过学费没有？",
        yuewen_to_merge=["小朋友", "你哋今个月交咗学费咩呀"],
        yuewen_merged="小朋友，你哋今个月交咗学费咩呀",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="交过了！",
        yuewen_to_merge=["交"],
        yuewen_merged="交！",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="太好了！大家去上堂吧",
        yuewen_to_merge=["哎", "好在", "噉大家可以返去上堂喇"],
        yuewen_merged="哎，好在！噉大家可以返去上堂喇",
        include_in_prompt=True,
    ),
]
merge_test_cases_block_4 = []
merge_test_cases_block_5 = []
merge_test_cases_block_6 = []
merge_test_cases_block_7 = []
merge_test_cases_block_8 = []
merge_test_cases_block_9 = []
merge_test_cases_block_10 = []
merge_test_cases_block_11 = []
merge_test_cases_block_12 = []
merge_test_cases_block_13 = []
merge_test_cases_block_14 = []
merge_test_cases_block_15 = []
merge_test_cases_block_16 = []
merge_test_cases_block_17 = []
merge_test_cases_block_18 = []
merge_test_cases_block_19 = []
merge_test_cases_block_20 = []
merge_test_cases_block_21 = []
merge_test_cases_block_22 = []
merge_test_cases_block_23 = []
merge_test_cases_block_24 = []
merge_test_cases_block_25 = []
merge_test_cases_block_26 = []
merge_test_cases_block_27 = []
merge_test_cases_block_28 = []
merge_test_cases_block_29 = []
merge_test_cases_block_30 = []
merge_test_cases_block_31 = []
merge_test_cases_block_32 = []
merge_test_cases_block_33 = []
merge_test_cases_block_34 = []
merge_test_cases_block_35 = []
merge_test_cases_block_36 = []
merge_test_cases_block_37 = []
merge_test_cases_block_38 = []
merge_test_cases_block_39 = []
merge_test_cases_block_40 = []
merge_test_cases_block_41 = []
merge_test_cases_block_42 = []
merge_test_cases_block_43 = []
merge_test_cases_block_44 = []
merge_test_cases_block_45 = []
merge_test_cases_block_46 = []
merge_test_cases_block_47 = []
merge_test_cases_block_48 = []
merge_test_cases_block_49 = []
merge_test_cases_block_50 = []
merge_test_cases_block_51 = []
merge_test_cases_block_52 = []
merge_test_cases_block_53 = []
merge_test_cases_block_54 = []
merge_test_cases_block_55 = []
merge_test_cases_block_56 = []
merge_test_cases_block_57 = []
merge_test_cases_block_58 = []
merge_test_cases_block_59 = []
merge_test_cases_block_60 = []
merge_test_cases_block_61 = []
merge_test_cases_block_62 = []
merge_test_cases_block_63 = []
merge_test_cases_block_64 = []
merge_test_cases_block_65 = []
merge_test_cases_block_66 = []
merge_test_cases_block_67 = []
merge_test_cases_block_68 = []
merge_test_cases_block_69 = []
merge_test_cases_block_70 = [
    MergeTestCase(
        zhongwen="对不起，常餐卖光了",
        yuewen_to_merge=["唔好意思", "上餐卖晒"],
        yuewen_merged="唔好意思，上餐卖晒",
    ),
    MergeTestCase(
        zhongwen="那改要特餐吧",
        yuewen_to_merge=["咁改要特餐啦"],
        yuewen_merged="咁改要特餐啦",
    ),
    MergeTestCase(
        zhongwen="特餐？特餐有什么吃？",
        yuewen_to_merge=["特餐", "特餐有咩食㗎"],
        yuewen_merged="特餐？特餐有咩食㗎？",
    ),
    MergeTestCase(
        zhongwen="特餐即是午餐呀",
        yuewen_to_merge=["特餐就即系午餐啰"],
        yuewen_merged="特餐就即系午餐啰",
    ),
    MergeTestCase(
        zhongwen="午餐又吃什么呢？",
        yuewen_to_merge=["午餐食乜嘢㗎"],
        yuewen_merged="午餐食乜嘢㗎？",
    ),
    MergeTestCase(
        zhongwen="都是晚餐那些吧",
        yuewen_to_merge=["都系晚餐𠮶啲嘢啰"],
        yuewen_merged="都系晚餐𠮶啲嘢啰",
    ),
    MergeTestCase(
        zhongwen="什么是晚餐？",
        yuewen_to_merge=["咁乜嘢系晚餐呀"],
        yuewen_merged="咁乜嘢系晚餐呀？",
    ),
    MergeTestCase(
        zhongwen="跟快餐一样",
        yuewen_to_merge=["同快餐一样啰"],
        yuewen_merged="同快餐一样啰",
    ),
    MergeTestCase(
        zhongwen="快餐吃什么？",
        yuewen_to_merge=["咁快餐食咩㗎"],
        yuewen_merged="咁快餐食咩㗎？",
    ),
    MergeTestCase(
        zhongwen="唉，快餐不就是常餐",
        yuewen_to_merge=["系", "快餐就即系上餐啰"],
        yuewen_merged="系，快餐就即系上餐啰",
    ),
    MergeTestCase(
        zhongwen="常餐不是卖光了吗？",
        yuewen_to_merge=["咁你头先又话冇上餐", "系呀", "上餐就系卖晒呀"],
        yuewen_merged="咁你头先又话冇上餐，系呀，上餐就系卖晒呀？",
    ),
    MergeTestCase(
        zhongwen="对，常餐卖光了，要吃特餐吗？",
        yuewen_to_merge=["咁你试唔试下特餐啦"],
        yuewen_merged="咁你试唔试下特餐啦？",
    ),
    MergeTestCase(
        zhongwen="来两份特餐吧",
        yuewen_to_merge=["两份特餐啦"],
        yuewen_merged="两份特餐啦",
    ),
    MergeTestCase(
        zhongwen="对不起，特餐卖光了",
        yuewen_to_merge=["唔好意思", "特餐卖晒嘅"],
        yuewen_merged="唔好意思，特餐卖晒嘅",
    ),
    MergeTestCase(
        zhongwen="妈妈，改快餐吧",
        yuewen_to_merge=["妈妈", "不如改快餐啦"],
        yuewen_merged="妈妈，不如改快餐啦",
    ),
    MergeTestCase(
        zhongwen="快餐有什么？",
        yuewen_to_merge=["快餐有咩㗎"],
        yuewen_merged="快餐有咩㗎？",
    ),
    MergeTestCase(
        zhongwen="快餐即是常餐",
        yuewen_to_merge=["快餐即系上餐"],
        yuewen_merged="快餐即系上餐",
    ),
    MergeTestCase(
        zhongwen="常餐又有什么呢？",
        yuewen_to_merge=["咁上餐有咩㗎"],
        yuewen_merged="咁上餐有咩㗎？",
    ),
    MergeTestCase(
        zhongwen="常餐即是午餐",
        yuewen_to_merge=["上餐就即系午餐啰"],
        yuewen_merged="上餐就即系午餐啰",
    ),
    MergeTestCase(
        zhongwen="那么午餐又有什么吃？",
        yuewen_to_merge=["哎呀", "咁午餐有咩食呀"],
        yuewen_merged="哎呀，咁午餐有咩食呀？",
    ),
    MergeTestCase(
        zhongwen="午餐跟晚餐一样",
        yuewen_to_merge=["午餐同晚餐一样㗎"],
        yuewen_merged="午餐同晚餐一样㗎",
    ),
    MergeTestCase(
        zhongwen="晚餐呢？",
        yuewen_to_merge=["咁晚餐呢"],
        yuewen_merged="咁晚餐呢？",
    ),
    MergeTestCase(
        zhongwen="晚餐不就是特餐",
        yuewen_to_merge=["晚餐就即系特餐啰"],
        yuewen_merged="晚餐就即系特餐啰",
    ),
    MergeTestCase(
        zhongwen="不是说特餐卖光了吗？",
        yuewen_to_merge=["咁你头先又话冇特餐"],
        yuewen_merged="咁你头先又话冇特餐？",
    ),
    MergeTestCase(
        zhongwen="特餐卖光了，要试试快餐吗？都一样的",
        yuewen_to_merge=["系呀", "特餐系卖晒呀", "咁你试唔试下个快餐啦", "一样嘅啫"],
        yuewen_merged="系呀，特餐系卖晒呀，咁你试唔试下个快餐啦？一样嘅啫",
    ),
    MergeTestCase(
        zhongwen="来两份快餐吧",
        yuewen_to_merge=["咁两份快餐啦"],
        yuewen_merged="咁两份快餐啦",
    ),
]
merge_test_cases_block_71 = [
    MergeTestCase(
        zhongwen="对不起，没快餐了",
        yuewen_to_merge=["唔好意思冇快餐呀"],
        yuewen_merged="唔好意思，冇快餐呀",
    ),
    MergeTestCase(
        zhongwen="太过分了吧？你们究竟有吃的没？",
        yuewen_to_merge=["嚟唔嚟普啲呀", "噉你哋究竟有啲咩餐呀"],
        yuewen_merged="嚟唔嚟普啲呀？噉你哋究竟有啲咩餐呀？",
    ),
    MergeTestCase(
        zhongwen="午餐吧，午餐精采呀",
        yuewen_to_merge=["午餐啦"],
        yuewen_merged="午餐啦",
    ),
    MergeTestCase(
        zhongwen="怎么个精采法？",
        yuewen_to_merge=["午餐好嘢呀", "点好嘢法呀"],
        yuewen_merged="午餐好嘢呀，点好嘢法呀？",
    ),
    MergeTestCase(
        zhongwen="跟晚餐一样精采",
        yuewen_to_merge=["同晚餐一样咁好嘢"],
        yuewen_merged="同晚餐一样咁好嘢",
    ),
    MergeTestCase(
        zhongwen="晚餐又怎样呢？",
        yuewen_to_merge=["噉晚餐又点好嘢法呀"],
        yuewen_merged="噉晚餐又点好嘢法呀？",
    ),
    MergeTestCase(
        zhongwen="跟常餐一样精采",
        yuewen_to_merge=["同上餐一样咁好嘢啰"],
        yuewen_merged="同上餐一样咁好嘢啰",
    ),
    MergeTestCase(
        zhongwen="常餐又怎样呢？",
        yuewen_to_merge=["噉上餐又点好嘢法呀"],
        yuewen_merged="噉上餐又点好嘢法呀？",
    ),
    MergeTestCase(
        zhongwen="常餐早卖光了，你说精采不？",
        yuewen_to_merge=["上餐", "上餐一早卖晒啦", "你话好唔好嘢"],
        yuewen_merged="上餐，上餐一早卖晒啦，你话好唔好嘢？",
    ),
    MergeTestCase(
        zhongwen="好吧好吧！两份午餐好了",
        yuewen_to_merge=["好啦好啦", "要两份午餐啦"],
        yuewen_merged="好啦好啦！要两份午餐啦",
    ),
]
merge_test_cases_block_72 = [
    MergeTestCase(
        zhongwen="对不起，午餐卖光了",
        yuewen_to_merge=["唔好意思", "午餐卖晒"],
        yuewen_merged="唔好意思，午餐卖晒",
    ),
    MergeTestCase(
        zhongwen="要试试我们的晚餐吗？都一样的",
        yuewen_to_merge=["试唔试下我哋嘅晚餐啦", "一样嘅啫"],
        yuewen_merged="试唔试下我哋嘅晚餐啦？一样嘅啫",
    ),
    MergeTestCase(
        zhongwen="光天白日，吃什么鬼晚餐？",
        yuewen_to_merge=["日光日白食乜鬼嘢晚餐啊"],
        yuewen_merged="日光日白食乜鬼嘢晚餐啊？",
    ),
    MergeTestCase(
        zhongwen="唉，说是说晚餐，还不就是午餐？",
        yuewen_to_merge=["系", "个名叫晚餐啫", "其实唔系真系午餐"],
        yuewen_merged="系，个名叫晚餐啫，其实唔系真系午餐？",
    ),
    MergeTestCase(
        zhongwen="好吧好吧，拜托！两份晚餐！快！",
        yuewen_to_merge=["好啦好啦", "怕咗你啦", "要两份晚餐啦", "快啲手啊"],
        yuewen_merged="好啦好啦，怕咗你啦！要两份晚餐啦！快啲手啊！",
    ),
    MergeTestCase(
        zhongwen="要快吗？那得吃快餐了！",
        yuewen_to_merge=["想快", "想快就要快餐啊"],
        yuewen_merged="想快，想快就要快餐啊！",
    ),
]
mlamd_merge_test_cases: list[MergeTestCase] = sum(
    (globals()[f"merge_test_cases_block_{i}"] for i in range(73)), []
)
"""MLAMD 粤文 merging test cases."""
# endregion


# region 粤文 Proof Test Cases
proof_test_cases_block_0 = [
    ProofTestCase(
        zhongwen="在麦太即将临盆的时候",
        yuewen="就喺麦太快要临盘嘅时候",
        yuewen_proofread="就喺麦太快要临盆嘅时候",
        note="Corrected '临盘' to '临盆' as '临盆' is the correct term for childbirth.",
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="一只胶兜在九龙上空飞过",
        yuewen="有一个胶兜喺九龙上空飞过",
        yuewen_proofread="有一个胶兜喺九龙上空飞过",
        note="",
    ),
    ProofTestCase(
        zhongwen="沿荔枝角道直出大角咀道",
        yuewen="沿住荔枝角度直出大角咀度",
        yuewen_proofread="沿住荔枝角道直出大角咀道",
        note="Corrected '荔枝角度' to '荔枝角道' and '大角咀度' to '大角咀道' as '道' "
        "is the correct word for 'road' in both cases.",
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="经好彩酒家左转花园街乐园牛丸王⋯",
        yuewen="经过好彩走家再左转返出花园街乐园牛园望对上⋯",
        yuewen_proofread="经过好彩酒家再左转返出花园街乐园牛丸王对上⋯",
        note="Corrected '走家' to '酒家' and '牛园望' to '牛丸王' as these are likely "
        "mishearings of the intended place names.",
    ),
    ProofTestCase(
        zhongwen="更正一下：",
        yuewen="都系唔好：",
        yuewen_proofread="都系唔好：",
        note="",
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="先到街市大楼妹记鱼腩粥外边",
        yuewen="先去街市大楼𠮶间妹记鱼腩粥𠮶度",
        yuewen_proofread="先去街市大楼𠮶间妹记鱼腩粥𠮶度",
        note="",
    ),
    ProofTestCase(
        zhongwen="转呀，转⋯再更正一下：",
        yuewen="转下，转下⋯都系唔好：",
        yuewen_proofread="转下，转下⋯都系唔好：",
        note="",
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="直出亚皆老街跨过火车桥右转太平道",
        yuewen="都系出返去阿街路街飞过火车桥右转入太平道",
        yuewen_proofread="都系出返去亚皆老街飞过火车桥右转入太平道",
        note="Corrected '阿街路街' to '亚皆老街' as it is a mishearing of the street "
        "name '亚皆老街'.",
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="再右拐窝打老道向女人街方向飞⋯",
        yuewen="再右转抹返出去窝打炉道向女人街方向飞下下⋯",
        yuewen_proofread="再右转抹返出去窝打老道向女人街方向飞下下⋯",
        note="Corrected '炉' to '老' in '窝打炉道' as it was likely a mishearing of "
        "the correct street name '窝打老道'.",
    ),
    ProofTestCase(
        zhongwen="飞呀，飞⋯",
        yuewen="飞下，飞下⋯",
        yuewen_proofread="飞下，飞下⋯",
        note="",
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="胶兜最后飞进广华医院候产房",
        yuewen="最后胶兜飞咗入广华医院嘅后产房",
        yuewen_proofread="最后胶兜飞咗入广华医院嘅候产房",
        note="Corrected '后产房' to '候产房' as '候产房' (waiting room for childbirth) "
        "matches the intended meaning and is a plausible mishearing.",
    ),
    ProofTestCase(
        zhongwen="也就是在麦太右边额角上⋯",
        yuewen="亦即系麦太右边云晶对上⋯",
        yuewen_proofread="亦即系麦太右边魂精对上⋯",
        note="Corrected '云晶' to '魂精' as '魂精' is a valid Cantonese term for "
        "'temple' and matches the meaning of '额角' in the 中文.",
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="更正：左边额角上⋯",
        yuewen="都系唔好：左边云晶对上⋯",
        yuewen_proofread="都系唔好：左边魂精对上⋯",
        note="Corrected '云晶' to '魂精' as '魂精' accurately refers to the side of "
        "the head and matches the meaning of '额角' in the 中文.",
    ),
    ProofTestCase(
        zhongwen="转呀，转⋯",
        yuewen="转下，转下，转下噉⋯",
        yuewen_proofread="转下，转下，转下噉⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="麦太认定这是异像",
        yuewen="麦太认定呢个系异象",
        yuewen_proofread="麦太认定呢个系异像",
        note="Corrected '异象' to '异像' as '异像' is the correct term in this context",
    ),
    ProofTestCase(
        zhongwen="于是向额角上的胶兜许愿",
        yuewen="于是向云晶对上嘅胶兜许愿",
        yuewen_proofread="于是向魂精对上嘅胶兜许愿",
        note="Corrected '云晶' to '魂精' as '魂精' is a valid Cantonese anatomical "
        "term for the temple area and fits the context.",
    ),
    ProofTestCase(
        zhongwen="脑海中同时出现即将诞生的儿子容貌⋯",
        yuewen="而脑入面亦即时出现咗快要出世个仔嘅样⋯",
        yuewen_proofread="而脑入面亦即时出现咗快要出世个仔嘅样⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="希望他好聪明，读书好叻！",
        yuewen="希望佢好聪明，读书好叻！",
        yuewen_proofread="希望佢好聪明，读书好叻！",
        note="",
    ),
    ProofTestCase(
        zhongwen="胶兜对麦太的愿望似乎没有反应",
        yuewen="胶兜对麦太嘅愿望似乎冇咩表示",
        yuewen_proofread="胶兜对麦太嘅愿望似乎冇咩表示",
        note="",
    ),
    ProofTestCase(
        zhongwen="于是她向胶兜补充说：",
        yuewen="于是佢对住胶兜补充噉话：",
        yuewen_proofread="于是佢对住胶兜补充噉话：",
        note="",
    ),
    ProofTestCase(
        zhongwen="或者读书唔叻，工作叻呢？",
        yuewen="或者读书唔叻，出嚟做嘢叻啦？",
        yuewen_proofread="或者读书唔叻，出嚟做嘢叻啦？",
        note="",
    ),
    ProofTestCase(
        zhongwen="又或者⋯",
        yuewen="又或者呢⋯",
        yuewen_proofread="又或者呢⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="又或者好靓仔，好靓仔",
        yuewen="又或者系好靓仔，好靓仔",
        yuewen_proofread="又或者系好靓仔，好靓仔",
        note="",
    ),
    ProofTestCase(
        zhongwen="跟周润发，梁朝伟那么靓仔！",
        yuewen="好似周润发，同埋梁朝伟咁靓仔！",
        yuewen_proofread="好似周润发，同埋梁朝伟咁靓仔！",
        note="",
    ),
    ProofTestCase(
        zhongwen="胶兜仍然在转，毫无点头迹象",
        yuewen="胶兜依然系噉喺度转，好似一啲应承嘅迹象都冇",
        yuewen_proofread="胶兜依然系噉喺度转，好似一啲应承嘅迹象都冇",
        note="",
    ),
    ProofTestCase(
        zhongwen="麦太一时心虚",
        yuewen="麦太一时心虚",
        yuewen_proofread="麦太一时心虚",
        note="",
    ),
    ProofTestCase(
        zhongwen="赶忙趁胶兜落地前另许一个愿望：",
        yuewen="嗱嗱嗱喺胶兜未落地之前起过另外一个愿望：",
        yuewen_proofread="嗱嗱嗱喺胶兜未落地之前起过另外一个愿望：",
        note="",
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="唔聪明唔靓仔也算了，只要福星高照",
        yuewen="就算唔系咁聪明同咁靓仔，只要复星高照",
        yuewen_proofread="就算唔系咁聪明同咁靓仔，只要福星高照",
        note="Corrected '复星' to '福星' as '福星' is the correct term for good "
        "fortune, matching the intended meaning.",
    ),
    ProofTestCase(
        zhongwen="一世够运，逢凶化吉！",
        yuewen="一世救运，乜嘢事都逢凶化㗎喇！",
        yuewen_proofread="一世够运，乜嘢事都逢凶化㗎喇！",
        note="Corrected '救运' to '够运' as '够运' is the correct term for "
        "being lucky, matching the original meaning.",
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="靠自己能力解决事情当然最好",
        yuewen="佢靠自己有料解决啲嘢就梗系好啦",
        yuewen_proofread="佢靠自己有料解决啲嘢就梗系好啦",
        note="",
    ),
    ProofTestCase(
        zhongwen="不过运气还是很重要的",
        yuewen="不过运气都好紧要㖞",
        yuewen_proofread="不过运气都好紧要㖞",
        note="",
    ),
    ProofTestCase(
        zhongwen="虽是说像梁朝伟周润发也行运定了",
        yuewen="虽然似梁朝伟周润发都唔返去冒运行",
        yuewen_proofread="虽然似梁朝伟周润发都行运定咗",
        note="Corrected '唔返去冒运行' to '都行运定咗' as the original phrase was a "
        "mishearing; '行运定咗' matches the meaning of '行运定了'.",
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="但总得要叻仔呀！",
        yuewen="但系都要叻仔先得㗎！",
        yuewen_proofread="但系都要叻仔先得㗎！",
        note="",
    ),
]
proof_test_cases_block_1 = [
    ProofTestCase(
        zhongwen="最后，胶兜「嘀督」一声落地",
        yuewen="最后，胶兜「滴嘟」一声咁落地",
        yuewen_proofread="最后，胶兜「嘀督」一声咁落地",
        note="Corrected '滴嘟' to '嘀督' to match the intended onomatopoeic sound "
        "described in the original text.",
    ),
    ProofTestCase(
        zhongwen="嘀督？嘀督，就是答应了",
        yuewen="滴嘟？滴嘟㖞，即系应承啦",
        yuewen_proofread="嘀督？嘀督㖞，即系应承啦",
        note="Corrected '滴嘟' to '嘀督' to match the intended sound and meaning of "
        "'嘀督' as a phonetic rendering of '嘀督' (答应了).",
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="麦太想，这次走运了！",
        yuewen="麦太心谂，今次冇死喇！",
        yuewen_proofread="麦太心谂，今次冇死喇！",
        note="",
    ),
    ProofTestCase(
        zhongwen="可是答应了些什么呢？",
        yuewen="但你应承咗啲咩呢？",
        yuewen_proofread="但你应承咗啲咩呢？",
        note="",
    ),
    ProofTestCase(
        zhongwen="叻仔？好运？",
        yuewen="叻仔？好运？",
        yuewen_proofread="叻仔？好运？",
        note="",
    ),
    ProofTestCase(
        zhongwen="还是似周润发？",
        yuewen="定系话自周人烦啊？",
        yuewen_proofread="定系话似周润发啊？",
        note="Corrected '自周人烦' to '似周润发' as it is a mishearing of the actor's "
        "name '周润发'.",
    ),
    ProofTestCase(
        zhongwen="为了纪念这赐福的胶兜",
        yuewen="为咗纪念呢个赤幅嘅胶兜",
        yuewen_proofread="为咗纪念呢个赐福嘅胶兜",
        note="Corrected '赤幅' to '赐福' as '赐福' is the correct term and '赤幅' is a "
        "likely mishearing.",
    ),
    ProofTestCase(
        zhongwen="麦太决定把儿子命名麦胶",
        yuewen="麦太决定将个仔嘅名叫做麦胶",
        yuewen_proofread="麦太决定将个仔嘅名叫做麦胶",
        note="",
    ),
    ProofTestCase(
        zhongwen="不行，胶胶声，多难听！",
        yuewen="都系唔好，胶胶声，咁难听！",
        yuewen_proofread="都系唔好，胶胶声，咁难听！",
        note="",
    ),
    ProofTestCase(
        zhongwen="还是唤他麦兜！",
        yuewen="不如叫麦兜啦！",
        yuewen_proofread="不如叫麦兜啦！",
        note="",
    ),
    ProofTestCase(
        zhongwen="各位⋯",
        yuewen="各位⋯",
        yuewen_proofread="各位⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="我就是险些给定名麦胶的小朋友⋯",
        yuewen="我就系呢个差少少就叫做麦胶嘅小朋友⋯",
        yuewen_proofread="我就系呢个差少少就叫做麦胶嘅小朋友⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="麦兜！",
        yuewen="麦兜！",
        yuewen_proofread="麦兜！",
        note="",
    ),
]
proof_test_cases_block_2 = [
    ProofTestCase(
        zhongwen="麦太，没见面一阵",
        yuewen="咦，麦太，咩唔见你一排",
        yuewen_proofread="咦，麦太，咩唔见你一排",
        note="",
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="怎么小腿粗起来了？",
        yuewen="个脚刮囊粗咗咁多呀？",
        yuewen_proofread="个脚瓜囊粗咗咁多呀？",
        note="Corrected '脚刮囊' to '脚瓜囊' as '脚瓜囊' is the correct Cantonese term for "
        "'calf', matching the meaning of '小腿'.",
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="可怜呀，每天扑来扑去⋯",
        yuewen="鬼咩，日日扑嚟扑去⋯",
        yuewen_proofread="鬼咩，日日扑嚟扑去⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="替儿子找幼稚园！",
        yuewen="同我仔揾幼稚园吖嘛！",
        yuewen_proofread="同我仔揾幼稚园吖嘛！",
        note="",
    ),
    ProofTestCase(
        zhongwen="怎么不试一试好彩酒楼对面",
        yuewen="点解唔试下好彩走楼斜对面",
        yuewen_proofread="点解唔试下好彩酒楼斜对面",
        note="Corrected '走楼' to '酒楼' as '酒楼' is the correct term for restaurant, "
        "matching the original meaning.",
    ),
    ProofTestCase(
        zhongwen="旧中侨国货楼上的⋯",
        yuewen="旧中桥百货公司楼上𠮶间⋯",
        yuewen_proofread="旧中侨百货公司楼上𠮶间⋯",
        note="Corrected '中桥' to '中侨' as '中侨' is the correct name, matching the "
        "original 中文.",
    ),
    ProofTestCase(
        zhongwen="春田花花幼稚园？",
        yuewen="春田花花幼稚园呢？",
        yuewen_proofread="春田花花幼稚园呢？",
        note="",
    ),
    ProofTestCase(
        zhongwen="就是座落界限街南昌街交界⋯",
        yuewen="就系坐落喺界限街同南昌街交界⋯",
        yuewen_proofread="就系坐落喺界限街同南昌街交界⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="银城美食广场附近的⋯",
        yuewen="银城美食广场附近𠮶间⋯",
        yuewen_proofread="银城美食广场附近𠮶间⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="春田花花幼稚园？",
        yuewen="春田花花幼稚园呀？",
        yuewen_proofread="春田花花幼稚园呀？",
        note="",
    ),
    ProofTestCase(
        zhongwen="对！深水埗地铁站步行不用10分钟！",
        yuewen="系呀！深水埗地铁站口行过去唔使十分钟呀！",
        yuewen_proofread="系呀！深水埗地铁站口行过去唔使十分钟呀！",
        note="",
    ),
    ProofTestCase(
        zhongwen="春田花花幼稚园，师资优良⋯",
        yuewen="春田花花幼稚园，诗诗优良⋯",
        yuewen_proofread="春田花花幼稚园，师资优良⋯",
        note="Corrected '诗诗' to '师资' as '师资' is the correct term for teaching "
        "staff, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="而且还有西人教英文！",
        yuewen="仲系西人教英文添㗎！",
        yuewen_proofread="仲系西人教英文添㗎！",
        note="",
    ),
    ProofTestCase(
        zhongwen="西人教英文？",
        yuewen="咦，西人教英文？",
        yuewen_proofread="咦，西人教英文？",
        note="",
    ),
    ProofTestCase(
        zhongwen="是呀！",
        yuewen="系呀！",
        yuewen_proofread="系呀！",
        note="",
    ),
    ProofTestCase(
        zhongwen="春田花花，确有好多西人呀！",
        yuewen="春田花花，真系好多西人㗎！",
        yuewen_proofread="春田花花，真系好多西人㗎！",
        note="",
    ),
]
proof_test_cases_block_3 = [
    ProofTestCase(
        zhongwen="这个猪样白兔小朋友⋯",
        yuewen="呢个扮紧白兔猪样嘅小朋友⋯",
        yuewen_proofread="呢个扮紧白兔猪样嘅小朋友⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="横看竖看也不像发哥伟仔的一个⋯",
        yuewen="即系横睇掂睇都唔似发哥或者位仔𠮶个呢⋯",
        yuewen_proofread="即系横睇掂睇都唔似发哥或者伟仔𠮶个呢⋯",
        note="Corrected '位仔' to '伟仔' as it is a mishearing of the name '伟仔', referring to 梁朝伟.",
    ),
    ProofTestCase(
        zhongwen="就是我，麦兜",
        yuewen="就系我，麦兜",
        yuewen_proofread="就系我，麦兜",
        note="",
    ),
    ProofTestCase(
        zhongwen="这是我就读的幼稚园",
        yuewen="呢间就系我读嘅幼稚园",
        yuewen_proofread="呢间就系我读嘅幼稚园",
        note="",
    ),
    ProofTestCase(
        zhongwen="校长是潮州人",
        yuewen="校长系潮州人",
        yuewen_proofread="校长系潮州人",
        note="",
    ),
    ProofTestCase(
        zhongwen="可能是潮州口音的关系",
        yuewen="可能仲系讲紧潮州话嘅",
        yuewen_proofread="可能仲系讲紧潮州话嘅",
        note="",
    ),
    ProofTestCase(
        zhongwen="这么多年来⋯",
        yuewen="所以咁多年嚟⋯",
        yuewen_proofread="所以咁多年嚟⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="我其实不大明白他的说话",
        yuewen="我其实唔系好知佢噏文",
        yuewen_proofread="我其实唔系好知佢噏乜",
        note="Corrected '噏文' to '噏乜' as '噏乜' (what he's saying) matches the "
        "meaning of '他的说话', while '噏文' is likely a mishearing.",
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="蛋挞！　　蛋挞！",
        yuewen="大湖荒岩宅",
        yuewen_proofread="",
        note="Cleared as '大湖荒岩宅' bears no resemblance to the original phrase "
        "'蛋挞！　　蛋挞！' and is clearly a pure artifact. ",
    ),
    ProofTestCase(
        zhongwen="荔芋火鸭礼！　　荔芋火鸭礼！",
        yuewen="湾吉校坟交涉设",
        yuewen_proofread="",
        note="Cleared as '湾吉校坟交涉设' bears no resemblance to the original phrase "
        "'荔芋火鸭礼！　　荔芋火鸭礼！' and is clearly a pure artifact.",
    ),
    ProofTestCase(
        zhongwen="也不能忘记校训九十八！",
        yuewen="都唔好湾吉校坟交涉白！",
        yuewen_proofread="",
        note="Cleared as '都唔好湾吉校坟交涉白！' bears no resemblance to the original "
        "phrase '也不能忘记校训九十八！' and is clearly a pure artifact.",
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="好！各位同学⋯",
        yuewen="𠮶个位同学⋯",
        yuewen_proofread="𠮶个位同学⋯",
        note="",
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="今天的早会主要是跟大家分享",
        yuewen="今次座会系要同大家分享",
        yuewen_proofread="今次早会系要同大家分享",
        note="Corrected '座会' to '早会' as it is a mishearing of '早会', which matches "
        "the meaning of the 中文.",
    ),
    ProofTestCase(
        zhongwen="一个重要主题：",
        yuewen="一个可重要嘅主题：",
        yuewen_proofread="一个可重要嘅主题：",
        note="",
    ),
    ProofTestCase(
        zhongwen="小朋友，这个月你们交过学费没有？",
        yuewen="小朋友，你哋今个月交咗学费咩呀？",
        yuewen_proofread="小朋友，你哋今个月交咗学费咩呀？",
        note="",
    ),
    ProofTestCase(
        zhongwen="交过了！",
        yuewen="交",
        yuewen_proofread="交过咗！",
        note="Added '过咗' to match the completed action indicated by '交过了' in the "
        "中文; the original '交' is likely a transcription omission.",
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="太好了！大家去上堂吧",
        yuewen="哎，好在！噉大家可以返去上堂喇",
        yuewen_proofread="哎，好啦！噉大家可以返去上堂喇",
        note="Corrected '好在' to '好啦' as '好啦' is a more appropriate expression.",
    ),
]
proof_test_cases_block_4 = []
proof_test_cases_block_5 = []
proof_test_cases_block_6 = []
proof_test_cases_block_7 = []
proof_test_cases_block_8 = []
proof_test_cases_block_9 = []
proof_test_cases_block_10 = []
proof_test_cases_block_11 = []
proof_test_cases_block_12 = []
proof_test_cases_block_13 = []
proof_test_cases_block_14 = []
proof_test_cases_block_15 = []
proof_test_cases_block_16 = []
proof_test_cases_block_17 = []
proof_test_cases_block_18 = []
proof_test_cases_block_19 = []
proof_test_cases_block_20 = []
proof_test_cases_block_21 = []
proof_test_cases_block_22 = []
proof_test_cases_block_23 = []
proof_test_cases_block_24 = []
proof_test_cases_block_25 = []
proof_test_cases_block_26 = []
proof_test_cases_block_27 = []
proof_test_cases_block_28 = []
proof_test_cases_block_29 = []
proof_test_cases_block_30 = []
proof_test_cases_block_31 = []
proof_test_cases_block_32 = []
proof_test_cases_block_33 = []
proof_test_cases_block_34 = []
proof_test_cases_block_35 = []
proof_test_cases_block_36 = []
proof_test_cases_block_37 = []
proof_test_cases_block_38 = []
proof_test_cases_block_39 = []
proof_test_cases_block_40 = []
proof_test_cases_block_41 = []
proof_test_cases_block_42 = []
proof_test_cases_block_43 = []
proof_test_cases_block_44 = []
proof_test_cases_block_45 = []
proof_test_cases_block_46 = []
proof_test_cases_block_47 = []
proof_test_cases_block_48 = []
proof_test_cases_block_49 = []
proof_test_cases_block_50 = []
proof_test_cases_block_51 = []
proof_test_cases_block_52 = []
proof_test_cases_block_53 = []
proof_test_cases_block_54 = []
proof_test_cases_block_55 = []
proof_test_cases_block_56 = []
proof_test_cases_block_57 = []
proof_test_cases_block_58 = []
proof_test_cases_block_59 = []
proof_test_cases_block_60 = []
proof_test_cases_block_61 = []
proof_test_cases_block_62 = []
proof_test_cases_block_63 = []
proof_test_cases_block_64 = []
proof_test_cases_block_65 = []
proof_test_cases_block_66 = []
proof_test_cases_block_67 = []
proof_test_cases_block_68 = []
proof_test_cases_block_69 = []
proof_test_cases_block_70 = [
    ProofTestCase(
        zhongwen="对不起，常餐卖光了",
        yuewen="唔好意思，上餐卖晒",
        yuewen_proofread="唔好意思，常餐卖晒",
        note="Corrected '上餐' to '常餐' as '常餐' is the correct term for the set meal, matching the meaning of the 中文.",
    ),
    ProofTestCase(
        zhongwen="那改要特餐吧",
        yuewen="咁改要特餐啦",
        yuewen_proofread="咁改要特餐啦",
        note="",
    ),
    ProofTestCase(
        zhongwen="特餐？特餐有什么吃？",
        yuewen="特餐？特餐有咩食㗎？",
        yuewen_proofread="特餐？特餐有咩食㗎？",
        note="",
    ),
    ProofTestCase(
        zhongwen="特餐即是午餐呀",
        yuewen="特餐就即系午餐啰",
        yuewen_proofread="特餐就即系午餐啰",
        note="",
    ),
    ProofTestCase(
        zhongwen="午餐又吃什么呢？",
        yuewen="午餐食乜嘢㗎？",
        yuewen_proofread="午餐食乜嘢㗎？",
        note="",
    ),
    ProofTestCase(
        zhongwen="都是晚餐那些吧",
        yuewen="都系晚餐𠮶啲嘢啰",
        yuewen_proofread="都系晚餐𠮶啲嘢啰",
        note="",
    ),
    ProofTestCase(
        zhongwen="什么是晚餐？",
        yuewen="咁乜嘢系晚餐呀？",
        yuewen_proofread="咁乜嘢系晚餐呀？",
        note="",
    ),
    ProofTestCase(
        zhongwen="跟快餐一样",
        yuewen="同快餐一样啰",
        yuewen_proofread="同快餐一样啰",
        note="",
    ),
    ProofTestCase(
        zhongwen="快餐吃什么？",
        yuewen="咁快餐食咩㗎？",
        yuewen_proofread="咁快餐食咩㗎？",
        note="",
    ),
    ProofTestCase(
        zhongwen="唉，快餐不就是常餐",
        yuewen="系，快餐就即系上餐啰",
        yuewen_proofread="系，快餐就即系常餐啰",
        note="Corrected '上餐' to '常餐' as '常餐' is the correct term for 'regular set meal', matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="常餐不是卖光了吗？",
        yuewen="咁你头先又话冇上餐，系呀，上餐就系卖晒呀？",
        yuewen_proofread="咁你头先又话冇常餐，系呀，常餐就系卖晒呀？",
        note="Corrected '上餐' to '常餐' as '常餐' is the correct term for the set meal, matching the meaning of '常餐' in the 中文; '上餐' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="对，常餐卖光了，要吃特餐吗？",
        yuewen="咁你试唔试下特餐啦？",
        yuewen_proofread="咁你试唔试下特餐啦？",
        note="",
    ),
    ProofTestCase(
        zhongwen="来两份特餐吧",
        yuewen="两份特餐啦",
        yuewen_proofread="两份特餐啦",
        note="",
    ),
    ProofTestCase(
        zhongwen="对不起，特餐卖光了",
        yuewen="唔好意思，特餐卖晒嘅",
        yuewen_proofread="唔好意思，特餐卖晒喇",
        note="Replaced '卖晒嘅' with '卖晒喇' as '卖晒喇' is the natural way to indicate 'sold out' in Cantonese, while '卖晒嘅' is likely a mishearing or unnatural ending.",
    ),
    ProofTestCase(
        zhongwen="妈妈，改快餐吧",
        yuewen="妈妈，不如改快餐啦",
        yuewen_proofread="妈妈，不如改快餐啦",
        note="",
    ),
    ProofTestCase(
        zhongwen="快餐有什么？",
        yuewen="快餐有咩㗎？",
        yuewen_proofread="快餐有咩㗎？",
        note="",
    ),
    ProofTestCase(
        zhongwen="快餐即是常餐",
        yuewen="快餐即系上餐",
        yuewen_proofread="快餐即系常餐",
        note="Corrected '上餐' to '常餐' as '常餐' is the correct term for 'regular set meal', matching the meaning of the 中文.",
    ),
    ProofTestCase(
        zhongwen="常餐又有什么呢？",
        yuewen="咁上餐有咩㗎？",
        yuewen_proofread="常餐有咩㗎？",
        note="Corrected '上餐' to '常餐' as '常餐' is the correct term for the set meal, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="常餐即是午餐",
        yuewen="上餐就即系午餐啰",
        yuewen_proofread="常餐就即系午餐啰",
        note="Corrected '上餐' to '常餐' as '常餐' is the correct term for 'set meal' or 'regular meal', matching the meaning of '常餐' in the 中文.",
    ),
    ProofTestCase(
        zhongwen="那么午餐又有什么吃？",
        yuewen="哎呀，咁午餐有咩食呀？",
        yuewen_proofread="哎呀，咁午餐有咩食呀？",
        note="",
    ),
    ProofTestCase(
        zhongwen="午餐跟晚餐一样",
        yuewen="午餐同晚餐一样㗎",
        yuewen_proofread="午餐同晚餐一样㗎",
        note="",
    ),
    ProofTestCase(
        zhongwen="晚餐呢？",
        yuewen="咁晚餐呢？",
        yuewen_proofread="咁晚餐呢？",
        note="",
    ),
    ProofTestCase(
        zhongwen="晚餐不就是特餐",
        yuewen="晚餐就即系特餐啰",
        yuewen_proofread="晚餐就即系特餐啰",
        note="",
    ),
    ProofTestCase(
        zhongwen="不是说特餐卖光了吗？",
        yuewen="咁你头先又话冇特餐？",
        yuewen_proofread="咁你头先又话冇特餐？",
        note="",
    ),
    ProofTestCase(
        zhongwen="特餐卖光了，要试试快餐吗？都一样的",
        yuewen="系呀，特餐系卖晒呀，咁你试唔试下个快餐啦？一样嘅啫",
        yuewen_proofread="系呀，特餐系卖晒呀，咁你试唔试下个快餐啦？一样嘅啫",
        note="",
    ),
    ProofTestCase(
        zhongwen="来两份快餐吧",
        yuewen="咁两份快餐啦",
        yuewen_proofread="咁两份快餐啦",
        note="",
    ),
]
proof_test_cases_block_71 = [
    ProofTestCase(
        zhongwen="对不起，没快餐了",
        yuewen="唔好意思，冇快餐呀",
        yuewen_proofread="唔好意思，冇快餐呀",
        note="",
    ),
    ProofTestCase(
        zhongwen="太过分了吧？你们究竟有吃的没？",
        yuewen="嚟唔嚟普啲呀？噉你哋究竟有啲咩餐呀？",
        yuewen_proofread="嚟唔嚟普啲呀？噉你哋究竟有啲咩餐呀？",
        note="",
    ),
    ProofTestCase(
        zhongwen="午餐吧，午餐精采呀",
        yuewen="午餐啦",
        yuewen_proofread="午餐啦",
        note="",
    ),
    ProofTestCase(
        zhongwen="怎么个精采法？",
        yuewen="午餐好嘢呀，点好嘢法呀？",
        yuewen_proofread="午餐好嘢呀，点好嘢法呀？",
        note="",
    ),
    ProofTestCase(
        zhongwen="跟晚餐一样精采",
        yuewen="同晚餐一样咁好嘢",
        yuewen_proofread="同晚餐一样咁好嘢",
        note="",
    ),
    ProofTestCase(
        zhongwen="晚餐又怎样呢？",
        yuewen="噉晚餐又点好嘢法呀？",
        yuewen_proofread="噉晚餐又点好嘢法呀？",
        note="",
    ),
    ProofTestCase(
        zhongwen="跟常餐一样精采",
        yuewen="同上餐一样咁好嘢啰",
        yuewen_proofread="同上餐一样咁好嘢啰",
        note="",
    ),
    ProofTestCase(
        zhongwen="常餐又怎样呢？",
        yuewen="噉上餐又点好嘢法呀？",
        yuewen_proofread="噉常餐又点好嘢法呀？",
        note="Corrected '上餐' to '常餐' as '常餐' is the correct term for the set meal, "
        "matching the meaning of '常餐' in the 中文; '上餐' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="常餐早卖光了，你说精采不？",
        yuewen="上餐，上餐一早卖晒啦，你话好唔好嘢？",
        yuewen_proofread="常餐，常餐一早卖晒啦，你话好唔好嘢？",
        note="Corrected '上餐' to '常餐' as '常餐' is the correct term for the set meal "
        "referenced in the 中文, and '上餐' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="好吧好吧！两份午餐好了",
        yuewen="好啦好啦！要两份午餐啦",
        yuewen_proofread="好啦好啦！要两份午餐啦",
        note="",
    ),
]
proof_test_cases_block_72 = [
    ProofTestCase(
        zhongwen="对不起，午餐卖光了",
        yuewen="唔好意思，午餐卖晒",
        yuewen_proofread="唔好意思，午餐卖晒",
        note="",
    ),
    ProofTestCase(
        zhongwen="要试试我们的晚餐吗？都一样的",
        yuewen="试唔试下我哋嘅晚餐啦？一样嘅啫",
        yuewen_proofread="试唔试下我哋嘅晚餐啦？一样嘅啫",
        note="",
    ),
    ProofTestCase(
        zhongwen="光天白日，吃什么鬼晚餐？",
        yuewen="日光日白食乜鬼嘢晚餐啊？",
        yuewen_proofread="日光日白食乜鬼嘢晚餐啊？",
        note="",
    ),
    ProofTestCase(
        zhongwen="唉，说是说晚餐，还不就是午餐？",
        yuewen="系，个名叫晚餐啫，其实唔系真系午餐？",
        yuewen_proofread="系，个名叫晚餐啫，其实唔系真系午餐？",
        note="",
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="好吧好吧，拜托！两份晚餐！快！",
        yuewen="好啦好啦，怕咗你啦！要两份晚餐啦！快啲手啊！",
        yuewen_proofread="好啦好啦，怕咗你啦！要两份晚餐啦！快啲手啊！",
        note="",
    ),
    ProofTestCase(
        zhongwen="要快吗？那得吃快餐了！",
        yuewen="想快，想快就要快餐啊！",
        yuewen_proofread="想快，想快就要快餐啊！",
        note="",
    ),
]
mlamd_proof_test_cases: list[ProofTestCase] = sum(
    (globals()[f"proof_test_cases_block_{i}"] for i in range(73)), []
)
"""MLAMD 粤文 proofing test cases."""
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
    "mlamd_distribute_test_cases",
    "mlamd_shift_test_cases",
    "mlamd_merge_test_cases",
    "mlamd_proof_test_cases",
]

if __name__ == "__main__":
    set_logging_verbosity(2)

    test_case_lists = {
        "Distribute": mlamd_distribute_test_cases,
        "Shift": mlamd_shift_test_cases,
        "Merge": mlamd_merge_test_cases,
        "Proof": mlamd_proof_test_cases,
    }
    for test_case_type, test_cases in test_case_lists.items():
        info(f"Validating {test_case_type} test cases...")

        # Validate test cases
        test_case_dict = {}
        noops = 0
        for test_case in test_cases:
            if test_case.noop:
                debug(test_case.source_str)
                noops += 1
            else:
                info(test_case.source_str)
            if test_case.key in test_case_dict:
                raise ScinoephileError(f"Duplicate key found:\n{test_case.key}")
            test_case_dict[test_case.key] = test_case
        info(
            f"{test_case_type} test cases validated: {len(test_case_dict)} "
            f"unique keys, of which {len(test_cases) - noops} direct changes."
        )

        # Validate queries
        query_dict = {}
        for test_case in test_cases:
            debug(test_case.query.source_str)
            if test_case.query.key in query_dict:
                raise ScinoephileError(
                    f"Duplicate query key found:\n{test_case.query.key}"
                )
            query_dict[test_case.query.key] = test_case.query
        info(f"{test_case_type} queries validated: {len(query_dict)} unique keys.")
