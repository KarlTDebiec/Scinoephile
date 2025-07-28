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
        difficulty=2,
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
        difficulty=2,
    ),
    ProofTestCase(
        zhongwen="经好彩酒家左转花园街乐园牛丸王⋯",
        yuewen="经过好彩走家再左转返出花园街乐园牛园望对上⋯",
        yuewen_proofread="经过好彩酒家再左转返出花园街乐园牛丸王对上⋯",
        note="Corrected '走家' to '酒家' and '牛园望' to '牛丸王' as these are "
        "likely mishearings of the correct place names in the "
        "context.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="更正一下：",
        yuewen="都系唔好：",
        yuewen_proofread="都系唔好：",
        note="",
        include_in_prompt=True,
        difficulty=2,
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
        difficulty=2,
    ),
    ProofTestCase(
        zhongwen="直出亚皆老街跨过火车桥右转太平道",
        yuewen="都系出返去阿街路街飞过火车桥右转入太平道",
        yuewen_proofread="都系出返去亚皆老街飞过火车桥右转入太平道",
        note="Corrected '阿街路街' to '亚皆老街' as it is a mishearing of the "
        "street name '亚皆老街'.",
        include_in_prompt=True,
        difficulty=2,
    ),
    ProofTestCase(
        zhongwen="再右拐窝打老道向女人街方向飞⋯",
        yuewen="再右转抹返出去窝打炉道向女人街方向飞下下⋯",
        yuewen_proofread="再右转抹返出去窝打老道向女人街方向飞下下⋯",
        note="Corrected '窝打炉道' to '窝打老道' as '窝打老道' is the correct street "
        "name, matching the 中文.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="飞呀，飞⋯",
        yuewen="飞下，飞下⋯",
        yuewen_proofread="飞下，飞下⋯",
        note="",
        include_in_prompt=True,
        difficulty=2,
    ),
    ProofTestCase(
        zhongwen="胶兜最后飞进广华医院候产房",
        yuewen="最后胶兜飞咗入广华医院嘅后产房",
        yuewen_proofread="最后胶兜飞咗入广华医院嘅候产房",
        note="Corrected '后产房' to '候产房' as '候产房' (waiting room for "
        "childbirth) matches the meaning in the 中文, while '后产房' is "
        "likely a mishearing.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="也就是在麦太右边额角上⋯",
        yuewen="亦即系麦太右边云晶对上⋯",
        yuewen_proofread="亦即系麦太右边魂精对上⋯",
        note="Corrected '云晶' to '魂精' as '魂精' is a valid Cantonese term for "
        "'temple' and matches the meaning of '额角' in the 中文.",
        include_in_prompt=True,
        difficulty=2,
    ),
    ProofTestCase(
        zhongwen="更正：左边额角上⋯",
        yuewen="都系唔好：左边云晶对上⋯",
        yuewen_proofread="都系唔好：左边魂精对上⋯",
        note="Corrected '云晶' to '魂精' as '魂精' is a valid Cantonese term for "
        "'temple' and matches the meaning of '额角' in the 中文.",
        difficulty=1,
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
        difficulty=2,
    ),
    ProofTestCase(
        zhongwen="于是向额角上的胶兜许愿",
        yuewen="于是向云晶对上嘅胶兜许愿",
        yuewen_proofread="于是向魂精对上嘅胶兜许愿",
        note="Corrected '云晶' to '魂精' as '魂精' is a valid Cantonese term for "
        "'temple' (额角), matching the meaning in the 中文.",
        difficulty=1,
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
        difficulty=2,
    ),
    ProofTestCase(
        zhongwen="唔聪明唔靓仔也算了，只要福星高照",
        yuewen="就算唔系咁聪明同咁靓仔，只要复星高照",
        yuewen_proofread="就算唔系咁聪明同咁靓仔，只要福星高照",
        note="Corrected '复星高照' to '福星高照' as '福星高照' is the correct idiom "
        "meaning 'blessed with good fortune', matching the 中文.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="一世够运，逢凶化吉！",
        yuewen="一世救运，乜嘢事都逢凶化㗎喇！",
        yuewen_proofread="一世够运，乜嘢事都逢凶化㗎喇！",
        note="Corrected '救运' to '够运' as '够运' is the correct term for being "
        "lucky, matching the original meaning.",
        include_in_prompt=True,
        difficulty=2,
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
        difficulty=2,
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
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="嘀督？嘀督，就是答应了",
        yuewen="滴嘟？滴嘟㖞，即系应承啦",
        yuewen_proofread="嘀督？嘀督㖞，即系应承啦",
        note="Corrected '滴嘟' to '嘀督' to match the intended sound and "
        "meaning of '嘀督' as a phonetic rendering of '嘀督' (答应了).",
        include_in_prompt=True,
        difficulty=2,
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
        "actor's name, matching the meaning in the 中文.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="为了纪念这赐福的胶兜",
        yuewen="为咗纪念呢个赤幅嘅胶兜",
        yuewen_proofread="为咗纪念呢个赐福嘅胶兜",
        note="Corrected '赤幅' to '赐福' as '赐福' (bestowing blessing) matches "
        "the meaning of the 中文, while '赤幅' is a likely mishearing.",
        difficulty=1,
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
        difficulty=2,
    ),
    ProofTestCase(
        zhongwen="怎么小腿粗起来了？",
        yuewen="个脚刮囊粗咗咁多呀？",
        yuewen_proofread="个脚瓜囊粗咗咁多呀？",
        note="Corrected '脚刮囊' to '脚瓜囊' as '脚瓜囊' is the correct Cantonese "
        "term for 'calf', matching the meaning of '小腿'.",
        include_in_prompt=True,
        difficulty=2,
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
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="旧中侨国货楼上的⋯",
        yuewen="旧中桥百货公司楼上𠮶间⋯",
        yuewen_proofread="旧中侨百货公司楼上𠮶间⋯",
        note="Corrected '中桥' to '中侨' as '中侨' is the correct name, matching "
        "the 中文 '中侨'.",
        difficulty=1,
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
        note="Corrected '诗诗优良' to '师资优良' as '师资' is the correct term for "
        "teaching staff, matching the meaning in the 中文.",
        difficulty=1,
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
        difficulty=1,
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
        difficulty=2,
    ),
    ProofTestCase(
        zhongwen="蛋挞！　　蛋挞！",
        yuewen="大湖荒岩宅",
        yuewen_proofread="",
        note="Cleared as '大湖荒岩宅' bears no resemblance to the original "
        "phrase '蛋挞！ 蛋挞！' and is clearly a complete transcription "
        "failure.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="荔芋火鸭礼！　　荔芋火鸭礼！",
        yuewen="湾吉校坟交涉设",
        yuewen_proofread="",
        note="Cleared as '湾吉校坟交涉设' bears no resemblance to the original "
        "phrase '荔芋火鸭礼！　　荔芋火鸭礼！' and is clearly a complete "
        "transcription failure.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="也不能忘记校训九十八！",
        yuewen="都唔好湾吉校坟交涉白！",
        yuewen_proofread="",
        note="Cleared as '都唔好湾吉校坟交涉白！' bears no resemblance to the "
        "original phrase '也不能忘记校训九十八！' and is clearly a pure "
        "artifact.",
        include_in_prompt=True,
        difficulty=2,
    ),
    ProofTestCase(
        zhongwen="好！各位同学⋯",
        yuewen="𠮶个位同学⋯",
        yuewen_proofread="𠮶个位同学⋯",
        note="",
        include_in_prompt=True,
        difficulty=2,
    ),
    ProofTestCase(
        zhongwen="今天的早会主要是跟大家分享",
        yuewen="今次座会系要同大家分享",
        yuewen_proofread="今次早会系要同大家分享",
        note="Corrected '座会' to '早会' as '早会' is the correct term for "
        "'morning assembly', matching the meaning in the 中文.",
        difficulty=1,
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
        note="Corrected '好逗利' to '好烂' as '烂' matches the meaning of '很烂' "
        "in the 中文, while '逗利' is likely a mishearing.",
        difficulty=1,
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
        yuewen="⋯仲有一个好疼我哋",
        yuewen_proofread="⋯仲有一个好疼我哋",
        note="",
    ),
    ProofTestCase(
        zhongwen="就是有点游魂的Miss Chan",
        yuewen="不过就有少少失魂嘅班主有Miss Chan",
        yuewen_proofread="不过就有少少游魂嘅班主有Miss Chan",
        note="Corrected '失魂' to '游魂' as '游魂' matches the meaning of '游魂' "
        "in the 中文, while '失魂' is a likely mishearing.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="她的志愿是做第二个王菲",
        yuewen="佢嘅志愿系做下一个王妃",
        yuewen_proofread="佢嘅志愿系做下一个王菲",
        note="Corrected '王妃' to '王菲' as '王菲' is the correct name of the "
        "singer, matching the meaning in the 中文.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="做第二个陈慧琳也可以",
        yuewen="或者系做下一个陈维林都得",
        yuewen_proofread="或者系做下一个陈慧琳都得",
        note="Corrected '陈维林' to '陈慧琳' as '陈慧琳' is the correct name, "
        "matching the meaning in the 中文.",
        difficulty=1,
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
        "the 中文.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="亚辉同学！　　到！",
        yuewen="阿辉同学！　　到！",
        yuewen_proofread="阿辉同学！　　到！",
        note="",
    ),
    ProofTestCase(
        zhongwen="菇时同学！　　到！",
        yuewen="Boosie同学！　　到！",
        yuewen_proofread="菇时同学！　　到！",
        note="Corrected 'Boosie' to '菇时' as 'Boosie' is a mishearing of "
        "the name '菇时'.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="得巴同学！　　到！",
        yuewen="德巴同学！　　到！",
        yuewen_proofread="得巴同学！　　到！",
        note="Corrected '德巴' to '得巴' as it matches the original name in "
        "the 中文 and is likely a mishearing.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="阿May同学！　　到！",
        yuewen="阿May同学！　　到！",
        yuewen_proofread="阿May同学！　　到！",
        note="",
    ),
    ProofTestCase(
        zhongwen="阿June同学！　　到！",
        yuewen="阿June同学！　　到！",
        yuewen_proofread="阿June同学！　　到！",
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
        yuewen_proofread="菇时同学！　　到！",
        note="Corrected '川明' to '菇时' as it is a mishearing of the name in "
        "the original text.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="还有谁没点过吗？",
        yuewen="好，仲有边个未点？猫",
        yuewen_proofread="好，仲有边个未点？",
        note="Removed '猫' at the end as it is likely a mishearing or "
        "extraneous word not present in the original meaning.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="麦兜！",
        yuewen="噢！",
        yuewen_proofread="",
        note="Cleared as '噢！' bears no resemblance to the original phrase "
        "'麦兜！' and is clearly a complete transcription failure.",
        include_in_prompt=True,
        difficulty=2,
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
        note="Corrected '仁住仁住' to '印住印住' as '印住' (feeling pressed or "
        "uneasy) is a common Cantonese expression for a feeling in "
        "the heart, matching the sense of '觉得' in the 中文, while '仁住' "
        "is likely a mishearing.",
        difficulty=1,
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
        yuewen="点解橙叫「Orange」呢？",
        yuewen_proofread="点解橙叫「Orange」呢？",
        note="",
    ),
    ProofTestCase(
        zhongwen="妈妈说吃橙可通大便",
        yuewen="妈妈话食橙会通大变",
        yuewen_proofread="妈妈话食橙会通大便",
        note="Corrected '大变' to '大便' as '大便' is the correct term for "
        "'bowel movement', matching the meaning in the 中文.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="「疴」这个我明白，可是「烂﹣煮」呢？",
        yuewen="「噢」呢个我明白，但系「橙」呢？",
        yuewen_proofread="",
        note="Cleared as '「噢」呢个我明白，但系「橙」呢？' bears no resemblance to the "
        "original phrase '「疴」这个我明白，可是「烂﹣煮」呢？' and is clearly a "
        "complete transcription failure.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="还有这个「芭﹣娜﹣娜」香蕉",
        yuewen="仲有呢个啊「芭拉娜」啊，香蕉啊",
        yuewen_proofread="仲有呢个「芭﹣娜﹣娜」啊，香蕉啊",
        note="Corrected '芭拉娜' to '芭娜娜' as '芭娜娜' is the correct "
        "transliteration for 'banana', matching styling of the 中文.",
        difficulty=1,
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="为什么雨伞又会是「暗﹣芭﹣娜﹣娜」呢？",
        yuewen="点解雨姐会叫做「暗芭拉娜」呢？",
        yuewen_proofread="点解雨姐会叫做「暗芭娜娜」呢？",
        note="Corrected '暗芭拉娜' to '暗芭娜娜' as '芭娜娜' is the correct "
        "transliteration for 'banana', matching the intended pun in "
        "the 中文.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="我「暗」的「暗」掉一条蕉",
        yuewen="嗱，我「暗」啦，噉我「暗」𠮶条香蕉",
        yuewen_proofread="嗱，我「暗」啦，噉我「暗」𠮶条蕉",
        note="Corrected '香蕉' to '蕉' as '蕉' is the colloquial Cantonese "
        "term for 'banana' and matches the meaning of '一条蕉' in the "
        "中文.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="至多是疴烂煮，怎么会下起雨来呢？",
        yuewen="至多会Orange啫，点解会搞到落雨呢？",
        yuewen_proofread="至多会屙烂煮啫，点解会搞到落雨呢？",
        note="Corrected 'Orange' to '屙烂煮' as '屙烂煮' (diarrhea) is the "
        "correct term matching the meaning of the 中文, while 'Orange' "
        "is a mishearing.",
        difficulty=1,
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
        difficulty=1,
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
        yuewen_proofread="我哋一班同学仔放咗学都经常光顾",
        note="Corrected '系傍陈' to '光顾' as '光顾' matches the meaning of '光顾' "
        "in the 中文, while '系傍陈' is likely a mishearing.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="鱼蛋粗面，麻烦你　　粗面买光了",
        yuewen="唔该，鱼蛋粗啊　　冇粗面噃",
        yuewen_proofread="唔该，鱼蛋粗啊　　冇粗面噃",
        note="",
    ),
    ProofTestCase(
        zhongwen="那样子⋯来碗鱼蛋河粉吧　　鱼蛋买光了",
        yuewen="噉啊⋯要碗鱼蛋好啊⋯　　冇鱼蛋噃",
        yuewen_proofread="噉啊⋯要碗鱼蛋河粉啊⋯　　冇鱼蛋噃",
        note="Added '河粉' after '鱼蛋' to match the intended meaning of "
        "'鱼蛋河粉' in the 中文; '好' was likely a mishearing of '河'.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="那么⋯金钱肚粗面好了　　粗面买光了",
        yuewen="噉啊⋯要金钱透粗啊⋯　　冇粗面噃",
        yuewen_proofread="噉啊⋯要金钱肚粗面啊⋯　　冇粗面噃",
        note="Corrected '金钱透粗' to '金钱肚粗面' as '金钱肚粗面' is the correct dish "
        "name, matching the meaning in the 中文.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="那么要鱼蛋油面吧　　鱼蛋买光了",
        yuewen="噉啊咁要鱼蛋油面啊　　冇鱼蛋噃",
        yuewen_proofread="噉啊咁要鱼蛋油面啊　　冇鱼蛋噃",
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
        yuewen_proofread="噉要墨鱼丸粗啊　　冇粗面噃",
        note="Corrected '蜜丸' to '墨鱼丸' as '墨鱼丸' is the correct term for "
        "'墨鱼丸' (cuttlefish ball), matching the 中文.",
        difficulty=1,
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
        note="Corrected '鱼蛋奶' to '鱼蛋濑' as '鱼蛋濑' (fish ball lai fun) "
        "matches the intended meaning, while '鱼蛋奶' is likely a "
        "mishearing.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="麦兜呀，鱼蛋跟粗面都买光了",
        yuewen="麦兜啊，佢哋啲鱼蛋同粗面卖晒㗎啦",
        yuewen_proofread="麦兜啊，鱼蛋同粗面卖晒㗎啦",
        note="Removed '佢哋啲' as it is a mishearing and not present in the "
        "original meaning; the sentence should directly address 麦兜 "
        "and state that the items are sold out.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="即是所有鱼蛋跟粗面的配搭都没了",
        yuewen="即系所有要鱼蛋或者粗面嘅配搭都冇㗎啦",
        yuewen_proofread="即系所有要鱼蛋或者粗面嘅配搭都冇㗎啦",
        note="",
    ),
    ProofTestCase(
        zhongwen="没有那些配搭吗？",
        yuewen="噢，冇𠮶啲配搭啊？",
        yuewen_proofread="噢，冇𠮶啲配搭啊？",
        note="",
    ),
    ProofTestCase(
        zhongwen="麻烦你，净要鱼蛋吧　　鱼蛋买光了",
        yuewen="噉唔该，净鱼蛋啊　　冇鱼蛋噃",
        yuewen_proofread="噉唔该，净鱼蛋啊　　冇鱼蛋噃",
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
        yuewen_proofread="嗰阵我无忧无虑，冇乜所谓﹣﹣",
        note="Corrected '果只' to '嗰阵' as '嗰阵' (that time) matches the "
        "meaning of '那时候', while '果只' is likely a mishearing.",
        difficulty=1,
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
        yuewen_proofread="麦兜，射呀！",
        note="Corrected '转身食啊' to '射呀' as '射呀' matches the meaning of "
        "'shoot!' in the 中文, while '转身食啊' is likely a mishearing.",
        difficulty=1,
    ),
]  # proof_test_cases_block_5
proof_test_cases_block_6 = [
    ProofTestCase(
        zhongwen="看着自己每天疴烂煮⋯",
        yuewen="睇住自己日日柯能处⋯",
        yuewen_proofread="睇住自己日日疴烂煮⋯",
        note="Corrected '柯能处' to '疴烂煮' as '疴烂煮' is a phonetic match and "
        "the correct phrase for the context of the 中文.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="每天长肉⋯",
        yuewen="日日掌肉⋯",
        yuewen_proofread="日日长肉⋯",
        note="Corrected '掌肉' to '长肉' as '长肉' (to gain weight) matches the "
        "meaning of the 中文, while '掌肉' is likely a mishearing.",
        difficulty=1,
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
        "'Miss Chan', matching the original name in the 中文.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="我时常想着学习",
        yuewen="我成日想学习",
        yuewen_proofread="我成日想学习",
        note="",
    ),
    ProofTestCase(
        zhongwen="可每次我总唱成「疴」什么什么的⋯",
        yuewen="但系唱嚟唱去都系「阿伦厨」，咁「Ballana」噉⋯",
        yuewen_proofread="但系唱嚟唱去都系「疴乜乜」噉⋯",
        note="Corrected '阿伦厨' to '疴乜乜' as '疴乜乜' is a plausible mishearing "
        "and matches the meaning of '疴什么什么的' in the 中文.",
        difficulty=1,
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
        zhongwen="一、二、三、四、五、六、七⋯",
        yuewen="1234567⋯",
        yuewen_proofread="1234567⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="多劳多得！",
        yuewen="多喽多得！",
        yuewen_proofread="多劳多得！",
        note="Corrected '多喽' to '多劳' as '多劳多得' is the correct phrase "
        "meaning 'more work, more gain', and '喽' is a mishearing of "
        "'劳'.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="星期一至星期七⋯多劳多得！",
        yuewen="星期一至星期七⋯多喽多得！",
        yuewen_proofread="星期一至星期七⋯多劳多得！",
        note="Corrected '多喽多得' to '多劳多得' as '多劳多得' is the correct phrase "
        "meaning 'more work, more gain', and '喽' is a mishearing of "
        "'劳'.",
        difficulty=1,
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
        yuewen_proofread="www.麦太世界.com",
        note="Corrected 'mcticege' to '麦太世界' to match the style of the 中文.",
        include_in_prompt=True,
        difficulty=2,
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
        "matching the meaning in the 中文.",
        difficulty=1,
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
        yuewen="然后将鸡包纸一反反转",
        yuewen_proofread="然后将鸡包纸一反反转",
        note="",
    ),
    ProofTestCase(
        zhongwen="这一味纸包鸡就完成了，很容易是吧？",
        yuewen="呢味自包鸡就完成喇，系咪好易整啦？",
        yuewen_proofread="呢味纸包鸡就完成喇，系咪好易整啦？",
        note="Corrected '自包鸡' to '纸包鸡' as '纸包鸡' is the correct dish name, "
        "matching the meaning in the 中文.",
        difficulty=1,
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
        yuewen_proofread="而家要教大家一味几别致嘅小菜﹣",
        note="Corrected '间阵' to '而家' as '而家' means 'now', matching '现在', "
        "and '别节' to '别致' as '别致' is the correct term for 'unique' or "
        "'special'.",
    ),
    ProofTestCase(
        zhongwen="包鸡纸包鸡包纸包鸡",
        yuewen="包鸡子包鸡包子包鸡",
        yuewen_proofread="包鸡纸包鸡包纸包鸡",
        note="Corrected '鸡子' and '包子' to '鸡纸' and '包纸' respectively, as "
        "'纸' is the correct word in the repeated phrase '纸包鸡' "
        "(paper-wrapped chicken), matching the 中文.",
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
        "'鸡包纸' (the paper used to wrap the chicken), and changed '牛鸡' "
        "to '嗰块鸡' as '牛鸡' is likely a mishearing of '嗰块鸡' (that piece "
        "of chicken).",
    ),
    ProofTestCase(
        zhongwen="再依照这样子用包鸡纸把它包起",
        yuewen="然后再好似噉样将包鸡子包包包包包包住佢",
        yuewen_proofread="然后再好似噉样将包鸡纸包包包包包包住佢",
        note="Corrected '包鸡子' to '包鸡纸' as '包鸡纸' (greaseproof paper) "
        "matches the meaning in the 中文, while '包鸡子' is likely a "
        "mishearing.",
    ),
    ProofTestCase(
        zhongwen="一味「包鸡纸包鸡包纸包鸡」完成了！",
        yuewen="咁一味「包鸡子包鸡包子包鸡」就完成喇！",
        yuewen_proofread="咁一味「包鸡纸包鸡包纸包鸡」就完成喇！",
        note="Corrected '包鸡子包鸡包子包鸡' to '包鸡纸包鸡包纸包鸡' as '纸' is the correct "
        "word in the dish name, matching the original phrase.",
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
        note="Removed the extra '包鸡' at the end as it is likely a "
        "mishearing and does not correspond to the original "
        "repetition pattern in the 中文.",
    ),
    ProofTestCase(
        zhongwen="包鸡包鸡包纸包鸡",
        yuewen="包包鸡纸包鸡包纸包鸡",
        yuewen_proofread="包鸡包鸡包纸包鸡",
        note="Corrected '包包鸡纸包鸡包纸包鸡' to '包鸡包鸡包纸包鸡' to match the repetition "
        "and order of '包鸡' and '包纸包鸡' in the 中文; the extra '包' and "
        "word order were likely transcription errors.",
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
        yuewen="再包包包包，包鸡包纸包纸，纸纸纸纸",
        yuewen_proofread="再包包包，纸纸纸",
        note="Removed extra repetitions and corrected '包鸡包纸包纸' to match "
        "the intended repetition of '包' and '纸' as in the 中文; the "
        "original had likely misheard or over-transcribed the words.",
    ),
    ProofTestCase(
        zhongwen="纸包纸，纸包鸡，鸡包纸，纸包鸡⋯",
        yuewen="纸包纸，纸包鸡，包鸡纸，纸包鸡，鸡鸡鸡，纸纸纸再包鸡鸡⋯",
        yuewen_proofread="纸包纸，纸包鸡，鸡包纸，纸包鸡，鸡鸡鸡，纸纸纸再包鸡鸡⋯",
        note="Corrected '包鸡纸' to '鸡包纸' to match the pattern and likely "
        "intended word order.",
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
        yuewen_proofread="佢长大后发咗！",
        note="Added '后' after '长大' to match the meaning of '长大后' in the "
        "中文, as its omission is likely a transcription error.",
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
        yuewen="唔得都要得字幕由Amara.org",
        yuewen_proofread="",
        note="Cleared as '唔得都要得字幕由Amara.org' contains unrelated content "
        "('字幕由Amara.org') and does not correspond to the original "
        "phrase '没有不成的事'.",
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
        "meaning in the 中文, while '同事手' is a likely mishearing.",
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
        yuewen="我试过好努力咁读书，但系⋯",
        yuewen_proofread="我试过好努力咁读书，但系⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="可是⋯我仍然有梦",
        yuewen="但系⋯我仲可以发梦",
        yuewen_proofread="但系⋯我仲可以发梦",
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
        note="Corrected '沙游' to '沙幼' as '沙幼' (fine sand) matches the "
        "meaning in the 中文, while '沙游' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="七彩缤纷的珊瑚，目不暇给的热带鱼",
        yuewen="七彩缤纷嘅珊瑚，目不下级嘅热带鱼群",
        yuewen_proofread="七彩缤纷嘅珊瑚，目不暇给嘅热带鱼群",
        note="Corrected '目不下级' to '目不暇给' as '目不暇给' is the correct idiom "
        "meaning 'too many to take in', matching the 中文.",
    ),
    ProofTestCase(
        zhongwen="充满赤道活力的原始海洋，脱离繁嚣",
        yuewen="充满住赤道热力嘅原始海洋，远离凡嚣",
        yuewen_proofread="充满住赤道热力嘅原始海洋，远离繁嚣",
        note="Corrected '凡嚣' to '繁嚣' as '繁嚣' is the correct term for '繁嚣' "
        "(bustle), matching the 中文.",
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
        note="Corrected '点远发呀' to '有几远呀' as '点远发' is a mishearing; '有几远' "
        "is the correct way to ask 'how far' in Cantonese.",
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
        yuewen_proofread="会！发财咗再讲啦",
        note="Corrected '得学发咗先啦' to '发财咗再讲啦' as '得学发' is a mishearing of "
        "'发财', and '再讲' matches '再说' in the 中文.",
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
        "Kitty乐园' as '好迪士尼呢' is a mishearing of '有迪士尼' and 'HelloTT' "
        "is a mishearing of 'Hello Kitty', both matching the intended "
        "meaning of the 中文.",
    ),
    ProofTestCase(
        zhongwen="我这个发夹也是在那儿买的",
        yuewen="我而家打紧个发卷都系𠮶边买嘅",
        yuewen_proofread="我而家戴紧个发夹都系𠮶边买嘅",
        note="Corrected '打紧个发卷' to '戴紧个发夹' as '发夹' matches the meaning of "
        "'发夹' in the 中文, while '发卷' is likely a mishearing.",
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
        "of the 中文.",
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
        "'food court', matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="那儿的海南鸡饭很大碟的",
        yuewen="𠮶度啲可能几份好大碟㗎",
        yuewen_proofread="𠮶度啲海南鸡饭好大碟㗎",
        note="Corrected '可能几份' to '海南鸡饭' as '海南鸡饭' is the correct dish "
        "mentioned in the 中文, while '可能几份' is a mishearing.",
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
        "is a mishearing of '好多' (a lot), matching the meaning of "
        "'饭很多'.",
    ),
    ProofTestCase(
        zhongwen="不过说到我最想去的地方，那可厉害了",
        yuewen="不过讲到我最想去嘅地方呢，𠮶度细嚟啰",
        yuewen_proofread="不过讲到我最想去嘅地方呢，𠮶度犀利啰",
        note="Corrected '细嚟啰' to '犀利啰' as '犀利' (sai3 lei6) matches the "
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
        yuewen_proofread="座落于印度洋嘅世外桃源",
        note="Corrected '独来鱼' to '座落于' as '独来鱼' is a mishearing of '座落于', "
        "matching the meaning of the 中文.",
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
        yuewen_proofread="冇嘢吖嘛？快啲饮埋啲药水佢先啦！",
        note="Corrected '食埋啲药水' to '饮埋啲药水' as '饮' is the correct verb for "
        "drinking medicine, matching the meaning of '喝掉'.",
    ),
    ProofTestCase(
        zhongwen="妈妈我不想喝药水",
        yuewen="妈妈，我唔想食药水呀",
        yuewen_proofread="妈妈，我唔想饮药水呀",
        note="Corrected '食药水' to '饮药水' as '饮' is the correct verb for "
        "drinking medicine in liquid form, matching the meaning of "
        "'喝药水'.",
    ),
    ProofTestCase(
        zhongwen="不要呀妈妈，我不喝呀",
        yuewen="唔好捞妈妈，我唔食呀",
        yuewen_proofread="唔好呀妈妈，我唔饮呀",
        note="Corrected '唔好捞' to '唔好呀' as '捞' is a mishearing of '呀', and "
        "'我唔食呀' to '我唔饮呀' since the original is about drinking, not "
        "eating.",
    ),
    ProofTestCase(
        zhongwen="我不喝士多啤梨药水呀！",
        yuewen="我唔食士多啤梨药水呀！",
        yuewen_proofread="我唔饮士多啤梨药水呀！",
        note="Corrected '食' to '饮' as the correct verb for drinking "
        "medicine is '饮', not '食'.",
    ),
    ProofTestCase(
        zhongwen="别哭了，不喝药水病不会好的",
        yuewen="唔好喊啦，唔食药唔会好㗎",
        yuewen_proofread="唔好喊啦，唔饮药水唔会好㗎",
        note="Corrected '唔食药' to '唔饮药水' as the original refers to drinking "
        "medicine (liquid), not eating medicine.",
    ),
    ProofTestCase(
        zhongwen="乖乖，病好了妈妈带你去马尔代夫",
        yuewen="乖乖啲，病好咗妈妈大理马尔代夫",
        yuewen_proofread="乖乖啲，病好咗妈妈带你去马尔代夫",
        note="Corrected '妈妈大理马尔代夫' to '妈妈带你去马尔代夫' as '大理' is a mishearing "
        "of '带你', which matches the meaning of the 中文.",
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
        yuewen_proofread="乖，饮埋啲药水先啦",
        note="Corrected '食埋啲药水' to '饮埋啲药水' as '饮' is the correct verb for "
        "taking liquid medicine, matching the meaning of '喝掉'.",
    ),
]  # proof_test_cases_block_19
proof_test_cases_block_20 = [
    ProofTestCase(
        zhongwen="好呀，马尔代夫！",
        yuewen="嘻嘻，好嘢，买二代夫！",
        yuewen_proofread="嘻嘻，好嘢，马尔代夫！",
        note="Corrected '买二代夫' to '马尔代夫' as it is a mishearing of the "
        "place name '马尔代夫' (Maldives).",
    ),
    ProofTestCase(
        zhongwen="马尔代夫！",
        yuewen="买二代夫！",
        yuewen_proofread="马尔代夫！",
        note="Corrected '买二代夫' to '马尔代夫' as it is a mishearing of the "
        "place name '马尔代夫' (Maldives).",
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
        yuewen_proofread="嚟啦，饮多啲！",
        note="Corrected '食多更' to '饮多啲' as the original phrase is about "
        "drinking more, not eating more; '饮多啲' matches the meaning of "
        "'多喝一点'.",
        include_in_prompt=True,
    ),
]  # proof_test_cases_block_20
proof_test_cases_block_21 = [
    ProofTestCase(
        zhongwen="妈妈，你看！",
        yuewen="妈妈你睇！",
        yuewen_proofread="妈妈你睇！",
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
        note="Corrected '啲嘢' to '啲药' as the sentence is about finishing "
        "medicine, not just 'things'; '药' matches the meaning of '药' "
        "in the 中文.",
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
        note="Removed '下' from '饮下一格' to correct the mishearing; '饮一格' "
        "matches the meaning of '喝一格' (drink one section/cup).",
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
        note="Corrected '饮实' to '饮晒' as '饮晒' means 'finished drinking', "
        "matching the meaning of '喝光了' in the 中文.",
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
        note="Corrected '阿哋' to '我哋' as '我哋' is the correct Cantonese "
        "pronoun for 'we', while '阿哋' is likely a mishearing.",
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
        note="Corrected '耶南树影' to '椰林树影' and '沙游' to '沙幼' as both are "
        "likely mishearings; '椰林树影，水清沙幼' is a well-known phrase "
        "describing the Maldives.",
    ),
    ProofTestCase(
        zhongwen="座落于印度洋的世外桃源呀！",
        yuewen="助流于印度园嘅世外导演啦！",
        yuewen_proofread="座落于印度洋嘅世外桃源啦！",
        note="Corrected '助流于印度园嘅世外导演' to '座落于印度洋嘅世外桃源' as the original was "
        "a clear mishearing of the place and descriptive terms.",
    ),
    ProofTestCase(
        zhongwen="想不到你还有点文采",
        yuewen="啊，估唔到你几好文采㗎噃",
        yuewen_proofread="啊，估唔到你几好文采㗎噃",
        note="",
    ),
    ProofTestCase(
        zhongwen="说得不错呀！",
        yuewen="讲得几好听啊！",
        yuewen_proofread="讲得几好听啊！",
        note="",
    ),
    ProofTestCase(
        zhongwen="我不是光说的呀，妈妈你说过⋯",
        yuewen="妈妈，我唔系讲喇㗎， 又系你话嘅，你话⋯",
        yuewen_proofread="妈妈，我唔系讲吓㗎， 又系你话嘅，你话⋯",
        note="Corrected '讲喇㗎' to '讲吓㗎' as '讲吓' (just saying) matches the "
        "meaning of '光说的' in the 中文, while '讲喇㗎' is likely a "
        "mishearing.",
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
        yuewen_proofread="唔系㖞，妈妈，你话我病好咗就去㗎㖞",
        note="Added '我病' before '好咗' to match the meaning of '你说我病好了就去的', "
        "as the original 粤文 omitted '我病', likely due to a mishearing "
        "or omission.",
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
        yuewen="系喇，系喇，系喇，发咗喇",
        yuewen_proofread="系喇，系喇，系喇，发咗喇",
        note="",
    ),
    ProofTestCase(
        zhongwen="我们下个星期去，好了吧？",
        yuewen="下个礼拜同你去啦？",
        yuewen_proofread="下个礼拜同你去啦？",
        note="",
    ),
    ProofTestCase(
        zhongwen="太好了！",
        yuewen="得未啊！好嘢！",
        yuewen_proofread="得未啊！好嘢！",
        note="",
    ),
]  # proof_test_cases_block_22
proof_test_cases_block_23 = [
    ProofTestCase(
        zhongwen="麦唛，我是麦兜呀",
        yuewen="喂，麦麦啊，麦豆啊，我系，即系呢",
        yuewen_proofread="喂，麦麦啊，麦兜啊，我系，即系呢",
        note="Corrected '麦豆' to '麦兜' as '麦兜' is the correct name, matching "
        "the 中文 and likely a mishearing.",
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
        note="Corrected '飞机真好难食㗎？' to '飞机餐好难食㗎？' as '飞机餐' is the correct "
        "term for 'airplane meal', matching the meaning in the 中文.",
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
        "'马尔代夫' (Maldives), which matches the intended meaning.",
    ),
    ProofTestCase(
        zhongwen="那边蓝天白云，椰林树影⋯",
        yuewen="𠮶度蓝天五百云，夜临雪⋯",
        yuewen_proofread="𠮶度蓝天白云，椰林树⋯",
        note="Corrected '五百云' to '白云' as it is a mishearing of '白云', and "
        "'夜临雪' to '椰林树' as it is a mishearing of '椰林树'.",
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
        note="Cleared as the provided 粤文 is a repeated string of '竟然' with "
        "no relation to the original 中文, indicating a complete "
        "transcription failure.",
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
        note="Corrected '绝鸡' to '住鸡' as '包得住' (can wrap/cover) matches the "
        "meaning of '包着', while '绝鸡' is likely a mishearing.",
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
        yuewen_proofread="尤其系细细旧嗰啲",
        note="Replaced '𠮶啲' with '嗰啲' as '嗰啲' is the standard written "
        "Cantonese for 'those', and '𠮶啲' is a common mishearing or "
        "nonstandard variant.",
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
        yuewen="好激动噉同在场嘅记者讲⋯",
        yuewen_proofread="好激动噉同在场嘅记者讲⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="足以证明香港运动员不是腊鸭！",
        yuewen="今次佢嘅成绩可以证明到香港嘅运动员唔系𫚭鸭！",
        yuewen_proofread="今次佢嘅成绩可以证明到香港嘅运动员唔系腊鸭！",
        note="Corrected '𫚭鸭' to '腊鸭' as '腊鸭' is the correct term, matching "
        "the meaning in the 中文.",
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
        "the intended phrase '报告完毕'.",
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
        note="Corrected '励根' to '黎根' as '黎根' matches the name in the 中文 "
        "and '励根' is likely a mishearing.",
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
        yuewen_proofread="我要黎紧收我做徒弟！",
        note="Corrected '来紧' to '黎紧' and '度徒弟' to '做徒弟' as '黎紧' (coming "
        "to) and '做徒弟' (as apprentice) match the intended meaning, "
        "while '度徒弟' is likely a mishearing of '做徒弟'.",
    ),
    ProofTestCase(
        zhongwen="无论几辛苦，我一定要得到奥运金牌！",
        yuewen="无论几辛苦，我一定要捞到奥运金牌！",
        yuewen_proofread="无论几辛苦，我一定要攞到奥运金牌！",
        note="Corrected '捞到' to '攞到' as '攞到' is the correct Cantonese verb "
        "for 'to get/obtain', matching the meaning of the 中文.",
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
        note="Corrected '系今排' to '举起金牌' as '今排' is a mishearing of '金牌', "
        "which matches the meaning of the 中文.",
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
proof_test_cases_block_35 = [
    ProofTestCase(
        zhongwen="想不到我黎根避进南丫岛也给你发现",
        yuewen="制估唔到我嚟跟你入嚟南丫岛都畀你揾到",
        yuewen_proofread="真估唔到我嚟根避入嚟南丫岛都畀你揾到",
        note="Corrected '制估' to '真估' as '真估唔到' is the correct phrase for "
        "'想不到', and '跟你' to '根避' to better match the meaning of '黎根避' "
        "(come to hide/avoid) in the 中文.",
    ),
    ProofTestCase(
        zhongwen="小朋友，你知道什么是狗仔队吧？",
        yuewen="小朋友，我谂你都知道乜嘢叫做狗仔队嘞？",
        yuewen_proofread="小朋友，我谂你都知道乜嘢叫做狗仔队嘞？",
        note="",
    ),
    ProofTestCase(
        zhongwen="加上总有小朋友及家长来说要拜我为师",
        yuewen="再加上不时有啲小朋友同埋家长嚟揾我话要拜我为师",
        yuewen_proofread="再加上不时有啲小朋友同埋家长嚟揾我话要拜我为师",
        note="",
    ),
    ProofTestCase(
        zhongwen="我才过来南丫岛避一避",
        yuewen="所以我咪过嚟南丫岛避一避",
        yuewen_proofread="所以我咪过嚟南丫岛避一避",
        note="",
    ),
    ProofTestCase(
        zhongwen="至于拜师的事⋯",
        yuewen="至于拜师嘅嘢⋯",
        yuewen_proofread="至于拜师嘅嘢⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="拜你个头！",
        yuewen="拜你个头嘅！",
        yuewen_proofread="拜你个头嘅！",
        note="",
    ),
    ProofTestCase(
        zhongwen="你们这些住香港岛的小朋友骄生惯养",
        yuewen="你哋呢班住喺香港岛嘅小朋友娇生惯养",
        yuewen_proofread="你哋呢班住喺香港岛嘅小朋友娇生惯养",
        note="",
    ),
    ProofTestCase(
        zhongwen="怎么吃得苦？",
        yuewen="边挨得苦㗎？",
        yuewen_proofread="边挨得苦㗎？",
        note="",
    ),
    ProofTestCase(
        zhongwen="想跟珊珊般得奥运金牌？",
        yuewen="想学山伞攞奥运金牌？",
        yuewen_proofread="想学珊珊攞奥运金牌？",
        note="Corrected '山伞' to '珊珊' as '珊珊' is the correct name, matching "
        "the reference in the 中文.",
    ),
    ProofTestCase(
        zhongwen="别作梦了！",
        yuewen="食母你嘢！",
        yuewen_proofread="",
        note="Cleared as '食母你嘢！' bears no resemblance to the original "
        "phrase '别作梦了！' and is clearly a complete transcription "
        "failure.",
    ),
]  # proof_test_cases_block_35
proof_test_cases_block_36 = [
    ProofTestCase(
        zhongwen="小朋友，你看！",
        yuewen="小朋友，你睇下！",
        yuewen_proofread="小朋友，你睇下！",
        note="",
    ),
]  # proof_test_cases_block_36
proof_test_cases_block_37 = [
    ProofTestCase(
        zhongwen="这个⋯",
        yuewen="哗⋯",
        yuewen_proofread="哗⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="这脚瓜⋯好粗好大！比一节瓜还要大！",
        yuewen="呢只，呢只脚瓜好粗好大呀！仲大个只瓜呀！",
        yuewen_proofread="呢只，呢只脚瓜好粗好大呀！仲大过节瓜呀！",
        note="Corrected '仲大个只瓜呀' to '仲大过节瓜呀' as '节瓜' is the correct term "
        "matching '一节瓜' in the 中文, and '大过' means 'bigger than'.",
    ),
    ProofTestCase(
        zhongwen="脚瓜的肌肉非常结实⋯",
        yuewen="脚瓜啲肌肉非常结实⋯",
        yuewen_proofread="脚瓜啲肌肉非常结实⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="青筋凸现，钢线似的",
        yuewen="啲青筋凸晒出嚟，好似钢线噉",
        yuewen_proofread="啲青筋凸晒出嚟，好似钢线噉",
        note="",
    ),
    ProofTestCase(
        zhongwen="每一条脚毛都硬似铁钉",
        yuewen="啲脚毛，每一条好似铁钉噉硬",
        yuewen_proofread="啲脚毛，每一条好似铁钉噉硬",
        note="",
    ),
    ProofTestCase(
        zhongwen="脚趾甲有一寸厚，究竟⋯",
        yuewen="脚趾弓啲脚甲成吋噉厚，究竟⋯",
        yuewen_proofread="脚趾甲啲脚甲成吋噉厚，究竟⋯",
        note="Corrected '脚趾弓' to '脚趾甲' as '脚趾甲' is the correct term for "
        "'toenail', matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="要行过几多座山⋯",
        yuewen="要行我几多座山⋯",
        yuewen_proofread="要行过几多座山⋯",
        note="Corrected '行我' to '行过' as '行过' (walk across) matches the "
        "meaning of '行过' in the 中文, while '行我' is likely a "
        "mishearing.",
    ),
    ProofTestCase(
        zhongwen="跨过几多个海⋯",
        yuewen="跨我几多个海⋯",
        yuewen_proofread="跨过几多个海⋯",
        note="Corrected '跨我' to '跨过' as '跨过' is the correct verb for "
        "'cross over' and matches the meaning in the 中文; '跨我' is "
        "likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="吃过几多苦头⋯",
        yuewen="挨过几多苦头⋯",
        yuewen_proofread="挨过几多苦头⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="才可以练成这举世无双的脚瓜？",
        yuewen="先至可以练成呢只举世无双嘅脚瓜？",
        yuewen_proofread="先至可以练成呢只举世无双嘅脚瓜？",
        note="",
    ),
]  # proof_test_cases_block_37
proof_test_cases_block_38 = [
    ProofTestCase(
        zhongwen="我⋯我一定要练成这脚瓜！",
        yuewen="我⋯我一定要练成呢只脚挂！",
        yuewen_proofread="我⋯我一定要练成呢只脚瓜！",
        note="Corrected '脚挂' to '脚瓜' as '脚瓜' is the correct Cantonese term "
        "for 'calf', matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="师傅！",
        yuewen="师父！",
        yuewen_proofread="师傅！",
        note="Corrected '师父' to '师傅' as '师傅' is the correct term for "
        "addressing a taxi driver or worker, matching the context of "
        "the 中文.",
    ),
]  # proof_test_cases_block_38
proof_test_cases_block_39 = [
    ProofTestCase(
        zhongwen="我可以去小个便吗？",
        yuewen="我可唔可以去个小便呢？",
        yuewen_proofread="我可唔可以去个小便呢？",
        note="",
    ),
]  # proof_test_cases_block_39
proof_test_cases_block_40 = [
    ProofTestCase(
        zhongwen="每次唱这首歌，我都会急小便",
        yuewen="而知点解每一字唱呢首歌都会急小便",
        yuewen_proofread="唔知点解每一次唱呢首歌都会急小便",
        note="Corrected '而知' to '唔知' as it is a likely mishearing of '每次' "
        "or '唔知', and '每一字' to '每一次' to match the meaning of '每次' in "
        "the 中文.",
    ),
    ProofTestCase(
        zhongwen="现在先去，一回恐怕还是会急",
        yuewen="仅次去定先，都怕一阵会再急过",
        yuewen_proofread="而家去定先，都怕一阵会再急过",
        note="Corrected '仅次去定先' to '而家去定先' as '而家' (now) is the correct "
        "term matching the meaning of '现在', while '仅次' is a "
        "mishearing.",
    ),
    ProofTestCase(
        zhongwen="但是我现在一定要唱这首歌",
        yuewen="但系我而家一定要唱呢首歌",
        yuewen_proofread="但系我而家一定要唱呢首歌",
        note="",
    ),
    ProofTestCase(
        zhongwen="希望可以改变黎根对我的看法",
        yuewen="希望可以改变黎根对我嘅睇法",
        yuewen_proofread="希望可以改变黎根对我嘅睇法",
        note="",
    ),
    ProofTestCase(
        zhongwen="我要用这歌打动黎根",
        yuewen="我要用呢首歌打动黎根",
        yuewen_proofread="我要用呢首歌打动黎根",
        note="",
    ),
    ProofTestCase(
        zhongwen="我要黎根收我做徒弟！",
        yuewen="我要黎根收我做徒弟！",
        yuewen_proofread="我要黎根收我做徒弟！",
        note="",
    ),
    ProofTestCase(
        zhongwen="歌，是这样唱的⋯",
        yuewen="𠮶首歌系噉唱嘅⋯",
        yuewen_proofread="𠮶首歌系噉唱嘅⋯",
        note="",
    ),
]  # proof_test_cases_block_40
proof_test_cases_block_41 = [
    ProofTestCase(
        zhongwen="黎根听完歌以后，表情有点古怪⋯",
        yuewen="黎今听完首歌之后，啲表情有啲古怪⋯",
        yuewen_proofread="黎根听完首歌之后，啲表情有啲古怪⋯",
        note="Corrected '黎今' to '黎根' as '黎根' is the correct name matching "
        "the 中文, and '黎今' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="我一定要好好把握这机会",
        yuewen="唔，我一定要好好把握呢个机会",
        yuewen_proofread="唔，我一定要好好把握呢个机会",
        note="",
    ),
    ProofTestCase(
        zhongwen="师傅！你收我做徒弟吧！",
        yuewen="师父！你收我做徒弟啦！",
        yuewen_proofread="师父！你收我做徒弟啦！",
        note="",
    ),
    ProofTestCase(
        zhongwen="你唔收我做徒弟，我一世都这么跪着！",
        yuewen="你收我做徒弟，我呢一世都跪喺度！",
        yuewen_proofread="你唔收我做徒弟，我呢一世都跪喺度！",
        note="Added '唔' before '收我做徒弟' to match the meaning of the 中文, as "
        "the original 粤文 omitted the negation, likely due to a "
        "mishearing.",
    ),
    ProofTestCase(
        zhongwen="起来呀！",
        yuewen="起身啊！",
        yuewen_proofread="起身啊！",
        note="",
    ),
    ProofTestCase(
        zhongwen="多谢师傅！",
        yuewen="多谢师父！",
        yuewen_proofread="多谢师傅！",
        note="Corrected '师父' to '师傅' as '师傅' is the appropriate term for a "
        "driver or worker, matching the context of the 中文.",
    ),
    ProofTestCase(
        zhongwen="不⋯我是叫你扶我起来呀！",
        yuewen="唔系啊⋯我系叫你扶我起身啊！",
        yuewen_proofread="唔系啊⋯我系叫你扶我起身啊！",
        note="",
    ),
    ProofTestCase(
        zhongwen="不成了！我的脚瓜太痹了！",
        yuewen="顶唔顺啊！我个腿挂好鼻啊！字幕由Amara.org社群提供",
        yuewen_proofread="顶唔顺啊！我个脚瓜好痹啊！字幕由Amara.org社群提供",
        note="Corrected '腿挂' to '脚瓜' as '脚瓜' is the correct Cantonese term "
        "for 'calf', matching the meaning of '脚瓜' in the 中文.",
    ),
]  # proof_test_cases_block_41
proof_test_cases_block_42 = [
    ProofTestCase(
        zhongwen="我将今天发生的事讲给妈妈听",
        yuewen="我将今日发生嘅嘢话晒畀妈妈听",
        yuewen_proofread="我将今日发生嘅嘢话晒畀妈妈听",
        note="",
    ),
    ProofTestCase(
        zhongwen="妈妈一句话也没说",
        yuewen="妈妈佢乜嘢都冇讲到",
        yuewen_proofread="妈妈佢乜嘢都冇讲到",
        note="",
    ),
    ProofTestCase(
        zhongwen="从冰箱内拿了只雪鸡出来解冻",
        yuewen="净系喺冰箱度攞咗只雪鸡出嚟解冻",
        yuewen_proofread="净系喺冰箱度攞咗只雪鸡出嚟解冻",
        note="",
    ),
    ProofTestCase(
        zhongwen="晚饭时，妈妈倒了三杯米酒",
        yuewen="晚饭时候，妈妈倒咗三杯米酒",
        yuewen_proofread="晚饭时候，妈妈倒咗三杯米酒",
        note="",
    ),
    ProofTestCase(
        zhongwen="又将几只橙和蒸好的鸡放到祖先前",
        yuewen="再将几个铲同埋蒸熟咗嘅鸡放喺祖先前面",
        yuewen_proofread="再将几只橙同埋蒸熟咗嘅鸡放喺祖先前面",
        note="Corrected '铲' to '橙' as '橙' (oranges) matches the meaning in "
        "the 中文, while '铲' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="妈妈叫我跪低，向祖先请请",
        yuewen="妈妈叫我跪低，同祖先请请",
        yuewen_proofread="妈妈叫我跪低，向祖先请请",
        note="Corrected '同祖先请请' to '向祖先请请' as '向' is the correct "
        "preposition for addressing ancestors in this context, "
        "matching the 中文.",
    ),
    ProofTestCase(
        zhongwen="妈妈跟着又念念有词的",
        yuewen="跟住，妈妈口噏噏噉讲咗一啲嘢",
        yuewen_proofread="跟住，妈妈口噏噏噉讲咗一啲嘢",
        note="",
    ),
    ProofTestCase(
        zhongwen="然后我们一起向祖先再拜了几拜",
        yuewen="然之后我哋又一齐对住祖先拜多几拜",
        yuewen_proofread="然之后我哋又一齐对住祖先拜多几拜",
        note="",
    ),
    ProofTestCase(
        zhongwen="妈妈蹲低把酒洒到地上",
        yuewen="妈妈虎低身将啲酒倒喺地上面",
        yuewen_proofread="妈妈蹲低身将啲酒倒喺地上面",
        note="Corrected '虎低身' to '蹲低身' as '蹲低' is the correct term for "
        "'squat down', matching the meaning of '蹲低' in the 中文.",
    ),
    ProofTestCase(
        zhongwen="庄重而温柔地跟我说：",
        yuewen="庄重又温柔紧同我讲：",
        yuewen_proofread="庄重又温柔紧同我讲：",
        note="",
    ),
    ProofTestCase(
        zhongwen="以后生生性性",
        yuewen="以后要生生性性",
        yuewen_proofread="以后要生生性性",
        note="",
    ),
    ProofTestCase(
        zhongwen="跟师傅学习，光宗耀祖！",
        yuewen="跟师父学嘢，当中要祖！",
        yuewen_proofread="跟师父学嘢，光宗耀祖！",
        note="Corrected '当中要祖' to '光宗耀祖' as '当中要祖' is a mishearing of "
        "'光宗耀祖', which matches the meaning in the 中文.",
    ),
]  # proof_test_cases_block_42
proof_test_cases_block_43 = [
    ProofTestCase(
        zhongwen="妈妈在长洲找了间酒楼摆拜师宴",
        yuewen="妈妈喺长洲揾咗间酒楼摆咗几回白丝宴",
        yuewen_proofread="妈妈喺长洲揾咗间酒楼摆拜师宴",
        note="Corrected '几回白丝宴' to '拜师宴' as '白丝宴' is a mishearing of "
        "'拜师宴', which matches the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="因为我是师傅最后一个入室弟子",
        yuewen="因为我系师父最后一个入室弟子",
        yuewen_proofread="因为我系师父最后一个入室弟子",
        note="",
    ),
    ProofTestCase(
        zhongwen="到贺的乡绅父老特别多",
        yuewen="所以到学嘅乡亲父老特别多",
        yuewen_proofread="所以到贺嘅乡亲父老特别多",
        note="Corrected '到学' to '到贺' as '到贺' (to congratulate) matches the "
        "meaning in the 中文, while '到学' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="想不到黄德森也来了",
        yuewen="估唔到黄德森都有嚟饮",
        yuewen_proofread="估唔到黄德森都有嚟饮",
        note="",
    ),
    ProofTestCase(
        zhongwen="还赞我背上的肉厚",
        yuewen="仲赞我背著啲肉口添",
        yuewen_proofread="仲赞我背脊啲肉厚添",
        note="Corrected '背著' to '背脊' and '肉口' to '肉厚' as these are likely "
        "mishearings; '背脊' means 'back' and '肉厚' means 'meaty/thick', "
        "matching the meaning of the 中文.",
    ),
    ProofTestCase(
        zhongwen="珊珊因为去了集训，没来",
        yuewen="但系山神就去咗集训，冇嚟到",
        yuewen_proofread="但系珊珊就去咗集训，冇嚟到",
        note="Corrected '山神' to '珊珊' as '山神' is a mishearing of the name '珊珊'.",
    ),
    ProofTestCase(
        zhongwen="麦唛，菇时跟得巴都来了",
        yuewen="默默，姑侍同德巴都嚟咗",
        yuewen_proofread="麦唛，菇时跟得巴都嚟咗",
        note="Corrected '默默' to '麦唛' and '姑侍同德巴都' to '菇时跟得巴都' to match the "
        "names and phrasing in the 中文; the original was a mishearing "
        "of the character names and phrase.",
    ),
    ProofTestCase(
        zhongwen="还带着成绩表，奖牌和大包",
        yuewen="仲带埋成绩表，奖牌，同大包嚟添",
        yuewen_proofread="仲带埋成绩表，奖牌，同大包嚟添",
        note="",
    ),
    ProofTestCase(
        zhongwen="他们都希望黎根也可以收他们做徒弟",
        yuewen="佢哋都希望嚟今可以收埋佢哋做徒弟",
        yuewen_proofread="佢哋都希望黎根可以收埋佢哋做徒弟",
        note="Corrected '嚟今' to '黎根' as '黎根' is the correct name matching "
        "the 中文, and '嚟今' is a likely mishearing.",
    ),
    ProofTestCase(
        zhongwen="吃过鸡丝翅，就是拜师仪式",
        yuewen="食完鸡丝翅，就到咗拜师仪式",
        yuewen_proofread="食完鸡丝翅，就到咗拜师仪式",
        note="",
    ),
    ProofTestCase(
        zhongwen="妈妈倒了杯茶给我，让我给师傅喝",
        yuewen="妈妈针咗杯热茶畀我，叫我弟畀师父饮",
        yuewen_proofread="妈妈针咗杯热茶畀我，叫我畀师父饮",
        note="Removed '弟' as it is a likely mishearing; the sentence "
        "should be '叫我畀师父饮' (let me give it to the master) to match "
        "the meaning of the 中文.",
    ),
    ProofTestCase(
        zhongwen="我千辛万苦来长洲找黎根⋯",
        yuewen="哦，我前三万苦嚟到长洲揾嚟近⋯",
        yuewen_proofread="哦，我千辛万苦嚟到长洲揾黎根⋯",
        note="Corrected '前三万苦' to '千辛万苦' as it is a mishearing of the "
        "idiom, and '嚟近' to '黎根' to match the name in the 中文.",
    ),
    ProofTestCase(
        zhongwen="我终于可以跟珊珊一起练滑浪风帆了！",
        yuewen="哦，我终于可以同山神一齐练习玩弄风范啊！",
        yuewen_proofread="哦，我终于可以同珊珊一齐练习滑浪风帆啊！",
        note="Corrected '山神' to '珊珊' as it is a mishearing of the name, "
        "and '玩弄风范' to '滑浪风帆' to match the intended meaning of "
        "'练滑浪风帆'.",
    ),
    ProofTestCase(
        zhongwen="我将茶递给黎根，黎根他⋯",
        yuewen="我将杯茶递咗畀嚟跟，嚟跟佢⋯",
        yuewen_proofread="我将杯茶递咗畀黎根，黎根佢⋯",
        note="Corrected '嚟跟' to '黎根' as '嚟跟' is a mishearing of the name '黎根'.",
    ),
    ProofTestCase(
        zhongwen="师傅他把茶喝了，正式收我做徒弟",
        yuewen="亦唔系，师父佢饮咗杯茶，正式收咗我做徒弟嘞",
        yuewen_proofread="亦唔系，师父佢饮咗杯茶，正式收咗我做徒弟嘞",
        note="",
    ),
    ProofTestCase(
        zhongwen="宾客们好像都很高兴",
        yuewen="啲来宾睇嚟好高气",
        yuewen_proofread="啲来宾睇嚟好高兴",
        note="Corrected '高气' to '高兴' as '高兴' is the correct term for "
        "'happy', matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="长洲的乡绅父老拍掌拍得特别落力",
        yuewen="特别系长洲啲乡亲父老拍奖拍得特别落力",
        yuewen_proofread="特别系长洲啲乡绅父老拍掌拍得特别落力",
        note="Corrected '乡亲' to '乡绅' and '拍奖' to '拍掌' as these are likely "
        "mishearings; '乡绅' matches '乡绅' in 中文 and '拍掌' is the correct "
        "term for clapping.",
    ),
    ProofTestCase(
        zhongwen="多谢各位赏面！多谢各位！",
        yuewen="多谢各位上面！多谢各位！",
        yuewen_proofread="多谢各位赏面！多谢各位！",
        note="Corrected '上面' to '赏面' as '赏面' is the correct phrase for "
        "'giving face' or 'honoring with your presence', matching the "
        "meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="在下平生有两项称得上得意的绝技",
        yuewen="在下评生有两项称得上得意嘅绝技",
        yuewen_proofread="在下平生有两项称得上得意嘅绝技",
        note="Corrected '评生' to '平生' as '平生' is the correct term for "
        "'one's whole life', matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="第一项，是滑浪风帆！",
        yuewen="第一样系滑浪风范！",
        yuewen_proofread="第一样系滑浪风帆！",
        note="Corrected '风范' to '风帆' as '风帆' is the correct term for "
        "windsurfing, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="我把它传给外甥女珊珊了",
        yuewen="呢样早已传咗畀我外甥女山神啊",
        yuewen_proofread="呢样早已传咗畀我外甥女珊珊啊",
        note="Corrected '山神' to '珊珊' as '珊珊' is the correct name matching "
        "the 中文, while '山神' is a likely mishearing.",
    ),
    ProofTestCase(
        zhongwen="另一项绝技，我打算传给这个新徒弟⋯",
        yuewen="另一项绝技，我打算传畀呢个新修嘅徒弟⋯",
        yuewen_proofread="另一项绝技，我打算传畀呢个新修嘅徒弟⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="希望他把长洲人世世代代的绝技",
        yuewen="希望我可以将我哋长洲人世世代代嘅传统",
        yuewen_proofread="希望我可以将我哋长洲人世世代代嘅传统",
        note="",
    ),
    ProofTestCase(
        zhongwen="发扬光大！",
        yuewen="发扬光大！",
        yuewen_proofread="发扬光大！",
        note="",
    ),
    ProofTestCase(
        zhongwen="请问那是什么绝技呢？",
        yuewen="噉请问𠮶样绝技系乜嘢啊？",
        yuewen_proofread="噉请问𠮶样绝技系乜嘢啊？",
        note="",
    ),
]  # proof_test_cases_block_43
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
        note="Corrected '抢爆山' to '抢包山' as '抢包山' is the correct term for "
        "the traditional event, and '爆' is a likely mishearing of "
        "'包'.",
    ),
]  # proof_test_cases_block_44
proof_test_cases_block_45 = [
    ProofTestCase(
        zhongwen="抢包山？",
        yuewen="抢包山？",
        yuewen_proofread="抢包山？",
        note="",
    ),
    ProofTestCase(
        zhongwen="年轻观众可能不知「抢包山」何物",
        yuewen="年轻嘅观众可能唔知乜嘢系「抢包山」呀",
        yuewen_proofread="年轻嘅观众可能唔知乜嘢系「抢包山」呀",
        note="",
    ),
    ProofTestCase(
        zhongwen="抢包山乃长洲独有传统节日",
        yuewen="抢包山系长洲独有嘅传统节日",
        yuewen_proofread="抢包山系长洲独有嘅传统节日",
        note="",
    ),
    ProofTestCase(
        zhongwen="每年农历四月",
        yuewen="每年农历四月",
        yuewen_proofread="每年农历四月",
        note="",
    ),
    ProofTestCase(
        zhongwen="长洲居民均举办太平清醮",
        yuewen="长洲嘅居民都会举办太平清朝",
        yuewen_proofread="长洲嘅居民都会举办太平清醮",
        note="Corrected '太平清朝' to '太平清醮' as '太平清醮' is the correct term for "
        "the festival, while '清朝' is a mishearing.",
    ),
    ProofTestCase(
        zhongwen="于北帝庙前搭起三座包山",
        yuewen="喺北帝庙前搭起三座包山",
        yuewen_proofread="喺北帝庙前搭起三座包山",
        note="",
    ),
    ProofTestCase(
        zhongwen="什么是包山呢？",
        yuewen="噉乜嘢系包山呢？",
        yuewen_proofread="噉乜嘢系包山呢？",
        note="",
    ),
    ProofTestCase(
        zhongwen="顾名思义⋯",
        yuewen="顾名思义⋯",
        yuewen_proofread="顾名思义⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="包山就是一座由好多好多包砌起的山！",
        yuewen="包山就系一座由好多，好多，好多包砌起嘅山！",
        yuewen_proofread="包山就系一座由好多，好多，好多包砌起嘅山！",
        note="",
    ),
    ProofTestCase(
        zhongwen="一座包山，起码六、七层楼高⋯",
        yuewen="一座包山起码六七层楼高⋯",
        yuewen_proofread="一座包山起码六七层楼高⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="你可以想像一下包山有多高了吧？",
        yuewen="噉你可以想像一下𠮶度有几多包喇？",
        yuewen_proofread="噉你可以想像一下𠮶度有几多包喇？",
        note="",
    ),
    ProofTestCase(
        zhongwen="抢包山，就是要把包山上的包抢到手！",
        yuewen="噉抢包山，自然就系要将包山嘅包抢到手！",
        yuewen_proofread="噉抢包山，自然就系要将包山嘅包抢到手！",
        note="",
    ),
    ProofTestCase(
        zhongwen="锣鼓响起",
        yuewen="罗古响起",
        yuewen_proofread="锣鼓响起",
        note="Corrected '罗古' to '锣鼓' as '锣鼓' is the correct term for 'gong "
        "and drum', matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="数以百计的青年一涌而上抢包",
        yuewen="数以百计嘅青年就会一涌而上去抢包",
        yuewen_proofread="数以百计嘅青年就会一涌而上去抢包",
        note="",
    ),
    ProofTestCase(
        zhongwen="抢得位置愈高的包，就是愈大的祝福",
        yuewen="抢到位置越高嘅包，就代表越大嘅祝福",
        yuewen_proofread="抢到位置越高嘅包，就代表越大嘅祝福",
        note="",
    ),
    ProofTestCase(
        zhongwen="更可以表现自己的不凡身手",
        yuewen="更加可以表现自己不凡嘅身手",
        yuewen_proofread="更加可以表现自己不凡嘅身手",
        note="",
    ),
    ProofTestCase(
        zhongwen="在1978年两座包山忽然倒下，多人重伤",
        yuewen="但喺1978年，两座包山突然塌咗",
        yuewen_proofread="但喺1978年，两座包山突然塌咗",
        note="",
    ),
    ProofTestCase(
        zhongwen="「抢包山」从此被禁！",
        yuewen="都去抢包山，而长洲特有嘅传统亦占备为榜！",
        yuewen_proofread="",
        note="Cleared as '都去抢包山，而长洲特有嘅传统亦占备为榜！' does not correspond to the "
        "original phrase '「抢包山」从此被禁！' and appears to be a complete "
        "transcription failure.",
    ),
    ProofTestCase(
        zhongwen="而长洲独有的传统，亦渐被遗忘",
        yuewen="长洲特有嘅传统，亦占备为榜",
        yuewen_proofread="长洲特有嘅传统，亦渐被遗忘",
        note="Corrected '占备为榜' to '渐被遗忘' as '占备为榜' is a mishearing of "
        "'渐被遗忘', matching the meaning in the 中文.",
    ),
]  # proof_test_cases_block_45
proof_test_cases_block_46 = [
    ProofTestCase(
        zhongwen="奥运金牌⋯这一世是没有机会的了",
        yuewen="奥运金牌⋯我谂呢一世都唔会攞到",
        yuewen_proofread="奥运金牌⋯我谂呢一世都唔会攞到",
        note="",
    ),
    ProofTestCase(
        zhongwen="每个星期六我都搭船过长洲",
        yuewen="每个礼拜六，我都会搭船过长洲",
        yuewen_proofread="每个礼拜六，我都会搭船过长洲",
        note="",
    ),
    ProofTestCase(
        zhongwen="去学抢包山⋯",
        yuewen="去学抢包山⋯",
        yuewen_proofread="去学抢包山⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="一项没有奖牌，没有对手，没有比赛⋯",
        yuewen="一日冇奖牌，冇对手，冇比赛⋯",
        yuewen_proofread="一日冇奖牌，冇对手，冇比赛⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="甚至没有人知道是运动的运动",
        yuewen="甚至乎冇人知对佢系运动嘅运动",
        yuewen_proofread="甚至乎冇人知对佢系运动嘅运动",
        note="",
    ),
    ProofTestCase(
        zhongwen="更坏的是，连包山也没有！",
        yuewen="更衰嘅系，连包山都冇！",
        yuewen_proofread="更衰嘅系，连包山都冇！",
        note="",
    ),
    ProofTestCase(
        zhongwen="师傅只是叫我去他的家⋯",
        yuewen="师傅净系叫我去佢屋企⋯",
        yuewen_proofread="师傅净系叫我去佢屋企⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="在组合柜爬来爬去",
        yuewen="喺个组合柜度爬嚟爬去",
        yuewen_proofread="喺个组合柜度爬嚟爬去",
        note="",
    ),
    ProofTestCase(
        zhongwen="碰！三番！",
        yuewen="通！三番！",
        yuewen_proofread="碰！三番！",
        note="Corrected '通' to '碰' as '碰' is the correct term used in "
        "mahjong, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="别躲懒！继续练！",
        yuewen="冇偷懒！继续练！",
        yuewen_proofread="唔好偷懒！继续练！",
        note="Corrected '冇偷懒' to '唔好偷懒' as the original phrase means "
        "'don't be lazy', not 'didn't slack off'; '唔好偷懒' matches the "
        "intended meaning.",
    ),
    ProofTestCase(
        zhongwen="一天，珊珊到了师传家！",
        yuewen="有一日，山伞嚟咗师傅屋企！",
        yuewen_proofread="有一日，珊珊嚟咗师傅屋企！",
        note="Corrected '山伞' to '珊珊' as it is a mishearing of the "
        "character's name.",
    ),
    ProofTestCase(
        zhongwen="珊珊！我的师姐珊珊！",
        yuewen="山伞！我个师仔山伞啊！",
        yuewen_proofread="珊珊！我个师姐珊珊啊！",
        note="Corrected '山伞' to '珊珊' as it is a mishearing of the name, "
        "and '师仔' to '师姐' to match the intended meaning of '师姐' in "
        "the 中文.",
    ),
    ProofTestCase(
        zhongwen="可以看见珊珊⋯",
        yuewen="可以见到山伞⋯",
        yuewen_proofread="可以见到珊珊⋯",
        note="Corrected '山伞' to '珊珊' as '山伞' is a mishearing of the name '珊珊'.",
    ),
    ProofTestCase(
        zhongwen="这几个星期爬得再辛苦也是值得的！",
        yuewen="爬得咁辛苦，都系值得㗎！",
        yuewen_proofread="爬得咁辛苦，都系值得㗎！",
        note="",
    ),
    ProofTestCase(
        zhongwen="珊珊！",
        yuewen="山伞！",
        yuewen_proofread="珊珊！",
        note="Corrected '山伞' to '珊珊' as '山伞' is a mishearing of the name '珊珊'.",
    ),
    ProofTestCase(
        zhongwen="珊你个头！继续练习！",
        yuewen="伞你个头啊！继续练习！",
        yuewen_proofread="珊你个头啊！继续练习！",
        note="Corrected '伞' to '珊' as '珊你个头' is a common Cantonese phrase, "
        "while '伞' is likely a mishearing.",
    ),
]  # proof_test_cases_block_46
proof_test_cases_block_47 = [
    ProofTestCase(
        zhongwen="还不去？",
        yuewen="仲唔系？",
        yuewen_proofread="仲唔去？",
        note="Corrected '仲唔系？' to '仲唔去？' as '仲唔去' matches the meaning of "
        "'还不去', while '仲唔系' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="珊珊没看见我这个师弟",
        yuewen="山神佢见唔到我呢个师弟",
        yuewen_proofread="珊珊佢见唔到我呢个师弟",
        note="Corrected '山神' to '珊珊' as '珊珊' is the correct name matching "
        "the 中文, while '山神' is a likely mishearing.",
    ),
    ProofTestCase(
        zhongwen="我只有死死气再爬上组合柜",
        yuewen="我唯有死死气爬返上个组合柜",
        yuewen_proofread="我唯有死死气爬返上个组合柜",
        note="",
    ),
    ProofTestCase(
        zhongwen="我咁大个仔，什么「头」也给骂过⋯",
        yuewen="我咁大个仔，乜嘢头都畀人闹过⋯",
        yuewen_proofread="我咁大个仔，乜嘢头都畀人闹过⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="「珊你个头」却特别刺耳",
        yuewen="但系「山呢个头」唔知点解特别瘾",
        yuewen_proofread="但系「珊你个头」唔知点解特别瘾",
        note="Corrected '山呢个头' to '珊你个头' as it is a mishearing; '珊你个头' "
        "matches the intended phrase in the 中文.",
    ),
    ProofTestCase(
        zhongwen="我⋯我⋯",
        yuewen="我⋯我⋯",
        yuewen_proofread="我⋯我⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="我唔学抢包山了！",
        yuewen="我唔好抢包纱嘞！字幕由纱友提供",
        yuewen_proofread="我唔学抢包山嘞！字幕由纱友提供",
        note="Corrected '抢包纱' to '抢包山' as '抢包山' is the correct term for "
        "the bun-snatching event, matching the meaning in the 中文.",
    ),
]  # proof_test_cases_block_47
proof_test_cases_block_48 = [
    ProofTestCase(
        zhongwen="其实今天是我第一次近距离见黎根",
        yuewen="其实今日系我第一次咁近距离同丽根见面",
        yuewen_proofread="其实今日系我第一次咁近距离同丽根见面",
        note="",
    ),
    ProofTestCase(
        zhongwen="他恐怕都有五十岁了",
        yuewen="睇怕佢都有五十岁啦",
        yuewen_proofread="睇怕佢都有五十岁啦",
        note="",
    ),
    ProofTestCase(
        zhongwen="却还是一副孩子脸",
        yuewen="但系仲有一副孩子脸",
        yuewen_proofread="但系仲有一副孩子脸",
        note="",
    ),
    ProofTestCase(
        zhongwen="鸡尾包！新鲜出炉！",
        yuewen="鸡尾包！啱啱出炉嘅！",
        yuewen_proofread="鸡尾包！啱啱出炉嘅！",
        note="",
    ),
]  # proof_test_cases_block_48
proof_test_cases_block_49 = [
    ProofTestCase(
        zhongwen="其实鸡尾包呢⋯",
        yuewen="其实鸡尾爆呢⋯",
        yuewen_proofread="其实鸡尾包呢⋯",
        note="Corrected '鸡尾爆' to '鸡尾包' as '鸡尾包' is the correct term for "
        "the bun, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="你说这似不似鸡尾？",
        yuewen="吓，你话噉样似唔似鸡尾呀？哈哈哈哈",
        yuewen_proofread="吓，你话噉样似唔似鸡尾呀？哈哈哈哈",
        note="",
    ),
]  # proof_test_cases_block_49
proof_test_cases_block_50 = [
    ProofTestCase(
        zhongwen="麦兜他学东西⋯还可以",
        yuewen="麦兜嘅学嘢呢⋯都仲可以",
        yuewen_proofread="麦兜嘅学嘢呢⋯都仲可以",
        note="",
    ),
    ProofTestCase(
        zhongwen="黎根接着说了一大堆话⋯",
        yuewen="跟住黎根讲咗一大堆说话⋯",
        yuewen_proofread="跟住黎根讲咗一大堆说话⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="他的抱负，他对麦兜的期望",
        yuewen="讲下佢嘅抱负，佢对麦兜嘅期望",
        yuewen_proofread="讲下佢嘅抱负，佢对麦兜嘅期望",
        note="",
    ),
    ProofTestCase(
        zhongwen="他说他会把他所识的毫不保留教给麦兜",
        yuewen="佢话会将佢识嘅嘢毫无保留噉教晒畀麦兜",
        yuewen_proofread="佢话会将佢识嘅嘢毫无保留噉教晒畀麦兜",
        note="",
    ),
    ProofTestCase(
        zhongwen="黎根越说越兴奋，直到双眼发光",
        yuewen="黎根越讲越兴奋",
        yuewen_proofread="黎根越讲越兴奋",
        note="",
    ),
    ProofTestCase(
        zhongwen="他又说滑浪风帆并不是他最犀利的项目",
        yuewen="佢话滑浪风帆都唔系佢最犀利𠮶样",
        yuewen_proofread="佢话滑浪风帆都唔系佢最犀利𠮶样",
        note="",
    ),
    ProofTestCase(
        zhongwen="他最大强项是抢包山",
        yuewen="佢最劲嘅就系抢包山",
        yuewen_proofread="佢最劲嘅就系抢包山",
        note="",
    ),
    ProofTestCase(
        zhongwen="他说抢包山结合了南拳",
        yuewen="佢话抢包山结合咗南拳",
        yuewen_proofread="佢话抢包山结合咗南拳",
        note="",
    ),
    ProofTestCase(
        zhongwen="神功戏和现代器械操",
        yuewen="神功气现代气蟹粗",
        yuewen_proofread="神功戏同现代器械操",
        note="Corrected '气' to '戏' and '气蟹粗' to '器械操' as these are likely "
        "mishearings of the correct terms for '神功戏' and '器械操'.",
    ),
    ProofTestCase(
        zhongwen="他说抢包山才是他一生最大成就",
        yuewen="佢话抢包山先至系佢呢世人最大嘅成就",
        yuewen_proofread="佢话抢包山先至系佢呢世人最大嘅成就",
        note="",
    ),
    ProofTestCase(
        zhongwen="缩脚，唔该！",
        yuewen="缩𠮶只脚，唔该！",
        yuewen_proofread="缩𠮶只脚，唔该！",
        note="",
    ),
    ProofTestCase(
        zhongwen="你看！",
        yuewen="你睇下！",
        yuewen_proofread="你睇下！",
        note="",
    ),
    ProofTestCase(
        zhongwen="这脚瓜⋯好粗好大！比一节瓜还要大！",
        yuewen="哗，呢节，呢节脚瓜好粗好大呀！仲大过节瓜！",
        yuewen_proofread="哗，呢节，呢节脚瓜好粗好大呀！仲大过节瓜！",
        note="",
    ),
    ProofTestCase(
        zhongwen="脚瓜的肌肉非常结实⋯",
        yuewen="脚瓜嘅肌肉非常结实⋯",
        yuewen_proofread="脚瓜嘅肌肉非常结实⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="青筋凸现，钢线似的",
        yuewen="啲青筋凸晒出嚟，好似钢线噉",
        yuewen_proofread="啲青筋凸晒出嚟，好似钢线噉",
        note="",
    ),
    ProofTestCase(
        zhongwen="每一条脚毛都硬似铁钉",
        yuewen="啲脚毛每一条都好似铁钉咁硬",
        yuewen_proofread="啲脚毛每一条都好似铁钉咁硬",
        note="",
    ),
    ProofTestCase(
        zhongwen="脚趾甲有一寸厚，究竟⋯",
        yuewen="脚趾弓啲脚夹成串咁厚，究竟⋯",
        yuewen_proofread="脚趾甲啲脚甲成寸咁厚，究竟⋯",
        note="Corrected '脚趾弓啲脚夹成串咁厚' to '脚趾甲啲脚甲成寸咁厚' as '脚趾甲' (toenail) "
        "and '脚甲' (nail) are the correct terms, and '成寸' (an inch "
        "thick) matches the meaning of '一寸厚'; '弓' and '夹' are likely "
        "mishearings of '甲' and '寸' respectively.",
    ),
    ProofTestCase(
        zhongwen="要走过几多座山",
        yuewen="要行个几度呢?几多座山",
        yuewen_proofread="要行过几多座山",
        note="Corrected '行个几度呢?' to '行过' as '行过' (walk across) matches the "
        "meaning of '走过' in the 中文, while '个几度呢?' is likely a "
        "mishearing.",
    ),
    ProofTestCase(
        zhongwen="跨过几多个海",
        yuewen="挂过几多个海",
        yuewen_proofread="跨过几多个海",
        note="Corrected '挂过' to '跨过' as '跨过' (to cross over) matches the "
        "meaning of the 中文, while '挂过' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="吃过几多苦头",
        yuewen="挨过几多斧头",
        yuewen_proofread="挨过几多苦头",
        note="Corrected '斧头' to '苦头' as '苦头' matches the meaning of '苦头' "
        "(hardships) in the 中文, while '斧头' is a likely mishearing.",
    ),
    ProofTestCase(
        zhongwen="才可以练成这举世无双的脚瓜？",
        yuewen="先至可以练成呢一只举细无伤嘅脚瓜？",
        yuewen_proofread="先至可以练成呢一只举世无双嘅脚瓜？",
        note="Corrected '举细无伤' to '举世无双' as it is a mishearing of the "
        "correct phrase meaning 'peerless' or 'unparalleled'.",
    ),
]  # proof_test_cases_block_50
proof_test_cases_block_51 = [
    ProofTestCase(
        zhongwen="我个仔⋯",
        yuewen="我个仔⋯",
        yuewen_proofread="我个仔⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="你个仔，他日都会有这只大脚瓜",
        yuewen="你个仔，第时都会有我咁大只脚瓜",
        yuewen_proofread="你个仔，第时都会有我咁大只脚瓜",
        note="",
    ),
    ProofTestCase(
        zhongwen="其实我也不知道个仔要这么粗的脚瓜⋯",
        yuewen="其实，我都唔知我仔要咁粗嘅脚瓜⋯",
        yuewen_proofread="其实，我都唔知我仔要咁粗嘅脚瓜⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="有什么用",
        yuewen="有咩用",
        yuewen_proofread="有咩用",
        note="",
    ),
    ProofTestCase(
        zhongwen="可是看见那些凸现的青筋，不知怎样⋯",
        yuewen="但系见到佢一条条凸起嘅青筋，唔知点解⋯",
        yuewen_proofread="但系见到佢一条条凸起嘅青筋，唔知点解⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="我想起麦兜的爸爸，阿炳",
        yuewen="我，我谂起麦兜嘅爸爸，阿炳",
        yuewen_proofread="我，我谂起麦兜嘅爸爸，阿炳",
        note="",
    ),
]  # proof_test_cases_block_51
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
proof_test_cases_block_53 = [
    ProofTestCase(
        zhongwen="想不到真的让妈妈拿去了。吓得我！",
        yuewen="咦，估唔到真系妈妈攞咗㖞。吓得我啊！",
        yuewen_proofread="咦，估唔到真系妈妈攞咗㖞。吓得我啊！",
        note="",
    ),
    ProofTestCase(
        zhongwen="妈妈怎么会写起英文信？",
        yuewen="点解妈妈会用英文写信嘅？",
        yuewen_proofread="点解妈妈会用英文写信嘅？",
        note="",
    ),
    ProofTestCase(
        zhongwen="信很短",
        yuewen="封信好短",
        yuewen_proofread="封信好短",
        note="",
    ),
    ProofTestCase(
        zhongwen="我猜是妈妈用电子辞典逐个字译成英文",
        yuewen="我谂妈妈佢系好辛苦用电子词典逐个逐个字译做英文",
        yuewen_proofread="我谂妈妈佢系好辛苦用电子词典逐个逐个字译做英文",
        note="",
    ),
    ProofTestCase(
        zhongwen="于是我又用电子辞典把信译回中文",
        yuewen="于是我让返电子词典，将封信译返做中文",
        yuewen_proofread="于是我用返电子词典，将封信译返做中文",
        note="Corrected '让返' to '用返' as '用返' (use again) matches the "
        "meaning of '又用' in the 中文, while '让返' is likely a "
        "mishearing.",
    ),
    ProofTestCase(
        zhongwen="信，是妈妈写给奥委会主席的",
        yuewen="封信原来系妈妈写畀奥委会主席㗎",
        yuewen_proofread="封信原来系妈妈写畀奥委会主席㗎",
        note="",
    ),
    ProofTestCase(
        zhongwen="「亲爱的主席：」",
        yuewen="「亲爱的主席：」",
        yuewen_proofread="「亲爱的主席：」",
        note="",
    ),
    ProofTestCase(
        zhongwen="「你好吗？我很好！」",
        yuewen="「你好吗？我很好！」",
        yuewen_proofread="「你好吗？我很好！」",
        note="",
    ),
    ProofTestCase(
        zhongwen="「你吃包吗？我吃包！」",
        yuewen="你吃包吗？我吃包！",
        yuewen_proofread="你吃包吗？我吃包！",
        note="",
    ),
    ProofTestCase(
        zhongwen="「我们居住在香港这里的人，很爱吃包」",
        yuewen="我门居住在香港这类的人，肯爱吃包",
        yuewen_proofread="我哋居住在香港呢度嘅人，好爱食包",
        note="Corrected '我门' to '我哋' as '我哋' is the correct Cantonese "
        "pronoun, '这类' to '呢度' as '呢度' (here) matches the meaning of "
        "'这里', and '肯爱' to '好爱' as '好爱' is the natural way to say "
        "'very love' in Cantonese; '食包' is the correct Cantonese for "
        "'吃包'.",
    ),
    ProofTestCase(
        zhongwen="「小笼包，上海包，广东包，莲蓉包」",
        yuewen="「小笼包，上海包，广东包，联融包」",
        yuewen_proofread="「小笼包，上海包，广东包，莲蓉包」",
        note="Corrected '联融包' to '莲蓉包' as '莲蓉包' is the correct term for "
        "lotus seed paste bun, matching the 中文.",
    ),
    ProofTestCase(
        zhongwen="「好朋友，我认为",
        yuewen="「好朋友，我认为",
        yuewen_proofread="「好朋友，我认为",
        note="",
    ),
    ProofTestCase(
        zhongwen="抢劫那些包，十分重要」",
        yuewen="抢劫𠮶些包，十分重要」",
        yuewen_proofread="抢劫𠮶些包，十分重要」",
        note="",
    ),
    ProofTestCase(
        zhongwen="「也算是运动，就真！」",
        yuewen="也算是运动，就真！",
        yuewen_proofread="也算是运动，就真！",
        note="",
    ),
    ProofTestCase(
        zhongwen="「要大力！大吃晚上的粥，和大节瓜！」",
        yuewen="「要大力！大吃吻上的粥，和大字瓜！」",
        yuewen_proofread="「要大力！大吃晚上的粥，和大节瓜！」",
        note="Corrected '吻上的粥' to '晚上的粥' and '大字瓜' to '大节瓜' as both are "
        "likely mishearings of the intended words in the context.",
    ),
    ProofTestCase(
        zhongwen="「按照我愚蠢的见解⋯」",
        yuewen="「按照我愚蠢的见解⋯」",
        yuewen_proofread="「按照我愚蠢的见解⋯」",
        note="",
    ),
    ProofTestCase(
        zhongwen="「抢劫那些包，是奥运会比赛」",
        yuewen="抢劫𠮶些包，系奥运会比赛",
        yuewen_proofread="抢劫𠮶些包，系奥运会比赛",
        note="",
    ),
    ProofTestCase(
        zhongwen="「让全世界的体育家，抢过！」",
        yuewen="「让全世界嘅体育家，抢过！」",
        yuewen_proofread="「让全世界嘅体育家，抢过！」",
        note="",
    ),
    ProofTestCase(
        zhongwen="「世界便和平！」",
        yuewen="「世界变和平！」",
        yuewen_proofread="「世界变和平！」",
        note="",
    ),
    ProofTestCase(
        zhongwen="「你有孩子吗？」",
        yuewen="「你有孩子吗？」",
        yuewen_proofread="「你有孩子吗？」",
        note="",
    ),
    ProofTestCase(
        zhongwen="「我有一个孩子，麦兜」",
        yuewen="「我有一个孩子，麦兜」",
        yuewen_proofread="「我有一个孩子，麦兜」",
        note="",
    ),
    ProofTestCase(
        zhongwen="终于讲到我了！",
        yuewen="终于讲到我啦！",
        yuewen_proofread="终于讲到我啦！",
        note="",
    ),
    ProofTestCase(
        zhongwen="「他是一个好男孩」",
        yuewen="「她系一个好男孩」",
        yuewen_proofread="「佢系一个好男孩」",
        note="Corrected '她' to '佢' as '佢' is the correct gender-neutral "
        "pronoun in Cantonese for 'he' or 'she', matching the meaning "
        "of '他' in the 中文.",
    ),
    ProofTestCase(
        zhongwen="「他非常懂得抢劫那些包」",
        yuewen="她非常懂得抢劫𠮶些包",
        yuewen_proofread="佢非常懂得抢劫𠮶些包",
        note="Corrected '她' to '佢' as '佢' is the correct gender-neutral "
        "pronoun in Cantonese for 'he' or 'she', matching the meaning "
        "of '他' in the 中文.",
    ),
    ProofTestCase(
        zhongwen="「有一天，我看见他，抢劫包⋯」",
        yuewen="有一天我看见她，抢劫包⋯",
        yuewen_proofread="有一天我看见佢，抢劫包⋯",
        note="Corrected '她' to '佢' as '佢' is the standard Cantonese "
        "pronoun for 'he/she', matching the unspecified gender in the "
        "中文.",
    ),
    ProofTestCase(
        zhongwen="「抢了一个奥运金牌」",
        yuewen="抢了一个奥运金牌",
        yuewen_proofread="抢了一个奥运金牌",
        note="",
    ),
    ProofTestCase(
        zhongwen="「那便是一个母亲能够有的最大的安慰」",
        yuewen="哪便是一个母亲能够有的最好的，最大的安慰",
        yuewen_proofread="哪便是一个母亲能够有的最好的，最大的安慰",
        note="",
    ),
    ProofTestCase(
        zhongwen="「孩子的才干，得到了世界人类的知道」",
        yuewen="「孩子的才干得到了世界人类的知道」",
        yuewen_proofread="「孩子的才干得到了世界人类的知道」",
        note="",
    ),
    ProofTestCase(
        zhongwen="「父母愿意做什么的东西都得」",
        yuewen="「父母愿意做什么的东西都得」",
        yuewen_proofread="「父母愿意做什么的东西都得」",
        note="",
    ),
    ProofTestCase(
        zhongwen="「于是我写了这忽然间的信给你」",
        yuewen="于是我写了这忽然间的信给你",
        yuewen_proofread="于是我写了这忽然间的信给你",
        note="",
    ),
    ProofTestCase(
        zhongwen="「虽然你不知道我是什么微细的东西」",
        yuewen="虽然你不知道我是什么微细的东西",
        yuewen_proofread="虽然你不知道我是什么微细的东西",
        note="",
    ),
    ProofTestCase(
        zhongwen="「但我的孩子很大，很大！」",
        yuewen="但我的孩子很大，很大！",
        yuewen_proofread="但我的孩子很大，很大！",
        note="",
    ),
    ProofTestCase(
        zhongwen="「有一天，你都会知道」",
        yuewen="「有一天你都会知道」",
        yuewen_proofread="「有一天你都会知道」",
        note="",
    ),
    ProofTestCase(
        zhongwen="「多谢合作！」",
        yuewen="「多谢合作！」",
        yuewen_proofread="「多谢合作！」",
        note="",
    ),
    ProofTestCase(
        zhongwen="「你忠实的，麦太」",
        yuewen="「你忠实的，麦太」",
        yuewen_proofread="「你忠实的，麦太」",
        note="",
    ),
]  # proof_test_cases_block_53
proof_test_cases_block_54 = [
    ProofTestCase(
        zhongwen="看完妈妈的信",
        yuewen="睇完妈妈封信后",
        yuewen_proofread="睇完妈妈封信后",
        note="",
    ),
    ProofTestCase(
        zhongwen="我决定回长洲继续学捡包山",
        yuewen="我决定返长洲继续抢包生",
        yuewen_proofread="我决定返长洲继续捡包山",
        note="Corrected '抢包生' to '捡包山' as '捡包山' is the correct term for "
        "the traditional activity, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="我不是为了见珊珊",
        yuewen="我唔系为咗见到山神",
        yuewen_proofread="我唔系为咗见珊珊",
        note="Corrected '山神' to '珊珊' as '山神' is a mishearing of the name '珊珊'.",
    ),
    ProofTestCase(
        zhongwen="我并不知道为什么要抢那些包",
        yuewen="我唔知点解要抢𠮶啲包",
        yuewen_proofread="我唔知点解要抢𠮶啲包",
        note="",
    ),
    ProofTestCase(
        zhongwen="我也不相信抢包山会成为奥运项目",
        yuewen="我亦唔信抢包生会成为奥运项目",
        yuewen_proofread="我亦唔信抢包山会成为奥运项目",
        note="Corrected '抢包生' to '抢包山' as '抢包山' is the correct term for "
        "the traditional event, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="可是，我依然努力练习抢包山",
        yuewen="但系，我依然努力练习抢包生",
        yuewen_proofread="但系，我依然努力练习抢包山",
        note="Corrected '抢包生' to '抢包山' as '抢包山' is the correct term for "
        "the traditional activity, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="因为，我爱我妈妈",
        yuewen="因为，我爱我妈妈",
        yuewen_proofread="因为，我爱我妈妈",
        note="",
    ),
    ProofTestCase(
        zhongwen="师傅说我攀爬功夫已经不错",
        yuewen="师傅话，我嘅攀爬功夫已经唔错",
        yuewen_proofread="师傅话，我嘅攀爬功夫已经唔错",
        note="",
    ),
    ProofTestCase(
        zhongwen="可以开始教我「十二路抢包手」",
        yuewen="可以开始教我「十二路抢包手」",
        yuewen_proofread="可以开始教我「十二路抢包手」",
        note="",
    ),
    ProofTestCase(
        zhongwen="师傅说当年师祖要出这套",
        yuewen="师傅话，当年师祖使出呢套",
        yuewen_proofread="师傅话，当年师祖要出呢套",
        note="Corrected '使出' to '要出' as '要出' matches the meaning of '要出' "
        "in the 中文, while '使出' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="「十二路抢包手」⋯",
        yuewen="十二路抢包手⋯",
        yuewen_proofread="十二路抢包手⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="连林世荣也大大赞好",
        yuewen="连林世荣睇见都大赞老爷",
        yuewen_proofread="连林世荣睇见都大大赞好",
        note="Corrected '大赞老爷' to '大大赞好' as '大大赞好' matches the meaning of "
        "'大大赞好' in the 中文, while '老爷' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="后来麦嘎告诉我⋯",
        yuewen="后来，默默话我知⋯",
        yuewen_proofread="后来，麦嘎话我知⋯",
        note="Corrected '默默' to '麦嘎' as it is a mishearing of the name "
        "'麦嘎', matching the 中文.",
    ),
    ProofTestCase(
        zhongwen="林世荣即是猪肉荣，是黄飞鸿的徒弟",
        yuewen="林世荣即系猪肉荣，系黄飞鸿嘅徒弟",
        yuewen_proofread="林世荣即系猪肉荣，系黄飞鸿嘅徒弟",
        note="",
    ),
    ProofTestCase(
        zhongwen="我不知道师傅像不像黄飞鸿",
        yuewen="我唔知到师傅似唔似黄飞鸿",
        yuewen_proofread="我唔知到师傅似唔似黄飞鸿",
        note="",
    ),
    ProofTestCase(
        zhongwen="我却肯定像一块猪肉",
        yuewen="但系我就肯定似旧猪肉",
        yuewen_proofread="但系我就肯定似旧猪肉",
        note="",
    ),
    ProofTestCase(
        zhongwen="我是一块堵住两个包",
        yuewen="我就系一个揸住两个包",
        yuewen_proofread="我就系一块堵住两个包",
        note="Corrected '一个揸住' to '一块堵住' as '堵住' matches the meaning of "
        "'堵住' in the 中文, while '揸住' (holding) is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="在长洲转来转去的猪肉",
        yuewen="喺长洲转嚟转去嘅猪肉",
        yuewen_proofread="喺长洲转嚟转去嘅猪肉",
        note="",
    ),
    ProofTestCase(
        zhongwen="我一边练习，一边胡思乱想；始终⋯",
        yuewen="我一边练习，一边乱练，一边谂嘢；始终⋯",
        yuewen_proofread="我一边练习，一边胡思乱想，一边谂嘢；始终⋯",
        note="Corrected '乱练' to '胡思乱想' as '乱练' is likely a mishearing of "
        "'胡思乱想', which matches the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="我还是不大喜欢抢包",
        yuewen="我都唔系咁钟意抢包",
        yuewen_proofread="我都唔系咁钟意抢包",
        note="",
    ),
    ProofTestCase(
        zhongwen="我只是爱我妈妈",
        yuewen="我净系爱我妈妈",
        yuewen_proofread="我净系爱我妈妈",
        note="",
    ),
    ProofTestCase(
        zhongwen="于是我咬实牙根⋯",
        yuewen="于是我咬细牙根⋯",
        yuewen_proofread="于是我咬实牙根⋯",
        note="Corrected '咬细牙根' to '咬实牙根' as '咬实' is the correct phrase "
        "meaning 'to grit one's teeth', matching the 中文.",
    ),
    ProofTestCase(
        zhongwen="一步一步，一爪一爪⋯",
        yuewen="一步一步，一爪一爪⋯",
        yuewen_proofread="一步一步，一爪一爪⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="我最后终于练成「十二路抢包手」",
        yuewen="最后，我终于练成十二路抢包手啦",
        yuewen_proofread="最后，我终于练成十二路抢包手啦",
        note="",
    ),
]  # proof_test_cases_block_54
proof_test_cases_block_55 = [
    ProofTestCase(
        zhongwen="喂，我是麦兜",
        yuewen="喂，我系麦兜啊",
        yuewen_proofread="喂，我系麦兜啊",
        note="",
    ),
    ProofTestCase(
        zhongwen="刚才的是小朋友麦兜，我是大个佬麦兜",
        yuewen="正话𠮶个系细路仔麦兜，我系大个佬麦兜",
        yuewen_proofread="正话𠮶个系细路仔麦兜，我系大个佬麦兜",
        note="",
    ),
    ProofTestCase(
        zhongwen="小朋友麦兜和大个佬麦兜除了声音不同⋯",
        yuewen="细路仔麦兜同大个佬麦兜除咗把声唔同之外⋯",
        yuewen_proofread="细路仔麦兜同大个佬麦兜除咗把声唔同之外⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="小朋友麦兜的世界仍然有好多幻想",
        yuewen="细路仔麦兜嘅世界仲有好多幻想",
        yuewen_proofread="细路仔麦兜嘅世界仲有好多幻想",
        note="",
    ),
    ProofTestCase(
        zhongwen="仍然有好多希望",
        yuewen="仲有好多希望",
        yuewen_proofread="仲有好多希望",
        note="",
    ),
    ProofTestCase(
        zhongwen="希望⋯失望⋯",
        yuewen="希望⋯失望⋯",
        yuewen_proofread="希望⋯失望⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="希望⋯",
        yuewen="希望⋯",
        yuewen_proofread="希望⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="失望",
        yuewen="失望",
        yuewen_proofread="失望",
        note="",
    ),
    ProofTestCase(
        zhongwen="久而久之，就变成大个佬麦兜",
        yuewen="搞咗一轮，就变咗大个佬麦兜",
        yuewen_proofread="搞咗一轮，就变咗大个佬麦兜",
        note="",
    ),
    ProofTestCase(
        zhongwen="我现在还是多说点小朋友麦兜",
        yuewen="不过，而家我都系想讲返细路仔麦兜",
        yuewen_proofread="不过，而家我都系想讲返细路仔麦兜",
        note="",
    ),
    ProofTestCase(
        zhongwen="小朋友麦兜仍然希望希望⋯",
        yuewen="细路仔麦兜仲系希望希望⋯",
        yuewen_proofread="细路仔麦兜仲系希望希望⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="希望真的有圣诞老人",
        yuewen="希望真系有圣诞老人",
        yuewen_proofread="希望真系有圣诞老人",
        note="",
    ),
    ProofTestCase(
        zhongwen="而且好想试试圣诞火鸡的滋味",
        yuewen="仲系好想好想试下圣诞火鸡嘅滋味",
        yuewen_proofread="仲系好想好想试下圣诞火鸡嘅滋味",
        note="",
    ),
    ProofTestCase(
        zhongwen="对，那时我还没吃过火鸡",
        yuewen="系啊，我𠮶阵我真系仲未食过火鸡",
        yuewen_proofread="系啊，我𠮶阵我真系仲未食过火鸡",
        note="",
    ),
    ProofTestCase(
        zhongwen="关于火鸡的一切⋯",
        yuewen="所有关于火鸡嘅嘢⋯",
        yuewen_proofread="所有关于火鸡嘅嘢⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="圣诞树上一闪一闪的饰物",
        yuewen="圣诞树一闪一闪嘅灯饰",
        yuewen_proofread="圣诞树一闪一闪嘅灯饰",
        note="",
    ),
    ProofTestCase(
        zhongwen="就像天上掉落的星星",
        yuewen="就好似喺天上面落嚟嘅星星噉",
        yuewen_proofread="就好似喺天上面落嚟嘅星星噉",
        note="",
    ),
    ProofTestCase(
        zhongwen="落到火炉旁边",
        yuewen="落喺火炉旁边",
        yuewen_proofread="落喺火炉旁边",
        note="",
    ),
    ProofTestCase(
        zhongwen="一片片比外边的雪还要白的鸡胸肉⋯",
        yuewen="一片一片，比窗外面嘅雪仲要白嘅鸡胸肉⋯",
        yuewen_proofread="一片一片，比窗外面嘅雪仲要白嘅鸡胸肉⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="就在我们跟前",
        yuewen="就喺我哋面前啦",
        yuewen_proofread="就喺我哋面前啦",
        note="",
    ),
    ProofTestCase(
        zhongwen="香气直入灵魂⋯",
        yuewen="香气直入灵魂⋯",
        yuewen_proofread="香气直入灵魂⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="连守在灵魂旁边的天使都醒过来",
        yuewen="就连守喺灵魂旁边嘅天使都醒咗起嚟",
        yuewen_proofread="就连守喺灵魂旁边嘅天使都醒咗起嚟",
        note="",
    ),
    ProofTestCase(
        zhongwen="围住这香而圣洁的肉⋯",
        yuewen="围住呢一嚿好香好香又好盛洁嘅肉⋯",
        yuewen_proofread="围住呢一嚿好香好香又好圣洁嘅肉⋯",
        note="Corrected '盛洁' to '圣洁' as '圣洁' is the correct term for "
        "'holy/pure', matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="在圣诞夜中飞呀，飞⋯",
        yuewen="喺圣诞夜里面飞呀，飞呀⋯",
        yuewen_proofread="喺圣诞夜里面飞呀，飞呀⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="这关于火鸡的一切，不过是我的想像",
        yuewen="但系呢一切一切关于火鸡嘅嘢，都不过系我嘅想像",
        yuewen_proofread="但系呢一切一切关于火鸡嘅嘢，都不过系我嘅想像",
        note="",
    ),
    ProofTestCase(
        zhongwen="我从来没吃过火鸡⋯",
        yuewen="因为我从来都未食过火鸡⋯",
        yuewen_proofread="因为我从来都未食过火鸡⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="连它的气味也没嗅过",
        yuewen="就连𠮶阵味都未闻过",
        yuewen_proofread="就连𠮶阵味都未闻过",
        note="",
    ),
    ProofTestCase(
        zhongwen="妈妈说火鸡太大",
        yuewen="妈妈话火鸡太大",
        yuewen_proofread="妈妈话火鸡太大",
        note="",
    ),
    ProofTestCase(
        zhongwen="我们一家两口，吃不下",
        yuewen="我哋一家两口，点食都食唔晒",
        yuewen_proofread="我哋一家两口，点食都食唔晒",
        note="",
    ),
    ProofTestCase(
        zhongwen="有年圣诞节妈妈买了半只烤鸭庆祝",
        yuewen="有一年圣诞节，妈妈买咗半边烧鸭庆祝",
        yuewen_proofread="有一年圣诞节，妈妈买咗半边烧鸭庆祝",
        note="",
    ),
    ProofTestCase(
        zhongwen="当时的我，十分十分失望",
        yuewen="当时我，真系十分十分之失望",
        yuewen_proofread="当时我，真系十分十分之失望",
        note="",
    ),
    ProofTestCase(
        zhongwen="又有一年，一间百货公司结业",
        yuewen="又有一年，有间大薄货公司倒闭",
        yuewen_proofread="又有一年，有间百货公司倒闭",
        note="Corrected '大薄货公司' to '百货公司' as '大薄货' is a mishearing of "
        "'百货', which matches the meaning of the original.",
    ),
    ProofTestCase(
        zhongwen="妈妈以四折买了个小小焗炉",
        yuewen="妈妈用四折买咗个焗炉仔返屋企",
        yuewen_proofread="妈妈用四折买咗个焗炉仔返屋企",
        note="",
    ),
    ProofTestCase(
        zhongwen="可能因为买了焗炉而技痒",
        yuewen="可能系因为买咗焗炉嘅样",
        yuewen_proofread="可能系因为买咗焗炉而技痒",
        note="Corrected '嘅样' to '而技痒' as '技痒' (itching to use one's "
        "skills) matches the meaning in the 中文, while '嘅样' is likely "
        "a mishearing.",
    ),
    ProofTestCase(
        zhongwen="那日妈妈竟然跟我说⋯",
        yuewen="𠮶日妈妈竟然同我讲⋯佢话",
        yuewen_proofread="𠮶日妈妈竟然同我讲⋯佢话",
        note="",
    ),
    ProofTestCase(
        zhongwen="让我们明天去超级市场揪火鸡",
        yuewen="明日我哋要超级市场抽火鸡",
        yuewen_proofread="明日我哋要超级市场揪火鸡",
        note="Corrected '抽火鸡' to '揪火鸡' as '揪' matches the meaning of 'to "
        "grab/catch' in the 中文, while '抽' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="我跟妈妈把火鸡揪回家的路上⋯",
        yuewen="我同妈妈抽住只火鸡行返屋企𠮶阵⋯",
        yuewen_proofread="我同妈妈揪住只火鸡行返屋企𠮶阵⋯",
        note="Corrected '抽住' to '揪住' as '揪住' (to pull/drag) matches the "
        "meaning of '揪回家' in the 中文, while '抽住' is likely a "
        "mishearing.",
    ),
    ProofTestCase(
        zhongwen="是我生命中最开心的时刻",
        yuewen="喺𠮶阵时我谂系我生命里面最开心嘅一刻",
        yuewen_proofread="喺𠮶阵时我谂系我生命里面最开心嘅一刻",
        note="",
    ),
    ProofTestCase(
        zhongwen="火鸡终于解冻了",
        yuewen="火鸡终于解冻啦",
        yuewen_proofread="火鸡终于解冻啦",
        note="",
    ),
    ProofTestCase(
        zhongwen="我学着妈妈，把双手涂满盐⋯",
        yuewen="我同妈妈噉双手查满盐⋯",
        yuewen_proofread="我同妈妈噉双手查满盐⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="在火鸡丰厚的鸡胸上擦呀，擦",
        yuewen="喺火鸡封口嘅鸡胸度，起细噉啫啫",
        yuewen_proofread="喺火鸡丰厚嘅鸡胸度，起细噉啫啫",
        note="Corrected '封口' to '丰厚' as '丰厚' matches the meaning of '丰厚' "
        "in the 中文, while '封口' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="妈妈不留神漏出了火鸡内的洋葱粒",
        yuewen="联火鸡时，妈妈一个唔觉意畀酿喺火鸡里面嘅火鸡内脏洋葱粒红萝虾粒",
        yuewen_proofread="联火鸡时，妈妈一个唔觉意畀酿喺火鸡里面嘅火鸡内脏洋葱粒红萝卜粒",
        note="Corrected '红萝虾粒' to '红萝卜粒' as '红萝卜' (carrot) matches the "
        "likely intended meaning, while '红萝虾' is a mishearing.",
    ),
    ProofTestCase(
        zhongwen="红萝卜粒",
        yuewen="流嘅出嚟",
        yuewen_proofread="",
        note="Cleared as '流嘅出嚟' bears no resemblance to the original "
        "phrase '红萝卜粒' and is clearly a complete transcription "
        "failure.",
    ),
    ProofTestCase(
        zhongwen="我说：火鸡「疴烂煮」！",
        yuewen="我话：火鸡我能住呀！火鸡",
        yuewen_proofread="",
        note="Cleared as '火鸡我能住呀！火鸡' bears no resemblance to the original "
        "phrase '火鸡「疴烂煮」！' and is clearly a complete transcription "
        "failure.",
    ),
    ProofTestCase(
        zhongwen="好勉强把火鸡塞进焗炉内",
        yuewen="好勉强噏咗入焗炉度",
        yuewen_proofread="好勉强塞咗入焗炉度",
        note="Corrected '噏咗' to '塞咗' as '塞' (to stuff) matches the meaning "
        "of '塞进' in the 中文, while '噏' is a mishearing.",
    ),
    ProofTestCase(
        zhongwen="12月24日",
        yuewen="10月24日",
        yuewen_proofread="12月24日",
        note="Corrected '10月24日' to '12月24日' as the month was misheard; "
        "the correct date is December 24th, not October 24th.",
    ),
    ProofTestCase(
        zhongwen="上升的白烟跟奇异的焦味拨动星星",
        yuewen="上升嘅白烟同奇异嘅㶶味拨动声声",
        yuewen_proofread="上升嘅白烟同奇异嘅焦味拨动星星",
        note="Corrected '㶶味' to '焦味' as '焦味' is the correct term for "
        "'burnt smell', and '声声' to '星星' to match the meaning of '星星' "
        "in the 中文; both are likely mishearings.",
    ),
    ProofTestCase(
        zhongwen="焗炉戚戚恻恻，戚戚恻恻⋯",
        yuewen="个焗炉叱叱叱叱，叱叱叱咁⋯",
        yuewen_proofread="个焗炉戚戚恻恻，戚戚恻恻咁⋯",
        note="Corrected '叱叱叱叱' to '戚戚恻恻' as it is a mishearing of the "
        "onomatopoeic phrase '戚戚恻恻', matching the original meaning.",
    ),
    ProofTestCase(
        zhongwen="有如天使预早送来的福音",
        yuewen="就好似天赐预祖畀我哋嘅福音",
        yuewen_proofread="就好似天使预早畀我哋嘅福音",
        note="Corrected '天赐预祖' to '天使预早' as '天使预早' matches the meaning of "
        "'天使预早送来的福音', while '天赐预祖' is likely a mishearing.",
    ),
]  # proof_test_cases_block_55
proof_test_cases_block_56 = [
    ProofTestCase(
        zhongwen="好靓的晚上啊！",
        yuewen="好靓嘅夜晚呀！",
        yuewen_proofread="好靓嘅夜晚呀！",
        note="",
    ),
    ProofTestCase(
        zhongwen="我和妈妈坐在尖东海傍",
        yuewen="我同妈妈坐喺尖东海旁",
        yuewen_proofread="我同妈妈坐喺尖东海旁",
        note="",
    ),
    ProofTestCase(
        zhongwen="点点灯光在海面走来走去⋯",
        yuewen="点点点点嘅灯光喺海上面走来走去⋯",
        yuewen_proofread="点点灯光喺海上面走来走去⋯",
        note="Removed the repeated '点点点点嘅' and replaced with '点点' to match "
        "the intended meaning of '点点灯光' (spots of light), as the "
        "repetition is likely a mishearing or stutter.",
    ),
    ProofTestCase(
        zhongwen="美丽又温柔",
        yuewen="又靓又温柔",
        yuewen_proofread="又靓又温柔",
        note="",
    ),
    ProofTestCase(
        zhongwen="真的好靓！",
        yuewen="真系好靓！",
        yuewen_proofread="真系好靓！",
        note="",
    ),
]  # proof_test_cases_block_56
proof_test_cases_block_57 = [
    ProofTestCase(
        zhongwen="我从没吃过这么浓味的东西",
        yuewen="我从未食过咁浓味嘅嘢",
        yuewen_proofread="我从未食过咁浓味嘅嘢",
        note="",
    ),
    ProofTestCase(
        zhongwen="甚至杯面，烧鸭的味道也没有这么浓",
        yuewen="连烧鸭连杯面都冇咁浓嘅味道",
        yuewen_proofread="连烧鸭连杯面都冇咁浓嘅味道",
        note="",
    ),
    ProofTestCase(
        zhongwen="火鸡的味道把我每一个味蕾缠住⋯",
        yuewen="火鸡嘅味道喺我嘅每一个味蕾度缠住⋯",
        yuewen_proofread="火鸡嘅味道喺我嘅每一个味蕾度缠住⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="爆发⋯缠住⋯爆发⋯",
        yuewen="爆发⋯缠住⋯爆发⋯",
        yuewen_proofread="爆发⋯缠住⋯爆发⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="就像今晚的一切",
        yuewen="就好似今晚嘅嘢噉",
        yuewen_proofread="就好似今晚嘅嘢噉",
        note="",
    ),
    ProofTestCase(
        zhongwen="最靓最靓，最犀利，而且最温柔",
        yuewen="最靓，最靓，最犀利，亦都系最温柔",
        yuewen_proofread="最靓，最靓，最犀利，亦都系最温柔",
        note="",
    ),
]  # proof_test_cases_block_57
proof_test_cases_block_58 = [
    ProofTestCase(
        zhongwen="第二天我睡得很晏⋯",
        yuewen="第二日我瞓到好硬⋯",
        yuewen_proofread="第二日我瞓到好晏⋯",
        note="Corrected '好硬' to '好晏' as '好晏' (very late) matches the "
        "meaning of '很晏', while '好硬' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="刷过牙我还感觉到火鸡的美味",
        yuewen="测完牙，我仲感觉到火鸡嘅美味",
        yuewen_proofread="刷完牙，我仲感觉到火鸡嘅美味",
        note="Corrected '测完牙' to '刷完牙' as '刷牙' is the correct term for "
        "brushing teeth, matching the meaning of '刷过牙' in the 中文.",
    ),
    ProofTestCase(
        zhongwen="因为早餐吃得晚⋯",
        yuewen="因为早餐食得硬⋯",
        yuewen_proofread="因为早餐食得晏⋯",
        note="Corrected '食得硬' to '食得晏' as '晏' (late) matches the meaning "
        "of '吃得晚', while '硬' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="午餐时妈妈只煮了罐栗米汤",
        yuewen="唔餐妈妈净系整咗罐粟米汤畀我",
        yuewen_proofread="午餐妈妈净系整咗罐粟米汤畀我",
        note="Corrected '唔餐' to '午餐' as '唔餐' is a mishearing of '午餐', "
        "which matches the meaning of the original sentence.",
    ),
    ProofTestCase(
        zhongwen="我用汤匙撩了两下",
        yuewen="我系噉用匙羹撩下撩下",
        yuewen_proofread="我系噉用匙羹撩下撩下",
        note="",
    ),
    ProofTestCase(
        zhongwen="竟然发现美味的火鸡粒",
        yuewen="我竟然撩到一粒美味嘅火鸡肉",
        yuewen_proofread="我竟然撩到一粒美味嘅火鸡肉",
        note="",
    ),
    ProofTestCase(
        zhongwen="不用说，那夜就是我渴望了⋯",
        yuewen="𠮶晚唔使讲⋯",
        yuewen_proofread="𠮶晚唔使讲⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="很久很久很久的⋯圣诞火鸡大餐！",
        yuewen="当然系食我限咗好耐好耐好耐好耐嘅⋯圣诞火鸡大餐！",
        yuewen_proofread="当然系食我限咗好耐好耐好耐好耐嘅⋯圣诞火鸡大餐！",
        note="",
    ),
    ProofTestCase(
        zhongwen="一片片的火鸡肉和伴碟的薯仔和节瓜⋯",
        yuewen="一片一片嘅火鸡肉半碟嘅有薯仔同节瓜⋯",
        yuewen_proofread="一片一片嘅火鸡肉同伴碟嘅薯仔同节瓜⋯",
        note="Corrected '半碟嘅有薯仔' to '同伴碟嘅薯仔' as '伴碟' (garnish/side) "
        "matches the meaning in the 中文, while '半碟' is likely a "
        "mishearing.",
    ),
    ProofTestCase(
        zhongwen="上面淋了老抽生粉献",
        yuewen="上面淋咗一层老抽生粉馅",
        yuewen_proofread="上面淋咗一层老抽生粉献",
        note="Corrected '馅' to '献' as '献' (gravy/sauce) matches the "
        "meaning of the 中文, while '馅' (filling) is likely a "
        "mishearing.",
    ),
    ProofTestCase(
        zhongwen="我们真的好兴奋，好满足",
        yuewen="我哋真系好兴奋，好满足",
        yuewen_proofread="我哋真系好兴奋，好满足",
        note="",
    ),
    ProofTestCase(
        zhongwen="之后，我们吃了一个星期的⋯",
        yuewen="之后我哋仲食咗一个礼拜嘅⋯火鸡三文治",
        yuewen_proofread="之后我哋仲食咗一个礼拜嘅⋯火鸡三文治",
        note="",
    ),
    ProofTestCase(
        zhongwen="火鸡三文治早餐",
        yuewen="做早餐",
        yuewen_proofread="",
        note="Cleared as '做早餐' bears no resemblance to the original phrase "
        "'火鸡三文治早餐' and is clearly a complete transcription failure.",
    ),
    ProofTestCase(
        zhongwen="星期天",
        yuewen="星期日",
        yuewen_proofread="星期日",
        note="",
    ),
    ProofTestCase(
        zhongwen="我大着胆跟妈妈说：不如去饮茶吖",
        yuewen="我嘅记心肝同妈妈讲：不如饮茶",
        yuewen_proofread="我大着胆同妈妈讲：不如饮茶",
        note="Corrected '我嘅记心肝' to '我大着胆' as '记心肝' is a mishearing of "
        "'大着胆', which matches the meaning of the 中文.",
    ),
    ProofTestCase(
        zhongwen="妈妈骂我「冇衣食」⋯",
        yuewen="妈妈闹我「冇意食」⋯",
        yuewen_proofread="妈妈闹我「冇衣食」⋯",
        note="Corrected '冇意食' to '冇衣食' as '冇衣食' (no food or clothing) "
        "matches the meaning in the 中文, while '冇意食' is likely a "
        "mishearing.",
    ),
    ProofTestCase(
        zhongwen="不过还是带了我去饮茶",
        yuewen="但系都带咗我去饮茶",
        yuewen_proofread="但系都带咗我去饮茶",
        note="",
    ),
    ProofTestCase(
        zhongwen="之后，妈妈又有计⋯",
        yuewen="之后妈妈又有计⋯",
        yuewen_proofread="之后妈妈又有计⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="她把冰箱内剩下来的火鸡肉撕呀撕",
        yuewen="佢将雪柜净返嘅火鸡肉系噉撕系噉撕",
        yuewen_proofread="佢将雪柜净返嘅火鸡肉系噉撕系噉撕",
        note="",
    ),
    ProofTestCase(
        zhongwen="有时候也叫我帮手撕",
        yuewen="有时都叫我帮手撕",
        yuewen_proofread="有时都叫我帮手撕",
        note="",
    ),
    ProofTestCase(
        zhongwen="火鸡留在指甲的味道",
        yuewen="火鸡留喺指甲𠮶阵味",
        yuewen_proofread="火鸡留喺指甲𠮶阵味",
        note="",
    ),
    ProofTestCase(
        zhongwen="原来得洗好多次",
        yuewen="原来洗好多次都仲喺度㗎",
        yuewen_proofread="原来洗好多次都仲喺度㗎",
        note="",
    ),
    ProofTestCase(
        zhongwen="银芽火鸡丝炒米，好味道",
        yuewen="银牙火鸡丝炒米，好味道噉",
        yuewen_proofread="银芽火鸡丝炒米，好味道噉",
        note="Corrected '银牙' to '银芽' as '银芽' (bean sprouts) is the correct "
        "ingredient, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="栗子炆火鸡丝㷛",
        yuewen="焯焯栗子焖火鸡丝煲",
        yuewen_proofread="栗子焖火鸡丝煲",
        note="Removed the duplicated '焯焯' at the beginning, which is "
        "likely a mishearing or extraneous, to match the intended "
        "meaning of '栗子炆火鸡丝㷛'.",
    ),
    ProofTestCase(
        zhongwen="花生火鸡骨煲粥",
        yuewen="花生火鸡骨煲粥",
        yuewen_proofread="花生火鸡骨煲粥",
        note="",
    ),
    ProofTestCase(
        zhongwen="纸包火鸡包包纸",
        yuewen="纸包火鸡包包纸",
        yuewen_proofread="纸包火鸡包包纸",
        note="",
    ),
    ProofTestCase(
        zhongwen="包火鸡包包包火鸡包",
        yuewen="包火鸡包包包火鸡包",
        yuewen_proofread="包火鸡包包包火鸡包",
        note="",
    ),
    ProofTestCase(
        zhongwen="酿火鸡馅搽面包",
        yuewen="让火鸡馅茶面包",
        yuewen_proofread="酿火鸡馅搽面包",
        note="Corrected '让' to '酿' and '茶' to '搽' as both are likely "
        "mishearings; '酿火鸡馅搽面包' matches the meaning of the original "
        "phrase about spreading turkey stuffing on bread.",
    ),
    ProofTestCase(
        zhongwen="唉，我好后悔讲过一句「火鸡疴烂煮」",
        yuewen="唉，我后悔讲过火鸡阿宁处呢句嘢",
        yuewen_proofread="唉，我后悔讲过火鸡疴烂煮呢句嘢",
        note="Corrected '阿宁处' to '疴烂煮' as '疴烂煮' is the correct phrase "
        "matching the original '火鸡疴烂煮'.",
    ),
    ProofTestCase(
        zhongwen="端午节，当我翻开我最喜欢吃的裹蒸粽⋯",
        yuewen="到端午节，当我督开我最钟意食嘅果精粽嘅时候⋯",
        yuewen_proofread="到端午节，当我督开我最钟意食嘅裹蒸粽嘅时候⋯",
        note="Corrected '果精粽' to '裹蒸粽' as '裹蒸粽' is the correct term for "
        "the type of rice dumpling mentioned in the 中文, and '果精粽' is "
        "a likely mishearing.",
    ),
    ProofTestCase(
        zhongwen="发现咸蛋旁边是一件火鸡背的时候⋯",
        yuewen="发现宿喺咸蛋旁边嘅系一件火鸡背脊⋯",
        yuewen_proofread="发现宿喺咸蛋旁边嘅系一件火鸡背脊⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="我脑部一时想唔通，哭起来",
        yuewen="我脑部一时想唔通，喊咗起上嚟",
        yuewen_proofread="我脑部一时想唔通，喊咗起上嚟",
        note="",
    ),
    ProofTestCase(
        zhongwen="救命呀！",
        yuewen="救命啊！",
        yuewen_proofread="救命啊！",
        note="",
    ),
    ProofTestCase(
        zhongwen="妈妈悄悄把剩下的火鸡扔掉",
        yuewen="妈妈净计计将净低嘅火鸡劈咗",
        yuewen_proofread="妈妈静鸡鸡将净低嘅火鸡劈咗",
        note="Corrected '净计计' to '静鸡鸡' as '静鸡鸡' is the correct Cantonese "
        "phrase for 'quietly' or 'secretly', matching the meaning of "
        "'悄悄' in the 中文.",
    ),
    ProofTestCase(
        zhongwen="那已经是火鸡解冻后差不多半年的事",
        yuewen="原来𠮶阵已经系只火鸡解冻咗差唔多半年后嘅事",
        yuewen_proofread="原来𠮶阵已经系只火鸡解冻咗差唔多半年后嘅事",
        note="",
    ),
    ProofTestCase(
        zhongwen="我的美梦跟恶梦亦同时完结",
        yuewen="我嘅美梦同噩梦，都同时完结",
        yuewen_proofread="我嘅美梦同噩梦，都同时完结",
        note="",
    ),
    ProofTestCase(
        zhongwen="后来我才知道⋯",
        yuewen="后来我先知道⋯",
        yuewen_proofread="后来我先知道⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="一只火鸡由出世到给人宰掉",
        yuewen="一只火鸡由出世到畀人㓥",
        yuewen_proofread="一只火鸡由出世到畀人㓥",
        note="",
    ),
    ProofTestCase(
        zhongwen="也不过是几个月间的事",
        yuewen="都不过系几个月之间嘅事",
        yuewen_proofread="都不过系几个月之间嘅事",
        note="",
    ),
    ProofTestCase(
        zhongwen="即是说，火鸡死掉后跟我们一起的日子",
        yuewen="即系话，只火鸡死咗之后，同我哋一齐嘅日子",
        yuewen_proofread="即系话，火鸡死咗之后，同我哋一齐嘅日子",
        note="Removed '只' before '火鸡' as it is likely a mishearing and not "
        "present in the original meaning.",
    ),
    ProofTestCase(
        zhongwen="还要长过它的一生",
        yuewen="仲长过佢自己本身条命",
        yuewen_proofread="仲长过佢自己本身条命",
        note="",
    ),
    ProofTestCase(
        zhongwen="我还发觉，火鸡的味道⋯",
        yuewen="我仲发觉到，火鸡嘅味道⋯",
        yuewen_proofread="我仲发觉到，火鸡嘅味道⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="将吃未吃和第一口之间已经是最高峰",
        yuewen="味食同食第一啖之间已经系佢嘅最高峰",
        yuewen_proofread="未食同食第一啖之间已经系佢嘅最高峰",
        note="Corrected '味食' to '未食' as '未食' (not yet eaten) matches the "
        "meaning of '将吃未吃' in the 中文, while '味食' is likely a "
        "mishearing.",
    ),
    ProofTestCase(
        zhongwen="之后的，不过是开始了也就吃下去",
        yuewen="之后，不过都系食开就食埋落去噉解",
        yuewen_proofread="之后，不过都系食开就食埋落去噉解",
        note="",
    ),
    ProofTestCase(
        zhongwen="我没有哲学家的头脑⋯",
        yuewen="我冇知学家嘅头脑⋯",
        yuewen_proofread="我冇哲学家嘅头脑⋯",
        note="Corrected '知学家' to '哲学家' as '哲学家' is the correct term for "
        "'philosopher', matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="不知道两件事情应该得出什么道理",
        yuewen="唔知呢两样嘢要得起嘅呢个，得出啲咩道理",
        yuewen_proofread="唔知呢两样嘢要得出啲咩道理",
        note="Removed '得起嘅呢个' as it is likely a mishearing and does not "
        "fit the context of '得出什么道理'.",
    ),
    ProofTestCase(
        zhongwen="可是这些想法⋯",
        yuewen="但系呢啲谂法⋯",
        yuewen_proofread="但系呢啲谂法⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="在我长大后⋯",
        yuewen="喺我长大之后⋯",
        yuewen_proofread="喺我长大之后⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="在一些跟圣诞节无关的日子⋯",
        yuewen="系一啲同圣诞节无关嘅日子⋯",
        yuewen_proofread="系一啲同圣诞节无关嘅日子⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="毫无因由的在我脑中出现过三两次",
        yuewen="无端端噉喺我脑部出现过两三次",
        yuewen_proofread="无端端噉喺我脑部出现过两三次",
        note="",
    ),
    ProofTestCase(
        zhongwen="一次，是在我自己的婚宴上",
        yuewen="一次，喺我自己嘅婚宴上",
        yuewen_proofread="一次，喺我自己嘅婚宴上",
        note="",
    ),
    ProofTestCase(
        zhongwen="一次⋯",
        yuewen="一次⋯",
        yuewen_proofread="一次⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="是在我妈妈火化那天",
        yuewen="喺我妈妈火化𠮶日",
        yuewen_proofread="喺我妈妈火化𠮶日",
        note="",
    ),
    ProofTestCase(
        zhongwen="那天，我看着天空几缕灰色的烟",
        yuewen="𠮶日，我望住天东几条灰色嘅烟",
        yuewen_proofread="𠮶日，我望住天空几条灰色嘅烟",
        note="Corrected '天东' to '天空' as '天东' is likely a mishearing of "
        "'天空', which matches the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="忽然间嗅到火鸡又浓又淡的气味",
        yuewen="忽然闻到火鸡又浓又淡嘅气味",
        yuewen_proofread="忽然闻到火鸡又浓又淡嘅气味",
        note="",
    ),
    ProofTestCase(
        zhongwen="我好后悔要妈妈扔掉最后几件火鸡",
        yuewen="我后悔，要妈妈劈咗个忌廉，火鸡",
        yuewen_proofread="我后悔，要妈妈劈咗个火鸡，火鸡",
        note="Corrected '忌廉' to '火鸡' as '忌廉' (cream) is a mishearing of "
        "'火鸡' (turkey), which matches the context of the 中文.",
    ),
]  # proof_test_cases_block_58
proof_test_cases_block_59 = [
    ProofTestCase(
        zhongwen="特别报告",
        yuewen="特别报道",
        yuewen_proofread="特别报告",
        note="Corrected '报道' to '报告' as '报告' matches the meaning of "
        "'report' in the 中文, while '报道' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="奥运金牌得主李丽珊决定参加今届奥运",
        yuewen="奥运滑浪风帆金牌得主李丽珊决定参加今届嘅奥运",
        yuewen_proofread="奥运滑浪风帆金牌得主李丽珊决定参加今届嘅奥运",
        note="",
    ),
    ProofTestCase(
        zhongwen="向全世界人再次证明⋯",
        yuewen="向全世界人再次证明⋯",
        yuewen_proofread="向全世界人再次证明⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="香港运动员不是腊鸭",
        yuewen="香港嘅运动员唔系腊鸭",
        yuewen_proofread="香港嘅运动员唔系腊鸭",
        note="",
    ),
    ProofTestCase(
        zhongwen="另方面⋯",
        yuewen="另一方面⋯",
        yuewen_proofread="另一方面⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="香港体运总会霍震霆⋯",
        yuewen="中国香港体育协会企奥委会会长霍振庭⋯",
        yuewen_proofread="中国香港体育协会暨奥委会会长霍震霆⋯",
        note="Corrected '企奥委会' to '暨奥委会' and '霍振庭' to '霍震霆' as these are "
        "likely mishearings of the correct terms and names.",
    ),
    ProofTestCase(
        zhongwen="正式向亚运协会提出申请",
        yuewen="正式向亚运协会提出申请",
        yuewen_proofread="正式向亚运协会提出申请",
        note="",
    ),
    ProofTestCase(
        zhongwen="香港将争夺下届亚运会主办权",
        yuewen="香港将要争夺下届亚运会嘅主办权",
        yuewen_proofread="香港将要争夺下届亚运会嘅主办权",
        note="",
    ),
    ProofTestCase(
        zhongwen="多个运动团体立即表示热烈支持",
        yuewen="多个运动团体立即表示热烈支持",
        yuewen_proofread="多个运动团体立即表示热烈支持",
        note="",
    ),
    ProofTestCase(
        zhongwen="其中港九新界竹战联谊会⋯",
        yuewen="其中港狗新界足战联谊会⋯",
        yuewen_proofread="其中港九新界竹战联谊会⋯",
        note="Corrected '港狗' to '港九' and '足战' to '竹战' as these are likely "
        "mishearings of the correct terms in the context of the "
        "association's name.",
    ),
    ProofTestCase(
        zhongwen="更希望打麻将可以成为亚运项目",
        yuewen="更希望打麻雀可以成为亚运项目",
        yuewen_proofread="更希望打麻雀可以成为亚运项目",
        note="",
    ),
    ProofTestCase(
        zhongwen="另外，全港茶餐厅员工协会⋯",
        yuewen="另外⋯",
        yuewen_proofread="另外⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="经已发动所有会员⋯",
        yuewen="全港茶餐厅联工协会经热发动所有会员⋯",
        yuewen_proofread="全港茶餐厅联工协会经已发动所有会员⋯",
        note="Corrected '经热' to '经已' as '经已' is the correct term for "
        "'already', matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="争取「掷蛋挞」成为亚运比赛项目",
        yuewen="争取掟蛋挞成为亚运会比赛项目",
        yuewen_proofread="争取掟蛋挞成为亚运会比赛项目",
        note="",
    ),
    ProofTestCase(
        zhongwen="港九烧味卤味腊味同业会",
        yuewen="港狗烧尾掳尾立尾同业会",
        yuewen_proofread="港九烧味卤味腊味同业会",
        note="Corrected '港狗烧尾掳尾立尾' to '港九烧味卤味腊味' as the original was a "
        "mishearing of the association's name.",
    ),
    ProofTestCase(
        zhongwen="亦向霍主席当面提出⋯",
        yuewen="亦都向霍主席当面提出⋯",
        yuewen_proofread="亦都向霍主席当面提出⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="「挂腊鸭」可以成为亚运比赛项目",
        yuewen="挂立鸭可以成为亚运比赛项目",
        yuewen_proofread="挂腊鸭可以成为亚运比赛项目",
        note="Corrected '挂立鸭' to '挂腊鸭' as '挂腊鸭' is the correct term for "
        "the preserved duck, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="较为特别的是，CIC保险营业员联同⋯",
        yuewen="较为特别嘅系，CIC保险营业员联同⋯",
        yuewen_proofread="较为特别嘅系，CIC保险营业员联同⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="大角咀春田花花幼稚园⋯",
        yuewen="大角嘴春田花花幼稚园⋯",
        yuewen_proofread="大角咀春田花花幼稚园⋯",
        note="Corrected '大角嘴' to '大角咀' as '大角咀' is the correct place name, "
        "matching the 中文.",
    ),
    ProofTestCase(
        zhongwen="附属小学一班小朋友⋯",
        yuewen="附属小学嘅一班小朋友⋯",
        yuewen_proofread="附属小学嘅一班小朋友⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="争取「抢包山」",
        yuewen="争取「抢包山」",
        yuewen_proofread="争取「抢包山」",
        note="",
    ),
    ProofTestCase(
        zhongwen="一项几乎绝迹的运动⋯",
        yuewen="一项几乎绝迹嘅运动⋯",
        yuewen_proofread="一项几乎绝迹嘅运动⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="成为本港举办亚运的重点推介比赛项目",
        yuewen="成为本港举办亚运重点推介嘅比赛项目",
        yuewen_proofread="成为本港举办亚运重点推介嘅比赛项目",
        note="",
    ),
]  # proof_test_cases_block_59
proof_test_cases_block_60 = [
    ProofTestCase(
        zhongwen="最后⋯",
        yuewen="最后，最后⋯",
        yuewen_proofread="最后，最后⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="最后，一切成烟",
        yuewen="全部都系banana",
        yuewen_proofread="",
        note="Cleared as '全部都系banana' bears no resemblance to the original "
        "phrase '最后，一切成烟' and is clearly a complete transcription "
        "failure.",
    ),
    ProofTestCase(
        zhongwen="最后，他们选了「掷蛋挞」做推介项目",
        yuewen="最后佢哋选咗定蛋挞做推介项目",
        yuewen_proofread="最后佢哋选咗掷蛋挞做推介项目",
        note="Corrected '定蛋挞' to '掷蛋挞' as '掷蛋挞' matches the meaning of the "
        "original '掷蛋挞' (throwing egg tarts), while '定蛋挞' is likely a "
        "mishearing.",
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
        note="Corrected '李利山' to '李丽珊' as it is a mishearing of the name, "
        "and '丧乱' to '蝉联' as '蝉联' is the correct term for defending a "
        "title, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="亦由一个香港人从未听过的地方夺得",
        yuewen="亚运主办权亦都由一个香港人从未听过嘅地方夺得",
        yuewen_proofread="亚运主办权亦都由一个香港人从未听过嘅地方夺得",
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
        note="Corrected '钉' to '掷' as '掷' (to throw) matches the meaning "
        "of the original 中文, while '钉' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="一切回复正常",
        yuewen="一切回复正常",
        yuewen_proofread="一切回复正常",
        note="",
    ),
]  # proof_test_cases_block_60
proof_test_cases_block_61 = [
    ProofTestCase(
        zhongwen="上中学后，我再没有练习抢包手",
        yuewen="上个中学，我已经再冇练习抢包手",
        yuewen_proofread="上个中学，我已经再冇练习抢包手",
        note="",
    ),
    ProofTestCase(
        zhongwen="有时候跟妈妈饮茶⋯",
        yuewen="间中同妈妈饮茶⋯",
        yuewen_proofread="间中同妈妈饮茶⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="我都会手快快替她抢一笼大包",
        yuewen="我都会手快快噉帮佢抢龙大包",
        yuewen_proofread="我都会手快快噉帮佢抢一笼大包",
        note="Added '一笼' to correct the omission, as '抢龙大包' is likely a "
        "mishearing of '抢一笼大包'.",
    ),
    ProofTestCase(
        zhongwen="之后，茶楼再不卖大包了",
        yuewen="之后，茶楼都冇埋大包",
        yuewen_proofread="之后，茶楼都冇卖大包",
        note="Corrected '冇埋大包' to '冇卖大包' as '冇埋' is likely a mishearing of "
        "'冇卖', which matches the meaning of '再不卖' in the 中文.",
    ),
    ProofTestCase(
        zhongwen="点心车亦转成点心纸",
        yuewen="退车仔都转咗用点心纸",
        yuewen_proofread="点心车仔都转咗用点心纸",
        note="Corrected '退车仔' to '点心车仔' as '点心车' is the correct term for "
        "dim sum cart, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="一切落空",
        yuewen="一切都落空",
        yuewen_proofread="一切都落空",
        note="",
    ),
]  # proof_test_cases_block_61
proof_test_cases_block_62 = [
    ProofTestCase(
        zhongwen="有时候我也会跟同学回到长洲烧烤",
        yuewen="有时我都会同班同学仔返长洲宵夜食",
        yuewen_proofread="有时我都会同班同学仔返长洲烧烤食",
        note="Corrected '宵夜' to '烧烤' as '烧烤' matches the activity "
        "described in the 中文, while '宵夜' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="每次看见师傅⋯",
        yuewen="每次见到师傅⋯",
        yuewen_proofread="每次见到师傅⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="他都好像老了一点",
        yuewen="佢都好似老咗啲噉",
        yuewen_proofread="佢都好似老咗啲噉",
        note="",
    ),
]  # proof_test_cases_block_62
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
        note="Corrected '厂包' to '抢包' as '抢包' is the correct term for the "
        "bun-snatching event, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="师傅说，那阵胶气，相当臭",
        yuewen="师傅话𠮶阵胶气，都几丑下",
        yuewen_proofread="师傅话𠮶阵胶气，都几臭下",
        note="Corrected '丑' to '臭' as '臭' is the correct word for "
        "'smelly', matching the meaning of '相当臭' in the 中文.",
    ),
]  # proof_test_cases_block_63
proof_test_cases_block_64 = [
    ProofTestCase(
        zhongwen="长洲有个张保仔洞",
        yuewen="墙后个张宝仔洞",
        yuewen_proofread="长洲有个张保仔洞",
        note="Corrected '墙后' to '长洲' as it is a mishearing of the place "
        "name '长洲', and '张宝仔' to '张保仔' to match the correct name of "
        "the cave.",
    ),
    ProofTestCase(
        zhongwen="听说张保仔在洞内藏了很多宝藏",
        yuewen="听讲海盗张宝仔喺里面收埋咗好多宝藏",
        yuewen_proofread="听讲海盗张保仔喺里面收埋咗好多宝藏",
        note="Corrected '张宝仔' to '张保仔' as '张保仔' is the correct name, "
        "matching the 中文.",
    ),
    ProofTestCase(
        zhongwen="因为我练过抢包手，身手比较灵活⋯",
        yuewen="因为我练过抢包手，身手比较灵活⋯",
        yuewen_proofread="因为我练过抢包手，身手比较灵活⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="同学们叫我爬进去看看，说不定会发达",
        yuewen="班同我叫我爬佢睇下，话唔定会发达",
        yuewen_proofread="班同学叫我爬入去睇下，话唔定会发达",
        note="Corrected '班同我' to '班同学' as '同我' is a likely mishearing of "
        "'同学'; changed '爬佢' to '爬入去' as '爬入去' (crawl in) matches the "
        "meaning of '爬进去', while '爬佢' is a mishearing.",
    ),
    ProofTestCase(
        zhongwen="于是我就向着这个又黑又窄的洞⋯",
        yuewen="于是我就向住呢一个又黑又窄嘅洞⋯",
        yuewen_proofread="于是我就向住呢一个又黑又窄嘅洞⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="一直爬",
        yuewen="系噉爬爬",
        yuewen_proofread="系噉爬爬",
        note="",
    ),
    ProofTestCase(
        zhongwen="洞里面什么也没有，只有一个盒",
        yuewen="洞里面乜都冇，净系有一个盒",
        yuewen_proofread="洞里面乜都冇，净系有一个盒",
        note="",
    ),
    ProofTestCase(
        zhongwen="我小心揭开盒⋯",
        yuewen="我好小心揭开呢个盒⋯",
        yuewen_proofread="我好小心揭开呢个盒⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="发现里面一个没吃完的大包",
        yuewen="发现入面系一个食净咗嘅大包",
        yuewen_proofread="发现入面系一个食剩咗嘅大包",
        note="Corrected '食净咗' to '食剩咗' as '食剩' is the correct term for "
        "'leftover' or 'not finished eating', matching the meaning of "
        "'没吃完'.",
    ),
    ProofTestCase(
        zhongwen="是不是张保仔吃过的呢？",
        yuewen="唔知系咪张宝仔食净㗎啦？",
        yuewen_proofread="唔知系咪张保仔食净㗎啦？",
        note="Corrected '张宝仔' to '张保仔' as '张保仔' is the correct historical "
        "figure referenced in the 中文.",
    ),
    ProofTestCase(
        zhongwen="揸住个包，我忽然明白⋯",
        yuewen="揸住个包，我忽然明白⋯",
        yuewen_proofread="揸住个包，我忽然明白⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="原来有些事情， 没有就是没有",
        yuewen="原来有啲嘢，冇就真系冇",
        yuewen_proofread="原来有啲嘢，冇就真系冇",
        note="",
    ),
    ProofTestCase(
        zhongwen="唔得，就是唔得",
        yuewen="唔得，就真系唔得",
        yuewen_proofread="唔得，就真系唔得",
        note="",
    ),
    ProofTestCase(
        zhongwen="没有鱼蛋没有粗面没去成马尔代夫⋯",
        yuewen="冇鱼蛋，冇粗面，冇去买义大夫⋯",
        yuewen_proofread="冇鱼蛋，冇粗面，冇去马尔代夫⋯",
        note="Corrected '买义大夫' to '马尔代夫' as it is a mishearing of the "
        "place name '马尔代夫' (Maldives).",
    ),
    ProofTestCase(
        zhongwen="没有奖牌没有张保仔宝藏",
        yuewen="冇奖牌冇张宝仔宝藏",
        yuewen_proofread="冇奖牌冇张保仔宝藏",
        note="Corrected '宝仔' to '保仔' as '保仔' is the correct name for "
        "'张保仔', matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="而张保仔，也没有咬过那个包",
        yuewen="而张宝仔，亦都冇咬过个包",
        yuewen_proofread="而张保仔，亦都冇咬过个包",
        note="Corrected '张宝仔' to '张保仔' as '张保仔' is the correct historical "
        "name, matching the 中文.",
    ),
    ProofTestCase(
        zhongwen="原来蠢，并不那么好笑",
        yuewen="原来，唔系咁好笑",
        yuewen_proofread="原来，唔系咁好笑",
        note="",
    ),
    ProofTestCase(
        zhongwen="蠢会失败⋯",
        yuewen="会失败⋯",
        yuewen_proofread="会失败⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="会失望",
        yuewen="会失望",
        yuewen_proofread="会失望",
        note="",
    ),
    ProofTestCase(
        zhongwen="失望，并不那么好笑",
        yuewen="失望，唔系咁好笑",
        yuewen_proofread="失望，唔系咁好笑",
        note="",
    ),
    ProofTestCase(
        zhongwen="肥，都不一定好笑",
        yuewen="肥，都未必好笑",
        yuewen_proofread="肥，都未必好笑",
        note="",
    ),
    ProofTestCase(
        zhongwen="肥，不一定大力",
        yuewen="肥，唔一定大力",
        yuewen_proofread="肥，唔一定大力",
        note="",
    ),
    ProofTestCase(
        zhongwen="大力，亦不一定得",
        yuewen="大力，亦都唔一定得",
        yuewen_proofread="大力，亦都唔一定得",
        note="",
    ),
    ProofTestCase(
        zhongwen="揸住个包，我忽然想⋯",
        yuewen="揸住个包，我忽然喺度谂⋯",
        yuewen_proofread="揸住个包，我忽然喺度谂⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="长大了，到我要面对这个实掘掘⋯",
        yuewen="大个咗到我要面对呢一个实角局⋯",
        yuewen_proofread="大个咗到我要面对呢一个实掘掘⋯",
        note="Corrected '实角局' to '实掘掘' as '实掘掘' matches the meaning and "
        "sound of the original 中文 phrase.",
    ),
    ProofTestCase(
        zhongwen="未必可以发梦，未必那么好笑的⋯",
        yuewen="未必到你发梦，又未必咁好笑嘅⋯",
        yuewen_proofread="未必到你发梦，又未必咁好笑嘅⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="世界的时候，我会怎么样？",
        yuewen="世界嘅时候，我会系点㗎呢？",
        yuewen_proofread="世界嘅时候，我会系点㗎呢？",
        note="",
    ),
]  # proof_test_cases_block_64
proof_test_cases_block_65 = [
    ProofTestCase(
        zhongwen="「⋯无力挽！」",
        yuewen="「⋯无泪弯！」",
        yuewen_proofread="「⋯无力挽！」",
        note="Corrected '无泪弯' to '无力挽' as it is a mishearing; '无力挽' "
        "matches the intended meaning of '无力挽' (no strength to "
        "save/stop).",
    ),
]  # proof_test_cases_block_65
proof_test_cases_block_66 = []  # proof_test_cases_block_66
proof_test_cases_block_67 = [
    ProofTestCase(
        zhongwen="是的，我就是大个佬麦兜",
        yuewen="系呀，我就系大个佬麦豆喇",
        yuewen_proofread="系呀，我就系大个佬麦兜喇",
        note="Corrected '麦豆' to '麦兜' as '麦兜' is the correct name, matching "
        "the original meaning.",
    ),
    ProofTestCase(
        zhongwen="肥，算大力",
        yuewen="肥啰，算大力啦",
        yuewen_proofread="肥啰，算大力啦",
        note="",
    ),
    ProofTestCase(
        zhongwen="麻麻地可以",
        yuewen="麻麻地得咁啦",
        yuewen_proofread="麻麻地得咁啦",
        note="",
    ),
    ProofTestCase(
        zhongwen="负家产",
        yuewen="富家产啰",
        yuewen_proofread="负家产啰",
        note="Corrected '富家产' to '负家产' as '负家产' (negative assets) matches "
        "the meaning of the 中文, while '富家产' (rich assets) is a likely "
        "mishearing.",
    ),
    ProofTestCase(
        zhongwen="脚爪是真的大，比一节瓜还要大",
        yuewen="脚瓜真系几大，仲大过个折瓜",
        yuewen_proofread="脚瓜真系几大，仲大过个节瓜",
        note="Corrected '折瓜' to '节瓜' as '节瓜' is the correct term for the "
        "vegetable, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="脚瓜上的肌肉非常结实⋯",
        yuewen="脚瓜上面个肌肉非常结实⋯",
        yuewen_proofread="脚瓜上面个肌肉非常结实⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="青筋一条条凸出来，似钢筋",
        yuewen="啲青筋一条一条凸下凸下，好似钢筋",
        yuewen_proofread="啲青筋一条一条凸下凸下，好似钢筋",
        note="",
    ),
    ProofTestCase(
        zhongwen="至于脚趾甲⋯",
        yuewen="至于脚趾弓啲脚甲⋯",
        yuewen_proofread="至于脚趾甲⋯",
        note="Removed '弓啲' as it is likely a mishearing; '脚趾甲' directly "
        "matches the meaning of '脚趾甲' in the 中文.",
    ),
    ProofTestCase(
        zhongwen="有次我无无聊聊真的量了一下⋯",
        yuewen="有次我无无聊聊真系走去卡下佢⋯",
        yuewen_proofread="有次我无无聊聊真系走去卡下佢⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="足有一寸厚",
        yuewen="哗，粥粥成串咁厚",
        yuewen_proofread="哗，足足成寸咁厚",
        note="Corrected '粥粥成串' to '足足成寸' as '足足成寸' means 'a full inch "
        "thick', matching the meaning of the 中文, while '粥粥成串' is a "
        "mishearing.",
    ),
    ProofTestCase(
        zhongwen="是的，故事讲完了",
        yuewen="系呀，故事讲完喇",
        yuewen_proofread="系呀，故事讲完喇",
        note="",
    ),
    ProofTestCase(
        zhongwen="这是一个尝试",
        yuewen="呢个系一个尝试",
        yuewen_proofread="呢个系一个尝试",
        note="",
    ),
    ProofTestCase(
        zhongwen="失败⋯尝试⋯",
        yuewen="失败⋯尝试⋯",
        yuewen_proofread="失败⋯尝试⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="好多包⋯可是没有包保成功的故事",
        yuewen="好多包⋯但系冇包补成功嘅故事",
        yuewen_proofread="好多包⋯但系冇包保成功嘅故事",
        note="Corrected '包补' to '包保' as '包保' (guarantee) matches the "
        "meaning in the 中文, while '包补' is likely a mishearing.",
    ),
    ProofTestCase(
        zhongwen="故事说了一轮⋯",
        yuewen="故事讲咗一轮⋯",
        yuewen_proofread="故事讲咗一轮⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="什么也没有？也不是",
        yuewen="乜都冇？又唔系噃",
        yuewen_proofread="乜都冇？又唔系噃",
        note="",
    ),
    ProofTestCase(
        zhongwen="就是大了双脚瓜",
        yuewen="就系大咗两个脚瓜",
        yuewen_proofread="就系大咗两个脚瓜",
        note="",
    ),
    ProofTestCase(
        zhongwen="可是楝一双脚瓜站这儿⋯",
        yuewen="但系冻住两个脚瓜企喺度⋯",
        yuewen_proofread="但系冻住两个脚瓜企喺度⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="当浪打过来⋯",
        yuewen="当啲浪打埋嚟⋯",
        yuewen_proofread="当啲浪打埋嚟⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="那感觉还真不错",
        yuewen="𠮶张感觉真系好好",
        yuewen_proofread="𠮶张感觉真系好好",
        note="",
    ),
    ProofTestCase(
        zhongwen="你知道我麻麻地叻佬，不懂得⋯",
        yuewen="你知我麻麻地叻佬，唔识得⋯",
        yuewen_proofread="你知我麻麻地叻佬，唔识得⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="替自己的故事加点教训呀锦囊呀那些",
        yuewen="帮自己嘅故事加啲教训呀锦囊呀𠮶啲嘢",
        yuewen_proofread="帮自己嘅故事加啲教训呀锦囊呀𠮶啲嘢",
        note="",
    ),
    ProofTestCase(
        zhongwen="可是，浸一双脚瓜站水中⋯",
        yuewen="但系冻住两个脚瓜企喺水𠮶度⋯",
        yuewen_proofread="但系冻住两个脚瓜企喺水𠮶度⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="当风吹向我的脑，我会想⋯",
        yuewen="当风吹喺我个脑部，我会谂⋯",
        yuewen_proofread="当风吹喺我个脑部，我会谂⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="如果妈妈看见我这个大脚瓜⋯",
        yuewen="如果妈妈见到我呢个大脚瓜⋯",
        yuewen_proofread="如果妈妈见到我呢个大脚瓜⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="我猜，她会好开心",
        yuewen="我谂，佢会好开心",
        yuewen_proofread="我谂，佢会好开心",
        note="",
    ),
]  # proof_test_cases_block_67
proof_test_cases_block_68 = [
    ProofTestCase(
        zhongwen="不成，还是出个锦囊！",
        yuewen="都系唔好呀，都系出返个锦囊先得！",
        yuewen_proofread="都系唔好呀，都系出返个锦囊先得！",
        note="",
    ),
    ProofTestCase(
        zhongwen="妈妈的dot com散掉后，她又有计",
        yuewen="妈妈个Doccom散咗之后，佢又有计喇",
        yuewen_proofread="妈妈个dot com散咗之后，佢又有计喇",
        note="Corrected 'Doccom' to 'dot com' as it is a mishearing of the "
        "English term 'dot com', matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="她出版了一本教烹饪的食谱",
        yuewen="佢出咗半教主送嘅食谱，谂住捞返扎沙",
        yuewen_proofread="佢出版咗一本教煮嘢食嘅食谱，谂住捞返扎沙",
        note="Corrected '出咗半教主送嘅食谱' to '出版咗一本教煮嘢食嘅食谱' as the original was "
        "a mishearing; '出版' and '一本教煮嘢食嘅食谱' match the meaning of "
        "'出版了一本教烹饪的食谱'.",
    ),
    ProofTestCase(
        zhongwen="食谱最后一页教人整烧鸡",
        yuewen="食谱最后一页系教人整烧鸡嘅",
        yuewen_proofread="食谱最后一页系教人整烧鸡嘅",
        note="",
    ),
    ProofTestCase(
        zhongwen="方法简单，人人可学",
        yuewen="方法简单，人人都学得识",
        yuewen_proofread="方法简单，人人都学得识",
        note="",
    ),
    ProofTestCase(
        zhongwen="「烧鸡」",
        yuewen="「烧鸡」",
        yuewen_proofread="「烧鸡」",
        note="",
    ),
    ProofTestCase(
        zhongwen="材料是⋯鸡",
        yuewen="材料系⋯鸡",
        yuewen_proofread="材料系⋯鸡",
        note="",
    ),
    ProofTestCase(
        zhongwen="方法：把鸡烧几烧",
        yuewen="方法：攞只鸡去烧佢几烧",
        yuewen_proofread="方法：攞只鸡去烧佢几烧",
        note="",
    ),
    ProofTestCase(
        zhongwen="就这样，一味「烧鸡」大功告成",
        yuewen="就噉，一味「烧鸡」就大功告成喇",
        yuewen_proofread="就噉，一味「烧鸡」就大功告成喇",
        note="",
    ),
    ProofTestCase(
        zhongwen="食谱里面补充说：",
        yuewen="食谱度又补充噉话：",
        yuewen_proofread="食谱度又补充噉话：",
        note="",
    ),
    ProofTestCase(
        zhongwen="如果你想把鸡烧得美味可口⋯",
        yuewen="如果想你个鸡烧得美味可口⋯",
        yuewen_proofread="如果你想把鸡烧得美味可口⋯",
        note="Corrected '如果想你个鸡' to '如果你想把鸡' as the original was a "
        "mishearing; '你想把鸡' matches the intended meaning of the 中文.",
    ),
    ProofTestCase(
        zhongwen="吃完后不会心肺实胃气涨",
        yuewen="冇话食完腰心腰肺顶住个胃",
        yuewen_proofread="冇话食完腰心腰肺顶住个胃",
        note="",
    ),
    ProofTestCase(
        zhongwen="秘诀是：拜托，把鸡烧好一点⋯",
        yuewen="个秘诀系：唔该，烧得佢好啲啰⋯",
        yuewen_proofread="个秘诀系：唔该，烧得佢好啲啰⋯",
        note="",
    ),
    ProofTestCase(
        zhongwen="多谢合作！",
        yuewen="多谢合作！",
        yuewen_proofread="多谢合作！",
        note="",
    ),
]  # proof_test_cases_block_68
proof_test_cases_block_69 = [
    ProofTestCase(
        zhongwen="麻烦你，一客常餐",
        yuewen="唔该，我要一个常餐啦",
        yuewen_proofread="唔该，我要一个常餐啦",
        note="",
    ),
    ProofTestCase(
        zhongwen="常餐？常餐有什么吃？",
        yuewen="常餐？常餐有咩食㗎？",
        yuewen_proofread="常餐？常餐有咩食㗎？",
        note="",
    ),
    ProofTestCase(
        zhongwen="跟特餐一样吧",
        yuewen="同特餐一样啰",
        yuewen_proofread="同特餐一样啰",
        note="",
    ),
    ProofTestCase(
        zhongwen="特餐是什么？",
        yuewen="噉特餐系咩嚟㗎？",
        yuewen_proofread="噉特餐系咩嚟㗎？",
        note="",
    ),
    ProofTestCase(
        zhongwen="跟快餐差不多",
        yuewen="同快餐咁上下啰",
        yuewen_proofread="同快餐咁上下啰",
        note="",
    ),
    ProofTestCase(
        zhongwen="快餐又是什么？",
        yuewen="噉快餐又系咩嚟㗎？",
        yuewen_proofread="噉快餐又系咩嚟㗎？",
        note="",
    ),
    ProofTestCase(
        zhongwen="快餐即是午餐",
        yuewen="即系快餐咪真系午餐",
        yuewen_proofread="即系快餐咪真系午餐",
        note="",
    ),
    ProofTestCase(
        zhongwen="午餐吃什么？",
        yuewen="午餐食咩㗎？",
        yuewen_proofread="午餐食咩㗎？",
        note="",
    ),
    ProofTestCase(
        zhongwen="午餐跟晚餐一样",
        yuewen="午餐同晚餐一样㗎",
        yuewen_proofread="午餐同晚餐一样㗎",
        note="",
    ),
    ProofTestCase(
        zhongwen="晚餐又吃什么？",
        yuewen="噉晚餐又食啲咩呀？",
        yuewen_proofread="噉晚餐又食啲咩呀？",
        note="",
    ),
    ProofTestCase(
        zhongwen="晚餐即是常餐",
        yuewen="晚餐咪真系常餐啰",
        yuewen_proofread="晚餐咪真系常餐啰",
        note="",
    ),
    ProofTestCase(
        zhongwen="那么，两客常餐吧",
        yuewen="噉呀，我要两个常餐啦",
        yuewen_proofread="噉呀，我要两个常餐啦",
        note="",
    ),
    ProofTestCase(
        zhongwen="今天常餐精采呀！",
        yuewen="好嘢呀我哋今日啲常餐",
        yuewen_proofread="好嘢呀我哋今日啲常餐",
        note="",
    ),
]  # proof_test_cases_block_69
proof_test_cases_block_70 = [
    ProofTestCase(
        zhongwen="对不起，常餐卖光了",
        yuewen="唔好意思，上餐卖晒",
        yuewen_proofread="唔好意思，常餐卖晒",
        note="Corrected '上餐' to '常餐' as '常餐' is the correct term for the "
        "set meal, matching the meaning in the 中文.",
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
        note="Corrected '上餐' to '常餐' as '常餐' is the correct term for the "
        "set meal, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="常餐不是卖光了吗？",
        yuewen="咁你头先又话冇上餐？",
        yuewen_proofread="咁你头先又话冇常餐？",
        note="Corrected '上餐' to '常餐' as '常餐' is the correct term for the "
        "set meal, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="对，常餐卖光了，要吃特餐吗？",
        yuewen="系呀，上餐就系卖晒呀，咁你试唔试下特餐啦？",
        yuewen_proofread="系呀，常餐就系卖晒呀，咁你试唔试下特餐啦？",
        note="Corrected '上餐' to '常餐' as '常餐' is the correct term for the "
        "set meal, matching the meaning in the 中文.",
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
        note="Replaced '卖晒嘅' with '卖晒喇' as '卖晒喇' is the natural way to "
        "indicate 'sold out' in Cantonese, while '卖晒嘅' is likely a "
        "mishearing or unnatural ending.",
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
        note="Corrected '上餐' to '常餐' as '常餐' is the correct term for the "
        "set meal, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="常餐又有什么呢？",
        yuewen="咁上餐有咩㗎？",
        yuewen_proofread="咁常餐有咩㗎？",
        note="Corrected '上餐' to '常餐' as '常餐' is the correct term for the "
        "set meal, matching the meaning in the 中文.",
        include_in_prompt=True,
    ),
    ProofTestCase(
        zhongwen="常餐即是午餐",
        yuewen="上餐就即系午餐啰",
        yuewen_proofread="常餐就即系午餐啰",
        note="Corrected '上餐' to '常餐' as '常餐' is the correct term for the "
        "set meal, matching the meaning in the 中文.",
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
        yuewen_proofread="嚟唔嚟譜啲呀？噉你哋究竟有啲咩餐呀？",
        note="Corrected '普啲' to '譜啲' as '譜啲' (reasonable) matches the "
        "intended meaning of '太过分了吧' in the 中文, while '普啲' is likely "
        "a mishearing.",
    ),
    ProofTestCase(
        zhongwen="午餐吧，午餐精采呀",
        yuewen="午餐啦，午餐，好嘢呀",
        yuewen_proofread="午餐啦，午餐，好嘢呀",
        note="",
    ),
    ProofTestCase(
        zhongwen="怎么个精采法？",
        yuewen="点好嘢法呀？",
        yuewen_proofread="点好嘢法呀？",
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
        yuewen_proofread="同常餐一样咁好嘢啰",
        note="Corrected '上餐' to '常餐' as '常餐' is the correct term for the "
        "set meal, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="常餐又怎样呢？",
        yuewen="噉上餐又点好嘢法呀？",
        yuewen_proofread="噉常餐又点好嘢法呀？",
        note="Corrected '上餐' to '常餐' as '常餐' is the correct term for the "
        "set meal, matching the meaning in the 中文.",
    ),
    ProofTestCase(
        zhongwen="常餐早卖光了，你说精采不？",
        yuewen="上餐，上餐一早卖晒啦，你话好唔好嘢？",
        yuewen_proofread="常餐，常餐一早卖晒啦，你话好唔好嘢？",
        note="Corrected '上餐' to '常餐' as '常餐' is the correct term for the "
        "set meal, matching the meaning in the 中文.",
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
        yuewen="日光日白，食乜鬼嘢晚餐啊？",
        yuewen_proofread="日光日白，食乜鬼嘢晚餐啊？",
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
