#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MLAMD."""

from __future__ import annotations

import pytest
from PIL import Image

from scinoephile.audio.cantonese.models import (
    MergeTestCase,
    ProofTestCase,
    ShiftTestCase,
    SplitTestCase,
)
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


# region 粤文 Split Test Cases
mlamd_split_test_cases = [
    # region Block 0
    SplitTestCase(
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
    # endregion#
    # region Block 2
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
        one_zhongwen="旧中侨国货楼上的⋯",
        one_yuewen_start="",
        two_zhongwen="春田花花幼稚园？",
        two_yuewen_end="春田花花幼稚园呢",
        yuewen_to_split="旧中桥百货公司楼上𠮶间",
        one_yuewen_to_append="旧中桥百货公司楼上𠮶间",
        two_yuewen_to_prepend="",
    ),
    SplitTestCase(
        one_zhongwen="银城美食广场附近的⋯",
        one_yuewen_start="",
        two_zhongwen="春田花花幼稚园？",
        two_yuewen_end="春田花花幼稚园呀",
        yuewen_to_split="银城美食广场附近𠮶间",
        one_yuewen_to_append="银城美食广场附近𠮶间",
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
    # endregion
    # region Block 3 (WIP)
    SplitTestCase(
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
    SplitTestCase(
        one_zhongwen="荔芋火鸭礼！　　荔芋火鸭礼！",
        one_yuewen_start="",
        two_zhongwen="忘记校训九十七⋯　　忘记校训九十七⋯",
        two_yuewen_end="",
        yuewen_to_split="湾吉校坟交涉设",
        one_yuewen_to_append="湾吉校坟交涉设",
        two_yuewen_to_prepend="",
    ),
    SplitTestCase(
        one_zhongwen="也不能忘记校训九十八！",
        one_yuewen_start="",
        two_zhongwen="也不能忘记校训九十八！",
        two_yuewen_end="",
        yuewen_to_split="都唔好湾吉校坟交涉白",
        one_yuewen_to_append="都唔好湾吉校坟交涉白",
        two_yuewen_to_prepend="",
    ),
    SplitTestCase(
        one_zhongwen="好！各位同学⋯",
        one_yuewen_start="",
        two_zhongwen="今天的早会主要是跟大家分享",
        two_yuewen_end="",
        yuewen_to_split="𠮶个位同学",
        one_yuewen_to_append="𠮶个位同学",
        two_yuewen_to_prepend="",
    ),
    SplitTestCase(
        one_zhongwen="今天的早会主要是跟大家分享",
        one_yuewen_start="",
        two_zhongwen="一个重要主题：",
        two_yuewen_end="",
        yuewen_to_split="今次座会系要同大家分享一个可重要嘅主题",
        one_yuewen_to_append="今次座会系要同大家分享",
        two_yuewen_to_prepend="一个可重要嘅主题",
    ),
    # endregion
]
"""MLAMD 粤文 splitting test cases."""

# endregion

# region 粤文 Merge Test Cases

mlamd_merge_test_cases = [
    # region Block 0
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
    # endregion
    # region Block 1
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
    MergeTestCase(
        zhongwen="麦太想，这次走运了！",
        yuewen_to_merge=["麦太心谂", "今次冇死喇"],
        yuewen_merged="麦太心谂，今次冇死喇！",
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
    # endregion
    # region Block 2
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
    ),
    MergeTestCase(
        zhongwen="对！深水埗地铁站步行不用10分钟！",
        yuewen_to_merge=["系呀", "深水埗地铁站口行过去唔使十分钟呀"],
        yuewen_merged="系呀！深水埗地铁站口行过去唔使十分钟呀！",
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
    # endregion
    # region Block 3 (WIP)
    # endregion
]
"""MLAMD 粤文 merging test cases."""

# endregion

# region 粤文 Shift Test Cases
mlamd_shift_test_cases: list[ShiftTestCase] = [
    # region Block 0
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
    # endregion
    # region Block 1
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
    # endregion
    # region Block 2
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
    ),
    ShiftTestCase(
        one_zhongwen="西人教英文？",
        one_yuewen="咦西人教英文",
        two_zhongwen="是呀！",
        two_yuewen="",
        one_yuewen_shifted="咦西人教英文",
        two_yuewen_shifted="",
    ),
    ShiftTestCase(
        one_zhongwen="是呀！",
        one_yuewen="",
        two_zhongwen="春田花花，确有好多西人呀！",
        two_yuewen="系呀春田花花真系好多西人㗎",
        one_yuewen_shifted="系呀",
        two_yuewen_shifted="春田花花真系好多西人㗎",
    ),
    # endregion
    # region Block 3 (WIP)
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
    # endregion
]
"""MLAMD 粤文 shifting test cases."""

# endregion

# region 粤文 Proof Test Cases

mlamd_proof_test_cases = [
    # region Block 0
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
        yuewen_proofread="麦太认定呢个系异象",
        note="",
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
    # endregion
    # region Block 1
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
    # endregion
    # region Block 2
    ProofTestCase(
        zhongwen="麦太，没见面一阵",
        yuewen="咦，麦太，咩唔见你一排",
        yuewen_proofread="咦，麦太，咩唔见你一排",
        note="",
    ),
    ProofTestCase(
        zhongwen="怎么小腿粗起来了？",
        yuewen="个脚刮囊粗咗咁多呀？",
        yuewen_proofread="个脚瓜囊粗咗咁多呀？",
        note="Corrected '脚刮囊' to '脚瓜囊' as '脚瓜囊' is the correct Cantonese term for "
        "'calf', matching the meaning of '小腿'.",
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
    # endregion
    # region Block 3 (WIP)
    # endregion
]

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
    "mlamd_shift_test_cases",
    "mlamd_split_test_cases",
    "mlamd_proofread_test_cases",
]
