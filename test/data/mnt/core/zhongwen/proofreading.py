"""中文 proof test cases."""

#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.

from __future__ import annotations

from scinoephile.core.zhongwen.proofreading import ZhongwenProofreadingTestCase

# noinspection PyArgumentList
test_case_block_0 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="《龙猫》",
    verified=True,
)  # test_case_block_0
# noinspection PyArgumentList
test_case_block_1 = ZhongwenProofreadingTestCase.get_test_case_cls(4)(
    zimu_1="爸爸，牛奶糖",
    zimu_2="谢谢",
    zimu_3="你们两个累不累啊",
    zimu_4="就快到了",
    verified=True,
)  # test_case_block_1
# noinspection PyArgumentList
test_case_block_2 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="小美，快躲起来",
    verified=True,
)  # test_case_block_2
# noinspection PyArgumentList
test_case_block_3 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="还以为是警察呢！",
    verified=True,
)  # test_case_block_3
# noinspection PyArgumentList
test_case_block_4 = ZhongwenProofreadingTestCase.get_test_case_cls(5)(
    zimu_1="有没有人在家啊？",
    zimu_2="谢谢",
    zimu_3="我姓草壁\n新搬来的",
    zimu_4="请多关照",
    zimu_5="搬家辛苦了",
    verified=True,
)  # test_case_block_4
# noinspection PyArgumentList
test_case_block_5 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="谢谢你",
    verified=True,
)  # test_case_block_5
# noinspection PyArgumentList
test_case_block_6 = ZhongwenProofreadingTestCase.get_test_case_cls(4)(
    zimu_1="好，到了",
    zimu_2="等等我吧",
    zimu_3="小美，有座桥啊",
    zimu_4="有桥？",
    verified=True,
)  # test_case_block_6
# noinspection PyArgumentList
test_case_block_7 = ZhongwenProofreadingTestCase.get_test_case_cls(4)(
    zimu_1="有鱼呢，又闪了一下",
    zimu_2="怎么样？喜不喜欢？",
    zimu_3="爸爸，这里好棒啊",
    zimu_4="树林中还有隧道啊",
    verified=True,
)  # test_case_block_7
# noinspection PyArgumentList
test_case_block_8 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="那就是新家吗？",
    verified=True,
)  # test_case_block_8
# noinspection PyArgumentList
test_case_block_9 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="跑快一点！",
    verified=True,
)  # test_case_block_9
# noinspection PyArgumentList
test_case_block_10 = ZhongwenProofreadingTestCase.get_test_case_cls(4)(
    zimu_1="很旧啊",
    zimu_2="很旧啊",
    zimu_3="好像一间鬼屋",
    zimu_4="鬼屋",
    verified=True,
)  # test_case_block_10
# noinspection PyArgumentList
test_case_block_11 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="柱子烂掉了",
    verified=True,
)  # test_case_block_11
# noinspection PyArgumentList
test_case_block_12 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="要倒了！",
    zimu_2="要倒了！",
    verified=True,
)  # test_case_block_12
# noinspection PyArgumentList
test_case_block_13 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="小美，妳看",
    zimu_2="妳看",
    verified=True,
)  # test_case_block_13
# noinspection PyArgumentList
test_case_block_14 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="好大啊",
    verified=True,
)  # test_case_block_14
# noinspection PyArgumentList
test_case_block_15 = ZhongwenProofreadingTestCase.get_test_case_cls(4)(
    zimu_1="爸爸，好大的树啊",
    zimu_2="那叫做樟树",
    zimu_3="樟树呢",
    zimu_4="樟树",
    verified=True,
)  # test_case_block_15
# noinspection PyArgumentList
test_case_block_16 = ZhongwenProofreadingTestCase.get_test_case_cls(3)(
    zimu_1="橡果子",
    zimu_2="我看一下",
    zimu_3="那里也有",
    verified=True,
)  # test_case_block_16
# noinspection PyArgumentList
test_case_block_17 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="捡到了",
    verified=True,
)  # test_case_block_17
# noinspection PyArgumentList
test_case_block_18 = ZhongwenProofreadingTestCase.get_test_case_cls(4)(
    zimu_1="别玩了\n这样木门打不开",
    zimu_2="橡果子",
    zimu_3="有很多橡果子掉到屋里",
    zimu_4="从上面掉下来的",
    verified=True,
)  # test_case_block_18
# noinspection PyArgumentList
test_case_block_19 = ZhongwenProofreadingTestCase.get_test_case_cls(12)(
    zimu_1="该不会是我们家有松鼠吧",
    zimu_2="松鼠？",
    zimu_3="还是\n吃橡果子的老鼠呢？",
    zimu_4="我喜欢松鼠",
    zimu_5="这要搬到哪儿呢？",
    zimu_6="放这里，我这就开门",
    zimu_7="小月，你去把后门打开",
    zimu_8="好",
    zimu_9="去了就看得到",
    zimu_10="快点",
    zimu_11="等人家嘛",
    zimu_12="快点",
    xiugai_3="还是吃橡果子的老鼠呢？",
    beizhu_3="去除“\\n”换行符，修正OCR误识。",
    difficulty=1,
)  # test_case_block_19
# noinspection PyArgumentList
test_case_block_20 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="进去罗",
    xiugai_1="进去咯",
    beizhu_1="将“罗”改为“咯”，修正错别字。",
    difficulty=1,
)  # test_case_block_20
# noinspection PyArgumentList
test_case_block_21 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="浴室",
    verified=True,
)  # test_case_block_21
# noinspection PyArgumentList
test_case_block_22 = ZhongwenProofreadingTestCase.get_test_case_cls(7)(
    zimu_1="不见了",
    zimu_2="这间是浴室",
    zimu_3="爸爸，有怪东西",
    zimu_4="松鼠吗？",
    zimu_5="不知道",
    zimu_6="不像蟑螂也不像老鼠",
    zimu_7="只知道是一堆黑色的东西",
    verified=True,
)  # test_case_block_22
# noinspection PyArgumentList
test_case_block_23 = ZhongwenProofreadingTestCase.get_test_case_cls(6)(
    zimu_1="有没有？",
    zimu_2="那一定是＂灰尘精灵＂",
    zimu_3="灰尘精灵",
    zimu_4="画册里有吗？",
    zimu_5="有啊",
    zimu_6="今天天气那么好\n不可能会有鬼的",
    xiugai_2="那一定是“灰尘精灵”",
    beizhu_2="将“＂”改为“””，修正引号为中文全角引号。",
    difficulty=1,
)  # test_case_block_23
# noinspection PyArgumentList
test_case_block_24 = ZhongwenProofreadingTestCase.get_test_case_cls(5)(
    zimu_1="我们从光的地方\n一下子进到暗的地方",
    zimu_2="眼睛就会发昏\n灰尘精灵就会跑出来",
    zimu_3="原来是这样啊",
    zimu_4="灰尘精灵快点滚出来",
    zimu_5="你要躲着不出来\n我就把你眼睛挖出来！",
    verified=True,
)  # test_case_block_24
# noinspection PyArgumentList
test_case_block_25 = ZhongwenProofreadingTestCase.get_test_case_cls(6)(
    zimu_1="好了，去做事",
    zimu_2="上二楼的楼梯\n到底在哪里呢？",
    zimu_3="你们两个去把楼梯找出来",
    zimu_4="然后把二楼的窗户打开",
    zimu_5="好",
    zimu_6="人家也要",
    verified=True,
)  # test_case_block_25
# noinspection PyArgumentList
test_case_block_26 = ZhongwenProofreadingTestCase.get_test_case_cls(3)(
    zimu_1="厕所",
    zimu_2="甚么？",
    zimu_3="甚么？",
    verified=True,
)  # test_case_block_26
# noinspection PyArgumentList
test_case_block_27 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="甚么？",
    zimu_2="甚么？",
    verified=True,
)  # test_case_block_27
# noinspection PyArgumentList
test_case_block_28 = ZhongwenProofreadingTestCase.get_test_case_cls(3)(
    zimu_1="甚么？",
    zimu_2="没有",
    zimu_3="没有",
    verified=True,
)  # test_case_block_28
# noinspection PyArgumentList
test_case_block_29 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="小美，找到了",
    verified=True,
)  # test_case_block_29
# noinspection PyArgumentList
test_case_block_30 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="乌漆抹黑的",
    zimu_2="灰尘精灵呢？",
    verified=True,
)  # test_case_block_30
# noinspection PyArgumentList
test_case_block_31 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="橡果子",
    verified=True,
)  # test_case_block_31
# noinspection PyArgumentList
test_case_block_32 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="灰尘精灵快点滚出来",
    verified=True,
)  # test_case_block_32
# noinspection PyArgumentList
test_case_block_33 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="灰尘精灵",
    zimu_2="你在不在？",
    verified=True,
)  # test_case_block_33
# noinspection PyArgumentList
test_case_block_34 = ZhongwenProofreadingTestCase.get_test_case_cls(3)(
    zimu_1="爸爸，真的有怪东西",
    zimu_2="那真是太棒了",
    zimu_3="爸爸从小就梦想\n能够住在鬼屋里面",
    xiugai_3="爸爸从小就梦想能够住在鬼屋里面",
    beizhu_3="去除“梦想”与“能够住在鬼屋里面”之间的换行符，修正换行错误。",
    difficulty=1,
)  # test_case_block_34
# noinspection PyArgumentList
test_case_block_35 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="糟了",
    verified=True,
)  # test_case_block_35
# noinspection PyArgumentList
test_case_block_36 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="抓到了！姐姐",
    verified=True,
)  # test_case_block_36
# noinspection PyArgumentList
test_case_block_37 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="小美",
    verified=True,
)  # test_case_block_37
# noinspection PyArgumentList
test_case_block_38 = ZhongwenProofreadingTestCase.get_test_case_cls(17)(
    zimu_1="好活泼啊",
    zimu_2="这位是一直照顾这个家",
    zimu_3="住在隔壁的婆婆",
    zimu_4="婆婆今天是来帮忙的",
    zimu_5="我叫做小月，这是我妹妹小美",
    zimu_6="婆婆好",
    zimu_7="好，你们好啊",
    zimu_8="这孩子真是聪明伶俐",
    zimu_9="如果你们不急着搬进来",
    zimu_10="我还打算请人先收拾一下呢",
    zimu_11="这样子已经很好了",
    zimu_12="现在这时田里农事很忙碌呢",
    zimu_13="不过我还是偶尔会来打扫",
    zimu_14="小美，妳手怎么脏兮兮的？",
    zimu_15="怎么弄的？",
    zimu_16="灰尘精灵跑掉了",
    zimu_17="妳看妳的脚",
    verified=True,
)  # test_case_block_38
# noinspection PyArgumentList
test_case_block_39 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="我的脚也脏兮兮的",
    zimu_2="哎呀呀！",
    verified=True,
)  # test_case_block_39
# noinspection PyArgumentList
test_case_block_40 = ZhongwenProofreadingTestCase.get_test_case_cls(14)(
    zimu_1="看样子是煤煤虫在作怪",
    zimu_2="煤煤虫？",
    zimu_3="你说的煤煤虫是不是会",
    zimu_4="＂哇啦哇啦＂的乱跑啊",
    zimu_5="是啊",
    zimu_6="它们专门跑到没人住的旧房子里",
    zimu_7="然后弄得满屋子的灰尘和煤灰",
    zimu_8="我小时候也有看过",
    zimu_9="想不到妳们也看到",
    zimu_10="婆婆，它们是妖怪吗？",
    zimu_11="其实也没什么好怕的",
    zimu_12="只要对它们笑笑\n它们就不会害人",
    zimu_13="住上一阵子之后\n它们自然就会不见",
    zimu_14="说不定它们已经在天花板上\n讨论该搬去哪里了",
    xiugai_9="想不到你们也看到",
    beizhu_9="将“妳们”改为“你们”，修正错别字。",
    difficulty=1,
)  # test_case_block_40
# noinspection PyArgumentList
test_case_block_41 = ZhongwenProofreadingTestCase.get_test_case_cls(10)(
    zimu_1="小美，它们很快就会不见了",
    zimu_2="不好玩",
    zimu_3="可是要是来这么一大堆\n该怎么办？",
    zimu_4="人家才不怕那些",
    zimu_5="是吗？",
    zimu_6="那以后晚上\n姐姐就不陪妳上厕所",
    zimu_7="来来⋯快来打扫吧",
    zimu_8="妳们去河边打点水回来吧",
    zimu_9="河边啊",
    zimu_10="人家也要去",
    verified=True,
)  # test_case_block_41
# noinspection PyArgumentList
test_case_block_42 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="小美，妳在一边等着",
    verified=True,
)  # test_case_block_42
# noinspection PyArgumentList
test_case_block_43 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="有没有抓到鱼？",
    verified=True,
)  # test_case_block_43
# noinspection PyArgumentList
test_case_block_44 = ZhongwenProofreadingTestCase.get_test_case_cls(4)(
    zimu_1="婆婆，有水了",
    zimu_2="好好打啊",
    zimu_3="打到水变凉为止",
    zimu_4="好",
    verified=True,
)  # test_case_block_44
# noinspection PyArgumentList
test_case_block_45 = ZhongwenProofreadingTestCase.get_test_case_cls(3)(
    zimu_1="你不是刚刚那个吗？\n有事吗",
    zimu_2="我妈妈要给婆婆的",
    zimu_3="是什么？",
    verified=True,
)  # test_case_block_45
# noinspection PyArgumentList
test_case_block_46 = ZhongwenProofreadingTestCase.get_test_case_cls(4)(
    zimu_1="等等，这是什么啊",
    zimu_2="是勘太吗？",
    zimu_3="你们家是可怕的大鬼屋",
    zimu_4="勘太！",
    verified=True,
)  # test_case_block_46
# noinspection PyArgumentList
test_case_block_47 = ZhongwenProofreadingTestCase.get_test_case_cls(7)(
    zimu_1="爸爸以前也这样作弄过女生",
    zimu_2="男生最讨人厌了",
    zimu_3="不过\n婆婆这个糯米团很好吃",
    zimu_4="那便多吃点啊",
    zimu_5="婆婆，谢谢您的糯米团",
    zimu_6="真是太谢谢您了",
    zimu_7="婆婆再见",
    xiugai_3="不过，婆婆这个糯米团很好吃",
    beizhu_3="将“不过\\n婆婆这个糯米团很好吃”中的换行符改为逗号，修正OCR识别错误。",
    difficulty=1,
)  # test_case_block_47
# noinspection PyArgumentList
test_case_block_48 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="爸爸，我们家\n破破烂烂的会否倒下来",
    zimu_2="要是才刚搬来就倒塌\n那可怎么得了",
    verified=True,
)  # test_case_block_48
# noinspection PyArgumentList
test_case_block_49 = ZhongwenProofreadingTestCase.get_test_case_cls(4)(
    zimu_1="我们一起大笑看看",
    zimu_2="可怕的东西就会跑光",
    zimu_3="人家才不怕呢！",
    zimu_4="人家才不怕呢！",
    verified=True,
)  # test_case_block_49
# noinspection PyArgumentList
test_case_block_50 = ZhongwenProofreadingTestCase.get_test_case_cls(3)(
    zimu_1="一\n﹣",
    zimu_2="很好，加油",
    zimu_3="用力，加把劲",
    xiugai_1="一﹣",
    beizhu_1="去除换行符，将“一\\n﹣”合并为“一﹣”。",
    difficulty=1,
)  # test_case_block_50
# noinspection PyArgumentList
test_case_block_51 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="好了\n衣服都洗好了",
    verified=True,
)  # test_case_block_51
# noinspection PyArgumentList
test_case_block_52 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="出发了！",
    verified=True,
)  # test_case_block_52
# noinspection PyArgumentList
test_case_block_53 = ZhongwenProofreadingTestCase.get_test_case_cls(8)(
    zimu_1="婆婆",
    zimu_2="您好！！",
    zimu_3="您可真忙啊",
    zimu_4="三个一起出门啊？",
    zimu_5="我们要去医院看妈妈",
    zimu_6="可有好一段路呢",
    zimu_7="替我帮你们妈妈问好",
    zimu_8="好的",
    verified=True,
)  # test_case_block_53
# noinspection PyArgumentList
test_case_block_54 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="走这边！走这边！",
    verified=True,
)  # test_case_block_54
# noinspection PyArgumentList
test_case_block_55 = ZhongwenProofreadingTestCase.get_test_case_cls(13)(
    zimu_1="大家好",
    zimu_2="妳好",
    zimu_3="妈妈！",
    zimu_4="小美妳也来啦",
    zimu_5="爸爸还走错路呢",
    zimu_6="真的吗",
    zimu_7="妳也来啦",
    zimu_8="今天田里休息一天",
    zimu_9="是啊",
    zimu_10="爸爸正在跟医生说话",
    zimu_11="妈妈很高兴你们都来了",
    zimu_12="新家怎么样啦",
    zimu_13="都整理好了没？",
    xiugai_2="你好",
    beizhu_2="将“妳好”改为“你好”，修正错别字。",
    xiugai_4="小美你也来啦",
    beizhu_4="将“妳”改为“你”，修正错别字。",
    xiugai_7="你也来啦",
    beizhu_7="将“妳”改为“你”，修正错别字。",
    difficulty=1,
)  # test_case_block_55
# noinspection PyArgumentList
test_case_block_56 = ZhongwenProofreadingTestCase.get_test_case_cls(26)(
    zimu_1="甚么？我们家是鬼屋啊",
    zimu_2="妈妈喜欢住鬼屋吗？",
    zimu_3="当然罗",
    zimu_4="妈妈真想快点出院\n看看鬼长什么样子",
    zimu_5="小美太好了",
    zimu_6="我好担心啊",
    zimu_7="因为我好怕\n妈妈会不喜欢那里",
    zimu_8="那你们两个呢？",
    zimu_9="喜欢",
    zimu_10="妈妈我不怕鬼",
    zimu_11="小美的头发都是妳梳的？",
    zimu_12="梳得真好",
    zimu_13="要好好谢姐姐啊！小美",
    zimu_14="可是姐姐动不动就生气",
    zimu_15="还不都是因为你不乖",
    zimu_16="小月，过来让妈妈看看",
    zimu_17="你的头发会不会太短了",
    zimu_18="我喜欢这个样子",
    zimu_19="人家也要！人家也要！",
    zimu_20="排队！",
    zimu_21="头发还是一样经常打结",
    zimu_22="就跟妈妈小时候一样",
    zimu_23="那我长大以后",
    zimu_24="头发会不会\n变得跟妈妈的一样呢？",
    zimu_25="应该会吧",
    zimu_26="因为妳跟妈妈最像了",
    verified=True,
)  # test_case_block_56
# noinspection PyArgumentList
test_case_block_57 = ZhongwenProofreadingTestCase.get_test_case_cls(9)(
    zimu_1="妈妈好像好了很多",
    zimu_2="是啊",
    zimu_3="医生也说\n再过不久就可以出院了",
    zimu_4="再过不久，明天吗？",
    zimu_5="妳什么都是明天",
    zimu_6="明天可能有点难",
    zimu_7="可是人家好想要跟妈妈一起睡",
    zimu_8="妳不是说你已经长大\n要自己一个人睡的吗？",
    zimu_9="跟妈妈睡没关系",
    verified=True,
)  # test_case_block_57
# noinspection PyArgumentList
test_case_block_58 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="爸爸",
    zimu_2="天亮了",
    verified=True,
)  # test_case_block_58
# noinspection PyArgumentList
test_case_block_59 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="起床！",
    verified=True,
)  # test_case_block_59
# noinspection PyArgumentList
test_case_block_60 = ZhongwenProofreadingTestCase.get_test_case_cls(13)(
    zimu_1="对不起，爸爸又睡过头",
    zimu_2="今天开始要带便当",
    zimu_3="糟糕，爸爸忘记了",
    zimu_4="没关系，我也帮你们做好了",
    zimu_5="烧焦了",
    zimu_6="马上来",
    zimu_7="这是小美的",
    zimu_8="我的",
    zimu_9="小美，坐下来好好吃饭",
    zimu_10="来",
    zimu_11="便当自己包好",
    zimu_12="小月",
    zimu_13="糟了，来啊",
    verified=True,
)  # test_case_block_60
# noinspection PyArgumentList
test_case_block_61 = ZhongwenProofreadingTestCase.get_test_case_cls(8)(
    zimu_1="这么快就交到朋友啦？",
    zimu_2="叫得很真亲密呢",
    zimu_3="她叫小满",
    zimu_4="我吃饱了",
    zimu_5="我去上学了",
    zimu_6="路上小心啊",
    zimu_7="早",
    zimu_8="早，赶快走吧\n好",
    verified=True,
)  # test_case_block_61
# noinspection PyArgumentList
test_case_block_62 = ZhongwenProofreadingTestCase.get_test_case_cls(4)(
    zimu_1="爸爸！",
    zimu_2="你看我像不像姐姐",
    zimu_3="妳拿着便当要上哪儿去？",
    zimu_4="就在附近走走",
    verified=True,
)  # test_case_block_62
# noinspection PyArgumentList
test_case_block_63 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="爸爸，可以吃便当了吗？",
    zimu_2="一早就想吃呀？",
    verified=True,
)  # test_case_block_63
# noinspection PyArgumentList
test_case_block_64 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="爸爸你开花店了",
    verified=True,
)  # test_case_block_64
# noinspection PyArgumentList
test_case_block_65 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="小蝌蚪！",
    verified=True,
)  # test_case_block_65
# noinspection PyArgumentList
test_case_block_66 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="破了一个大洞",
    verified=True,
)  # test_case_block_66
# noinspection PyArgumentList
test_case_block_67 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="发现了",
    verified=True,
)  # test_case_block_67
# noinspection PyArgumentList
test_case_block_68 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="你是谁？",
    zimu_2="灰尘精灵吗？",
    verified=True,
)  # test_case_block_68
# noinspection PyArgumentList
test_case_block_69 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="龙猫！你叫做龙猫呀？",
    verified=True,
)  # test_case_block_69
# noinspection PyArgumentList
test_case_block_70 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="你一定就叫做大龙猫",
    verified=True,
)  # test_case_block_70
# noinspection PyArgumentList
test_case_block_71 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="大龙猫",
    verified=True,
)  # test_case_block_71
# noinspection PyArgumentList
test_case_block_72 = ZhongwenProofreadingTestCase.get_test_case_cls(12)(
    zimu_1="待会见",
    zimu_2="待会见",
    zimu_3="我回来了",
    zimu_4="妳回来啦",
    zimu_5="都已经这时间啦",
    zimu_6="小美呢？待会我要去小满家",
    zimu_7="爸爸还没吃便当呢",
    zimu_8="小美没有在院子里玩吗？",
    zimu_9="小美",
    zimu_10="小美",
    zimu_11="小美",
    zimu_12="小美",
    verified=True,
)  # test_case_block_72
# noinspection PyArgumentList
test_case_block_73 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="爸爸！\n小美的帽子掉在这里",
    verified=True,
)  # test_case_block_73
# noinspection PyArgumentList
test_case_block_74 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="小美！小美！",
    verified=True,
)  # test_case_block_74
# noinspection PyArgumentList
test_case_block_75 = ZhongwenProofreadingTestCase.get_test_case_cls(22)(
    zimu_1="小美！够了，快起来",
    zimu_2="妳干什么睡在这里！",
    zimu_3="大龙猫？",
    zimu_4="大龙猫？",
    zimu_5="怪了",
    zimu_6="你做梦啦",
    zimu_7="大龙猫刚才还在的",
    zimu_8="大龙猫？",
    zimu_9="你是说画册上那个大妖怪吗？",
    zimu_10="它的名字叫做大龙猫啊",
    zimu_11="它的毛好多啊",
    zimu_12="嘴巴是这样子的",
    zimu_13="有这么小的",
    zimu_14="还有这么大的",
    zimu_15="还有一只这么大的在睡觉",
    zimu_16="找到了",
    zimu_17="真是个好地方",
    zimu_18="简直像是个秘密基地一样",
    zimu_19="爸爸",
    zimu_20="小美说\n她看到一只大龙猫",
    zimu_21="大龙猫？",
    zimu_22="这边！",
    xiugai_2="你干什么睡在这里！",
    beizhu_2="将“妳”改为“你”，修正错别字。",
    difficulty=1,
)  # test_case_block_75
# noinspection PyArgumentList
test_case_block_76 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="你们两个等等我",
    verified=True,
)  # test_case_block_76
# noinspection PyArgumentList
test_case_block_77 = ZhongwenProofreadingTestCase.get_test_case_cls(5)(
    zimu_1="是这里吗？",
    zimu_2="它刚才\n睡在一棵很大的树里面",
    zimu_3="可是这里只有一条路啊",
    zimu_4="小美，你快回来啊",
    zimu_5="小美，回来啊",
    xiugai_2="它刚才睡在一棵很大的树里面",
    beizhu_2="去掉“它刚才\n睡在一棵很大的树里面”中的换行符，修正OCR换行错误。",
    difficulty=1,
)  # test_case_block_77
# noinspection PyArgumentList
test_case_block_78 = ZhongwenProofreadingTestCase.get_test_case_cls(3)(
    zimu_1="真的有啦",
    zimu_2="刚才真的有大龙猫",
    zimu_3="我没有骗你们",
    verified=True,
)  # test_case_block_78
# noinspection PyArgumentList
test_case_block_79 = ZhongwenProofreadingTestCase.get_test_case_cls(10)(
    zimu_1="小美啊",
    zimu_2="人家没有骗你们",
    zimu_3="其实爸爸跟姐姐",
    zimu_4="也没有认为妳在骗人啊",
    zimu_5="小美刚才一定是\n遇到了森林的主人",
    zimu_6="这就表示小美运气很好",
    zimu_7="不过这种机会并不常有",
    zimu_8="来，我们去跟它打个招呼吧",
    zimu_9="打招呼？",
    zimu_10="现在向大树出发了",
    verified=True,
)  # test_case_block_79
# noinspection PyArgumentList
test_case_block_80 = ZhongwenProofreadingTestCase.get_test_case_cls(3)(
    zimu_1="小美好像变重了",
    zimu_2="爸爸，你看那樟树",
    zimu_3="好大啊",
    verified=True,
)  # test_case_block_80
# noinspection PyArgumentList
test_case_block_81 = ZhongwenProofreadingTestCase.get_test_case_cls(3)(
    zimu_1="就是它！",
    zimu_2="是这棵吗？",
    zimu_3="爸爸，快来啊",
    verified=True,
)  # test_case_block_81
# noinspection PyArgumentList
test_case_block_82 = ZhongwenProofreadingTestCase.get_test_case_cls(31)(
    zimu_1="那个洞不见了",
    zimu_2="真的是这里吗？",
    zimu_3="小美她说洞不见了",
    zimu_4="所以我说啦",
    zimu_5="那不是想看\n随时就能看到的",
    zimu_6="还会再看得到吗？",
    zimu_7="我也好想看啊",
    zimu_8="那得碰运气",
    zimu_9="这棵树真大啊",
    zimu_10="一定是从很久很久以前",
    zimu_11="就已经长在这里的",
    zimu_12="很久很久以前",
    zimu_13="树木跟我们人的感情很好",
    zimu_14="爸爸就是因为看到这棵树",
    zimu_15="才会这么喜欢现在这个家的",
    zimu_16="而且知道\n妈妈一定也会喜欢这里",
    zimu_17="来，我们谢谢它再回家",
    zimu_18="该吃饭了",
    zimu_19="对了\n我跟小满约好要到她家去",
    zimu_20="人家也要去",
    zimu_21="立正站好！",
    zimu_22="多谢您照顾我们家小美",
    zimu_23="从今以后还盼您多多关照",
    zimu_24="请您多多关照",
    zimu_25="我们比赛看谁先到家",
    zimu_26="爸爸偷跑",
    zimu_27="等人家嘛",
    zimu_28="小美，快点",
    zimu_29="等人家嘛",
    zimu_30="妈妈，今天出了一件大新闻",
    zimu_31="因为小美说她看到了\n一只很大的龙猫精灵",
    verified=True,
)  # test_case_block_82
# noinspection PyArgumentList
test_case_block_83 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="我好希望我也能够见它一面",
    verified=True,
)  # test_case_block_83
# noinspection PyArgumentList
test_case_block_84 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="勘太",
    zimu_2="再不快点就要迟到了\n嗯",
    verified=True,
)  # test_case_block_84
# noinspection PyArgumentList
test_case_block_85 = ZhongwenProofreadingTestCase.get_test_case_cls(16)(
    zimu_1="小美",
    zimu_2="老师",
    zimu_3="什么事？小月",
    zimu_4="我妹妹",
    zimu_5="你们看，你们看，她妹妹",
    zimu_6="婆婆、小美？",
    zimu_7="对不起",
    zimu_8="她一直吵着\n要到姐姐那边去所以⋯",
    zimu_9="可是",
    zimu_10="小美",
    zimu_11="今天是爸爸\n要到大学去教课的日子",
    zimu_12="我们不是说好了",
    zimu_13="你要在婆婆家\n乖乖等姊姊放学的吗？",
    zimu_14="姊姊还要再上两个小时的课",
    zimu_15="婆婆的田里又那么忙",
    zimu_16="小美在婆婆的家里一直都很乖的",
    verified=True,
)  # test_case_block_85
# noinspection PyArgumentList
test_case_block_86 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="婆婆，那我去跟老师说说看",
    verified=True,
)  # test_case_block_86
# noinspection PyArgumentList
test_case_block_87 = ZhongwenProofreadingTestCase.get_test_case_cls(4)(
    zimu_1="现在小月因为妈妈住院",
    zimu_2="所以妹妹暂时没人照顾",
    zimu_3="同学们要好好跟她相处啊",
    zimu_4="好、好",
    verified=True,
)  # test_case_block_87
# noinspection PyArgumentList
test_case_block_88 = ZhongwenProofreadingTestCase.get_test_case_cls(3)(
    zimu_1="这是什么啊",
    zimu_2="大龙猫呀",
    zimu_3="不要吵",
    verified=True,
)  # test_case_block_88
# noinspection PyArgumentList
test_case_block_89 = ZhongwenProofreadingTestCase.get_test_case_cls(7)(
    zimu_1="再见再见，明天见了",
    zimu_2="再见",
    zimu_3="我今天不能去社团了",
    zimu_4="我去跟老师说",
    zimu_5="再见了",
    zimu_6="拜拜，再见",
    zimu_7="小美，快点，要下雨了",
    verified=True,
)  # test_case_block_89
# noinspection PyArgumentList
test_case_block_90 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="下雨了",
    verified=True,
)  # test_case_block_90
# noinspection PyArgumentList
test_case_block_91 = ZhongwenProofreadingTestCase.get_test_case_cls(3)(
    zimu_1="人家都没有哭，棒不棒？\n嗯",
    zimu_2="可是真伤脑筋",
    zimu_3="土地公爷爷\n请您让我们躲一下雨",
    verified=True,
)  # test_case_block_91
# noinspection PyArgumentList
test_case_block_92 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="可是⋯",
    verified=True,
)  # test_case_block_92
# noinspection PyArgumentList
test_case_block_93 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="姊姊，有伞子真棒啊",
    zimu_2="可是伞子顶破了一个大洞",
    verified=True,
)  # test_case_block_93
# noinspection PyArgumentList
test_case_block_94 = ZhongwenProofreadingTestCase.get_test_case_cls(8)(
    zimu_1="爸爸今天好像没带伞",
    zimu_2="人家也要去接爸爸",
    zimu_3="不就是忘记了",
    zimu_4="明明都已经下雨了",
    zimu_5="竟然还会傻得忘了带伞\n你骗鬼啊！",
    zimu_6="好痛啊",
    zimu_7="我看啊\n你八成是把伞子弄坏了",
    zimu_8="才不是呢",
    verified=True,
)  # test_case_block_94
# noinspection PyArgumentList
test_case_block_95 = ZhongwenProofreadingTestCase.get_test_case_cls(18)(
    zimu_1="有人在家吗？",
    zimu_2="小月？还有小美",
    zimu_3="妈",
    zimu_4="今天真的是麻烦你们了",
    zimu_5="不用客气",
    zimu_6="对了\n这是勘太今天借我们的伞",
    zimu_7="这孩子⋯",
    zimu_8="这么破的伞子真不好意思",
    zimu_9="这把伞帮了我们好大的忙",
    zimu_10="不过却害勘太都淋湿了",
    zimu_11="麻烦伯母谢谢勘太",
    zimu_12="不必客气",
    zimu_13="反正他老是弄得全身都是泥",
    zimu_14="淋淋雨反而干净些",
    zimu_15="你们要去接爸爸啊",
    zimu_16="真是孝顺啊",
    zimu_17="小美，拜拜",
    zimu_18="拜拜",
    xiugai_6="对了，这是勘太今天借我们的伞",
    beizhu_6="将“对了\\n这是勘太今天借我们的伞”中的换行符去除。",
    xiugai_8="这么破的伞实在真不好意思",
    beizhu_8="将“伞子”改为“伞实在”，修正错别字。",
    difficulty=1,
)  # test_case_block_95
# noinspection PyArgumentList
test_case_block_96 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="刚才是谁来了呀",
    zimu_2="才懒得理呢",
    verified=True,
)  # test_case_block_96
# noinspection PyArgumentList
test_case_block_97 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="刚好赶上",
    verified=True,
)  # test_case_block_97
# noinspection PyArgumentList
test_case_block_98 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="你们要坐车吗？",
    zimu_2="开车",
    verified=True,
)  # test_case_block_98
# noinspection PyArgumentList
test_case_block_99 = ZhongwenProofreadingTestCase.get_test_case_cls(3)(
    zimu_1="爸爸没有搭这班车",
    zimu_2="一定是搭下一班啦",
    zimu_3="小美，妳到婆婆家等好不好？",
    xiugai_3="小美，你到婆婆家等好不好？",
    beizhu_3="将“妳”改为“你”，修正错别字。",
    difficulty=1,
)  # test_case_block_99
# noinspection PyArgumentList
test_case_block_100 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="怎么啦？",
    verified=True,
)  # test_case_block_100
# noinspection PyArgumentList
test_case_block_101 = ZhongwenProofreadingTestCase.get_test_case_cls(5)(
    zimu_1="小美",
    zimu_2="妳困啦",
    zimu_3="早跟你说过的嘛",
    zimu_4="要不要先到婆婆家去睡一下？",
    zimu_5="爸爸就快到了\n撑着点啊",
    xiugai_2="你困啦",
    beizhu_2="将“妳”改为“你”，修正错别字。",
    xiugai_5="爸爸就快到了撑着点啊",
    beizhu_5="去除“\n”，修正换行符为连续文本。",
    difficulty=1,
)  # test_case_block_101
# noinspection PyArgumentList
test_case_block_102 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="巴士怎么这么慢",
    verified=True,
)  # test_case_block_102
# noinspection PyArgumentList
test_case_block_103 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="来",
    verified=True,
)  # test_case_block_103
# noinspection PyArgumentList
test_case_block_104 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="大龙猫？",
    verified=True,
)  # test_case_block_104
# noinspection PyArgumentList
test_case_block_105 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="等我一下",
    verified=True,
)  # test_case_block_105
# noinspection PyArgumentList
test_case_block_106 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="这个借你",
    zimu_2="快点啊\n小美快要掉下来了啦",
    verified=True,
)  # test_case_block_106
# noinspection PyArgumentList
test_case_block_107 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="要这样子用",
    verified=True,
)  # test_case_block_107
# noinspection PyArgumentList
test_case_block_108 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="巴士来了！",
    verified=True,
)  # test_case_block_108
# noinspection PyArgumentList
test_case_block_109 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="大龙猫\n把爸爸的伞给带走了",
    verified=True,
)  # test_case_block_109
# noinspection PyArgumentList
test_case_block_110 = ZhongwenProofreadingTestCase.get_test_case_cls(13)(
    zimu_1="对不起，对不起",
    zimu_2="开车",
    zimu_3="爸爸没搭上电车",
    zimu_4="所以就没赶上平常那班巴士",
    zimu_5="害你们担心啦",
    zimu_6="出现了，爸爸\n真的出现了",
    zimu_7="对呀，还有猫的巴士",
    zimu_8="那辆巴士好大啊",
    zimu_9="眼睛像这样子啊",
    zimu_10="吓死人了",
    zimu_11="看到了！\n我看到大龙猫了！",
    zimu_12="好棒啊",
    zimu_13="好吓人啊",
    verified=True,
)  # test_case_block_110
# noinspection PyArgumentList
test_case_block_111 = ZhongwenProofreadingTestCase.get_test_case_cls(8)(
    zimu_1="妈妈",
    zimu_2="我现在心还在蹦蹦乱跳呢",
    zimu_3="今天真是既吓人又惊奇\n又开心的一天",
    zimu_4="而且大龙猫送给我们的礼物\n实在是太棒了",
    zimu_5="是一个用竹叶包着",
    zimu_6="然后外面再用\n龙须草绑着的小包包",
    zimu_7="我跟小美回家以后打开一看",
    zimu_8="发现里面都是橡果子",
    verified=True,
)  # test_case_block_111
# noinspection PyArgumentList
test_case_block_112 = ZhongwenProofreadingTestCase.get_test_case_cls(7)(
    zimu_1="我们想家里院子\n变成森林的话一定很棒",
    zimu_2="所以就把它们洒在院子里",
    zimu_3="不过",
    zimu_4="它们现在都还没有发芽",
    zimu_5="所以小美每天都一直在说",
    zimu_6="还没发芽，还没发芽",
    zimu_7="就好像猴子螃蟹大战\n里面那个螃蟹一样啊",
    verified=True,
)  # test_case_block_112
# noinspection PyArgumentList
test_case_block_113 = ZhongwenProofreadingTestCase.get_test_case_cls(3)(
    zimu_1="学校很快就要放暑假了",
    zimu_2="希望妈妈的病\n能够快点好起来好吗？",
    zimu_3="小月",
    xiugai_2="希望妈妈的病能够快点好起来好吗？",
    beizhu_2="去除“希望妈妈的病”与“能够快点好起来好吗？”之间的换行符，合并为一句。",
    difficulty=1,
)  # test_case_block_113
# noinspection PyArgumentList
test_case_block_114 = ZhongwenProofreadingTestCase.get_test_case_cls(6)(
    zimu_1="要关灯了",
    zimu_2="等等",
    zimu_3="爸爸，明天会不会发芽？",
    zimu_4="这个问题呀",
    zimu_5="我看要问大龙猫才会知道",
    zimu_6="晚安",
    verified=True,
)  # test_case_block_114
# noinspection PyArgumentList
test_case_block_115 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="小美",
    verified=True,
)  # test_case_block_115
# noinspection PyArgumentList
test_case_block_116 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="那是我们种橡果子的地方",
    verified=True,
)  # test_case_block_116
# noinspection PyArgumentList
test_case_block_117 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="太棒了！",
    verified=True,
)  # test_case_block_117
# noinspection PyArgumentList
test_case_block_118 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="小美，我们都变成风了啊",
    verified=True,
)  # test_case_block_118
# noinspection PyArgumentList
test_case_block_119 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="大树不见了",
    verified=True,
)  # test_case_block_119
# noinspection PyArgumentList
test_case_block_120 = ZhongwenProofreadingTestCase.get_test_case_cls(7)(
    zimu_1="成功了！",
    zimu_2="好像在作梦",
    zimu_3="却又不是梦",
    zimu_4="好像在作梦",
    zimu_5="却又不是梦",
    zimu_6="万岁！",
    zimu_7="好啊！",
    verified=True,
)  # test_case_block_120
# noinspection PyArgumentList
test_case_block_121 = ZhongwenProofreadingTestCase.get_test_case_cls(4)(
    zimu_1="草壁先生在吗？电报",
    zimu_2="草壁先生在家吗？",
    zimu_3="有您的电报",
    zimu_4="没人在家啊",
    verified=True,
)  # test_case_block_121
# noinspection PyArgumentList
test_case_block_122 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="婆婆",
    verified=True,
)  # test_case_block_122
# noinspection PyArgumentList
test_case_block_123 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="我在这儿",
    zimu_2="长成这个样就能吃了",
    verified=True,
)  # test_case_block_123
# noinspection PyArgumentList
test_case_block_124 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="婆婆，那这个呢？",
    zimu_2="可以",
    verified=True,
)  # test_case_block_124
# noinspection PyArgumentList
test_case_block_125 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="婆婆你的这块田\n好像是一座宝山啊",
    zimu_2="来，休息一下喘口气",
    verified=True,
)  # test_case_block_125
# noinspection PyArgumentList
test_case_block_126 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="已经冰透了",
    zimu_2="那我要吃了",
    verified=True,
)  # test_case_block_126
# noinspection PyArgumentList
test_case_block_127 = ZhongwenProofreadingTestCase.get_test_case_cls(18)(
    zimu_1="好好吃啊",
    zimu_2="真的呀",
    zimu_3="这是因为经常被太阳晒",
    zimu_4="对身体非常健康的啊",
    zimu_5="对妈妈的身体也有益吗？",
    zimu_6="当然啦",
    zimu_7="只要是\n吃了婆婆田里种的东西",
    zimu_8="身体就会好啦",
    zimu_9="这个星期六\n我妈妈就会回来了",
    zimu_10="妈妈要跟我一起睡觉啊",
    zimu_11="是吗？\n马上就要出院了",
    zimu_12="不算是真正的出院",
    zimu_13="星期一还得回去复诊",
    zimu_14="还没有那么快好",
    zimu_15="这样吗？",
    zimu_16="那可要多吃点东西补一补了",
    zimu_17="我要把我自己摘的\n粟米给妈妈吃",
    zimu_18="那她一定会很高兴的",
    verified=True,
)  # test_case_block_127
# noinspection PyArgumentList
test_case_block_128 = ZhongwenProofreadingTestCase.get_test_case_cls(3)(
    zimu_1="电报",
    zimu_2="你们不在\n所以邮差送去我家",
    zimu_3="给我们的",
    xiugai_2="你们不在，所以邮差送去我家",
    beizhu_2="将“你们不在\\n所以邮差送去我家”中的换行符去除，合并为一句。",
    difficulty=1,
)  # test_case_block_128
# noinspection PyArgumentList
test_case_block_129 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="婆婆\n我爸爸不到傍晚不回来",
    zimu_2="快打开看吧\n要是急事耽搁就不好了",
    verified=True,
)  # test_case_block_129
# noinspection PyArgumentList
test_case_block_130 = ZhongwenProofreadingTestCase.get_test_case_cls(11)(
    zimu_1="发电处七国山医院",
    zimu_2="七国山医院送来的",
    zimu_3="那就是从妈妈的医院",
    zimu_4="难道妈妈发生了什么事",
    zimu_5="婆婆，怎么办？",
    zimu_6="医院要我们跟他们联络",
    zimu_7="你别紧张，冷静一点",
    zimu_8="知不知道爸爸上班的地方？",
    zimu_9="爸爸研究室的电话号码\n我是知道",
    zimu_10="可是没有电话可打呀",
    zimu_11="勘太\n你带小月去打电话",
    xiugai_9="爸爸研究室的电话号码我是知道",
    beizhu_9="去掉“\\n”，修正换行符误识。",
    xiugai_11="勘太你带小月去打电话",
    beizhu_11="去掉“\\n”，修正换行符误识。",
    difficulty=1,
)  # test_case_block_130
# noinspection PyArgumentList
test_case_block_131 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="小美妳留下来陪婆婆",
    verified=True,
)  # test_case_block_131
# noinspection PyArgumentList
test_case_block_132 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="小美妳回去婆婆那里",
    xiugai_1="小美你回去婆婆那里",
    beizhu_1="将“妳”改为“你”，修正错别字。",
    difficulty=1,
)  # test_case_block_132
# noinspection PyArgumentList
test_case_block_133 = ZhongwenProofreadingTestCase.get_test_case_cls(8)(
    zimu_1="请你接市外电话",
    zimu_2="请接东京31局1382号",
    zimu_3="好",
    zimu_4="这个女孩还真是讨人喜欢呢",
    zimu_5="喂！是的",
    zimu_6="请问是考古学教室吗？",
    zimu_7="我爸爸⋯\n麻烦请草壁先生听电话",
    zimu_8="我叫做草壁月",
    xiugai_7="我爸爸⋯麻烦请草壁先生听电话",
    beizhu_7="去除换行符，将“我爸爸⋯\n麻烦请草壁先生听电话”合并为一行。",
    difficulty=1,
)  # test_case_block_133
# noinspection PyArgumentList
test_case_block_134 = ZhongwenProofreadingTestCase.get_test_case_cls(13)(
    zimu_1="爸爸，是我，小月",
    zimu_2="怎么了？",
    zimu_3="医院来电报？我知道了",
    zimu_4="爸爸现在就\n打电话到医院去问",
    zimu_5="是不是妈妈出事了",
    zimu_6="怎么办呀？爸爸",
    zimu_7="不会有事的",
    zimu_8="爸爸给医院打过电话\n就马上就回妳电话",
    zimu_9="你在那边等一下",
    zimu_10="待会儿就打给妳",
    zimu_11="婆婆\n我还可以在这里待一会吗？",
    zimu_12="我爸爸还会打电话来",
    zimu_13="没关系，慢慢来",
    verified=True,
)  # test_case_block_134
# noinspection PyArgumentList
test_case_block_135 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="姊姊",
    verified=True,
)  # test_case_block_135
# noinspection PyArgumentList
test_case_block_136 = ZhongwenProofreadingTestCase.get_test_case_cls(4)(
    zimu_1="不可以啦",
    zimu_2="这个是要给妈妈的粟米",
    zimu_3="不可以！",
    zimu_4="这个是要给妈妈的啦",
    verified=True,
)  # test_case_block_136
# noinspection PyArgumentList
test_case_block_137 = ZhongwenProofreadingTestCase.get_test_case_cls(13)(
    zimu_1="小美",
    zimu_2="爸爸说妈妈的病又有点恶化了",
    zimu_3="所以这个礼拜妈妈不能回家了",
    zimu_4="我不要！",
    zimu_5="你不要也不行啊",
    zimu_6="妈妈要是勉强出院\n反而更严重了那怎么办",
    zimu_7="我不要！",
    zimu_8="不过是晚几天而已",
    zimu_9="我不要！",
    zimu_10="那妈妈死掉\n也没有关系是不是",
    zimu_11="不要！",
    zimu_12="妳这个大笨蛋！",
    zimu_13="我不管妳了！",
    verified=True,
)  # test_case_block_137
# noinspection PyArgumentList
test_case_block_138 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="走吧",
    zimu_2="姊姊大坏蛋！",
    verified=True,
)  # test_case_block_138
# noinspection PyArgumentList
test_case_block_139 = ZhongwenProofreadingTestCase.get_test_case_cls(4)(
    zimu_1="衣服该收收了",
    zimu_2="别这么沮丧",
    zimu_3="婆婆不是过来帮忙了吗",
    zimu_4="打起精神",
    verified=True,
)  # test_case_block_139
# noinspection PyArgumentList
test_case_block_140 = ZhongwenProofreadingTestCase.get_test_case_cls(3)(
    zimu_1="你爸爸说他今天\n要留在医院过夜",
    zimu_2="妳妈妈不过是感冒而已",
    zimu_3="下个星期六一定会回来的",
    verified=True,
)  # test_case_block_140
# noinspection PyArgumentList
test_case_block_141 = ZhongwenProofreadingTestCase.get_test_case_cls(11)(
    zimu_1="之前也是这样",
    zimu_2="医生说只要住数天就会好了",
    zimu_3="而且那次也是说得了感冒",
    zimu_4="我妈妈要是死了该怎么办",
    zimu_5="小月",
    zimu_6="我妈妈要是死了那我们⋯",
    zimu_7="妳放心，不要乱想",
    zimu_8="妳妈妈哪舍得下\n妳们这些可爱的孩子",
    zimu_9="别哭了别哭了",
    zimu_10="在妳爸爸回来之前",
    zimu_11="婆婆都会陪着妳的\n好不好呀",
    xiugai_8="妳妈妈哪舍得下妳们这些可爱的孩子",
    beizhu_8="去除“\\n”换行符，修正OCR识别错误。",
    xiugai_11="婆婆都会陪着妳的好不好呀",
    beizhu_11="去除“\\n”换行符，修正OCR识别错误。",
    difficulty=1,
)  # test_case_block_141
# noinspection PyArgumentList
test_case_block_142 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="小美呀",
    verified=True,
)  # test_case_block_142
# noinspection PyArgumentList
test_case_block_143 = ZhongwenProofreadingTestCase.get_test_case_cls(14)(
    zimu_1="小美",
    zimu_2="小美",
    zimu_3="小美回来了没？",
    zimu_4="没在公车站牌那边吗？",
    zimu_5="这就奇怪了",
    zimu_6="她会跑到哪里去了？",
    zimu_7="我刚刚跟小美吵了一架",
    zimu_8="因为她⋯",
    zimu_9="她会不会\n跑去妈妈住的医院了",
    zimu_10="七国山医院去了呀",
    zimu_11="可是就连大人也得\n走上三个钟头才会到",
    zimu_12="我去看看",
    zimu_13="勘太\n快点去叫你爸爸回来",
    zimu_14="小美不见了",
    verified=True,
)  # test_case_block_143
# noinspection PyArgumentList
test_case_block_144 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="小美真是笨蛋\n不知道路又爱乱跑",
    verified=True,
)  # test_case_block_144
# noinspection PyArgumentList
test_case_block_145 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="小美",
    verified=True,
)  # test_case_block_145
# noinspection PyArgumentList
test_case_block_146 = ZhongwenProofreadingTestCase.get_test_case_cls(6)(
    zimu_1="打搅了，伯伯，请问⋯⋯",
    zimu_2="您有没有看见束辫子的小女孩\n从这条路经过",
    zimu_3="她是我妹妹",
    zimu_4="这个嘛⋯⋯小女孩啊",
    zimu_5="没什么印象",
    zimu_6="她会不会没往这边来",
    xiugai_2="您有没有看见束辫子的小女孩从这条路经过",
    beizhu_2="去除“您有没有看见束辫子的小女孩\n"
    "从这条路经过”中的换行符，修正OCR换行错误。",
    difficulty=1,
)  # test_case_block_146
# noinspection PyArgumentList
test_case_block_147 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="妳确定她是往这边来的？",
    zimu_2="我也不知道",
    verified=True,
)  # test_case_block_147
# noinspection PyArgumentList
test_case_block_148 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="小美",
    verified=True,
)  # test_case_block_148
# noinspection PyArgumentList
test_case_block_149 = ZhongwenProofreadingTestCase.get_test_case_cls(16)(
    zimu_1="停车！",
    zimu_2="搞什么啊！危险啊",
    zimu_3="我在找我妹妹",
    zimu_4="你们有没有看一个小女孩",
    zimu_5="妳妹妹？",
    zimu_6="她好像是往七国山医院去了",
    zimu_7="她是一个四岁的小女孩",
    zimu_8="良子啊，你刚才有没有看到",
    zimu_9="我们两个\n就是从那个方向来的",
    zimu_10="不过\n好像没有看到那样的小孩",
    zimu_11="谢谢你们",
    zimu_12="你从哪里来的？",
    zimu_13="松乡",
    zimu_14="松乡！？",
    zimu_15="会不会搞错了呀",
    zimu_16="就是啊",
    xiugai_5="你妹妹？",
    beizhu_5="将“妳妹妹？”改为“你妹妹？”，修正错别字。",
    difficulty=1,
)  # test_case_block_149
# noinspection PyArgumentList
test_case_block_150 = ZhongwenProofreadingTestCase.get_test_case_cls(11)(
    zimu_1="小月",
    zimu_2="勘太",
    zimu_3="怎么样？",
    zimu_4="没看到，那妳呢？",
    zimu_5="现在我爸爸他们也去找了",
    zimu_6="我去往七国山的路上看看",
    zimu_7="妳先回家去",
    zimu_8="我想小美一定是想去医院",
    zimu_9="可是却走错路了",
    zimu_10="一定是",
    zimu_11="刚才有人在神池\n发现一只小孩的凉鞋",
    verified=True,
)  # test_case_block_150
# noinspection PyArgumentList
test_case_block_151 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="不过还不确定\n那就是小美的鞋子",
    verified=True,
)  # test_case_block_151
# noinspection PyArgumentList
test_case_block_152 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="找到了吗？",
    verified=True,
)  # test_case_block_152
# noinspection PyArgumentList
test_case_block_153 = ZhongwenProofreadingTestCase.get_test_case_cls(3)(
    zimu_1="喃呒阿弥陀佛",
    zimu_2="池那边泥比较深一点\n从那边开始啊",
    zimu_3="递根竹竿给我！",
    verified=True,
)  # test_case_block_153
# noinspection PyArgumentList
test_case_block_154 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="喃呒阿弥陀佛\n婆婆，小月来了",
    verified=True,
)  # test_case_block_154
# noinspection PyArgumentList
test_case_block_155 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="婆婆",
    zimu_2="妳看看这个",
    verified=True,
)  # test_case_block_155
# noinspection PyArgumentList
test_case_block_156 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="不是小美的",
    verified=True,
)  # test_case_block_156
# noinspection PyArgumentList
test_case_block_157 = ZhongwenProofreadingTestCase.get_test_case_cls(9)(
    zimu_1="太好了",
    zimu_2="我还以\n这是小美的",
    zimu_3="婆婆就爱穷紧张",
    zimu_4="虚惊一场啊",
    zimu_5="那孩子到底跑到哪去了？",
    zimu_6="再去四处找找",
    zimu_7="快点啊，天要黑了",
    zimu_8="不好意思啊",
    zimu_9="大家辛苦你们\n再回头去找找好了",
    xiugai_2="我还以为这是小美的",
    beizhu_2="将“我还以\\n这是小美的”改为“我还以为这是小美的”，补全漏字。",
    xiugai_9="大家辛苦你们了，再回头去找找好了",
    beizhu_9="将“大家辛苦你们\\n再回头去找找好了”改为“大家辛苦你们了，再回头去找找好了”，补全漏字并合并断行。",
    difficulty=1,
)  # test_case_block_157
# noinspection PyArgumentList
test_case_block_158 = ZhongwenProofreadingTestCase.get_test_case_cls(5)(
    zimu_1="求求你们",
    zimu_2="把我带去龙猫那里",
    zimu_3="我的妹妹走丢了",
    zimu_4="不久天就要黑了",
    zimu_5="她一定在哪里迷了路",
    verified=True,
)  # test_case_block_158
# noinspection PyArgumentList
test_case_block_159 = ZhongwenProofreadingTestCase.get_test_case_cls(7)(
    zimu_1="大龙猫？",
    zimu_2="大龙猫",
    zimu_3="我妹妹小美走失了",
    zimu_4="我找了好久都找不到",
    zimu_5="求求你，帮我找小美好不好",
    zimu_6="她一定已经吓哭了",
    zimu_7="我现在不知道该怎么办好",
    verified=True,
)  # test_case_block_159
# noinspection PyArgumentList
test_case_block_160 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="大家都看不到它",
    verified=True,
)  # test_case_block_160
# noinspection PyArgumentList
test_case_block_161 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="小美",
    verified=True,
)  # test_case_block_161
# noinspection PyArgumentList
test_case_block_162 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="树林开出了一条路了",
    verified=True,
)  # test_case_block_162
# noinspection PyArgumentList
test_case_block_163 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="小美",
    verified=True,
)  # test_case_block_163
# noinspection PyArgumentList
test_case_block_164 = ZhongwenProofreadingTestCase.get_test_case_cls(3)(
    zimu_1="姊姊",
    zimu_2="姊姊",
    zimu_3="小美",
    verified=True,
)  # test_case_block_164
# noinspection PyArgumentList
test_case_block_165 = ZhongwenProofreadingTestCase.get_test_case_cls(5)(
    zimu_1="小美",
    zimu_2="姊姊",
    zimu_3="妳这个傻瓜",
    zimu_4="对不起",
    zimu_5="妳是不是想要把粟米\n送去医院给妈妈？",
    verified=True,
)  # test_case_block_165
# noinspection PyArgumentList
test_case_block_166 = ZhongwenProofreadingTestCase.get_test_case_cls(3)(
    zimu_1="＂七国山医院＂",
    zimu_2="你要送我们去医院吗？",
    zimu_3="谢谢你",
    xiugai_1="“七国山医院”",
    beizhu_1="将全角引号“＂”改为中文引号“””。",
    difficulty=1,
)  # test_case_block_166
# noinspection PyArgumentList
test_case_block_167 = ZhongwenProofreadingTestCase.get_test_case_cls(13)(
    zimu_1="对不起，只不过是感冒",
    zimu_2="医院就擅自决定\n发电报给家里了",
    zimu_3="那两个孩子一定都很担心我吧",
    zimu_4="真是苦了她们了",
    zimu_5="她们知道你平安就会安心的",
    zimu_6="这些年来我们一家四口",
    zimu_7="不都这样努力过来的吗？",
    zimu_8="享福之前总得吃点苦啊",
    zimu_9="她们表面好像没事\n可是心里一定很难过",
    zimu_10="小月越是懂事\n就越教人于心不忍",
    zimu_11="是啊",
    zimu_12="出院以后我一定要好好疼她们",
    zimu_13="让她们尽情耍耍小脾气",
    verified=True,
)  # test_case_block_167
# noinspection PyArgumentList
test_case_block_168 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="妈妈在笑",
    zimu_2="看样子是没事了",
    verified=True,
)  # test_case_block_168
# noinspection PyArgumentList
test_case_block_169 = ZhongwenProofreadingTestCase.get_test_case_cls(2)(
    zimu_1="我得赶快把身体养好才行",
    zimu_2="是啊",
    verified=True,
)  # test_case_block_169
# noinspection PyArgumentList
test_case_block_170 = ZhongwenProofreadingTestCase.get_test_case_cls(6)(
    zimu_1="是谁摆的啊？",
    zimu_2="怎么啦？",
    zimu_3="我好像看到小月和小美坐在那棵松树上笑",
    zimu_4="搞不好是真的也说不定啊",
    zimu_5="妳看",
    zimu_6="＂送给妈妈＂",
    xiugai_6="“送给妈妈”",
    beizhu_6="将“＂送给妈妈＂”中的全角引号改为中文引号。",
    difficulty=1,
)  # test_case_block_170
# noinspection PyArgumentList
test_case_block_171 = ZhongwenProofreadingTestCase.get_test_case_cls(1)(
    zimu_1="谢谢观看",
    verified=True,
)  # test_case_block_171


test_cases: list[ZhongwenProofreadingTestCase] = [
    test_case
    for name, test_case in globals().items()
    if name.startswith("test_case_block_") and test_case is not None
]
"""中文 proofreading test cases."""

__all__ = [
    "test_cases",
]
