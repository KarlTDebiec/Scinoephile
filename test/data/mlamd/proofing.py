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
        note="Corrected '荔枝角度' to '荔枝角道' and '大角咀度' to '大角咀道' as '道' is "
        "the correct word for 'road' in both cases.",
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="经好彩酒家左转花园街乐园牛丸王⋯",
        yuewen="经过好彩走家再左转返出花园街乐园牛园望对上⋯",
        yuewen_proofread="经过好彩酒家再左转返出花园街乐园牛丸王对上⋯",
        note="Corrected '走家' to '酒家', '牛园望' to '牛丸王' as these are likely "
        "mishearings of the correct place names in the context.",
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
        note="Corrected '阿街路街' to '亚皆老街' as it is a mishearing of the "
        "street name '亚皆老街'.",
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="再右拐窝打老道向女人街方向飞⋯",
        yuewen="再右转抹返出去窝打炉道向女人街方向飞下下⋯",
        yuewen_proofread="再右转抹返出去窝打老道向女人街方向飞下下⋯",
        note="Corrected '窝打炉道' to '窝打老道' as '窝打老道' is the correct street "
        "name, matching the 中文.",
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
        note="Corrected '后产房' to '候产房' as '候产房' (waiting room for "
        "childbirth) matches the meaning in the 中文, while '后产房' is "
        "likely a mishearing.",
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
        note="Corrected '云晶' to '魂精' as '魂精' is a valid Cantonese term for "
        "'temple' and matches the meaning of '额角' in the 中文.",
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
        note="Corrected '异象' to '异像' as '异像' is the correct term in this "
        "context.",
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="于是向额角上的胶兜许愿",
        yuewen="于是向云晶对上嘅胶兜许愿",
        yuewen_proofread="于是向魂精对上嘅胶兜许愿",
        note="Corrected '云晶' to '魂精' as '魂精' is a valid Cantonese term for "
        "'temple' (额角), matching the meaning in the 中文.",
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
        yuewen_proofread="胶兜依然系噉喺度转，好似一啲点头嘅迹象都冇",
        note="Corrected '应承嘅迹象' to '点头嘅迹象' as '点头' matches the meaning of "
        "'点头迹象' in the 中文, while '应承' is likely a mishearing.",
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
        note="Corrected '复星高照' to '福星高照' as '福星高照' is the correct idiom "
        "meaning 'blessed with good fortune', while '复星' is likely a "
        "mishearing.",
    ),
    ProofTestCase(
        zhongwen="一世够运，逢凶化吉！",
        yuewen="一世救运，乜嘢事都逢凶化㗎喇！",
        yuewen_proofread="一世够运，乜嘢事都逢凶化㗎喇！",
        note="Corrected '救运' to '够运' as '够运' is the correct term for being "
        "lucky, matching the original meaning.",
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
]  # proof_test_cases_block_0
proof_test_cases_block_1 = [
    ProofTestCase(
        zhongwen="最后，胶兜「嘀督」一声落地",
        yuewen="最后，胶兜「滴嘟」一声咁落地",
        yuewen_proofread="最后，胶兜「嘀督」一声咁落地",
        note="Corrected '滴嘟' to '嘀督' to match the intended sound and "
        "meaning of '嘀督' as a phonetic rendering of the sound effect "
        "in the 中文.",
    ),
    ProofTestCase(
        zhongwen="嘀督？嘀督，就是答应了",
        yuewen="滴嘟？滴嘟㖞，即系应承啦",
        yuewen_proofread="嘀督？嘀督㖞，即系应承啦",
        note="Corrected '滴嘟' to '嘀督' to match the intended sound and "
        "meaning of '嘀督' as a phonetic rendering of '嘀督' (答应了).",
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
        note="Corrected '自周人烦' to '似周润发' as it is a mishearing of the "
        "celebrity name '周润发'.",
    ),
    ProofTestCase(
        zhongwen="为了纪念这赐福的胶兜",
        yuewen="为咗纪念呢个赤幅嘅胶兜",
        yuewen_proofread="为咗纪念呢个赐福嘅胶兜",
        note="Corrected '赤幅' to '赐福' as '赐福' (bestowing blessing) matches "
        "the meaning in the 中文, while '赤幅' is a likely mishearing.",
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
]  # proof_test_cases_block_1
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
        note="Corrected '脚刮囊' to '脚瓜囊' as '脚瓜囊' is the correct Cantonese "
        "term for 'calf', matching the meaning of '小腿'.",
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
        note="Corrected '走楼' to '酒楼' as '酒楼' is the correct term for "
        "'restaurant' and matches the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="旧中侨国货楼上的⋯",
        yuewen="旧中桥百货公司楼上𠮶间⋯",
        yuewen_proofread="旧中侨百货公司楼上𠮶间⋯",
        note="Corrected '中桥' to '中侨' as '中侨' matches the original name in "
        "the 中文, and '中桥' is likely a mishearing.",
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
        note="Corrected '诗诗优良' to '师资优良' as '师资' (teaching staff) is the "
        "correct term, and '诗诗' is a likely mishearing.",
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
]  # proof_test_cases_block_2
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
        note="Corrected '位仔' to '伟仔' as '伟仔' is the correct nickname for "
        "梁朝伟, matching the meaning in the 中文.",
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
        note="Corrected '噏文' to '噏乜' as '噏乜' (what he's saying) matches "
        "the meaning of '他的说话', while '噏文' is likely a mishearing.",
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="蛋挞！　　蛋挞！",
        yuewen="大湖荒岩宅",
        yuewen_proofread="",
        note="Cleared as '大湖荒岩宅' bears no resemblance to the original "
        "phrase '蛋挞！　　蛋挞！' and is clearly a complete transcription "
        "failure.",
    ),
    ProofTestCase(
        zhongwen="荔芋火鸭礼！　　荔芋火鸭礼！",
        yuewen="湾吉校坟交涉设",
        yuewen_proofread="",
        note="Cleared as '湾吉校坟交涉设' bears no resemblance to the original "
        "phrase '荔芋火鸭礼！　　荔芋火鸭礼！' and is clearly a pure artifact.",
    ),
    ProofTestCase(
        zhongwen="也不能忘记校训九十八！",
        yuewen="都唔好湾吉校坟交涉白！",
        yuewen_proofread="",
        note="Cleared as '都唔好湾吉校坟交涉白！' bears no resemblance to the "
        "original phrase '也不能忘记校训九十八！' and is clearly a pure "
        "artifact.",
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
        note="Corrected '座会' to '早会' as '早会' is the correct term for "
        "'morning assembly', matching the meaning of the 中文.",
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
        yuewen="交！",
        yuewen_proofread="交！",
        note="",
    ),
    ProofTestCase(
        zhongwen="太好了！大家去上堂吧",
        yuewen="哎，好在！噉大家可以返去上堂喇",
        yuewen_proofread="哎，好在！噉大家可以返去上堂喇",
        note="",
    ),
]  # proof_test_cases_block_3
proof_test_cases_block_4 = [
    ProofTestCase(
        zhongwen="你们可能觉得这间幼稚园很烂",
        yuewen="你哋可能觉得呢间幼稚园好逗利",
        yuewen_proofread="你哋可能觉得呢间幼稚园好烂",
        note="Corrected '好逗利' to '好烂' as '逗利' is a mishearing of '烂', "
        "which matches the meaning of '很烂' in the 中文.",
    ),
    ProofTestCase(
        zhongwen="可是，对我和我一班同学",
        yuewen="但系，对于我同埋我班同学仔嚟讲",
        yuewen_proofread="但系，对于我同埋我班同学仔嚟讲",
        note="",
    ),
    ProofTestCase(
        zhongwen="这儿是我们最快乐，最美丽的乐园⋯",
        yuewen="呢度系我哋最快乐，最美丽嘅乐园⋯",
        yuewen_proofread="呢度系我哋最快乐，最美丽嘅乐园⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="⋯还有一个很疼我们",
        yuewen="仲有一个好疼我哋⋯",
        yuewen_proofread="仲有一个好疼我哋⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="就是有点游魂的Miss Chan",
        yuewen="不过就有少少失魂嘅班主有Miss Chan",
        yuewen_proofread="不过就有少少游魂嘅班主有Miss Chan",
        note="Corrected '失魂' to '游魂' as '游魂' matches the meaning of '游魂' "
        "in the 中文, while '失魂' is a similar-sounding but incorrect "
        "term in this context.",
    ),
    ProofTestCase(
        zhongwen="她的志愿是做第二个王菲",
        yuewen="佢嘅志愿系做下一个王妃",
        yuewen_proofread="佢嘅志愿系做下一个王菲",
        note="Corrected '王妃' to '王菲' as '王菲' is the correct name of the "
        "singer, matching the original meaning.",
    ),
    ProofTestCase(
        zhongwen="做第二个陈慧琳也可以",
        yuewen="或者系做下一个陈维林都得",
        yuewen_proofread="或者系做下一个陈慧琳都得",
        note="Corrected '陈维林' to '陈慧琳' as '陈慧琳' is the correct name "
        "matching the original meaning, while '陈维林' is a likely "
        "mishearing.",
    ),
    ProofTestCase(
        zhongwen="我们现在开始点名",
        yuewen="好喇，我哋而家开始点名",
        yuewen_proofread="好喇，我哋而家开始点名",
        note="",
    ),
    ProofTestCase(
        zhongwen="麦唛同学！　　到！",
        yuewen="麦麦同学！　　到！",
        yuewen_proofread="麦唛同学！　　到！",
        note="Corrected '麦麦' to '麦唛' as '麦唛' is the correct name, matching "
        "the original 中文.",
    ),
    ProofTestCase(
        zhongwen="亚辉同学！　　到！",
        yuewen="阿辉同学！到！",
        yuewen_proofread="阿辉同学！到！",
        note="",
    ),
    ProofTestCase(
        zhongwen="菇时同学！　　到！",
        yuewen="Boosie同学！　　到！",
        yuewen_proofread="菇时同学！　　到！",
        note="Corrected 'Boosie' to '菇时' as 'Boosie' is a mishearing of "
        "the name '菇时'.",
    ),
    ProofTestCase(
        zhongwen="得巴同学！　　到！",
        yuewen="德巴同学！到！",
        yuewen_proofread="德巴同学！到！",
        note="",
    ),
    ProofTestCase(
        zhongwen="阿May同学！　　到！",
        yuewen="阿May同学！到！",
        yuewen_proofread="阿May同学！到！",
        note="",
    ),
    ProofTestCase(
        zhongwen="阿June同学！　　到！",
        yuewen="阿June同学！到！",
        yuewen_proofread="阿June同学！到！",
        note="",
    ),
    ProofTestCase(
        zhongwen="阿May同学！",
        yuewen="阿May同学！",
        yuewen_proofread="阿May同学！",
        note="",
    ),
    ProofTestCase(
        zhongwen="Miss Chan，我点过两次了！",
        yuewen="Miss Chan，你点咗我两次喇！",
        yuewen_proofread="Miss Chan，你点咗我两次喇！",
        note="",
    ),
    ProofTestCase(
        zhongwen="呀，真的吗？",
        yuewen="啊，系咩？",
        yuewen_proofread="啊，系咩？",
        note="",
    ),
    ProofTestCase(
        zhongwen="我们现在继续点名",
        yuewen="好，我哋而家继续点名",
        yuewen_proofread="好，我哋而家继续点名",
        note="",
    ),
    ProofTestCase(
        zhongwen="菇时同学！　　到！",
        yuewen="川明同学！　　到！",
        yuewen_proofread="",
        note="Cleared as '川明同学！　　到！' bears no resemblance to the original "
        "phrase '菇时同学！　　到！' and is clearly a pure artifact.",
    ),
    ProofTestCase(
        zhongwen="还有谁没点过吗？",
        yuewen="好，仲有边个未点？",
        yuewen_proofread="好，仲有边个未点？",
        note="",
    ),
    ProofTestCase(
        zhongwen="麦兜！",
        yuewen="猫！噢！",
        yuewen_proofread="",
        note="Cleared as '猫！噢！' bears no resemblance to the original "
        "phrase '麦兜！' and is clearly a complete transcription "
        "failure.",
    ),
    ProofTestCase(
        zhongwen="麦兜同学！",
        yuewen="麦兜同学！",
        yuewen_proofread="麦兜同学！",
        note="",
    ),
    ProofTestCase(
        zhongwen="麦唛呀，即是呢⋯",
        yuewen="妈妈啊，麦兜同学，即系呢⋯",
        yuewen_proofread="妈妈啊，麦兜同学，即系呢⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="我好像觉得呢⋯",
        yuewen="我个心总系仁住仁住⋯",
        yuewen_proofread="我个心总系印住印住⋯",
        note="Corrected '仁住仁住' to '印住印住' as '印住' (a pounding or pressing "
        "feeling) is a common Cantonese expression for a feeling in "
        "the heart, while '仁住' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="有什么人在喊我似的",
        yuewen="好似有人嗌紧我个名噉嘅",
        yuewen_proofread="好似有人嗌紧我个名噉嘅",
        note="",
    ),
    ProofTestCase(
        zhongwen="你们不要以为我心散",
        yuewen="你哋唔好以为我心散啊",
        yuewen_proofread="你哋唔好以为我心散啊",
        note="",
    ),
    ProofTestCase(
        zhongwen="其实我正在思考一个学术问题：",
        yuewen="其实我系喺度思考紧一啲学术性嘅问题：",
        yuewen_proofread="其实我系喺度思考紧一啲学术性嘅问题：",
        note="",
    ),
    ProofTestCase(
        zhongwen="橙，为什么会是「疴﹣烂﹣煮」呢？",
        yuewen="点解橙叫Orange呢？",
        yuewen_proofread="点解橙叫Orange呢？",
        note="",
    ),
    ProofTestCase(
        zhongwen="妈妈说吃橙可通大便",
        yuewen="妈妈话食橙会通大变",
        yuewen_proofread="妈妈话食橙会通大便",
        note="Corrected '大变' to '大便' as '大便' is the correct term for bowel "
        "movement, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="「疴」这个我明白，可是「烂﹣煮」呢？",
        yuewen="「噢」呢个我明白，但系「橙」呢？",
        yuewen_proofread="",
        note="Cleared as '「噢」呢个我明白，但系「橙」呢？' bears no resemblance to the "
        "original phrase '「疴」这个我明白，可是「烂﹣煮」呢？' and is clearly a "
        "complete transcription failure.",
    ),
    ProofTestCase(
        zhongwen="还有这个「芭﹣娜﹣娜」香蕉",
        yuewen="仲有呢个啊，「芭拉娜」啊，香蕉啊",
        yuewen_proofread="仲有呢个啊，「芭娜娜」啊，香蕉啊",
        note="Corrected '芭拉娜' to '芭娜娜' as '芭娜娜' is the correct "
        "transliteration for 'banana' in Cantonese, matching the 中文.",
    ),
    ProofTestCase(
        zhongwen="为什么雨伞又会是「暗﹣芭﹣娜﹣娜」呢？",
        yuewen="点解雨姐会叫做暗芭拉娜呢？",
        yuewen_proofread="点解雨姐会叫做暗芭娜娜呢？",
        note="Corrected '暗芭拉娜' to '暗芭娜娜' as '芭娜娜' is the correct "
        "transliteration for 'banana', matching the intended pun in "
        "the original.",
    ),
    ProofTestCase(
        zhongwen="我「暗」的「暗」掉一条蕉",
        yuewen="嗱，我暗啦，噉我暗𠮶条香蕉",
        yuewen_proofread="嗱，我暗啦，噉我暗𠮶条蕉",
        note="Replaced '香蕉' with '蕉' as the original phrase is '掉一条蕉', and "
        "'蕉' is the correct colloquial term for 'banana' in this "
        "context; '香蕉' is likely a mishearing or over-formalization.",
    ),
    ProofTestCase(
        zhongwen="至多是疴烂煮，怎么会下起雨来呢？",
        yuewen="至多会Orange啫，点解会搞到落雨呢？",
        yuewen_proofread="至多会屙烂啫，点解会搞到落雨呢？",
        note="Corrected 'Orange' to '屙烂' as '屙烂' (diarrhea) is a plausible "
        "mishearing and matches the meaning of '疴烂煮' in the 中文.",
    ),
    ProofTestCase(
        zhongwen="这世界还有很多事情我弄不明白",
        yuewen="呢个世界仲有好多嘢我谂唔明",
        yuewen_proofread="呢个世界仲有好多嘢我谂唔明",
        note="",
    ),
    ProofTestCase(
        zhongwen="但我不害怕",
        yuewen="不过我唔怕",
        yuewen_proofread="不过我唔怕",
        note="",
    ),
    ProofTestCase(
        zhongwen="我想，有天我念完幼稚园",
        yuewen="我谂，到我读完幼稚园",
        yuewen_proofread="我谂，到我读完幼稚园",
        note="",
    ),
    ProofTestCase(
        zhongwen="升小学，上中学",
        yuewen="识埋小学，上到中学",
        yuewen_proofread="升埋小学，上到中学",
        note="Corrected '识埋小学' to '升埋小学' as '升' (move up/advance) matches "
        "the meaning of '升小学' in the 中文, while '识' (know) is likely a "
        "mishearing.",
    ),
    ProofTestCase(
        zhongwen="再念大学⋯",
        yuewen="再入埋大学⋯",
        yuewen_proofread="再入埋大学⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="当我大学毕业的时候",
        yuewen="等我大学毕业𠮶阵",
        yuewen_proofread="等我大学毕业𠮶阵",
        note="",
    ),
    ProofTestCase(
        zhongwen="我知道我会明白一切！",
        yuewen="我谂我乜都会明白晒！",
        yuewen_proofread="我谂我乜都会明白晒！",
        note="",
    ),
    ProofTestCase(
        zhongwen="那时候⋯",
        yuewen="到𠮶阵⋯",
        yuewen_proofread="到𠮶阵⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="我买所房子给妈妈！",
        yuewen="我买层楼畀我妈妈！",
        yuewen_proofread="我买层楼畀我妈妈！",
        note="",
    ),
]  # proof_test_cases_block_4
proof_test_cases_block_5 = [
    ProofTestCase(
        zhongwen="幼稚园楼下，由校长兼营的茶餐厅",
        yuewen="喺幼稚园楼下，校长兼营嘅间茶餐厅",
        yuewen_proofread="喺幼稚园楼下，校长兼营嘅间茶餐厅",
        note="",
    ),
    ProofTestCase(
        zhongwen="我们一班同学下课后经常光顾",
        yuewen="我哋一班同学仔放咗学都经常系傍陈",
        yuewen_proofread="我哋一班同学仔放咗学都经常去光顾",
        note="Corrected '系傍陈' to '去光顾' as '傍陈' is a likely mishearing of "
        "'光顾', which matches the meaning of the 中文.",
    ),
    ProofTestCase(
        zhongwen="鱼蛋粗面，麻烦你　　粗面买光了",
        yuewen="唔该鱼蛋粗啊，冇粗面噃",
        yuewen_proofread="唔该鱼蛋粗面啊，冇粗面噃",
        note="Corrected '鱼蛋粗啊' to '鱼蛋粗面啊' as '粗啊' is likely a mishearing "
        "or truncation of '粗面'.",
    ),
    ProofTestCase(
        zhongwen="那样子⋯来碗鱼蛋河粉吧　　鱼蛋买光了",
        yuewen="噉啊⋯要碗鱼蛋好啊　　冇鱼蛋噃",
        yuewen_proofread="噉啊⋯要碗鱼蛋河粉啊　　冇鱼蛋噃",
        note="Added '河粉' after '鱼蛋' to match the intended meaning of "
        "'鱼蛋河粉' in the 中文, as '鱼蛋好' is likely a mishearing of '鱼蛋河粉'.",
    ),
    ProofTestCase(
        zhongwen="那么⋯金钱肚粗面好了　　粗面买光了",
        yuewen="噉啊⋯要金钱透粗啊　　冇粗面噃",
        yuewen_proofread="噉啊⋯要金钱肚粗啊　　冇粗面噃",
        note="Corrected '金钱透' to '金钱肚' as '金钱肚' is the correct term for "
        "the dish, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="那么要鱼蛋油面吧　　鱼蛋买光了",
        yuewen="噉啊，咁要鱼蛋油面啊　　冇鱼蛋噃",
        yuewen_proofread="噉啊，咁要鱼蛋油面啊　　冇鱼蛋噃",
        note="",
    ),
    ProofTestCase(
        zhongwen="怎么都买光了？",
        yuewen="乜样样都冇嘅？",
        yuewen_proofread="乜样样都冇嘅？",
        note="",
    ),
    ProofTestCase(
        zhongwen="来个墨鱼丸粗面吧　　粗面买光了",
        yuewen="噉要蜜丸粗啊　　冇粗面噃",
        yuewen_proofread="噉要墨丸粗啊　　冇粗面噃",
        note="Corrected '蜜丸' to '墨丸' as '墨丸' (墨鱼丸) matches the intended "
        "meaning of '墨鱼丸' in the 中文, while '蜜丸' is likely a "
        "mishearing.",
    ),
    ProofTestCase(
        zhongwen="又买光了？",
        yuewen="又冇啊？",
        yuewen_proofread="又冇啊？",
        note="",
    ),
    ProofTestCase(
        zhongwen="麻烦来碗鱼蛋濑吧　　鱼蛋买光了",
        yuewen="噉唔该畀碗鱼蛋奶啊　　冇鱼蛋噃",
        yuewen_proofread="噉唔该畀碗鱼蛋濑啊　　冇鱼蛋噃",
        note="Corrected '鱼蛋奶' to '鱼蛋濑' as '濑' is the correct term for "
        "'noodles in soup' (濑粉), matching the context of ordering "
        "food.",
    ),
    ProofTestCase(
        zhongwen="麦兜呀，鱼蛋跟粗面都买光了",
        yuewen="麦兜啊，佢哋啲鱼蛋同粗面卖晒㗎啦",
        yuewen_proofread="麦兜啊，佢哋啲鱼蛋同粗面卖晒㗎啦",
        note="",
    ),
    ProofTestCase(
        zhongwen="即是所有鱼蛋跟粗面的配搭都没了",
        yuewen="即系所有要鱼蛋或者粗面嘅配搭都冇㗎啦",
        yuewen_proofread="即系所有要鱼蛋或者粗面嘅配搭都冇㗎啦",
        note="",
    ),
    ProofTestCase(
        zhongwen="没有那些配搭吗？",
        yuewen="「噢」冇𠮶啲配搭啊？",
        yuewen_proofread="冇𠮶啲配搭啊？",
        note="Removed the extraneous '「噢」' at the beginning, which is not "
        "present in the original and likely a mishearing or filler.",
    ),
    ProofTestCase(
        zhongwen="麻烦你，净要鱼蛋吧　　鱼蛋买光了",
        yuewen="噉唔该净鱼蛋啊　　冇鱼蛋噃",
        yuewen_proofread="噉唔该净鱼蛋啊　　冇鱼蛋噃",
        note="",
    ),
    ProofTestCase(
        zhongwen="那么净要粗面呢？　　粗面买光了",
        yuewen="净粗面呢？　　冇粗面噃",
        yuewen_proofread="净粗面呢？　　冇粗面噃",
        note="",
    ),
    ProofTestCase(
        zhongwen="看到这里⋯",
        yuewen="睇到呢度⋯",
        yuewen_proofread="睇到呢度⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="大家大概都知道我是个怎么样的叻仔",
        yuewen="大家大概都知道我有几叻仔嘞",
        yuewen_proofread="大家大概都知道我有几叻仔嘞",
        note="",
    ),
    ProofTestCase(
        zhongwen="那时候我无忧无虑，万事无所谓﹣﹣",
        yuewen="果只我无忧无虑，冇乜所谓﹣﹣",
        yuewen_proofread="果阵我无忧无虑，冇乜所谓﹣﹣",
        note="Corrected '果只' to '果阵' as '果阵' (that time) matches the "
        "meaning of '那时候', while '果只' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="鱼蛋买光了？那么粗面吧",
        yuewen="冇鱼蛋咩？粗面都好啊",
        yuewen_proofread="冇鱼蛋咩？粗面都好啊",
        note="",
    ),
    ProofTestCase(
        zhongwen="麦兜，射呀！",
        yuewen="麦兜，转身食啊！",
        yuewen_proofread="麦兜，转身食啊！",
        note="",
    ),
]  # proof_test_cases_block_5
proof_test_cases_block_6 = [
    ProofTestCase(
        zhongwen="看着自己每天疴烂煮⋯",
        yuewen="睇住自己日日柯能处⋯",
        yuewen_proofread="睇住自己日日疴烂煮⋯",
        note="Corrected '柯能处' to '疴烂煮' as '疴烂煮' is a direct and correct "
        "phonetic match for the original phrase, while '柯能处' is a "
        "mishearing.",
    ),
    ProofTestCase(
        zhongwen="每天长肉⋯",
        yuewen="日日掌肉⋯",
        yuewen_proofread="日日长肉⋯",
        note="Corrected '掌肉' to '长肉' as '长肉' (to gain weight) matches the "
        "meaning of the 中文, while '掌肉' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="我感到充满力量！",
        yuewen="感到充满力量！",
        yuewen_proofread="感到充满力量！",
        note="",
    ),
    ProofTestCase(
        zhongwen="世界好美丽！",
        yuewen="世界好美丽！",
        yuewen_proofread="世界好美丽！",
        note="",
    ),
]  # proof_test_cases_block_6
proof_test_cases_block_7 = [
    ProofTestCase(
        zhongwen="有一首歌，Miss Chan唱的好听",
        yuewen="有一首歌，麦词春唱得好好听呀",
        yuewen_proofread="有一首歌，Miss Chan唱得好好听呀",
        note="Corrected '麦词春' to 'Miss Chan' as '麦词春' is a mishearing of "
        "'Miss Chan', matching the original meaning.",
    ),
    ProofTestCase(
        zhongwen="我时常想着学习",
        yuewen="我成日想学习",
        yuewen_proofread="我成日想学习",
        note="",
    ),
    ProofTestCase(
        zhongwen="可每次我总唱成「疴」什么什么的⋯",
        yuewen="但系唱嚟唱去都系阿伦厨，咁Ballana噉⋯",
        yuewen_proofread="",
        note="Cleared as '阿伦厨，咁Ballana噉⋯' bears no resemblance to the "
        "original phrase about singing '疴' and is clearly a complete "
        "transcription failure.",
    ),
    ProofTestCase(
        zhongwen="是All Things Bright and Beautiful吧？",
        yuewen="系唔系All Things Bright and Beautiful呀？",
        yuewen_proofread="系唔系All Things Bright and Beautiful呀？",
        note="",
    ),
    ProofTestCase(
        zhongwen="是的，一切都好！",
        yuewen="系呀，所有嘢都几好喇！",
        yuewen_proofread="系呀，所有嘢都几好喇！",
        note="",
    ),
    ProofTestCase(
        zhongwen="世上一切，一切一切⋯",
        yuewen="世上一切⋯",
        yuewen_proofread="世上一切⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="所有那些，都好！",
        yuewen="所有𠮶啲嘢，都几好！All Things Bright and Beautiful",
        yuewen_proofread="所有𠮶啲嘢，都几好！All Things Bright and Beautiful",
        note="",
    ),
]  # proof_test_cases_block_7
proof_test_cases_block_8 = [
    ProofTestCase(
        zhongwen="多劳多得！",
        yuewen="1234567，多喽多得！",
        yuewen_proofread="多劳多得！",
        note="Removed '1234567' as it is unrelated and likely a "
        "transcription error; corrected '多喽多得' to '多劳多得' to match the "
        "intended phrase, as '多喽' is a mishearing of '多劳'.",
    ),
    ProofTestCase(
        zhongwen="星期一至星期七⋯多劳多得！",
        yuewen="星期一至星期七⋯多喽多得！",
        yuewen_proofread="星期一至星期七⋯多劳多得！",
        note="Corrected '多喽多得' to '多劳多得' as '多劳多得' is the correct phrase "
        "meaning 'the more you work, the more you earn', and '喽' is a "
        "mishearing of '劳'.",
    ),
    ProofTestCase(
        zhongwen="这位喊得特劲的中年母猪",
        yuewen="呢个嗌得特别劲嘅中年母猪",
        yuewen_proofread="呢个嗌得特别劲嘅中年母猪",
        note="",
    ),
    ProofTestCase(
        zhongwen="就是我妈妈麦太",
        yuewen="就系我妈妈麦太",
        yuewen_proofread="就系我妈妈麦太",
        note="",
    ),
    ProofTestCase(
        zhongwen="我妈妈真的很劲",
        yuewen="我妈妈真系好劲呀",
        yuewen_proofread="我妈妈真系好劲呀",
        note="",
    ),
    ProofTestCase(
        zhongwen="一个女人背起整个世界！",
        yuewen="一个女人揹起成个世界！",
        yuewen_proofread="一个女人揹起成个世界！",
        note="",
    ),
]  # proof_test_cases_block_8
proof_test_cases_block_9 = [
    ProofTestCase(
        zhongwen="是的，我妈妈真的很厉害",
        yuewen="系呀，我妈妈真系好犀利㗎",
        yuewen_proofread="系呀，我妈妈真系好犀利㗎",
        note="",
    ),
    ProofTestCase(
        zhongwen="除了兼任保险，地产经纪及trading⋯",
        yuewen="除咗做保险地产经纪同埋trading之外⋯",
        yuewen_proofread="除咗做保险地产经纪同埋trading之外⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="她还趁高科技热潮搞了个烹饪网站⋯",
        yuewen="佢仲趁住高科技热潮搞咗个煮𩠌嘅网站⋯",
        yuewen_proofread="佢仲趁住高科技热潮搞咗个煮𩠌嘅网站⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="www．麦太世界．com",
        yuewen="www.mcticege.com",
        yuewen_proofread="www.mctaisegai.com",
        note="Corrected 'mcticege' to 'mctaisegai' as it is a closer "
        "phonetic representation of '麦太世界' in Cantonese.",
    ),
    ProofTestCase(
        zhongwen="她做的菜，同样厉害",
        yuewen="佢煮嘅𩠌，一样咁犀利",
        yuewen_proofread="佢煮嘅𩠌，一样咁犀利",
        note="",
    ),
    ProofTestCase(
        zhongwen="欢迎大家收看《麦太世界》",
        yuewen="欢迎大家收睇《麦太世界》",
        yuewen_proofread="欢迎大家收睇《麦太世界》",
        note="",
    ),
    ProofTestCase(
        zhongwen="今日为大家介绍一个⋯",
        yuewen="今日我为大家介绍个⋯",
        yuewen_proofread="今日我为大家介绍个⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="简单别致的小菜纸包鸡",
        yuewen="简单又别致嘅小菜自包鸡",
        yuewen_proofread="简单又别致嘅小菜纸包鸡",
        note="Corrected '自包鸡' to '纸包鸡' as '纸包鸡' is the correct dish name, "
        "matching the meaning in 中文.",
    ),
    ProofTestCase(
        zhongwen="家中小朋友一定好喜欢",
        yuewen="家里头嘅小朋友一定好喜欢㗎",
        yuewen_proofread="家里头嘅小朋友一定好喜欢㗎",
        note="",
    ),
    ProofTestCase(
        zhongwen="材料很简单：一个鸡包",
        yuewen="材料系好简单：我哋只需要一个鸡包",
        yuewen_proofread="材料系好简单：我哋只需要一个鸡包",
        note="",
    ),
    ProofTestCase(
        zhongwen="将鸡包底部的纸撕下来⋯慢慢地撕",
        yuewen="我哋将黐喺鸡包底嘅纸撕出嚟⋯慢慢撕",
        yuewen_proofread="我哋将黐喺鸡包底嘅纸撕出嚟⋯慢慢撕",
        note="",
    ),
    ProofTestCase(
        zhongwen="就会得到一张鸡包纸",
        yuewen="咁就会得到一张鸡包纸喇",
        yuewen_proofread="咁就会得到一张鸡包纸喇",
        note="",
    ),
    ProofTestCase(
        zhongwen="把鸡包纸一反反转",
        yuewen="然后将鸡包纸一反，反转",
        yuewen_proofread="然后将鸡包纸一反，反转",
        note="",
    ),
    ProofTestCase(
        zhongwen="这一味纸包鸡就完成了，很容易是吧？",
        yuewen="呢味自包鸡就完成喇，系咪好易整啦？",
        yuewen_proofread="呢味纸包鸡就完成喇，系咪好易整啦？",
        note="Corrected '自包鸡' to '纸包鸡' as '纸包鸡' is the correct dish name "
        "and matches the 中文.",
    ),
    ProofTestCase(
        zhongwen="多谢大家收看",
        yuewen="多谢大家收睇",
        yuewen_proofread="多谢大家收睇",
        note="",
    ),
]  # proof_test_cases_block_9
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
]  # proof_test_cases_block_10
proof_test_cases_block_11 = [
    ProofTestCase(
        zhongwen="现在要教大家一味别致小菜﹣",
        yuewen="间阵要教大家一味几别节嘅小菜﹣",
        yuewen_proofread="间阵要教大家一味几别致嘅小菜﹣",
        note="Corrected '别节' to '别致' as '别致' is the correct term for "
        "'unique' or 'special', matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="包鸡纸包鸡包纸包鸡",
        yuewen="包鸡子包鸡包子包鸡",
        yuewen_proofread="包鸡纸包鸡包纸包鸡",
        note="Corrected '鸡子' and '子' to '鸡纸' and '纸' as '纸' is the correct "
        "word for '纸包鸡' (paper-wrapped chicken), matching the "
        "original phrase.",
    ),
    ProofTestCase(
        zhongwen="首先将纸包鸡小心撕开",
        yuewen="首先将子包鸡小心噉撕开",
        yuewen_proofread="首先将纸包鸡小心噉撕开",
        note="Corrected '子包鸡' to '纸包鸡' as '纸包鸡' is the correct dish name "
        "and matches the 中文.",
    ),
    ProofTestCase(
        zhongwen="大家就会有一张纸包鸡及一块鸡",
        yuewen="大家就会有一张包鸡子同埋一嚿鸡啦",
        yuewen_proofread="大家就会有一张纸包鸡同埋一嚿鸡啦",
        note="Corrected '包鸡子' to '纸包鸡' as '纸包鸡' is the correct term for "
        "the dish, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="接着把鸡包纸这样子包起那块鸡",
        yuewen="跟住将鸡包子好似我噉包住牛鸡",
        yuewen_proofread="跟住将鸡包纸好似我噉包住嗰块鸡",
        note="Corrected '鸡包子' to '鸡包纸' as '鸡包纸' matches the meaning of "
        "'把鸡包纸这样子包起' and '鸡包子' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="再依照这样子用包鸡纸把它包起",
        yuewen="然后再好似噉样将包鸡子包包包包包包住佢",
        yuewen_proofread="然后再好似噉样将包鸡纸包包包包包包住佢",
        note="Corrected '包鸡子' to '包鸡纸' as '包鸡纸' (greaseproof paper) "
        "matches the meaning in the 中文 and '包鸡子' is likely a "
        "mishearing.",
    ),
    ProofTestCase(
        zhongwen="一味「包鸡纸包鸡包纸包鸡」完成了！",
        yuewen="咁一味包鸡子包鸡包子包鸡就完成喇！",
        yuewen_proofread="咁一味包鸡纸包鸡包纸包鸡就完成喇！",
        note="Corrected '包鸡子' and '包子' to '包鸡纸' and '包纸' respectively, as "
        "'纸' is the correct word in the phrase '纸包鸡', matching the "
        "original meaning.",
    ),
    ProofTestCase(
        zhongwen="真的很简单吧？",
        yuewen="系咪好简单呢？",
        yuewen_proofread="系咪好简单呢？",
        note="",
    ),
    ProofTestCase(
        zhongwen="还真有一块鸡吃呢！",
        yuewen="仲真系有嚿鸡食添！",
        yuewen_proofread="仲真系有嚿鸡食添！",
        note="",
    ),
]  # proof_test_cases_block_11
proof_test_cases_block_12 = []  # proof_test_cases_block_12
proof_test_cases_block_13 = []  # proof_test_cases_block_13
proof_test_cases_block_14 = []  # proof_test_cases_block_14
proof_test_cases_block_15 = []  # proof_test_cases_block_15
proof_test_cases_block_16 = []  # proof_test_cases_block_16
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
]  # proof_test_cases_block_17
proof_test_cases_block_18 = []  # proof_test_cases_block_18
proof_test_cases_block_19 = []  # proof_test_cases_block_19
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
]  # proof_test_cases_block_20
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
]  # proof_test_cases_block_21
proof_test_cases_block_22 = []  # proof_test_cases_block_22
proof_test_cases_block_23 = []  # proof_test_cases_block_23
proof_test_cases_block_24 = []  # proof_test_cases_block_24
proof_test_cases_block_25 = []  # proof_test_cases_block_25
proof_test_cases_block_26 = []  # proof_test_cases_block_26
proof_test_cases_block_27 = []  # proof_test_cases_block_27
proof_test_cases_block_28 = []  # proof_test_cases_block_28
proof_test_cases_block_29 = []  # proof_test_cases_block_29
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
]  # proof_test_cases_block_30
proof_test_cases_block_31 = []  # proof_test_cases_block_31
proof_test_cases_block_32 = [
    ProofTestCase(
        zhongwen="长洲，我终于来到长洲了！",
        yuewen="长洲，我终于嚟到长洲嘞！",
        yuewen_proofread="长洲，我终于嚟到长洲嘞！",
        note="",
    ),
]  # proof_test_cases_block_32
proof_test_cases_block_33 = [
    ProofTestCase(
        zhongwen="长洲，我得亲吻这片圣洁的土地！",
        yuewen="长洲，我要亲吻呢片盛洁嘅土地！",
        yuewen_proofread="长洲，我要亲吻呢片圣洁嘅土地！",
        note="Corrected '盛洁' to '圣洁' as '圣洁' is the correct term for 'sacred' or 'holy', matching the meaning in the 中文.",
    ),
]  # proof_test_cases_block_33
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
]  # proof_test_cases_block_34
proof_test_cases_block_35 = []  # proof_test_cases_block_35
proof_test_cases_block_36 = []  # proof_test_cases_block_36
proof_test_cases_block_37 = []  # proof_test_cases_block_37
proof_test_cases_block_38 = []  # proof_test_cases_block_38
proof_test_cases_block_39 = []  # proof_test_cases_block_39
proof_test_cases_block_40 = []  # proof_test_cases_block_40
proof_test_cases_block_41 = []  # proof_test_cases_block_41
proof_test_cases_block_42 = []  # proof_test_cases_block_42
proof_test_cases_block_43 = []  # proof_test_cases_block_43
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
]  # proof_test_cases_block_44
proof_test_cases_block_45 = []  # proof_test_cases_block_45
proof_test_cases_block_46 = []  # proof_test_cases_block_46
proof_test_cases_block_47 = []  # proof_test_cases_block_47
proof_test_cases_block_48 = []  # proof_test_cases_block_48
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
]  # proof_test_cases_block_49
proof_test_cases_block_50 = []  # proof_test_cases_block_50
proof_test_cases_block_51 = []  # proof_test_cases_block_51
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
]  # proof_test_cases_block_52
proof_test_cases_block_53 = []  # proof_test_cases_block_53
proof_test_cases_block_54 = []  # proof_test_cases_block_54
proof_test_cases_block_55 = []  # proof_test_cases_block_55
proof_test_cases_block_56 = []  # proof_test_cases_block_56
proof_test_cases_block_57 = []  # proof_test_cases_block_57
proof_test_cases_block_58 = []  # proof_test_cases_block_58
proof_test_cases_block_59 = []  # proof_test_cases_block_59
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
]  # proof_test_cases_block_60
proof_test_cases_block_61 = []  # proof_test_cases_block_61
proof_test_cases_block_62 = []  # proof_test_cases_block_62
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
]  # proof_test_cases_block_63
proof_test_cases_block_64 = []  # proof_test_cases_block_64
proof_test_cases_block_65 = [
    ProofTestCase(
        zhongwen="「⋯无力挽！」",
        yuewen="「⋯无泪弯！」",
        yuewen_proofread="「⋯无力挽！」",
        note="Corrected '无泪弯' to '无力挽' as it is a clear mishearing; '无力挽' matches the intended meaning of '无力挽' in the 中文.",
    ),
]  # proof_test_cases_block_65
proof_test_cases_block_66 = []  # proof_test_cases_block_66
proof_test_cases_block_67 = []  # proof_test_cases_block_67
proof_test_cases_block_68 = []  # proof_test_cases_block_68
proof_test_cases_block_69 = []  # proof_test_cases_block_69
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
]  # proof_test_cases_block_70
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
]  # proof_test_cases_block_71
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
]  # proof_test_cases_block_72
mlamd_proof_test_cases: list[ProofTestCase] = sum(
    (globals()[f"proof_test_cases_block_{i}"] for i in range(73)), []
)
"""MLAMD 粤文 proof test cases."""

__all__ = [
    "mlamd_proof_test_cases",
]
