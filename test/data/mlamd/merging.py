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
        include_in_prompt=True,
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
]  # merge_test_cases_block_0
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
    MergeTestCase(
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
]  # merge_test_cases_block_1
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
]  # merge_test_cases_block_2
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
    MergeTestCase(
        zhongwen="小朋友，这个月你们交过学费没有？",
        yuewen_to_merge=["小朋友", "你哋今个月交咗学费咩呀"],
        yuewen_merged="小朋友，你哋今个月交咗学费咩呀？",
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
    ),
    MergeTestCase(
        zhongwen="这儿是我们最快乐，最美丽的乐园⋯",
        yuewen_to_merge=["呢度系我哋最快乐", "最美丽嘅乐园"],
        yuewen_merged="呢度系我哋最快乐，最美丽嘅乐园⋯",
    ),
    MergeTestCase(
        zhongwen="⋯还有一个很疼我们",
        yuewen_to_merge=["仲有一个好疼我哋"],
        yuewen_merged="仲有一个好疼我哋⋯",
    ),
    MergeTestCase(
        zhongwen="就是有点游魂的Miss Chan",
        yuewen_to_merge=["不过就有少少失魂嘅班主有Miss", "Chan"],
        yuewen_merged="不过就有少少失魂嘅班主有Miss Chan",
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
    ),
    MergeTestCase(
        zhongwen="麦唛同学！　　到！",
        yuewen_to_merge=["麦麦同学", "到"],
        yuewen_merged="麦麦同学！　　到！",
    ),
    MergeTestCase(
        zhongwen="亚辉同学！　　到！",
        yuewen_to_merge=["阿辉同学", "到"],
        yuewen_merged="阿辉同学！到！",
    ),
    MergeTestCase(
        zhongwen="菇时同学！　　到！",
        yuewen_to_merge=["Boosie同学", "到"],
        yuewen_merged="Boosie同学！　　到！",
    ),
    MergeTestCase(
        zhongwen="得巴同学！　　到！",
        yuewen_to_merge=["德巴同学", "到"],
        yuewen_merged="德巴同学！到！",
    ),
    MergeTestCase(
        zhongwen="阿May同学！　　到！",
        yuewen_to_merge=["阿May同学", "到"],
        yuewen_merged="阿May同学！到！",
    ),
    MergeTestCase(
        zhongwen="阿June同学！　　到！",
        yuewen_to_merge=["阿June同学", "到"],
        yuewen_merged="阿June同学！到！",
    ),
    MergeTestCase(
        zhongwen="阿May同学！",
        yuewen_to_merge=["阿May同学"],
        yuewen_merged="阿May同学！",
    ),
    MergeTestCase(
        zhongwen="Miss Chan，我点过两次了！",
        yuewen_to_merge=["Miss", "Chan你点咗我两次喇"],
        yuewen_merged="Miss Chan，你点咗我两次喇！",
    ),
    MergeTestCase(
        zhongwen="呀，真的吗？",
        yuewen_to_merge=["啊", "系咩"],
        yuewen_merged="啊，系咩？",
    ),
    MergeTestCase(
        zhongwen="我们现在继续点名",
        yuewen_to_merge=["好", "我哋而家继续点名"],
        yuewen_merged="好，我哋而家继续点名",
    ),
    MergeTestCase(
        zhongwen="菇时同学！　　到！",
        yuewen_to_merge=["川明同学", "到"],
        yuewen_merged="川明同学！　　到！",
    ),
    MergeTestCase(
        zhongwen="还有谁没点过吗？",
        yuewen_to_merge=["好", "仲有边个未点"],
        yuewen_merged="好，仲有边个未点？",
    ),
    MergeTestCase(
        zhongwen="麦兜！",
        yuewen_to_merge=["猫", "噢"],
        yuewen_merged="猫！噢！",
    ),
    MergeTestCase(
        zhongwen="麦兜同学！",
        yuewen_to_merge=["麦兜同学"],
        yuewen_merged="麦兜同学！",
    ),
    MergeTestCase(
        zhongwen="麦唛呀，即是呢⋯",
        yuewen_to_merge=["妈妈啊", "麦兜同学", "即系呢"],
        yuewen_merged="妈妈啊，麦兜同学，即系呢⋯",
    ),
    MergeTestCase(
        zhongwen="我好像觉得呢⋯",
        yuewen_to_merge=["我个心总系仁住仁住"],
        yuewen_merged="我个心总系仁住仁住⋯",
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
    ),
    MergeTestCase(
        zhongwen="橙，为什么会是「疴﹣烂﹣煮」呢？",
        yuewen_to_merge=["点解橙叫Orange呢"],
        yuewen_merged="点解橙叫Orange呢？",
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
    ),
    MergeTestCase(
        zhongwen="还有这个「芭﹣娜﹣娜」香蕉",
        yuewen_to_merge=["仲有呢个啊", "芭拉娜啊", "香蕉啊"],
        yuewen_merged="仲有呢个啊，「芭拉娜」啊，香蕉啊",
    ),
    MergeTestCase(
        zhongwen="为什么雨伞又会是「暗﹣芭﹣娜﹣娜」呢？",
        yuewen_to_merge=["点解雨姐会叫做暗芭拉娜呢"],
        yuewen_merged="点解雨姐会叫做暗芭拉娜呢？",
    ),
    MergeTestCase(
        zhongwen="我「暗」的「暗」掉一条蕉",
        yuewen_to_merge=["嗱", "我暗啦", "噉我暗𠮶条香蕉"],
        yuewen_merged="嗱，我暗啦，噉我暗𠮶条香蕉",
    ),
    MergeTestCase(
        zhongwen="至多是疴烂煮，怎么会下起雨来呢？",
        yuewen_to_merge=["至多会Orange啫", "点解会搞到落雨呢"],
        yuewen_merged="至多会Orange啫，点解会搞到落雨呢？",
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
    ),
    MergeTestCase(
        zhongwen="升小学，上中学",
        yuewen_to_merge=["识埋小学", "上到中学"],
        yuewen_merged="识埋小学，上到中学",
    ),
    MergeTestCase(
        zhongwen="再念大学⋯",
        yuewen_to_merge=["再入埋大学"],
        yuewen_merged="再入埋大学⋯",
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
    ),
    MergeTestCase(
        zhongwen="那时候⋯",
        yuewen_to_merge=["到𠮶阵"],
        yuewen_merged="到𠮶阵⋯",
    ),
    MergeTestCase(
        zhongwen="我买所房子给妈妈！",
        yuewen_to_merge=["我买层楼畀我妈妈"],
        yuewen_merged="我买层楼畀我妈妈！",
    ),
]  # merge_test_cases_block_4
merge_test_cases_block_5 = [
    MergeTestCase(
        zhongwen="幼稚园楼下，由校长兼营的茶餐厅",
        yuewen_to_merge=["喺幼稚园楼下校长兼营嘅间茶餐厅"],
        yuewen_merged="喺幼稚园楼下，校长兼营嘅间茶餐厅",
    ),
    MergeTestCase(
        zhongwen="我们一班同学下课后经常光顾",
        yuewen_to_merge=["我哋一班同学仔放咗学都经常系傍陈"],
        yuewen_merged="我哋一班同学仔放咗学都经常系傍陈",
    ),
    MergeTestCase(
        zhongwen="鱼蛋粗面，麻烦你　　粗面买光了",
        yuewen_to_merge=["唔该鱼蛋粗啊", "冇粗面噃"],
        yuewen_merged="唔该鱼蛋粗啊，冇粗面噃",
    ),
    MergeTestCase(
        zhongwen="那样子⋯来碗鱼蛋河粉吧　　鱼蛋买光了",
        yuewen_to_merge=["噉啊", "要碗鱼蛋好啊", "冇鱼蛋噃"],
        yuewen_merged="噉啊⋯要碗鱼蛋好啊　　冇鱼蛋噃",
    ),
    MergeTestCase(
        zhongwen="那么⋯金钱肚粗面好了　　粗面买光了",
        yuewen_to_merge=["噉啊", "要金钱透粗啊", "冇粗面噃"],
        yuewen_merged="噉啊⋯要金钱透粗啊　　冇粗面噃",
    ),
    MergeTestCase(
        zhongwen="那么要鱼蛋油面吧　　鱼蛋买光了",
        yuewen_to_merge=["噉啊", "咁要鱼蛋油面啊", "冇鱼蛋噃"],
        yuewen_merged="噉啊，咁要鱼蛋油面啊　　冇鱼蛋噃",
    ),
    MergeTestCase(
        zhongwen="怎么都买光了？",
        yuewen_to_merge=["乜样样都冇嘅"],
        yuewen_merged="乜样样都冇嘅？",
    ),
    MergeTestCase(
        zhongwen="来个墨鱼丸粗面吧　　粗面买光了",
        yuewen_to_merge=["噉要蜜丸粗啊", "冇粗面噃"],
        yuewen_merged="噉要蜜丸粗啊　　冇粗面噃",
    ),
    MergeTestCase(
        zhongwen="又买光了？",
        yuewen_to_merge=["又冇啊"],
        yuewen_merged="又冇啊？",
    ),
    MergeTestCase(
        zhongwen="麻烦来碗鱼蛋濑吧　　鱼蛋买光了",
        yuewen_to_merge=["噉唔该畀碗鱼蛋奶啊", "冇鱼蛋噃"],
        yuewen_merged="噉唔该畀碗鱼蛋奶啊　　冇鱼蛋噃",
    ),
    MergeTestCase(
        zhongwen="麦兜呀，鱼蛋跟粗面都买光了",
        yuewen_to_merge=["麦兜啊", "佢哋啲鱼蛋同粗面卖晒㗎啦"],
        yuewen_merged="麦兜啊，佢哋啲鱼蛋同粗面卖晒㗎啦",
    ),
    MergeTestCase(
        zhongwen="即是所有鱼蛋跟粗面的配搭都没了",
        yuewen_to_merge=["即系所有要鱼蛋或者粗面嘅配搭都冇㗎啦"],
        yuewen_merged="即系所有要鱼蛋或者粗面嘅配搭都冇㗎啦",
    ),
    MergeTestCase(
        zhongwen="没有那些配搭吗？",
        yuewen_to_merge=["噢", "冇𠮶啲配搭啊"],
        yuewen_merged="「噢」冇𠮶啲配搭啊？",
    ),
    MergeTestCase(
        zhongwen="麻烦你，净要鱼蛋吧　　鱼蛋买光了",
        yuewen_to_merge=["噉唔该净鱼蛋啊", "冇鱼蛋噃"],
        yuewen_merged="噉唔该净鱼蛋啊　　冇鱼蛋噃",
    ),
    MergeTestCase(
        zhongwen="那么净要粗面呢？　　粗面买光了",
        yuewen_to_merge=["净粗面呢", "冇粗面噃"],
        yuewen_merged="净粗面呢？　　冇粗面噃",
    ),
    MergeTestCase(
        zhongwen="看到这里⋯",
        yuewen_to_merge=["睇到呢度"],
        yuewen_merged="睇到呢度⋯",
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
    ),
    MergeTestCase(
        zhongwen="鱼蛋买光了？那么粗面吧",
        yuewen_to_merge=["冇鱼蛋咩", "粗面都好啊"],
        yuewen_merged="冇鱼蛋咩？粗面都好啊",
    ),
    MergeTestCase(
        zhongwen="麦兜，射呀！",
        yuewen_to_merge=["麦兜", "转身食啊"],
        yuewen_merged="麦兜，转身食啊！",
    ),
]  # merge_test_cases_block_5
merge_test_cases_block_6 = [
    MergeTestCase(
        zhongwen="看着自己每天疴烂煮⋯",
        yuewen_to_merge=["睇住自己日日柯能处"],
        yuewen_merged="睇住自己日日柯能处⋯",
    ),
    MergeTestCase(
        zhongwen="每天长肉⋯",
        yuewen_to_merge=["日日掌肉"],
        yuewen_merged="日日掌肉⋯",
    ),
    MergeTestCase(
        zhongwen="我感到充满力量！",
        yuewen_to_merge=["感到充满力量"],
        yuewen_merged="感到充满力量！",
    ),
    MergeTestCase(
        zhongwen="世界好美丽！",
        yuewen_to_merge=["世界好美丽"],
        yuewen_merged="世界好美丽！",
    ),
]  # merge_test_cases_block_6
merge_test_cases_block_7 = [
    MergeTestCase(
        zhongwen="有一首歌，Miss Chan唱的好听",
        yuewen_to_merge=["有一首歌", "麦词春唱得好好听呀"],
        yuewen_merged="有一首歌，麦词春唱得好好听呀",
    ),
    MergeTestCase(
        zhongwen="我时常想着学习",
        yuewen_to_merge=["我成日想学习"],
        yuewen_merged="我成日想学习",
    ),
    MergeTestCase(
        zhongwen="可每次我总唱成「疴」什么什么的⋯",
        yuewen_to_merge=["但系唱嚟唱去都系阿伦厨", "咁Ballana噉"],
        yuewen_merged="但系唱嚟唱去都系阿伦厨，咁Ballana噉⋯",
    ),
    MergeTestCase(
        zhongwen="是All Things Bright and Beautiful吧？",
        yuewen_to_merge=["系唔系All", "Things", "Bright", "and", "Beautiful呀"],
        yuewen_merged="系唔系All Things Bright and Beautiful呀？",
    ),
    MergeTestCase(
        zhongwen="是的，一切都好！",
        yuewen_to_merge=["系呀", "所有嘢都几好喇"],
        yuewen_merged="系呀，所有嘢都几好喇！",
    ),
    MergeTestCase(
        zhongwen="世上一切，一切一切⋯",
        yuewen_to_merge=["世上一切"],
        yuewen_merged="世上一切⋯",
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
    ),
]  # merge_test_cases_block_7
merge_test_cases_block_8 = [
    MergeTestCase(
        zhongwen="多劳多得！",
        yuewen_to_merge=["1234567", "多喽多得"],
        yuewen_merged="1234567，多喽多得！",
    ),
    MergeTestCase(
        zhongwen="星期一至星期七⋯多劳多得！",
        yuewen_to_merge=["星期一至星期七多喽多得"],
        yuewen_merged="星期一至星期七⋯多喽多得！",
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
    ),
]  # merge_test_cases_block_8
merge_test_cases_block_9 = [
    MergeTestCase(
        zhongwen="是的，我妈妈真的很厉害",
        yuewen_to_merge=["系呀", "我妈妈真系好犀利㗎"],
        yuewen_merged="系呀，我妈妈真系好犀利㗎",
    ),
    MergeTestCase(
        zhongwen="除了兼任保险，地产经纪及trading⋯",
        yuewen_to_merge=["除咗做保险地产经纪同埋trading之外"],
        yuewen_merged="除咗做保险地产经纪同埋trading之外⋯",
    ),
    MergeTestCase(
        zhongwen="她还趁高科技热潮搞了个烹饪网站⋯",
        yuewen_to_merge=["佢仲趁住高科技热潮搞咗个煮𩠌嘅网站"],
        yuewen_merged="佢仲趁住高科技热潮搞咗个煮𩠌嘅网站⋯",
    ),
    MergeTestCase(
        zhongwen="www．麦太世界．com",
        yuewen_to_merge=["www.mcticege.com"],
        yuewen_merged="www.mcticege.com",
    ),
    MergeTestCase(
        zhongwen="她做的菜，同样厉害",
        yuewen_to_merge=["佢煮嘅𩠌一样咁犀利"],
        yuewen_merged="佢煮嘅𩠌，一样咁犀利",
    ),
    MergeTestCase(
        zhongwen="欢迎大家收看《麦太世界》",
        yuewen_to_merge=["欢迎大家收睇麦太世界"],
        yuewen_merged="欢迎大家收睇《麦太世界》",
    ),
    MergeTestCase(
        zhongwen="今日为大家介绍一个⋯",
        yuewen_to_merge=["今日我为大家介绍个"],
        yuewen_merged="今日我为大家介绍个⋯",
    ),
    MergeTestCase(
        zhongwen="简单别致的小菜纸包鸡",
        yuewen_to_merge=["简单又别致嘅小菜", "自包鸡"],
        yuewen_merged="简单又别致嘅小菜自包鸡",
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
    ),
    MergeTestCase(
        zhongwen="将鸡包底部的纸撕下来⋯慢慢地撕",
        yuewen_to_merge=["我哋将黐喺鸡包底嘅纸撕出嚟", "慢慢撕"],
        yuewen_merged="我哋将黐喺鸡包底嘅纸撕出嚟⋯慢慢撕",
    ),
    MergeTestCase(
        zhongwen="就会得到一张鸡包纸",
        yuewen_to_merge=["咁就会得到一张鸡包纸喇"],
        yuewen_merged="咁就会得到一张鸡包纸喇",
    ),
    MergeTestCase(
        zhongwen="把鸡包纸一反反转",
        yuewen_to_merge=["然后将鸡包纸一反", "反转"],
        yuewen_merged="然后将鸡包纸一反，反转",
    ),
    MergeTestCase(
        zhongwen="这一味纸包鸡就完成了，很容易是吧？",
        yuewen_to_merge=["呢味自包鸡就完成喇", "系咪好易整啦"],
        yuewen_merged="呢味自包鸡就完成喇，系咪好易整啦？",
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
    ),
    MergeTestCase(
        zhongwen="只要把这纸这样子⋯",
        yuewen_to_merge=["我哋只需要张张纸", "咁样"],
        yuewen_merged="我哋只需要张张纸咁样⋯",
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
    ),
]  # merge_test_cases_block_10
merge_test_cases_block_11 = [
    MergeTestCase(
        zhongwen="现在要教大家一味别致小菜﹣",
        yuewen_to_merge=["间阵要教大家一味几别节嘅小菜"],
        yuewen_merged="间阵要教大家一味几别节嘅小菜﹣",
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
        yuewen_merged="咁一味包鸡子包鸡包子包鸡就完成喇！",
    ),
    MergeTestCase(
        zhongwen="真的很简单吧？",
        yuewen_to_merge=["系咪好简单呢"],
        yuewen_merged="系咪好简单呢？",
    ),
    MergeTestCase(
        zhongwen="还真有一块鸡吃呢！",
        yuewen_to_merge=["仲真系有嚿鸡食添"],
        yuewen_merged="仲真系有嚿鸡食添！",
    ),
]  # merge_test_cases_block_11
merge_test_cases_block_12 = [
    MergeTestCase(
        zhongwen="今日为大家介绍一味⋯",
        yuewen_to_merge=["今日要同大家介绍一味"],
        yuewen_merged="今日要同大家介绍一味⋯",
    ),
    MergeTestCase(
        zhongwen="小朋友一定喜欢的⋯",
        yuewen_to_merge=["小朋友一定喜欢嘅"],
        yuewen_merged="小朋友一定喜欢嘅⋯",
    ),
    MergeTestCase(
        zhongwen="鸡包包鸡包包鸡包纸包纸⋯",
        yuewen_to_merge=["鸡包包", "鸡包包", "鸡包纸包", "纸包鸡"],
        yuewen_merged="鸡包包鸡包包鸡包纸包纸包鸡⋯",
    ),
    MergeTestCase(
        zhongwen="包鸡包鸡包纸包鸡",
        yuewen_to_merge=["包包鸡", "纸包鸡", "包纸包鸡"],
        yuewen_merged="包包鸡纸包鸡包纸包鸡",
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
        zhongwen="可我妈妈也有她温柔的一面",
        yuewen_to_merge=["不过我妈妈都有佢温柔嘅一面"],
        yuewen_merged="不过我妈妈都有佢温柔嘅一面",
    ),
    MergeTestCase(
        zhongwen="例如每晚睡觉前，她都会说故事给我听",
        yuewen_to_merge=["例如每晚临睡前", "佢都会讲故事畀我听"],
        yuewen_merged="例如每晚临睡前，佢都会讲故事畀我听",
    ),
    MergeTestCase(
        zhongwen="他死了！",
        yuewen_to_merge=["有一日", "佢死咗"],
        yuewen_merged="有一日，佢死咗！",
    ),
    MergeTestCase(
        zhongwen="从前，有个小朋友很勤力念书⋯",
        yuewen_to_merge=["从前有个小朋友好勤力读书"],
        yuewen_merged="从前，有个小朋友好勤力读书⋯",
    ),
    MergeTestCase(
        zhongwen="他长大后，发财了！",
        yuewen_to_merge=["佢长大发咗"],
        yuewen_merged="佢长大发咗！",
    ),
    MergeTestCase(
        zhongwen="他扭了脚骹！",
        yuewen_to_merge=["有一日佢屈亲个脚脚"],
        yuewen_merged="有一日佢屈亲个脚脚！",
    ),
    MergeTestCase(
        zhongwen="妈妈，我想睡觉",
        yuewen_to_merge=["妈我想瞓啦"],
        yuewen_merged="妈，我想瞓啦",
    ),
]  # merge_test_cases_block_12
merge_test_cases_block_13 = []  # merge_test_cases_block_13
merge_test_cases_block_14 = []  # merge_test_cases_block_14
merge_test_cases_block_15 = []  # merge_test_cases_block_15
merge_test_cases_block_16 = []  # merge_test_cases_block_16
merge_test_cases_block_17 = [
    MergeTestCase(
        zhongwen="衰仔，快点起床上学",
        yuewen_to_merge=["喂", "衰仔啊", "快啲起身返学喇"],
        yuewen_merged="喂，衰仔啊，快啲起身返学喇",
    ),
    MergeTestCase(
        zhongwen="咦？",
        yuewen_to_merge=["咦"],
        yuewen_merged="咦？",
    ),
    MergeTestCase(
        zhongwen="妈妈！",
        yuewen_to_merge=["妈妈"],
        yuewen_merged="妈妈！",
    ),
]  # merge_test_cases_block_17
merge_test_cases_block_18 = []  # merge_test_cases_block_18
merge_test_cases_block_19 = []  # merge_test_cases_block_19
merge_test_cases_block_20 = [
    MergeTestCase(
        zhongwen="好呀，马尔代夫！",
        yuewen_to_merge=["嘻嘻", "好嘢"],
        yuewen_merged="嘻嘻，好嘢！",
    ),
    MergeTestCase(  # REVIEW
        zhongwen="马尔代夫！",
        yuewen_to_merge=["买二代夫", "买二代夫"],
        yuewen_merged="买二代夫，买二代夫！",
    ),
    MergeTestCase(
        zhongwen="马尔代夫！",
        yuewen_to_merge=["买二代夫"],
        yuewen_merged="买二代夫！",
    ),
    MergeTestCase(
        zhongwen="妈妈，那么我们什么时候去？",
        yuewen_to_merge=["妈妈", "咁我哋几时去呀"],
        yuewen_merged="妈妈，咁我哋几时去呀？",
    ),
    MergeTestCase(
        zhongwen="你先把药水喝掉，病好了我就去订机票",
        yuewen_to_merge=["嗯", "你乖乖哋食埋啲药", "好返晒啦", "我即刻订机票"],
        yuewen_merged="嗯，你乖乖哋食埋啲药，好返晒啦我即刻订机票",
    ),
    MergeTestCase(
        zhongwen="来，多喝一点！",
        yuewen_to_merge=["嚟啦", "食多更"],
        yuewen_merged="嚟啦，食多更！",
    ),
]  # merge_test_cases_block_20
merge_test_cases_block_21 = [
    MergeTestCase(
        zhongwen="妈妈，你看！",
        yuewen_to_merge=["妈妈你睇"],
        yuewen_merged="妈妈，你睇！",
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
merge_test_cases_block_22 = []  # merge_test_cases_block_22
merge_test_cases_block_23 = []  # merge_test_cases_block_23
merge_test_cases_block_24 = []  # merge_test_cases_block_24
merge_test_cases_block_25 = []  # merge_test_cases_block_25
merge_test_cases_block_26 = []  # merge_test_cases_block_26
merge_test_cases_block_27 = []  # merge_test_cases_block_27
merge_test_cases_block_28 = []  # merge_test_cases_block_28
merge_test_cases_block_29 = []  # merge_test_cases_block_29
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
merge_test_cases_block_31 = []  # merge_test_cases_block_31
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
merge_test_cases_block_35 = []  # merge_test_cases_block_35
merge_test_cases_block_36 = []  # merge_test_cases_block_36
merge_test_cases_block_37 = []  # merge_test_cases_block_37
merge_test_cases_block_38 = []  # merge_test_cases_block_38
merge_test_cases_block_39 = []  # merge_test_cases_block_39
merge_test_cases_block_40 = []  # merge_test_cases_block_40
merge_test_cases_block_41 = []  # merge_test_cases_block_41
merge_test_cases_block_42 = []  # merge_test_cases_block_42
merge_test_cases_block_43 = []  # merge_test_cases_block_43
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
merge_test_cases_block_45 = []  # merge_test_cases_block_45
merge_test_cases_block_46 = []  # merge_test_cases_block_46
merge_test_cases_block_47 = []  # merge_test_cases_block_47
merge_test_cases_block_48 = []  # merge_test_cases_block_48
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
]  # merge_test_cases_block_50
merge_test_cases_block_51 = []  # merge_test_cases_block_51
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
merge_test_cases_block_53 = []  # merge_test_cases_block_53
merge_test_cases_block_54 = []  # merge_test_cases_block_54
merge_test_cases_block_55 = []  # merge_test_cases_block_55
merge_test_cases_block_56 = []  # merge_test_cases_block_56
merge_test_cases_block_57 = []  # merge_test_cases_block_57
merge_test_cases_block_58 = []  # merge_test_cases_block_58
merge_test_cases_block_59 = []  # merge_test_cases_block_59
merge_test_cases_block_60 = [
    MergeTestCase(
        zhongwen="最后⋯",
        yuewen_to_merge=["最后"],
        yuewen_merged="最后⋯",
    ),
    MergeTestCase(
        zhongwen="最后，一切成烟",
        yuewen_to_merge=["最后全部都系banana"],
        yuewen_merged="最后，全部都系banana",
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
    ),
    MergeTestCase(
        zhongwen="之后李丽珊蝉联失败⋯",
        yuewen_to_merge=["之后李利山丧乱失败"],
        yuewen_merged="之后李利山丧乱失败⋯",
    ),
    MergeTestCase(
        zhongwen="亚运主办权⋯",
        yuewen_to_merge=["亚运主办权"],
        yuewen_merged="亚运主办权⋯",
    ),
    MergeTestCase(
        zhongwen="亦由一个香港人从未听过的地方夺得",
        yuewen_to_merge=["亦都由一个香港人从未听过嘅地方夺得"],
        yuewen_merged="亦都由一个香港人从未听过嘅地方夺得",
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
merge_test_cases_block_61 = []  # merge_test_cases_block_61
merge_test_cases_block_62 = []  # merge_test_cases_block_62
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
        yuewen_merged="师傅话，𠮶阵胶气，都几丑下",
    ),
]  # merge_test_cases_block_63
merge_test_cases_block_64 = []  # merge_test_cases_block_64
merge_test_cases_block_65 = [
    MergeTestCase(
        zhongwen="「⋯无力挽！」",
        yuewen_to_merge=["无泪弯"],
        yuewen_merged="「⋯无泪弯！」",
    ),
]  # merge_test_cases_block_65
merge_test_cases_block_66 = []  # merge_test_cases_block_66
merge_test_cases_block_67 = []  # merge_test_cases_block_67
merge_test_cases_block_68 = []  # merge_test_cases_block_68
merge_test_cases_block_69 = []  # merge_test_cases_block_69
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
    MergeTestCase(  # REVIEW: SEEMS TO BE MISALIGNED
        zhongwen="常餐不是卖光了吗？",
        yuewen_to_merge=["咁你头先又话冇上餐", "系呀", "上餐就系卖晒呀"],
        yuewen_merged="咁你头先又话冇上餐，系呀，上餐就系卖晒呀？",
    ),
    MergeTestCase(  # REVIEW: SEEMS TO BE MISALIGNED
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
