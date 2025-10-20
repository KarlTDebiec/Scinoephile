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
        yuewen_1_shifted="喂警察",
        yuewen_2_shifted="攞我新闻证出嚟睇",
    ),
]  # shift_test_cases_block_0
shift_test_cases_block_1 = [
    ShiftTestCase(
        zhongwen_1="﹣检查一下　　﹣收到",
        yuewen_1="查下咩料收到",
        zhongwen_2="﹣袋子里装什么？　　﹣总机",
        yuewen_2="角度系袋住啲咩呀",
        yuewen_1_shifted="查下咩料",
        yuewen_2_shifted="收到角度系袋住啲咩呀",
        difficulty=1,
    ),
    ShiftTestCase(
        zhongwen_1="﹣袋子里装什么？　　﹣总机",
        yuewen_1="收到角度系袋住啲咩呀",
        zhongwen_2="﹣打开来看看　　﹣身份证号码：C532743",
        yuewen_2="通话电台查查个牌匙C532743",
        yuewen_1_shifted="收到角度系袋住啲咩呀",
        yuewen_2_shifted="通话电台查查个牌匙C532743",
    ),
    ShiftTestCase(
        zhongwen_1="﹣打开来看看　　﹣身份证号码：C532743",
        yuewen_1="通话电台查查个牌匙C532743",
        zhongwen_2="尾数一，季正雄",
        yuewen_2="尾数1贵正红",
        yuewen_1_shifted="通话电台查查个牌匙C532743",
        yuewen_2_shifted="尾数1贵正红",
    ),
    ShiftTestCase(
        zhongwen_1="尾数一，季正雄",
        yuewen_1="尾数1贵正红",
        zhongwen_2="打开",
        yuewen_2="打佢",
        yuewen_1_shifted="尾数1贵正红",
        yuewen_2_shifted="打佢",
    ),
]  # shift_test_cases_block_1
shift_test_cases_block_2 = [
    ShiftTestCase(
        zhongwen_1="协议中有关香港的安排",
        yuewen_1="嘅arrangementsforHong",
        zhongwen_2="不是权宜之计",
        yuewen_2="Kongcontainedinthe",
        yuewen_1_shifted="嘅arrangementsforHongKongcontainedinthe",
        yuewen_2_shifted="",
        difficulty=1,
    ),
    ShiftTestCase(
        zhongwen_1="不是权宜之计",
        yuewen_1="",
        zhongwen_2="这些安排是长期的政策",
        yuewen_2="agreement而notmeasuresofexpediency",
        yuewen_1_shifted="agreement而",
        yuewen_2_shifted="notmeasuresofexpediency",
        difficulty=1,
    ),
    ShiftTestCase(
        zhongwen_1="这些安排是长期的政策",
        yuewen_1="notmeasuresofexpediency",
        zhongwen_2="它们将写入为香港制定的基本法",
        yuewen_2="嘅好longtermpoliciesWhichwillbe",
        yuewen_1_shifted="notmeasuresofexpediency嘅好longtermpolicies",
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
        yuewen_1_shifted="也是我们双方共同的",
        yuewen_2_shifted="",
        difficulty=1,
    ),
]  # shift_test_cases_block_2
shift_test_cases_block_3 = []  # shift_test_cases_block_3
shift_test_cases_block_4 = []  # shift_test_cases_block_4
shift_test_cases_block_5 = []  # shift_test_cases_block_5
shift_test_cases_block_6 = []  # shift_test_cases_block_6
shift_test_cases_block_7 = []  # shift_test_cases_block_7
shift_test_cases_block_8 = []  # shift_test_cases_block_8
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
