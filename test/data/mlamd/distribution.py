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
distribute_test_cases_block_5 = [
    DistributeTestCase(
        one_zhongwen="鱼蛋粗面，麻烦你　　粗面买光了",
        one_yuewen_start="唔该鱼蛋粗啊",
        two_zhongwen="那样子⋯来碗鱼蛋河粉吧　　鱼蛋买光了",
        two_yuewen_end="噉啊要碗鱼蛋好啊",
        yuewen_to_distribute="冇粗面噃",
        one_yuewen_to_append="冇粗面噃",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="那样子⋯来碗鱼蛋河粉吧　　鱼蛋买光了",
        one_yuewen_start="噉啊要碗鱼蛋好啊",
        two_zhongwen="那么⋯金钱肚粗面好了　　粗面买光了",
        two_yuewen_end="噉啊要金钱透粗啊冇粗面噃",
        yuewen_to_distribute="冇鱼蛋噃",
        one_yuewen_to_append="冇鱼蛋噃",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="那么⋯金钱肚粗面好了　　粗面买光了",
        one_yuewen_start="噉啊要金钱透粗啊冇粗面噃",
        two_zhongwen="那么要鱼蛋油面吧　　鱼蛋买光了",
        two_yuewen_end="咁要鱼蛋油面啊",
        yuewen_to_distribute="噉啊",
        one_yuewen_to_append="",
        two_yuewen_to_prepend="噉啊",
    ),
    DistributeTestCase(
        one_zhongwen="又买光了？",
        one_yuewen_start="冇粗面噃",
        two_zhongwen="麻烦来碗鱼蛋濑吧　　鱼蛋买光了",
        two_yuewen_end="噉唔该畀碗鱼蛋奶啊",
        yuewen_to_distribute="又冇啊",
        one_yuewen_to_append="又冇啊",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="麻烦来碗鱼蛋濑吧　　鱼蛋买光了",
        one_yuewen_start="噉唔该畀碗鱼蛋奶啊",
        two_zhongwen="麦兜呀，鱼蛋跟粗面都买光了",
        two_yuewen_end="麦兜啊佢哋啲鱼蛋同粗面卖晒㗎啦",
        yuewen_to_distribute="冇鱼蛋噃",
        one_yuewen_to_append="冇鱼蛋噃",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="看到这里⋯",
        one_yuewen_start="",
        two_zhongwen="大家大概都知道我是个怎么样的叻仔",
        two_yuewen_end="大家大概都知道我有几叻仔嘞",
        yuewen_to_distribute="睇到呢度",
        one_yuewen_to_append="睇到呢度",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="那时候我无忧无虑，万事无所谓﹣﹣",
        one_yuewen_start="果只我无忧无虑",
        two_zhongwen="鱼蛋买光了？那么粗面吧",
        two_yuewen_end="冇鱼蛋咩粗面都好啊",
        yuewen_to_distribute="冇乜所谓",
        one_yuewen_to_append="冇乜所谓",
        two_yuewen_to_prepend="",
    ),
]  # distribute_test_cases_block_5
distribute_test_cases_block_6 = []  # distribute_test_cases_block_6
distribute_test_cases_block_7 = [
    DistributeTestCase(
        one_zhongwen="可每次我总唱成「疴」什么什么的⋯",
        one_yuewen_start="但系唱嚟唱去都系阿伦厨",
        two_zhongwen="是All Things Bright and Beautiful吧？",
        two_yuewen_end="系唔系AllThingsBrightand",
        yuewen_to_distribute="咁Ballana噉",
        one_yuewen_to_append="咁Ballana噉",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="是All Things Bright and Beautiful吧？",
        one_yuewen_start="系唔系AllThingsBrightand",
        two_zhongwen="是的，一切都好！",
        two_yuewen_end="系呀",
        yuewen_to_distribute="Beautiful呀",
        one_yuewen_to_append="Beautiful呀",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="是的，一切都好！",
        one_yuewen_start="系呀",
        two_zhongwen="世上一切，一切一切⋯",
        two_yuewen_end="",
        yuewen_to_distribute="所有嘢都几好喇",
        one_yuewen_to_append="所有嘢都几好喇",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="世上一切，一切一切⋯",
        one_yuewen_start="",
        two_zhongwen="所有那些，都好！",
        two_yuewen_end="所有𠮶啲嘢都几好AllThingsBrightandBeautiful",
        yuewen_to_distribute="世上一切",
        one_yuewen_to_append="世上一切",
        two_yuewen_to_prepend="",
    ),
]  # distribute_test_cases_block_7
distribute_test_cases_block_8 = [
    DistributeTestCase(
        one_zhongwen="这位喊得特劲的中年母猪",
        one_yuewen_start="",
        two_zhongwen="就是我妈妈麦太",
        two_yuewen_end="麦太",
        yuewen_to_distribute="呢个嗌得特别劲嘅中年母猪就系我妈妈",
        one_yuewen_to_append="呢个嗌得特别劲嘅中年母猪",
        two_yuewen_to_prepend="就系我妈妈",
    ),
    DistributeTestCase(
        one_zhongwen="这位喊得特劲的中年母猪",
        one_yuewen_start="",
        two_zhongwen="就是我妈妈麦太",
        two_yuewen_end="就系我妈妈麦太",
        yuewen_to_distribute="呢个嗌得特别劲嘅中年母猪",
        one_yuewen_to_append="呢个嗌得特别劲嘅中年母猪",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="我妈妈真的很劲",
        one_yuewen_start="",
        two_zhongwen="一个女人背起整个世界！",
        two_yuewen_end="一个女人揹起成个世界",
        yuewen_to_distribute="我妈妈真系好劲呀",
        one_yuewen_to_append="我妈妈真系好劲呀",
        two_yuewen_to_prepend="",
    ),
]  # distribute_test_cases_block_8
distribute_test_cases_block_9 = [
    DistributeTestCase(
        one_zhongwen="将鸡包底部的纸撕下来⋯慢慢地撕",
        one_yuewen_start="我哋将黐喺鸡包底嘅纸撕出嚟",
        two_zhongwen="就会得到一张鸡包纸",
        two_yuewen_end="咁就会得到一张鸡包纸喇",
        yuewen_to_distribute="慢慢撕",
        one_yuewen_to_append="慢慢撕",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="今日为大家介绍一个⋯",
        one_yuewen_start="",
        two_zhongwen="简单别致的小菜纸包鸡",
        two_yuewen_end="简单又别致嘅小菜自包鸡",
        yuewen_to_distribute="今日我为大家介绍个",
        one_yuewen_to_append="今日我为大家介绍个",
        two_yuewen_to_prepend="",
    ),
]  # distribute_test_cases_block_9
distribute_test_cases_block_10 = []  # distribute_test_cases_block_10
distribute_test_cases_block_11 = []  # distribute_test_cases_block_11
distribute_test_cases_block_12 = [
    DistributeTestCase(
        one_zhongwen="今日为大家介绍一味⋯",
        one_yuewen_start="",
        two_zhongwen="小朋友一定喜欢的⋯",
        two_yuewen_end="小朋友一定喜欢嘅",
        yuewen_to_distribute="今日要同大家介绍一味",
        one_yuewen_to_append="今日要同大家介绍一味",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="鸡包包鸡包包鸡包纸包纸⋯",
        one_yuewen_start="鸡包包鸡包包鸡包纸包",
        two_zhongwen="包鸡包鸡包纸包鸡",
        two_yuewen_end="包包鸡纸包鸡包纸包鸡",
        yuewen_to_distribute="纸包鸡",
        one_yuewen_to_append="纸包鸡",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="只要将鸡包包住个鸡包",
        one_yuewen_start="我哋先将鸡包",
        two_zhongwen="再包住个鸡包⋯",
        two_yuewen_end="",
        yuewen_to_distribute="包住个鸡包",
        one_yuewen_to_append="包住个鸡包",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="再包住个鸡包⋯",
        one_yuewen_start="",
        two_zhongwen="包住张鸡包纸",
        two_yuewen_end="包住张鸡包纸",
        yuewen_to_distribute="再包住个鸡包",
        one_yuewen_to_append="再包住个鸡包",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="再包包包包包住个纸鸡包",
        one_yuewen_start="再包包包包",
        two_zhongwen="再包包包，纸纸纸",
        two_yuewen_end="再包包包包包鸡包纸包纸",
        yuewen_to_distribute="包住个纸包鸡",
        one_yuewen_to_append="包住个纸包鸡",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="再包包包，纸纸纸",
        one_yuewen_start="再包包包包包鸡包纸包纸",
        two_zhongwen="纸包纸，纸包鸡，鸡包纸，纸包鸡⋯",
        two_yuewen_end="纸包纸纸包鸡包鸡纸纸包鸡鸡鸡鸡纸纸纸再包鸡鸡",
        yuewen_to_distribute="纸纸纸纸",
        one_yuewen_to_append="纸纸纸纸",
        two_yuewen_to_prepend="",
    ),
]  # distribute_test_cases_block_12
distribute_test_cases_block_13 = [
    DistributeTestCase(
        one_zhongwen="对她，一、二、三、四、五、六、七",
        one_yuewen_start="",
        two_zhongwen="没有不成的事",
        two_yuewen_end="字幕由Amara.org",
        yuewen_to_distribute="佢一二三四五六七唔得都要得",
        one_yuewen_to_append="佢一二三四五六七",
        two_yuewen_to_prepend="唔得都要得",
    ),
]  # distribute_test_cases_block_13
distribute_test_cases_block_14 = [
    DistributeTestCase(
        one_zhongwen="至于好运⋯",
        one_yuewen_start="",
        two_zhongwen="我用一双童子手替妈妈抽的六合彩号码",
        two_yuewen_end="我用我嘅同事手帮妈妈抽嘅六合彩number",
        yuewen_to_distribute="至于好运",
        one_yuewen_to_append="至于好运",
        two_yuewen_to_prepend="",
    ),
]  # distribute_test_cases_block_14
distribute_test_cases_block_15 = [
    DistributeTestCase(
        one_zhongwen="充满赤道活力的原始海洋，脱离繁嚣",
        one_yuewen_start="充满住赤道热力嘅原始海洋",
        two_zhongwen="体验热情如火的风土人情",
        two_yuewen_end="体验热情如火嘅风土人情",
        yuewen_to_distribute="远离凡嚣",
        one_yuewen_to_append="远离凡嚣",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="很远的",
        one_yuewen_start="",
        two_zhongwen="有多远？",
        two_yuewen_end="点远发呀",
        yuewen_to_distribute="啊好远㗎",
        one_yuewen_to_append="啊好远㗎",
        two_yuewen_to_prepend="",
    ),
]  # distribute_test_cases_block_15
distribute_test_cases_block_16 = [
    DistributeTestCase(
        one_zhongwen="那儿蓝天白云，椰林树影，水清沙幼",
        one_yuewen_start="𠮶度南天白云夜临树影",
        two_zhongwen="座落于印度洋的世外桃源",
        two_yuewen_end="独来鱼印度洋嘅世外桃源",
        yuewen_to_distribute="水清沙幽",
        one_yuewen_to_append="水清沙幽",
        two_yuewen_to_prepend="",
    ),
]  # distribute_test_cases_block_16
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
distribute_test_cases_block_18 = [
    DistributeTestCase(
        one_zhongwen="医生，吃了药会不会有那个什么的？",
        one_yuewen_start="医生啊",
        two_zhongwen="不会！",
        two_yuewen_end="唔会",
        yuewen_to_distribute="啲药食咗会唔会有𠮶啲咩㗎",
        one_yuewen_to_append="啲药食咗会唔会有𠮶啲咩㗎",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="那么吃药用不用那个什么的？",
        one_yuewen_start="",
        two_zhongwen="不用！给他打口针吧！",
        two_yuewen_end="唔使同佢打多支针添呢",
        yuewen_to_distribute="噉佢食药使唔使咩啊",
        one_yuewen_to_append="噉佢食药使唔使咩啊",
        two_yuewen_to_prepend="",
    ),
]  # distribute_test_cases_block_18
distribute_test_cases_block_19 = [
    DistributeTestCase(
        one_zhongwen="不要呀妈妈，我不喝呀",
        one_yuewen_start="唔好捞妈妈",
        two_zhongwen="我不喝士多啤梨药水呀！",
        two_yuewen_end="我唔食士多啤梨药水呀",
        yuewen_to_distribute="我唔食呀",
        one_yuewen_to_append="我唔食呀",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="真的吗？",
        one_yuewen_start="",
        two_zhongwen="妈妈什么时候骗过你？",
        two_yuewen_end="妈妈几时呃过你呀",
        yuewen_to_distribute="真嘅",
        one_yuewen_to_append="真嘅",
        two_yuewen_to_prepend="",
    ),
]  # distribute_test_cases_block_19
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
distribute_test_cases_block_22 = [
    DistributeTestCase(
        one_zhongwen="妈妈呀⋯",
        one_yuewen_start="",
        two_zhongwen="什么事？",
        two_yuewen_end="乜嘢啊",
        yuewen_to_distribute="妈妈",
        one_yuewen_to_append="妈妈",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="马尔代夫，椰林树影，水清沙幼⋯",
        one_yuewen_start="马尔代夫呢耶南树影",
        two_zhongwen="座落于印度洋的世外桃源呀！",
        two_yuewen_end="助流于印度园嘅世外导演啦",
        yuewen_to_distribute="水清沙游",
        one_yuewen_to_append="水清沙游",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="我病好了带我去马尔代夫的！",
        one_yuewen_start="你话我病好咗之日就同我去马尔代夫㗎",
        two_zhongwen="我是说发了财就带你去",
        two_yuewen_end="我话发咗先至同你去㗎",
        yuewen_to_distribute="你讲过㗎",
        one_yuewen_to_append="你讲过㗎",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="好了，别哭了",
        one_yuewen_start="得啦得啦",
        two_zhongwen="带你去马尔代夫好了",
        two_yuewen_end="同你去马尔代夫啦",
        yuewen_to_distribute="唔好喊啦",
        one_yuewen_to_append="唔好喊啦",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="真的吗？　　对",
        one_yuewen_start="真嘅",
        two_zhongwen="什么时候去？",
        two_yuewen_end="",
        yuewen_to_distribute="系啊",
        one_yuewen_to_append="系啊",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="什么时候去？",
        one_yuewen_start="",
        two_zhongwen="发财再说",
        two_yuewen_end="等我发咗先啰",
        yuewen_to_distribute="咁几时去啊",
        one_yuewen_to_append="咁几时去啊",
        two_yuewen_to_prepend="",
    ),
]  # distribute_test_cases_block_22
distribute_test_cases_block_23 = [
    DistributeTestCase(
        one_zhongwen="快点帮手执行李",
        one_yuewen_start="哦快啲嚟执埋啲行李先啦",
        two_zhongwen="跟我向他们说，我明天去马尔代夫了",
        two_yuewen_end="你帮我话畀佢哋知我明日去买热带裤薄",
        yuewen_to_distribute="哦",
        one_yuewen_to_append="哦",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="要执行李了，回来再跟你说吧",
        one_yuewen_start="我要执行你喇",
        two_zhongwen="再见！",
        two_yuewen_end="拜拜",
        yuewen_to_distribute="返嚟先再同你倾过啦",
        one_yuewen_to_append="返嚟先再同你倾过啦",
        two_yuewen_to_prepend="",
    ),
]  # distribute_test_cases_block_23
distribute_test_cases_block_24 = [
    DistributeTestCase(
        one_zhongwen="那么成绩表呢？",
        one_yuewen_start="都要㗎",
        two_zhongwen="成绩表就不用了",
        two_yuewen_end="成绩表又唔使",
        yuewen_to_distribute="咁成绩表呢",
        one_yuewen_to_append="咁成绩表呢",
        two_yuewen_to_prepend="",
    ),
]  # distribute_test_cases_block_24
distribute_test_cases_block_25 = [
    DistributeTestCase(
        one_zhongwen="妈妈你替我收好它别抛掉",
        one_yuewen_start="",
        two_zhongwen="抛掉就去不成了",
        two_yuewen_end="",
        yuewen_to_distribute="竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然",
        one_yuewen_to_append="竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然竟然",
        two_yuewen_to_prepend="",
    ),
]  # distribute_test_cases_block_25
distribute_test_cases_block_26 = []  # distribute_test_cases_block_26
distribute_test_cases_block_27 = []  # distribute_test_cases_block_27
distribute_test_cases_block_28 = [
    DistributeTestCase(
        one_zhongwen="奥运滑浪风帆选手李丽珊五场四胜",
        one_yuewen_start="",
        two_zhongwen="夺得香港历史上第一面奥运金牌！",
        two_yuewen_end="",
        yuewen_to_distribute="奥运滑浪风帆选手李丽珊以五场四胜嘅结果夺取香港历史上第一面奥运金牌",
        one_yuewen_to_append="奥运滑浪风帆选手李丽珊以五场四胜嘅结果",
        two_yuewen_to_prepend="夺取香港历史上第一面奥运金牌",
    ),
    DistributeTestCase(
        one_zhongwen="消息说当李丽珊获悉自己稳夺金牌后",
        one_yuewen_start="",
        two_zhongwen="激动地对在场记者表示她今次的成绩⋯",
        two_yuewen_end="",
        yuewen_to_distribute="消息话李丽珊喺知道自己稳夺奥运金牌之后好激动噉同在场嘅记者讲",
        one_yuewen_to_append="消息话李丽珊喺知道自己稳夺奥运金牌之后",
        two_yuewen_to_prepend="好激动噉同在场嘅记者讲",
    ),
    DistributeTestCase(
        one_zhongwen="对不起，应该　　是垃圾，不是腊鸭！",
        one_yuewen_start="各位对唔住应该系垃圾",
        two_zhongwen="对不起，应该　　不是垃圾，也不是腊鸭！",
        two_yuewen_end="对唔住应该系唔系垃圾亦都唔系𫚭鸭",
        yuewen_to_distribute="唔系𫚭鸭",
        one_yuewen_to_append="唔系𫚭鸭",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="激动地对在场记者表示她今次的成绩⋯",
        one_yuewen_start="好激动噉同在场嘅记者讲",
        two_zhongwen="足以证明香港运动员不是腊鸭！",
        two_yuewen_end="可以证明到香港嘅运动员唔系𫚭鸭",
        yuewen_to_distribute="今次佢嘅成绩",
        one_yuewen_to_append="今次佢嘅成绩",
        two_yuewen_to_prepend="",
    ),
]  # distribute_test_cases_block_28
distribute_test_cases_block_29 = [
    DistributeTestCase(
        one_zhongwen="靓仔，好运，叻仔⋯",
        one_yuewen_start="靓仔好运",
        two_zhongwen="好像都没希望了",
        two_yuewen_end="睇嚟都唔多靠得住",
        yuewen_to_distribute="叻仔呀",
        one_yuewen_to_append="叻仔呀",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="于是，一个梦还没醒⋯",
        one_yuewen_start="于是",
        two_zhongwen="我又得到另一个梦",
        two_yuewen_end="我又得到另外一个梦",
        yuewen_to_distribute="一个梦都未醒",
        one_yuewen_to_append="一个梦都未醒",
        two_yuewen_to_prepend="",
    ),
]  # distribute_test_cases_block_29
distribute_test_cases_block_30 = []  # distribute_test_cases_block_30
distribute_test_cases_block_31 = [
    DistributeTestCase(
        one_zhongwen="当我站在奥运会颁奖台上",
        one_yuewen_start="",
        two_zhongwen="我会举起金牌跟全世界说：",
        two_yuewen_end="系今排同全世界讲",
        yuewen_to_distribute="三张堂上面",
        one_yuewen_to_append="三张堂上面",
        two_yuewen_to_prepend="",
    ),
]  # distribute_test_cases_block_31
distribute_test_cases_block_32 = []  # distribute_test_cases_block_32
distribute_test_cases_block_33 = []  # distribute_test_cases_block_33
distribute_test_cases_block_34 = []  # distribute_test_cases_block_34
distribute_test_cases_block_35 = [
    DistributeTestCase(
        one_zhongwen="你们这些住香港岛的小朋友骄生惯养",
        one_yuewen_start="",
        two_zhongwen="怎么吃得苦？",
        two_yuewen_end="",
        yuewen_to_distribute="你哋呢班住喺香港岛嘅小朋友娇生惯养边挨得苦㗎",
        one_yuewen_to_append="你哋呢班住喺香港岛嘅小朋友娇生惯养",
        two_yuewen_to_prepend="边挨得苦㗎",
    ),
    DistributeTestCase(
        one_zhongwen="想跟珊珊般得奥运金牌？",
        one_yuewen_start="",
        two_zhongwen="别作梦了！",
        two_yuewen_end="",
        yuewen_to_distribute="想学山伞攞奥运金牌食母你嘢",
        one_yuewen_to_append="想学山伞攞奥运金牌",
        two_yuewen_to_prepend="食母你嘢",
    ),
]  # distribute_test_cases_block_35
distribute_test_cases_block_36 = []  # distribute_test_cases_block_36
distribute_test_cases_block_37 = [
    DistributeTestCase(
        one_zhongwen="脚趾甲有一寸厚，究竟⋯",
        one_yuewen_start="脚趾弓啲脚甲成吋噉厚",
        two_zhongwen="要行过几多座山⋯",
        two_yuewen_end="要行我几多座山",
        yuewen_to_distribute="究竟",
        one_yuewen_to_append="究竟",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="跨过几多个海⋯",
        one_yuewen_start="",
        two_zhongwen="吃过几多苦头⋯",
        two_yuewen_end="",
        yuewen_to_distribute="跨我几多个海",
        one_yuewen_to_append="跨我几多个海",
        two_yuewen_to_prepend="",
    ),
    DistributeTestCase(
        one_zhongwen="吃过几多苦头⋯",
        one_yuewen_start="",
        two_zhongwen="才可以练成这举世无双的脚瓜？",
        two_yuewen_end="先至可以练成呢只举世无双嘅脚瓜",
        yuewen_to_distribute="挨过几多苦头",
        one_yuewen_to_append="挨过几多苦头",
        two_yuewen_to_prepend="",
    ),
]  # distribute_test_cases_block_37
distribute_test_cases_block_38 = []  # distribute_test_cases_block_38
distribute_test_cases_block_39 = []  # distribute_test_cases_block_39
distribute_test_cases_block_40 = []  # distribute_test_cases_block_40
distribute_test_cases_block_41 = []  # distribute_test_cases_block_41
distribute_test_cases_block_42 = []  # distribute_test_cases_block_42
distribute_test_cases_block_43 = [
    DistributeTestCase(
        one_zhongwen="希望他把长洲人世世代代的绝技",
        one_yuewen_start="",
        two_zhongwen="发扬光大！",
        two_yuewen_end="",
        yuewen_to_distribute="希望我可以将我哋长洲人世世代代嘅传统发扬光大",
        one_yuewen_to_append="希望我可以将我哋长洲人世世代代嘅传统",
        two_yuewen_to_prepend="发扬光大",
    ),
]  # distribute_test_cases_block_43
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
