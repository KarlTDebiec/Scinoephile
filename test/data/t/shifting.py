#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for T."""

from __future__ import annotations

from itertools import chain

from scinoephile.audio.cantonese.shifting import ShiftTestCase

shift_test_cases_block_0 = [
    ShiftTestCase(
        zhongwen_1="警察",
        yuewen_1="喂警察",
        zhongwen_2="拿身份证出来",
        yuewen_2="攞我新闻证出嚟睇",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
        prompt=True,
        verified=True,
    ),
]  # shift_test_cases_block_0
shift_test_cases_block_1 = [
    ShiftTestCase(
        zhongwen_1="﹣检查一下　　﹣收到",
        yuewen_1="查下咩料收到",
        zhongwen_2="﹣袋子里装什么？　　﹣总机",
        yuewen_2="角度系袋住啲咩呀",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
        verified=True,
    ),
    ShiftTestCase(
        zhongwen_1="﹣袋子里装什么？　　﹣总机",
        yuewen_1="角度系袋住啲咩呀",
        zhongwen_2="﹣打开来看看　　﹣身份证号码：C532743",
        yuewen_2="通话电台查查个牌匙C532743",
        yuewen_1_shifted="角度系袋住啲咩呀通话电台",
        yuewen_2_shifted="查查个牌匙C532743",
        difficulty=1,
        prompt=True,
        verified=True,
    ),
    ShiftTestCase(
        zhongwen_1="﹣打开来看看　　﹣身份证号码：C532743",
        yuewen_1="查查个牌匙C532743",
        zhongwen_2="尾数一，季正雄",
        yuewen_2="尾数1贵正红",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
        verified=True,
    ),
    ShiftTestCase(
        zhongwen_1="尾数一，季正雄",
        yuewen_1="尾数1贵正红",
        zhongwen_2="打开",
        yuewen_2="打佢",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
        verified=True,
    ),
]  # shift_test_cases_block_1
shift_test_cases_block_2 = [
    ShiftTestCase(
        zhongwen_1="协议中有关香港的安排",
        yuewen_1="嘅arrangementsfor",
        zhongwen_2="不是权宜之计",
        yuewen_2="HongKongcontainedin",
        yuewen_1_shifted="嘅arrangementsforHongKongcontainedin",
        yuewen_2_shifted="",
        difficulty=1,
    ),
    ShiftTestCase(
        zhongwen_1="不是权宜之计",
        yuewen_1="",
        zhongwen_2="这些安排是长期的政策",
        yuewen_2="theagreement而notmeasuresofexpediency",
        yuewen_1_shifted="theagreement而notmeasuresofexpediency",
        yuewen_2_shifted="",
        difficulty=1,
    ),
    ShiftTestCase(
        zhongwen_1="这些安排是长期的政策",
        yuewen_1="",
        zhongwen_2="它们将写入为香港制定的基本法",
        yuewen_2="嘅好longtermpoliciesWhichwillbe",
        yuewen_1_shifted="嘅好longtermpolicies",
        yuewen_2_shifted="Whichwillbe",
        difficulty=1,
    ),
    ShiftTestCase(
        zhongwen_1="它们将写入为香港制定的基本法",
        yuewen_1="Whichwillbe",
        zhongwen_2="五十年不变",
        yuewen_2="incorporatedinthebasiclawforHong",
        yuewen_1_shifted="WhichwillbeincorporatedinthebasiclawforHong",
        yuewen_2_shifted="",
        difficulty=1,
    ),
    ShiftTestCase(
        zhongwen_1="五十年不变",
        yuewen_1="",
        zhongwen_2="五十年不变",
        yuewen_2="KongAndpreservedintactFor50yearsfrom1997",
        yuewen_1_shifted="KongAndpreservedintactFor50yearsfrom1997",
        yuewen_2_shifted="",
        difficulty=1,
    ),
    ShiftTestCase(
        zhongwen_1="是中英两国的共同利益",
        yuewen_1="",
        zhongwen_2="也是我们双方共同的责任",
        yuewen_2="也是我们双方共同的",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
]  # shift_test_cases_block_2
shift_test_cases_block_3 = [
    ShiftTestCase(
        zhongwen_1="今天下午观塘发生械劫案",
        yuewen_1="",
        zhongwen_2="四名持枪械匪徒",
        yuewen_2="今日下昼观塘发生鞋劫案四名持枪鞋匪徒连环打劫立华街五间金行",
        yuewen_1_shifted="今日下昼观塘发生鞋劫案",
        yuewen_2_shifted="四名持枪鞋匪徒连环打劫立华街五间金行",
        difficulty=1,
    ),
    ShiftTestCase(
        zhongwen_1="今天下午观塘发生械劫案",
        yuewen_1="今日下昼观塘发生鞋劫案",
        zhongwen_2="四名持枪械匪徒",
        yuewen_2="",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="四名持枪械匪徒",
        yuewen_1="",
        zhongwen_2="连环打劫物华街五间金行",
        yuewen_2="四名持枪鞋匪徒连环打劫立华街五间金行",
        yuewen_1_shifted="四名持枪鞋匪徒",
        yuewen_2_shifted="连环打劫立华街五间金行",
        difficulty=1,
    ),
    ShiftTestCase(
        zhongwen_1="连环打劫物华街五间金行",
        yuewen_1="连环打劫立华街五间金行",
        zhongwen_2="去你妈的！",
        yuewen_2="",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="由观众提供片段，见到贼人离开的时候",
        yuewen_1="",
        zhongwen_2="在附近秘密执勤的飞虎队员发生枪战",
        yuewen_2="由观众提供片段见到贼人离开嘅时候同喺附近秘密执勤嘅飞虎队员发生枪战",
        yuewen_1_shifted="由观众提供片段见到贼人离开嘅时候",
        yuewen_2_shifted="同喺附近秘密执勤嘅飞虎队员发生枪战",
        difficulty=1,
    ),
    ShiftTestCase(
        zhongwen_1="去你妈的！",
        yuewen_1="",
        zhongwen_2="由观众提供片段，见到贼人离开的时候",
        yuewen_2="由观众提供片段见到贼人离开嘅时候",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="由观众提供片段，见到贼人离开的时候",
        yuewen_1="由观众提供片段见到贼人离开嘅时候",
        zhongwen_2="在附近秘密执勤的飞虎队员发生枪战",
        yuewen_2="同喺附近秘密执勤嘅飞虎队员发生枪战",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="在附近秘密执勤的飞虎队员发生枪战",
        yuewen_1="同喺附近秘密执勤嘅飞虎队员发生枪战",
        zhongwen_2="双方开枪过百发",
        yuewen_2="",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="双方开枪过百发",
        yuewen_1="",
        zhongwen_2="事件中，两名途人及三名军装警员受伤",
        yuewen_2="双方开枪过白房事件中两名逃人及三名军人警察获杀",
        yuewen_1_shifted="双方开枪过白房",
        yuewen_2_shifted="事件中两名逃人及三名军人警察获杀",
        difficulty=1,
    ),
    ShiftTestCase(
        zhongwen_1="在附近秘密执勤的飞虎队员发生枪战",
        yuewen_1="同喺附近秘密执勤嘅飞虎队员发生枪战",
        zhongwen_2="双方开枪过百发",
        yuewen_2="双方开枪过白房",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="双方开枪过百发",
        yuewen_1="双方开枪过白房",
        zhongwen_2="事件中，两名途人及三名军装警员受伤",
        yuewen_2="事件中两名逃人及三名军人警察获杀",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="事件中，两名途人及三名军装警员受伤",
        yuewen_1="事件中两名逃人及三名军人警察获杀",
        zhongwen_2="五间金行合共损失大约一千万",
        yuewen_2="现间有狂黑洞损失大约三次万",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="五间金行合共损失大约一千万",
        yuewen_1="现间有狂黑洞损失大约三次万",
        zhongwen_2="警方相信，今次械劫案的主谋",
        yuewen_2="",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="警方相信，今次械劫案的主谋",
        yuewen_1="",
        zhongwen_2="是「头号通缉犯」叶国欢",
        yuewen_2="警方相信今次鞋劫案嘅主谋系头号通缉犯叶国宽",
        yuewen_1_shifted="警方相信今次鞋劫案嘅主谋",
        yuewen_2_shifted="系头号通缉犯叶国宽",
        difficulty=1,
    ),
    ShiftTestCase(
        zhongwen_1="是「头号通缉犯」叶国欢",
        yuewen_1="系头号通缉犯叶国宽",
        zhongwen_2="一夫当关，万夫莫敌！",
        yuewen_2="一孤当关万夫莫敌",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="一夫当关，万夫莫敌！",
        yuewen_1="一孤当关万夫莫敌",
        zhongwen_2="真是威风！欢哥！",
        yuewen_2="真系威吓宽哥",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="真是威风！欢哥！",
        yuewen_1="真系威吓宽哥",
        zhongwen_2="但大事不妙了！",
        yuewen_2="但系大剂啦",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="但大事不妙了！",
        yuewen_1="但系大剂啦",
        zhongwen_2="都说放多些报纸！",
        yuewen_2="都话贱到啲报纸㗎喇",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="都说放多些报纸！",
        yuewen_1="都话贱到啲报纸㗎喇",
        zhongwen_2="你看！到处都是血！",
        yuewen_2="睇吓睇吓",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="你看！到处都是血！",
        yuewen_1="睇吓睇吓",
        zhongwen_2="拿去吧，混蛋！",
        yuewen_2="周围都系血攞去啦仆街",
        yuewen_1_shifted="睇吓睇吓周围都系血",
        yuewen_2_shifted="攞去啦仆街",
        difficulty=1,
    ),
]  # shift_test_cases_block_3
shift_test_cases_block_4 = [
    ShiftTestCase(
        zhongwen_1="真是很不妙！",
        yuewen_1="喂,真系好大只呀",
        zhongwen_2="两折，不好意思，最多两折！",
        yuewen_2="两折,唔好意思,最多两折",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="两折，不好意思，最多两折！",
        yuewen_1="两折,唔好意思,最多两折",
        zhongwen_2="说好四折",
        yuewen_2="",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="说好四折",
        yuewen_1="",
        zhongwen_2="还有道义吗？",
        yuewen_2="讲好四折㗎㖞讲唔讲道义㗎",
        yuewen_1_shifted="讲好四折㗎",
        yuewen_2_shifted="㖞讲唔讲道义㗎",
        difficulty=1,
    ),
    ShiftTestCase(
        zhongwen_1="两折，不好意思，最多两折！",
        yuewen_1="两折,唔好意思,最多两折",
        zhongwen_2="说好四折",
        yuewen_2="讲好四折㗎",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="说好四折",
        yuewen_1="讲好四折㗎",
        zhongwen_2="还有道义吗？",
        yuewen_2="㖞讲唔讲道义㗎",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="还有道义吗？",
        yuewen_1="㖞讲唔讲道义㗎",
        zhongwen_2="一千万货你只给两百万？",
        yuewen_2="成千万货你哋畀两搞",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="一千万货你只给两百万？",
        yuewen_1="成千万货你哋畀两搞",
        zhongwen_2="以前至少五折！",
        yuewen_2="",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="以前至少五折！",
        yuewen_1="",
        zhongwen_2="你们销赃的全赚了！",
        yuewen_2="以前除少都五只啦",
        yuewen_1_shifted="以前除少都五只啦",
        yuewen_2_shifted="",
        difficulty=1,
    ),
    ShiftTestCase(
        zhongwen_1="你们销赃的全赚了！",
        yuewen_1="",
        zhongwen_2="赚你个屁！",
        yuewen_2="你哋班消庄佬赞晒呀赞你条毛咩",
        yuewen_1_shifted="你哋班消庄佬赞晒呀",
        yuewen_2_shifted="赞你条毛咩",
        difficulty=1,
    ),
    ShiftTestCase(
        zhongwen_1="赚你个屁！",
        yuewen_1="赞你条毛咩",
        zhongwen_2="今时不同往日",
        yuewen_2="今时唔同往日喇",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="今时不同往日",
        yuewen_1="今时唔同往日喇",
        zhongwen_2="外面的警察盯得很紧！",
        yuewen_2="喂,出面啲差异睇得好紧㗎",
        yuewen_1_shifted="今时唔同往日",
        yuewen_2_shifted="喇喂,出面啲差异睇得好紧㗎",
        difficulty=1,
    ),
    ShiftTestCase(
        zhongwen_1="赚你个屁！",
        yuewen_1="赞你条毛咩",
        zhongwen_2="今时不同往日",
        yuewen_2="今时唔同往日",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="今时不同往日",
        yuewen_1="今时唔同往日",
        zhongwen_2="外面的警察盯得很紧！",
        yuewen_2="喇喂,出面啲差异睇得好紧㗎",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
]  # shift_test_cases_block_4
shift_test_cases_block_5 = [
    ShiftTestCase(
        zhongwen_1="尤其是你的货，欢哥！",
        yuewen_1="系尤其是你嗰批货啊宽哥",
        zhongwen_2="上次那一批，销了两年，足足两年！",
        yuewen_2="上次嗰批烧咗两年足足两年啊",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="上次那一批，销了两年，足足两年！",
        yuewen_1="上次嗰批烧咗两年足足两年啊",
        zhongwen_2="炒股、炒楼、炒栗子更能赚钱！",
        yuewen_2="真系炒股炒楼炒栗子都好过啦系吧",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="炒股、炒楼、炒栗子更能赚钱！",
        yuewen_1="真系炒股炒楼炒栗子都好过啦系吧",
        zhongwen_2="帮个忙",
        yuewen_2="都说说畀我",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="帮个忙",
        yuewen_1="都说说畀我",
        zhongwen_2="四折！",
        yuewen_2="死绝",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="四折！",
        yuewen_1="死绝",
        zhongwen_2="欢哥开口，怎么着都行！",
        yuewen_2="既然宽哥出到声点话点好啦",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
]  # shift_test_cases_block_5
shift_test_cases_block_6 = [
    ShiftTestCase(
        zhongwen_1="不如你找其它买家？",
        yuewen_1="唔好呀唔好呀",
        zhongwen_2="我都买不下手，我看没人敢收⋯",
        yuewen_2="唔好呀唔好呀",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="我都买不下手，我看没人敢收⋯",
        yuewen_1="唔好呀唔好呀",
        zhongwen_2="去你妈的！",
        yuewen_2="唔好呀唔好呀唔好呀唔好呀唔好呀",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="去你妈的！",
        yuewen_1="唔好呀唔好呀唔好呀唔好呀唔好呀",
        zhongwen_2="开保险箱！",
        yuewen_2="唔好呀唔好呀",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="开保险箱！",
        yuewen_1="唔好呀唔好呀",
        zhongwen_2="你算是抢我？",
        yuewen_2="唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
]  # shift_test_cases_block_6
shift_test_cases_block_7 = []  # shift_test_cases_block_7
shift_test_cases_block_8 = [
    ShiftTestCase(
        zhongwen_1="真的多谢了，欢哥！",
        yuewen_1="真系多谢晒你呀宽哥",
        zhongwen_2="以后别来找我",
        yuewen_2="以后咪嚟揾我",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="以后别来找我",
        yuewen_1="以后咪嚟揾我",
        zhongwen_2="不要再合作",
        yuewen_2="唔好再合作啦",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
    ShiftTestCase(
        zhongwen_1="不要再合作",
        yuewen_1="唔好再合作啦",
        zhongwen_2="各走各路！",
        yuewen_2="各行各路啊",
        yuewen_1_shifted="",
        yuewen_2_shifted="",
    ),
]  # shift_test_cases_block_8
shift_test_cases_block_9 = []  # shift_test_cases_block_9
shift_test_cases_block_10 = []  # shift_test_cases_block_10
shift_test_cases_block_11 = []  # shift_test_cases_block_11
shift_test_cases_block_12 = []  # shift_test_cases_block_12
shift_test_cases_block_13 = []  # shift_test_cases_block_13
shift_test_cases_block_14 = []  # shift_test_cases_block_14
shift_test_cases_block_15 = []  # shift_test_cases_block_15
shift_test_cases_block_16 = []  # shift_test_cases_block_16
shift_test_cases_block_17 = []  # shift_test_cases_block_17
shift_test_cases_block_18 = []  # shift_test_cases_block_18
shift_test_cases_block_19 = []  # shift_test_cases_block_19
shift_test_cases_block_20 = []  # shift_test_cases_block_20
shift_test_cases_block_21 = []  # shift_test_cases_block_21
shift_test_cases_block_22 = []  # shift_test_cases_block_22
shift_test_cases_block_23 = []  # shift_test_cases_block_23
shift_test_cases_block_24 = []  # shift_test_cases_block_24
shift_test_cases_block_25 = []  # shift_test_cases_block_25
shift_test_cases_block_26 = []  # shift_test_cases_block_26
shift_test_cases_block_27 = []  # shift_test_cases_block_27
shift_test_cases_block_28 = []  # shift_test_cases_block_28
shift_test_cases_block_29 = []  # shift_test_cases_block_29
shift_test_cases_block_30 = []  # shift_test_cases_block_30
shift_test_cases_block_31 = []  # shift_test_cases_block_31
shift_test_cases_block_32 = []  # shift_test_cases_block_32
shift_test_cases_block_33 = []  # shift_test_cases_block_33
shift_test_cases_block_34 = []  # shift_test_cases_block_34
shift_test_cases_block_35 = []  # shift_test_cases_block_35
shift_test_cases_block_36 = []  # shift_test_cases_block_36
shift_test_cases_block_37 = []  # shift_test_cases_block_37
shift_test_cases_block_38 = []  # shift_test_cases_block_38
shift_test_cases_block_39 = []  # shift_test_cases_block_39
shift_test_cases_block_40 = []  # shift_test_cases_block_40
shift_test_cases_block_41 = []  # shift_test_cases_block_41
shift_test_cases_block_42 = []  # shift_test_cases_block_42
shift_test_cases_block_43 = []  # shift_test_cases_block_43
shift_test_cases_block_44 = []  # shift_test_cases_block_44
shift_test_cases_block_45 = []  # shift_test_cases_block_45
shift_test_cases_block_46 = []  # shift_test_cases_block_46
shift_test_cases_block_47 = []  # shift_test_cases_block_47
shift_test_cases_block_48 = []  # shift_test_cases_block_48
shift_test_cases_block_49 = []  # shift_test_cases_block_49
shift_test_cases_block_50 = []  # shift_test_cases_block_50
shift_test_cases_block_51 = []  # shift_test_cases_block_51
shift_test_cases_block_52 = []  # shift_test_cases_block_52
shift_test_cases_block_53 = []  # shift_test_cases_block_53
shift_test_cases_block_54 = []  # shift_test_cases_block_54
shift_test_cases_block_55 = []  # shift_test_cases_block_55
shift_test_cases_block_56 = []  # shift_test_cases_block_56
shift_test_cases_block_57 = []  # shift_test_cases_block_57
shift_test_cases_block_58 = []  # shift_test_cases_block_58
shift_test_cases_block_59 = []  # shift_test_cases_block_59
shift_test_cases_block_60 = []  # shift_test_cases_block_60
shift_test_cases_block_61 = []  # shift_test_cases_block_61
shift_test_cases_block_62 = []  # shift_test_cases_block_62
shift_test_cases_block_63 = []  # shift_test_cases_block_63
shift_test_cases_block_64 = []  # shift_test_cases_block_64
shift_test_cases_block_65 = []  # shift_test_cases_block_65
shift_test_cases_block_66 = []  # shift_test_cases_block_66
shift_test_cases_block_67 = []  # shift_test_cases_block_67
shift_test_cases_block_68 = []  # shift_test_cases_block_68
shift_test_cases_block_69 = []  # shift_test_cases_block_69
shift_test_cases_block_70 = []  # shift_test_cases_block_70
shift_test_cases_block_71 = []  # shift_test_cases_block_71
shift_test_cases_block_72 = []  # shift_test_cases_block_72
shift_test_cases_block_73 = []  # shift_test_cases_block_73
shift_test_cases_block_74 = []  # shift_test_cases_block_74
shift_test_cases_block_75 = []  # shift_test_cases_block_75
shift_test_cases_block_76 = []  # shift_test_cases_block_76
shift_test_cases_block_77 = []  # shift_test_cases_block_77
shift_test_cases_block_78 = []  # shift_test_cases_block_78
shift_test_cases_block_79 = []  # shift_test_cases_block_79
shift_test_cases_block_80 = []  # shift_test_cases_block_80
shift_test_cases_block_81 = []  # shift_test_cases_block_81
shift_test_cases_block_82 = []  # shift_test_cases_block_82
shift_test_cases_block_83 = []  # shift_test_cases_block_83
shift_test_cases_block_84 = []  # shift_test_cases_block_84
shift_test_cases_block_85 = []  # shift_test_cases_block_85
shift_test_cases_block_86 = []  # shift_test_cases_block_86
shift_test_cases_block_87 = []  # shift_test_cases_block_87
shift_test_cases_block_88 = []  # shift_test_cases_block_88
shift_test_cases_block_89 = []  # shift_test_cases_block_89
shift_test_cases_block_90 = []  # shift_test_cases_block_90
shift_test_cases_block_91 = []  # shift_test_cases_block_91
shift_test_cases_block_92 = []  # shift_test_cases_block_92
shift_test_cases_block_93 = []  # shift_test_cases_block_93
shift_test_cases_block_94 = []  # shift_test_cases_block_94
shift_test_cases_block_95 = []  # shift_test_cases_block_95
shift_test_cases_block_96 = []  # shift_test_cases_block_96
shift_test_cases_block_97 = []  # shift_test_cases_block_97
shift_test_cases_block_98 = []  # shift_test_cases_block_98
shift_test_cases_block_99 = []  # shift_test_cases_block_99
shift_test_cases_block_100 = []  # shift_test_cases_block_100
shift_test_cases_block_101 = []  # shift_test_cases_block_101
shift_test_cases_block_102 = []  # shift_test_cases_block_102
shift_test_cases_block_103 = []  # shift_test_cases_block_103
shift_test_cases_block_104 = []  # shift_test_cases_block_104
shift_test_cases_block_105 = []  # shift_test_cases_block_105
shift_test_cases_block_106 = []  # shift_test_cases_block_106
shift_test_cases_block_107 = []  # shift_test_cases_block_107
shift_test_cases_block_108 = []  # shift_test_cases_block_108
shift_test_cases_block_109 = []  # shift_test_cases_block_109
shift_test_cases_block_110 = []  # shift_test_cases_block_110
shift_test_cases_block_111 = []  # shift_test_cases_block_111
shift_test_cases_block_112 = []  # shift_test_cases_block_112
shift_test_cases_block_113 = []  # shift_test_cases_block_113
shift_test_cases_block_114 = []  # shift_test_cases_block_114
shift_test_cases_block_115 = []  # shift_test_cases_block_115
shift_test_cases_block_116 = []  # shift_test_cases_block_116
shift_test_cases_block_117 = []  # shift_test_cases_block_117
shift_test_cases_block_118 = []  # shift_test_cases_block_118
shift_test_cases_block_119 = []  # shift_test_cases_block_119
shift_test_cases_block_120 = []  # shift_test_cases_block_120
shift_test_cases_block_121 = []  # shift_test_cases_block_121
shift_test_cases_block_122 = []  # shift_test_cases_block_122
shift_test_cases_block_123 = []  # shift_test_cases_block_123
shift_test_cases_block_124 = []  # shift_test_cases_block_124
shift_test_cases_block_125 = []  # shift_test_cases_block_125
shift_test_cases_block_126 = []  # shift_test_cases_block_126
shift_test_cases_block_127 = []  # shift_test_cases_block_127
shift_test_cases_block_128 = []  # shift_test_cases_block_128
shift_test_cases_block_129 = []  # shift_test_cases_block_129
shift_test_cases_block_130 = []  # shift_test_cases_block_130
shift_test_cases_block_131 = []  # shift_test_cases_block_131
shift_test_cases_block_132 = []  # shift_test_cases_block_132
shift_test_cases_block_133 = []  # shift_test_cases_block_133
shift_test_cases_block_134 = []  # shift_test_cases_block_134
shift_test_cases_block_135 = []  # shift_test_cases_block_135
shift_test_cases_block_136 = []  # shift_test_cases_block_136
shift_test_cases_block_137 = []  # shift_test_cases_block_137
shift_test_cases_block_138 = []  # shift_test_cases_block_138
shift_test_cases_block_139 = []  # shift_test_cases_block_139
shift_test_cases_block_140 = []  # shift_test_cases_block_140
shift_test_cases_block_141 = []  # shift_test_cases_block_141
shift_test_cases_block_142 = []  # shift_test_cases_block_142
shift_test_cases_block_143 = []  # shift_test_cases_block_143
shift_test_cases_block_144 = []  # shift_test_cases_block_144
shift_test_cases_block_145 = []  # shift_test_cases_block_145
shift_test_cases_block_146 = []  # shift_test_cases_block_146
shift_test_cases_block_147 = []  # shift_test_cases_block_147
shift_test_cases_block_148 = []  # shift_test_cases_block_148
shift_test_cases_block_149 = []  # shift_test_cases_block_149
shift_test_cases_block_150 = []  # shift_test_cases_block_150
shift_test_cases_block_151 = []  # shift_test_cases_block_151
shift_test_cases_block_152 = []  # shift_test_cases_block_152
shift_test_cases_block_153 = []  # shift_test_cases_block_153
shift_test_cases_block_154 = []  # shift_test_cases_block_154
shift_test_cases_block_155 = []  # shift_test_cases_block_155
shift_test_cases_block_156 = []  # shift_test_cases_block_156
shift_test_cases_block_157 = []  # shift_test_cases_block_157
shift_test_cases_block_158 = []  # shift_test_cases_block_158
shift_test_cases_block_159 = []  # shift_test_cases_block_159
shift_test_cases_block_160 = []  # shift_test_cases_block_160
shift_test_cases_block_161 = []  # shift_test_cases_block_161
shift_test_cases_block_162 = []  # shift_test_cases_block_162
shift_test_cases_block_163 = []  # shift_test_cases_block_163
shift_test_cases_block_164 = []  # shift_test_cases_block_164
shift_test_cases_block_165 = []  # shift_test_cases_block_165
shift_test_cases_block_166 = []  # shift_test_cases_block_166
shift_test_cases_block_167 = []  # shift_test_cases_block_167
shift_test_cases_block_168 = []  # shift_test_cases_block_168
shift_test_cases_block_169 = []  # shift_test_cases_block_169
shift_test_cases_block_170 = []  # shift_test_cases_block_170
shift_test_cases_block_171 = []  # shift_test_cases_block_171
shift_test_cases_block_172 = []  # shift_test_cases_block_172
shift_test_cases_block_173 = []  # shift_test_cases_block_173
shift_test_cases_block_174 = []  # shift_test_cases_block_174
shift_test_cases_block_175 = []  # shift_test_cases_block_175
shift_test_cases_block_176 = []  # shift_test_cases_block_176
shift_test_cases_block_177 = []  # shift_test_cases_block_177
shift_test_cases_block_178 = []  # shift_test_cases_block_178
shift_test_cases_block_179 = []  # shift_test_cases_block_179
shift_test_cases_block_180 = []  # shift_test_cases_block_180
shift_test_cases_block_181 = []  # shift_test_cases_block_181

t_shift_test_cases: list[ShiftTestCase] = list(
    chain.from_iterable(
        cases
        for name, cases in globals().items()
        if name.startswith("shift_test_cases_block_") and cases
    )
)

"""T 粤文 shifting test cases."""

__all__ = [
    "t_shift_test_cases",
]
