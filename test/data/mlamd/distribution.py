#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MLAMD."""

from __future__ import annotations

from scinoephile.audio.cantonese.distribution import DistributeTestCase

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
]  # distribute_test_cases_block_0
distribute_test_cases_block_1 = []  # distribute_test_cases_block_1
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
        one_zhongwen="西人教英文？",
        one_yuewen_start="咦",
        two_zhongwen="是呀！",
        two_yuewen_end="",
        yuewen_to_distribute="西人教英文",
        one_yuewen_to_append="西人教英文",
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
]  # distribute_test_cases_block_2
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
    DistributeTestCase(
        one_zhongwen="今天的早会主要是跟大家分享",
        one_yuewen_start="",
        two_zhongwen="一个重要主题：",
        two_yuewen_end="一个可重要嘅主题",
        yuewen_to_distribute="今次座会系要同大家分享",
        one_yuewen_to_append="今次座会系要同大家分享",
        two_yuewen_to_prepend="",
    ),
]  # distribute_test_cases_block_3
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
]  # distribute_test_cases_block_4
distribute_test_cases_block_5 = []  # distribute_test_cases_block_5
distribute_test_cases_block_6 = []  # distribute_test_cases_block_6
distribute_test_cases_block_7 = []  # distribute_test_cases_block_7
distribute_test_cases_block_8 = []  # distribute_test_cases_block_8
distribute_test_cases_block_9 = []  # distribute_test_cases_block_9
distribute_test_cases_block_10 = []  # distribute_test_cases_block_10
distribute_test_cases_block_11 = []  # distribute_test_cases_block_11
distribute_test_cases_block_12 = []  # distribute_test_cases_block_12
distribute_test_cases_block_13 = []  # distribute_test_cases_block_13
distribute_test_cases_block_14 = []  # distribute_test_cases_block_14
distribute_test_cases_block_15 = []  # distribute_test_cases_block_15
distribute_test_cases_block_16 = []  # distribute_test_cases_block_16
distribute_test_cases_block_17 = [
    DistributeTestCase(
        one_zhongwen="咦？",
        one_yuewen_start="",
        two_zhongwen="妈妈！",
        two_yuewen_end="妈妈",
        yuewen_to_distribute="咦",
        one_yuewen_to_append="咦",
        two_yuewen_to_prepend="",
    ),
]  # distribute_test_cases_block_17
distribute_test_cases_block_18 = []  # distribute_test_cases_block_18
distribute_test_cases_block_19 = []  # distribute_test_cases_block_19
distribute_test_cases_block_20 = [
    DistributeTestCase(
        one_zhongwen="马尔代夫！",
        one_yuewen_start="买二代夫",
        two_zhongwen="马尔代夫！",
        two_yuewen_end="",
        yuewen_to_distribute="买二代夫",
        one_yuewen_to_append="买二代夫",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="马尔代夫！",
        one_yuewen_start="",
        two_zhongwen="马尔代夫！",
        two_yuewen_end="买二代夫",
        yuewen_to_distribute="买二代夫",
        one_yuewen_to_append="",
        two_yuewen_to_prepend="买二代夫",
    ),
]  # distribute_test_cases_block_20
distribute_test_cases_block_21 = [
    DistributeTestCase(
        one_zhongwen="我喝一格，又喝一格，又喝一格⋯",
        one_yuewen_start="我饮下一格又一格",
        two_zhongwen="就给我喝光了！",
        two_yuewen_end="吓咪我饮晒㖞",
        yuewen_to_distribute="又一格",
        one_yuewen_to_append="又一格",
        two_yuewen_to_prepend="",
    ),
]  # distribute_test_cases_block_21
distribute_test_cases_block_22 = []  # distribute_test_cases_block_22
distribute_test_cases_block_23 = []  # distribute_test_cases_block_23
distribute_test_cases_block_24 = []  # distribute_test_cases_block_24
distribute_test_cases_block_25 = []  # distribute_test_cases_block_25
distribute_test_cases_block_26 = []  # distribute_test_cases_block_26
distribute_test_cases_block_27 = []  # distribute_test_cases_block_27
distribute_test_cases_block_28 = []  # distribute_test_cases_block_28
distribute_test_cases_block_29 = []  # distribute_test_cases_block_29
distribute_test_cases_block_30 = []  # distribute_test_cases_block_30
distribute_test_cases_block_31 = []  # distribute_test_cases_block_31
distribute_test_cases_block_32 = []  # distribute_test_cases_block_32
distribute_test_cases_block_33 = []  # distribute_test_cases_block_33
distribute_test_cases_block_34 = []  # distribute_test_cases_block_34
distribute_test_cases_block_35 = []  # distribute_test_cases_block_35
distribute_test_cases_block_36 = []  # distribute_test_cases_block_36
distribute_test_cases_block_37 = []  # distribute_test_cases_block_37
distribute_test_cases_block_38 = []  # distribute_test_cases_block_38
distribute_test_cases_block_39 = []  # distribute_test_cases_block_39
distribute_test_cases_block_40 = []  # distribute_test_cases_block_40
distribute_test_cases_block_41 = []  # distribute_test_cases_block_41
distribute_test_cases_block_42 = []  # distribute_test_cases_block_42
distribute_test_cases_block_43 = []  # distribute_test_cases_block_43
distribute_test_cases_block_44 = [
    DistributeTestCase(
        one_zhongwen="第二项绝技，就是⋯",
        one_yuewen_start="",
        two_zhongwen="抢包山！",
        two_yuewen_end="",
        yuewen_to_distribute="第二样绝技就系抢爆山",
        one_yuewen_to_append="第二样绝技就系",
        two_yuewen_to_prepend="抢爆山",
    ),
]  # distribute_test_cases_block_44
distribute_test_cases_block_45 = []  # distribute_test_cases_block_45
distribute_test_cases_block_46 = []  # distribute_test_cases_block_46
distribute_test_cases_block_47 = []  # distribute_test_cases_block_47
distribute_test_cases_block_48 = []  # distribute_test_cases_block_48
distribute_test_cases_block_49 = []  # distribute_test_cases_block_49
distribute_test_cases_block_50 = [
    DistributeTestCase(
        one_zhongwen="吃过几多苦头",
        one_yuewen_start="",
        two_zhongwen="才可以练成这举世无双的脚瓜？",
        two_yuewen_end="先至可以练成呢一只举细无伤嘅脚瓜",
        yuewen_to_distribute="挨过几多斧头",
        one_yuewen_to_append="挨过几多斧头",
        two_yuewen_to_prepend="",
    ),
]  # distribute_test_cases_block_50
distribute_test_cases_block_51 = []  # distribute_test_cases_block_51
distribute_test_cases_block_52 = []  # distribute_test_cases_block_52
distribute_test_cases_block_53 = []  # distribute_test_cases_block_53
distribute_test_cases_block_54 = []  # distribute_test_cases_block_54
distribute_test_cases_block_55 = []  # distribute_test_cases_block_55
distribute_test_cases_block_56 = []  # distribute_test_cases_block_56
distribute_test_cases_block_57 = []  # distribute_test_cases_block_57
distribute_test_cases_block_58 = []  # distribute_test_cases_block_58
distribute_test_cases_block_59 = []  # distribute_test_cases_block_59
distribute_test_cases_block_60 = [
    DistributeTestCase(
        one_zhongwen="亚运主办权⋯",
        one_yuewen_start="",
        two_zhongwen="亦由一个香港人从未听过的地方夺得",
        two_yuewen_end="亦都由一个香港人从未听过嘅地方夺得",
        yuewen_to_distribute="亚运主办权",
        one_yuewen_to_append="亚运主办权",
        two_yuewen_to_prepend="",
    ),
]  # distribute_test_cases_block_60
distribute_test_cases_block_61 = []  # distribute_test_cases_block_61
distribute_test_cases_block_62 = []  # distribute_test_cases_block_62
distribute_test_cases_block_63 = []  # distribute_test_cases_block_63
distribute_test_cases_block_64 = []  # distribute_test_cases_block_64
distribute_test_cases_block_65 = []  # distribute_test_cases_block_65
distribute_test_cases_block_66 = []  # distribute_test_cases_block_66
distribute_test_cases_block_67 = []  # distribute_test_cases_block_67
distribute_test_cases_block_68 = []  # distribute_test_cases_block_68
distribute_test_cases_block_69 = []  # distribute_test_cases_block_69
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
]  # distribute_test_cases_block_70
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
]  # distribute_test_cases_block_71
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
]  # distribute_test_cases_block_72

mlamd_distribute_test_cases: list[DistributeTestCase] = sum(
    (globals()[f"distribute_test_cases_block_{i}"] for i in range(73)), []
)
"""MLAMD 粤文 distribute test cases."""

__all__ = [
    "mlamd_distribute_test_cases",
]
