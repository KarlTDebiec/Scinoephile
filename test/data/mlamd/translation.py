#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MLAMD."""

from __future__ import annotations

from scinoephile.audio.cantonese.alignment.models import get_translate_test_case_model
from scinoephile.core.abcs import TestCase

translate_test_case_block_3 = get_translate_test_case_model(
    23,
    (0, 1, 2, 3, 12, 13, 14, 15, 16),
)(
    zhongwen_1="〝鹅满是快烙滴好耳痛⋯〞",
    zhongwen_2="〝鹅闷天天一戏个窗！〞",
    zhongwen_3="〝鹅们在壳习，鹅闷载升胀⋯〞",
    zhongwen_4="〝鹅闷是春天滴化！〞",
    zhongwen_5="这个猪样白兔小朋友⋯",
    yuewen_5="呢个扮紧白兔猪样嘅小朋友⋯",
    zhongwen_6="横看竖看也不像发哥伟仔的一个⋯",
    yuewen_6="即系横睇掂睇都唔似发哥或者伟仔𠮶个呢⋯",
    zhongwen_7="就是我，麦兜",
    yuewen_7="就系我，麦兜",
    zhongwen_8="这是我就读的幼稚园",
    yuewen_8="呢间就系我读嘅幼稚园",
    zhongwen_9="校长是潮州人",
    yuewen_9="校长系潮州人",
    zhongwen_10="可能是潮州口音的关系",
    yuewen_10="可能仲系讲紧潮州话嘅",
    zhongwen_11="这么多年来⋯",
    yuewen_11="所以咁多年嚟⋯",
    zhongwen_12="我其实不大明白他的说话",
    yuewen_12="我其实唔系好知佢噏乜",
    zhongwen_13="蛋挞！　　蛋挞！",
    zhongwen_14="荔芋火鸭礼！　　荔芋火鸭礼！",
    zhongwen_15="忘记校训九十七⋯　　忘记校训九十七⋯",
    zhongwen_16="也不能忘记校训九十八！",
    zhongwen_17="也不能忘记校训九十八！",
    zhongwen_18="好！各位同学⋯",
    yuewen_18="𠮶个位同学⋯",
    zhongwen_19="今天的早会主要是跟大家分享",
    yuewen_19="今次早会系要同大家分享",
    zhongwen_20="一个重要主题：",
    yuewen_20="一个可重要嘅主题：",
    zhongwen_21="小朋友，这个月你们交过学费没有？",
    yuewen_21="小朋友，你哋今个月交咗学费咩呀？",
    zhongwen_22="交过了！",
    yuewen_22="交！",
    zhongwen_23="太好了！大家去上堂吧",
    yuewen_23="哎，好在！噉大家可以返去上堂喇",
    yuewen_1="〝鹅满系快烙嗰阵好耳痛⋯〞",
    yuewen_2="〝鹅闷日日都要玩下个窗！〞",
    yuewen_3="〝鹅哋喺壳度练习，鹅闷就升胀⋯〞",
    yuewen_4="〝鹅闷就系春天嘅化身！〞",
    yuewen_13="蛋挞！　　蛋挞！",
    yuewen_14="荔芋火鸭礼！　　荔芋火鸭礼！",
    yuewen_15="唔好忘记校训九十七⋯　　唔好忘记校训九十七⋯",
    yuewen_16="都唔可以忘记校训九十八！",
    yuewen_17="都唔可以忘记校训九十八！",
)


mlamd_translate_test_cases: list[TestCase] = [
    translate_test_case_block_3,
]
"""MLAMD 粤文 translation test cases."""

__all__ = [
    "mlamd_translate_test_cases",
]
