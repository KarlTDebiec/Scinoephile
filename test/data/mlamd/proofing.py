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
proof_test_cases_block_12 = [
    ProofTestCase(
        zhongwen="今日为大家介绍一味⋯",
        yuewen="今日要同大家介绍一味⋯",
        yuewen_proofread="今日要同大家介绍一味⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="小朋友一定喜欢的⋯",
        yuewen="小朋友一定喜欢嘅⋯",
        yuewen_proofread="小朋友一定喜欢嘅⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="鸡包包鸡包包鸡包纸包纸⋯",
        yuewen="鸡包包鸡包包鸡包纸包纸包鸡⋯",
        yuewen_proofread="鸡包包鸡包包鸡包纸包纸⋯",
        note="Removed the extra '包鸡' at the end to match the repetition "
        "pattern in the 中文 and avoid a likely mishearing.",
    ),
    ProofTestCase(
        zhongwen="包鸡包鸡包纸包鸡",
        yuewen="包包鸡纸包鸡包纸包鸡",
        yuewen_proofread="包鸡包鸡包纸包鸡",
        note="Corrected '包包鸡纸包鸡包纸包鸡' to '包鸡包鸡包纸包鸡' to match the repetition "
        "and order of '包鸡' as in the original phrase; the extra '包' "
        "and misplaced '纸' were likely mishearings.",
    ),
    ProofTestCase(
        zhongwen="做法亦很简单",
        yuewen="做法都好简单",
        yuewen_proofread="做法都好简单",
        note="",
    ),
    ProofTestCase(
        zhongwen="只要将鸡包包住个鸡包",
        yuewen="我哋先将鸡包包住个鸡包",
        yuewen_proofread="我哋先将鸡包包住个鸡包",
        note="",
    ),
    ProofTestCase(
        zhongwen="再包住个鸡包⋯",
        yuewen="再包住个鸡包⋯",
        yuewen_proofread="再包住个鸡包⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="包住张鸡包纸",
        yuewen="包住张鸡包纸",
        yuewen_proofread="包住张鸡包纸",
        note="",
    ),
    ProofTestCase(
        zhongwen="再包包包包包住个纸鸡包",
        yuewen="再包包包包包住个纸包鸡",
        yuewen_proofread="再包包包包包住个纸包鸡",
        note="",
    ),
    ProofTestCase(
        zhongwen="再包包包，纸纸纸",
        yuewen="再包包包包包鸡包纸包纸纸纸纸纸纸包纸纸包鸡包鸡纸纸包鸡鸡鸡鸡纸纸纸再包鸡鸡",
        yuewen_proofread="",
        note="Cleared as the provided 粤文 is a string of repeated words "
        "with no meaningful correspondence to the original 中文 phrase, "
        "indicating a complete transcription failure.",
    ),
    ProofTestCase(
        zhongwen="可我妈妈也有她温柔的一面",
        yuewen="不过我妈妈都有佢温柔嘅一面",
        yuewen_proofread="不过我妈妈都有佢温柔嘅一面",
        note="",
    ),
    ProofTestCase(
        zhongwen="例如每晚睡觉前，她都会说故事给我听",
        yuewen="例如每晚临睡前，佢都会讲故事畀我听",
        yuewen_proofread="例如每晚临睡前，佢都会讲故事畀我听",
        note="",
    ),
    ProofTestCase(
        zhongwen="从前，有个小朋友撒谎；有一天⋯",
        yuewen="从前有个小朋友讲大话",
        yuewen_proofread="从前有个小朋友讲大话",
        note="",
    ),
    ProofTestCase(
        zhongwen="他死了！",
        yuewen="有一日，佢死咗！",
        yuewen_proofread="有一日，佢死咗！",
        note="",
    ),
    ProofTestCase(
        zhongwen="从前，有个小朋友很勤力念书⋯",
        yuewen="从前，有个小朋友好勤力读书⋯",
        yuewen_proofread="从前，有个小朋友好勤力读书⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="他长大后，发财了！",
        yuewen="佢长大发咗！",
        yuewen_proofread="佢长大发咗！",
        note="",
    ),
    ProofTestCase(
        zhongwen="从前，有个小朋友不孝，有天⋯",
        yuewen="从前有个小朋友唔孝顺⋯",
        yuewen_proofread="从前有个小朋友唔孝顺⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="他扭了脚骹！",
        yuewen="有一日佢屈亲个脚脚！",
        yuewen_proofread="有一日佢屈亲个脚骹！",
        note="Corrected '脚脚' to '脚骹' as '脚骹' is the correct Cantonese term "
        "for 'ankle', matching the meaning of the 中文.",
    ),
    ProofTestCase(
        zhongwen="妈妈，我想睡觉",
        yuewen="妈，我想瞓啦",
        yuewen_proofread="妈，我想瞓啦",
        note="",
    ),
]  # proof_test_cases_block_12
proof_test_cases_block_13 = [
    ProofTestCase(
        zhongwen="从前，有个小朋友早睡晚起；第二天⋯",
        yuewen="从前有个小朋友早睡晚起；第二朝⋯",
        yuewen_proofread="从前有个小朋友早睡晚起；第二朝⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="他死了！",
        yuewen="佢死咗！",
        yuewen_proofread="佢死咗！",
        note="",
    ),
    ProofTestCase(
        zhongwen="我妈妈就是这样子，一切都那么直接",
        yuewen="我妈妈就系噉，一切都咁直接",
        yuewen_proofread="我妈妈就系噉，一切都咁直接",
        note="",
    ),
    ProofTestCase(
        zhongwen="她爱得我直接⋯",
        yuewen="佢爱得我直接⋯",
        yuewen_proofread="佢爱得我直接⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="对我的期望直接",
        yuewen="对我嘅期望直接",
        yuewen_proofread="对我嘅期望直接",
        note="",
    ),
    ProofTestCase(
        zhongwen="对她，一、二、三、四、五、六、七",
        yuewen="佢，一、二、三、四、五、六、七",
        yuewen_proofread="佢，一、二、三、四、五、六、七",
        note="",
    ),
    ProofTestCase(
        zhongwen="没有不成的事",
        yuewen="唔得都要得字幕由Amara.org社群提供",
        yuewen_proofread="唔得都要得",
        note="Removed '字幕由Amara.org社群提供' as it is not part of the spoken "
        "content and is unrelated to the original sentence.",
    ),
]  # proof_test_cases_block_13
proof_test_cases_block_14 = [
    ProofTestCase(
        zhongwen="可有些事情，要是真的不成呢？",
        yuewen="但系如果有啲嘢，真系真系唔得呢？",
        yuewen_proofread="但系如果有啲嘢，真系真系唔得呢？",
        note="",
    ),
    ProofTestCase(
        zhongwen="日子一天一天的过",
        yuewen="日子一日一日咁过",
        yuewen_proofread="日子一日一日咁过",
        note="",
    ),
    ProofTestCase(
        zhongwen="首先是周润发事件⋯",
        yuewen="首先周润发𠮶单嘢⋯",
        yuewen_proofread="首先周润发𠮶单嘢⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="拜托不要再提了！",
        yuewen="大家都唔好再提！",
        yuewen_proofread="大家都唔好再提！",
        note="",
    ),
    ProofTestCase(
        zhongwen="至于好运⋯",
        yuewen="至于好运⋯",
        yuewen_proofread="至于好运⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="我用一双童子手替妈妈抽的六合彩号码",
        yuewen="我用我嘅同事手帮妈妈抽嘅六合彩number",
        yuewen_proofread="我用我嘅童子手帮妈妈抽嘅六合彩number",
        note="Corrected '同事手' to '童子手' as '童子手' (child's hand) matches the "
        "meaning in the 中文, while '同事手' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="奇迹般似的一个号码也没中过！",
        yuewen="竟然奇迹一样，一个都未中过！",
        yuewen_proofread="竟然奇迹一样，一个都未中过！",
        note="",
    ),
    ProofTestCase(
        zhongwen="叻仔？",
        yuewen="叻仔？",
        yuewen_proofread="叻仔？",
        note="",
    ),
    ProofTestCase(
        zhongwen="我也试过努力念书，可是⋯",
        yuewen="过好努力咁读书，但系⋯",
        yuewen_proofread="过好努力咁读书，但系⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="可是⋯我仍然有梦",
        yuewen="我试，但系⋯我仲可以发梦",
        yuewen_proofread="我试，但系⋯我仲可以发梦",
        note="",
    ),
]  # proof_test_cases_block_14
proof_test_cases_block_15 = [
    ProofTestCase(
        zhongwen="马尔代夫，座落于印度洋的世外桃源",
        yuewen="马尔代夫，坐落于印度洋嘅世外桃源",
        yuewen_proofread="马尔代夫，坐落于印度洋嘅世外桃源",
        note="",
    ),
    ProofTestCase(
        zhongwen="蓝天白云，椰林树影，水清沙幼",
        yuewen="蓝天白云，椰林树影，水清沙游",
        yuewen_proofread="蓝天白云，椰林树影，水清沙幼",
        note="Corrected '沙游' to '沙幼' as '沙幼' (fine sand) is the correct "
        "phrase matching the original meaning, while '沙游' is likely a "
        "mishearing.",
    ),
    ProofTestCase(
        zhongwen="七彩缤纷的珊瑚，目不暇给的热带鱼",
        yuewen="七彩缤纷嘅珊瑚，目不下级嘅热带鱼群",
        yuewen_proofread="七彩缤纷嘅珊瑚，目不暇给嘅热带鱼群",
        note="Corrected '目不下级' to '目不暇给' as '目不暇给' is the correct idiom "
        "meaning 'too many to take in', and '下级' is a likely "
        "mishearing of '暇给'.",
    ),
    ProofTestCase(
        zhongwen="充满赤道活力的原始海洋，脱离繁嚣",
        yuewen="充满住赤道热力嘅原始海洋，远离凡嚣",
        yuewen_proofread="充满住赤道热力嘅原始海洋，远离繁嚣",
        note="Corrected '凡嚣' to '繁嚣' as '繁嚣' is the correct term for "
        "'hustle and bustle', matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="体验热情如火的风土人情",
        yuewen="体验热情如火嘅风土人情",
        yuewen_proofread="体验热情如火嘅风土人情",
        note="",
    ),
    ProofTestCase(
        zhongwen="享受一个脱俗出尘的梦幻之旅",
        yuewen="享受一个脱轴出尘嘅梦幻之旅",
        yuewen_proofread="享受一个脱俗出尘嘅梦幻之旅",
        note="Corrected '脱轴' to '脱俗' as '脱俗' is the correct term for 'out "
        "of the ordinary', matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="犀利旅行社，旅行社牌照号码350999",
        yuewen="犀利旅行社，旅行社牌照号码350999",
        yuewen_proofread="犀利旅行社，旅行社牌照号码350999",
        note="",
    ),
    ProofTestCase(
        zhongwen="妈妈你知道马尔代夫在哪儿吗？",
        yuewen="妈妈你知唔知到马尔代夫系边㗎？",
        yuewen_proofread="妈妈你知唔知到马尔代夫系边㗎？",
        note="",
    ),
    ProofTestCase(
        zhongwen="很远的",
        yuewen="啊好远㗎",
        yuewen_proofread="啊好远㗎",
        note="",
    ),
    ProofTestCase(
        zhongwen="有多远？",
        yuewen="点远发呀？",
        yuewen_proofread="有几远呀？",
        note="Corrected '点远发呀' to '有几远呀' as '点远发呀' is a mishearing; '有几远呀' "
        "accurately asks 'how far' in Cantonese.",
    ),
    ProofTestCase(
        zhongwen="得搭飞机",
        yuewen="搭飞机至到啰",
        yuewen_proofread="搭飞机至到啰",
        note="",
    ),
    ProofTestCase(
        zhongwen="妈妈你会带我去吗？",
        yuewen="咁妈妈你会唔会走落去㗎？",
        yuewen_proofread="咁妈妈你会唔会走落去㗎？",
        note="",
    ),
    ProofTestCase(
        zhongwen="会！发财了再说吧",
        yuewen="会！得学发咗先啦",
        yuewen_proofread="会！得发咗先啦",
        note="Removed '学' from '得学发咗先啦' as it is likely a mishearing; "
        "'得发咗先啦' matches the meaning of '发财了再说吧'.",
    ),
    ProofTestCase(
        zhongwen="那么妈妈你什么时候发？",
        yuewen="咁妈妈你几时发得呀？",
        yuewen_proofread="咁妈妈你几时发得呀？",
        note="",
    ),
    ProofTestCase(
        zhongwen="快了⋯",
        yuewen="呃，就快啦⋯",
        yuewen_proofread="呃，就快啦⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="发梦呀！",
        yuewen="发梦吖嘛！",
        yuewen_proofread="发梦吖嘛！",
        note="",
    ),
]  # proof_test_cases_block_15
proof_test_cases_block_16 = [
    ProofTestCase(
        zhongwen="校长早晨！",
        yuewen="嗨！",
        yuewen_proofread="嗨！",
        note="",
    ),
    ProofTestCase(
        zhongwen="你最喜爱的地方是哪儿？",
        yuewen="你最喜爱嘅地方喺边度呀？",
        yuewen_proofread="你最喜爱嘅地方喺边度呀？",
        note="",
    ),
    ProofTestCase(
        zhongwen="我最喜爱的地方是日本",
        yuewen="我最喜爱嘅地方呢，就系日本喇",
        yuewen_proofread="我最喜爱嘅地方呢，就系日本喇",
        note="",
    ),
    ProofTestCase(
        zhongwen="那儿有Disneyland和Hello Kitty Land",
        yuewen="𠮶度好迪士尼呢，同埋HelloTT呢",
        yuewen_proofread="𠮶度有迪士尼乐园，同埋Hello Kitty乐园",
        note="Corrected '好迪士尼呢' to '有迪士尼乐园' and 'HelloTT呢' to 'Hello "
        "Kitty乐园' as '好' is a mishearing of '有', and 'HelloTT' is a "
        "mishearing of 'Hello Kitty', both matching the intended "
        "meaning of the original sentence.",
    ),
    ProofTestCase(
        zhongwen="我这个发夹也是在那儿买的",
        yuewen="我而家打紧个发卷都系𠮶边买嘅",
        yuewen_proofread="我而家戴紧个发夹都系𠮶边买嘅",
        note="Corrected '打紧个发卷' to '戴紧个发夹' as '发夹' matches the meaning of "
        "'发夹' in the 中文, while '发卷' is a likely mishearing.",
    ),
    ProofTestCase(
        zhongwen="我最喜爱的地方是加拿大",
        yuewen="我最钟意嘅地方就系加拿大",
        yuewen_proofread="我最钟意嘅地方就系加拿大",
        note="",
    ),
    ProofTestCase(
        zhongwen="婆婆跟舅父他们都在加拿大",
        yuewen="婆婆同埋舅父呀，佢哋都系加拿大㗎",
        yuewen_proofread="婆婆同埋舅父呀，佢哋都系加拿大㗎",
        note="",
    ),
    ProofTestCase(
        zhongwen="我最喜爱的地方是泰国",
        yuewen="我最钟意去嘅地方就系泰国喇",
        yuewen_proofread="我最钟意去嘅地方就系泰国喇",
        note="",
    ),
    ProofTestCase(
        zhongwen="那儿有很好多水上活动，还有鱼翅吃",
        yuewen="𠮶度有好多水晶活动㗎，仲有一次食添㖞",
        yuewen_proofread="𠮶度有好多水上活动㗎，仲有鱼翅食添㖞",
        note="Corrected '水晶活动' to '水上活动' as '水晶' is a mishearing of '水上', "
        "and '一次食' to '鱼翅食' as '鱼翅' (shark fin) matches the meaning "
        "in the 中文.",
    ),
    ProofTestCase(
        zhongwen="我最喜爱的地方⋯",
        yuewen="呃，我最喜爱嘅地方呢⋯",
        yuewen_proofread="呃，我最喜爱嘅地方呢⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="就是那间什么！",
        yuewen="就系𠮶间咩嚟啰！",
        yuewen_proofread="就系𠮶间咩嚟啰！",
        note="",
    ),
    ProofTestCase(
        zhongwen="那儿有欢乐天地，还有美食广场",
        yuewen="𠮶度有欢乐天地啦，仲有米食广场啦",
        yuewen_proofread="𠮶度有欢乐天地啦，仲有美食广场啦",
        note="Corrected '米食广场' to '美食广场' as '美食广场' is the correct term for "
        "'food court', matching the meaning in 中文.",
    ),
    ProofTestCase(
        zhongwen="那儿的海南鸡饭很大碟的",
        yuewen="𠮶度啲可能几份好大碟㗎",
        yuewen_proofread="𠮶度啲海南鸡饭好大碟㗎",
        note="Corrected '可能几份' to '海南鸡饭' as '可能几份' is a mishearing of "
        "'海南鸡饭', which matches the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="对了，那地方叫银城中心",
        yuewen="系喇系喇，𠮶间叫做银城中心",
        yuewen_proofread="系喇系喇，𠮶间叫做银城中心",
        note="",
    ),
    ProofTestCase(
        zhongwen="那店子的饭很多，很大碟的！",
        yuewen="𠮶间嘢啲饭好多人，好大碟㗎！",
        yuewen_proofread="𠮶间嘢啲饭好多，好大碟㗎！",
        note="Corrected '好多人' to '好多' as '好多人' means 'many people', which "
        "is a mishearing of '好多' (a lot of [rice]), matching the "
        "meaning of the 中文.",
    ),
    ProofTestCase(
        zhongwen="不过说到我最想去的地方，那可厉害了",
        yuewen="不过讲到我最想去嘅地方呢，𠮶度细嚟啰",
        yuewen_proofread="不过讲到我最想去嘅地方呢，𠮶度犀利啰",
        note="Corrected '细嚟啰' to '犀利啰' as '犀利' (sai1 lei6) matches the "
        "meaning of '厉害' in the 中文, while '细嚟' is likely a "
        "mishearing.",
    ),
    ProofTestCase(
        zhongwen="那儿蓝天白云，椰林树影，水清沙幼",
        yuewen="𠮶度南天白云，夜临树影，水清沙幽",
        yuewen_proofread="𠮶度蓝天白云，椰林树影，水清沙幼",
        note="Corrected '南天' to '蓝天', '夜临' to '椰林', and '沙幽' to '沙幼' as "
        "these are likely mishearings of the correct terms describing "
        "the scenery.",
    ),
    ProofTestCase(
        zhongwen="座落于印度洋的世外桃源",
        yuewen="独来鱼，印度洋嘅世外桃源",
        yuewen_proofread="座落于，印度洋嘅世外桃源",
        note="Corrected '独来鱼' to '座落于' as '独来鱼' is a mishearing of '座落于', "
        "matching the original meaning.",
    ),
]  # proof_test_cases_block_16
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
proof_test_cases_block_18 = [
    ProofTestCase(
        zhongwen="开点药给他吃就没事了",
        yuewen="开啲药过佢食就冇事㗎喇",
        yuewen_proofread="开啲药过佢食就冇事㗎喇",
        note="",
    ),
    ProofTestCase(
        zhongwen="医生，吃了药会不会有那个什么的？",
        yuewen="医生啊，啲药食咗会唔会有𠮶啲咩㗎？",
        yuewen_proofread="医生啊，啲药食咗会唔会有𠮶啲咩㗎？",
        note="",
    ),
    ProofTestCase(
        zhongwen="不会！",
        yuewen="唔会！",
        yuewen_proofread="唔会！",
        note="",
    ),
    ProofTestCase(
        zhongwen="那么吃药用不用那个什么的？",
        yuewen="噉佢食药使唔使咩啊？",
        yuewen_proofread="噉佢食药使唔使咩啊？",
        note="",
    ),
    ProofTestCase(
        zhongwen="不用！给他打口针吧！",
        yuewen="唔使！同佢打多支针添呢！",
        yuewen_proofread="唔使！同佢打多支针添呢！",
        note="",
    ),
    ProofTestCase(
        zhongwen="怎么？得打针？",
        yuewen="吓？要打针啊？",
        yuewen_proofread="吓？要打针啊？",
        note="",
    ),
    ProofTestCase(
        zhongwen="他最怕打针的了",
        yuewen="佢好怕打针㗎㖞",
        yuewen_proofread="佢好怕打针㗎㖞",
        note="",
    ),
    ProofTestCase(
        zhongwen="那么他怕不怕死？",
        yuewen="噉佢怕唔怕死呀？",
        yuewen_proofread="噉佢怕唔怕死呀？",
        note="",
    ),
]  # proof_test_cases_block_18
proof_test_cases_block_19 = [
    ProofTestCase(
        zhongwen="没事吧？快点先把药水喝掉！",
        yuewen="冇嘢吖嘛？快啲食埋啲药水佢先啦！",
        yuewen_proofread="冇嘢吖嘛？快啲食埋啲药水佢先啦！",
        note="",
    ),
    ProofTestCase(
        zhongwen="妈妈我不想喝药水",
        yuewen="妈妈，我唔想食药水呀",
        yuewen_proofread="妈妈，我唔想饮药水呀",
        note="Corrected '食药水' to '饮药水' as '饮' is the correct verb for "
        "taking liquid medicine in Cantonese, while '食' is used for "
        "eating solid food.",
    ),
    ProofTestCase(
        zhongwen="不要呀妈妈，我不喝呀",
        yuewen="唔好捞妈妈，我唔食呀",
        yuewen_proofread="唔好呀妈妈，我唔饮呀",
        note="Corrected '唔好捞' to '唔好呀' as '捞' is a mishearing of '呀', and "
        "'唔食' to '唔饮' as the context is about drinking, not eating.",
    ),
    ProofTestCase(
        zhongwen="我不喝士多啤梨药水呀！",
        yuewen="我唔食士多啤梨药水呀！",
        yuewen_proofread="我唔饮士多啤梨药水呀！",
        note="Corrected '食' to '饮' as '饮' is the correct verb for drinking "
        "medicine, matching the meaning of '喝' in the 中文.",
    ),
    ProofTestCase(
        zhongwen="别哭了，不喝药水病不会好的",
        yuewen="唔好喊啦，唔食药唔会好㗎",
        yuewen_proofread="唔好喊啦，唔食药唔会好㗎",
        note="",
    ),
    ProofTestCase(
        zhongwen="乖乖，病好了妈妈带你去马尔代夫",
        yuewen="乖乖啲，病好咗妈妈大理马尔代夫",
        yuewen_proofread="乖乖啲，病好咗妈妈带你去马尔代夫",
        note="Corrected '大理' to '带你' as '带你' matches the meaning of '带你去' "
        "in the 中文, and '大理' is a likely mishearing.",
    ),
    ProofTestCase(
        zhongwen="真的吗？",
        yuewen="真嘅？",
        yuewen_proofread="真嘅？",
        note="",
    ),
    ProofTestCase(
        zhongwen="妈妈什么时候骗过你？",
        yuewen="妈妈几时呃过你呀？",
        yuewen_proofread="妈妈几时呃过你呀？",
        note="",
    ),
    ProofTestCase(
        zhongwen="乖，先把药水喝掉",
        yuewen="乖，食埋啲药水先啦",
        yuewen_proofread="乖，食埋啲药水先啦",
        note="",
    ),
]  # proof_test_cases_block_19
proof_test_cases_block_20 = [
    ProofTestCase(
        zhongwen="好呀，马尔代夫！",
        yuewen="嘻嘻，好嘢！",
        yuewen_proofread="嘻嘻，好嘢！",
        note="",
    ),
    ProofTestCase(
        zhongwen="马尔代夫！",
        yuewen="买二代夫，买二代夫！",
        yuewen_proofread="马尔代夫，马尔代夫！",
        note="Corrected '买二代夫' to '马尔代夫' as '买二代夫' is a mishearing of the "
        "place name '马尔代夫' (Maldives).",
    ),
    ProofTestCase(
        zhongwen="马尔代夫！",
        yuewen="买二代夫！",
        yuewen_proofread="马尔代夫！",
        note="Corrected '买二代夫' to '马尔代夫' as it is a clear mishearing of "
        "the place name '马尔代夫' (Maldives).",
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
    ProofTestCase(
        zhongwen="妈妈你看，我病好了！",
        yuewen="我好返喇！",
        yuewen_proofread="我好返喇！",
        note="",
    ),
    ProofTestCase(
        zhongwen="我把药都吃光了",
        yuewen="啲嘢所以我全部食晒喇",
        yuewen_proofread="啲药所以我全部食晒喇",
        note="Corrected '啲嘢' to '啲药' as the context is about taking "
        "medicine, and '药' is likely misheard as '嘢'.",
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
        yuewen_proofread="我饮下一格，又一格，又一格⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="就给我喝光了！",
        yuewen="吓，咪我饮晒㖞！",
        yuewen_proofread="吓，咪我饮晒㖞！",
        note="",
    ),
]  # proof_test_cases_block_21
proof_test_cases_block_22 = [
    ProofTestCase(
        zhongwen="喝光了就叻仔了！",
        yuewen="饮实就叻仔啦！",
        yuewen_proofread="饮晒就叻仔啦！",
        note="Corrected '饮实' to '饮晒' as '饮晒' means 'finished drinking' and "
        "matches the meaning of '喝光了' in the 中文.",
    ),
    ProofTestCase(
        zhongwen="喝光了就病好了！",
        yuewen="饮实就好返实啦！",
        yuewen_proofread="饮晒就好返实啦！",
        note="Corrected '饮实' to '饮晒' as '饮晒' means 'drink it all', "
        "matching the meaning of '喝光了' in the 中文.",
    ),
    ProofTestCase(
        zhongwen="妈妈呀⋯",
        yuewen="妈妈⋯",
        yuewen_proofread="妈妈⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="什么事？",
        yuewen="乜嘢啊？",
        yuewen_proofread="乜嘢啊？",
        note="",
    ),
    ProofTestCase(
        zhongwen="我们什么时候去马尔代夫？",
        yuewen="阿哋几时去马尔代夫啊？",
        yuewen_proofread="我哋几时去马尔代夫啊？",
        note="Corrected '阿哋' to '我哋' as '阿哋' is a likely mishearing of "
        "'我哋', which means 'we/us' in Cantonese.",
    ),
    ProofTestCase(
        zhongwen="什么马尔代夫？",
        yuewen="乜嘢马尔代夫啊？",
        yuewen_proofread="乜嘢马尔代夫啊？",
        note="",
    ),
    ProofTestCase(
        zhongwen="你说我病好带我去马尔代夫的呀！",
        yuewen="呢，你话我返就同我去马尔代夫㗎嘛！",
        yuewen_proofread="呢，你话我病好就同我去马尔代夫㗎嘛！",
        note="Inserted '病好' after '我' to match the meaning of '我病好' in the "
        "中文, as '返' is likely a mishearing of '病好'.",
    ),
    ProofTestCase(
        zhongwen="马尔代夫，椰林树影，水清沙幼⋯",
        yuewen="马尔代夫呢，耶南树影，水清沙游⋯",
        yuewen_proofread="马尔代夫呢，椰林树影，水清沙幼⋯",
        note="Corrected '耶南树影' to '椰林树影' and '水清沙游' to '水清沙幼' as both are "
        "likely mishearings of the standard phrase describing the "
        "Maldives.",
    ),
    ProofTestCase(
        zhongwen="座落于印度洋的世外桃源呀！",
        yuewen="助流于印度园嘅世外导演啦！",
        yuewen_proofread="座落于印度洋嘅世外桃源啦！",
        note="Corrected '助流于印度园嘅世外导演啦！' to '座落于印度洋嘅世外桃源啦！' as '助流' is a "
        "mishearing of '座落', '印度园' should be '印度洋', and '世外导演' should "
        "be '世外桃源', all matching the original meaning.",
    ),
    ProofTestCase(
        zhongwen="想不到你还有点文采",
        yuewen="啊，估唔到你几好文采㗎噃",
        yuewen_proofread="啊，估唔到你几好文采㗎噃",
        note="",
    ),
    ProofTestCase(
        zhongwen="说得不错呀！",
        yuewen="讲得几好听啊！妈妈",
        yuewen_proofread="讲得几好听啊！",
        note="Removed '妈妈' as it does not correspond to anything in the "
        "original sentence and is likely a transcription error.",
    ),
    ProofTestCase(
        zhongwen="我不是光说的呀，妈妈你说过⋯",
        yuewen="我唔系讲喇㗎，又系你话嘅，你话⋯",
        yuewen_proofread="我唔系讲喇㗎，又系你话嘅，你话⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="我病好了带我去马尔代夫的！",
        yuewen="我病好咗之日就同我去马尔代夫㗎，你讲过㗎！",
        yuewen_proofread="我病好咗之日就同我去马尔代夫㗎，你讲过㗎！",
        note="",
    ),
    ProofTestCase(
        zhongwen="我是说发了财就带你去",
        yuewen="我话发咗先至同你去㗎",
        yuewen_proofread="我话发咗先至同你去㗎",
        note="",
    ),
    ProofTestCase(
        zhongwen="不是的，妈妈你说我病好了就去的",
        yuewen="唔系㖞，妈妈，你话好咗就同我去㗎㖞",
        yuewen_proofread="唔系㖞，妈妈，你话好咗就同我去㗎㖞",
        note="",
    ),
    ProofTestCase(
        zhongwen="你分明讲过病好了就去马尔代夫的",
        yuewen="你明明讲过好返就同你去马尔代夫㗎㖞",
        yuewen_proofread="你明明讲过好返就同你去马尔代夫㗎㖞",
        note="",
    ),
    ProofTestCase(
        zhongwen="你讲过的！",
        yuewen="你讲过㗎！",
        yuewen_proofread="你讲过㗎！",
        note="",
    ),
    ProofTestCase(
        zhongwen="好了，别哭了",
        yuewen="得啦，得啦，唔好喊啦",
        yuewen_proofread="得啦，得啦，唔好喊啦",
        note="",
    ),
    ProofTestCase(
        zhongwen="带你去马尔代夫好了",
        yuewen="同你去马尔代夫啦",
        yuewen_proofread="同你去马尔代夫啦",
        note="",
    ),
    ProofTestCase(
        zhongwen="真的吗？　　对",
        yuewen="真嘅？　　系啊",
        yuewen_proofread="真嘅？　　系啊",
        note="",
    ),
    ProofTestCase(
        zhongwen="什么时候去？",
        yuewen="咁几时去啊？",
        yuewen_proofread="咁几时去啊？",
        note="",
    ),
    ProofTestCase(
        zhongwen="发财再说",
        yuewen="等我发咗先啰",
        yuewen_proofread="等我发咗先啰",
        note="",
    ),
    ProofTestCase(
        zhongwen="你早发财了⋯",
        yuewen="你发咗㗎喇，你发咗㗎喇⋯",
        yuewen_proofread="你发咗㗎喇，你发咗㗎喇⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="好了好了，发财了",
        yuewen="系喇系喇系喇，发咗喇",
        yuewen_proofread="系喇系喇系喇，发咗喇",
        note="",
    ),
    ProofTestCase(
        zhongwen="我们下个星期去，好了吧？",
        yuewen="下个礼拜同你去啦，得未啊？",
        yuewen_proofread="下个礼拜同你去啦，得未啊？",
        note="",
    ),
    ProofTestCase(
        zhongwen="太好了！",
        yuewen="好嘢！",
        yuewen_proofread="好嘢！",
        note="",
    ),
]  # proof_test_cases_block_22
proof_test_cases_block_23 = [
    ProofTestCase(
        zhongwen="麦唛，我是麦兜呀",
        yuewen="喂，麦麦啊，麦豆啊我系，即系呢",
        yuewen_proofread="喂，麦麦啊，麦兜啊我系，即系呢",
        note="Corrected '麦豆' to '麦兜' as '麦兜' is the correct name matching "
        "the 中文 '麦兜'.",
    ),
    ProofTestCase(
        zhongwen="是这样子的，我明天就飞了",
        yuewen="我明日就要飞喇",
        yuewen_proofread="我明日就要飞喇",
        note="",
    ),
    ProofTestCase(
        zhongwen="对　　⋯是吗？",
        yuewen="系啊　　⋯系咩？",
        yuewen_proofread="系啊　　⋯系咩？",
        note="",
    ),
    ProofTestCase(
        zhongwen="飞机餐很难吃的吗？",
        yuewen="飞机真好难食㗎？",
        yuewen_proofread="飞机餐好难食㗎？",
        note="Inserted '餐' after '飞机' to correct the mishearing; '飞机餐' "
        "means 'airplane meal', matching the meaning of the 中文.",
    ),
    ProofTestCase(
        zhongwen="也得吃呀！",
        yuewen="但点都要食㗎啦！",
        yuewen_proofread="但点都要食㗎啦！",
        note="",
    ),
    ProofTestCase(
        zhongwen="难道自己带东西上去吃吗？",
        yuewen="唔通自己带嘢上去食咩？",
        yuewen_proofread="唔通自己带嘢上去食咩？",
        note="",
    ),
    ProofTestCase(
        zhongwen="还在讲？",
        yuewen="仲讲？",
        yuewen_proofread="仲讲？",
        note="",
    ),
    ProofTestCase(
        zhongwen="快点帮手执行李",
        yuewen="哦，快啲嚟执埋啲行李先啦，哦",
        yuewen_proofread="哦，快啲嚟执埋啲行李先啦，哦",
        note="",
    ),
    ProofTestCase(
        zhongwen="跟我向他们说，我明天去马尔代夫了",
        yuewen="你帮我话畀佢哋知，我明日去买热带裤薄",
        yuewen_proofread="你帮我话畀佢哋知，我明日去马尔代夫喇",
        note="Corrected '买热带裤薄' to '马尔代夫喇' as '买热带裤薄' is a mishearing of "
        "'马尔代夫' (Maldives), which matches the intended meaning in the "
        "中文.",
    ),
    ProofTestCase(
        zhongwen="那边蓝天白云，椰林树影⋯",
        yuewen="𠮶度蓝天五百云，夜临雪⋯",
        yuewen_proofread="𠮶度蓝天白云，椰林树影⋯",
        note="Corrected '五百云' to '白云' as it is a mishearing, and '夜临雪' to "
        "'椰林树影' to match the intended meaning and sound of the "
        "original phrase.",
    ),
    ProofTestCase(
        zhongwen="还在讲！",
        yuewen="水清净沙有！",
        yuewen_proofread="",
        note="Cleared as '水清净沙有！' bears no resemblance to the original "
        "phrase '还在讲！' and is clearly a complete transcription "
        "failure.",
    ),
    ProofTestCase(
        zhongwen="来了！",
        yuewen="我嚟紧㗎喇！",
        yuewen_proofread="我嚟紧㗎喇！",
        note="",
    ),
    ProofTestCase(
        zhongwen="要执行李了，回来再跟你说吧",
        yuewen="我要执行你喇，返嚟先再同你倾过啦",
        yuewen_proofread="我要执行李喇，返嚟先再同你倾过啦",
        note="Corrected '执行你' to '执行李' as '执行李' (to pack luggage) matches "
        "the meaning of the 中文, while '执行你' is a mishearing.",
    ),
    ProofTestCase(
        zhongwen="再见！",
        yuewen="拜拜！",
        yuewen_proofread="拜拜！",
        note="",
    ),
]  # proof_test_cases_block_23
proof_test_cases_block_24 = [
    ProofTestCase(
        zhongwen="妈妈，我得把出世纸带着吗？",
        yuewen="哎哟，妈妈，我系咪要带埋出世纸去㗎？",
        yuewen_proofread="哎哟，妈妈，我系咪要带埋出世纸去㗎？",
        note="",
    ),
    ProofTestCase(
        zhongwen="也要的",
        yuewen="都要㗎",
        yuewen_proofread="都要㗎",
        note="",
    ),
    ProofTestCase(
        zhongwen="那么成绩表呢？",
        yuewen="咁成绩表呢？",
        yuewen_proofread="咁成绩表呢？",
        note="",
    ),
    ProofTestCase(
        zhongwen="成绩表就不用了",
        yuewen="成绩表又唔使",
        yuewen_proofread="成绩表又唔使",
        note="",
    ),
    ProofTestCase(
        zhongwen="太好了！吓得我！",
        yuewen="好嘢！吓得我啊！咁都好啲",
        yuewen_proofread="好嘢！吓得我啊！咁都好啲",
        note="",
    ),
]  # proof_test_cases_block_24
proof_test_cases_block_25 = [
    ProofTestCase(
        zhongwen="找到了！",
        yuewen="揾到喇！",
        yuewen_proofread="揾到喇！",
        note="",
    ),
    ProofTestCase(
        zhongwen="妈妈你替我收好它别抛掉",
        yuewen="竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然",
        yuewen_proofread="",
        note="Cleared as the provided 粤文 is a repeated string of '竟然' and "
        "bears no resemblance to the original phrase '妈妈你替我收好它别抛掉', "
        "indicating a complete transcription failure.",
    ),
]  # proof_test_cases_block_25
proof_test_cases_block_26 = [
    ProofTestCase(
        zhongwen="早机去，晚机返",
        yuewen="早机去，晚机返",
        yuewen_proofread="早机去，晚机返",
        note="",
    ),
    ProofTestCase(
        zhongwen="妈妈说这样才够精明",
        yuewen="妈妈话噉先最著数",
        yuewen_proofread="妈妈话噉先最著数",
        note="",
    ),
    ProofTestCase(
        zhongwen="就这样⋯",
        yuewen="就系噉样⋯",
        yuewen_proofread="就系噉样⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="我过了我小时候最精明⋯",
        yuewen="我过咗我小时候最著数⋯",
        yuewen_proofread="我过咗我小时候最著数⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="最美丽的一天",
        yuewen="最完美嘅一日",
        yuewen_proofread="最完美嘅一日",
        note="",
    ),
    ProofTestCase(
        zhongwen="依你说，纸是否可以包着鸡呢？",
        yuewen="噉你话，纸包唔包得绝鸡呢？",
        yuewen_proofread="噉你话，纸包唔包得住鸡呢？",
        note="Corrected '绝鸡' to '住鸡' as '住' is the correct word for 'wrap' "
        "or 'cover' in this context, while '绝' is likely a "
        "mishearing.",
    ),
    ProofTestCase(
        zhongwen="也可以的⋯",
        yuewen="都得嘅⋯",
        yuewen_proofread="都得嘅⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="特别是小小一块的",
        yuewen="尤其系细细旧𠮶啲",
        yuewen_proofread="尤其系细细旧𠮶啲",
        note="",
    ),
]  # proof_test_cases_block_26
proof_test_cases_block_27 = [
    ProofTestCase(
        zhongwen="妈妈晚安！",
        yuewen="妈妈，做头！",
        yuewen_proofread="",
        note="Cleared as '妈妈，做头！' bears no resemblance to the original "
        "phrase '妈妈晚安！' and is clearly a complete transcription "
        "failure.",
    ),
]  # proof_test_cases_block_27
proof_test_cases_block_28 = [
    ProofTestCase(
        zhongwen="最新消息",
        yuewen="啱啱收到消息",
        yuewen_proofread="啱啱收到消息",
        note="",
    ),
    ProofTestCase(
        zhongwen="奥运滑浪风帆选手李丽珊五场四胜",
        yuewen="奥运滑浪风帆选手李丽珊以五场四胜嘅结果",
        yuewen_proofread="奥运滑浪风帆选手李丽珊以五场四胜嘅结果",
        note="",
    ),
    ProofTestCase(
        zhongwen="夺得香港历史上第一面奥运金牌！",
        yuewen="夺取香港历史上第一面奥运金牌！",
        yuewen_proofread="夺取香港历史上第一面奥运金牌！",
        note="",
    ),
    ProofTestCase(
        zhongwen="消息说当李丽珊获悉自己稳夺金牌后",
        yuewen="消息话李丽珊喺知道自己稳夺奥运金牌之后",
        yuewen_proofread="消息话李丽珊喺知道自己稳夺奥运金牌之后",
        note="",
    ),
    ProofTestCase(
        zhongwen="激动地对在场记者表示她今次的成绩⋯",
        yuewen="好激动噉同在场嘅记者讲今次佢嘅成绩⋯",
        yuewen_proofread="好激动噉同在场嘅记者讲今次佢嘅成绩⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="足以证明香港运动员不是腊鸭！",
        yuewen="可以证明到香港嘅运动员唔系𫚭鸭！",
        yuewen_proofread="可以证明到香港嘅运动员唔系腊鸭！",
        note="Corrected '𫚭鸭' to '腊鸭' as '腊鸭' is the correct term and "
        "matches the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="对不起，应该　　是垃圾，不是腊鸭！",
        yuewen="各位对唔住，应该系垃圾，唔系𫚭鸭！",
        yuewen_proofread="各位对唔住，应该系垃圾，唔系腊鸭！",
        note="Corrected '𫚭鸭' to '腊鸭' as '腊鸭' is the correct term and "
        "matches the intended meaning.",
    ),
    ProofTestCase(
        zhongwen="对不起，应该　　不是垃圾，也不是腊鸭！",
        yuewen="对唔住，应该系唔系垃圾，亦都唔系𫚭鸭！",
        yuewen_proofread="对唔住，应该系唔系垃圾，亦都唔系腊鸭！",
        note="Corrected '𫚭鸭' to '腊鸭' as '腊鸭' is the correct term and "
        "matches the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="特别报告完毕",
        yuewen="特别报个原不",
        yuewen_proofread="特别报告完毕",
        note="Corrected '报个原不' to '报告完毕' as it is a clear mishearing of "
        "the intended phrase.",
    ),
]  # proof_test_cases_block_28
proof_test_cases_block_29 = [
    ProofTestCase(
        zhongwen="妈妈好像又有计了",
        yuewen="咦，妈妈好似又有计噉噃",
        yuewen_proofread="咦，妈妈好似又有计噉噃",
        note="",
    ),
    ProofTestCase(
        zhongwen="靓仔，好运，叻仔⋯",
        yuewen="靓仔，好运，叻仔呀⋯",
        yuewen_proofread="靓仔，好运，叻仔呀⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="好像都没希望了",
        yuewen="睇嚟都唔多靠得住",
        yuewen_proofread="睇嚟都唔多靠得住",
        note="",
    ),
    ProofTestCase(
        zhongwen="是不是可以靠手瓜呢？",
        yuewen="哗，好唔好靠下个手瓜噉呢？",
        yuewen_proofread="哗，好唔好靠下个手瓜噉呢？",
        note="",
    ),
    ProofTestCase(
        zhongwen="于是，一个梦还没醒⋯",
        yuewen="于是，一个梦都未醒⋯",
        yuewen_proofread="于是，一个梦都未醒⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="我又得到另一个梦",
        yuewen="我又得到另外一个梦",
        yuewen_proofread="我又得到另外一个梦",
        note="",
    ),
    ProofTestCase(
        zhongwen="应该是脚瓜",
        yuewen="系咪应该系脚瓜之争",
        yuewen_proofread="系咪应该系脚瓜之争",
        note="",
    ),
    ProofTestCase(
        zhongwen="我知道一点也不容易",
        yuewen="我知道一啲都唔容易",
        yuewen_proofread="我知道一啲都唔容易",
        note="",
    ),
    ProofTestCase(
        zhongwen="我知道要找到黎根绝对不容易",
        yuewen="我知道要揾到励根绝对唔容易",
        yuewen_proofread="我知道要揾到黎根绝对唔容易",
        note="Corrected '励根' to '黎根' as '黎根' is the correct name matching "
        "the 中文, while '励根' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="我知道要他收我做徒弟更加不容易",
        yuewen="我知道要佢收我做徒弟更加唔容易",
        yuewen_proofread="我知道要佢收我做徒弟更加唔容易",
        note="",
    ),
]  # proof_test_cases_block_29
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
        note="Corrected '来紧' to '黎根' and '度徒弟' to '做徒弟' as both are likely "
        "mishearings; '黎根' is a name and '做徒弟' matches the meaning of "
        "'做徒弟' in the 中文.",
    ),
    ProofTestCase(
        zhongwen="无论几辛苦，我一定要得到奥运金牌！",
        yuewen="无论几辛苦，我一定要捞到奥运金牌！",
        yuewen_proofread="无论几辛苦，我一定要攞到奥运金牌！",
        note="Corrected '捞到' to '攞到' as '攞到' is the correct Cantonese verb "
        "for 'to get/obtain', matching the meaning of '得到'.",
    ),
]  # proof_test_cases_block_30
proof_test_cases_block_31 = [
    ProofTestCase(
        zhongwen="当我站在奥运会颁奖台上",
        yuewen="三张堂上面",
        yuewen_proofread="",
        note="Cleared as '三张堂上面' bears no resemblance to the original "
        "phrase '当我站在奥运会颁奖台上' and is clearly a complete transcription "
        "failure.",
    ),
    ProofTestCase(
        zhongwen="我会举起金牌跟全世界说：",
        yuewen="系今排同全世界讲：",
        yuewen_proofread="举起金牌同全世界讲：",
        note="Replaced '系今排' with '举起金牌' as '今排' is a mishearing of '金牌', "
        "which matches the meaning of the original sentence about "
        "raising a gold medal.",
    ),
]  # proof_test_cases_block_31
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
        note="Corrected '盛洁' to '圣洁' as '圣洁' is the correct term for "
        "'holy' or 'sacred', matching the meaning in the 中文.",
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
        note="Corrected '引用' to '孕育' as '孕育' is the correct term for "
        "'nurtured' or 'gave rise to', matching the meaning in the "
        "中文.",
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
