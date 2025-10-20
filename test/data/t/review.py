#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for T."""

from __future__ import annotations

from scinoephile.audio.cantonese.review.abcs import ReviewTestCase

review_test_case_block_0 = ReviewTestCase.get_test_case_cls(2)(
    zhongwen_1="警察",
    yuewen_1="喂警察",
    zhongwen_2="拿身份证出来",
    yuewen_2="攞我身份证出嚟睇",
    yuewen_revised_1="警察",
    note_1="Removed '喂' to match the context and maintain consistency, "
    "as the rest of the subtitles do not include interjections "
    "and the speech likely starts directly with '警察'.",
    yuewen_revised_2="",
    note_2="",
)  # review_test_case_block_0
review_test_case_block_1 = ReviewTestCase.get_test_case_cls(5)(
    zhongwen_1="﹣检查一下　　﹣收到",
    yuewen_1="﹣查下先　　﹣收到",
    zhongwen_2="﹣袋子里装什么？　　﹣总机",
    yuewen_2="袋入面装住咩呀？",
    zhongwen_3="﹣打开来看看　　﹣身份证号码：C532743",
    yuewen_3="打開嚟睇下，身份證號碼：C532743",
    zhongwen_4="尾数一，季正雄",
    yuewen_4="尾数1，季正雄",
    zhongwen_5="打开",
    yuewen_5="打開",
    yuewen_revised_1="",
    note_1="",
    yuewen_revised_2="袋入面裝住咩呀？總機",
    note_2="Added '總機' to match the implied response in the sequence, as "
    "the next subtitle references an ID number, indicating a "
    "reply was missing in the previous subtitle.",
    yuewen_revised_3="",
    note_3="",
    yuewen_revised_4="",
    note_4="",
    yuewen_revised_5="",
    note_5="",
)  # review_test_case_block_1
review_test_case_block_2 = ReviewTestCase.get_test_case_cls(10)(
    zhongwen_1="协议中有关香港的安排",
    yuewen_1="协议中有关香港嘅安排",
    zhongwen_2="不是权宜之计",
    yuewen_2="唔係权宜之计",
    zhongwen_3="这些安排是长期的政策",
    yuewen_3="而not measures of expediency嘅好long term policies。",
    zhongwen_4="它们将写入为香港制定的基本法",
    yuewen_4="呢啲安排会写入为香港制定嘅基本法入面",
    zhongwen_5="五十年不变",
    yuewen_5="五十年都唔变",
    zhongwen_6="五十年不变",
    yuewen_6="五十年都唔变",
    zhongwen_7="确保《联合声明》",
    yuewen_7="确保《联合声明》",
    zhongwen_8="不受干扰地全面贯彻实施",
    yuewen_8="可以唔受干扰咁全面贯彻落实",
    zhongwen_9="是中英两国的共同利益",
    yuewen_9="也是我哋双方共同嘅",
    zhongwen_10="也是我们双方共同的责任",
    yuewen_10="都系我哋双方共同嘅责任",
    yuewen_revised_1="",
    note_1="",
    yuewen_revised_2="",
    note_2="",
    yuewen_revised_3="呢啲安排唔係权宜之计，而係好long term policies。",
    note_3="Revised to provide a more natural and accurate sequence in "
    "Cantonese, connecting the ideas and removing the English "
    "phrase 'not measures of expediency' which was out of place. "
    "Now it reads as a single, coherent statement in Cantonese.",
    yuewen_revised_4="",
    note_4="",
    yuewen_revised_5="",
    note_5="",
    yuewen_revised_6="",
    note_6="",
    yuewen_revised_7="",
    note_7="",
    yuewen_revised_8="",
    note_8="",
    yuewen_revised_9="都系我哋双方共同嘅利益",
    note_9="Revised to include '利益' (interests) at the end, to match the "
    "meaning of the original and to maintain consistency with the "
    "next subtitle, which refers to '责任' (responsibility).",
    yuewen_revised_10="",
    note_10="",
)  # review_test_case_block_2
review_test_case_block_3 = None  # review_test_case_block_3
review_test_case_block_4 = None  # review_test_case_block_4
review_test_case_block_5 = None  # review_test_case_block_5
review_test_case_block_6 = None  # review_test_case_block_6
review_test_case_block_7 = None  # review_test_case_block_7
review_test_case_block_8 = None  # review_test_case_block_8
review_test_case_block_9 = None  # review_test_case_block_9
review_test_case_block_10 = None  # review_test_case_block_10
review_test_case_block_11 = None  # review_test_case_block_11
review_test_case_block_12 = None  # review_test_case_block_12
review_test_case_block_13 = None  # review_test_case_block_13
review_test_case_block_14 = None  # review_test_case_block_14
review_test_case_block_15 = None  # review_test_case_block_15
review_test_case_block_16 = None  # review_test_case_block_16
review_test_case_block_17 = None  # review_test_case_block_17
review_test_case_block_18 = None  # review_test_case_block_18
review_test_case_block_19 = None  # review_test_case_block_19
review_test_case_block_20 = None  # review_test_case_block_20
review_test_case_block_21 = None  # review_test_case_block_21
review_test_case_block_22 = None  # review_test_case_block_22
review_test_case_block_23 = None  # review_test_case_block_23
review_test_case_block_24 = None  # review_test_case_block_24
review_test_case_block_25 = None  # review_test_case_block_25
review_test_case_block_26 = None  # review_test_case_block_26
review_test_case_block_27 = None  # review_test_case_block_27
review_test_case_block_28 = None  # review_test_case_block_28
review_test_case_block_29 = None  # review_test_case_block_29
review_test_case_block_30 = None  # review_test_case_block_30
review_test_case_block_31 = None  # review_test_case_block_31
review_test_case_block_32 = None  # review_test_case_block_32
review_test_case_block_33 = None  # review_test_case_block_33
review_test_case_block_34 = None  # review_test_case_block_34
review_test_case_block_35 = None  # review_test_case_block_35
review_test_case_block_36 = None  # review_test_case_block_36
review_test_case_block_37 = None  # review_test_case_block_37
review_test_case_block_38 = None  # review_test_case_block_38
review_test_case_block_39 = None  # review_test_case_block_39
review_test_case_block_40 = None  # review_test_case_block_40
review_test_case_block_41 = None  # review_test_case_block_41
review_test_case_block_42 = None  # review_test_case_block_42
review_test_case_block_43 = None  # review_test_case_block_43
review_test_case_block_44 = None  # review_test_case_block_44
review_test_case_block_45 = None  # review_test_case_block_45
review_test_case_block_46 = None  # review_test_case_block_46
review_test_case_block_47 = None  # review_test_case_block_47
review_test_case_block_48 = None  # review_test_case_block_48
review_test_case_block_49 = None  # review_test_case_block_49
review_test_case_block_50 = None  # review_test_case_block_50
review_test_case_block_51 = None  # review_test_case_block_51
review_test_case_block_52 = None  # review_test_case_block_52
review_test_case_block_53 = None  # review_test_case_block_53
review_test_case_block_54 = None  # review_test_case_block_54
review_test_case_block_55 = None  # review_test_case_block_55
review_test_case_block_56 = None  # review_test_case_block_56
review_test_case_block_57 = None  # review_test_case_block_57
review_test_case_block_58 = None  # review_test_case_block_58
review_test_case_block_59 = None  # review_test_case_block_59
review_test_case_block_60 = None  # review_test_case_block_60
review_test_case_block_61 = None  # review_test_case_block_61
review_test_case_block_62 = None  # review_test_case_block_62
review_test_case_block_63 = None  # review_test_case_block_63
review_test_case_block_64 = None  # review_test_case_block_64
review_test_case_block_65 = None  # review_test_case_block_65
review_test_case_block_66 = None  # review_test_case_block_66
review_test_case_block_67 = None  # review_test_case_block_67
review_test_case_block_68 = None  # review_test_case_block_68
review_test_case_block_69 = None  # review_test_case_block_69
review_test_case_block_70 = None  # review_test_case_block_70
review_test_case_block_71 = None  # review_test_case_block_71
review_test_case_block_72 = None  # review_test_case_block_72
review_test_case_block_73 = None  # review_test_case_block_73
review_test_case_block_74 = None  # review_test_case_block_74
review_test_case_block_75 = None  # review_test_case_block_75
review_test_case_block_76 = None  # review_test_case_block_76
review_test_case_block_77 = None  # review_test_case_block_77
review_test_case_block_78 = None  # review_test_case_block_78
review_test_case_block_79 = None  # review_test_case_block_79
review_test_case_block_80 = None  # review_test_case_block_80
review_test_case_block_81 = None  # review_test_case_block_81
review_test_case_block_82 = None  # review_test_case_block_82
review_test_case_block_83 = None  # review_test_case_block_83
review_test_case_block_84 = None  # review_test_case_block_84
review_test_case_block_85 = None  # review_test_case_block_85
review_test_case_block_86 = None  # review_test_case_block_86
review_test_case_block_87 = None  # review_test_case_block_87
review_test_case_block_88 = None  # review_test_case_block_88
review_test_case_block_89 = None  # review_test_case_block_89
review_test_case_block_90 = None  # review_test_case_block_90
review_test_case_block_91 = None  # review_test_case_block_91
review_test_case_block_92 = None  # review_test_case_block_92
review_test_case_block_93 = None  # review_test_case_block_93
review_test_case_block_94 = None  # review_test_case_block_94
review_test_case_block_95 = None  # review_test_case_block_95
review_test_case_block_96 = None  # review_test_case_block_96
review_test_case_block_97 = None  # review_test_case_block_97
review_test_case_block_98 = None  # review_test_case_block_98
review_test_case_block_99 = None  # review_test_case_block_99
review_test_case_block_100 = None  # review_test_case_block_100
review_test_case_block_101 = None  # review_test_case_block_101
review_test_case_block_102 = None  # review_test_case_block_102
review_test_case_block_103 = None  # review_test_case_block_103
review_test_case_block_104 = None  # review_test_case_block_104
review_test_case_block_105 = None  # review_test_case_block_105
review_test_case_block_106 = None  # review_test_case_block_106
review_test_case_block_107 = None  # review_test_case_block_107
review_test_case_block_108 = None  # review_test_case_block_108
review_test_case_block_109 = None  # review_test_case_block_109
review_test_case_block_110 = None  # review_test_case_block_110
review_test_case_block_111 = None  # review_test_case_block_111
review_test_case_block_112 = None  # review_test_case_block_112
review_test_case_block_113 = None  # review_test_case_block_113
review_test_case_block_114 = None  # review_test_case_block_114
review_test_case_block_115 = None  # review_test_case_block_115
review_test_case_block_116 = None  # review_test_case_block_116
review_test_case_block_117 = None  # review_test_case_block_117
review_test_case_block_118 = None  # review_test_case_block_118
review_test_case_block_119 = None  # review_test_case_block_119
review_test_case_block_120 = None  # review_test_case_block_120
review_test_case_block_121 = None  # review_test_case_block_121
review_test_case_block_122 = None  # review_test_case_block_122
review_test_case_block_123 = None  # review_test_case_block_123
review_test_case_block_124 = None  # review_test_case_block_124
review_test_case_block_125 = None  # review_test_case_block_125
review_test_case_block_126 = None  # review_test_case_block_126
review_test_case_block_127 = None  # review_test_case_block_127
review_test_case_block_128 = None  # review_test_case_block_128
review_test_case_block_129 = None  # review_test_case_block_129
review_test_case_block_130 = None  # review_test_case_block_130
review_test_case_block_131 = None  # review_test_case_block_131
review_test_case_block_132 = None  # review_test_case_block_132
review_test_case_block_133 = None  # review_test_case_block_133
review_test_case_block_134 = None  # review_test_case_block_134
review_test_case_block_135 = None  # review_test_case_block_135
review_test_case_block_136 = None  # review_test_case_block_136
review_test_case_block_137 = None  # review_test_case_block_137
review_test_case_block_138 = None  # review_test_case_block_138
review_test_case_block_139 = None  # review_test_case_block_139
review_test_case_block_140 = None  # review_test_case_block_140
review_test_case_block_141 = None  # review_test_case_block_141
review_test_case_block_142 = None  # review_test_case_block_142
review_test_case_block_143 = None  # review_test_case_block_143
review_test_case_block_144 = None  # review_test_case_block_144
review_test_case_block_145 = None  # review_test_case_block_145
review_test_case_block_146 = None  # review_test_case_block_146
review_test_case_block_147 = None  # review_test_case_block_147
review_test_case_block_148 = None  # review_test_case_block_148
review_test_case_block_149 = None  # review_test_case_block_149
review_test_case_block_150 = None  # review_test_case_block_150
review_test_case_block_151 = None  # review_test_case_block_151
review_test_case_block_152 = None  # review_test_case_block_152
review_test_case_block_153 = None  # review_test_case_block_153
review_test_case_block_154 = None  # review_test_case_block_154
review_test_case_block_155 = None  # review_test_case_block_155
review_test_case_block_156 = None  # review_test_case_block_156
review_test_case_block_157 = None  # review_test_case_block_157
review_test_case_block_158 = None  # review_test_case_block_158
review_test_case_block_159 = None  # review_test_case_block_159
review_test_case_block_160 = None  # review_test_case_block_160
review_test_case_block_161 = None  # review_test_case_block_161
review_test_case_block_162 = None  # review_test_case_block_162
review_test_case_block_163 = None  # review_test_case_block_163
review_test_case_block_164 = None  # review_test_case_block_164
review_test_case_block_165 = None  # review_test_case_block_165
review_test_case_block_166 = None  # review_test_case_block_166
review_test_case_block_167 = None  # review_test_case_block_167
review_test_case_block_168 = None  # review_test_case_block_168
review_test_case_block_169 = None  # review_test_case_block_169
review_test_case_block_170 = None  # review_test_case_block_170
review_test_case_block_171 = None  # review_test_case_block_171
review_test_case_block_172 = None  # review_test_case_block_172
review_test_case_block_173 = None  # review_test_case_block_173
review_test_case_block_174 = None  # review_test_case_block_174
review_test_case_block_175 = None  # review_test_case_block_175
review_test_case_block_176 = None  # review_test_case_block_176
review_test_case_block_177 = None  # review_test_case_block_177
review_test_case_block_178 = None  # review_test_case_block_178
review_test_case_block_179 = None  # review_test_case_block_179
review_test_case_block_180 = None  # review_test_case_block_180
review_test_case_block_181 = None  # review_test_case_block_181

t_review_test_cases: list[ReviewTestCase] = [
    test_case
    for name, test_case in globals().items()
    if name.startswith("review_test_case_block_") and test_case is not None
]
"""T 粤文 review test cases."""

__all__ = [
    "t_review_test_cases",
]
