#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Zhongwen proof test cases."""

from __future__ import annotations

from scinoephile.core.zhongwen.proofing.abcs import ZhongwenProofTestCase

# noinspection PyArgumentList
test_case_block_0 = ZhongwenProofTestCase.get_test_case_cls(33)(
    zimu_1="在麦太即将临盆的时候",
    zimu_2="一只胶兜在九龙上空飞过",
    zimu_3="沿荔枝角道直出大角咀道",
    zimu_4="经好彩酒家左转花园街乐园牛丸王",
    zimu_5="更正一下：",
    zimu_6="先到街市大楼妹记鱼腩粥外边",
    zimu_7="转呀，转…再更正一下",
    zimu_8="直出亚皆老街跨过火车桥右转太平道",
    zimu_9="再右拐窝打老道向女人街方向飞…",
    zimu_10="飞呀 飞.",
    zimu_11="胶兜最后飞进广华医院候产房",
    zimu_12="也就是在麦太右边额角上",
    zimu_13="更正：左边额角上",
    zimu_14="转呀 转·",
    zimu_15="麦太认定这是异像",
    zimu_16="于是向额角上的胶兜许愿",
    zimu_17="脑海中同时出现即将诞生的儿子容貌…",
    zimu_18="希望他好聪明，读书好叻！",
    zimu_19="胶兜对麦太的愿望似乎没有反应",
    zimu_20="于是她向胶兜补充说：",
    zimu_21="或者读书唔叻，工作叻呢？",
    zimu_22="又或者…",
    zimu_23="又或者好靓仔，好靓仔",
    zimu_24="跟周润发，梁朝伟那么靓仔！",
    zimu_25="胶兜仍然在转，毫无点头迹象",
    zimu_26="麦太一时心虚",
    zimu_27="赶忙趁胶兜落地前另许一个愿望：",
    zimu_28="唔聪明唔靓仔也算了，只要福星高照",
    zimu_29="一世够运，逢凶化吉！",
    zimu_30="靠自己能力解决事情当然最好",
    zimu_31="不过运气还是很重要的",
    zimu_32="虽是说像梁朝伟周润发也行运定了",
    zimu_33="但总得要叻仔呀 F!",
    xiugai_4="经好彩酒家左转花园街乐园牛丸王…",
    beizhu_4="添加 OCR 遗漏的省略号。",
    xiugai_7="转呀，转…再更正一下：",
    beizhu_7="添加 OCR 遗漏的冒号。",
    xiugai_10="飞呀，飞…",
    beizhu_10="添加 OCR 遗漏的逗号；将句号更正为省略号。",
    xiugai_12="也就是在麦太右边额角上…",
    beizhu_12="添加 OCR 遗漏的省略号。",
    xiugai_13="更正：左边额角上…",
    beizhu_13="添加 OCR 遗漏的省略号。",
    xiugai_14="转呀，转…",
    beizhu_14="添加 OCR 遗漏的逗号；将点更正为省略号。",
    xiugai_33="但总得要叻仔呀！",
    beizhu_33="将 OCR 误识的 'F' 更正为感叹号。",
    difficulty=3,
    verified=True,
)  # test_case_block_0
# noinspection PyArgumentList
test_case_block_1 = ZhongwenProofTestCase.get_test_case_cls(13)(
    zimu_1="最后，胶兜 嘀督」一声落地",
    zimu_2="嘀督？嘀督，就是答应了",
    zimu_3="麦太想，这次走运了！",
    zimu_4="可是答应了些什么呢？",
    zimu_5="叻仔？好运？",
    zimu_6="还是似周润发 ？",
    zimu_7="为了纪念这赐福的胶兜",
    zimu_8="麦太决定把儿子命名麦胶",
    zimu_9="不行，月 胶胶声，多难听！",
    zimu_10="还是唤他麦兜！",
    zimu_11="各位",
    zimu_12="我就是险些给定名麦胶的小朋友…",
    zimu_13="麦兜！",
    xiugai_1="最后，胶兜「嘀督」一声落地",
    beizhu_1="添加了缺失的左书名号。",
    xiugai_6="还是似周润发？",
    beizhu_6="删除问号前的空格。",
    xiugai_9="不行，胶胶声，多难听！",
    beizhu_9="删除了OCR错误添加的‘月’字。",
    xiugai_11="各位…",
    beizhu_11="添加 OCR 遗漏的省略号。",
    difficulty=3,
    verified=True,
)  # test_case_block_1
# noinspection PyArgumentList
test_case_block_2 = ZhongwenProofTestCase.get_test_case_cls(16)(
    zimu_1="麦太，没见面一阵",
    zimu_2="怎么小腿粗起来了？",
    zimu_3="可怜呀，每天扑来扑去",
    zimu_4="替儿子找幼稚园！",
    zimu_5="怎么不试一试好彩酒楼对面",
    zimu_6="旧中侨国货楼上的…",
    zimu_7="春田花花幼稚园",
    zimu_8="就是座落界限街南昌街交界.",
    zimu_9="银城美食广场附近的",
    zimu_10="春田花花幼稚园",
    zimu_11="对！深水埗地铁站步行不用10分钟！",
    zimu_12="春田花花幼稚园，师资优良",
    zimu_13="而且还有西人教英文！",
    zimu_14="西人教英文？",
    zimu_15="是呀！",
    zimu_16="春田花花，确有好多西人呀！",
    xiugai_3="可怜呀，每天扑来扑去…",
    beizhu_3="添加 OCR 遗漏的省略号。",
    xiugai_7="春田花花幼稚园？",
    beizhu_7="添加 OCR 遗漏的问号。",
    xiugai_8="就是座落界限街南昌街交界…",
    beizhu_8="将句号更正为省略号。",
    xiugai_9="银城美食广场附近的…",
    beizhu_9="添加 OCR 遗漏的省略号。",
    xiugai_10="春田花花幼稚园？",
    beizhu_10="添加 OCR 遗漏的问号。",
    xiugai_12="春田花花幼稚园，师资优良…",
    beizhu_12="添加 OCR 遗漏的省略号。",
    difficulty=3,
    verified=True,
)  # test_case_block_2
# noinspection PyArgumentList
test_case_block_3 = ZhongwenProofTestCase.get_test_case_cls(23)(
    zimu_1='鹅满是快烙滴好耳痛"',
    zimu_2="鹅闷天天一戏个窗！",
    zimu_3="鹅们在壳习，鹅闷载升胀 II",
    zimu_4="鹅闷是春天滴化！",
    zimu_5="这个猪样白兔小朋友…",
    zimu_6="横看竖看也不像发哥伟仔的一个",
    zimu_7="就是我，麦兜",
    zimu_8="这是我就读的幼稚园",
    zimu_9="校长是潮州人",
    zimu_10="可能是潮州口音的关系",
    zimu_11="这么多年来",
    zimu_12="我其实不大明白他的说话",
    zimu_13="蛋挞！ 蛋挞！",
    zimu_14="荔芋火鸭札！ 荔芋火鸭札！",
    zimu_15="忘记校训九十七 忘记校训九十七",
    zimu_16="也不能忘记校训九十八！",
    zimu_17="也不能忘记校训九十八！",
    zimu_18="好！各位同学…",
    zimu_19="今天的早会主要是跟大家分享",
    zimu_20="一个重要主题 页：",
    zimu_21="小朋友，这个月你们交过学费没有？",
    zimu_22="交过了！",
    zimu_23="太好了！大家去上堂吧",
    xiugai_1="〝鹅满是快烙滴好耳痛…〞",
    beizhu_1="已更正引号。",
    xiugai_2="〝鹅闷天天一戏个窗！〞",
    beizhu_2="添加了缺失的引号。",
    xiugai_3="〝鹅们在壳习，鹅闷载升胀…〞",
    beizhu_3="添加了缺失的引号；将‘II’更正为省略号。",
    xiugai_4="〝鹅闷是春天滴化！〞",
    beizhu_4="添加了缺失的引号。",
    xiugai_6="横看竖看也不像发哥伟仔的一个…",
    beizhu_6="添加 OCR 遗漏的省略号。",
    xiugai_11="这么多年来…",
    beizhu_11="添加 OCR 遗漏的省略号。",
    xiugai_13="蛋挞！　　蛋挞！",
    beizhu_13="已修正间距。",
    xiugai_14="荔芋火鸭礼！　　荔芋火鸭礼！",
    beizhu_14="将 OCR 误识的‘札’更正为‘礼’；已修正间距。",
    xiugai_15="忘记校训九十七…　　忘记校训九十七…",
    beizhu_15="添加 OCR 遗漏的省略号和间距。",
    xiugai_20="一个重要主题：",
    beizhu_20="已删除字符“页”。",
    difficulty=3,
    verified=True,
)  # test_case_block_3
# noinspection PyArgumentList
test_case_block_4 = ZhongwenProofTestCase.get_test_case_cls(55)(
    zimu_1="你们可能觉得这间幼稚园很烂",
    zimu_2="可是， 对我和我一班同学",
    zimu_3="这儿是我们最快乐，最美丽的乐园…",
    zimu_4="·还有一个很疼我们",
    zimu_5="就是有点游魂的Mi ss Chan",
    zimu_6="她的志愿是做第二个王菲",
    zimu_7="做第二个陈慧琳也可以",
    zimu_8="我们现在开始点名",
    zimu_9="麦唛同学！ 到！",
    zimu_10="亚辉同学！ 到！",
    zimu_11="菇时同学！ 到！",
    zimu_12="得巴同学！ 到！",
    zimu_13="阿May同学！ 到！",
    zimu_14="阿June同学！ 到！",
    zimu_15="阿May同学！ 到！",
    zimu_16="麦唛同学！ 到！",
    zimu_17="阿May同学！",
    zimu_18="Miss Chan' 我点过两次了！",
    zimu_19="呀，真的吗？",
    zimu_20="校长早晨！",
    zimu_21="校长再见！",
    zimu_22="我们现在继续点名",
    zimu_23="阿June同学！ 到！",
    zimu_24="亚辉同学！ 到！",
    zimu_25="得巴同学！ 到！",
    zimu_26="阿May同学！ 到！",
    zimu_27="麦唛同学！ 到！",
    zimu_28="菇时同学！ 到！",
    zimu_29="菇时同学！ 到！",
    zimu_30="还有谁没点过吗？",
    zimu_31="麦兜！",
    zimu_32="麦兜同学！",
    zimu_33="麦兜同学！",
    zimu_34="麦兜同学！",
    zimu_35="麦唛呀 即是呢…",
    zimu_36="我好像觉得呢",
    zimu_37="有什么人在喊我似的",
    zimu_38="你们不要以为我心散",
    zimu_39="其实我正在思考一个学术问题：",
    zimu_40="橙，为什么会是 「疴-烂-煮」 呢？",
    zimu_41="妈妈说吃橙可通大便",
    zimu_42="「疴」 这个我明白，可是 「烂-煮」 呢？",
    zimu_43="还有这个 芭-娜-哪 香蕉",
    zimu_44="为什么雨伞又会是 「暗-芭-娜-哪 - 呢？",
    zimu_45="我 「暗」的「暗」掉一条蕉",
    zimu_46="至多是疴烂煮，怎么会下起雨来呢",
    zimu_47="这世界还有很多事情我弄不明白",
    zimu_48="但我不害怕",
    zimu_49="我想，有天我念完幼稚园",
    zimu_50="升小学 上中学",
    zimu_51="再念大学…",
    zimu_52="当我大学毕业的时候",
    zimu_53="我知道我会明白一切！",
    zimu_54="那时候…",
    zimu_55="我买所房子给妈妈！",
    xiugai_4="还有一个很疼我们的",
    beizhu_4="补全“的”字，原文漏字。",
    xiugai_5="就是有点游魂的Miss Chan",
    beizhu_5="将“Mi ss”改为“Miss”，原文识别错误。",
    xiugai_11="菇时同学！到！",
    beizhu_11="去除“！”与“到！”之间的空格，原文多余空格。",
    xiugai_12="得巴同学！到！",
    beizhu_12="去除“！”与“到！”之间的空格，原文多余空格。",
    xiugai_13="阿May同学！到！",
    beizhu_13="去除“！”与“到！”之间的空格，原文多余空格。",
    xiugai_14="阿June同学！到！",
    beizhu_14="去除“！”与“到！”之间的空格，原文多余空格。",
    xiugai_15="阿May同学！到！",
    beizhu_15="去除“！”与“到！”之间的空格，原文多余空格。",
    xiugai_16="麦唛同学！到！",
    beizhu_16="去除“！”与“到！”之间的空格，原文多余空格。",
    xiugai_18="Miss Chan，我点过两次了！",
    beizhu_18="将“Miss Chan' 我点过两次了！”改为“Miss Chan，我点过两次了！”，原文标点识别错误。",
    xiugai_23="阿June同学！到！",
    beizhu_23="去除“！”与“到！”之间的空格，原文多余空格。",
    xiugai_24="亚辉同学！到！",
    beizhu_24="去除“！”与“到！”之间的空格，原文多余空格。",
    xiugai_25="得巴同学！到！",
    beizhu_25="去除“！”与“到！”之间的空格，原文多余空格。",
    xiugai_26="阿May同学！到！",
    beizhu_26="去除“！”与“到！”之间的空格，原文多余空格。",
    xiugai_27="麦唛同学！到！",
    beizhu_27="去除“！”与“到！”之间的空格，原文多余空格。",
    xiugai_28="菇时同学！到！",
    beizhu_28="去除“！”与“到！”之间的空格，原文多余空格。",
    xiugai_29="菇时同学！到！",
    beizhu_29="去除“！”与“到！”之间的空格，原文多余空格。",
    xiugai_40="橙，为什么会是「疴-烂-煮」呢？",
    beizhu_40="将“ 「疴-烂-煮」 呢？”中的空格去除，保持一致性。",
    xiugai_42="「疴」这个我明白，可是「烂-煮」呢？",
    beizhu_42="去除“「疴」 这个我明白，可是 「烂-煮」 呢？”中的多余空格。",
    xiugai_44="为什么雨伞又会是「暗-芭-娜-哪」呢？",
    beizhu_44="去除“ 「暗-芭-娜-哪 - 呢？”中的多余空格和破折号。",
    xiugai_45="我「暗」的「暗」掉一条蕉",
    beizhu_45="去除多余空格。",
    difficulty=1,
)  # test_case_block_4
# noinspection PyArgumentList
test_case_block_5 = None  # test_case_block_5
# noinspection PyArgumentList
test_case_block_6 = None  # test_case_block_6
# noinspection PyArgumentList
test_case_block_7 = None  # test_case_block_7
# noinspection PyArgumentList
test_case_block_8 = None  # test_case_block_8
# noinspection PyArgumentList
test_case_block_9 = None  # test_case_block_9
# noinspection PyArgumentList
test_case_block_10 = None  # test_case_block_10
# noinspection PyArgumentList
test_case_block_11 = None  # test_case_block_11
# noinspection PyArgumentList
test_case_block_12 = None  # test_case_block_12
# noinspection PyArgumentList
test_case_block_13 = None  # test_case_block_13
# noinspection PyArgumentList
test_case_block_14 = None  # test_case_block_14
# noinspection PyArgumentList
test_case_block_15 = None  # test_case_block_15
# noinspection PyArgumentList
test_case_block_16 = None  # test_case_block_16
# noinspection PyArgumentList
test_case_block_17 = None  # test_case_block_17
# noinspection PyArgumentList
test_case_block_18 = None  # test_case_block_18
# noinspection PyArgumentList
test_case_block_19 = None  # test_case_block_19
# noinspection PyArgumentList
test_case_block_20 = None  # test_case_block_20
# noinspection PyArgumentList
test_case_block_21 = None  # test_case_block_21
# noinspection PyArgumentList
test_case_block_22 = None  # test_case_block_22
# noinspection PyArgumentList
test_case_block_23 = None  # test_case_block_23
# noinspection PyArgumentList
test_case_block_24 = None  # test_case_block_24
# noinspection PyArgumentList
test_case_block_25 = None  # test_case_block_25
# noinspection PyArgumentList
test_case_block_26 = None  # test_case_block_26
# noinspection PyArgumentList
test_case_block_27 = None  # test_case_block_27
# noinspection PyArgumentList
test_case_block_28 = None  # test_case_block_28
# noinspection PyArgumentList
test_case_block_29 = None  # test_case_block_29
# noinspection PyArgumentList
test_case_block_30 = None  # test_case_block_30
# noinspection PyArgumentList
test_case_block_31 = None  # test_case_block_31
# noinspection PyArgumentList
test_case_block_32 = None  # test_case_block_32
# noinspection PyArgumentList
test_case_block_33 = None  # test_case_block_33
# noinspection PyArgumentList
test_case_block_34 = None  # test_case_block_34
# noinspection PyArgumentList
test_case_block_35 = None  # test_case_block_35
# noinspection PyArgumentList
test_case_block_36 = None  # test_case_block_36
# noinspection PyArgumentList
test_case_block_37 = None  # test_case_block_37
# noinspection PyArgumentList
test_case_block_38 = None  # test_case_block_38
# noinspection PyArgumentList
test_case_block_39 = None  # test_case_block_39
# noinspection PyArgumentList
test_case_block_40 = None  # test_case_block_40
# noinspection PyArgumentList
test_case_block_41 = None  # test_case_block_41
# noinspection PyArgumentList
test_case_block_42 = None  # test_case_block_42
# noinspection PyArgumentList
test_case_block_43 = None  # test_case_block_43
# noinspection PyArgumentList
test_case_block_44 = None  # test_case_block_44
# noinspection PyArgumentList
test_case_block_45 = None  # test_case_block_45
# noinspection PyArgumentList
test_case_block_46 = None  # test_case_block_46
# noinspection PyArgumentList
test_case_block_47 = None  # test_case_block_47
# noinspection PyArgumentList
test_case_block_48 = None  # test_case_block_48
# noinspection PyArgumentList
test_case_block_49 = None  # test_case_block_49
# noinspection PyArgumentList
test_case_block_50 = None  # test_case_block_50
# noinspection PyArgumentList
test_case_block_51 = None  # test_case_block_51
# noinspection PyArgumentList
test_case_block_52 = None  # test_case_block_52
# noinspection PyArgumentList
test_case_block_53 = None  # test_case_block_53
# noinspection PyArgumentList
test_case_block_54 = None  # test_case_block_54
# noinspection PyArgumentList
test_case_block_55 = None  # test_case_block_55
# noinspection PyArgumentList
test_case_block_56 = None  # test_case_block_56
# noinspection PyArgumentList
test_case_block_57 = None  # test_case_block_57
# noinspection PyArgumentList
test_case_block_58 = None  # test_case_block_58
# noinspection PyArgumentList
test_case_block_59 = None  # test_case_block_59
# noinspection PyArgumentList
test_case_block_60 = None  # test_case_block_60
# noinspection PyArgumentList
test_case_block_61 = None  # test_case_block_61
# noinspection PyArgumentList
test_case_block_62 = None  # test_case_block_62
# noinspection PyArgumentList
test_case_block_63 = None  # test_case_block_63
# noinspection PyArgumentList
test_case_block_64 = None  # test_case_block_64
# noinspection PyArgumentList
test_case_block_65 = None  # test_case_block_65
# noinspection PyArgumentList
test_case_block_66 = None  # test_case_block_66
# noinspection PyArgumentList
test_case_block_67 = None  # test_case_block_67
# noinspection PyArgumentList
test_case_block_68 = None  # test_case_block_68
# noinspection PyArgumentList
test_case_block_69 = None  # test_case_block_69
# noinspection PyArgumentList
test_case_block_70 = None  # test_case_block_70
# noinspection PyArgumentList
test_case_block_71 = None  # test_case_block_71
# noinspection PyArgumentList
test_case_block_72 = None  # test_case_block_72


zhongwen_proof_test_cases: list[ZhongwenProofTestCase] = [
    test_case
    for name, test_case in globals().items()
    if name.startswith("test_case_block_") and test_case is not None
]
"""中文 proof test cases."""

__all__ = [
    "zhongwen_proof_test_cases",
]
