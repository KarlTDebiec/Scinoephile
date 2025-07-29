#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MLAMD."""

from __future__ import annotations

from scinoephile.audio.cantonese.merging import MergeTestCase

merge_test_cases_block_0 = [
    MergeTestCase(
        zhongwen="在麦太即将临盆的时候",
        yuewen_to_merge=["就喺麦太快要临盘嘅时候"],
        yuewen_merged="就喺麦太快要临盘嘅时候",
        include_in_prompt=True,
        difficulty=2,
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
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="更正一下：",
        yuewen_to_merge=["都系唔好"],
        yuewen_merged="都系唔好：",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="先到街市大楼妹记鱼腩粥外边",
        yuewen_to_merge=["先去街市大楼𠮶间妹记鱼腩粥𠮶度"],
        yuewen_merged="先去街市大楼𠮶间妹记鱼腩粥𠮶度",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="转呀，转⋯再更正一下：",
        yuewen_to_merge=["转下", "转下", "都系唔好"],
        yuewen_merged="转下，转下⋯都系唔好：",
        include_in_prompt=True,
        difficulty=2,
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
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="飞呀，飞⋯",
        yuewen_to_merge=["飞下", "飞下"],
        yuewen_merged="飞下，飞下⋯",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="胶兜最后飞进广华医院候产房",
        yuewen_to_merge=["最后胶兜飞咗入广华医院嘅后产房"],
        yuewen_merged="最后胶兜飞咗入广华医院嘅后产房",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="也就是在麦太右边额角上⋯",
        yuewen_to_merge=["亦即系麦太右边云晶对上"],
        yuewen_merged="亦即系麦太右边云晶对上⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="更正：左边额角上⋯",
        yuewen_to_merge=["都系唔好", "左边云晶对上"],
        yuewen_merged="都系唔好：左边云晶对上⋯",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="转呀，转⋯",
        yuewen_to_merge=["转下", "转下", "转下噉"],
        yuewen_merged="转下，转下，转下噉⋯",
        include_in_prompt=True,
        difficulty=2,
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
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="希望他好聪明，读书好叻！",
        yuewen_to_merge=["希望佢好聪明", "读书好叻"],
        yuewen_merged="希望佢好聪明，读书好叻！",
        difficulty=1,
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
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="或者读书唔叻，工作叻呢？",
        yuewen_to_merge=["或者读书唔叻", "出嚟做嘢叻啦"],
        yuewen_merged="或者读书唔叻，出嚟做嘢叻啦？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="又或者⋯",
        yuewen_to_merge=["又或者呢"],
        yuewen_merged="又或者呢⋯",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="又或者好靓仔，好靓仔",
        yuewen_to_merge=["又或者系好靓仔好靓仔"],
        yuewen_merged="又或者系好靓仔，好靓仔",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="跟周润发，梁朝伟那么靓仔！",
        yuewen_to_merge=["好似周润发同埋梁朝伟咁靓仔"],
        yuewen_merged="好似周润发，同埋梁朝伟咁靓仔！",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="胶兜仍然在转，毫无点头迹象",
        yuewen_to_merge=["胶兜依然系噉喺度转", "好似一啲应承嘅迹象都冇"],
        yuewen_merged="胶兜依然系噉喺度转，好似一啲应承嘅迹象都冇",
        include_in_prompt=True,
        difficulty=2,
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
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="唔聪明唔靓仔也算了，只要福星高照",
        yuewen_to_merge=["就算唔系咁聪明同咁靓仔", "只要复星高照"],
        yuewen_merged="就算唔系咁聪明同咁靓仔，只要复星高照",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="一世够运，逢凶化吉！",
        yuewen_to_merge=["一世救运", "乜嘢事都逢凶化㗎喇"],
        yuewen_merged="一世救运，乜嘢事都逢凶化㗎喇！",
        difficulty=1,
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
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="但总得要叻仔呀！",
        yuewen_to_merge=["但系都要叻仔先得㗎"],
        yuewen_merged="但系都要叻仔先得㗎！",
        difficulty=1,
    ),
]  # merge_test_cases_block_0
merge_test_cases_block_1 = [
    MergeTestCase(
        zhongwen="最后，胶兜「嘀督」一声落地",
        yuewen_to_merge=["最后胶兜滴嘟一声咁落地"],
        yuewen_merged="最后，胶兜「滴嘟」一声咁落地",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="嘀督？嘀督，就是答应了",
        yuewen_to_merge=["滴嘟", "滴嘟㖞", "即系应承啦"],
        yuewen_merged="滴嘟？滴嘟㖞，即系应承啦",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="麦太想，这次走运了！",
        yuewen_to_merge=["麦太心谂", "今次冇死喇"],
        yuewen_merged="麦太心谂，今次冇死喇！",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="可是答应了些什么呢？",
        yuewen_to_merge=["但你应承咗啲咩呢"],
        yuewen_merged="但你应承咗啲咩呢？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="叻仔？好运？",
        yuewen_to_merge=["叻仔", "好运"],
        yuewen_merged="叻仔？好运？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="还是似周润发？",
        yuewen_to_merge=["定系话自周人烦啊"],
        yuewen_merged="定系话自周人烦啊？",
        difficulty=1,
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
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="还是唤他麦兜！",
        yuewen_to_merge=["不如叫麦兜啦"],
        yuewen_merged="不如叫麦兜啦！",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="各位⋯",
        yuewen_to_merge=["各位"],
        yuewen_merged="各位⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="我就是险些给定名麦胶的小朋友⋯",
        yuewen_to_merge=["我就系呢个差少少就叫做麦胶嘅小朋友"],
        yuewen_merged="我就系呢个差少少就叫做麦胶嘅小朋友⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="麦兜！",
        yuewen_to_merge=["麦兜"],
        yuewen_merged="麦兜！",
        difficulty=1,
    ),
]  # merge_test_cases_block_1
merge_test_cases_block_2 = [
    MergeTestCase(
        zhongwen="麦太，没见面一阵",
        yuewen_to_merge=["咦", "麦太", "咩唔见你一排"],
        yuewen_merged="咦，麦太，咩唔见你一排",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="怎么小腿粗起来了？",
        yuewen_to_merge=["个脚刮囊粗咗咁多呀"],
        yuewen_merged="个脚刮囊粗咗咁多呀？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="可怜呀，每天扑来扑去⋯",
        yuewen_to_merge=["鬼咩", "日日扑嚟扑去"],
        yuewen_merged="鬼咩，日日扑嚟扑去⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="替儿子找幼稚园！",
        yuewen_to_merge=["同我仔揾幼稚园吖嘛"],
        yuewen_merged="同我仔揾幼稚园吖嘛！",
        difficulty=1,
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
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="春田花花幼稚园？",
        yuewen_to_merge=["春田花花幼稚园呢"],
        yuewen_merged="春田花花幼稚园呢？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="就是座落界限街南昌街交界⋯",
        yuewen_to_merge=["就系坐落喺界限街同南昌街交界"],
        yuewen_merged="就系坐落喺界限街同南昌街交界⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="银城美食广场附近的⋯",
        yuewen_to_merge=["银城美食广场附近𠮶间"],
        yuewen_merged="银城美食广场附近𠮶间⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="春田花花幼稚园？",
        yuewen_to_merge=["春田花花幼稚园呀"],
        yuewen_merged="春田花花幼稚园呀？",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="对！深水埗地铁站步行不用10分钟！",
        yuewen_to_merge=["系呀", "深水埗地铁站口行过去唔使十分钟呀"],
        yuewen_merged="系呀！深水埗地铁站口行过去唔使十分钟呀！",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="春田花花幼稚园，师资优良⋯",
        yuewen_to_merge=["春田花花幼稚园", "诗诗优良"],
        yuewen_merged="春田花花幼稚园，诗诗优良⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="而且还有西人教英文！",
        yuewen_to_merge=["仲系西人教英文添㗎"],
        yuewen_merged="仲系西人教英文添㗎！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="西人教英文？",
        yuewen_to_merge=["咦", "西人教英文"],
        yuewen_merged="咦，西人教英文？",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="是呀！",
        yuewen_to_merge=["系呀"],
        yuewen_merged="系呀！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="春田花花，确有好多西人呀！",
        yuewen_to_merge=["春田花花", "真系好多西人㗎"],
        yuewen_merged="春田花花，真系好多西人㗎！",
        difficulty=1,
    ),
]  # merge_test_cases_block_2
merge_test_cases_block_3 = [
    MergeTestCase(
        zhongwen="这个猪样白兔小朋友⋯",
        yuewen_to_merge=["呢个扮紧白兔猪样嘅小朋友"],
        yuewen_merged="呢个扮紧白兔猪样嘅小朋友⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="横看竖看也不像发哥伟仔的一个⋯",
        yuewen_to_merge=["即系横睇掂睇都唔似发哥或者", "位仔𠮶个呢"],
        yuewen_merged="即系横睇掂睇都唔似发哥或者位仔𠮶个呢⋯",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="就是我，麦兜",
        yuewen_to_merge=["就系我", "麦兜"],
        yuewen_merged="就系我，麦兜",
        difficulty=1,
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
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="这么多年来⋯",
        yuewen_to_merge=["所以咁多年嚟"],
        yuewen_merged="所以咁多年嚟⋯",
        difficulty=1,
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
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="荔芋火鸭礼！　　荔芋火鸭礼！",
        yuewen_to_merge=["湾吉校坟交涉设"],
        yuewen_merged="湾吉校坟交涉设",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="也不能忘记校训九十八！",
        yuewen_to_merge=["都唔好湾吉校坟交涉白"],
        yuewen_merged="都唔好湾吉校坟交涉白！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="好！各位同学⋯",
        yuewen_to_merge=["𠮶个位同学"],
        yuewen_merged="𠮶个位同学⋯",
        difficulty=2,
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
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="小朋友，这个月你们交过学费没有？",
        yuewen_to_merge=["小朋友", "你哋今个月交咗学费咩呀"],
        yuewen_merged="小朋友，你哋今个月交咗学费咩呀？",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="交过了！",
        yuewen_to_merge=["交"],
        yuewen_merged="交！",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="太好了！大家去上堂吧",
        yuewen_to_merge=["哎", "好在", "噉大家可以返去上堂喇"],
        yuewen_merged="哎，好在！噉大家可以返去上堂喇",
        include_in_prompt=True,
        difficulty=2,
    ),
]  # merge_test_cases_block_3
merge_test_cases_block_4 = [
    MergeTestCase(
        zhongwen="你们可能觉得这间幼稚园很烂",
        yuewen_to_merge=["你哋可能觉得呢间幼稚园好逗利"],
        yuewen_merged="你哋可能觉得呢间幼稚园好逗利",
    ),
    MergeTestCase(
        zhongwen="可是，对我和我一班同学",
        yuewen_to_merge=["但系对于我同埋我班同学仔嚟讲"],
        yuewen_merged="但系，对于我同埋我班同学仔嚟讲",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="这儿是我们最快乐，最美丽的乐园⋯",
        yuewen_to_merge=["呢度系我哋最快乐", "最美丽嘅乐园"],
        yuewen_merged="呢度系我哋最快乐，最美丽嘅乐园⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="⋯还有一个很疼我们",
        yuewen_to_merge=["仲有一个好疼我哋"],
        yuewen_merged="⋯仲有一个好疼我哋",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="就是有点游魂的Miss Chan",
        yuewen_to_merge=["不过就有少少失魂嘅班主有Miss", "Chan"],
        yuewen_merged="不过就有少少失魂嘅班主有Miss Chan",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="她的志愿是做第二个王菲",
        yuewen_to_merge=["佢嘅志愿系做下一个王妃"],
        yuewen_merged="佢嘅志愿系做下一个王妃",
    ),
    MergeTestCase(
        zhongwen="做第二个陈慧琳也可以",
        yuewen_to_merge=["或者系做下一个陈维林都得"],
        yuewen_merged="或者系做下一个陈维林都得",
    ),
    MergeTestCase(
        zhongwen="我们现在开始点名",
        yuewen_to_merge=["好喇", "我哋而家开始点名"],
        yuewen_merged="好喇，我哋而家开始点名",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="麦唛同学！　　到！",
        yuewen_to_merge=["麦麦同学", "到"],
        yuewen_merged="麦麦同学！　　到！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="亚辉同学！　　到！",
        yuewen_to_merge=["阿辉同学", "到"],
        yuewen_merged="阿辉同学！　　到！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="菇时同学！　　到！",
        yuewen_to_merge=["Boosie同学", "到"],
        yuewen_merged="Boosie同学！　　到！",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="得巴同学！　　到！",
        yuewen_to_merge=["德巴同学", "到"],
        yuewen_merged="德巴同学！　　到！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="阿May同学！　　到！",
        yuewen_to_merge=["阿May同学", "到"],
        yuewen_merged="阿May同学！　　到！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="阿June同学！　　到！",
        yuewen_to_merge=["阿June同学", "到"],
        yuewen_merged="阿June同学！　　到！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="阿May同学！",
        yuewen_to_merge=["阿May同学"],
        yuewen_merged="阿May同学！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="Miss Chan，我点过两次了！",
        yuewen_to_merge=["Miss", "Chan你点咗我两次喇"],
        yuewen_merged="Miss Chan，你点咗我两次喇！",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="呀，真的吗？",
        yuewen_to_merge=["啊", "系咩"],
        yuewen_merged="啊，系咩？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="我们现在继续点名",
        yuewen_to_merge=["好", "我哋而家继续点名"],
        yuewen_merged="好，我哋而家继续点名",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="菇时同学！　　到！",
        yuewen_to_merge=["川明同学", "到"],
        yuewen_merged="川明同学！　　到！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="还有谁没点过吗？",
        yuewen_to_merge=["好", "仲有边个未点"],
        yuewen_merged="好，仲有边个未点？",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="麦兜！",
        yuewen_to_merge=["猫", "噢"],
        yuewen_merged="猫！噢！",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="麦兜同学！",
        yuewen_to_merge=["麦兜同学"],
        yuewen_merged="麦兜同学！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="麦唛呀，即是呢⋯",
        yuewen_to_merge=["妈妈啊", "麦兜同学", "即系呢"],
        yuewen_merged="妈妈啊，麦兜同学，即系呢⋯",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="我好像觉得呢⋯",
        yuewen_to_merge=["我个心总系仁住仁住"],
        yuewen_merged="我个心总系仁住仁住⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="有什么人在喊我似的",
        yuewen_to_merge=["好似有人嗌紧我个名噉嘅"],
        yuewen_merged="好似有人嗌紧我个名噉嘅",
    ),
    MergeTestCase(
        zhongwen="你们不要以为我心散",
        yuewen_to_merge=["你哋唔好以为我心散啊"],
        yuewen_merged="你哋唔好以为我心散啊",
    ),
    MergeTestCase(
        zhongwen="其实我正在思考一个学术问题：",
        yuewen_to_merge=["其实我系喺度思考紧一啲学术性嘅问题"],
        yuewen_merged="其实我系喺度思考紧一啲学术性嘅问题：",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="橙，为什么会是「疴﹣烂﹣煮」呢？",
        yuewen_to_merge=["点解橙叫Orange呢"],
        yuewen_merged="点解橙叫「Orange」呢？",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="妈妈说吃橙可通大便",
        yuewen_to_merge=["妈妈话食橙会通大", "变"],
        yuewen_merged="妈妈话食橙会通大变",
    ),
    MergeTestCase(
        zhongwen="「疴」这个我明白，可是「烂﹣煮」呢？",
        yuewen_to_merge=["噢", "呢个我明白", "但系橙呢"],
        yuewen_merged="「噢」呢个我明白，但系「橙」呢？",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="还有这个「芭﹣娜﹣娜」香蕉",
        yuewen_to_merge=["仲有呢个啊", "芭拉娜啊", "香蕉啊"],
        yuewen_merged="仲有呢个啊「芭拉娜」啊香蕉啊",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="为什么雨伞又会是「暗﹣芭﹣娜﹣娜」呢？",
        yuewen_to_merge=["点解雨姐会叫做暗芭拉娜呢"],
        yuewen_merged="点解雨姐会叫做「暗芭拉娜」呢？",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="我「暗」的「暗」掉一条蕉",
        yuewen_to_merge=["嗱", "我暗啦", "噉我暗𠮶条香蕉"],
        yuewen_merged="嗱，我「暗」啦，噉我「暗」𠮶条香蕉",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="至多是疴烂煮，怎么会下起雨来呢？",
        yuewen_to_merge=["至多会Orange啫", "点解会搞到落雨呢"],
        yuewen_merged="至多会Orange啫，点解会搞到落雨呢？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="这世界还有很多事情我弄不明白",
        yuewen_to_merge=["呢个世界仲有好多嘢我谂唔明"],
        yuewen_merged="呢个世界仲有好多嘢我谂唔明",
    ),
    MergeTestCase(
        zhongwen="但我不害怕",
        yuewen_to_merge=["不过我唔怕"],
        yuewen_merged="不过我唔怕",
    ),
    MergeTestCase(
        zhongwen="我想，有天我念完幼稚园",
        yuewen_to_merge=["我谂", "到我读完幼稚园"],
        yuewen_merged="我谂，到我读完幼稚园",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="升小学，上中学",
        yuewen_to_merge=["识埋小学", "上到中学"],
        yuewen_merged="识埋小学，上到中学",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="再念大学⋯",
        yuewen_to_merge=["再入埋大学"],
        yuewen_merged="再入埋大学⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="当我大学毕业的时候",
        yuewen_to_merge=["等我大学毕业𠮶阵"],
        yuewen_merged="等我大学毕业𠮶阵",
    ),
    MergeTestCase(
        zhongwen="我知道我会明白一切！",
        yuewen_to_merge=["我谂我乜都会明白晒"],
        yuewen_merged="我谂我乜都会明白晒！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="那时候⋯",
        yuewen_to_merge=["到𠮶阵"],
        yuewen_merged="到𠮶阵⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="我买所房子给妈妈！",
        yuewen_to_merge=["我买层楼畀我妈妈"],
        yuewen_merged="我买层楼畀我妈妈！",
        difficulty=1,
    ),
]  # merge_test_cases_block_4
merge_test_cases_block_5 = [
    MergeTestCase(
        zhongwen="幼稚园楼下，由校长兼营的茶餐厅",
        yuewen_to_merge=["喺幼稚园楼下校长兼营嘅间茶餐厅"],
        yuewen_merged="喺幼稚园楼下，校长兼营嘅间茶餐厅",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="我们一班同学下课后经常光顾",
        yuewen_to_merge=["我哋一班同学仔放咗学都经常系傍陈"],
        yuewen_merged="我哋一班同学仔放咗学都经常系傍陈",
    ),
    MergeTestCase(
        zhongwen="鱼蛋粗面，麻烦你　　粗面买光了",
        yuewen_to_merge=["唔该鱼蛋粗啊", "冇粗面噃"],
        yuewen_merged="唔该，鱼蛋粗啊　　冇粗面噃",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="那样子⋯来碗鱼蛋河粉吧　　鱼蛋买光了",
        yuewen_to_merge=["噉啊", "要碗鱼蛋好啊", "冇鱼蛋噃"],
        yuewen_merged="噉啊⋯要碗鱼蛋好啊　　冇鱼蛋噃",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="那么⋯金钱肚粗面好了　　粗面买光了",
        yuewen_to_merge=["噉啊", "要金钱透粗啊", "冇粗面噃"],
        yuewen_merged="噉啊⋯要金钱透粗啊　　冇粗面噃",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="那么要鱼蛋油面吧　　鱼蛋买光了",
        yuewen_to_merge=["噉啊", "咁要鱼蛋油面啊", "冇鱼蛋噃"],
        yuewen_merged="噉啊咁要鱼蛋油面啊　　冇鱼蛋噃",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="怎么都买光了？",
        yuewen_to_merge=["乜样样都冇嘅"],
        yuewen_merged="乜样样都冇嘅？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="来个墨鱼丸粗面吧　　粗面买光了",
        yuewen_to_merge=["噉要蜜丸粗啊", "冇粗面噃"],
        yuewen_merged="噉要蜜丸粗啊　　冇粗面噃",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="又买光了？",
        yuewen_to_merge=["又冇啊"],
        yuewen_merged="又冇啊？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="麻烦来碗鱼蛋濑吧　　鱼蛋买光了",
        yuewen_to_merge=["噉唔该畀碗鱼蛋奶啊", "冇鱼蛋噃"],
        yuewen_merged="噉唔该畀碗鱼蛋奶啊　　冇鱼蛋噃",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="麦兜呀，鱼蛋跟粗面都买光了",
        yuewen_to_merge=["麦兜啊", "佢哋啲鱼蛋同粗面卖晒㗎啦"],
        yuewen_merged="麦兜啊，佢哋啲鱼蛋同粗面卖晒㗎啦",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="即是所有鱼蛋跟粗面的配搭都没了",
        yuewen_to_merge=["即系所有要鱼蛋或者粗面嘅配搭都冇㗎啦"],
        yuewen_merged="即系所有要鱼蛋或者粗面嘅配搭都冇㗎啦",
    ),
    MergeTestCase(
        zhongwen="没有那些配搭吗？",
        yuewen_to_merge=["噢", "冇𠮶啲配搭啊"],
        yuewen_merged="噢，冇𠮶啲配搭啊？",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="麻烦你，净要鱼蛋吧　　鱼蛋买光了",
        yuewen_to_merge=["噉唔该净鱼蛋啊", "冇鱼蛋噃"],
        yuewen_merged="噉唔该，净鱼蛋啊　　冇鱼蛋噃",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="那么净要粗面呢？　　粗面买光了",
        yuewen_to_merge=["净粗面呢", "冇粗面噃"],
        yuewen_merged="净粗面呢？　　冇粗面噃",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="看到这里⋯",
        yuewen_to_merge=["睇到呢度"],
        yuewen_merged="睇到呢度⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="大家大概都知道我是个怎么样的叻仔",
        yuewen_to_merge=["大家大概都知道我有几叻仔嘞"],
        yuewen_merged="大家大概都知道我有几叻仔嘞",
    ),
    MergeTestCase(
        zhongwen="那时候我无忧无虑，万事无所谓﹣﹣",
        yuewen_to_merge=["果只我无忧无虑", "冇乜所谓"],
        yuewen_merged="果只我无忧无虑，冇乜所谓﹣﹣",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="鱼蛋买光了？那么粗面吧",
        yuewen_to_merge=["冇鱼蛋咩", "粗面都好啊"],
        yuewen_merged="冇鱼蛋咩？粗面都好啊",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="麦兜，射呀！",
        yuewen_to_merge=["麦兜", "转身食啊"],
        yuewen_merged="麦兜，转身食啊！",
        difficulty=1,
    ),
]  # merge_test_cases_block_5
merge_test_cases_block_6 = [
    MergeTestCase(
        zhongwen="看着自己每天疴烂煮⋯",
        yuewen_to_merge=["睇住自己日日柯能处"],
        yuewen_merged="睇住自己日日柯能处⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="每天长肉⋯",
        yuewen_to_merge=["日日掌肉"],
        yuewen_merged="日日掌肉⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="我感到充满力量！",
        yuewen_to_merge=["感到充满力量"],
        yuewen_merged="感到充满力量！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="世界好美丽！",
        yuewen_to_merge=["世界好美丽"],
        yuewen_merged="世界好美丽！",
        difficulty=1,
    ),
]  # merge_test_cases_block_6
merge_test_cases_block_7 = [
    MergeTestCase(
        zhongwen="有一首歌，Miss Chan唱的好听",
        yuewen_to_merge=["有一首歌", "麦词春唱得好好听呀"],
        yuewen_merged="有一首歌，麦词春唱得好好听呀",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="我时常想着学习",
        yuewen_to_merge=["我成日想学习"],
        yuewen_merged="我成日想学习",
    ),
    MergeTestCase(
        zhongwen="可每次我总唱成「疴」什么什么的⋯",
        yuewen_to_merge=["但系唱嚟唱去都系阿伦厨", "咁Ballana噉"],
        yuewen_merged="但系唱嚟唱去都系「阿伦厨」，咁「Ballana」噉⋯",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="是All Things Bright and Beautiful吧？",
        yuewen_to_merge=["系唔系All", "Things", "Bright", "and", "Beautiful呀"],
        yuewen_merged="系唔系All Things Bright and Beautiful呀？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="是的，一切都好！",
        yuewen_to_merge=["系呀", "所有嘢都几好喇"],
        yuewen_merged="系呀，所有嘢都几好喇！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="世上一切，一切一切⋯",
        yuewen_to_merge=["世上一切"],
        yuewen_merged="世上一切⋯",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="所有那些，都好！",
        yuewen_to_merge=[
            "所有𠮶啲嘢",
            "都几好",
            "All",
            "Things",
            "Bright",
            "and",
            "Beautiful",
        ],
        yuewen_merged="所有𠮶啲嘢，都几好！All Things Bright and Beautiful",
        difficulty=2,
    ),
]  # merge_test_cases_block_7
merge_test_cases_block_8 = [
    MergeTestCase(
        zhongwen="一、二、三、四、五、六、七⋯",
        yuewen_to_merge=["1234567"],
        yuewen_merged="1234567⋯",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="多劳多得！",
        yuewen_to_merge=["多喽多得"],
        yuewen_merged="多喽多得！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="星期一至星期七⋯多劳多得！",
        yuewen_to_merge=["星期一至星期七多喽多得"],
        yuewen_merged="星期一至星期七⋯多喽多得！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="这位喊得特劲的中年母猪",
        yuewen_to_merge=["呢个嗌得特别劲嘅中年母猪"],
        yuewen_merged="呢个嗌得特别劲嘅中年母猪",
    ),
    MergeTestCase(
        zhongwen="就是我妈妈麦太",
        yuewen_to_merge=["就系我妈妈", "麦太"],
        yuewen_merged="就系我妈妈麦太",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="我妈妈真的很劲",
        yuewen_to_merge=["我妈妈真系好劲呀"],
        yuewen_merged="我妈妈真系好劲呀",
    ),
    MergeTestCase(
        zhongwen="一个女人背起整个世界！",
        yuewen_to_merge=["一个女人揹起成个世界"],
        yuewen_merged="一个女人揹起成个世界！",
        difficulty=1,
    ),
]  # merge_test_cases_block_8
merge_test_cases_block_9 = [
    MergeTestCase(
        zhongwen="是的，我妈妈真的很厉害",
        yuewen_to_merge=["系呀", "我妈妈真系好犀利㗎"],
        yuewen_merged="系呀，我妈妈真系好犀利㗎",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="除了兼任保险，地产经纪及trading⋯",
        yuewen_to_merge=["除咗做保险地产经纪同埋trading之外"],
        yuewen_merged="除咗做保险地产经纪同埋trading之外⋯",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="她还趁高科技热潮搞了个烹饪网站⋯",
        yuewen_to_merge=["佢仲趁住高科技热潮搞咗个煮𩠌嘅网站"],
        yuewen_merged="佢仲趁住高科技热潮搞咗个煮𩠌嘅网站⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="www．麦太世界．com",
        yuewen_to_merge=["www.mcticege.com"],
        yuewen_merged="www.mcticege.com",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="她做的菜，同样厉害",
        yuewen_to_merge=["佢煮嘅𩠌一样咁犀利"],
        yuewen_merged="佢煮嘅𩠌，一样咁犀利",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="欢迎大家收看《麦太世界》",
        yuewen_to_merge=["欢迎大家收睇麦太世界"],
        yuewen_merged="欢迎大家收睇《麦太世界》",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="今日为大家介绍一个⋯",
        yuewen_to_merge=["今日我为大家介绍个"],
        yuewen_merged="今日我为大家介绍个⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="简单别致的小菜纸包鸡",
        yuewen_to_merge=["简单又别致嘅小菜", "自包鸡"],
        yuewen_merged="简单又别致嘅小菜自包鸡",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="家中小朋友一定好喜欢",
        yuewen_to_merge=["家里头嘅小朋友一定好喜欢㗎"],
        yuewen_merged="家里头嘅小朋友一定好喜欢㗎",
    ),
    MergeTestCase(
        zhongwen="材料很简单：一个鸡包",
        yuewen_to_merge=["材料系好简单", "我哋只需要一个鸡包"],
        yuewen_merged="材料系好简单：我哋只需要一个鸡包",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="将鸡包底部的纸撕下来⋯慢慢地撕",
        yuewen_to_merge=["我哋将黐喺鸡包底嘅纸撕出嚟", "慢慢撕"],
        yuewen_merged="我哋将黐喺鸡包底嘅纸撕出嚟⋯慢慢撕",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="就会得到一张鸡包纸",
        yuewen_to_merge=["咁就会得到一张鸡包纸喇"],
        yuewen_merged="咁就会得到一张鸡包纸喇",
    ),
    MergeTestCase(
        zhongwen="把鸡包纸一反反转",
        yuewen_to_merge=["然后将鸡包纸一反", "反转"],
        yuewen_merged="然后将鸡包纸一反反转",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="这一味纸包鸡就完成了，很容易是吧？",
        yuewen_to_merge=["呢味自包鸡就完成喇", "系咪好易整啦"],
        yuewen_merged="呢味自包鸡就完成喇，系咪好易整啦？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="多谢大家收看",
        yuewen_to_merge=["多谢大家收睇"],
        yuewen_merged="多谢大家收睇",
    ),
]  # merge_test_cases_block_9
merge_test_cases_block_10 = [
    MergeTestCase(
        zhongwen="好高兴这么快又跟大家见面",
        yuewen_to_merge=["好高兴咁快又同大家见面"],
        yuewen_merged="好高兴咁快又同大家见面",
    ),
    MergeTestCase(
        zhongwen="接下来我会教大家整一味纸鸡包",
        yuewen_to_merge=["跟住落嚟我会教大家整一味纸鸡包"],
        yuewen_merged="跟住落嚟我会教大家整一味纸鸡包",
    ),
    MergeTestCase(
        zhongwen="材料也很简单，只需要白纸一张",
        yuewen_to_merge=["材料都好简单", "只需要白纸一张"],
        yuewen_merged="材料都好简单，只需要白纸一张",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="只要把这纸这样子⋯",
        yuewen_to_merge=["我哋只需要张张纸", "咁样"],
        yuewen_merged="我哋只需要张张纸咁样⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="一个纸鸡包就这样完成了",
        yuewen_to_merge=["一个纸鸡包就咁完成咗喇"],
        yuewen_merged="一个纸鸡包就咁完成咗喇",
    ),
    MergeTestCase(
        zhongwen="各位小朋友，像鸡包不像呀？",
        yuewen_to_merge=["各位小朋友", "你哋话似唔似鸡包啊"],
        yuewen_merged="各位小朋友，你哋话似唔似鸡包啊？",
        difficulty=1,
    ),
]  # merge_test_cases_block_10
merge_test_cases_block_11 = [
    MergeTestCase(
        zhongwen="现在要教大家一味别致小菜﹣",
        yuewen_to_merge=["间阵要教大家一味几别节嘅小菜"],
        yuewen_merged="间阵要教大家一味几别节嘅小菜﹣",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="包鸡纸包鸡包纸包鸡",
        yuewen_to_merge=["包鸡子包", "鸡包子包鸡"],
        yuewen_merged="包鸡子包鸡包子包鸡",
    ),
    MergeTestCase(
        zhongwen="首先将纸包鸡小心撕开",
        yuewen_to_merge=["首先将子包鸡小心噉撕开"],
        yuewen_merged="首先将子包鸡小心噉撕开",
    ),
    MergeTestCase(
        zhongwen="大家就会有一张纸包鸡及一块鸡",
        yuewen_to_merge=["大家就会有一张包鸡子同埋一嚿鸡啦"],
        yuewen_merged="大家就会有一张包鸡子同埋一嚿鸡啦",
    ),
    MergeTestCase(
        zhongwen="接着把鸡包纸这样子包起那块鸡",
        yuewen_to_merge=["跟住将鸡包子好似我噉包住牛鸡"],
        yuewen_merged="跟住将鸡包子好似我噉包住牛鸡",
    ),
    MergeTestCase(
        zhongwen="再依照这样子用包鸡纸把它包起",
        yuewen_to_merge=["然后再好似噉样将包鸡子包包包包包包住佢"],
        yuewen_merged="然后再好似噉样将包鸡子包包包包包包住佢",
    ),
    MergeTestCase(
        zhongwen="一味「包鸡纸包鸡包纸包鸡」完成了！",
        yuewen_to_merge=["咁一味包鸡子包鸡包子包鸡就完成喇"],
        yuewen_merged="咁一味「包鸡子包鸡包子包鸡」就完成喇！",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="真的很简单吧？",
        yuewen_to_merge=["系咪好简单呢"],
        yuewen_merged="系咪好简单呢？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="还真有一块鸡吃呢！",
        yuewen_to_merge=["仲真系有嚿鸡食添"],
        yuewen_merged="仲真系有嚿鸡食添！",
        difficulty=1,
    ),
]  # merge_test_cases_block_11
merge_test_cases_block_12 = [
    MergeTestCase(
        zhongwen="今日为大家介绍一味⋯",
        yuewen_to_merge=["今日要同大家介绍一味"],
        yuewen_merged="今日要同大家介绍一味⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="小朋友一定喜欢的⋯",
        yuewen_to_merge=["小朋友一定喜欢嘅"],
        yuewen_merged="小朋友一定喜欢嘅⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="鸡包包鸡包包鸡包纸包纸⋯",
        yuewen_to_merge=["鸡包包", "鸡包包", "鸡包纸包", "纸包鸡", "包包鸡"],
        yuewen_merged="鸡包包鸡包包鸡包纸包纸包鸡包包鸡⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="包鸡包鸡包纸包鸡",
        yuewen_to_merge=["纸包鸡", "包纸包鸡"],
        yuewen_merged="纸包鸡包纸包鸡",
    ),
    MergeTestCase(
        zhongwen="做法亦很简单",
        yuewen_to_merge=["做法都好简单"],
        yuewen_merged="做法都好简单",
    ),
    MergeTestCase(
        zhongwen="只要将鸡包包住个鸡包",
        yuewen_to_merge=["我哋先将鸡包", "包住个鸡包"],
        yuewen_merged="我哋先将鸡包包住个鸡包",
    ),
    MergeTestCase(
        zhongwen="再包住个鸡包⋯",
        yuewen_to_merge=["再包住个鸡包"],
        yuewen_merged="再包住个鸡包⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="包住张鸡包纸",
        yuewen_to_merge=["包住张鸡包纸"],
        yuewen_merged="包住张鸡包纸",
    ),
    MergeTestCase(
        zhongwen="再包包包包包住个纸鸡包",
        yuewen_to_merge=["再包包包包", "包住个纸包鸡"],
        yuewen_merged="再包包包包包住个纸包鸡",
    ),
    MergeTestCase(
        zhongwen="再包包包，纸纸纸",
        yuewen_to_merge=["再包包包包", "包鸡包纸", "包纸", "纸纸纸纸"],
        yuewen_merged="再包包包包包鸡包纸包纸，纸纸纸纸",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="纸包纸，纸包鸡，鸡包纸，纸包鸡⋯",
        yuewen_to_merge=[
            "纸包纸",
            "纸包鸡",
            "包鸡纸",
            "纸包鸡",
            "鸡鸡鸡",
            "纸纸纸再包鸡鸡",
        ],
        yuewen_merged="纸包纸，纸包鸡，包鸡纸，纸包鸡，鸡鸡鸡，纸纸纸再包鸡鸡⋯",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="可我妈妈也有她温柔的一面",
        yuewen_to_merge=["不过我妈妈都有佢温柔嘅一面"],
        yuewen_merged="不过我妈妈都有佢温柔嘅一面",
    ),
    MergeTestCase(
        zhongwen="例如每晚睡觉前，她都会说故事给我听",
        yuewen_to_merge=["例如每晚临睡前", "佢都会讲故事畀我听"],
        yuewen_merged="例如每晚临睡前，佢都会讲故事畀我听",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="从前，有个小朋友撒谎；有一天⋯",
        yuewen_to_merge=["从前有个小朋友讲大话", "有一日"],
        yuewen_merged="从前，有个小朋友讲大话；有一日⋯",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="他死了！",
        yuewen_to_merge=["佢死咗"],
        yuewen_merged="佢死咗！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="从前，有个小朋友很勤力念书⋯",
        yuewen_to_merge=["从前有个小朋友好勤力读书"],
        yuewen_merged="从前，有个小朋友好勤力读书⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="他长大后，发财了！",
        yuewen_to_merge=["佢长大发咗"],
        yuewen_merged="佢长大发咗！",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="从前，有个小朋友不孝，有天⋯",
        yuewen_to_merge=["从前有个小朋友唔孝顺", "有一日"],
        yuewen_merged="从前，有个小朋友唔孝顺，有一日⋯",
        include_in_prompt=True,
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="他扭了脚骹！",
        yuewen_to_merge=["佢屈亲个脚脚"],
        yuewen_merged="佢屈亲个脚脚！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="妈妈，我想睡觉",
        yuewen_to_merge=["妈我想瞓啦"],
        yuewen_merged="妈，我想瞓啦",
        difficulty=1,
    ),
]  # merge_test_cases_block_12
merge_test_cases_block_13 = [
    MergeTestCase(
        zhongwen="从前，有个小朋友早睡晚起；第二天⋯",
        yuewen_to_merge=["从前有个小朋友早睡晚起", "第二朝"],
        yuewen_merged="从前，有个小朋友早睡晚起；第二朝⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="他死了！",
        yuewen_to_merge=["佢死咗"],
        yuewen_merged="佢死咗！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="我妈妈就是这样子，一切都那么直接",
        yuewen_to_merge=["我妈妈就系噉", "一切都咁直接"],
        yuewen_merged="我妈妈就系噉，一切都咁直接",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="她爱得我直接⋯",
        yuewen_to_merge=["佢爱得我直接"],
        yuewen_merged="佢爱得我直接⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="对我的期望直接",
        yuewen_to_merge=["对我嘅期望直接"],
        yuewen_merged="对我嘅期望直接",
    ),
    MergeTestCase(
        zhongwen="对她，一、二、三、四、五、六、七",
        yuewen_to_merge=["佢一二三四五六七"],
        yuewen_merged="佢，一、二、三、四、五、六、七",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="没有不成的事",
        yuewen_to_merge=["唔得都要得", "字幕由", "Amara.org"],
        yuewen_merged="唔得都要得字幕由Amara.org",
        difficulty=2,
    ),
]  # merge_test_cases_block_13
merge_test_cases_block_14 = [
    MergeTestCase(
        zhongwen="可有些事情，要是真的不成呢？",
        yuewen_to_merge=["但系如果有啲嘢真系真系唔得呢"],
        yuewen_merged="但系如果有啲嘢，真系真系唔得呢？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="日子一天一天的过",
        yuewen_to_merge=["日子一日一日咁过"],
        yuewen_merged="日子一日一日咁过",
    ),
    MergeTestCase(
        zhongwen="首先是周润发事件⋯",
        yuewen_to_merge=["首先周润发𠮶单嘢"],
        yuewen_merged="首先周润发𠮶单嘢⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="拜托不要再提了！",
        yuewen_to_merge=["大家都唔好再提"],
        yuewen_merged="大家都唔好再提！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="至于好运⋯",
        yuewen_to_merge=["至于好运"],
        yuewen_merged="至于好运⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="我用一双童子手替妈妈抽的六合彩号码",
        yuewen_to_merge=["我用我嘅同事手帮妈妈抽嘅六合彩number"],
        yuewen_merged="我用我嘅同事手帮妈妈抽嘅六合彩number",
    ),
    MergeTestCase(
        zhongwen="奇迹般似的一个号码也没中过！",
        yuewen_to_merge=["竟然奇迹一样", "一个都未中过"],
        yuewen_merged="竟然奇迹一样，一个都未中过！",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="叻仔？",
        yuewen_to_merge=["叻仔"],
        yuewen_merged="叻仔？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="我也试过努力念书，可是⋯",
        yuewen_to_merge=["我试过好努力咁读书", "但系"],
        yuewen_merged="我试过好努力咁读书，但系⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="可是⋯我仍然有梦",
        yuewen_to_merge=["但系我仲可以发梦"],
        yuewen_merged="但系⋯我仲可以发梦",
        difficulty=1,
    ),
]  # merge_test_cases_block_14
merge_test_cases_block_15 = [
    MergeTestCase(
        zhongwen="马尔代夫，座落于印度洋的世外桃源",
        yuewen_to_merge=["马尔代夫", "坐落于印度洋嘅世外桃源"],
        yuewen_merged="马尔代夫，坐落于印度洋嘅世外桃源",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="蓝天白云，椰林树影，水清沙幼",
        yuewen_to_merge=["蓝天白云", "椰林树影", "水清沙游"],
        yuewen_merged="蓝天白云，椰林树影，水清沙游",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="七彩缤纷的珊瑚，目不暇给的热带鱼",
        yuewen_to_merge=["七彩缤纷嘅珊瑚", "目不下级嘅热带鱼群"],
        yuewen_merged="七彩缤纷嘅珊瑚，目不下级嘅热带鱼群",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="充满赤道活力的原始海洋，脱离繁嚣",
        yuewen_to_merge=["充满住赤道热力嘅原始海洋", "远离凡嚣"],
        yuewen_merged="充满住赤道热力嘅原始海洋，远离凡嚣",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="体验热情如火的风土人情",
        yuewen_to_merge=["体验热情如火嘅风土人情"],
        yuewen_merged="体验热情如火嘅风土人情",
    ),
    MergeTestCase(
        zhongwen="享受一个脱俗出尘的梦幻之旅",
        yuewen_to_merge=["享受一个脱轴出尘嘅梦幻之旅"],
        yuewen_merged="享受一个脱轴出尘嘅梦幻之旅",
    ),
    MergeTestCase(
        zhongwen="犀利旅行社，旅行社牌照号码350999",
        yuewen_to_merge=["犀利旅行社", "旅行社牌照号码350999"],
        yuewen_merged="犀利旅行社，旅行社牌照号码350999",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="妈妈你知道马尔代夫在哪儿吗？",
        yuewen_to_merge=["妈妈你知唔知到马尔代夫系边㗎"],
        yuewen_merged="妈妈你知唔知到马尔代夫系边㗎？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="很远的",
        yuewen_to_merge=["啊好远㗎"],
        yuewen_merged="啊好远㗎",
    ),
    MergeTestCase(
        zhongwen="有多远？",
        yuewen_to_merge=["点远发呀"],
        yuewen_merged="点远发呀？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="得搭飞机",
        yuewen_to_merge=["搭飞机至到啰"],
        yuewen_merged="搭飞机至到啰",
    ),
    MergeTestCase(
        zhongwen="妈妈你会带我去吗？",
        yuewen_to_merge=["咁妈妈你会唔会走落去㗎"],
        yuewen_merged="咁妈妈你会唔会走落去㗎？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="会！发财了再说吧",
        yuewen_to_merge=["会", "得学发咗先啦"],
        yuewen_merged="会！得学发咗先啦",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="那么妈妈你什么时候发？",
        yuewen_to_merge=["咁妈妈你几时发得呀"],
        yuewen_merged="咁妈妈你几时发得呀？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="快了⋯",
        yuewen_to_merge=["呃", "就快啦"],
        yuewen_merged="呃，就快啦⋯",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="发梦呀！",
        yuewen_to_merge=["发梦吖嘛"],
        yuewen_merged="发梦吖嘛！",
        difficulty=1,
    ),
]  # merge_test_cases_block_15
merge_test_cases_block_16 = [
    MergeTestCase(
        zhongwen="校长早晨！",
        yuewen_to_merge=["嗨"],
        yuewen_merged="嗨！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="你最喜爱的地方是哪儿？",
        yuewen_to_merge=["你最喜爱嘅地方喺边度呀"],
        yuewen_merged="你最喜爱嘅地方喺边度呀？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="我最喜爱的地方是日本",
        yuewen_to_merge=["我最喜爱嘅地方呢", "就系日本喇"],
        yuewen_merged="我最喜爱嘅地方呢，就系日本喇",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="那儿有Disneyland和Hello Kitty Land",
        yuewen_to_merge=["𠮶度好迪士尼呢", "同埋HelloTT呢"],
        yuewen_merged="𠮶度好迪士尼呢同埋HelloTT呢",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="我这个发夹也是在那儿买的",
        yuewen_to_merge=["我而家打紧个发卷都系𠮶边买嘅"],
        yuewen_merged="我而家打紧个发卷都系𠮶边买嘅",
    ),
    MergeTestCase(
        zhongwen="我最喜爱的地方是加拿大",
        yuewen_to_merge=["我最钟意嘅地方就系加拿大"],
        yuewen_merged="我最钟意嘅地方就系加拿大",
    ),
    MergeTestCase(
        zhongwen="婆婆跟舅父他们都在加拿大",
        yuewen_to_merge=["婆婆同埋舅父呀", "佢哋都系加拿大㗎"],
        yuewen_merged="婆婆同埋舅父呀，佢哋都系加拿大㗎",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="我最喜爱的地方是泰国",
        yuewen_to_merge=["我最钟意去嘅地方就系泰国喇"],
        yuewen_merged="我最钟意去嘅地方就系泰国喇",
    ),
    MergeTestCase(
        zhongwen="那儿有很好多水上活动，还有鱼翅吃",
        yuewen_to_merge=["𠮶度有好多水晶活动㗎", "仲有一次食添㖞"],
        yuewen_merged="𠮶度有好多水晶活动㗎，仲有一次食添㖞",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="我最喜爱的地方⋯",
        yuewen_to_merge=["呃", "我最喜爱嘅地方呢"],
        yuewen_merged="呃，我最喜爱嘅地方呢⋯",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="就是那间什么！",
        yuewen_to_merge=["就系𠮶间咩嚟啰"],
        yuewen_merged="就系𠮶间咩嚟啰！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="那儿有欢乐天地，还有美食广场",
        yuewen_to_merge=["𠮶度有欢乐天地啦", "仲有米食广场啦"],
        yuewen_merged="𠮶度有欢乐天地啦，仲有米食广场啦",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="那儿的海南鸡饭很大碟的",
        yuewen_to_merge=["𠮶度啲可能几份好大碟㗎"],
        yuewen_merged="𠮶度啲可能几份好大碟㗎",
    ),
    MergeTestCase(
        zhongwen="对了，那地方叫银城中心",
        yuewen_to_merge=["系喇系喇", "𠮶间叫做银城中心"],
        yuewen_merged="系喇系喇，𠮶间叫做银城中心",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="那店子的饭很多，很大碟的！",
        yuewen_to_merge=["𠮶间嘢啲饭好多人", "好大碟㗎"],
        yuewen_merged="𠮶间嘢啲饭好多人，好大碟㗎！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="不过说到我最想去的地方，那可厉害了",
        yuewen_to_merge=["不过讲到我最想去嘅地方呢", "𠮶度细嚟啰"],
        yuewen_merged="不过讲到我最想去嘅地方呢，𠮶度细嚟啰",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="那儿蓝天白云，椰林树影，水清沙幼",
        yuewen_to_merge=["𠮶度南天白云", "夜临树影", "水清沙幽"],
        yuewen_merged="𠮶度南天白云，夜临树影，水清沙幽",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="座落于印度洋的世外桃源",
        yuewen_to_merge=["独来鱼", "印度洋嘅世外桃源"],
        yuewen_merged="独来鱼印度洋嘅世外桃源",
        include_in_prompt=True,
        difficulty=2,
    ),
]  # merge_test_cases_block_16
merge_test_cases_block_17 = [
    MergeTestCase(
        zhongwen="衰仔，快点起床上学",
        yuewen_to_merge=["喂", "衰仔啊", "快啲起身返学喇"],
        yuewen_merged="喂，衰仔啊，快啲起身返学喇",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="咦？",
        yuewen_to_merge=["咦"],
        yuewen_merged="咦？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="妈妈！",
        yuewen_to_merge=["妈妈"],
        yuewen_merged="妈妈！",
        difficulty=1,
    ),
]  # merge_test_cases_block_17
merge_test_cases_block_18 = [
    MergeTestCase(
        zhongwen="开点药给他吃就没事了",
        yuewen_to_merge=["开啲药过佢食就冇事㗎喇"],
        yuewen_merged="开啲药过佢食就冇事㗎喇",
    ),
    MergeTestCase(
        zhongwen="医生，吃了药会不会有那个什么的？",
        yuewen_to_merge=["医生啊", "啲药食咗会唔会有𠮶啲咩㗎"],
        yuewen_merged="医生啊，啲药食咗会唔会有𠮶啲咩㗎？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="不会！",
        yuewen_to_merge=["唔会"],
        yuewen_merged="唔会！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="那么吃药用不用那个什么的？",
        yuewen_to_merge=["噉佢食药使唔使咩啊"],
        yuewen_merged="噉佢食药使唔使咩啊？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="不用！给他打口针吧！",
        yuewen_to_merge=["唔使", "同佢打多支针添呢"],
        yuewen_merged="唔使！同佢打多支针添呢！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="怎么？得打针？",
        yuewen_to_merge=["吓", "要打针啊"],
        yuewen_merged="吓？要打针啊？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="他最怕打针的了",
        yuewen_to_merge=["佢好怕打针㗎㖞"],
        yuewen_merged="佢好怕打针㗎㖞",
    ),
    MergeTestCase(
        zhongwen="那么他怕不怕死？",
        yuewen_to_merge=["噉佢怕唔怕死呀"],
        yuewen_merged="噉佢怕唔怕死呀？",
        difficulty=1,
    ),
]  # merge_test_cases_block_18
merge_test_cases_block_19 = [
    MergeTestCase(
        zhongwen="没事吧？快点先把药水喝掉！",
        yuewen_to_merge=["冇嘢吖嘛", "快啲食埋啲药水佢先啦"],
        yuewen_merged="冇嘢吖嘛？快啲食埋啲药水佢先啦！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="妈妈我不想喝药水",
        yuewen_to_merge=["妈妈", "我唔想食药水呀"],
        yuewen_merged="妈妈，我唔想食药水呀",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="不要呀妈妈，我不喝呀",
        yuewen_to_merge=["唔好捞妈妈", "我唔食呀"],
        yuewen_merged="唔好捞妈妈，我唔食呀",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="我不喝士多啤梨药水呀！",
        yuewen_to_merge=["我唔食士多啤梨药水呀"],
        yuewen_merged="我唔食士多啤梨药水呀！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="别哭了，不喝药水病不会好的",
        yuewen_to_merge=["唔好喊啦", "唔食药唔会好㗎"],
        yuewen_merged="唔好喊啦，唔食药唔会好㗎",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="乖乖，病好了妈妈带你去马尔代夫",
        yuewen_to_merge=["乖乖啲", "病好咗", "妈妈大理马尔代夫"],
        yuewen_merged="乖乖啲，病好咗妈妈大理马尔代夫",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="真的吗？",
        yuewen_to_merge=["真嘅"],
        yuewen_merged="真嘅？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="妈妈什么时候骗过你？",
        yuewen_to_merge=["妈妈几时呃过你呀"],
        yuewen_merged="妈妈几时呃过你呀？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="乖，先把药水喝掉",
        yuewen_to_merge=["乖", "食埋啲药水先啦"],
        yuewen_merged="乖，食埋啲药水先啦",
        difficulty=1,
    ),
]  # merge_test_cases_block_19
merge_test_cases_block_20 = [
    MergeTestCase(
        zhongwen="好呀，马尔代夫！",
        yuewen_to_merge=["嘻嘻", "好嘢", "买二代夫"],
        yuewen_merged="嘻嘻，好嘢，买二代夫！",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="马尔代夫！",
        yuewen_to_merge=["买二代夫"],
        yuewen_merged="买二代夫！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="妈妈，那么我们什么时候去？",
        yuewen_to_merge=["妈妈", "咁我哋几时去呀"],
        yuewen_merged="妈妈，咁我哋几时去呀？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="你先把药水喝掉，病好了我就去订机票",
        yuewen_to_merge=["嗯", "你乖乖哋食埋啲药", "好返晒啦", "我即刻订机票"],
        yuewen_merged="嗯，你乖乖哋食埋啲药，好返晒啦，我即刻订机票",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="来，多喝一点！",
        yuewen_to_merge=["嚟啦", "食多更"],
        yuewen_merged="嚟啦，食多更！",
        difficulty=1,
    ),
]  # merge_test_cases_block_20
merge_test_cases_block_21 = [
    MergeTestCase(
        zhongwen="妈妈，你看！",
        yuewen_to_merge=["妈妈你睇"],
        yuewen_merged="妈妈你睇！",
    ),
    MergeTestCase(
        zhongwen="妈妈你看，我病好了！",
        yuewen_to_merge=["我好返喇"],
        yuewen_merged="我好返喇！",
    ),
    MergeTestCase(
        zhongwen="我把药都吃光了",
        yuewen_to_merge=["啲嘢所以我全部食晒喇"],
        yuewen_merged="啲嘢所以我全部食晒喇",
    ),
    MergeTestCase(
        zhongwen="家中的东西有什么没给你吃光的？",
        yuewen_to_merge=["即系间屋有乜嘢唔系畀你食晒㗎"],
        yuewen_merged="即系间屋有乜嘢唔系畀你食晒㗎？",
    ),
    MergeTestCase(
        zhongwen="这次不同呀，原来这么一大樽的",
        yuewen_to_merge=["妈妈", "呢次唔同㗎", "本来咁大樽嘅"],
        yuewen_merged="妈妈，呢次唔同㗎，本来咁大樽嘅",
    ),
    MergeTestCase(
        zhongwen="我喝一格，又喝一格，又喝一格⋯",
        yuewen_to_merge=["我饮下一格", "又一格", "又一格"],
        yuewen_merged="我饮下一格，又一格，又一格⋯",
    ),
    MergeTestCase(
        zhongwen="就给我喝光了！",
        yuewen_to_merge=["吓", "咪我饮晒㖞"],
        yuewen_merged="吓，咪我饮晒㖞！",
    ),
]  # merge_test_cases_block_21
merge_test_cases_block_22 = [
    MergeTestCase(
        zhongwen="喝光了就叻仔了！",
        yuewen_to_merge=["饮实就叻仔啦"],
        yuewen_merged="饮实就叻仔啦！",
    ),
    MergeTestCase(
        zhongwen="喝光了就病好了！",
        yuewen_to_merge=["饮实就好返实啦"],
        yuewen_merged="饮实就好返实啦！",
    ),
    MergeTestCase(
        zhongwen="妈妈呀⋯",
        yuewen_to_merge=["妈妈"],
        yuewen_merged="妈妈⋯",
    ),
    MergeTestCase(
        zhongwen="什么事？",
        yuewen_to_merge=["乜嘢啊"],
        yuewen_merged="乜嘢啊？",
    ),
    MergeTestCase(
        zhongwen="我们什么时候去马尔代夫？",
        yuewen_to_merge=["阿哋几时去马尔代夫啊"],
        yuewen_merged="阿哋几时去马尔代夫啊？",
    ),
    MergeTestCase(
        zhongwen="什么马尔代夫？",
        yuewen_to_merge=["乜嘢马尔代夫啊"],
        yuewen_merged="乜嘢马尔代夫啊？",
    ),
    MergeTestCase(
        zhongwen="你说我病好带我去马尔代夫的呀！",
        yuewen_to_merge=["呢", "你话我返就同我去马尔代夫㗎嘛"],
        yuewen_merged="呢，你话我返就同我去马尔代夫㗎嘛！",
    ),
    MergeTestCase(
        zhongwen="马尔代夫，椰林树影，水清沙幼⋯",
        yuewen_to_merge=["马尔代夫呢", "耶南树影", "水清沙游"],
        yuewen_merged="马尔代夫呢，耶南树影，水清沙游⋯",
    ),
    MergeTestCase(
        zhongwen="座落于印度洋的世外桃源呀！",
        yuewen_to_merge=["助流于印度园嘅世外导演啦"],
        yuewen_merged="助流于印度园嘅世外导演啦！",
    ),
    MergeTestCase(
        zhongwen="想不到你还有点文采",
        yuewen_to_merge=["啊", "估唔到你几好文采㗎噃"],
        yuewen_merged="啊，估唔到你几好文采㗎噃",
    ),
    MergeTestCase(
        zhongwen="说得不错呀！",
        yuewen_to_merge=["讲得几好听啊"],
        yuewen_merged="讲得几好听啊！",
    ),
    MergeTestCase(
        zhongwen="我不是光说的呀，妈妈你说过⋯",
        yuewen_to_merge=["妈妈我唔系讲喇㗎", "又系你话嘅", "你话"],
        yuewen_merged="妈妈，我唔系讲喇㗎， 又系你话嘅，你话⋯",
    ),
    MergeTestCase(
        zhongwen="我病好了带我去马尔代夫的！",
        yuewen_to_merge=["我病好咗之日就同我去马尔代夫㗎", "你讲过㗎"],
        yuewen_merged="我病好咗之日就同我去马尔代夫㗎，你讲过㗎！",
    ),
    MergeTestCase(
        zhongwen="我是说发了财就带你去",
        yuewen_to_merge=["我话发咗先至同你去㗎"],
        yuewen_merged="我话发咗先至同你去㗎",
    ),
    MergeTestCase(
        zhongwen="不是的，妈妈你说我病好了就去的",
        yuewen_to_merge=["唔系㖞", "妈妈", "你话好咗就同我去㗎㖞"],
        yuewen_merged="唔系㖞，妈妈，你话好咗就同我去㗎㖞",
    ),
    MergeTestCase(
        zhongwen="你分明讲过病好了就去马尔代夫的",
        yuewen_to_merge=["你明明讲过好返就同你去马尔代夫㗎㖞"],
        yuewen_merged="你明明讲过好返就同你去马尔代夫㗎㖞",
    ),
    MergeTestCase(
        zhongwen="你讲过的！",
        yuewen_to_merge=["你讲过㗎"],
        yuewen_merged="你讲过㗎！",
    ),
    MergeTestCase(
        zhongwen="好了，别哭了",
        yuewen_to_merge=["得啦得啦", "唔好喊啦"],
        yuewen_merged="得啦，得啦，唔好喊啦",
    ),
    MergeTestCase(
        zhongwen="带你去马尔代夫好了",
        yuewen_to_merge=["同你去马尔代夫啦"],
        yuewen_merged="同你去马尔代夫啦",
    ),
    MergeTestCase(
        zhongwen="真的吗？　　对",
        yuewen_to_merge=["真嘅", "系啊"],
        yuewen_merged="真嘅？　　系啊",
    ),
    MergeTestCase(
        zhongwen="什么时候去？",
        yuewen_to_merge=["咁几时去啊"],
        yuewen_merged="咁几时去啊？",
    ),
    MergeTestCase(
        zhongwen="发财再说",
        yuewen_to_merge=["等我发咗先啰"],
        yuewen_merged="等我发咗先啰",
    ),
    MergeTestCase(
        zhongwen="你早发财了⋯",
        yuewen_to_merge=["你发咗㗎喇", "你发咗㗎喇"],
        yuewen_merged="你发咗㗎喇，你发咗㗎喇⋯",
    ),
    MergeTestCase(
        zhongwen="好了好了，发财了",
        yuewen_to_merge=["系喇系喇系喇发咗喇"],
        yuewen_merged="系喇，系喇，系喇，发咗喇",
    ),
    MergeTestCase(
        zhongwen="我们下个星期去，好了吧？",
        yuewen_to_merge=["下个礼拜同你去啦"],
        yuewen_merged="下个礼拜同你去啦？",
    ),
    MergeTestCase(
        zhongwen="太好了！",
        yuewen_to_merge=["得未啊", "好嘢"],
        yuewen_merged="得未啊！好嘢！",
    ),
]  # merge_test_cases_block_22
merge_test_cases_block_23 = [
    MergeTestCase(
        zhongwen="麦唛，我是麦兜呀",
        yuewen_to_merge=["喂", "麦麦啊", "麦豆啊我系", "即系呢"],
        yuewen_merged="喂，麦麦啊，麦豆啊，我系，即系呢",
    ),
    MergeTestCase(
        zhongwen="是这样子的，我明天就飞了",
        yuewen_to_merge=["我明日就要飞喇"],
        yuewen_merged="我明日就要飞喇",
    ),
    MergeTestCase(
        zhongwen="对　　⋯是吗？",
        yuewen_to_merge=["系啊", "系咩"],
        yuewen_merged="系啊　　⋯系咩？",
    ),
    MergeTestCase(
        zhongwen="飞机餐很难吃的吗？",
        yuewen_to_merge=["飞机真好难食㗎"],
        yuewen_merged="飞机真好难食㗎？",
    ),
    MergeTestCase(
        zhongwen="也得吃呀！",
        yuewen_to_merge=["但点都要食㗎啦"],
        yuewen_merged="但点都要食㗎啦！",
    ),
    MergeTestCase(
        zhongwen="难道自己带东西上去吃吗？",
        yuewen_to_merge=["唔通自己带嘢上去食咩"],
        yuewen_merged="唔通自己带嘢上去食咩？",
    ),
    MergeTestCase(
        zhongwen="还在讲？",
        yuewen_to_merge=["仲讲"],
        yuewen_merged="仲讲？",
    ),
    MergeTestCase(
        zhongwen="快点帮手执行李",
        yuewen_to_merge=["哦", "快啲嚟执埋啲行李先啦", "哦"],
        yuewen_merged="哦，快啲嚟执埋啲行李先啦，哦",
    ),
    MergeTestCase(
        zhongwen="跟我向他们说，我明天去马尔代夫了",
        yuewen_to_merge=["你帮我话畀佢哋知", "我明日去买热带裤薄"],
        yuewen_merged="你帮我话畀佢哋知，我明日去买热带裤薄",
    ),
    MergeTestCase(
        zhongwen="那边蓝天白云，椰林树影⋯",
        yuewen_to_merge=["𠮶度蓝天五百云", "夜临雪"],
        yuewen_merged="𠮶度蓝天五百云，夜临雪⋯",
    ),
    MergeTestCase(
        zhongwen="还在讲！",
        yuewen_to_merge=["水清净沙有"],
        yuewen_merged="水清净沙有！",
    ),
    MergeTestCase(
        zhongwen="来了！",
        yuewen_to_merge=["我嚟紧㗎喇"],
        yuewen_merged="我嚟紧㗎喇！",
    ),
    MergeTestCase(
        zhongwen="要执行李了，回来再跟你说吧",
        yuewen_to_merge=["我要执行你喇", "返嚟先再同你倾过啦"],
        yuewen_merged="我要执行你喇，返嚟先再同你倾过啦",
    ),
    MergeTestCase(
        zhongwen="再见！",
        yuewen_to_merge=["拜拜"],
        yuewen_merged="拜拜！",
    ),
]  # merge_test_cases_block_23
merge_test_cases_block_24 = [
    MergeTestCase(
        zhongwen="妈妈，我得把出世纸带着吗？",
        yuewen_to_merge=["哎哟", "妈妈", "我系咪要带埋出世纸去㗎"],
        yuewen_merged="哎哟，妈妈，我系咪要带埋出世纸去㗎？",
    ),
    MergeTestCase(
        zhongwen="也要的",
        yuewen_to_merge=["都要㗎"],
        yuewen_merged="都要㗎",
    ),
    MergeTestCase(
        zhongwen="那么成绩表呢？",
        yuewen_to_merge=["咁成绩表呢"],
        yuewen_merged="咁成绩表呢？",
    ),
    MergeTestCase(
        zhongwen="成绩表就不用了",
        yuewen_to_merge=["成绩表又唔使"],
        yuewen_merged="成绩表又唔使",
    ),
    MergeTestCase(
        zhongwen="太好了！吓得我！",
        yuewen_to_merge=["好嘢", "吓得我啊", "咁都好啲"],
        yuewen_merged="好嘢！吓得我啊！咁都好啲",
    ),
]  # merge_test_cases_block_24
merge_test_cases_block_25 = [
    MergeTestCase(
        zhongwen="找到了！",
        yuewen_to_merge=["揾到喇"],
        yuewen_merged="揾到喇！",
    ),
    MergeTestCase(
        zhongwen="妈妈你替我收好它别抛掉",
        yuewen_to_merge=[
            "竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然"
        ],
        yuewen_merged="竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然",
    ),
]  # merge_test_cases_block_25
merge_test_cases_block_26 = [
    MergeTestCase(
        zhongwen="早机去，晚机返",
        yuewen_to_merge=["早机去", "晚机返"],
        yuewen_merged="早机去，晚机返",
    ),
    MergeTestCase(
        zhongwen="妈妈说这样才够精明",
        yuewen_to_merge=["妈妈话噉先最著数"],
        yuewen_merged="妈妈话噉先最著数",
    ),
    MergeTestCase(
        zhongwen="就这样⋯",
        yuewen_to_merge=["就系噉样"],
        yuewen_merged="就系噉样⋯",
    ),
    MergeTestCase(
        zhongwen="我过了我小时候最精明⋯",
        yuewen_to_merge=["我过咗我小时候最著数"],
        yuewen_merged="我过咗我小时候最著数⋯",
    ),
    MergeTestCase(
        zhongwen="最美丽的一天",
        yuewen_to_merge=["最完美嘅一日"],
        yuewen_merged="最完美嘅一日",
    ),
    MergeTestCase(
        zhongwen="依你说，纸是否可以包着鸡呢？",
        yuewen_to_merge=["噉你话纸包唔包得绝鸡呢"],
        yuewen_merged="噉你话，纸包唔包得绝鸡呢？",
    ),
    MergeTestCase(
        zhongwen="也可以的⋯",
        yuewen_to_merge=["都得嘅"],
        yuewen_merged="都得嘅⋯",
    ),
    MergeTestCase(
        zhongwen="特别是小小一块的",
        yuewen_to_merge=["尤其系细细旧𠮶啲"],
        yuewen_merged="尤其系细细旧𠮶啲",
    ),
]  # merge_test_cases_block_26
merge_test_cases_block_27 = [
    MergeTestCase(
        zhongwen="妈妈晚安！",
        yuewen_to_merge=["妈妈", "做头"],
        yuewen_merged="妈妈，做头！",
    ),
]  # merge_test_cases_block_27
merge_test_cases_block_28 = [
    MergeTestCase(
        zhongwen="最新消息",
        yuewen_to_merge=["啱啱收到消息"],
        yuewen_merged="啱啱收到消息",
    ),
    MergeTestCase(
        zhongwen="奥运滑浪风帆选手李丽珊五场四胜",
        yuewen_to_merge=["奥运滑浪风帆选手李丽珊以五场四胜嘅结果"],
        yuewen_merged="奥运滑浪风帆选手李丽珊以五场四胜嘅结果",
    ),
    MergeTestCase(
        zhongwen="夺得香港历史上第一面奥运金牌！",
        yuewen_to_merge=["夺取香港历史上第一面奥运金牌"],
        yuewen_merged="夺取香港历史上第一面奥运金牌！",
    ),
    MergeTestCase(
        zhongwen="消息说当李丽珊获悉自己稳夺金牌后",
        yuewen_to_merge=["消息话李丽珊喺知道自己稳夺奥运金牌之后"],
        yuewen_merged="消息话李丽珊喺知道自己稳夺奥运金牌之后",
    ),
    MergeTestCase(
        zhongwen="激动地对在场记者表示她今次的成绩⋯",
        yuewen_to_merge=["好激动噉同在场嘅记者讲"],
        yuewen_merged="好激动噉同在场嘅记者讲⋯",
    ),
    MergeTestCase(
        zhongwen="足以证明香港运动员不是腊鸭！",
        yuewen_to_merge=["今次佢嘅成绩可以证明到香港嘅运动员唔系𫚭鸭"],
        yuewen_merged="今次佢嘅成绩可以证明到香港嘅运动员唔系𫚭鸭！",
    ),
    MergeTestCase(
        zhongwen="对不起，应该　　是垃圾，不是腊鸭！",
        yuewen_to_merge=["各位对唔住", "应该系垃圾", "唔系𫚭鸭"],
        yuewen_merged="各位对唔住，应该系垃圾，唔系𫚭鸭！",
    ),
    MergeTestCase(
        zhongwen="对不起，应该　　不是垃圾，也不是腊鸭！",
        yuewen_to_merge=["对唔住", "应该系唔系垃圾", "亦都唔系𫚭鸭"],
        yuewen_merged="对唔住，应该系唔系垃圾，亦都唔系𫚭鸭！",
    ),
    MergeTestCase(
        zhongwen="特别报告完毕",
        yuewen_to_merge=["特别报个原不"],
        yuewen_merged="特别报个原不",
    ),
]  # merge_test_cases_block_28
merge_test_cases_block_29 = [
    MergeTestCase(
        zhongwen="妈妈好像又有计了",
        yuewen_to_merge=["咦", "妈妈好似又有计噉噃"],
        yuewen_merged="咦，妈妈好似又有计噉噃",
    ),
    MergeTestCase(
        zhongwen="靓仔，好运，叻仔⋯",
        yuewen_to_merge=["靓仔", "好运", "叻仔呀"],
        yuewen_merged="靓仔，好运，叻仔呀⋯",
    ),
    MergeTestCase(
        zhongwen="好像都没希望了",
        yuewen_to_merge=["睇嚟都唔多靠得住"],
        yuewen_merged="睇嚟都唔多靠得住",
    ),
    MergeTestCase(
        zhongwen="是不是可以靠手瓜呢？",
        yuewen_to_merge=["哗", "好唔好靠下个手瓜噉呢"],
        yuewen_merged="哗，好唔好靠下个手瓜噉呢？",
    ),
    MergeTestCase(
        zhongwen="于是，一个梦还没醒⋯",
        yuewen_to_merge=["于是", "一个梦都未醒"],
        yuewen_merged="于是，一个梦都未醒⋯",
    ),
    MergeTestCase(
        zhongwen="我又得到另一个梦",
        yuewen_to_merge=["我又得到另外一个梦"],
        yuewen_merged="我又得到另外一个梦",
    ),
    MergeTestCase(
        zhongwen="应该是脚瓜",
        yuewen_to_merge=["系咪应该系脚瓜之争"],
        yuewen_merged="系咪应该系脚瓜之争",
    ),
    MergeTestCase(
        zhongwen="我知道一点也不容易",
        yuewen_to_merge=["我知道一啲都唔容易"],
        yuewen_merged="我知道一啲都唔容易",
    ),
    MergeTestCase(
        zhongwen="我知道要找到黎根绝对不容易",
        yuewen_to_merge=["我知道要揾到励根绝对唔容易"],
        yuewen_merged="我知道要揾到励根绝对唔容易",
    ),
    MergeTestCase(
        zhongwen="我知道要他收我做徒弟更加不容易",
        yuewen_to_merge=["我知道要佢收我做徒弟更加唔容易"],
        yuewen_merged="我知道要佢收我做徒弟更加唔容易",
    ),
]  # merge_test_cases_block_29
merge_test_cases_block_30 = [
    MergeTestCase(
        zhongwen="但无论多不容易，我都要试一试",
        yuewen_to_merge=["但无论几唔容易", "我都要试一试"],
        yuewen_merged="但无论几唔容易，我都要试一试",
    ),
    MergeTestCase(
        zhongwen="我要黎根收我做徒弟！",
        yuewen_to_merge=["我要来紧收我度徒弟"],
        yuewen_merged="我要来紧收我度徒弟！",
    ),
    MergeTestCase(
        zhongwen="无论几辛苦，我一定要得到奥运金牌！",
        yuewen_to_merge=["无论几辛苦", "我一定要捞到奥运金牌"],
        yuewen_merged="无论几辛苦，我一定要捞到奥运金牌！",
    ),
]  # merge_test_cases_block_30
merge_test_cases_block_31 = [
    MergeTestCase(
        zhongwen="当我站在奥运会颁奖台上",
        yuewen_to_merge=["三张堂上面"],
        yuewen_merged="三张堂上面",
    ),
    MergeTestCase(
        zhongwen="我会举起金牌跟全世界说：",
        yuewen_to_merge=["系今排同全世界讲"],
        yuewen_merged="系今排同全世界讲：",
    ),
]  # merge_test_cases_block_31
merge_test_cases_block_32 = [
    MergeTestCase(
        zhongwen="长洲，我终于来到长洲了！",
        yuewen_to_merge=["长洲", "我终于嚟到长洲嘞"],
        yuewen_merged="长洲，我终于嚟到长洲嘞！",
    ),
]  # merge_test_cases_block_32
merge_test_cases_block_33 = [
    MergeTestCase(
        zhongwen="长洲，我得亲吻这片圣洁的土地！",
        yuewen_to_merge=["长洲", "我要亲吻呢片盛洁嘅土地"],
        yuewen_merged="长洲，我要亲吻呢片盛洁嘅土地！",
    ),
]  # merge_test_cases_block_33
merge_test_cases_block_34 = [
    MergeTestCase(
        zhongwen="小朋友，这儿是南丫岛呀！",
        yuewen_to_merge=["小朋友呀", "呢度系南丫岛噃"],
        yuewen_merged="小朋友呀，呢度系南丫岛噃！",
    ),
    MergeTestCase(
        zhongwen="南丫岛？它也孕育了周润发！",
        yuewen_to_merge=["南丫岛", "都引用咗周润发噃"],
        yuewen_merged="南丫岛？都引用咗周润发噃！",
    ),
]  # merge_test_cases_block_34
merge_test_cases_block_35 = [
    MergeTestCase(
        zhongwen="想不到我黎根避进南丫岛也给你发现",
        yuewen_to_merge=["制估唔到我嚟跟你入嚟南丫岛都畀你揾到"],
        yuewen_merged="制估唔到我嚟跟你入嚟南丫岛都畀你揾到",
    ),
    MergeTestCase(
        zhongwen="小朋友，你知道什么是狗仔队吧？",
        yuewen_to_merge=["小朋友", "我谂你都知道乜嘢叫做狗仔队嘞"],
        yuewen_merged="小朋友，我谂你都知道乜嘢叫做狗仔队嘞？",
    ),
    MergeTestCase(
        zhongwen="加上总有小朋友及家长来说要拜我为师",
        yuewen_to_merge=["再加上不时有啲小朋友同埋家长嚟揾我话要拜我为师"],
        yuewen_merged="再加上不时有啲小朋友同埋家长嚟揾我话要拜我为师",
    ),
    MergeTestCase(
        zhongwen="我才过来南丫岛避一避",
        yuewen_to_merge=["所以我咪过嚟南丫岛避一避"],
        yuewen_merged="所以我咪过嚟南丫岛避一避",
    ),
    MergeTestCase(
        zhongwen="至于拜师的事⋯",
        yuewen_to_merge=["至于拜师嘅嘢"],
        yuewen_merged="至于拜师嘅嘢⋯",
    ),
    MergeTestCase(
        zhongwen="拜你个头！",
        yuewen_to_merge=["拜你个头嘅"],
        yuewen_merged="拜你个头嘅！",
    ),
    MergeTestCase(
        zhongwen="你们这些住香港岛的小朋友骄生惯养",
        yuewen_to_merge=["你哋呢班住喺香港岛嘅小朋友娇生惯养"],
        yuewen_merged="你哋呢班住喺香港岛嘅小朋友娇生惯养",
    ),
    MergeTestCase(
        zhongwen="怎么吃得苦？",
        yuewen_to_merge=["边挨得苦㗎"],
        yuewen_merged="边挨得苦㗎？",
    ),
    MergeTestCase(
        zhongwen="想跟珊珊般得奥运金牌？",
        yuewen_to_merge=["想学山伞攞奥运金牌"],
        yuewen_merged="想学山伞攞奥运金牌？",
    ),
    MergeTestCase(
        zhongwen="别作梦了！",
        yuewen_to_merge=["食母你嘢"],
        yuewen_merged="食母你嘢！",
    ),
]  # merge_test_cases_block_35
merge_test_cases_block_36 = [
    MergeTestCase(
        zhongwen="小朋友，你看！",
        yuewen_to_merge=["小朋友", "你睇下"],
        yuewen_merged="小朋友，你睇下！",
    ),
]  # merge_test_cases_block_36
merge_test_cases_block_37 = [
    MergeTestCase(
        zhongwen="这个⋯",
        yuewen_to_merge=["哗"],
        yuewen_merged="哗⋯",
    ),
    MergeTestCase(
        zhongwen="这脚瓜⋯好粗好大！比一节瓜还要大！",
        yuewen_to_merge=["呢只", "呢只脚瓜好粗好大呀", "仲大个只瓜呀"],
        yuewen_merged="呢只，呢只脚瓜好粗好大呀！仲大个只瓜呀！",
    ),
    MergeTestCase(
        zhongwen="脚瓜的肌肉非常结实⋯",
        yuewen_to_merge=["脚瓜啲肌肉非常结实"],
        yuewen_merged="脚瓜啲肌肉非常结实⋯",
    ),
    MergeTestCase(
        zhongwen="青筋凸现，钢线似的",
        yuewen_to_merge=["啲青筋凸晒出嚟", "好似钢线噉"],
        yuewen_merged="啲青筋凸晒出嚟，好似钢线噉",
    ),
    MergeTestCase(
        zhongwen="每一条脚毛都硬似铁钉",
        yuewen_to_merge=["啲脚毛", "每一条好似铁钉噉硬"],
        yuewen_merged="啲脚毛，每一条好似铁钉噉硬",
    ),
    MergeTestCase(
        zhongwen="脚趾甲有一寸厚，究竟⋯",
        yuewen_to_merge=["脚趾弓啲脚甲成吋噉厚", "究竟"],
        yuewen_merged="脚趾弓啲脚甲成吋噉厚，究竟⋯",
    ),
    MergeTestCase(
        zhongwen="要行过几多座山⋯",
        yuewen_to_merge=["要行我几多座山"],
        yuewen_merged="要行我几多座山⋯",
    ),
    MergeTestCase(
        zhongwen="跨过几多个海⋯",
        yuewen_to_merge=["跨我几多个海"],
        yuewen_merged="跨我几多个海⋯",
    ),
    MergeTestCase(
        zhongwen="吃过几多苦头⋯",
        yuewen_to_merge=["挨过几多苦头"],
        yuewen_merged="挨过几多苦头⋯",
    ),
    MergeTestCase(
        zhongwen="才可以练成这举世无双的脚瓜？",
        yuewen_to_merge=["先至可以练成呢只举世无双嘅脚瓜"],
        yuewen_merged="先至可以练成呢只举世无双嘅脚瓜？",
    ),
]  # merge_test_cases_block_37
merge_test_cases_block_38 = [
    MergeTestCase(
        zhongwen="我⋯我一定要练成这脚瓜！",
        yuewen_to_merge=["我", "我一定要练成呢只脚挂"],
        yuewen_merged="我⋯我一定要练成呢只脚挂！",
    ),
    MergeTestCase(
        zhongwen="师傅！",
        yuewen_to_merge=["师父"],
        yuewen_merged="师父！",
    ),
]  # merge_test_cases_block_38
merge_test_cases_block_39 = [
    MergeTestCase(
        zhongwen="我可以去小个便吗？",
        yuewen_to_merge=["我可唔可以去个小便呢"],
        yuewen_merged="我可唔可以去个小便呢？",
    ),
]  # merge_test_cases_block_39
merge_test_cases_block_40 = [
    MergeTestCase(
        zhongwen="每次唱这首歌，我都会急小便",
        yuewen_to_merge=["而知点解每一字唱呢首歌都会急小便"],
        yuewen_merged="而知点解每一字唱呢首歌都会急小便",
    ),
    MergeTestCase(
        zhongwen="现在先去，一回恐怕还是会急",
        yuewen_to_merge=["仅次去定先都怕一阵会再急过"],
        yuewen_merged="仅次去定先，都怕一阵会再急过",
    ),
    MergeTestCase(
        zhongwen="但是我现在一定要唱这首歌",
        yuewen_to_merge=["但系我而家一定要唱呢首歌"],
        yuewen_merged="但系我而家一定要唱呢首歌",
    ),
    MergeTestCase(
        zhongwen="希望可以改变黎根对我的看法",
        yuewen_to_merge=["希望可以改变黎根对我嘅睇法"],
        yuewen_merged="希望可以改变黎根对我嘅睇法",
    ),
    MergeTestCase(
        zhongwen="我要用这歌打动黎根",
        yuewen_to_merge=["我要用呢首歌打动黎根"],
        yuewen_merged="我要用呢首歌打动黎根",
    ),
    MergeTestCase(
        zhongwen="我要黎根收我做徒弟！",
        yuewen_to_merge=["我要黎根收我做徒弟"],
        yuewen_merged="我要黎根收我做徒弟！",
    ),
    MergeTestCase(
        zhongwen="歌，是这样唱的⋯",
        yuewen_to_merge=["𠮶首歌系噉唱嘅"],
        yuewen_merged="𠮶首歌系噉唱嘅⋯",
    ),
]  # merge_test_cases_block_40
merge_test_cases_block_41 = [
    MergeTestCase(
        zhongwen="黎根听完歌以后，表情有点古怪⋯",
        yuewen_to_merge=["黎今听完首歌之后", "啲表情有啲古怪"],
        yuewen_merged="黎今听完首歌之后，啲表情有啲古怪⋯",
    ),
    MergeTestCase(
        zhongwen="我一定要好好把握这机会",
        yuewen_to_merge=["唔", "我一定要好好把握呢个机会"],
        yuewen_merged="唔，我一定要好好把握呢个机会",
    ),
    MergeTestCase(
        zhongwen="师傅！你收我做徒弟吧！",
        yuewen_to_merge=["师父", "你收我做徒弟啦"],
        yuewen_merged="师父！你收我做徒弟啦！",
    ),
    MergeTestCase(
        zhongwen="你唔收我做徒弟，我一世都这么跪着！",
        yuewen_to_merge=["你收我做徒弟", "我呢一世都跪喺度"],
        yuewen_merged="你收我做徒弟，我呢一世都跪喺度！",
    ),
    MergeTestCase(
        zhongwen="起来呀！",
        yuewen_to_merge=["起身啊"],
        yuewen_merged="起身啊！",
    ),
    MergeTestCase(
        zhongwen="多谢师傅！",
        yuewen_to_merge=["多谢师父"],
        yuewen_merged="多谢师父！",
    ),
    MergeTestCase(
        zhongwen="不⋯我是叫你扶我起来呀！",
        yuewen_to_merge=["唔系啊", "我系叫你扶我起身啊"],
        yuewen_merged="唔系啊⋯我系叫你扶我起身啊！",
    ),
    MergeTestCase(
        zhongwen="不成了！我的脚瓜太痹了！",
        yuewen_to_merge=[
            "顶唔顺啊",
            "我个腿挂好鼻啊",
            "字幕由",
            "Amara.org",
            "社群提供",
        ],
        yuewen_merged="顶唔顺啊！我个腿挂好鼻啊！字幕由Amara.org社群提供",
    ),
]  # merge_test_cases_block_41
merge_test_cases_block_42 = [
    MergeTestCase(
        zhongwen="我将今天发生的事讲给妈妈听",
        yuewen_to_merge=["我将今日发生嘅嘢话晒畀妈妈听"],
        yuewen_merged="我将今日发生嘅嘢话晒畀妈妈听",
    ),
    MergeTestCase(
        zhongwen="妈妈一句话也没说",
        yuewen_to_merge=["妈妈佢乜嘢都冇讲到"],
        yuewen_merged="妈妈佢乜嘢都冇讲到",
    ),
    MergeTestCase(
        zhongwen="从冰箱内拿了只雪鸡出来解冻",
        yuewen_to_merge=["净系喺冰箱度攞咗只雪鸡出嚟解冻"],
        yuewen_merged="净系喺冰箱度攞咗只雪鸡出嚟解冻",
    ),
    MergeTestCase(
        zhongwen="晚饭时，妈妈倒了三杯米酒",
        yuewen_to_merge=["晚饭时候", "妈妈倒咗三杯米酒"],
        yuewen_merged="晚饭时候，妈妈倒咗三杯米酒",
    ),
    MergeTestCase(
        zhongwen="又将几只橙和蒸好的鸡放到祖先前",
        yuewen_to_merge=["再将几个铲同埋蒸熟咗嘅鸡", "放喺祖先前面"],
        yuewen_merged="再将几个铲同埋蒸熟咗嘅鸡放喺祖先前面",
    ),
    MergeTestCase(
        zhongwen="妈妈叫我跪低，向祖先请请",
        yuewen_to_merge=["妈妈叫我跪低", "同祖先请请"],
        yuewen_merged="妈妈叫我跪低，同祖先请请",
    ),
    MergeTestCase(
        zhongwen="妈妈跟着又念念有词的",
        yuewen_to_merge=["跟住", "妈妈口噏噏噉讲咗一啲嘢"],
        yuewen_merged="跟住，妈妈口噏噏噉讲咗一啲嘢",
    ),
    MergeTestCase(
        zhongwen="然后我们一起向祖先再拜了几拜",
        yuewen_to_merge=["然之后我哋又一齐对住祖先拜多几拜"],
        yuewen_merged="然之后我哋又一齐对住祖先拜多几拜",
    ),
    MergeTestCase(
        zhongwen="妈妈蹲低把酒洒到地上",
        yuewen_to_merge=["妈妈虎低身将啲酒倒喺地上面"],
        yuewen_merged="妈妈虎低身将啲酒倒喺地上面",
    ),
    MergeTestCase(
        zhongwen="庄重而温柔地跟我说：",
        yuewen_to_merge=["庄重又温柔紧同我讲"],
        yuewen_merged="庄重又温柔紧同我讲：",
    ),
    MergeTestCase(
        zhongwen="以后生生性性",
        yuewen_to_merge=["以后要生生性性"],
        yuewen_merged="以后要生生性性",
    ),
    MergeTestCase(
        zhongwen="跟师傅学习，光宗耀祖！",
        yuewen_to_merge=["跟师父学嘢", "当中要祖"],
        yuewen_merged="跟师父学嘢，当中要祖！",
    ),
]  # merge_test_cases_block_42
merge_test_cases_block_43 = [
    MergeTestCase(
        zhongwen="妈妈在长洲找了间酒楼摆拜师宴",
        yuewen_to_merge=["妈妈喺长洲揾咗间酒楼", "摆咗几回白丝宴"],
        yuewen_merged="妈妈喺长洲揾咗间酒楼摆咗几回白丝宴",
    ),
    MergeTestCase(
        zhongwen="因为我是师傅最后一个入室弟子",
        yuewen_to_merge=["因为我系师父最后一个入室弟子"],
        yuewen_merged="因为我系师父最后一个入室弟子",
    ),
    MergeTestCase(
        zhongwen="到贺的乡绅父老特别多",
        yuewen_to_merge=["所以到学嘅乡亲父老特别多"],
        yuewen_merged="所以到学嘅乡亲父老特别多",
    ),
    MergeTestCase(
        zhongwen="想不到黄德森也来了",
        yuewen_to_merge=["估唔到黄德森都有嚟饮"],
        yuewen_merged="估唔到黄德森都有嚟饮",
    ),
    MergeTestCase(
        zhongwen="还赞我背上的肉厚",
        yuewen_to_merge=["仲赞我背著啲肉口添"],
        yuewen_merged="仲赞我背著啲肉口添",
    ),
    MergeTestCase(
        zhongwen="珊珊因为去了集训，没来",
        yuewen_to_merge=["但系山神就去咗集训", "冇嚟到"],
        yuewen_merged="但系山神就去咗集训，冇嚟到",
    ),
    MergeTestCase(
        zhongwen="麦唛，菇时跟得巴都来了",
        yuewen_to_merge=["默默", "姑侍同德巴都嚟咗"],
        yuewen_merged="默默，姑侍同德巴都嚟咗",
    ),
    MergeTestCase(
        zhongwen="还带着成绩表，奖牌和大包",
        yuewen_to_merge=["仲带埋成绩表", "奖牌", "同大包嚟添"],
        yuewen_merged="仲带埋成绩表，奖牌，同大包嚟添",
    ),
    MergeTestCase(
        zhongwen="他们都希望黎根也可以收他们做徒弟",
        yuewen_to_merge=["佢哋都希望嚟今可以收埋佢哋做徒弟"],
        yuewen_merged="佢哋都希望嚟今可以收埋佢哋做徒弟",
    ),
    MergeTestCase(
        zhongwen="吃过鸡丝翅，就是拜师仪式",
        yuewen_to_merge=["食完鸡丝翅", "就到咗拜师仪式"],
        yuewen_merged="食完鸡丝翅，就到咗拜师仪式",
    ),
    MergeTestCase(
        zhongwen="妈妈倒了杯茶给我，让我给师傅喝",
        yuewen_to_merge=["妈妈针咗杯热茶畀我", "叫我弟畀师父饮"],
        yuewen_merged="妈妈针咗杯热茶畀我，叫我弟畀师父饮",
    ),
    MergeTestCase(
        zhongwen="我千辛万苦来长洲找黎根⋯",
        yuewen_to_merge=["哦", "我前三万苦嚟到长洲揾嚟近"],
        yuewen_merged="哦，我前三万苦嚟到长洲揾嚟近⋯",
    ),
    MergeTestCase(
        zhongwen="我终于可以跟珊珊一起练滑浪风帆了！",
        yuewen_to_merge=["哦", "我终于可以同山神一齐练习玩弄风范啊"],
        yuewen_merged="哦，我终于可以同山神一齐练习玩弄风范啊！",
    ),
    MergeTestCase(
        zhongwen="我将茶递给黎根，黎根他⋯",
        yuewen_to_merge=["我将杯茶递咗畀嚟跟嚟跟佢"],
        yuewen_merged="我将杯茶递咗畀嚟跟，嚟跟佢⋯",
    ),
    MergeTestCase(
        zhongwen="师傅他把茶喝了，正式收我做徒弟",
        yuewen_to_merge=["亦唔系", "师父佢饮咗杯茶", "正式收咗我做徒弟嘞"],
        yuewen_merged="亦唔系，师父佢饮咗杯茶，正式收咗我做徒弟嘞",
    ),
    MergeTestCase(
        zhongwen="宾客们好像都很高兴",
        yuewen_to_merge=["啲来宾睇嚟好高气"],
        yuewen_merged="啲来宾睇嚟好高气",
    ),
    MergeTestCase(
        zhongwen="长洲的乡绅父老拍掌拍得特别落力",
        yuewen_to_merge=["特别系长洲啲乡亲父老", "拍奖拍得特别落力"],
        yuewen_merged="特别系长洲啲乡亲父老拍奖拍得特别落力",
    ),
    MergeTestCase(
        zhongwen="多谢各位赏面！多谢各位！",
        yuewen_to_merge=["多谢各位上面", "多谢各位"],
        yuewen_merged="多谢各位上面！多谢各位！",
    ),
    MergeTestCase(
        zhongwen="在下平生有两项称得上得意的绝技",
        yuewen_to_merge=["在下评生有两项称得上得意嘅绝技"],
        yuewen_merged="在下评生有两项称得上得意嘅绝技",
    ),
    MergeTestCase(
        zhongwen="第一项，是滑浪风帆！",
        yuewen_to_merge=["第一样系滑浪风范"],
        yuewen_merged="第一样系滑浪风范！",
    ),
    MergeTestCase(
        zhongwen="我把它传给外甥女珊珊了",
        yuewen_to_merge=["呢样早已传咗畀我外甥女山神啊"],
        yuewen_merged="呢样早已传咗畀我外甥女山神啊",
    ),
    MergeTestCase(
        zhongwen="另一项绝技，我打算传给这个新徒弟⋯",
        yuewen_to_merge=["另一项绝技我打算传畀呢个新修嘅徒弟"],
        yuewen_merged="另一项绝技，我打算传畀呢个新修嘅徒弟⋯",
    ),
    MergeTestCase(
        zhongwen="希望他把长洲人世世代代的绝技",
        yuewen_to_merge=["希望我可以将我哋长洲人世世代代嘅传统"],
        yuewen_merged="希望我可以将我哋长洲人世世代代嘅传统",
    ),
    MergeTestCase(
        zhongwen="发扬光大！",
        yuewen_to_merge=["发扬光大"],
        yuewen_merged="发扬光大！",
    ),
    MergeTestCase(
        zhongwen="请问那是什么绝技呢？",
        yuewen_to_merge=["噉请问𠮶样绝技系乜嘢啊"],
        yuewen_merged="噉请问𠮶样绝技系乜嘢啊？",
    ),
]  # merge_test_cases_block_43
merge_test_cases_block_44 = [
    MergeTestCase(
        zhongwen="第二项绝技，就是⋯",
        yuewen_to_merge=["第二样绝技就系"],
        yuewen_merged="第二样绝技，就系⋯",
    ),
    MergeTestCase(
        zhongwen="抢包山！",
        yuewen_to_merge=["抢爆山"],
        yuewen_merged="抢爆山！",
    ),
]  # merge_test_cases_block_44
merge_test_cases_block_45 = [
    MergeTestCase(
        zhongwen="抢包山？",
        yuewen_to_merge=["抢包山?"],
        yuewen_merged="抢包山？",
    ),
    MergeTestCase(
        zhongwen="年轻观众可能不知「抢包山」何物",
        yuewen_to_merge=["年轻嘅观众可能唔知乜嘢系抢包山呀"],
        yuewen_merged="年轻嘅观众可能唔知乜嘢系「抢包山」呀",
    ),
    MergeTestCase(
        zhongwen="抢包山乃长洲独有传统节日",
        yuewen_to_merge=["抢包山系长洲独有嘅传统节日"],
        yuewen_merged="抢包山系长洲独有嘅传统节日",
    ),
    MergeTestCase(
        zhongwen="每年农历四月",
        yuewen_to_merge=["每年农历四月"],
        yuewen_merged="每年农历四月",
    ),
    MergeTestCase(
        zhongwen="长洲居民均举办太平清醮",
        yuewen_to_merge=["长洲嘅居民都会举办太平清朝"],
        yuewen_merged="长洲嘅居民都会举办太平清朝",
    ),
    MergeTestCase(
        zhongwen="于北帝庙前搭起三座包山",
        yuewen_to_merge=["喺北帝庙前搭起三座包山"],
        yuewen_merged="喺北帝庙前搭起三座包山",
    ),
    MergeTestCase(
        zhongwen="什么是包山呢？",
        yuewen_to_merge=["噉乜嘢系包山呢?"],
        yuewen_merged="噉乜嘢系包山呢？",
    ),
    MergeTestCase(
        zhongwen="顾名思义⋯",
        yuewen_to_merge=["顾名思义"],
        yuewen_merged="顾名思义⋯",
    ),
    MergeTestCase(
        zhongwen="包山就是一座由好多好多包砌起的山！",
        yuewen_to_merge=["包山就系一座由好多", "好多", "好多包砌起嘅山"],
        yuewen_merged="包山就系一座由好多，好多，好多包砌起嘅山！",
    ),
    MergeTestCase(
        zhongwen="一座包山，起码六、七层楼高⋯",
        yuewen_to_merge=["一座包山起码六七层楼高"],
        yuewen_merged="一座包山起码六七层楼高⋯",
    ),
    MergeTestCase(
        zhongwen="你可以想像一下包山有多高了吧？",
        yuewen_to_merge=["噉你可以想像一下𠮶度有几多包喇"],
        yuewen_merged="噉你可以想像一下𠮶度有几多包喇？",
    ),
    MergeTestCase(
        zhongwen="抢包山，就是要把包山上的包抢到手！",
        yuewen_to_merge=["噉抢包山", "自然就系要将包山嘅包抢到手"],
        yuewen_merged="噉抢包山，自然就系要将包山嘅包抢到手！",
    ),
    MergeTestCase(
        zhongwen="锣鼓响起",
        yuewen_to_merge=["罗古响起"],
        yuewen_merged="罗古响起",
    ),
    MergeTestCase(
        zhongwen="数以百计的青年一涌而上抢包",
        yuewen_to_merge=["数以百计嘅青年就会一涌而上去抢包"],
        yuewen_merged="数以百计嘅青年就会一涌而上去抢包",
    ),
    MergeTestCase(
        zhongwen="抢得位置愈高的包，就是愈大的祝福",
        yuewen_to_merge=["抢到位置越高嘅包", "就代表越大嘅祝福"],
        yuewen_merged="抢到位置越高嘅包，就代表越大嘅祝福",
    ),
    MergeTestCase(
        zhongwen="更可以表现自己的不凡身手",
        yuewen_to_merge=["更加可以表现自己不凡嘅身手"],
        yuewen_merged="更加可以表现自己不凡嘅身手",
    ),
    MergeTestCase(
        zhongwen="在1978年两座包山忽然倒下，多人重伤",
        yuewen_to_merge=["但喺1978年", "两座包山突然塌咗"],
        yuewen_merged="但喺1978年，两座包山突然塌咗",
    ),
    MergeTestCase(
        zhongwen="「抢包山」从此被禁！",
        yuewen_to_merge=["都去抢包山", "而长洲特有嘅传统亦占备为榜"],
        yuewen_merged="都去抢包山，而长洲特有嘅传统亦占备为榜！",
    ),
    MergeTestCase(
        zhongwen="而长洲独有的传统，亦渐被遗忘",
        yuewen_to_merge=["长洲特有嘅传统亦占备为榜"],
        yuewen_merged="长洲特有嘅传统，亦占备为榜",
    ),
]  # merge_test_cases_block_45
merge_test_cases_block_46 = [
    MergeTestCase(
        zhongwen="奥运金牌⋯这一世是没有机会的了",
        yuewen_to_merge=["奥运金牌", "我谂呢一世都唔会攞到"],
        yuewen_merged="奥运金牌⋯我谂呢一世都唔会攞到",
    ),
    MergeTestCase(
        zhongwen="每个星期六我都搭船过长洲",
        yuewen_to_merge=["每个礼拜六", "我都会搭船过长洲"],
        yuewen_merged="每个礼拜六，我都会搭船过长洲",
    ),
    MergeTestCase(
        zhongwen="去学抢包山⋯",
        yuewen_to_merge=["去学抢包山"],
        yuewen_merged="去学抢包山⋯",
    ),
    MergeTestCase(
        zhongwen="一项没有奖牌，没有对手，没有比赛⋯",
        yuewen_to_merge=["一日冇奖牌", "冇对手", "冇比赛"],
        yuewen_merged="一日冇奖牌，冇对手，冇比赛⋯",
    ),
    MergeTestCase(
        zhongwen="甚至没有人知道是运动的运动",
        yuewen_to_merge=["甚至乎冇人知对佢系运动嘅运动"],
        yuewen_merged="甚至乎冇人知对佢系运动嘅运动",
    ),
    MergeTestCase(
        zhongwen="更坏的是，连包山也没有！",
        yuewen_to_merge=["更衰嘅系", "连包山都冇"],
        yuewen_merged="更衰嘅系，连包山都冇！",
    ),
    MergeTestCase(
        zhongwen="师傅只是叫我去他的家⋯",
        yuewen_to_merge=["师傅净系叫我去佢屋企"],
        yuewen_merged="师傅净系叫我去佢屋企⋯",
    ),
    MergeTestCase(
        zhongwen="在组合柜爬来爬去",
        yuewen_to_merge=["喺个组合柜度爬嚟爬去"],
        yuewen_merged="喺个组合柜度爬嚟爬去",
    ),
    MergeTestCase(
        zhongwen="碰！三番！",
        yuewen_to_merge=["通", "三番"],
        yuewen_merged="通！三番！",
    ),
    MergeTestCase(
        zhongwen="别躲懒！继续练！",
        yuewen_to_merge=["冇偷懒", "继续练"],
        yuewen_merged="冇偷懒！继续练！",
    ),
    MergeTestCase(
        zhongwen="一天，珊珊到了师传家！",
        yuewen_to_merge=["有一日", "山伞嚟咗师傅屋企"],
        yuewen_merged="有一日，山伞嚟咗师傅屋企！",
    ),
    MergeTestCase(
        zhongwen="珊珊！我的师姐珊珊！",
        yuewen_to_merge=["山伞", "我个师仔山伞啊"],
        yuewen_merged="山伞！我个师仔山伞啊！",
    ),
    MergeTestCase(
        zhongwen="可以看见珊珊⋯",
        yuewen_to_merge=["可以见到山伞"],
        yuewen_merged="可以见到山伞⋯",
    ),
    MergeTestCase(
        zhongwen="这几个星期爬得再辛苦也是值得的！",
        yuewen_to_merge=["爬得咁辛苦", "都系值得㗎"],
        yuewen_merged="爬得咁辛苦，都系值得㗎！",
    ),
    MergeTestCase(
        zhongwen="珊珊！",
        yuewen_to_merge=["山伞"],
        yuewen_merged="山伞！",
    ),
    MergeTestCase(
        zhongwen="珊你个头！继续练习！",
        yuewen_to_merge=["伞你个头啊", "继续练习"],
        yuewen_merged="伞你个头啊！继续练习！",
    ),
]  # merge_test_cases_block_46
merge_test_cases_block_47 = [
    MergeTestCase(
        zhongwen="还不去？",
        yuewen_to_merge=["仲唔系"],
        yuewen_merged="仲唔系？",
    ),
    MergeTestCase(
        zhongwen="珊珊没看见我这个师弟",
        yuewen_to_merge=["山神佢见唔到我呢个师弟"],
        yuewen_merged="山神佢见唔到我呢个师弟",
    ),
    MergeTestCase(
        zhongwen="我只有死死气再爬上组合柜",
        yuewen_to_merge=["我唯有死死气爬返上个组合柜"],
        yuewen_merged="我唯有死死气爬返上个组合柜",
    ),
    MergeTestCase(
        zhongwen="我咁大个仔，什么「头」也给骂过⋯",
        yuewen_to_merge=["我咁大个仔", "乜嘢头都畀人闹过"],
        yuewen_merged="我咁大个仔，乜嘢头都畀人闹过⋯",
    ),
    MergeTestCase(
        zhongwen="「珊你个头」却特别刺耳",
        yuewen_to_merge=["但系山呢个头唔知点解特别瘾"],
        yuewen_merged="但系「山呢个头」唔知点解特别瘾",
    ),
    MergeTestCase(
        zhongwen="我⋯我⋯",
        yuewen_to_merge=["我", "我"],
        yuewen_merged="我⋯我⋯",
    ),
    MergeTestCase(
        zhongwen="我唔学抢包山了！",
        yuewen_to_merge=["我唔好抢包纱嘞", "字幕由纱友提供"],
        yuewen_merged="我唔好抢包纱嘞！字幕由纱友提供",
    ),
]  # merge_test_cases_block_47
merge_test_cases_block_48 = [
    MergeTestCase(
        zhongwen="其实今天是我第一次近距离见黎根",
        yuewen_to_merge=["其实今日系我第一次咁近距离同丽根见面"],
        yuewen_merged="其实今日系我第一次咁近距离同丽根见面",
    ),
    MergeTestCase(
        zhongwen="他恐怕都有五十岁了",
        yuewen_to_merge=["睇怕佢都有五十岁啦"],
        yuewen_merged="睇怕佢都有五十岁啦",
    ),
    MergeTestCase(
        zhongwen="却还是一副孩子脸",
        yuewen_to_merge=["但系仲有一副孩子脸"],
        yuewen_merged="但系仲有一副孩子脸",
    ),
    MergeTestCase(
        zhongwen="鸡尾包！新鲜出炉！",
        yuewen_to_merge=["鸡尾包", "啱啱出炉嘅"],
        yuewen_merged="鸡尾包！啱啱出炉嘅！",
    ),
]  # merge_test_cases_block_48
merge_test_cases_block_49 = [
    MergeTestCase(
        zhongwen="其实鸡尾包呢⋯",
        yuewen_to_merge=["其实鸡尾爆呢"],
        yuewen_merged="其实鸡尾爆呢⋯",
    ),
    MergeTestCase(
        zhongwen="你说这似不似鸡尾？",
        yuewen_to_merge=["吓", "你话噉样似唔似鸡尾呀", "哈哈哈哈"],
        yuewen_merged="吓，你话噉样似唔似鸡尾呀？哈哈哈哈",
    ),
]  # merge_test_cases_block_49
merge_test_cases_block_50 = [
    MergeTestCase(
        zhongwen="麦兜他学东西⋯还可以",
        yuewen_to_merge=["麦兜嘅学嘢呢都仲可以"],
        yuewen_merged="麦兜嘅学嘢呢⋯都仲可以",
    ),
    MergeTestCase(
        zhongwen="黎根接着说了一大堆话⋯",
        yuewen_to_merge=["跟住黎根讲咗一大堆说话"],
        yuewen_merged="跟住黎根讲咗一大堆说话⋯",
    ),
    MergeTestCase(
        zhongwen="他的抱负，他对麦兜的期望",
        yuewen_to_merge=["讲下佢嘅抱负", "佢对麦兜嘅期望"],
        yuewen_merged="讲下佢嘅抱负，佢对麦兜嘅期望",
    ),
    MergeTestCase(
        zhongwen="他说他会把他所识的毫不保留教给麦兜",
        yuewen_to_merge=["佢话会将佢识嘅嘢毫无保留噉教晒畀麦兜"],
        yuewen_merged="佢话会将佢识嘅嘢毫无保留噉教晒畀麦兜",
    ),
    MergeTestCase(
        zhongwen="黎根越说越兴奋，直到双眼发光",
        yuewen_to_merge=["黎根越讲越兴奋"],
        yuewen_merged="黎根越讲越兴奋",
    ),
    MergeTestCase(
        zhongwen="他又说滑浪风帆并不是他最犀利的项目",
        yuewen_to_merge=["佢话滑浪风帆都唔系佢最犀利𠮶样"],
        yuewen_merged="佢话滑浪风帆都唔系佢最犀利𠮶样",
    ),
    MergeTestCase(
        zhongwen="他最大强项是抢包山",
        yuewen_to_merge=["佢最劲嘅就系抢包山"],
        yuewen_merged="佢最劲嘅就系抢包山",
    ),
    MergeTestCase(
        zhongwen="他说抢包山结合了南拳",
        yuewen_to_merge=["佢话抢包山结合咗南拳"],
        yuewen_merged="佢话抢包山结合咗南拳",
    ),
    MergeTestCase(
        zhongwen="神功戏和现代器械操",
        yuewen_to_merge=["神功气", "现代气蟹粗"],
        yuewen_merged="神功气现代气蟹粗",
    ),
    MergeTestCase(
        zhongwen="他说抢包山才是他一生最大成就",
        yuewen_to_merge=["佢话抢包山先至系佢呢世人最大嘅成就"],
        yuewen_merged="佢话抢包山先至系佢呢世人最大嘅成就",
    ),
    MergeTestCase(
        zhongwen="缩脚，唔该！",
        yuewen_to_merge=["缩𠮶只脚唔该"],
        yuewen_merged="缩𠮶只脚，唔该！",
    ),
    MergeTestCase(
        zhongwen="你看！",
        yuewen_to_merge=["你睇下"],
        yuewen_merged="你睇下！",
    ),
    MergeTestCase(
        zhongwen="这脚瓜⋯好粗好大！比一节瓜还要大！",
        yuewen_to_merge=["哗", "呢节", "呢节脚瓜好粗好大呀", "仲大过节瓜"],
        yuewen_merged="哗，呢节，呢节脚瓜好粗好大呀！仲大过节瓜！",
    ),
    MergeTestCase(
        zhongwen="脚瓜的肌肉非常结实⋯",
        yuewen_to_merge=["脚瓜嘅肌肉非常结实"],
        yuewen_merged="脚瓜嘅肌肉非常结实⋯",
    ),
    MergeTestCase(
        zhongwen="青筋凸现，钢线似的",
        yuewen_to_merge=["啲青筋凸晒出嚟", "好似钢线噉"],
        yuewen_merged="啲青筋凸晒出嚟，好似钢线噉",
    ),
    MergeTestCase(
        zhongwen="每一条脚毛都硬似铁钉",
        yuewen_to_merge=["啲脚毛每一条都好似铁钉咁硬"],
        yuewen_merged="啲脚毛每一条都好似铁钉咁硬",
    ),
    MergeTestCase(
        zhongwen="脚趾甲有一寸厚，究竟⋯",
        yuewen_to_merge=["脚趾弓啲脚夹成串咁厚", "究竟"],
        yuewen_merged="脚趾弓啲脚夹成串咁厚，究竟⋯",
    ),
    MergeTestCase(
        zhongwen="要走过几多座山",
        yuewen_to_merge=["要行个几度呢?", "几多座山"],
        yuewen_merged="要行个几度呢?几多座山",
    ),
    MergeTestCase(
        zhongwen="跨过几多个海",
        yuewen_to_merge=["挂过几多个海"],
        yuewen_merged="挂过几多个海",
    ),
    MergeTestCase(
        zhongwen="吃过几多苦头",
        yuewen_to_merge=["挨过几多斧头"],
        yuewen_merged="挨过几多斧头",
    ),
    MergeTestCase(
        zhongwen="才可以练成这举世无双的脚瓜？",
        yuewen_to_merge=["先至可以练成呢一只举细无伤嘅脚瓜"],
        yuewen_merged="先至可以练成呢一只举细无伤嘅脚瓜？",
    ),
]  # merge_test_cases_block_50
merge_test_cases_block_51 = [
    MergeTestCase(
        zhongwen="我个仔⋯",
        yuewen_to_merge=["我个仔"],
        yuewen_merged="我个仔⋯",
    ),
    MergeTestCase(
        zhongwen="你个仔，他日都会有这只大脚瓜",
        yuewen_to_merge=["你个仔", "第时都会有我咁大只脚瓜"],
        yuewen_merged="你个仔，第时都会有我咁大只脚瓜",
    ),
    MergeTestCase(
        zhongwen="其实我也不知道个仔要这么粗的脚瓜⋯",
        yuewen_to_merge=["其实", "我都唔知我仔要咁粗嘅脚瓜"],
        yuewen_merged="其实，我都唔知我仔要咁粗嘅脚瓜⋯",
    ),
    MergeTestCase(
        zhongwen="有什么用",
        yuewen_to_merge=["有咩用"],
        yuewen_merged="有咩用",
    ),
    MergeTestCase(
        zhongwen="可是看见那些凸现的青筋，不知怎样⋯",
        yuewen_to_merge=["但系见到佢一条条凸起嘅青筋", "唔知点解"],
        yuewen_merged="但系见到佢一条条凸起嘅青筋，唔知点解⋯",
    ),
    MergeTestCase(
        zhongwen="我想起麦兜的爸爸，阿炳",
        yuewen_to_merge=["我", "我谂起麦兜嘅爸爸", "阿炳"],
        yuewen_merged="我，我谂起麦兜嘅爸爸，阿炳",
    ),
]  # merge_test_cases_block_51
merge_test_cases_block_52 = [
    MergeTestCase(
        zhongwen="我找来找去也找不到那部电子英文辞典",
        yuewen_to_merge=["我揾完成间屋", "都揾唔到部电子英文词典"],
        yuewen_merged="我揾完成间屋都揾唔到部电子英文词典",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="跑哪去了？",
        yuewen_to_merge=["去咗边呢"],
        yuewen_merged="去咗边呢？",
    ),
    MergeTestCase(
        zhongwen="难道⋯不会吧？",
        yuewen_to_merge=["唔通", "冇理由㗎"],
        yuewen_merged="唔通⋯冇理由㗎？",
    ),
]  # merge_test_cases_block_52
merge_test_cases_block_53 = [
    MergeTestCase(
        zhongwen="想不到真的让妈妈拿去了。吓得我！",
        yuewen_to_merge=["咦", "估唔到真系妈妈攞咗㖞", "吓得我啊"],
        yuewen_merged="咦，估唔到真系妈妈攞咗㖞。吓得我啊！",
    ),
    MergeTestCase(
        zhongwen="妈妈怎么会写起英文信？",
        yuewen_to_merge=["点解妈妈会用英文写信嘅"],
        yuewen_merged="点解妈妈会用英文写信嘅？",
    ),
    MergeTestCase(
        zhongwen="信很短",
        yuewen_to_merge=["封信好短"],
        yuewen_merged="封信好短",
    ),
    MergeTestCase(
        zhongwen="我猜是妈妈用电子辞典逐个字译成英文",
        yuewen_to_merge=["我谂妈妈佢系好辛苦用电子词典", "逐个逐个字译做英文"],
        yuewen_merged="我谂妈妈佢系好辛苦用电子词典逐个逐个字译做英文",
    ),
    MergeTestCase(
        zhongwen="于是我又用电子辞典把信译回中文",
        yuewen_to_merge=["于是我让返电子词典", "将封信译返做中文"],
        yuewen_merged="于是我让返电子词典，将封信译返做中文",
    ),
    MergeTestCase(
        zhongwen="信，是妈妈写给奥委会主席的",
        yuewen_to_merge=["封信原来系妈妈写畀奥委会主席㗎"],
        yuewen_merged="封信原来系妈妈写畀奥委会主席㗎",
    ),
    MergeTestCase(
        zhongwen="「亲爱的主席：」",
        yuewen_to_merge=["亲爱的主席"],
        yuewen_merged="「亲爱的主席：」",
    ),
    MergeTestCase(
        zhongwen="「你好吗？我很好！」",
        yuewen_to_merge=["你好吗", "我很好"],
        yuewen_merged="「你好吗？我很好！」",
    ),
    MergeTestCase(
        zhongwen="「你吃包吗？我吃包！」",
        yuewen_to_merge=["你吃包吗", "我吃包"],
        yuewen_merged="你吃包吗？我吃包！",
    ),
    MergeTestCase(
        zhongwen="「我们居住在香港这里的人，很爱吃包」",
        yuewen_to_merge=["我门居住在香港这类的人", "肯爱吃包"],
        yuewen_merged="我门居住在香港这类的人，肯爱吃包",
    ),
    MergeTestCase(
        zhongwen="「小笼包，上海包，广东包，莲蓉包」",
        yuewen_to_merge=["小笼包", "上海包", "广东包", "联融包"],
        yuewen_merged="「小笼包，上海包，广东包，联融包」",
    ),
    MergeTestCase(
        zhongwen="「好朋友，我认为",
        yuewen_to_merge=["好朋友", "我认为"],
        yuewen_merged="「好朋友，我认为",
    ),
    MergeTestCase(
        zhongwen="抢劫那些包，十分重要」",
        yuewen_to_merge=["抢劫𠮶些包十分重要"],
        yuewen_merged="抢劫𠮶些包，十分重要」",
    ),
    MergeTestCase(
        zhongwen="「也算是运动，就真！」",
        yuewen_to_merge=["也算是运动就真"],
        yuewen_merged="也算是运动，就真！",
    ),
    MergeTestCase(
        zhongwen="「要大力！大吃晚上的粥，和大节瓜！」",
        yuewen_to_merge=["要大力", "大吃", "吻上的粥", "和大字瓜"],
        yuewen_merged="「要大力！大吃吻上的粥，和大字瓜！」",
    ),
    MergeTestCase(
        zhongwen="「按照我愚蠢的见解⋯」",
        yuewen_to_merge=["按照我愚蠢的见解"],
        yuewen_merged="「按照我愚蠢的见解⋯」",
    ),
    MergeTestCase(
        zhongwen="「抢劫那些包，是奥运会比赛」",
        yuewen_to_merge=["抢劫𠮶些包", "系奥运会比赛"],
        yuewen_merged="抢劫𠮶些包，系奥运会比赛",
    ),
    MergeTestCase(
        zhongwen="「让全世界的体育家，抢过！」",
        yuewen_to_merge=["让全世界嘅体育家抢过"],
        yuewen_merged="「让全世界嘅体育家，抢过！」",
    ),
    MergeTestCase(
        zhongwen="「世界便和平！」",
        yuewen_to_merge=["世界变和平"],
        yuewen_merged="「世界变和平！」",
    ),
    MergeTestCase(
        zhongwen="「你有孩子吗？」",
        yuewen_to_merge=["你有孩子吗"],
        yuewen_merged="「你有孩子吗？」",
    ),
    MergeTestCase(
        zhongwen="「我有一个孩子，麦兜」",
        yuewen_to_merge=["我有一个孩子", "麦兜"],
        yuewen_merged="「我有一个孩子，麦兜」",
    ),
    MergeTestCase(
        zhongwen="终于讲到我了！",
        yuewen_to_merge=["终于讲到我啦"],
        yuewen_merged="终于讲到我啦！",
    ),
    MergeTestCase(
        zhongwen="「他是一个好男孩」",
        yuewen_to_merge=["她系一个好男孩"],
        yuewen_merged="「她系一个好男孩」",
    ),
    MergeTestCase(
        zhongwen="「他非常懂得抢劫那些包」",
        yuewen_to_merge=["她非常懂得抢劫𠮶些包"],
        yuewen_merged="她非常懂得抢劫𠮶些包",
    ),
    MergeTestCase(
        zhongwen="「有一天，我看见他，抢劫包⋯」",
        yuewen_to_merge=["有一天我看见她抢劫包"],
        yuewen_merged="有一天我看见她，抢劫包⋯",
    ),
    MergeTestCase(
        zhongwen="「抢了一个奥运金牌」",
        yuewen_to_merge=["抢了一个奥运金牌"],
        yuewen_merged="抢了一个奥运金牌",
    ),
    MergeTestCase(
        zhongwen="「那便是一个母亲能够有的最大的安慰」",
        yuewen_to_merge=["哪便是一个母亲能够有的最好的", "最大的安慰"],
        yuewen_merged="哪便是一个母亲能够有的最好的，最大的安慰",
    ),
    MergeTestCase(
        zhongwen="「孩子的才干，得到了世界人类的知道」",
        yuewen_to_merge=["孩子的才干得到了世界人类的知道"],
        yuewen_merged="「孩子的才干得到了世界人类的知道」",
    ),
    MergeTestCase(
        zhongwen="「父母愿意做什么的东西都得」",
        yuewen_to_merge=["父母愿意做什么的东西都得"],
        yuewen_merged="「父母愿意做什么的东西都得」",
    ),
    MergeTestCase(
        zhongwen="「于是我写了这忽然间的信给你」",
        yuewen_to_merge=["于是我写了这忽然间的信给你"],
        yuewen_merged="于是我写了这忽然间的信给你",
    ),
    MergeTestCase(
        zhongwen="「虽然你不知道我是什么微细的东西」",
        yuewen_to_merge=["虽然你不知道我是什么微细的东西"],
        yuewen_merged="虽然你不知道我是什么微细的东西",
    ),
    MergeTestCase(
        zhongwen="「但我的孩子很大，很大！」",
        yuewen_to_merge=["但我的孩子很大很大"],
        yuewen_merged="但我的孩子很大，很大！",
    ),
    MergeTestCase(
        zhongwen="「有一天，你都会知道」",
        yuewen_to_merge=["有一天你都会知道"],
        yuewen_merged="「有一天你都会知道」",
    ),
    MergeTestCase(
        zhongwen="「多谢合作！」",
        yuewen_to_merge=["多谢合作"],
        yuewen_merged="「多谢合作！」",
    ),
    MergeTestCase(
        zhongwen="「你忠实的，麦太」",
        yuewen_to_merge=["你忠实的", "麦太"],
        yuewen_merged="「你忠实的，麦太」",
    ),
]  # merge_test_cases_block_53
merge_test_cases_block_54 = [
    MergeTestCase(
        zhongwen="看完妈妈的信",
        yuewen_to_merge=["睇完妈妈封信后"],
        yuewen_merged="睇完妈妈封信后",
    ),
    MergeTestCase(
        zhongwen="我决定回长洲继续学捡包山",
        yuewen_to_merge=["我决定返长洲继续抢包生"],
        yuewen_merged="我决定返长洲继续抢包生",
    ),
    MergeTestCase(
        zhongwen="我不是为了见珊珊",
        yuewen_to_merge=["我唔系为咗见到山神"],
        yuewen_merged="我唔系为咗见到山神",
    ),
    MergeTestCase(
        zhongwen="我并不知道为什么要抢那些包",
        yuewen_to_merge=["我唔知点解要抢𠮶啲包"],
        yuewen_merged="我唔知点解要抢𠮶啲包",
    ),
    MergeTestCase(
        zhongwen="我也不相信抢包山会成为奥运项目",
        yuewen_to_merge=["我亦唔信抢包生会成为奥运项目"],
        yuewen_merged="我亦唔信抢包生会成为奥运项目",
    ),
    MergeTestCase(
        zhongwen="可是，我依然努力练习抢包山",
        yuewen_to_merge=["但系", "我依然努力练习抢包生"],
        yuewen_merged="但系，我依然努力练习抢包生",
    ),
    MergeTestCase(
        zhongwen="因为，我爱我妈妈",
        yuewen_to_merge=["因为我爱我妈妈"],
        yuewen_merged="因为，我爱我妈妈",
    ),
    MergeTestCase(
        zhongwen="师傅说我攀爬功夫已经不错",
        yuewen_to_merge=["师傅话", "我嘅攀爬功夫已经唔错"],
        yuewen_merged="师傅话，我嘅攀爬功夫已经唔错",
    ),
    MergeTestCase(
        zhongwen="可以开始教我「十二路抢包手」",
        yuewen_to_merge=["可以开始教我十二路抢包手"],
        yuewen_merged="可以开始教我「十二路抢包手」",
    ),
    MergeTestCase(
        zhongwen="师傅说当年师祖要出这套",
        yuewen_to_merge=["师傅话", "当年师祖使出呢套"],
        yuewen_merged="师傅话，当年师祖使出呢套",
    ),
    MergeTestCase(
        zhongwen="「十二路抢包手」⋯",
        yuewen_to_merge=["十二路抢包手"],
        yuewen_merged="十二路抢包手⋯",
    ),
    MergeTestCase(
        zhongwen="连林世荣也大大赞好",
        yuewen_to_merge=["连林世荣睇见都大赞老爷"],
        yuewen_merged="连林世荣睇见都大赞老爷",
    ),
    MergeTestCase(
        zhongwen="后来麦嘎告诉我⋯",
        yuewen_to_merge=["后来", "默默话我知"],
        yuewen_merged="后来，默默话我知⋯",
    ),
    MergeTestCase(
        zhongwen="林世荣即是猪肉荣，是黄飞鸿的徒弟",
        yuewen_to_merge=["林世荣即系猪肉荣", "系黄飞鸿嘅徒弟"],
        yuewen_merged="林世荣即系猪肉荣，系黄飞鸿嘅徒弟",
    ),
    MergeTestCase(
        zhongwen="我不知道师傅像不像黄飞鸿",
        yuewen_to_merge=["我唔知到师傅似唔似黄飞鸿"],
        yuewen_merged="我唔知到师傅似唔似黄飞鸿",
    ),
    MergeTestCase(
        zhongwen="我却肯定像一块猪肉",
        yuewen_to_merge=["但系我就肯定似旧猪肉"],
        yuewen_merged="但系我就肯定似旧猪肉",
    ),
    MergeTestCase(
        zhongwen="我是一块堵住两个包",
        yuewen_to_merge=["我就系一个揸住两个包"],
        yuewen_merged="我就系一个揸住两个包",
    ),
    MergeTestCase(
        zhongwen="在长洲转来转去的猪肉",
        yuewen_to_merge=["喺长洲转嚟转去嘅猪肉"],
        yuewen_merged="喺长洲转嚟转去嘅猪肉",
    ),
    MergeTestCase(
        zhongwen="我一边练习，一边胡思乱想；始终⋯",
        yuewen_to_merge=["我一边练习", "一边乱练", "一边谂嘢", "始终"],
        yuewen_merged="我一边练习，一边乱练，一边谂嘢；始终⋯",
    ),
    MergeTestCase(
        zhongwen="我还是不大喜欢抢包",
        yuewen_to_merge=["我都唔系咁钟意抢包"],
        yuewen_merged="我都唔系咁钟意抢包",
    ),
    MergeTestCase(
        zhongwen="我只是爱我妈妈",
        yuewen_to_merge=["我净系爱我妈妈"],
        yuewen_merged="我净系爱我妈妈",
    ),
    MergeTestCase(
        zhongwen="于是我咬实牙根⋯",
        yuewen_to_merge=["于是我咬细牙根"],
        yuewen_merged="于是我咬细牙根⋯",
    ),
    MergeTestCase(
        zhongwen="一步一步，一爪一爪⋯",
        yuewen_to_merge=["一步一步", "一爪一爪"],
        yuewen_merged="一步一步，一爪一爪⋯",
    ),
    MergeTestCase(
        zhongwen="我最后终于练成「十二路抢包手」",
        yuewen_to_merge=["最后", "我终于练成十二路抢包手啦"],
        yuewen_merged="最后，我终于练成十二路抢包手啦",
    ),
]  # merge_test_cases_block_54
merge_test_cases_block_55 = [
    MergeTestCase(
        zhongwen="喂，我是麦兜",
        yuewen_to_merge=["喂", "我系麦兜啊"],
        yuewen_merged="喂，我系麦兜啊",
    ),
    MergeTestCase(
        zhongwen="刚才的是小朋友麦兜，我是大个佬麦兜",
        yuewen_to_merge=["正话𠮶个系细路仔麦兜", "我系大个佬麦兜"],
        yuewen_merged="正话𠮶个系细路仔麦兜，我系大个佬麦兜",
    ),
    MergeTestCase(
        zhongwen="小朋友麦兜和大个佬麦兜除了声音不同⋯",
        yuewen_to_merge=["细路仔麦兜同大个佬麦兜除咗把声唔同之外"],
        yuewen_merged="细路仔麦兜同大个佬麦兜除咗把声唔同之外⋯",
    ),
    MergeTestCase(
        zhongwen="小朋友麦兜的世界仍然有好多幻想",
        yuewen_to_merge=["细路仔麦兜嘅世界仲有好多幻想"],
        yuewen_merged="细路仔麦兜嘅世界仲有好多幻想",
    ),
    MergeTestCase(
        zhongwen="仍然有好多希望",
        yuewen_to_merge=["仲有好多希望"],
        yuewen_merged="仲有好多希望",
    ),
    MergeTestCase(
        zhongwen="希望⋯失望⋯",
        yuewen_to_merge=["希望", "失望"],
        yuewen_merged="希望⋯失望⋯",
    ),
    MergeTestCase(
        zhongwen="希望⋯",
        yuewen_to_merge=["希望"],
        yuewen_merged="希望⋯",
    ),
    MergeTestCase(
        zhongwen="失望",
        yuewen_to_merge=["失望"],
        yuewen_merged="失望",
    ),
    MergeTestCase(
        zhongwen="久而久之，就变成大个佬麦兜",
        yuewen_to_merge=["搞咗一轮", "就变咗大个佬麦兜"],
        yuewen_merged="搞咗一轮，就变咗大个佬麦兜",
    ),
    MergeTestCase(
        zhongwen="我现在还是多说点小朋友麦兜",
        yuewen_to_merge=["不过", "而家我都系想讲返细路仔麦兜"],
        yuewen_merged="不过，而家我都系想讲返细路仔麦兜",
    ),
    MergeTestCase(
        zhongwen="小朋友麦兜仍然希望希望⋯",
        yuewen_to_merge=["细路仔麦兜仲系希望希望"],
        yuewen_merged="细路仔麦兜仲系希望希望⋯",
    ),
    MergeTestCase(
        zhongwen="希望真的有圣诞老人",
        yuewen_to_merge=["希望真系有圣诞老人"],
        yuewen_merged="希望真系有圣诞老人",
    ),
    MergeTestCase(
        zhongwen="而且好想试试圣诞火鸡的滋味",
        yuewen_to_merge=["仲系好想好想试下圣诞火鸡嘅滋味"],
        yuewen_merged="仲系好想好想试下圣诞火鸡嘅滋味",
    ),
    MergeTestCase(
        zhongwen="对，那时我还没吃过火鸡",
        yuewen_to_merge=["系啊", "我𠮶阵", "我真系仲未食过火鸡"],
        yuewen_merged="系啊，我𠮶阵我真系仲未食过火鸡",
    ),
    MergeTestCase(
        zhongwen="关于火鸡的一切⋯",
        yuewen_to_merge=["所有关于火鸡嘅嘢"],
        yuewen_merged="所有关于火鸡嘅嘢⋯",
    ),
    MergeTestCase(
        zhongwen="圣诞树上一闪一闪的饰物",
        yuewen_to_merge=["圣诞树一闪一闪嘅灯饰"],
        yuewen_merged="圣诞树一闪一闪嘅灯饰",
    ),
    MergeTestCase(
        zhongwen="就像天上掉落的星星",
        yuewen_to_merge=["就好似喺天上面落嚟嘅星星噉"],
        yuewen_merged="就好似喺天上面落嚟嘅星星噉",
    ),
    MergeTestCase(
        zhongwen="落到火炉旁边",
        yuewen_to_merge=["落喺火炉旁边"],
        yuewen_merged="落喺火炉旁边",
    ),
    MergeTestCase(
        zhongwen="一片片比外边的雪还要白的鸡胸肉⋯",
        yuewen_to_merge=["一片一片", "比窗外面嘅雪仲要白嘅鸡胸肉"],
        yuewen_merged="一片一片，比窗外面嘅雪仲要白嘅鸡胸肉⋯",
    ),
    MergeTestCase(
        zhongwen="就在我们跟前",
        yuewen_to_merge=["就喺我哋面前啦"],
        yuewen_merged="就喺我哋面前啦",
    ),
    MergeTestCase(
        zhongwen="香气直入灵魂⋯",
        yuewen_to_merge=["香气直入灵魂"],
        yuewen_merged="香气直入灵魂⋯",
    ),
    MergeTestCase(
        zhongwen="连守在灵魂旁边的天使都醒过来",
        yuewen_to_merge=["就连守喺灵魂旁边嘅天使都醒咗起嚟"],
        yuewen_merged="就连守喺灵魂旁边嘅天使都醒咗起嚟",
    ),
    MergeTestCase(
        zhongwen="围住这香而圣洁的肉⋯",
        yuewen_to_merge=["围住呢一嚿好香好香又好盛洁嘅肉"],
        yuewen_merged="围住呢一嚿好香好香又好盛洁嘅肉⋯",
    ),
    MergeTestCase(
        zhongwen="在圣诞夜中飞呀，飞⋯",
        yuewen_to_merge=["喺圣诞夜里面", "飞呀", "飞呀"],
        yuewen_merged="喺圣诞夜里面飞呀，飞呀⋯",
    ),
    MergeTestCase(
        zhongwen="这关于火鸡的一切，不过是我的想像",
        yuewen_to_merge=["但系呢一切一切关于火鸡嘅嘢", "都不过系我嘅想像"],
        yuewen_merged="但系呢一切一切关于火鸡嘅嘢，都不过系我嘅想像",
    ),
    MergeTestCase(
        zhongwen="我从来没吃过火鸡⋯",
        yuewen_to_merge=["因为我从来都未食过火鸡"],
        yuewen_merged="因为我从来都未食过火鸡⋯",
    ),
    MergeTestCase(
        zhongwen="连它的气味也没嗅过",
        yuewen_to_merge=["就连𠮶阵味都未闻过"],
        yuewen_merged="就连𠮶阵味都未闻过",
    ),
    MergeTestCase(
        zhongwen="妈妈说火鸡太大",
        yuewen_to_merge=["妈妈话火鸡太大"],
        yuewen_merged="妈妈话火鸡太大",
    ),
    MergeTestCase(
        zhongwen="我们一家两口，吃不下",
        yuewen_to_merge=["我哋一家两口点食都食唔晒"],
        yuewen_merged="我哋一家两口，点食都食唔晒",
    ),
    MergeTestCase(
        zhongwen="有年圣诞节妈妈买了半只烤鸭庆祝",
        yuewen_to_merge=["有一年圣诞节", "妈妈买咗半边烧鸭庆祝"],
        yuewen_merged="有一年圣诞节，妈妈买咗半边烧鸭庆祝",
    ),
    MergeTestCase(
        zhongwen="当时的我，十分十分失望",
        yuewen_to_merge=["当时我真系十分十分之失望"],
        yuewen_merged="当时我，真系十分十分之失望",
    ),
    MergeTestCase(
        zhongwen="又有一年，一间百货公司结业",
        yuewen_to_merge=["又有一年", "有间大薄货公司倒闭"],
        yuewen_merged="又有一年，有间大薄货公司倒闭",
    ),
    MergeTestCase(
        zhongwen="妈妈以四折买了个小小焗炉",
        yuewen_to_merge=["妈妈用四折买咗个焗炉仔返屋企"],
        yuewen_merged="妈妈用四折买咗个焗炉仔返屋企",
    ),
    MergeTestCase(
        zhongwen="可能因为买了焗炉而技痒",
        yuewen_to_merge=["可能系因为买咗焗炉嘅样"],
        yuewen_merged="可能系因为买咗焗炉嘅样",
    ),
    MergeTestCase(
        zhongwen="那日妈妈竟然跟我说⋯",
        yuewen_to_merge=["𠮶日妈妈竟然同我讲", "佢话"],
        yuewen_merged="𠮶日妈妈竟然同我讲⋯佢话",
    ),
    MergeTestCase(
        zhongwen="让我们明天去超级市场揪火鸡",
        yuewen_to_merge=["明日我哋要超级市场抽火鸡"],
        yuewen_merged="明日我哋要超级市场抽火鸡",
    ),
    MergeTestCase(
        zhongwen="我跟妈妈把火鸡揪回家的路上⋯",
        yuewen_to_merge=["我同妈妈抽住只火鸡行返屋企𠮶阵"],
        yuewen_merged="我同妈妈抽住只火鸡行返屋企𠮶阵⋯",
    ),
    MergeTestCase(
        zhongwen="是我生命中最开心的时刻",
        yuewen_to_merge=["喺𠮶阵时我谂系我生命里面最开心嘅一刻"],
        yuewen_merged="喺𠮶阵时我谂系我生命里面最开心嘅一刻",
    ),
    MergeTestCase(
        zhongwen="火鸡终于解冻了",
        yuewen_to_merge=["火鸡终于解冻啦"],
        yuewen_merged="火鸡终于解冻啦",
    ),
    MergeTestCase(
        zhongwen="我学着妈妈，把双手涂满盐⋯",
        yuewen_to_merge=["我同妈妈噉双手查满盐"],
        yuewen_merged="我同妈妈噉双手查满盐⋯",
    ),
    MergeTestCase(
        zhongwen="在火鸡丰厚的鸡胸上擦呀，擦",
        yuewen_to_merge=["喺火鸡封口嘅鸡胸度", "起细噉啫啫"],
        yuewen_merged="喺火鸡封口嘅鸡胸度，起细噉啫啫",
    ),
    MergeTestCase(
        zhongwen="妈妈不留神漏出了火鸡内的洋葱粒",
        yuewen_to_merge=[
            "联火鸡时",
            "妈妈一个唔觉意",
            "畀酿喺火鸡里面嘅火鸡内脏洋葱粒",
            "红萝虾粒",
        ],
        yuewen_merged="联火鸡时，妈妈一个唔觉意畀酿喺火鸡里面嘅火鸡内脏洋葱粒红萝虾粒",
    ),
    MergeTestCase(
        zhongwen="红萝卜粒",
        yuewen_to_merge=["流嘅出嚟"],
        yuewen_merged="流嘅出嚟",
    ),
    MergeTestCase(
        zhongwen="我说：火鸡「疴烂煮」！",
        yuewen_to_merge=["我话", "火鸡我能住呀", "火鸡"],
        yuewen_merged="我话：火鸡我能住呀！火鸡",
    ),
    MergeTestCase(
        zhongwen="好勉强把火鸡塞进焗炉内",
        yuewen_to_merge=["好勉强噏咗入焗炉度"],
        yuewen_merged="好勉强噏咗入焗炉度",
    ),
    MergeTestCase(
        zhongwen="12月24日",
        yuewen_to_merge=["10月24日"],
        yuewen_merged="10月24日",
    ),
    MergeTestCase(
        zhongwen="上升的白烟跟奇异的焦味拨动星星",
        yuewen_to_merge=["上升嘅白烟同奇异嘅㶶味拨动声声"],
        yuewen_merged="上升嘅白烟同奇异嘅㶶味拨动声声",
    ),
    MergeTestCase(
        zhongwen="焗炉戚戚恻恻，戚戚恻恻⋯",
        yuewen_to_merge=["个焗炉叱叱叱叱", "叱叱叱咁"],
        yuewen_merged="个焗炉叱叱叱叱，叱叱叱咁⋯",
    ),
    MergeTestCase(
        zhongwen="有如天使预早送来的福音",
        yuewen_to_merge=["就好似天赐预祖畀我哋嘅福音"],
        yuewen_merged="就好似天赐预祖畀我哋嘅福音",
    ),
]  # merge_test_cases_block_55
merge_test_cases_block_56 = [
    MergeTestCase(
        zhongwen="好靓的晚上啊！",
        yuewen_to_merge=["好靓嘅夜晚呀"],
        yuewen_merged="好靓嘅夜晚呀！",
    ),
    MergeTestCase(
        zhongwen="我和妈妈坐在尖东海傍",
        yuewen_to_merge=["我同妈妈坐喺尖东海旁"],
        yuewen_merged="我同妈妈坐喺尖东海旁",
    ),
    MergeTestCase(
        zhongwen="点点灯光在海面走来走去⋯",
        yuewen_to_merge=["点点点点嘅灯光喺海上面走来走去"],
        yuewen_merged="点点点点嘅灯光喺海上面走来走去⋯",
    ),
    MergeTestCase(
        zhongwen="美丽又温柔",
        yuewen_to_merge=["又靓", "又温柔"],
        yuewen_merged="又靓又温柔",
    ),
    MergeTestCase(
        zhongwen="真的好靓！",
        yuewen_to_merge=["真系好靓"],
        yuewen_merged="真系好靓！",
    ),
]  # merge_test_cases_block_56
merge_test_cases_block_57 = [
    MergeTestCase(
        zhongwen="我从没吃过这么浓味的东西",
        yuewen_to_merge=["我从未食过咁浓味嘅嘢"],
        yuewen_merged="我从未食过咁浓味嘅嘢",
    ),
    MergeTestCase(
        zhongwen="甚至杯面，烧鸭的味道也没有这么浓",
        yuewen_to_merge=["连烧鸭连杯面都冇咁浓嘅味道"],
        yuewen_merged="连烧鸭连杯面都冇咁浓嘅味道",
    ),
    MergeTestCase(
        zhongwen="火鸡的味道把我每一个味蕾缠住⋯",
        yuewen_to_merge=["火鸡嘅味道喺我嘅每一个味蕾度缠住"],
        yuewen_merged="火鸡嘅味道喺我嘅每一个味蕾度缠住⋯",
    ),
    MergeTestCase(
        zhongwen="爆发⋯缠住⋯爆发⋯",
        yuewen_to_merge=["爆发", "缠住", "爆发"],
        yuewen_merged="爆发⋯缠住⋯爆发⋯",
    ),
    MergeTestCase(
        zhongwen="就像今晚的一切",
        yuewen_to_merge=["就好似今晚嘅嘢噉"],
        yuewen_merged="就好似今晚嘅嘢噉",
    ),
    MergeTestCase(
        zhongwen="最靓最靓，最犀利，而且最温柔",
        yuewen_to_merge=["最靓", "最靓", "最犀利", "亦都系最温柔"],
        yuewen_merged="最靓，最靓，最犀利，亦都系最温柔",
    ),
]  # merge_test_cases_block_57
merge_test_cases_block_58 = [
    MergeTestCase(
        zhongwen="第二天我睡得很晏⋯",
        yuewen_to_merge=["第二日我瞓到好硬"],
        yuewen_merged="第二日我瞓到好硬⋯",
    ),
    MergeTestCase(
        zhongwen="刷过牙我还感觉到火鸡的美味",
        yuewen_to_merge=["测完牙", "我仲感觉到火鸡嘅美味"],
        yuewen_merged="测完牙，我仲感觉到火鸡嘅美味",
    ),
    MergeTestCase(
        zhongwen="因为早餐吃得晚⋯",
        yuewen_to_merge=["因为早餐食得硬"],
        yuewen_merged="因为早餐食得硬⋯",
    ),
    MergeTestCase(
        zhongwen="午餐时妈妈只煮了罐栗米汤",
        yuewen_to_merge=["唔餐妈妈净系整咗罐粟米汤畀我"],
        yuewen_merged="唔餐妈妈净系整咗罐粟米汤畀我",
    ),
    MergeTestCase(
        zhongwen="我用汤匙撩了两下",
        yuewen_to_merge=["我系噉用匙羹撩下撩下"],
        yuewen_merged="我系噉用匙羹撩下撩下",
    ),
    MergeTestCase(
        zhongwen="竟然发现美味的火鸡粒",
        yuewen_to_merge=["我竟然撩到一粒美味嘅火鸡肉"],
        yuewen_merged="我竟然撩到一粒美味嘅火鸡肉",
    ),
    MergeTestCase(
        zhongwen="不用说，那夜就是我渴望了⋯",
        yuewen_to_merge=["𠮶晚唔使讲"],
        yuewen_merged="𠮶晚唔使讲⋯",
    ),
    MergeTestCase(
        zhongwen="很久很久很久的⋯圣诞火鸡大餐！",
        yuewen_to_merge=["当然系食我限咗好耐好耐好耐好耐嘅圣诞火鸡大餐"],
        yuewen_merged="当然系食我限咗好耐好耐好耐好耐嘅⋯圣诞火鸡大餐！",
    ),
    MergeTestCase(
        zhongwen="一片片的火鸡肉和伴碟的薯仔和节瓜⋯",
        yuewen_to_merge=["一片一片嘅火鸡肉", "半碟嘅有薯仔同节瓜"],
        yuewen_merged="一片一片嘅火鸡肉半碟嘅有薯仔同节瓜⋯",
    ),
    MergeTestCase(
        zhongwen="上面淋了老抽生粉献",
        yuewen_to_merge=["上面淋咗一层老抽生粉馅"],
        yuewen_merged="上面淋咗一层老抽生粉馅",
    ),
    MergeTestCase(
        zhongwen="我们真的好兴奋，好满足",
        yuewen_to_merge=["我哋真系好兴奋", "好满足"],
        yuewen_merged="我哋真系好兴奋，好满足",
    ),
    MergeTestCase(
        zhongwen="之后，我们吃了一个星期的⋯",
        yuewen_to_merge=["之后我哋仲食咗一个礼拜嘅", "火鸡三文治"],
        yuewen_merged="之后我哋仲食咗一个礼拜嘅⋯火鸡三文治",
    ),
    MergeTestCase(
        zhongwen="火鸡三文治早餐",
        yuewen_to_merge=["做早餐"],
        yuewen_merged="做早餐",
    ),
    MergeTestCase(
        zhongwen="星期天",
        yuewen_to_merge=["星期日"],
        yuewen_merged="星期日",
    ),
    MergeTestCase(
        zhongwen="我大着胆跟妈妈说：不如去饮茶吖",
        yuewen_to_merge=["我嘅记心肝同妈妈讲", "不如饮茶"],
        yuewen_merged="我嘅记心肝同妈妈讲：不如饮茶",
    ),
    MergeTestCase(
        zhongwen="妈妈骂我「冇衣食」⋯",
        yuewen_to_merge=["妈妈闹我冇意食"],
        yuewen_merged="妈妈闹我「冇意食」⋯",
    ),
    MergeTestCase(
        zhongwen="不过还是带了我去饮茶",
        yuewen_to_merge=["但系都带咗我去饮茶"],
        yuewen_merged="但系都带咗我去饮茶",
    ),
    MergeTestCase(
        zhongwen="之后，妈妈又有计⋯",
        yuewen_to_merge=["之后妈妈又有计"],
        yuewen_merged="之后妈妈又有计⋯",
    ),
    MergeTestCase(
        zhongwen="她把冰箱内剩下来的火鸡肉撕呀撕",
        yuewen_to_merge=["佢将雪柜净返嘅火鸡肉", "系噉撕系噉撕"],
        yuewen_merged="佢将雪柜净返嘅火鸡肉系噉撕系噉撕",
    ),
    MergeTestCase(
        zhongwen="有时候也叫我帮手撕",
        yuewen_to_merge=["有时都叫我帮手撕"],
        yuewen_merged="有时都叫我帮手撕",
    ),
    MergeTestCase(
        zhongwen="火鸡留在指甲的味道",
        yuewen_to_merge=["火鸡留喺指甲𠮶阵味"],
        yuewen_merged="火鸡留喺指甲𠮶阵味",
    ),
    MergeTestCase(
        zhongwen="原来得洗好多次",
        yuewen_to_merge=["原来洗好多次都仲喺度㗎"],
        yuewen_merged="原来洗好多次都仲喺度㗎",
    ),
    MergeTestCase(
        zhongwen="银芽火鸡丝炒米，好味道",
        yuewen_to_merge=["银牙火鸡丝炒米好味道噉"],
        yuewen_merged="银牙火鸡丝炒米，好味道噉",
    ),
    MergeTestCase(
        zhongwen="栗子炆火鸡丝㷛",
        yuewen_to_merge=["焯焯栗子焖火鸡丝煲"],
        yuewen_merged="焯焯栗子焖火鸡丝煲",
    ),
    MergeTestCase(
        zhongwen="花生火鸡骨煲粥",
        yuewen_to_merge=["花生火鸡骨煲粥"],
        yuewen_merged="花生火鸡骨煲粥",
    ),
    MergeTestCase(
        zhongwen="纸包火鸡包包纸",
        yuewen_to_merge=["纸包火鸡包包纸"],
        yuewen_merged="纸包火鸡包包纸",
    ),
    MergeTestCase(
        zhongwen="包火鸡包包包火鸡包",
        yuewen_to_merge=["包火鸡包包包火鸡包"],
        yuewen_merged="包火鸡包包包火鸡包",
    ),
    MergeTestCase(
        zhongwen="酿火鸡馅搽面包",
        yuewen_to_merge=["让火鸡馅茶面包"],
        yuewen_merged="让火鸡馅茶面包",
    ),
    MergeTestCase(
        zhongwen="唉，我好后悔讲过一句「火鸡疴烂煮」",
        yuewen_to_merge=["唉", "我后悔讲过火鸡阿宁处呢句嘢"],
        yuewen_merged="唉，我后悔讲过火鸡阿宁处呢句嘢",
    ),
    MergeTestCase(
        zhongwen="端午节，当我翻开我最喜欢吃的裹蒸粽⋯",
        yuewen_to_merge=["到端午节", "当我督开我最钟意食嘅果精粽嘅时候"],
        yuewen_merged="到端午节，当我督开我最钟意食嘅果精粽嘅时候⋯",
    ),
    MergeTestCase(
        zhongwen="发现咸蛋旁边是一件火鸡背的时候⋯",
        yuewen_to_merge=["发现宿喺咸蛋旁边嘅系一件火鸡背脊"],
        yuewen_merged="发现宿喺咸蛋旁边嘅系一件火鸡背脊⋯",
    ),
    MergeTestCase(
        zhongwen="我脑部一时想唔通，哭起来",
        yuewen_to_merge=["我脑部一时想唔通", "喊咗起上嚟"],
        yuewen_merged="我脑部一时想唔通，喊咗起上嚟",
    ),
    MergeTestCase(
        zhongwen="救命呀！",
        yuewen_to_merge=["救命啊"],
        yuewen_merged="救命啊！",
    ),
    MergeTestCase(
        zhongwen="妈妈悄悄把剩下的火鸡扔掉",
        yuewen_to_merge=["妈妈净计计将净低嘅火鸡劈咗"],
        yuewen_merged="妈妈净计计将净低嘅火鸡劈咗",
    ),
    MergeTestCase(
        zhongwen="那已经是火鸡解冻后差不多半年的事",
        yuewen_to_merge=["原来𠮶阵已经系只火鸡解冻咗差唔多半年后嘅事"],
        yuewen_merged="原来𠮶阵已经系只火鸡解冻咗差唔多半年后嘅事",
    ),
    MergeTestCase(
        zhongwen="我的美梦跟恶梦亦同时完结",
        yuewen_to_merge=["我嘅美梦同噩梦", "都同时完结"],
        yuewen_merged="我嘅美梦同噩梦，都同时完结",
    ),
    MergeTestCase(
        zhongwen="后来我才知道⋯",
        yuewen_to_merge=["后来我先知道"],
        yuewen_merged="后来我先知道⋯",
    ),
    MergeTestCase(
        zhongwen="一只火鸡由出世到给人宰掉",
        yuewen_to_merge=["一只火鸡由出世到畀人㓥"],
        yuewen_merged="一只火鸡由出世到畀人㓥",
    ),
    MergeTestCase(
        zhongwen="也不过是几个月间的事",
        yuewen_to_merge=["都不过系几个月之间嘅事"],
        yuewen_merged="都不过系几个月之间嘅事",
    ),
    MergeTestCase(
        zhongwen="即是说，火鸡死掉后跟我们一起的日子",
        yuewen_to_merge=["即系话", "只火鸡死咗之后", "同我哋一齐嘅日子"],
        yuewen_merged="即系话，只火鸡死咗之后，同我哋一齐嘅日子",
    ),
    MergeTestCase(
        zhongwen="还要长过它的一生",
        yuewen_to_merge=["仲长过佢自己本身条命"],
        yuewen_merged="仲长过佢自己本身条命",
    ),
    MergeTestCase(
        zhongwen="我还发觉，火鸡的味道⋯",
        yuewen_to_merge=["我仲发觉到", "火鸡嘅味道"],
        yuewen_merged="我仲发觉到，火鸡嘅味道⋯",
    ),
    MergeTestCase(
        zhongwen="将吃未吃和第一口之间已经是最高峰",
        yuewen_to_merge=["味食同食第一啖之间", "已经系佢嘅最高峰"],
        yuewen_merged="味食同食第一啖之间已经系佢嘅最高峰",
    ),
    MergeTestCase(
        zhongwen="之后的，不过是开始了也就吃下去",
        yuewen_to_merge=["之后", "不过都系食开就食埋落去噉解"],
        yuewen_merged="之后，不过都系食开就食埋落去噉解",
    ),
    MergeTestCase(
        zhongwen="我没有哲学家的头脑⋯",
        yuewen_to_merge=["我冇知学家嘅头脑"],
        yuewen_merged="我冇知学家嘅头脑⋯",
    ),
    MergeTestCase(
        zhongwen="不知道两件事情应该得出什么道理",
        yuewen_to_merge=["唔知呢两样嘢要得起嘅呢个", "得出啲咩道理"],
        yuewen_merged="唔知呢两样嘢要得起嘅呢个，得出啲咩道理",
    ),
    MergeTestCase(
        zhongwen="可是这些想法⋯",
        yuewen_to_merge=["但系呢啲谂法"],
        yuewen_merged="但系呢啲谂法⋯",
    ),
    MergeTestCase(
        zhongwen="在我长大后⋯",
        yuewen_to_merge=["喺我长大之后"],
        yuewen_merged="喺我长大之后⋯",
    ),
    MergeTestCase(
        zhongwen="在一些跟圣诞节无关的日子⋯",
        yuewen_to_merge=["系一啲同圣诞节无关嘅日子"],
        yuewen_merged="系一啲同圣诞节无关嘅日子⋯",
    ),
    MergeTestCase(
        zhongwen="毫无因由的在我脑中出现过三两次",
        yuewen_to_merge=["无端端噉喺我脑部", "出现过两三次"],
        yuewen_merged="无端端噉喺我脑部出现过两三次",
    ),
    MergeTestCase(
        zhongwen="一次，是在我自己的婚宴上",
        yuewen_to_merge=["一次", "喺我自己嘅婚宴上"],
        yuewen_merged="一次，喺我自己嘅婚宴上",
    ),
    MergeTestCase(
        zhongwen="一次⋯",
        yuewen_to_merge=["一次"],
        yuewen_merged="一次⋯",
    ),
    MergeTestCase(
        zhongwen="是在我妈妈火化那天",
        yuewen_to_merge=["喺我妈妈火化𠮶日"],
        yuewen_merged="喺我妈妈火化𠮶日",
    ),
    MergeTestCase(
        zhongwen="那天，我看着天空几缕灰色的烟",
        yuewen_to_merge=["𠮶日", "我望住天东几条灰色嘅烟"],
        yuewen_merged="𠮶日，我望住天东几条灰色嘅烟",
    ),
    MergeTestCase(
        zhongwen="忽然间嗅到火鸡又浓又淡的气味",
        yuewen_to_merge=["忽然闻到火鸡又浓又淡嘅气味"],
        yuewen_merged="忽然闻到火鸡又浓又淡嘅气味",
    ),
    MergeTestCase(
        zhongwen="我好后悔要妈妈扔掉最后几件火鸡",
        yuewen_to_merge=["我后悔", "要妈妈劈咗个忌廉", "火鸡"],
        yuewen_merged="我后悔，要妈妈劈咗个忌廉，火鸡",
    ),
]  # merge_test_cases_block_58
merge_test_cases_block_59 = [
    MergeTestCase(
        zhongwen="特别报告",
        yuewen_to_merge=["特别报道"],
        yuewen_merged="特别报道",
    ),
    MergeTestCase(
        zhongwen="奥运金牌得主李丽珊决定参加今届奥运",
        yuewen_to_merge=["奥运滑浪风帆金牌得主李丽珊决定参加今届嘅奥运"],
        yuewen_merged="奥运滑浪风帆金牌得主李丽珊决定参加今届嘅奥运",
    ),
    MergeTestCase(
        zhongwen="向全世界人再次证明⋯",
        yuewen_to_merge=["向全世界人再次证明"],
        yuewen_merged="向全世界人再次证明⋯",
    ),
    MergeTestCase(
        zhongwen="香港运动员不是腊鸭",
        yuewen_to_merge=["香港嘅运动员唔系腊鸭"],
        yuewen_merged="香港嘅运动员唔系腊鸭",
    ),
    MergeTestCase(
        zhongwen="另方面⋯",
        yuewen_to_merge=["另一方面"],
        yuewen_merged="另一方面⋯",
    ),
    MergeTestCase(
        zhongwen="香港体运总会霍震霆⋯",
        yuewen_to_merge=["中国香港体育协会企奥委会会长霍振庭"],
        yuewen_merged="中国香港体育协会企奥委会会长霍振庭⋯",
    ),
    MergeTestCase(
        zhongwen="正式向亚运协会提出申请",
        yuewen_to_merge=["正式向亚运协会提出申请"],
        yuewen_merged="正式向亚运协会提出申请",
    ),
    MergeTestCase(
        zhongwen="香港将争夺下届亚运会主办权",
        yuewen_to_merge=["香港将要争夺下届亚运会嘅主办权"],
        yuewen_merged="香港将要争夺下届亚运会嘅主办权",
    ),
    MergeTestCase(
        zhongwen="多个运动团体立即表示热烈支持",
        yuewen_to_merge=["多个运动团体立即表示热烈支持"],
        yuewen_merged="多个运动团体立即表示热烈支持",
    ),
    MergeTestCase(
        zhongwen="其中港九新界竹战联谊会⋯",
        yuewen_to_merge=["其中港狗新界足战联谊会"],
        yuewen_merged="其中港狗新界足战联谊会⋯",
    ),
    MergeTestCase(
        zhongwen="更希望打麻将可以成为亚运项目",
        yuewen_to_merge=["更希望打麻雀可以成为亚运项目"],
        yuewen_merged="更希望打麻雀可以成为亚运项目",
    ),
    MergeTestCase(
        zhongwen="另外，全港茶餐厅员工协会⋯",
        yuewen_to_merge=["另外"],
        yuewen_merged="另外⋯",
    ),
    MergeTestCase(
        zhongwen="经已发动所有会员⋯",
        yuewen_to_merge=["全港茶餐厅联工协会经热发动所有会员"],
        yuewen_merged="全港茶餐厅联工协会经热发动所有会员⋯",
    ),
    MergeTestCase(
        zhongwen="争取「掷蛋挞」成为亚运比赛项目",
        yuewen_to_merge=["争取掟蛋挞成为亚运会比赛项目"],
        yuewen_merged="争取掟蛋挞成为亚运会比赛项目",
    ),
    MergeTestCase(
        zhongwen="港九烧味卤味腊味同业会",
        yuewen_to_merge=["港狗烧尾", "掳尾", "立尾同业会"],
        yuewen_merged="港狗烧尾掳尾立尾同业会",
    ),
    MergeTestCase(
        zhongwen="亦向霍主席当面提出⋯",
        yuewen_to_merge=["亦都向霍主席当面提出"],
        yuewen_merged="亦都向霍主席当面提出⋯",
    ),
    MergeTestCase(
        zhongwen="「挂腊鸭」可以成为亚运比赛项目",
        yuewen_to_merge=["挂立鸭可以成为亚运比赛项目"],
        yuewen_merged="挂立鸭可以成为亚运比赛项目",
    ),
    MergeTestCase(
        zhongwen="较为特别的是，CIC保险营业员联同⋯",
        yuewen_to_merge=["较为特别嘅系", "CIC保险营业员联同"],
        yuewen_merged="较为特别嘅系，CIC保险营业员联同⋯",
    ),
    MergeTestCase(
        zhongwen="大角咀春田花花幼稚园⋯",
        yuewen_to_merge=["大角嘴春田花花", "幼稚园"],
        yuewen_merged="大角嘴春田花花幼稚园⋯",
    ),
    MergeTestCase(
        zhongwen="附属小学一班小朋友⋯",
        yuewen_to_merge=["附属小学嘅一班小朋友"],
        yuewen_merged="附属小学嘅一班小朋友⋯",
    ),
    MergeTestCase(
        zhongwen="争取「抢包山」",
        yuewen_to_merge=["争取抢包山"],
        yuewen_merged="争取「抢包山」",
    ),
    MergeTestCase(
        zhongwen="一项几乎绝迹的运动⋯",
        yuewen_to_merge=["一项几乎绝迹嘅运动"],
        yuewen_merged="一项几乎绝迹嘅运动⋯",
    ),
    MergeTestCase(
        zhongwen="成为本港举办亚运的重点推介比赛项目",
        yuewen_to_merge=["成为本港举办亚运重点推介嘅比赛项目"],
        yuewen_merged="成为本港举办亚运重点推介嘅比赛项目",
    ),
]  # merge_test_cases_block_59
merge_test_cases_block_60 = [
    MergeTestCase(
        zhongwen="最后⋯",
        yuewen_to_merge=["最后", "最后"],
        yuewen_merged="最后，最后⋯",
    ),
    MergeTestCase(
        zhongwen="最后，一切成烟",
        yuewen_to_merge=["全部都系banana"],
        yuewen_merged="全部都系banana",
    ),
    MergeTestCase(
        zhongwen="最后，他们选了「掷蛋挞」做推介项目",
        yuewen_to_merge=["最后佢哋选咗定蛋挞做推介项目"],
        yuewen_merged="最后佢哋选咗定蛋挞做推介项目",
    ),
    MergeTestCase(
        zhongwen="至于香港争取申办亚运的口号⋯",
        yuewen_to_merge=["至于香港争取申办亚运嘅口号"],
        yuewen_merged="至于香港争取申办亚运嘅口号⋯",
    ),
    MergeTestCase(
        zhongwen="亦顺理成章叫成「香港一蛋挞」",
        yuewen_to_merge=["亦都顺理成章噉叫做香港一蛋挞"],
        yuewen_merged="亦都顺理成章噉叫做「香港一蛋挞」",
        include_in_prompt=True,
    ),
    MergeTestCase(
        zhongwen="之后李丽珊蝉联失败⋯",
        yuewen_to_merge=["之后李利山丧乱失败"],
        yuewen_merged="之后李利山丧乱失败⋯",
    ),
    MergeTestCase(
        zhongwen="亦由一个香港人从未听过的地方夺得",
        yuewen_to_merge=["亚运主办权亦都由一个香港人从未听过嘅地方夺得"],
        yuewen_merged="亚运主办权亦都由一个香港人从未听过嘅地方夺得",
    ),
    MergeTestCase(
        zhongwen="想着转行当运动员的茶餐厅伙记⋯",
        yuewen_to_merge=["谂住可以转行做运动员嘅茶餐厅伙计"],
        yuewen_merged="谂住可以转行做运动员嘅茶餐厅伙计⋯",
    ),
    MergeTestCase(
        zhongwen="都回到茶餐厅继续掷他们的蛋挞",
        yuewen_to_merge=["都返返去茶餐厅继续钉佢哋嘅蛋挞"],
        yuewen_merged="都返返去茶餐厅继续钉佢哋嘅蛋挞",
    ),
    MergeTestCase(
        zhongwen="一切回复正常",
        yuewen_to_merge=["一切回复正常"],
        yuewen_merged="一切回复正常",
    ),
]  # merge_test_cases_block_60
merge_test_cases_block_61 = [
    MergeTestCase(
        zhongwen="上中学后，我再没有练习抢包手",
        yuewen_to_merge=["上个中学", "我已经再冇练习抢包手"],
        yuewen_merged="上个中学，我已经再冇练习抢包手",
    ),
    MergeTestCase(
        zhongwen="有时候跟妈妈饮茶⋯",
        yuewen_to_merge=["间中同妈妈饮茶"],
        yuewen_merged="间中同妈妈饮茶⋯",
    ),
    MergeTestCase(
        zhongwen="我都会手快快替她抢一笼大包",
        yuewen_to_merge=["我都会手快快噉帮佢抢龙大包"],
        yuewen_merged="我都会手快快噉帮佢抢龙大包",
    ),
    MergeTestCase(
        zhongwen="之后，茶楼再不卖大包了",
        yuewen_to_merge=["之后茶楼都冇埋大包"],
        yuewen_merged="之后，茶楼都冇埋大包",
    ),
    MergeTestCase(
        zhongwen="点心车亦转成点心纸",
        yuewen_to_merge=["退车仔都转咗用点心纸"],
        yuewen_merged="退车仔都转咗用点心纸",
    ),
    MergeTestCase(
        zhongwen="一切落空",
        yuewen_to_merge=["一切都落空"],
        yuewen_merged="一切都落空",
    ),
]  # merge_test_cases_block_61
merge_test_cases_block_62 = [
    MergeTestCase(
        zhongwen="有时候我也会跟同学回到长洲烧烤",
        yuewen_to_merge=["有时我都会同班同学仔返长洲宵夜食"],
        yuewen_merged="有时我都会同班同学仔返长洲宵夜食",
    ),
    MergeTestCase(
        zhongwen="每次看见师傅⋯",
        yuewen_to_merge=["每次见到师傅"],
        yuewen_merged="每次见到师傅⋯",
    ),
    MergeTestCase(
        zhongwen="他都好像老了一点",
        yuewen_to_merge=["佢都好似老咗啲噉"],
        yuewen_merged="佢都好似老咗啲噉",
    ),
]  # merge_test_cases_block_62
merge_test_cases_block_63 = [
    MergeTestCase(
        zhongwen="因为环保⋯",
        yuewen_to_merge=["因为环保"],
        yuewen_merged="因为环保⋯",
    ),
    MergeTestCase(
        zhongwen="长洲的抢包都转为塑胶",
        yuewen_to_merge=["长洲嘅厂包经已转咗用塑胶"],
        yuewen_merged="长洲嘅厂包经已转咗用塑胶",
    ),
    MergeTestCase(
        zhongwen="师傅说，那阵胶气，相当臭",
        yuewen_to_merge=["师傅话𠮶阵胶气都几丑下"],
        yuewen_merged="师傅话𠮶阵胶气，都几丑下",
    ),
]  # merge_test_cases_block_63
merge_test_cases_block_64 = [
    MergeTestCase(
        zhongwen="长洲有个张保仔洞",
        yuewen_to_merge=["墙后个张宝仔洞"],
        yuewen_merged="墙后个张宝仔洞",
    ),
    MergeTestCase(
        zhongwen="听说张保仔在洞内藏了很多宝藏",
        yuewen_to_merge=["听讲海盗张宝仔喺里面收埋咗好多宝藏"],
        yuewen_merged="听讲海盗张宝仔喺里面收埋咗好多宝藏",
    ),
    MergeTestCase(
        zhongwen="因为我练过抢包手，身手比较灵活⋯",
        yuewen_to_merge=["因为我练过抢包手", "身手比较灵活"],
        yuewen_merged="因为我练过抢包手，身手比较灵活⋯",
    ),
    MergeTestCase(
        zhongwen="同学们叫我爬进去看看，说不定会发达",
        yuewen_to_merge=["班同我叫我爬佢睇下", "话唔定会发达"],
        yuewen_merged="班同我叫我爬佢睇下，话唔定会发达",
    ),
    MergeTestCase(
        zhongwen="于是我就向着这个又黑又窄的洞⋯",
        yuewen_to_merge=["于是我就向住呢一个又黑又窄嘅洞"],
        yuewen_merged="于是我就向住呢一个又黑又窄嘅洞⋯",
    ),
    MergeTestCase(
        zhongwen="一直爬",
        yuewen_to_merge=["系噉爬", "爬"],
        yuewen_merged="系噉爬爬",
    ),
    MergeTestCase(
        zhongwen="洞里面什么也没有，只有一个盒",
        yuewen_to_merge=["洞里面乜都冇", "净系有一个盒"],
        yuewen_merged="洞里面乜都冇，净系有一个盒",
    ),
    MergeTestCase(
        zhongwen="我小心揭开盒⋯",
        yuewen_to_merge=["我好小心揭开呢个盒"],
        yuewen_merged="我好小心揭开呢个盒⋯",
    ),
    MergeTestCase(
        zhongwen="发现里面一个没吃完的大包",
        yuewen_to_merge=["发现入面系一个食净咗嘅大包"],
        yuewen_merged="发现入面系一个食净咗嘅大包",
    ),
    MergeTestCase(
        zhongwen="是不是张保仔吃过的呢？",
        yuewen_to_merge=["唔知系咪张宝仔食净㗎啦"],
        yuewen_merged="唔知系咪张宝仔食净㗎啦？",
    ),
    MergeTestCase(
        zhongwen="揸住个包，我忽然明白⋯",
        yuewen_to_merge=["揸住个包", "我忽然明白"],
        yuewen_merged="揸住个包，我忽然明白⋯",
    ),
    MergeTestCase(
        zhongwen="原来有些事情， 没有就是没有",
        yuewen_to_merge=["原来有啲嘢冇", "就真系冇"],
        yuewen_merged="原来有啲嘢，冇就真系冇",
    ),
    MergeTestCase(
        zhongwen="唔得，就是唔得",
        yuewen_to_merge=["唔得", "就真系唔得"],
        yuewen_merged="唔得，就真系唔得",
    ),
    MergeTestCase(
        zhongwen="没有鱼蛋没有粗面没去成马尔代夫⋯",
        yuewen_to_merge=["冇鱼蛋", "冇粗面", "冇去买义大夫"],
        yuewen_merged="冇鱼蛋，冇粗面，冇去买义大夫⋯",
    ),
    MergeTestCase(
        zhongwen="没有奖牌没有张保仔宝藏",
        yuewen_to_merge=["冇奖牌冇张宝仔宝藏"],
        yuewen_merged="冇奖牌冇张宝仔宝藏",
    ),
    MergeTestCase(
        zhongwen="而张保仔，也没有咬过那个包",
        yuewen_to_merge=["而张宝仔亦都冇咬过个包"],
        yuewen_merged="而张宝仔，亦都冇咬过个包",
    ),
    MergeTestCase(
        zhongwen="原来蠢，并不那么好笑",
        yuewen_to_merge=["原来", "唔系咁好笑"],
        yuewen_merged="原来，唔系咁好笑",
    ),
    MergeTestCase(
        zhongwen="蠢会失败⋯",
        yuewen_to_merge=["会失败"],
        yuewen_merged="会失败⋯",
    ),
    MergeTestCase(
        zhongwen="会失望",
        yuewen_to_merge=["会失望"],
        yuewen_merged="会失望",
    ),
    MergeTestCase(
        zhongwen="失望，并不那么好笑",
        yuewen_to_merge=["失望", "唔系咁好笑"],
        yuewen_merged="失望，唔系咁好笑",
    ),
    MergeTestCase(
        zhongwen="肥，都不一定好笑",
        yuewen_to_merge=["肥", "都未必好笑"],
        yuewen_merged="肥，都未必好笑",
    ),
    MergeTestCase(
        zhongwen="肥，不一定大力",
        yuewen_to_merge=["肥", "唔一定大力"],
        yuewen_merged="肥，唔一定大力",
    ),
    MergeTestCase(
        zhongwen="大力，亦不一定得",
        yuewen_to_merge=["大力", "亦都唔一定得"],
        yuewen_merged="大力，亦都唔一定得",
    ),
    MergeTestCase(
        zhongwen="揸住个包，我忽然想⋯",
        yuewen_to_merge=["揸住个包", "我忽然喺度谂"],
        yuewen_merged="揸住个包，我忽然喺度谂⋯",
    ),
    MergeTestCase(
        zhongwen="长大了，到我要面对这个实掘掘⋯",
        yuewen_to_merge=["大个咗到我要面对呢一个实角局"],
        yuewen_merged="大个咗到我要面对呢一个实角局⋯",
    ),
    MergeTestCase(
        zhongwen="未必可以发梦，未必那么好笑的⋯",
        yuewen_to_merge=["未必到你发梦", "又未必咁好笑嘅"],
        yuewen_merged="未必到你发梦，又未必咁好笑嘅⋯",
    ),
    MergeTestCase(
        zhongwen="世界的时候，我会怎么样？",
        yuewen_to_merge=["世界嘅时候", "我会系点㗎呢"],
        yuewen_merged="世界嘅时候，我会系点㗎呢？",
    ),
]  # merge_test_cases_block_64
merge_test_cases_block_65 = [
    MergeTestCase(
        zhongwen="「⋯无力挽！」",
        yuewen_to_merge=["无泪弯"],
        yuewen_merged="「⋯无泪弯！」",
    ),
]  # merge_test_cases_block_65
merge_test_cases_block_66 = []  # merge_test_cases_block_66
merge_test_cases_block_67 = [
    MergeTestCase(
        zhongwen="是的，我就是大个佬麦兜",
        yuewen_to_merge=["系呀", "我就系大个佬麦豆喇"],
        yuewen_merged="系呀，我就系大个佬麦豆喇",
    ),
    MergeTestCase(
        zhongwen="肥，算大力",
        yuewen_to_merge=["肥啰", "算大力啦"],
        yuewen_merged="肥啰，算大力啦",
    ),
    MergeTestCase(
        zhongwen="麻麻地可以",
        yuewen_to_merge=["麻麻地得咁啦"],
        yuewen_merged="麻麻地得咁啦",
    ),
    MergeTestCase(
        zhongwen="负家产",
        yuewen_to_merge=["富家产啰"],
        yuewen_merged="富家产啰",
    ),
    MergeTestCase(
        zhongwen="脚爪是真的大，比一节瓜还要大",
        yuewen_to_merge=["脚瓜真系几大", "仲大过个折瓜"],
        yuewen_merged="脚瓜真系几大，仲大过个折瓜",
    ),
    MergeTestCase(
        zhongwen="脚瓜上的肌肉非常结实⋯",
        yuewen_to_merge=["脚瓜上面个肌肉非常结实"],
        yuewen_merged="脚瓜上面个肌肉非常结实⋯",
    ),
    MergeTestCase(
        zhongwen="青筋一条条凸出来，似钢筋",
        yuewen_to_merge=["啲青筋一条一条凸下凸下", "好似钢筋"],
        yuewen_merged="啲青筋一条一条凸下凸下，好似钢筋",
    ),
    MergeTestCase(
        zhongwen="至于脚趾甲⋯",
        yuewen_to_merge=["至于脚趾弓啲脚甲"],
        yuewen_merged="至于脚趾弓啲脚甲⋯",
    ),
    MergeTestCase(
        zhongwen="有次我无无聊聊真的量了一下⋯",
        yuewen_to_merge=["有次我无无聊聊真系走去卡下佢"],
        yuewen_merged="有次我无无聊聊真系走去卡下佢⋯",
    ),
    MergeTestCase(
        zhongwen="足有一寸厚",
        yuewen_to_merge=["哗", "粥粥成串咁厚"],
        yuewen_merged="哗，粥粥成串咁厚",
    ),
    MergeTestCase(
        zhongwen="是的，故事讲完了",
        yuewen_to_merge=["系呀", "故事讲完喇"],
        yuewen_merged="系呀，故事讲完喇",
    ),
    MergeTestCase(
        zhongwen="这是一个尝试",
        yuewen_to_merge=["呢个系一个尝试"],
        yuewen_merged="呢个系一个尝试",
    ),
    MergeTestCase(
        zhongwen="失败⋯尝试⋯",
        yuewen_to_merge=["失败", "尝试"],
        yuewen_merged="失败⋯尝试⋯",
    ),
    MergeTestCase(
        zhongwen="好多包⋯可是没有包保成功的故事",
        yuewen_to_merge=["好多包", "但系冇包补成功嘅故事"],
        yuewen_merged="好多包⋯但系冇包补成功嘅故事",
    ),
    MergeTestCase(
        zhongwen="故事说了一轮⋯",
        yuewen_to_merge=["故事讲咗一轮"],
        yuewen_merged="故事讲咗一轮⋯",
    ),
    MergeTestCase(
        zhongwen="什么也没有？也不是",
        yuewen_to_merge=["乜都冇", "又唔系噃"],
        yuewen_merged="乜都冇？又唔系噃",
    ),
    MergeTestCase(
        zhongwen="就是大了双脚瓜",
        yuewen_to_merge=["就系大咗两个脚瓜"],
        yuewen_merged="就系大咗两个脚瓜",
    ),
    MergeTestCase(
        zhongwen="可是楝一双脚瓜站这儿⋯",
        yuewen_to_merge=["但系冻住两个脚瓜企喺度"],
        yuewen_merged="但系冻住两个脚瓜企喺度⋯",
    ),
    MergeTestCase(
        zhongwen="当浪打过来⋯",
        yuewen_to_merge=["当啲浪打埋嚟"],
        yuewen_merged="当啲浪打埋嚟⋯",
    ),
    MergeTestCase(
        zhongwen="那感觉还真不错",
        yuewen_to_merge=["𠮶张感觉真系好好"],
        yuewen_merged="𠮶张感觉真系好好",
    ),
    MergeTestCase(
        zhongwen="你知道我麻麻地叻佬，不懂得⋯",
        yuewen_to_merge=["你知我麻麻地叻佬", "唔识得"],
        yuewen_merged="你知我麻麻地叻佬，唔识得⋯",
    ),
    MergeTestCase(
        zhongwen="替自己的故事加点教训呀锦囊呀那些",
        yuewen_to_merge=["帮自己嘅故事加啲教训呀", "锦囊呀𠮶啲嘢"],
        yuewen_merged="帮自己嘅故事加啲教训呀锦囊呀𠮶啲嘢",
    ),
    MergeTestCase(
        zhongwen="可是，浸一双脚瓜站水中⋯",
        yuewen_to_merge=["但系冻住两个脚瓜企喺水𠮶度"],
        yuewen_merged="但系冻住两个脚瓜企喺水𠮶度⋯",
    ),
    MergeTestCase(
        zhongwen="当风吹向我的脑，我会想⋯",
        yuewen_to_merge=["当风", "吹喺我个脑部", "我会谂"],
        yuewen_merged="当风吹喺我个脑部，我会谂⋯",
    ),
    MergeTestCase(
        zhongwen="如果妈妈看见我这个大脚瓜⋯",
        yuewen_to_merge=["如果妈妈见到我呢个大脚瓜"],
        yuewen_merged="如果妈妈见到我呢个大脚瓜⋯",
    ),
    MergeTestCase(
        zhongwen="我猜，她会好开心",
        yuewen_to_merge=["我谂佢会好开心"],
        yuewen_merged="我谂，佢会好开心",
    ),
]  # merge_test_cases_block_67
merge_test_cases_block_68 = [
    MergeTestCase(
        zhongwen="不成，还是出个锦囊！",
        yuewen_to_merge=["都系唔好呀", "都系出返个锦囊先得"],
        yuewen_merged="都系唔好呀，都系出返个锦囊先得！",
    ),
    MergeTestCase(
        zhongwen="妈妈的dot com散掉后，她又有计",
        yuewen_to_merge=["妈妈个Doccom散咗之后", "佢又有计喇"],
        yuewen_merged="妈妈个Doccom散咗之后，佢又有计喇",
    ),
    MergeTestCase(
        zhongwen="她出版了一本教烹饪的食谱",
        yuewen_to_merge=["佢出咗半教主送嘅食谱", "谂住捞返扎沙"],
        yuewen_merged="佢出咗半教主送嘅食谱，谂住捞返扎沙",
    ),
    MergeTestCase(
        zhongwen="食谱最后一页教人整烧鸡",
        yuewen_to_merge=["食谱最后一页系教人整烧鸡嘅"],
        yuewen_merged="食谱最后一页系教人整烧鸡嘅",
    ),
    MergeTestCase(
        zhongwen="方法简单，人人可学",
        yuewen_to_merge=["方法简单", "人人都学得识"],
        yuewen_merged="方法简单，人人都学得识",
    ),
    MergeTestCase(
        zhongwen="「烧鸡」",
        yuewen_to_merge=["烧鸡"],
        yuewen_merged="「烧鸡」",
    ),
    MergeTestCase(
        zhongwen="材料是⋯鸡",
        yuewen_to_merge=["材料系", "鸡"],
        yuewen_merged="材料系⋯鸡",
    ),
    MergeTestCase(
        zhongwen="方法：把鸡烧几烧",
        yuewen_to_merge=["方法", "攞只鸡", "去烧佢几烧"],
        yuewen_merged="方法：攞只鸡去烧佢几烧",
    ),
    MergeTestCase(
        zhongwen="就这样，一味「烧鸡」大功告成",
        yuewen_to_merge=["就噉", "一味烧鸡", "就大功告成喇"],
        yuewen_merged="就噉，一味「烧鸡」就大功告成喇",
    ),
    MergeTestCase(
        zhongwen="食谱里面补充说：",
        yuewen_to_merge=["食谱度又补充噉话"],
        yuewen_merged="食谱度又补充噉话：",
    ),
    MergeTestCase(
        zhongwen="如果你想把鸡烧得美味可口⋯",
        yuewen_to_merge=["如果想你个鸡烧得美味可口"],
        yuewen_merged="如果想你个鸡烧得美味可口⋯",
    ),
    MergeTestCase(
        zhongwen="吃完后不会心肺实胃气涨",
        yuewen_to_merge=["冇话食完腰心腰肺顶住个胃"],
        yuewen_merged="冇话食完腰心腰肺顶住个胃",
    ),
    MergeTestCase(
        zhongwen="秘诀是：拜托，把鸡烧好一点⋯",
        yuewen_to_merge=["个秘诀系唔该", "烧得佢好啲啰"],
        yuewen_merged="个秘诀系：唔该，烧得佢好啲啰⋯",
    ),
    MergeTestCase(
        zhongwen="多谢合作！",
        yuewen_to_merge=["多谢合作"],
        yuewen_merged="多谢合作！",
    ),
]  # merge_test_cases_block_68
merge_test_cases_block_69 = [
    MergeTestCase(
        zhongwen="麻烦你，一客常餐",
        yuewen_to_merge=["唔该", "我要一个常餐啦"],
        yuewen_merged="唔该，我要一个常餐啦",
    ),
    MergeTestCase(
        zhongwen="常餐？常餐有什么吃？",
        yuewen_to_merge=["常餐", "常餐有咩食㗎"],
        yuewen_merged="常餐？常餐有咩食㗎？",
    ),
    MergeTestCase(
        zhongwen="跟特餐一样吧",
        yuewen_to_merge=["同特餐一样啰"],
        yuewen_merged="同特餐一样啰",
    ),
    MergeTestCase(
        zhongwen="特餐是什么？",
        yuewen_to_merge=["噉特餐系咩嚟㗎"],
        yuewen_merged="噉特餐系咩嚟㗎？",
    ),
    MergeTestCase(
        zhongwen="跟快餐差不多",
        yuewen_to_merge=["同快餐咁上下啰"],
        yuewen_merged="同快餐咁上下啰",
    ),
    MergeTestCase(
        zhongwen="快餐又是什么？",
        yuewen_to_merge=["噉快餐又系咩嚟㗎"],
        yuewen_merged="噉快餐又系咩嚟㗎？",
    ),
    MergeTestCase(
        zhongwen="快餐即是午餐",
        yuewen_to_merge=["即系快餐咪真系午餐"],
        yuewen_merged="即系快餐咪真系午餐",
    ),
    MergeTestCase(
        zhongwen="午餐吃什么？",
        yuewen_to_merge=["午餐食咩㗎"],
        yuewen_merged="午餐食咩㗎？",
    ),
    MergeTestCase(
        zhongwen="午餐跟晚餐一样",
        yuewen_to_merge=["午餐同晚餐一样㗎"],
        yuewen_merged="午餐同晚餐一样㗎",
    ),
    MergeTestCase(
        zhongwen="晚餐又吃什么？",
        yuewen_to_merge=["噉晚餐又食啲咩呀"],
        yuewen_merged="噉晚餐又食啲咩呀？",
    ),
    MergeTestCase(
        zhongwen="晚餐即是常餐",
        yuewen_to_merge=["晚餐咪真系常餐啰"],
        yuewen_merged="晚餐咪真系常餐啰",
    ),
    MergeTestCase(
        zhongwen="那么，两客常餐吧",
        yuewen_to_merge=["噉呀", "我要两个常餐啦"],
        yuewen_merged="噉呀，我要两个常餐啦",
    ),
]  # merge_test_cases_block_69
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
        yuewen_to_merge=["咁你头先又话冇上餐"],
        yuewen_merged="咁你头先又话冇上餐？",
    ),
    MergeTestCase(
        zhongwen="对，常餐卖光了，要吃特餐吗？",
        yuewen_to_merge=["系呀", "上餐就系卖晒呀", "咁你试唔试下特餐啦"],
        yuewen_merged="系呀，上餐就系卖晒呀，咁你试唔试下特餐啦？",
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
]  # merge_test_cases_block_70
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
        yuewen_to_merge=["午餐啦", "午餐", "好嘢呀"],
        yuewen_merged="午餐啦，午餐，好嘢呀",
    ),
    MergeTestCase(
        zhongwen="怎么个精采法？",
        yuewen_to_merge=["点好嘢法呀"],
        yuewen_merged="点好嘢法呀？",
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
]  # merge_test_cases_block_71
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
        yuewen_merged="日光日白，食乜鬼嘢晚餐啊？",
        include_in_prompt=True,
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
]  # merge_test_cases_block_72
mlamd_merge_test_cases: list[MergeTestCase] = sum(
    (globals()[f"merge_test_cases_block_{i}"] for i in range(73)), []
)
"""MLAMD 粤文 merging test cases."""

__all__ = [
    "mlamd_merge_test_cases",
]
