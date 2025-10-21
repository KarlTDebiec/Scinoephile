#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for T."""

from __future__ import annotations

from scinoephile.audio.cantonese.translation.abcs import TranslateTestCase

translate_test_case_block_0 = None  # translate_test_case_block_0
translate_test_case_block_1 = None  # translate_test_case_block_1
translate_test_case_block_2 = TranslateTestCase.get_test_case_cls(
    10,
    (1, 3, 4, 5, 6, 7, 8),
)(
    zhongwen_1="协议中有关香港的安排",
    yuewen_1="协议中有关香港嘅安排",
    zhongwen_2="不是权宜之计",
    zhongwen_3="这些安排是长期的政策",
    yuewen_3="呢啲安排係長期嘅政策。",
    zhongwen_4="它们将写入为香港制定的基本法",
    zhongwen_5="五十年不变",
    zhongwen_6="五十年不变",
    zhongwen_7="确保《联合声明》",
    zhongwen_8="不受干扰地全面贯彻实施",
    zhongwen_9="是中英两国的共同利益",
    zhongwen_10="也是我们双方共同的责任",
    yuewen_10="也是我们双方共同的责任",
    yuewen_2="唔係權宜之計",
    yuewen_4="佢哋會寫入為香港制定嘅基本法入面",
    yuewen_5="五十年唔變",
    yuewen_6="五十年唔變",
    yuewen_7="確保《聯合聲明》",
    yuewen_8="唔受干擾咁全面貫徹實施",
    yuewen_9="係中英兩國共同嘅利益",
)  # translate_test_case_block_2
translate_test_case_block_3 = TranslateTestCase.get_test_case_cls(
    17,
    (3,),
)(
    zhongwen_1="今天下午观塘发生械劫案",
    yuewen_1="今日下昼观塘发生械劫案",
    zhongwen_2="四名持枪械匪徒",
    yuewen_2="四名持枪械匪徒",
    zhongwen_3="连环打劫物华街五间金行",
    yuewen_3="连环打劫物华街五间金行",
    zhongwen_4="去你妈的！",
    zhongwen_5="由观众提供片段，见到贼人离开的时候",
    yuewen_5="由观众提供片段，见到贼人离开嘅时候",
    zhongwen_6="在附近秘密执勤的飞虎队员发生枪战",
    yuewen_6="同喺附近秘密执勤嘅飞虎队员发生枪战",
    zhongwen_7="双方开枪过百发",
    yuewen_7="双方开枪过百发",
    zhongwen_8="事件中，两名途人及三名军装警员受伤",
    yuewen_8="事件中，两名途人及三名军装警员受伤",
    zhongwen_9="五间金行合共损失大约一千万",
    yuewen_9="五间金行合共损失大约一千万",
    zhongwen_10="警方相信，今次械劫案的主谋",
    yuewen_10="警方相信，今次械劫案嘅主谋",
    zhongwen_11="是「头号通缉犯」叶国欢",
    yuewen_11="系头号通缉犯叶国欢",
    zhongwen_12="一夫当关，万夫莫敌！",
    yuewen_12="一夫当关，万夫莫敌！",
    zhongwen_13="真是威风！欢哥！",
    yuewen_13="真系威风！欢哥！",
    zhongwen_14="但大事不妙了！",
    yuewen_14="但系大事不妙啦！",
    zhongwen_15="都说放多些报纸！",
    yuewen_15="都话放多啲报纸㗎喇！",
    zhongwen_16="你看！到处都是血！",
    yuewen_16="睇吓睇吓！周围都系血！",
    zhongwen_17="拿去吧，混蛋！",
    yuewen_17="攞去啦，仆街！",
    yuewen_4="屌你老母！",
)  # translate_test_case_block_3
translate_test_case_block_4 = TranslateTestCase.get_test_case_cls(
    10,
    (0,),
)(
    zhongwen_1="真是很不妙！",
    zhongwen_2="两折，不好意思，最多两折！",
    yuewen_2="两折,唔好意思,最多两折！",
    zhongwen_3="说好四折",
    yuewen_3="讲好四折㗎",
    zhongwen_4="还有道义吗？",
    yuewen_4="㖞，讲唔讲道义㗎？",
    zhongwen_5="一千万货你只给两百万？",
    yuewen_5="成千万货你哋畀两百万？",
    zhongwen_6="以前至少五折！",
    yuewen_6="以前至少都五折啦！",
    zhongwen_7="你们销赃的全赚了！",
    yuewen_7="你哋班销赃佬赚晒呀！",
    zhongwen_8="赚你个屁！",
    yuewen_8="赚你条毛咩！",
    zhongwen_9="今时不同往日",
    yuewen_9="今时唔同往日",
    zhongwen_10="外面的警察盯得很紧！",
    yuewen_10="喇喂,出面啲差佬睇得好紧㗎！",
    yuewen_1="真係好唔掂呀！",
)  # translate_test_case_block_4
translate_test_case_block_5 = TranslateTestCase.get_test_case_cls(
    6,
    (3,),
)(
    zhongwen_1="尤其是你的货，欢哥！",
    yuewen_1="系，尤其是你嗰批货啊，欢哥！",
    zhongwen_2="上次那一批，销了两年，足足两年！",
    yuewen_2="上次嗰批，销咗两年，足足两年啊！",
    zhongwen_3="炒股、炒楼、炒栗子更能赚钱！",
    yuewen_3="真系炒股、炒楼、炒栗子更能赚钱啦！",
    zhongwen_4="帮个忙",
    zhongwen_5="四折！",
    yuewen_5="四折！",
    zhongwen_6="欢哥开口，怎么着都行！",
    yuewen_6="既然欢哥出到声，点话点好啦！",
    yuewen_4="帮个手啦",
)  # translate_test_case_block_5
translate_test_case_block_6 = TranslateTestCase.get_test_case_cls(
    5,
    (0, 1, 2, 3, 4),
)(
    zhongwen_1="不如你找其它买家？",
    zhongwen_2="我都买不下手，我看没人敢收⋯",
    zhongwen_3="去你妈的！",
    zhongwen_4="开保险箱！",
    zhongwen_5="你算是抢我？",
    yuewen_1="不如你搵第二个买家啦？",
    yuewen_2="我都唔敢买，我睇下有边个敢收⋯",
    yuewen_3="屌你老母！",
    yuewen_4="开保险箱！",
    yuewen_5="你当抢我咩？",
)  # translate_test_case_block_6
translate_test_case_block_7 = None  # translate_test_case_block_7
translate_test_case_block_8 = None  # translate_test_case_block_8
translate_test_case_block_9 = TranslateTestCase.get_test_case_cls(
    1,
    (0,),
)(
    zhongwen_1="欢哥，火！",
    yuewen_1="欢哥，开火啦！",
)  # translate_test_case_block_9
translate_test_case_block_10 = None  # translate_test_case_block_10
translate_test_case_block_11 = None  # translate_test_case_block_11
translate_test_case_block_12 = None  # translate_test_case_block_12
translate_test_case_block_13 = None  # translate_test_case_block_13
translate_test_case_block_14 = None  # translate_test_case_block_14
translate_test_case_block_15 = None  # translate_test_case_block_15
translate_test_case_block_16 = None  # translate_test_case_block_16
translate_test_case_block_17 = None  # translate_test_case_block_17
translate_test_case_block_18 = None  # translate_test_case_block_18
translate_test_case_block_19 = None  # translate_test_case_block_19
translate_test_case_block_20 = None  # translate_test_case_block_20
translate_test_case_block_21 = None  # translate_test_case_block_21
translate_test_case_block_22 = None  # translate_test_case_block_22
translate_test_case_block_23 = None  # translate_test_case_block_23
translate_test_case_block_24 = None  # translate_test_case_block_24
translate_test_case_block_25 = None  # translate_test_case_block_25
translate_test_case_block_26 = None  # translate_test_case_block_26
translate_test_case_block_27 = None  # translate_test_case_block_27
translate_test_case_block_28 = None  # translate_test_case_block_28
translate_test_case_block_29 = None  # translate_test_case_block_29
translate_test_case_block_30 = None  # translate_test_case_block_30
translate_test_case_block_31 = None  # translate_test_case_block_31
translate_test_case_block_32 = None  # translate_test_case_block_32
translate_test_case_block_33 = None  # translate_test_case_block_33
translate_test_case_block_34 = None  # translate_test_case_block_34
translate_test_case_block_35 = None  # translate_test_case_block_35
translate_test_case_block_36 = None  # translate_test_case_block_36
translate_test_case_block_37 = None  # translate_test_case_block_37
translate_test_case_block_38 = None  # translate_test_case_block_38
translate_test_case_block_39 = None  # translate_test_case_block_39
translate_test_case_block_40 = None  # translate_test_case_block_40
translate_test_case_block_41 = None  # translate_test_case_block_41
translate_test_case_block_42 = None  # translate_test_case_block_42
translate_test_case_block_43 = None  # translate_test_case_block_43
translate_test_case_block_44 = None  # translate_test_case_block_44
translate_test_case_block_45 = None  # translate_test_case_block_45
translate_test_case_block_46 = None  # translate_test_case_block_46
translate_test_case_block_47 = None  # translate_test_case_block_47
translate_test_case_block_48 = None  # translate_test_case_block_48
translate_test_case_block_49 = None  # translate_test_case_block_49
translate_test_case_block_50 = None  # translate_test_case_block_50
translate_test_case_block_51 = None  # translate_test_case_block_51
translate_test_case_block_52 = None  # translate_test_case_block_52
translate_test_case_block_53 = None  # translate_test_case_block_53
translate_test_case_block_54 = None  # translate_test_case_block_54
translate_test_case_block_55 = None  # translate_test_case_block_55
translate_test_case_block_56 = None  # translate_test_case_block_56
translate_test_case_block_57 = None  # translate_test_case_block_57
translate_test_case_block_58 = None  # translate_test_case_block_58
translate_test_case_block_59 = None  # translate_test_case_block_59
translate_test_case_block_60 = None  # translate_test_case_block_60
translate_test_case_block_61 = None  # translate_test_case_block_61
translate_test_case_block_62 = None  # translate_test_case_block_62
translate_test_case_block_63 = None  # translate_test_case_block_63
translate_test_case_block_64 = None  # translate_test_case_block_64
translate_test_case_block_65 = None  # translate_test_case_block_65
translate_test_case_block_66 = None  # translate_test_case_block_66
translate_test_case_block_67 = None  # translate_test_case_block_67
translate_test_case_block_68 = None  # translate_test_case_block_68
translate_test_case_block_69 = None  # translate_test_case_block_69
translate_test_case_block_70 = None  # translate_test_case_block_70
translate_test_case_block_71 = None  # translate_test_case_block_71
translate_test_case_block_72 = None  # translate_test_case_block_72
translate_test_case_block_73 = None  # translate_test_case_block_73
translate_test_case_block_74 = None  # translate_test_case_block_74
translate_test_case_block_75 = None  # translate_test_case_block_75
translate_test_case_block_76 = None  # translate_test_case_block_76
translate_test_case_block_77 = None  # translate_test_case_block_77
translate_test_case_block_78 = None  # translate_test_case_block_78
translate_test_case_block_79 = None  # translate_test_case_block_79
translate_test_case_block_80 = None  # translate_test_case_block_80
translate_test_case_block_81 = None  # translate_test_case_block_81
translate_test_case_block_82 = None  # translate_test_case_block_82
translate_test_case_block_83 = None  # translate_test_case_block_83
translate_test_case_block_84 = None  # translate_test_case_block_84
translate_test_case_block_85 = None  # translate_test_case_block_85
translate_test_case_block_86 = None  # translate_test_case_block_86
translate_test_case_block_87 = None  # translate_test_case_block_87
translate_test_case_block_88 = None  # translate_test_case_block_88
translate_test_case_block_89 = None  # translate_test_case_block_89
translate_test_case_block_90 = None  # translate_test_case_block_90
translate_test_case_block_91 = None  # translate_test_case_block_91
translate_test_case_block_92 = None  # translate_test_case_block_92
translate_test_case_block_93 = None  # translate_test_case_block_93
translate_test_case_block_94 = None  # translate_test_case_block_94
translate_test_case_block_95 = None  # translate_test_case_block_95
translate_test_case_block_96 = None  # translate_test_case_block_96
translate_test_case_block_97 = None  # translate_test_case_block_97
translate_test_case_block_98 = None  # translate_test_case_block_98
translate_test_case_block_99 = None  # translate_test_case_block_99
translate_test_case_block_100 = None  # translate_test_case_block_100
translate_test_case_block_101 = None  # translate_test_case_block_101
translate_test_case_block_102 = None  # translate_test_case_block_102
translate_test_case_block_103 = None  # translate_test_case_block_103
translate_test_case_block_104 = None  # translate_test_case_block_104
translate_test_case_block_105 = None  # translate_test_case_block_105
translate_test_case_block_106 = None  # translate_test_case_block_106
translate_test_case_block_107 = None  # translate_test_case_block_107
translate_test_case_block_108 = None  # translate_test_case_block_108
translate_test_case_block_109 = None  # translate_test_case_block_109
translate_test_case_block_110 = None  # translate_test_case_block_110
translate_test_case_block_111 = None  # translate_test_case_block_111
translate_test_case_block_112 = None  # translate_test_case_block_112
translate_test_case_block_113 = None  # translate_test_case_block_113
translate_test_case_block_114 = None  # translate_test_case_block_114
translate_test_case_block_115 = None  # translate_test_case_block_115
translate_test_case_block_116 = None  # translate_test_case_block_116
translate_test_case_block_117 = None  # translate_test_case_block_117
translate_test_case_block_118 = None  # translate_test_case_block_118
translate_test_case_block_119 = None  # translate_test_case_block_119
translate_test_case_block_120 = None  # translate_test_case_block_120
translate_test_case_block_121 = None  # translate_test_case_block_121
translate_test_case_block_122 = None  # translate_test_case_block_122
translate_test_case_block_123 = None  # translate_test_case_block_123
translate_test_case_block_124 = None  # translate_test_case_block_124
translate_test_case_block_125 = None  # translate_test_case_block_125
translate_test_case_block_126 = None  # translate_test_case_block_126
translate_test_case_block_127 = None  # translate_test_case_block_127
translate_test_case_block_128 = None  # translate_test_case_block_128
translate_test_case_block_129 = None  # translate_test_case_block_129
translate_test_case_block_130 = None  # translate_test_case_block_130
translate_test_case_block_131 = None  # translate_test_case_block_131
translate_test_case_block_132 = None  # translate_test_case_block_132
translate_test_case_block_133 = None  # translate_test_case_block_133
translate_test_case_block_134 = None  # translate_test_case_block_134
translate_test_case_block_135 = None  # translate_test_case_block_135
translate_test_case_block_136 = None  # translate_test_case_block_136
translate_test_case_block_137 = None  # translate_test_case_block_137
translate_test_case_block_138 = None  # translate_test_case_block_138
translate_test_case_block_139 = None  # translate_test_case_block_139
translate_test_case_block_140 = None  # translate_test_case_block_140
translate_test_case_block_141 = None  # translate_test_case_block_141
translate_test_case_block_142 = None  # translate_test_case_block_142
translate_test_case_block_143 = None  # translate_test_case_block_143
translate_test_case_block_144 = None  # translate_test_case_block_144
translate_test_case_block_145 = None  # translate_test_case_block_145
translate_test_case_block_146 = None  # translate_test_case_block_146
translate_test_case_block_147 = None  # translate_test_case_block_147
translate_test_case_block_148 = None  # translate_test_case_block_148
translate_test_case_block_149 = None  # translate_test_case_block_149
translate_test_case_block_150 = None  # translate_test_case_block_150
translate_test_case_block_151 = None  # translate_test_case_block_151
translate_test_case_block_152 = None  # translate_test_case_block_152
translate_test_case_block_153 = None  # translate_test_case_block_153
translate_test_case_block_154 = None  # translate_test_case_block_154
translate_test_case_block_155 = None  # translate_test_case_block_155
translate_test_case_block_156 = None  # translate_test_case_block_156
translate_test_case_block_157 = None  # translate_test_case_block_157
translate_test_case_block_158 = None  # translate_test_case_block_158
translate_test_case_block_159 = None  # translate_test_case_block_159
translate_test_case_block_160 = None  # translate_test_case_block_160
translate_test_case_block_161 = None  # translate_test_case_block_161
translate_test_case_block_162 = None  # translate_test_case_block_162
translate_test_case_block_163 = None  # translate_test_case_block_163
translate_test_case_block_164 = None  # translate_test_case_block_164
translate_test_case_block_165 = None  # translate_test_case_block_165
translate_test_case_block_166 = None  # translate_test_case_block_166
translate_test_case_block_167 = None  # translate_test_case_block_167
translate_test_case_block_168 = None  # translate_test_case_block_168
translate_test_case_block_169 = None  # translate_test_case_block_169
translate_test_case_block_170 = None  # translate_test_case_block_170
translate_test_case_block_171 = None  # translate_test_case_block_171
translate_test_case_block_172 = None  # translate_test_case_block_172
translate_test_case_block_173 = None  # translate_test_case_block_173
translate_test_case_block_174 = None  # translate_test_case_block_174
translate_test_case_block_175 = None  # translate_test_case_block_175
translate_test_case_block_176 = None  # translate_test_case_block_176
translate_test_case_block_177 = None  # translate_test_case_block_177
translate_test_case_block_178 = None  # translate_test_case_block_178
translate_test_case_block_179 = None  # translate_test_case_block_179
translate_test_case_block_180 = None  # translate_test_case_block_180
translate_test_case_block_181 = None  # translate_test_case_block_181

t_translate_test_cases: list[TranslateTestCase] = [
    test_case
    for name, test_case in globals().items()
    if name.startswith("translate_test_case_block_") and test_case is not None
]
"""T 粤文 translation test cases."""

__all__ = [
    "t_translate_test_cases",
]
