#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MLAMD."""

from __future__ import annotations

from scinoephile.audio.cantonese.proofing import ProofTestCase

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
        include_in_prompt=True,
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
        yuewen_proofread="哎，好在！噉大家可以返去上堂喇",
        note="",
    ),
]
proof_test_cases_block_4 = []
proof_test_cases_block_5 = []
proof_test_cases_block_6 = []
proof_test_cases_block_7 = []
proof_test_cases_block_8 = []
proof_test_cases_block_9 = []
proof_test_cases_block_10 = [
    ProofTestCase(
        zhongwen="好高兴这么快又跟大家见面",
        yuewen="好高兴咁快又同大家见面",
        yuewen_proofread="好高兴咁快又同大家见面",
        note="",
    ),
    ProofTestCase(
        zhongwen="接下来我会教大家整一味纸鸡包",
        yuewen="跟住落嚟我会教大家整一味纸鸡包",
        yuewen_proofread="跟住落嚟我会教大家整一味纸鸡包",
        note="",
    ),
    ProofTestCase(
        zhongwen="材料也很简单，只需要白纸一张",
        yuewen="材料都好简单，只需要白纸一张",
        yuewen_proofread="材料都好简单，只需要白纸一张",
        note="",
    ),
    ProofTestCase(
        zhongwen="只要把这纸这样子⋯",
        yuewen="我哋只需要张张纸咁样⋯",
        yuewen_proofread="我哋只需要张张纸咁样⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="一个纸鸡包就这样完成了",
        yuewen="一个纸鸡包就咁完成咗喇",
        yuewen_proofread="一个纸鸡包就咁完成咗喇",
        note="",
    ),
    ProofTestCase(
        zhongwen="各位小朋友，像鸡包不像呀？",
        yuewen="各位小朋友，你哋话似唔似鸡包啊？",
        yuewen_proofread="各位小朋友，你哋话似唔似鸡包啊？",
        note="",
    ),
]
proof_test_cases_block_11 = []
proof_test_cases_block_12 = []
proof_test_cases_block_13 = []
proof_test_cases_block_14 = []
proof_test_cases_block_15 = []
proof_test_cases_block_16 = []
proof_test_cases_block_17 = [
    ProofTestCase(
        zhongwen="衰仔，快点起床上学",
        yuewen="喂，衰仔啊，快啲起身返学喇",
        yuewen_proofread="喂，衰仔啊，快啲起身返学喇",
        note="",
    ),
    ProofTestCase(
        zhongwen="咦？",
        yuewen="咦？",
        yuewen_proofread="咦？",
        note="",
    ),
    ProofTestCase(
        zhongwen="妈妈！",
        yuewen="妈妈！",
        yuewen_proofread="妈妈！",
        note="",
    ),
]
proof_test_cases_block_18 = []
proof_test_cases_block_19 = []
proof_test_cases_block_20 = [
    ProofTestCase(  # REVIEW
        zhongwen="好呀，马尔代夫！",
        yuewen="嘻嘻，好嘢！",
        yuewen_proofread="嘻嘻，好嘢！",
        note="",
    ),
    ProofTestCase(  # REVIEW
        zhongwen="马尔代夫！",
        yuewen="买二代夫，买二代夫！",
        yuewen_proofread="马尔代夫，马尔代夫！",
        note="Corrected '买二代夫' to '马尔代夫' as it is a mishearing of the country name '马尔代夫' (Maldives).",
    ),
    ProofTestCase(
        zhongwen="马尔代夫！",
        yuewen="买二代夫！",
        yuewen_proofread="马尔代夫！",
        note="Corrected '买二代夫' to '马尔代夫' as it is a mishearing of the country name '马尔代夫' (Maldives).",
    ),
    ProofTestCase(
        zhongwen="妈妈，那么我们什么时候去？",
        yuewen="妈妈，咁我哋几时去呀？",
        yuewen_proofread="妈妈，咁我哋几时去呀？",
        note="",
    ),
    ProofTestCase(
        zhongwen="你先把药水喝掉，病好了我就去订机票",
        yuewen="嗯，你乖乖哋食埋啲药，好返晒啦我即刻订机票",
        yuewen_proofread="嗯，你乖乖哋食埋啲药，好返晒啦我即刻订机票",
        note="",
    ),
    ProofTestCase(
        zhongwen="来，多喝一点！",
        yuewen="嚟啦，食多更！",
        yuewen_proofread="嚟啦，食多更！",
        note="",
        include_in_prompt=True,
    ),
]
proof_test_cases_block_21 = [
    ProofTestCase(
        zhongwen="妈妈，你看！",
        yuewen="妈妈，你睇！",
        yuewen_proofread="妈妈，你睇！",
        note="",
    ),
    ProofTestCase(  # REVIEW
        zhongwen="妈妈你看，我病好了！",
        yuewen="我好返喇！",
        yuewen_proofread="我好返喇！",
        note="",
    ),
    ProofTestCase(
        zhongwen="我把药都吃光了",
        yuewen="啲嘢所以我全部食晒喇",
        yuewen_proofread="啲药所以我全部食晒喇",
        note="Corrected '啲嘢' to '啲药' as '药' is the correct word for 'medicine' in this context, matching the 中文.",
    ),
    ProofTestCase(
        zhongwen="家中的东西有什么没给你吃光的？",
        yuewen="即系间屋有乜嘢唔系畀你食晒㗎？",
        yuewen_proofread="即系间屋有乜嘢唔系畀你食晒㗎？",
        note="",
    ),
    ProofTestCase(
        zhongwen="这次不同呀，原来这么一大樽的",
        yuewen="妈妈，呢次唔同㗎，本来咁大樽嘅",
        yuewen_proofread="妈妈，呢次唔同㗎，本来咁大樽嘅",
        note="",
    ),
    ProofTestCase(
        zhongwen="我喝一格，又喝一格，又喝一格⋯",
        yuewen="我饮下一格，又一格，又一格⋯",
        yuewen_proofread="我饮一格，又一格，又一格⋯",
        note="Removed '下' from '饮下一格' as it is likely a mishearing; '饮一格' matches the meaning of '喝一格' in the 中文.",
    ),
    ProofTestCase(
        zhongwen="就给我喝光了！",
        yuewen="吓，咪我饮晒㖞！",
        yuewen_proofread="吓，咪我饮晒㖞！",
        note="",
    ),
]
proof_test_cases_block_22 = []
proof_test_cases_block_23 = []
proof_test_cases_block_24 = []
proof_test_cases_block_25 = []
proof_test_cases_block_26 = []
proof_test_cases_block_27 = []
proof_test_cases_block_28 = []
proof_test_cases_block_29 = []
proof_test_cases_block_30 = [
    ProofTestCase(
        zhongwen="但无论多不容易，我都要试一试",
        yuewen="但无论几唔容易，我都要试一试",
        yuewen_proofread="但无论几唔容易，我都要试一试",
        note="",
    ),
    ProofTestCase(
        zhongwen="我要黎根收我做徒弟！",
        yuewen="我要来紧收我度徒弟！",
        yuewen_proofread="我要黎根收我做徒弟！",
        note="Corrected '来紧' to '黎根' and '度徒弟' to '做徒弟' as both are likely mishearings; '黎根' is a name and '做徒弟' matches the meaning of '做徒弟' in the 中文.",
    ),
    ProofTestCase(
        zhongwen="无论几辛苦，我一定要得到奥运金牌！",
        yuewen="无论几辛苦，我一定要捞到奥运金牌！",
        yuewen_proofread="无论几辛苦，我一定要攞到奥运金牌！",
        note="Corrected '捞到' to '攞到' as '攞到' is the correct Cantonese verb for 'to get/obtain', matching the meaning of the 中文.",
    ),
]
proof_test_cases_block_31 = []
proof_test_cases_block_32 = [
    ProofTestCase(
        zhongwen="长洲，我终于来到长洲了！",
        yuewen="长洲，我终于嚟到长洲嘞！",
        yuewen_proofread="长洲，我终于嚟到长洲嘞！",
        note="",
    ),
]
proof_test_cases_block_33 = [
    ProofTestCase(
        zhongwen="长洲，我得亲吻这片圣洁的土地！",
        yuewen="长洲，我要亲吻呢片盛洁嘅土地！",
        yuewen_proofread="长洲，我要亲吻呢片圣洁嘅土地！",
        note="Corrected '盛洁' to '圣洁' as '圣洁' is the correct term for 'sacred' or 'holy', matching the meaning in the 中文.",
    ),
]
proof_test_cases_block_34 = [
    ProofTestCase(
        zhongwen="小朋友，这儿是南丫岛呀！",
        yuewen="小朋友呀，呢度系南丫岛噃！",
        yuewen_proofread="小朋友呀，呢度系南丫岛噃！",
        note="",
    ),
    ProofTestCase(
        zhongwen="南丫岛？它也孕育了周润发！",
        yuewen="南丫岛？都引用咗周润发噃！",
        yuewen_proofread="南丫岛？都孕育咗周润发噃！",
        note="Corrected '引用' to '孕育' as '孕育' is the correct term for 'nurtured' or 'gave rise to', matching the meaning in the 中文.",
    ),
]
proof_test_cases_block_35 = []
proof_test_cases_block_36 = []
proof_test_cases_block_37 = []
proof_test_cases_block_38 = []
proof_test_cases_block_39 = []
proof_test_cases_block_40 = []
proof_test_cases_block_41 = []
proof_test_cases_block_42 = []
proof_test_cases_block_43 = []
proof_test_cases_block_44 = [
    ProofTestCase(
        zhongwen="第二项绝技，就是⋯",
        yuewen="第二样绝技，就系⋯",
        yuewen_proofread="第二样绝技，就系⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="抢包山！",
        yuewen="抢爆山！",
        yuewen_proofread="抢包山！",
        note="Corrected '抢爆山' to '抢包山' as '抢包山' is the correct term for the traditional event, and '爆' is a likely mishearing of '包'.",
    ),
]
proof_test_cases_block_45 = []
proof_test_cases_block_46 = []
proof_test_cases_block_47 = []
proof_test_cases_block_48 = []
proof_test_cases_block_49 = [
    ProofTestCase(
        zhongwen="其实鸡尾包呢⋯",
        yuewen="其实鸡尾爆呢⋯",
        yuewen_proofread="其实鸡尾包呢⋯",
        note="Corrected '鸡尾爆' to '鸡尾包' as '鸡尾包' is the correct term for the pastry, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="你说这似不似鸡尾？",
        yuewen="吓，你话噉样似唔似鸡尾呀？哈哈哈哈",
        yuewen_proofread="吓，你话噉样似唔似鸡尾呀？哈哈哈哈",
        note="",
    ),
]
proof_test_cases_block_50 = []
proof_test_cases_block_51 = []
proof_test_cases_block_52 = [
    ProofTestCase(
        zhongwen="我找来找去也找不到那部电子英文辞典",
        yuewen="我揾完成间屋都揾唔到部电子英文词典",
        yuewen_proofread="我揾完成间屋都揾唔到部电子英文词典",
        note="",
    ),
    ProofTestCase(
        zhongwen="跑哪去了？",
        yuewen="去咗边呢？",
        yuewen_proofread="去咗边呢？",
        note="",
    ),
    ProofTestCase(
        zhongwen="难道⋯不会吧？",
        yuewen="唔通⋯冇理由㗎？",
        yuewen_proofread="唔通⋯冇理由㗎？",
        note="",
    ),
]
proof_test_cases_block_53 = []
proof_test_cases_block_54 = []
proof_test_cases_block_55 = []
proof_test_cases_block_56 = []
proof_test_cases_block_57 = []
proof_test_cases_block_58 = []
proof_test_cases_block_59 = []
proof_test_cases_block_60 = [
    ProofTestCase(
        zhongwen="最后⋯",
        yuewen="最后⋯",
        yuewen_proofread="最后⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="最后，一切成烟",
        yuewen="最后，全部都系banana",
        yuewen_proofread="",
        note="Cleared as '全部都系banana' bears no resemblance to the original phrase '最后，一切成烟' and is clearly a complete transcription failure.",
    ),
    ProofTestCase(
        zhongwen="最后，他们选了「掷蛋挞」做推介项目",
        yuewen="最后佢哋选咗定蛋挞做推介项目",
        yuewen_proofread="最后佢哋选咗掷蛋挞做推介项目",
        note="Corrected '定蛋挞' to '掷蛋挞' as '掷蛋挞' matches the activity described in the 中文, and '定' is likely a mishearing of '掷'.",
    ),
    ProofTestCase(
        zhongwen="至于香港争取申办亚运的口号⋯",
        yuewen="至于香港争取申办亚运嘅口号⋯",
        yuewen_proofread="至于香港争取申办亚运嘅口号⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="亦顺理成章叫成「香港一蛋挞」",
        yuewen="亦都顺理成章噉叫做「香港一蛋挞」",
        yuewen_proofread="亦都顺理成章噉叫做「香港一蛋挞」",
        note="",
    ),
    ProofTestCase(
        zhongwen="之后李丽珊蝉联失败⋯",
        yuewen="之后李利山丧乱失败⋯",
        yuewen_proofread="之后李丽珊蝉联失败⋯",
        note="Corrected '李利山' to '李丽珊' as it is a mishearing of the name, and '丧乱' to '蝉联' as '蝉联' is the correct term for defending a title, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="亚运主办权⋯",
        yuewen="亚运主办权⋯",
        yuewen_proofread="亚运主办权⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="亦由一个香港人从未听过的地方夺得",
        yuewen="亦都由一个香港人从未听过嘅地方夺得",
        yuewen_proofread="亦都由一个香港人从未听过嘅地方夺得",
        note="",
    ),
    ProofTestCase(
        zhongwen="想着转行当运动员的茶餐厅伙记⋯",
        yuewen="谂住可以转行做运动员嘅茶餐厅伙计⋯",
        yuewen_proofread="谂住可以转行做运动员嘅茶餐厅伙计⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="都回到茶餐厅继续掷他们的蛋挞",
        yuewen="都返返去茶餐厅继续钉佢哋嘅蛋挞",
        yuewen_proofread="都返返去茶餐厅继续掷佢哋嘅蛋挞",
        note="Corrected '钉' to '掷' as '掷' (to throw) matches the meaning in the 中文, while '钉' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="一切回复正常",
        yuewen="一切回复正常",
        yuewen_proofread="一切回复正常",
        note="",
    ),
]
proof_test_cases_block_61 = []
proof_test_cases_block_62 = []
proof_test_cases_block_63 = [
    ProofTestCase(
        zhongwen="因为环保⋯",
        yuewen="因为环保⋯",
        yuewen_proofread="因为环保⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="长洲的抢包都转为塑胶",
        yuewen="长洲嘅厂包经已转咗用塑胶",
        yuewen_proofread="长洲嘅抢包经已转咗用塑胶",
        note="Corrected '厂包' to '抢包' as '抢包' is the correct term for the bun-snatching event, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="师傅说，那阵胶气，相当臭",
        yuewen="师傅话，𠮶阵胶气，都几丑下",
        yuewen_proofread="师傅话，𠮶阵胶气，都几臭下",
        note="Corrected '丑' to '臭' as '臭' (smelly) matches the meaning of '相当臭' in the 中文, while '丑' (ugly) is likely a mishearing.",
    ),
]
proof_test_cases_block_64 = []
proof_test_cases_block_65 = [
    ProofTestCase(
        zhongwen="「⋯无力挽！」",
        yuewen="「⋯无泪弯！」",
        yuewen_proofread="「⋯无力挽！」",
        note="Corrected '无泪弯' to '无力挽' as it is a clear mishearing; '无力挽' matches the intended meaning of '无力挽' in the 中文.",
    ),
]
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
        include_in_prompt=True,
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
        include_in_prompt=True,
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
"""MLAMD 粤文 proof test cases."""

__all__ = [
    "mlamd_proof_test_cases",
]
