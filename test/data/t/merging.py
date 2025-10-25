#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for T."""

from __future__ import annotations

from itertools import chain

from scinoephile.audio.cantonese.merging import MergeTestCase

merge_test_cases_block_0 = [
    MergeTestCase(
        zhongwen="警察",
        yuewen_to_merge=["喂", "警察"],
        yuewen_merged="喂，警察",
        difficulty=2,
        prompt=True,
        verified=True,
    ),
]  # merge_test_cases_block_0
merge_test_cases_block_1 = [
    MergeTestCase(
        zhongwen="﹣检查一下　　﹣收到",
        yuewen_to_merge=["查下咩料", "收到"],
        yuewen_merged="﹣查下咩料　　﹣收到",
        difficulty=1,
        prompt=True,
        verified=True,
    ),
    MergeTestCase(
        zhongwen="﹣袋子里装什么？　　﹣总机",
        yuewen_to_merge=["角度系袋住啲咩呀", "通话电台"],
        yuewen_merged="﹣角度系袋住啲咩呀？　　﹣通话电台",
        difficulty=1,
        verified=True,
    ),
    MergeTestCase(
        zhongwen="﹣打开来看看　　﹣身份证号码：C532743",
        yuewen_to_merge=["查", "查个牌匙", "C532743"],
        yuewen_merged="查查个牌匙：C532743",
        difficulty=3,
        verified=True,
    ),
    MergeTestCase(
        zhongwen="尾数一，季正雄",
        yuewen_to_merge=["尾数1", "贵正红"],
        yuewen_merged="尾数1，贵正红",
        difficulty=1,
        verified=True,
    ),
]  # merge_test_cases_block_1
merge_test_cases_block_2 = [
    MergeTestCase(
        zhongwen="协议中有关香港的安排",
        yuewen_to_merge=["嘅arrangements", "for", "Hong", "Kong", "contained", "in"],
        yuewen_merged="嘅arrangementsforHongKongcontainedin",
    ),
    MergeTestCase(
        zhongwen="不是权宜之计",
        yuewen_to_merge=["the", "agreement", "而not", "measures", "of", "expediency"],
        yuewen_merged="the，agreement，而not，measures，of，expediency",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="这些安排是长期的政策",
        yuewen_to_merge=["嘅好long", "term", "policies"],
        yuewen_merged="嘅好longtermpolicies",
    ),
    MergeTestCase(
        zhongwen="它们将写入为香港制定的基本法",
        yuewen_to_merge=[
            "Which",
            "will",
            "be",
            "incorporated",
            "in",
            "the",
            "basic",
            "law",
            "for",
            "Hong",
        ],
        yuewen_merged="Which，will，be，incorporated，in，the，basic，law，for，Hong",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="五十年不变",
        yuewen_to_merge=[
            "Kong",
            "And",
            "preserved",
            "in",
            "tact",
            "For",
            "50",
            "years",
            "from",
            "1997",
        ],
        yuewen_merged="Kong，And，preserved，in，tact，For，50，years，from，1997",
        difficulty=2,
    ),
]  # merge_test_cases_block_2
merge_test_cases_block_3 = [
    MergeTestCase(
        zhongwen="由观众提供片段，见到贼人离开的时候",
        yuewen_to_merge=["由观众提供片段见到贼人离开嘅时候"],
        yuewen_merged="由观众提供片段，见到贼人离开嘅时候",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="事件中，两名途人及三名军装警员受伤",
        yuewen_to_merge=["事件中两名逃人及三名军人警察获杀"],
        yuewen_merged="事件中，两名逃人及三名军人警察获杀",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="五间金行合共损失大约一千万",
        yuewen_to_merge=["现间有狂", "黑洞损失大约三次万"],
        yuewen_merged="现间有狂黑洞损失大约三次万",
    ),
    MergeTestCase(
        zhongwen="警方相信，今次械劫案的主谋",
        yuewen_to_merge=["警方相信今次鞋劫案嘅主谋"],
        yuewen_merged="警方相信，今次鞋劫案嘅主谋",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="是「头号通缉犯」叶国欢",
        yuewen_to_merge=["系头号通缉犯叶国宽"],
        yuewen_merged="系头号通缉犯叶国宽",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="一夫当关，万夫莫敌！",
        yuewen_to_merge=["一孤当关万夫莫敌"],
        yuewen_merged="一孤当关，万夫莫敌！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="真是威风！欢哥！",
        yuewen_to_merge=["真系威吓宽哥"],
        yuewen_merged="真系威吓！宽哥！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="但大事不妙了！",
        yuewen_to_merge=["但系大剂啦"],
        yuewen_merged="但系大剂啦！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="都说放多些报纸！",
        yuewen_to_merge=["都话贱到啲报纸㗎喇"],
        yuewen_merged="都话贱到啲报纸㗎喇！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="你看！到处都是血！",
        yuewen_to_merge=["睇吓睇吓", "周围都系血"],
        yuewen_merged="睇吓睇吓！周围都系血！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="拿去吧，混蛋！",
        yuewen_to_merge=["攞去啦", "仆街"],
        yuewen_merged="攞去啦，仆街！",
        difficulty=1,
    ),
]  # merge_test_cases_block_3
merge_test_cases_block_4 = [
    MergeTestCase(
        zhongwen="真是很不妙！",
        yuewen_to_merge=["喂,真系好大只呀"],
        yuewen_merged="喂,真系好大只呀！",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="两折，不好意思，最多两折！",
        yuewen_to_merge=["两折,唔好意思,最多两折"],
        yuewen_merged="两折,唔好意思,最多两折！",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="还有道义吗？",
        yuewen_to_merge=["㖞", "讲唔讲道义㗎"],
        yuewen_merged="㖞，讲唔讲道义㗎？",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="一千万货你只给两百万？",
        yuewen_to_merge=["成千万货你哋畀两搞"],
        yuewen_merged="成千万货你哋畀两搞？",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="以前至少五折！",
        yuewen_to_merge=["以前除少都五只啦"],
        yuewen_merged="以前除少都五只啦！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="你们销赃的全赚了！",
        yuewen_to_merge=["你哋班消庄佬赞晒呀"],
        yuewen_merged="你哋班消庄佬赞晒呀！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="赚你个屁！",
        yuewen_to_merge=["赞你条毛咩"],
        yuewen_merged="赞你条毛咩！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="外面的警察盯得很紧！",
        yuewen_to_merge=["喇", "喂,出面啲差异睇得好紧㗎"],
        yuewen_merged="喇喂,出面啲差异睇得好紧㗎！",
        difficulty=2,
    ),
]  # merge_test_cases_block_4
merge_test_cases_block_5 = [
    MergeTestCase(
        zhongwen="尤其是你的货，欢哥！",
        yuewen_to_merge=["系", "尤其是你嗰批货啊", "宽哥"],
        yuewen_merged="系，尤其是你嗰批货啊，宽哥！",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="上次那一批，销了两年，足足两年！",
        yuewen_to_merge=["上次嗰批", "烧咗两年", "足足两年啊"],
        yuewen_merged="上次嗰批，烧咗两年，足足两年啊！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="炒股、炒楼、炒栗子更能赚钱！",
        yuewen_to_merge=["真系炒股炒楼炒栗子都好过啦", "系吧"],
        yuewen_merged="真系炒股、炒楼、炒栗子都好过啦！系吧",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="四折！",
        yuewen_to_merge=["死绝"],
        yuewen_merged="死绝！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="欢哥开口，怎么着都行！",
        yuewen_to_merge=["既然宽哥出到声", "点话点好啦"],
        yuewen_merged="既然宽哥出到声，点话点好啦！",
        difficulty=1,
    ),
]  # merge_test_cases_block_5
merge_test_cases_block_6 = [
    MergeTestCase(
        zhongwen="不如你找其它买家？",
        yuewen_to_merge=["唔好呀", "唔好呀"],
        yuewen_merged="唔好呀，唔好呀？",
        difficulty=2,
    ),
    MergeTestCase(
        zhongwen="我都买不下手，我看没人敢收⋯",
        yuewen_to_merge=["唔好呀", "唔好呀"],
        yuewen_merged="唔好呀，唔好呀⋯",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="去你妈的！",
        yuewen_to_merge=["唔好呀", "唔好呀", "唔好呀", "唔好呀", "唔好呀"],
        yuewen_merged="唔好呀唔好呀唔好呀唔好呀唔好呀！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="开保险箱！",
        yuewen_to_merge=["唔好呀", "唔好呀"],
        yuewen_merged="唔好呀唔好呀！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="你算是抢我？",
        yuewen_to_merge=[
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
            "唔好呀",
        ],
        yuewen_merged="唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀？",
        difficulty=1,
    ),
]  # merge_test_cases_block_6
merge_test_cases_block_7 = []  # merge_test_cases_block_7
merge_test_cases_block_8 = [
    MergeTestCase(
        zhongwen="真的多谢了，欢哥！",
        yuewen_to_merge=["真系多谢晒你呀", "宽哥"],
        yuewen_merged="真系多谢晒你呀，宽哥！",
        difficulty=1,
    ),
    MergeTestCase(
        zhongwen="各走各路！",
        yuewen_to_merge=["各行各路啊"],
        yuewen_merged="各行各路啊！",
        difficulty=1,
    ),
]  # merge_test_cases_block_8
merge_test_cases_block_9 = [
    MergeTestCase(
        zhongwen="欢哥，火！",
        yuewen_to_merge=["阿", "花香", "回来了"],
        yuewen_merged="阿花香，回来了！",
        difficulty=1,
    ),
]  # merge_test_cases_block_9
merge_test_cases_block_10 = []  # merge_test_cases_block_10
merge_test_cases_block_11 = []  # merge_test_cases_block_11
merge_test_cases_block_12 = []  # merge_test_cases_block_12
merge_test_cases_block_13 = []  # merge_test_cases_block_13
merge_test_cases_block_14 = []  # merge_test_cases_block_14
merge_test_cases_block_15 = []  # merge_test_cases_block_15
merge_test_cases_block_16 = []  # merge_test_cases_block_16
merge_test_cases_block_17 = []  # merge_test_cases_block_17
merge_test_cases_block_18 = []  # merge_test_cases_block_18
merge_test_cases_block_19 = []  # merge_test_cases_block_19
merge_test_cases_block_20 = []  # merge_test_cases_block_20
merge_test_cases_block_21 = []  # merge_test_cases_block_21
merge_test_cases_block_22 = []  # merge_test_cases_block_22
merge_test_cases_block_23 = []  # merge_test_cases_block_23
merge_test_cases_block_24 = []  # merge_test_cases_block_24
merge_test_cases_block_25 = []  # merge_test_cases_block_25
merge_test_cases_block_26 = []  # merge_test_cases_block_26
merge_test_cases_block_27 = []  # merge_test_cases_block_27
merge_test_cases_block_28 = []  # merge_test_cases_block_28
merge_test_cases_block_29 = []  # merge_test_cases_block_29
merge_test_cases_block_30 = []  # merge_test_cases_block_30
merge_test_cases_block_31 = []  # merge_test_cases_block_31
merge_test_cases_block_32 = []  # merge_test_cases_block_32
merge_test_cases_block_33 = []  # merge_test_cases_block_33
merge_test_cases_block_34 = []  # merge_test_cases_block_34
merge_test_cases_block_35 = []  # merge_test_cases_block_35
merge_test_cases_block_36 = []  # merge_test_cases_block_36
merge_test_cases_block_37 = []  # merge_test_cases_block_37
merge_test_cases_block_38 = []  # merge_test_cases_block_38
merge_test_cases_block_39 = []  # merge_test_cases_block_39
merge_test_cases_block_40 = []  # merge_test_cases_block_40
merge_test_cases_block_41 = []  # merge_test_cases_block_41
merge_test_cases_block_42 = []  # merge_test_cases_block_42
merge_test_cases_block_43 = []  # merge_test_cases_block_43
merge_test_cases_block_44 = []  # merge_test_cases_block_44
merge_test_cases_block_45 = []  # merge_test_cases_block_45
merge_test_cases_block_46 = []  # merge_test_cases_block_46
merge_test_cases_block_47 = []  # merge_test_cases_block_47
merge_test_cases_block_48 = []  # merge_test_cases_block_48
merge_test_cases_block_49 = []  # merge_test_cases_block_49
merge_test_cases_block_50 = []  # merge_test_cases_block_50
merge_test_cases_block_51 = []  # merge_test_cases_block_51
merge_test_cases_block_52 = []  # merge_test_cases_block_52
merge_test_cases_block_53 = []  # merge_test_cases_block_53
merge_test_cases_block_54 = []  # merge_test_cases_block_54
merge_test_cases_block_55 = []  # merge_test_cases_block_55
merge_test_cases_block_56 = []  # merge_test_cases_block_56
merge_test_cases_block_57 = []  # merge_test_cases_block_57
merge_test_cases_block_58 = []  # merge_test_cases_block_58
merge_test_cases_block_59 = []  # merge_test_cases_block_59
merge_test_cases_block_60 = []  # merge_test_cases_block_60
merge_test_cases_block_61 = []  # merge_test_cases_block_61
merge_test_cases_block_62 = []  # merge_test_cases_block_62
merge_test_cases_block_63 = []  # merge_test_cases_block_63
merge_test_cases_block_64 = []  # merge_test_cases_block_64
merge_test_cases_block_65 = []  # merge_test_cases_block_65
merge_test_cases_block_66 = []  # merge_test_cases_block_66
merge_test_cases_block_67 = []  # merge_test_cases_block_67
merge_test_cases_block_68 = []  # merge_test_cases_block_68
merge_test_cases_block_69 = []  # merge_test_cases_block_69
merge_test_cases_block_70 = []  # merge_test_cases_block_70
merge_test_cases_block_71 = []  # merge_test_cases_block_71
merge_test_cases_block_72 = []  # merge_test_cases_block_72
merge_test_cases_block_73 = []  # merge_test_cases_block_73
merge_test_cases_block_74 = []  # merge_test_cases_block_74
merge_test_cases_block_75 = []  # merge_test_cases_block_75
merge_test_cases_block_76 = []  # merge_test_cases_block_76
merge_test_cases_block_77 = []  # merge_test_cases_block_77
merge_test_cases_block_78 = []  # merge_test_cases_block_78
merge_test_cases_block_79 = []  # merge_test_cases_block_79
merge_test_cases_block_80 = []  # merge_test_cases_block_80
merge_test_cases_block_81 = []  # merge_test_cases_block_81
merge_test_cases_block_82 = []  # merge_test_cases_block_82
merge_test_cases_block_83 = []  # merge_test_cases_block_83
merge_test_cases_block_84 = []  # merge_test_cases_block_84
merge_test_cases_block_85 = []  # merge_test_cases_block_85
merge_test_cases_block_86 = []  # merge_test_cases_block_86
merge_test_cases_block_87 = []  # merge_test_cases_block_87
merge_test_cases_block_88 = []  # merge_test_cases_block_88
merge_test_cases_block_89 = []  # merge_test_cases_block_89
merge_test_cases_block_90 = []  # merge_test_cases_block_90
merge_test_cases_block_91 = []  # merge_test_cases_block_91
merge_test_cases_block_92 = []  # merge_test_cases_block_92
merge_test_cases_block_93 = []  # merge_test_cases_block_93
merge_test_cases_block_94 = []  # merge_test_cases_block_94
merge_test_cases_block_95 = []  # merge_test_cases_block_95
merge_test_cases_block_96 = []  # merge_test_cases_block_96
merge_test_cases_block_97 = []  # merge_test_cases_block_97
merge_test_cases_block_98 = []  # merge_test_cases_block_98
merge_test_cases_block_99 = []  # merge_test_cases_block_99
merge_test_cases_block_100 = []  # merge_test_cases_block_100
merge_test_cases_block_101 = []  # merge_test_cases_block_101
merge_test_cases_block_102 = []  # merge_test_cases_block_102
merge_test_cases_block_103 = []  # merge_test_cases_block_103
merge_test_cases_block_104 = []  # merge_test_cases_block_104
merge_test_cases_block_105 = []  # merge_test_cases_block_105
merge_test_cases_block_106 = []  # merge_test_cases_block_106
merge_test_cases_block_107 = []  # merge_test_cases_block_107
merge_test_cases_block_108 = []  # merge_test_cases_block_108
merge_test_cases_block_109 = []  # merge_test_cases_block_109
merge_test_cases_block_110 = []  # merge_test_cases_block_110
merge_test_cases_block_111 = []  # merge_test_cases_block_111
merge_test_cases_block_112 = []  # merge_test_cases_block_112
merge_test_cases_block_113 = []  # merge_test_cases_block_113
merge_test_cases_block_114 = []  # merge_test_cases_block_114
merge_test_cases_block_115 = []  # merge_test_cases_block_115
merge_test_cases_block_116 = []  # merge_test_cases_block_116
merge_test_cases_block_117 = []  # merge_test_cases_block_117
merge_test_cases_block_118 = []  # merge_test_cases_block_118
merge_test_cases_block_119 = []  # merge_test_cases_block_119
merge_test_cases_block_120 = []  # merge_test_cases_block_120
merge_test_cases_block_121 = []  # merge_test_cases_block_121
merge_test_cases_block_122 = []  # merge_test_cases_block_122
merge_test_cases_block_123 = []  # merge_test_cases_block_123
merge_test_cases_block_124 = []  # merge_test_cases_block_124
merge_test_cases_block_125 = []  # merge_test_cases_block_125
merge_test_cases_block_126 = []  # merge_test_cases_block_126
merge_test_cases_block_127 = []  # merge_test_cases_block_127
merge_test_cases_block_128 = []  # merge_test_cases_block_128
merge_test_cases_block_129 = []  # merge_test_cases_block_129
merge_test_cases_block_130 = []  # merge_test_cases_block_130
merge_test_cases_block_131 = []  # merge_test_cases_block_131
merge_test_cases_block_132 = []  # merge_test_cases_block_132
merge_test_cases_block_133 = []  # merge_test_cases_block_133
merge_test_cases_block_134 = []  # merge_test_cases_block_134
merge_test_cases_block_135 = []  # merge_test_cases_block_135
merge_test_cases_block_136 = []  # merge_test_cases_block_136
merge_test_cases_block_137 = []  # merge_test_cases_block_137
merge_test_cases_block_138 = []  # merge_test_cases_block_138
merge_test_cases_block_139 = []  # merge_test_cases_block_139
merge_test_cases_block_140 = []  # merge_test_cases_block_140
merge_test_cases_block_141 = []  # merge_test_cases_block_141
merge_test_cases_block_142 = []  # merge_test_cases_block_142
merge_test_cases_block_143 = []  # merge_test_cases_block_143
merge_test_cases_block_144 = []  # merge_test_cases_block_144
merge_test_cases_block_145 = []  # merge_test_cases_block_145
merge_test_cases_block_146 = []  # merge_test_cases_block_146
merge_test_cases_block_147 = []  # merge_test_cases_block_147
merge_test_cases_block_148 = []  # merge_test_cases_block_148
merge_test_cases_block_149 = []  # merge_test_cases_block_149
merge_test_cases_block_150 = []  # merge_test_cases_block_150
merge_test_cases_block_151 = []  # merge_test_cases_block_151
merge_test_cases_block_152 = []  # merge_test_cases_block_152
merge_test_cases_block_153 = []  # merge_test_cases_block_153
merge_test_cases_block_154 = []  # merge_test_cases_block_154
merge_test_cases_block_155 = []  # merge_test_cases_block_155
merge_test_cases_block_156 = []  # merge_test_cases_block_156
merge_test_cases_block_157 = []  # merge_test_cases_block_157
merge_test_cases_block_158 = []  # merge_test_cases_block_158
merge_test_cases_block_159 = []  # merge_test_cases_block_159
merge_test_cases_block_160 = []  # merge_test_cases_block_160
merge_test_cases_block_161 = []  # merge_test_cases_block_161
merge_test_cases_block_162 = []  # merge_test_cases_block_162
merge_test_cases_block_163 = []  # merge_test_cases_block_163
merge_test_cases_block_164 = []  # merge_test_cases_block_164
merge_test_cases_block_165 = []  # merge_test_cases_block_165
merge_test_cases_block_166 = []  # merge_test_cases_block_166
merge_test_cases_block_167 = []  # merge_test_cases_block_167
merge_test_cases_block_168 = []  # merge_test_cases_block_168
merge_test_cases_block_169 = []  # merge_test_cases_block_169
merge_test_cases_block_170 = []  # merge_test_cases_block_170
merge_test_cases_block_171 = []  # merge_test_cases_block_171
merge_test_cases_block_172 = []  # merge_test_cases_block_172
merge_test_cases_block_173 = []  # merge_test_cases_block_173
merge_test_cases_block_174 = []  # merge_test_cases_block_174
merge_test_cases_block_175 = []  # merge_test_cases_block_175
merge_test_cases_block_176 = []  # merge_test_cases_block_176
merge_test_cases_block_177 = []  # merge_test_cases_block_177
merge_test_cases_block_178 = []  # merge_test_cases_block_178
merge_test_cases_block_179 = []  # merge_test_cases_block_179
merge_test_cases_block_180 = []  # merge_test_cases_block_180
merge_test_cases_block_181 = []  # merge_test_cases_block_181

t_merge_test_cases: list[MergeTestCase] = list(
    chain.from_iterable(
        cases
        for name, cases in globals().items()
        if name.startswith("merge_test_cases_block_") and cases
    )
)

"""T 粤文 merging test cases."""

__all__ = [
    "t_merge_test_cases",
]
