#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""T English proof test cases."""

from __future__ import annotations

from scinoephile.core.english.proofing.abcs import EnglishProofTestCase

# noinspection PyArgumentList
test_case_block_0 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="Police.",
    subtitle_2="Show me your ID.",
)  # test_case_block_0
# noinspection PyArgumentList
test_case_block_1 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="- Check his ID.\n- Yes sir.",
    subtitle_2="- What's in your bag?\n- Headquarter,",
    subtitle_3="- Let me see.\n- please verify ID number C532743...",
    subtitle_4="Bracket 1, Kwai Ching-hung.",
    subtitle_5="Open it.",
    revised_3="- Let me see.\n- Please verify ID number C532743...",
    note_3="Capitalized 'please' at the start of the sentence.",
    difficulty=1,
)  # test_case_block_1
# noinspection PyArgumentList
test_case_block_2 = EnglishProofTestCase.get_test_case_cls(10)(
    subtitle_1="The arrangement for Hong Kong",
    subtitle_2="contained in the agreement\nare not measures of expediency.",
    subtitle_3="contained in the agreement\nare not measures of expediency.",
    subtitle_4="They are long-term policies which will be incorporated",
    subtitle_5="in the Basic Law for Hong Kong",
    subtitle_6="and preserved intact for 50 years from 1997.",
    subtitle_7="It is the common interests",
    subtitle_8="as well as shared responsibilities of China and Britain",
    subtitle_9="to ensure the Joint Declaration is fully\n"
    "implemented with no encumbrances.",
    subtitle_10="to ensure the Joint Declaration is fully\n"
    "implemented with no encumbrances.",
    revised_2="contained in the agreement\nare not measures of expediency",
    note_2="Removed period at the end to match subtitle style.",
    revised_3="contained in the agreement\nare not measures of expediency",
    note_3="Removed period at the end to match subtitle style.",
    revised_7="It is in the common interests",
    note_7="Added 'in' to correct the phrase to 'It is in the common interests'.",
    difficulty=1,
)  # test_case_block_2
# noinspection PyArgumentList
test_case_block_3 = EnglishProofTestCase.get_test_case_cls(17)(
    subtitle_1="An armed robbery took place this afternoon in Kwun Tong.",
    subtitle_2="4 armed suspects robbed 5 gold shops\non Mut Wah Street.",
    subtitle_3="4 armed suspects robbed 5 gold shops\non Mut Wah Street.",
    subtitle_4="Fuck you!",
    subtitle_5="In the footage provided by our audience,",
    subtitle_6="the robbers exchanged fire",
    subtitle_7="with the Special Duties Unit.",
    subtitle_8="2 passersby and 3 policemen\nwere injured in the incident.",
    subtitle_9="The 5 gold shops lost $10M in total.",
    subtitle_10="The police believe the mastermind",
    subtitle_11='is the "Most Wanted" Yip Kwok-foon.',
    subtitle_12="Bro Foon, you're unbeatable!",
    subtitle_13="Bro Foon, you're unbeatable!",
    subtitle_14="But shit has hit the fan!",
    subtitle_15="I told you to put more newspaper underneath!",
    subtitle_16="Look, there's blood everywhere!",
    subtitle_17="Take it, jerk!",
)  # test_case_block_3
# noinspection PyArgumentList
test_case_block_4 = EnglishProofTestCase.get_test_case_cls(10)(
    subtitle_1="Shit has really hit the fan!",
    subtitle_2="I can give you 20% tops. Sorry.",
    subtitle_3="We agreed on 40%.",
    subtitle_4="Don't you have moral principle?",
    subtitle_5="You're paying $2M for $10M's worth of swag?",
    subtitle_6="We used to get 50%!",
    subtitle_7="Now you fences are getting it all!",
    subtitle_8="We're getting shit!",
    subtitle_9="Time has changed.",
    subtitle_10="The cops are on the prowl!",
    revised_4="Don't you have any moral principles?",
    note_4="Added 'any' and changed 'principle' to plural 'principles' "
    "for natural phrasing.",
    revised_7="Now you fences are getting everything!",
    note_7="Changed 'it all' to 'everything' for more natural phrasing.",
    revised_9="Times have changed.",
    note_9="Changed 'Time has changed.' to 'Times have changed.' for "
    "correct idiomatic usage.",
    difficulty=1,
)  # test_case_block_4
# noinspection PyArgumentList
test_case_block_5 = EnglishProofTestCase.get_test_case_cls(6)(
    subtitle_1="Especially for your swag, Bro Foon!",
    subtitle_2="It took us 2 years to fence it last time!",
    subtitle_3="Stocks, real estate,\nand even chestnuts are more profitable!",
    subtitle_4="Do me a favor.",
    subtitle_5="40%.",
    subtitle_6="Bro Foon, you always have your way!",
)  # test_case_block_5
# noinspection PyArgumentList
test_case_block_6 = None  # test_case_block_6
# noinspection PyArgumentList
test_case_block_7 = None  # test_case_block_7
# noinspection PyArgumentList
test_case_block_8 = None  # test_case_block_8
# noinspection PyArgumentList
test_case_block_9 = None  # test_case_block_9
# noinspection PyArgumentList
test_case_block_10 = None  # test_case_block_10
# noinspection PyArgumentList
test_case_block_11 = None  # test_case_block_11
# noinspection PyArgumentList
test_case_block_12 = None  # test_case_block_12
# noinspection PyArgumentList
test_case_block_13 = None  # test_case_block_13
# noinspection PyArgumentList
test_case_block_14 = None  # test_case_block_14
# noinspection PyArgumentList
test_case_block_15 = None  # test_case_block_15
# noinspection PyArgumentList
test_case_block_16 = None  # test_case_block_16
# noinspection PyArgumentList
test_case_block_17 = None  # test_case_block_17
# noinspection PyArgumentList
test_case_block_18 = None  # test_case_block_18
# noinspection PyArgumentList
test_case_block_19 = None  # test_case_block_19
# noinspection PyArgumentList
test_case_block_20 = None  # test_case_block_20
# noinspection PyArgumentList
test_case_block_21 = None  # test_case_block_21
# noinspection PyArgumentList
test_case_block_22 = None  # test_case_block_22
# noinspection PyArgumentList
test_case_block_23 = None  # test_case_block_23
# noinspection PyArgumentList
test_case_block_24 = None  # test_case_block_24
# noinspection PyArgumentList
test_case_block_25 = None  # test_case_block_25
# noinspection PyArgumentList
test_case_block_26 = None  # test_case_block_26
# noinspection PyArgumentList
test_case_block_27 = None  # test_case_block_27
# noinspection PyArgumentList
test_case_block_28 = None  # test_case_block_28
# noinspection PyArgumentList
test_case_block_29 = None  # test_case_block_29
# noinspection PyArgumentList
test_case_block_30 = None  # test_case_block_30
# noinspection PyArgumentList
test_case_block_31 = None  # test_case_block_31
# noinspection PyArgumentList
test_case_block_32 = None  # test_case_block_32
# noinspection PyArgumentList
test_case_block_33 = None  # test_case_block_33
# noinspection PyArgumentList
test_case_block_34 = None  # test_case_block_34
# noinspection PyArgumentList
test_case_block_35 = None  # test_case_block_35
# noinspection PyArgumentList
test_case_block_36 = None  # test_case_block_36
# noinspection PyArgumentList
test_case_block_37 = None  # test_case_block_37
# noinspection PyArgumentList
test_case_block_38 = None  # test_case_block_38
# noinspection PyArgumentList
test_case_block_39 = None  # test_case_block_39
# noinspection PyArgumentList
test_case_block_40 = None  # test_case_block_40
# noinspection PyArgumentList
test_case_block_41 = None  # test_case_block_41
# noinspection PyArgumentList
test_case_block_42 = None  # test_case_block_42
# noinspection PyArgumentList
test_case_block_43 = None  # test_case_block_43
# noinspection PyArgumentList
test_case_block_44 = None  # test_case_block_44
# noinspection PyArgumentList
test_case_block_45 = None  # test_case_block_45
# noinspection PyArgumentList
test_case_block_46 = None  # test_case_block_46
# noinspection PyArgumentList
test_case_block_47 = None  # test_case_block_47
# noinspection PyArgumentList
test_case_block_48 = None  # test_case_block_48
# noinspection PyArgumentList
test_case_block_49 = None  # test_case_block_49
# noinspection PyArgumentList
test_case_block_50 = None  # test_case_block_50
# noinspection PyArgumentList
test_case_block_51 = None  # test_case_block_51
# noinspection PyArgumentList
test_case_block_52 = None  # test_case_block_52
# noinspection PyArgumentList
test_case_block_53 = None  # test_case_block_53
# noinspection PyArgumentList
test_case_block_54 = None  # test_case_block_54
# noinspection PyArgumentList
test_case_block_55 = None  # test_case_block_55
# noinspection PyArgumentList
test_case_block_56 = None  # test_case_block_56
# noinspection PyArgumentList
test_case_block_57 = None  # test_case_block_57
# noinspection PyArgumentList
test_case_block_58 = None  # test_case_block_58
# noinspection PyArgumentList
test_case_block_59 = None  # test_case_block_59
# noinspection PyArgumentList
test_case_block_60 = None  # test_case_block_60
# noinspection PyArgumentList
test_case_block_61 = None  # test_case_block_61
# noinspection PyArgumentList
test_case_block_62 = None  # test_case_block_62
# noinspection PyArgumentList
test_case_block_63 = None  # test_case_block_63
# noinspection PyArgumentList
test_case_block_64 = None  # test_case_block_64
# noinspection PyArgumentList
test_case_block_65 = None  # test_case_block_65
# noinspection PyArgumentList
test_case_block_66 = None  # test_case_block_66
# noinspection PyArgumentList
test_case_block_67 = None  # test_case_block_67
# noinspection PyArgumentList
test_case_block_68 = None  # test_case_block_68
# noinspection PyArgumentList
test_case_block_69 = None  # test_case_block_69
# noinspection PyArgumentList
test_case_block_70 = None  # test_case_block_70
# noinspection PyArgumentList
test_case_block_71 = None  # test_case_block_71
# noinspection PyArgumentList
test_case_block_72 = None  # test_case_block_72
# noinspection PyArgumentList
test_case_block_73 = None  # test_case_block_73
# noinspection PyArgumentList
test_case_block_74 = None  # test_case_block_74
# noinspection PyArgumentList
test_case_block_75 = None  # test_case_block_75
# noinspection PyArgumentList
test_case_block_76 = None  # test_case_block_76
# noinspection PyArgumentList
test_case_block_77 = None  # test_case_block_77
# noinspection PyArgumentList
test_case_block_78 = None  # test_case_block_78
# noinspection PyArgumentList
test_case_block_79 = None  # test_case_block_79
# noinspection PyArgumentList
test_case_block_80 = None  # test_case_block_80
# noinspection PyArgumentList
test_case_block_81 = None  # test_case_block_81
# noinspection PyArgumentList
test_case_block_82 = None  # test_case_block_82
# noinspection PyArgumentList
test_case_block_83 = None  # test_case_block_83
# noinspection PyArgumentList
test_case_block_84 = None  # test_case_block_84
# noinspection PyArgumentList
test_case_block_85 = None  # test_case_block_85
# noinspection PyArgumentList
test_case_block_86 = None  # test_case_block_86
# noinspection PyArgumentList
test_case_block_87 = None  # test_case_block_87
# noinspection PyArgumentList
test_case_block_88 = None  # test_case_block_88
# noinspection PyArgumentList
test_case_block_89 = None  # test_case_block_89
# noinspection PyArgumentList
test_case_block_90 = None  # test_case_block_90
# noinspection PyArgumentList
test_case_block_91 = None  # test_case_block_91
# noinspection PyArgumentList
test_case_block_92 = None  # test_case_block_92
# noinspection PyArgumentList
test_case_block_93 = None  # test_case_block_93
# noinspection PyArgumentList
test_case_block_94 = None  # test_case_block_94
# noinspection PyArgumentList
test_case_block_95 = None  # test_case_block_95
# noinspection PyArgumentList
test_case_block_96 = None  # test_case_block_96
# noinspection PyArgumentList
test_case_block_97 = None  # test_case_block_97
# noinspection PyArgumentList
test_case_block_98 = None  # test_case_block_98
# noinspection PyArgumentList
test_case_block_99 = None  # test_case_block_99
# noinspection PyArgumentList
test_case_block_100 = None  # test_case_block_100
# noinspection PyArgumentList
test_case_block_101 = None  # test_case_block_101
# noinspection PyArgumentList
test_case_block_102 = None  # test_case_block_102
# noinspection PyArgumentList
test_case_block_103 = None  # test_case_block_103
# noinspection PyArgumentList
test_case_block_104 = None  # test_case_block_104
# noinspection PyArgumentList
test_case_block_105 = None  # test_case_block_105
# noinspection PyArgumentList
test_case_block_106 = None  # test_case_block_106
# noinspection PyArgumentList
test_case_block_107 = None  # test_case_block_107
# noinspection PyArgumentList
test_case_block_108 = None  # test_case_block_108
# noinspection PyArgumentList
test_case_block_109 = None  # test_case_block_109
# noinspection PyArgumentList
test_case_block_110 = None  # test_case_block_110
# noinspection PyArgumentList
test_case_block_111 = None  # test_case_block_111
# noinspection PyArgumentList
test_case_block_112 = None  # test_case_block_112
# noinspection PyArgumentList
test_case_block_113 = None  # test_case_block_113
# noinspection PyArgumentList
test_case_block_114 = None  # test_case_block_114
# noinspection PyArgumentList
test_case_block_115 = None  # test_case_block_115
# noinspection PyArgumentList
test_case_block_116 = None  # test_case_block_116
# noinspection PyArgumentList
test_case_block_117 = None  # test_case_block_117
# noinspection PyArgumentList
test_case_block_118 = None  # test_case_block_118
# noinspection PyArgumentList
test_case_block_119 = None  # test_case_block_119
# noinspection PyArgumentList
test_case_block_120 = None  # test_case_block_120
# noinspection PyArgumentList
test_case_block_121 = None  # test_case_block_121
# noinspection PyArgumentList
test_case_block_122 = None  # test_case_block_122
# noinspection PyArgumentList
test_case_block_123 = None  # test_case_block_123
# noinspection PyArgumentList
test_case_block_124 = None  # test_case_block_124
# noinspection PyArgumentList
test_case_block_125 = None  # test_case_block_125
# noinspection PyArgumentList
test_case_block_126 = None  # test_case_block_126
# noinspection PyArgumentList
test_case_block_127 = None  # test_case_block_127
# noinspection PyArgumentList
test_case_block_128 = None  # test_case_block_128
# noinspection PyArgumentList
test_case_block_129 = None  # test_case_block_129
# noinspection PyArgumentList
test_case_block_130 = None  # test_case_block_130
# noinspection PyArgumentList
test_case_block_131 = None  # test_case_block_131
# noinspection PyArgumentList
test_case_block_132 = None  # test_case_block_132
# noinspection PyArgumentList
test_case_block_133 = None  # test_case_block_133
# noinspection PyArgumentList
test_case_block_134 = None  # test_case_block_134
# noinspection PyArgumentList
test_case_block_135 = None  # test_case_block_135
# noinspection PyArgumentList
test_case_block_136 = None  # test_case_block_136
# noinspection PyArgumentList
test_case_block_137 = None  # test_case_block_137
# noinspection PyArgumentList
test_case_block_138 = None  # test_case_block_138
# noinspection PyArgumentList
test_case_block_139 = None  # test_case_block_139
# noinspection PyArgumentList
test_case_block_140 = None  # test_case_block_140
# noinspection PyArgumentList
test_case_block_141 = None  # test_case_block_141
# noinspection PyArgumentList
test_case_block_142 = None  # test_case_block_142
# noinspection PyArgumentList
test_case_block_143 = None  # test_case_block_143
# noinspection PyArgumentList
test_case_block_144 = None  # test_case_block_144
# noinspection PyArgumentList
test_case_block_145 = None  # test_case_block_145
# noinspection PyArgumentList
test_case_block_146 = None  # test_case_block_146
# noinspection PyArgumentList
test_case_block_147 = None  # test_case_block_147
# noinspection PyArgumentList
test_case_block_148 = None  # test_case_block_148
# noinspection PyArgumentList
test_case_block_149 = None  # test_case_block_149
# noinspection PyArgumentList
test_case_block_150 = None  # test_case_block_150
# noinspection PyArgumentList
test_case_block_151 = None  # test_case_block_151
# noinspection PyArgumentList
test_case_block_152 = None  # test_case_block_152
# noinspection PyArgumentList
test_case_block_153 = None  # test_case_block_153
# noinspection PyArgumentList
test_case_block_154 = None  # test_case_block_154
# noinspection PyArgumentList
test_case_block_155 = None  # test_case_block_155
# noinspection PyArgumentList
test_case_block_156 = None  # test_case_block_156
# noinspection PyArgumentList
test_case_block_157 = None  # test_case_block_157
# noinspection PyArgumentList
test_case_block_158 = None  # test_case_block_158
# noinspection PyArgumentList
test_case_block_159 = None  # test_case_block_159
# noinspection PyArgumentList
test_case_block_160 = None  # test_case_block_160
# noinspection PyArgumentList
test_case_block_161 = None  # test_case_block_161
# noinspection PyArgumentList
test_case_block_162 = None  # test_case_block_162
# noinspection PyArgumentList
test_case_block_163 = None  # test_case_block_163
# noinspection PyArgumentList
test_case_block_164 = None  # test_case_block_164
# noinspection PyArgumentList
test_case_block_165 = None  # test_case_block_165
# noinspection PyArgumentList
test_case_block_166 = None  # test_case_block_166
# noinspection PyArgumentList
test_case_block_167 = None  # test_case_block_167
# noinspection PyArgumentList
test_case_block_168 = None  # test_case_block_168
# noinspection PyArgumentList
test_case_block_169 = None  # test_case_block_169
# noinspection PyArgumentList
test_case_block_170 = None  # test_case_block_170
# noinspection PyArgumentList
test_case_block_171 = None  # test_case_block_171
# noinspection PyArgumentList
test_case_block_172 = None  # test_case_block_172
# noinspection PyArgumentList
test_case_block_173 = None  # test_case_block_173
# noinspection PyArgumentList
test_case_block_174 = None  # test_case_block_174
# noinspection PyArgumentList
test_case_block_175 = None  # test_case_block_175
# noinspection PyArgumentList
test_case_block_176 = None  # test_case_block_176
# noinspection PyArgumentList
test_case_block_177 = None  # test_case_block_177
# noinspection PyArgumentList
test_case_block_178 = None  # test_case_block_178
# noinspection PyArgumentList
test_case_block_179 = None  # test_case_block_179
# noinspection PyArgumentList
test_case_block_180 = None  # test_case_block_180
# noinspection PyArgumentList
test_case_block_181 = None  # test_case_block_181
# noinspection PyArgumentList
test_case_block_182 = None  # test_case_block_182
# noinspection PyArgumentList
test_case_block_183 = None  # test_case_block_183
# noinspection PyArgumentList
test_case_block_184 = None  # test_case_block_184
# noinspection PyArgumentList
test_case_block_185 = None  # test_case_block_185
# noinspection PyArgumentList
test_case_block_186 = None  # test_case_block_186
# noinspection PyArgumentList
test_case_block_187 = None  # test_case_block_187
# noinspection PyArgumentList
test_case_block_188 = None  # test_case_block_188
# noinspection PyArgumentList
test_case_block_189 = None  # test_case_block_189
# noinspection PyArgumentList
test_case_block_190 = None  # test_case_block_190
# noinspection PyArgumentList
test_case_block_191 = None  # test_case_block_191
# noinspection PyArgumentList
test_case_block_192 = None  # test_case_block_192
# noinspection PyArgumentList
test_case_block_193 = None  # test_case_block_193


t_english_proof_test_cases: list[EnglishProofTestCase] = [
    test_case
    for name, test_case in globals().items()
    if name.startswith("test_case_block_") and test_case is not None
]
"""T English proof test cases."""

__all__ = [
    "t_english_proof_test_cases",
]
