#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for T."""

from __future__ import annotations

from itertools import chain

from scinoephile.audio.cantonese.proofing import ProofTestCase

proof_test_cases_block_0 = [
    ProofTestCase(
        zhongwen="警察",
        yuewen="喂",
        yuewen_proofread="",
        note="The 粤文 '喂' (hello/hey) has no correspondence to the 中文 '警察' "
        "(police), indicating a complete mistranscription.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="拿身份证出来",
        yuewen="警察攞我新闻证出嚟睇",
        yuewen_proofread="攞身份证出嚟",
        note="Corrected '新闻证' (press card) to '身份证' (ID card), as the "
        "original likely misheard the word; the rest is fine.",
        difficulty=1,
    ),
]  # proof_test_cases_block_0
proof_test_cases_block_1 = [
    ProofTestCase(
        zhongwen="﹣检查一下　　﹣收到",
        yuewen="查下咩料",
        yuewen_proofread="查下先",
        note="Changed '查下咩料' to '查下先' because '查下咩料' does not correspond "
        "to '检查一下' and is likely a mishearing; '查下先' is a common "
        "Cantonese way to say 'check for a bit'.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="﹣袋子里装什么？　　﹣总机",
        yuewen="收到，角度系袋住啲咩呀？",
        yuewen_proofread="袋入面装住咩呀？",
        note="Changed '角度系袋住啲咩呀？' to '袋入面装住咩呀？' because '角度' is a clear "
        "mishearing of '袋度' (in the bag), which matches the context "
        "of asking what's in the bag.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="﹣打开来看看　　﹣身份证号码：C532743",
        yuewen="通话电台 查 查个牌匙：C532743",
        yuewen_proofread="打開嚟睇下，身份證號碼：C532743",
        note="Corrected '通话电台 查 查个牌匙' to '打開嚟睇下，身份證號碼' as the original was "
        "a complete mistranscription with no correspondence to the "
        "Chinese subtitle.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="尾数一，季正雄",
        yuewen="尾数1，贵正红",
        yuewen_proofread="尾数1，季正雄",
        note="Corrected '贵正红' to '季正雄' as it is a clear phonetic "
        "mishearing of the name.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="打开",
        yuewen="打佢",
        yuewen_proofread="打開",
        note="Corrected '打佢' (hit him/her) to '打開' (open), as '打佢' is a "
        "likely mishearing of the correct word.",
        difficulty=1,
    ),
]  # proof_test_cases_block_1
proof_test_cases_block_2 = [
    ProofTestCase(
        zhongwen="协议中有关香港的安排",
        yuewen="嘅arrangements for Hong Kong contained in the",
        yuewen_proofread="协议中有关香港嘅安排",
        note="Corrected the 粤文 to match the intended meaning, as the "
        "original was a mistranscription with English words and "
        "missing the actual content; this is a clear transcription "
        "error.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="这些安排是长期的政策",
        yuewen="agreement而notmeasuresofexpediency嘅好longtermpolicies",
        yuewen_proofread="agreement而唔係measuresofexpediency嘅好longtermpolicies",
        note="Corrected 'not' to '唔係' as it is a plausible phonetic "
        "confusion in Cantonese and matches the intended meaning.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="它们将写入为香港制定的基本法",
        yuewen="Which will be incorporated in the basic law for Hong。",
        yuewen_proofread="",
        note="The 粤文 subtitle is in English and does not correspond to the "
        "provided 中文 subtitle, indicating a complete "
        "mistranscription.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="五十年不变",
        yuewen="Kong And preserved in tact For 50 years from 1997",
        yuewen_proofread="",
        note="The 粤文 subtitle is in English and does not correspond to the "
        "provided 中文 subtitle, indicating a complete "
        "mistranscription.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="也是我们双方共同的责任",
        yuewen="也是我们双方共同的",
        yuewen_proofread="也是我们双方共同的责任",
        note="Added '责任' to the end, as it is likely a transcription "
        "omission and matches the phonetic flow of the original "
        "sentence.",
        difficulty=1,
    ),
]  # proof_test_cases_block_2
proof_test_cases_block_3 = []  # proof_test_cases_block_3
proof_test_cases_block_4 = []  # proof_test_cases_block_4
proof_test_cases_block_5 = []  # proof_test_cases_block_5
proof_test_cases_block_6 = []  # proof_test_cases_block_6
proof_test_cases_block_7 = []  # proof_test_cases_block_7
proof_test_cases_block_8 = []  # proof_test_cases_block_8
proof_test_cases_block_9 = []  # proof_test_cases_block_9
proof_test_cases_block_10 = []  # proof_test_cases_block_10
proof_test_cases_block_11 = []  # proof_test_cases_block_11
proof_test_cases_block_12 = []  # proof_test_cases_block_12
proof_test_cases_block_13 = []  # proof_test_cases_block_13
proof_test_cases_block_14 = []  # proof_test_cases_block_14
proof_test_cases_block_15 = []  # proof_test_cases_block_15
proof_test_cases_block_16 = []  # proof_test_cases_block_16
proof_test_cases_block_17 = []  # proof_test_cases_block_17
proof_test_cases_block_18 = []  # proof_test_cases_block_18
proof_test_cases_block_19 = []  # proof_test_cases_block_19
proof_test_cases_block_20 = []  # proof_test_cases_block_20
proof_test_cases_block_21 = []  # proof_test_cases_block_21
proof_test_cases_block_22 = []  # proof_test_cases_block_22
proof_test_cases_block_23 = []  # proof_test_cases_block_23
proof_test_cases_block_24 = []  # proof_test_cases_block_24
proof_test_cases_block_25 = []  # proof_test_cases_block_25
proof_test_cases_block_26 = []  # proof_test_cases_block_26
proof_test_cases_block_27 = []  # proof_test_cases_block_27
proof_test_cases_block_28 = []  # proof_test_cases_block_28
proof_test_cases_block_29 = []  # proof_test_cases_block_29
proof_test_cases_block_30 = []  # proof_test_cases_block_30
proof_test_cases_block_31 = []  # proof_test_cases_block_31
proof_test_cases_block_32 = []  # proof_test_cases_block_32
proof_test_cases_block_33 = []  # proof_test_cases_block_33
proof_test_cases_block_34 = []  # proof_test_cases_block_34
proof_test_cases_block_35 = []  # proof_test_cases_block_35
proof_test_cases_block_36 = []  # proof_test_cases_block_36
proof_test_cases_block_37 = []  # proof_test_cases_block_37
proof_test_cases_block_38 = []  # proof_test_cases_block_38
proof_test_cases_block_39 = []  # proof_test_cases_block_39
proof_test_cases_block_40 = []  # proof_test_cases_block_40
proof_test_cases_block_41 = []  # proof_test_cases_block_41
proof_test_cases_block_42 = []  # proof_test_cases_block_42
proof_test_cases_block_43 = []  # proof_test_cases_block_43
proof_test_cases_block_44 = []  # proof_test_cases_block_44
proof_test_cases_block_45 = []  # proof_test_cases_block_45
proof_test_cases_block_46 = []  # proof_test_cases_block_46
proof_test_cases_block_47 = []  # proof_test_cases_block_47
proof_test_cases_block_48 = []  # proof_test_cases_block_48
proof_test_cases_block_49 = []  # proof_test_cases_block_49
proof_test_cases_block_50 = []  # proof_test_cases_block_50
proof_test_cases_block_51 = []  # proof_test_cases_block_51
proof_test_cases_block_52 = []  # proof_test_cases_block_52
proof_test_cases_block_53 = []  # proof_test_cases_block_53
proof_test_cases_block_54 = []  # proof_test_cases_block_54
proof_test_cases_block_55 = []  # proof_test_cases_block_55
proof_test_cases_block_56 = []  # proof_test_cases_block_56
proof_test_cases_block_57 = []  # proof_test_cases_block_57
proof_test_cases_block_58 = []  # proof_test_cases_block_58
proof_test_cases_block_59 = []  # proof_test_cases_block_59
proof_test_cases_block_60 = []  # proof_test_cases_block_60
proof_test_cases_block_61 = []  # proof_test_cases_block_61
proof_test_cases_block_62 = []  # proof_test_cases_block_62
proof_test_cases_block_63 = []  # proof_test_cases_block_63
proof_test_cases_block_64 = []  # proof_test_cases_block_64
proof_test_cases_block_65 = []  # proof_test_cases_block_65
proof_test_cases_block_66 = []  # proof_test_cases_block_66
proof_test_cases_block_67 = []  # proof_test_cases_block_67
proof_test_cases_block_68 = []  # proof_test_cases_block_68
proof_test_cases_block_69 = []  # proof_test_cases_block_69
proof_test_cases_block_70 = []  # proof_test_cases_block_70
proof_test_cases_block_71 = []  # proof_test_cases_block_71
proof_test_cases_block_72 = []  # proof_test_cases_block_72
proof_test_cases_block_73 = []  # proof_test_cases_block_73
proof_test_cases_block_74 = []  # proof_test_cases_block_74
proof_test_cases_block_75 = []  # proof_test_cases_block_75
proof_test_cases_block_76 = []  # proof_test_cases_block_76
proof_test_cases_block_77 = []  # proof_test_cases_block_77
proof_test_cases_block_78 = []  # proof_test_cases_block_78
proof_test_cases_block_79 = []  # proof_test_cases_block_79
proof_test_cases_block_80 = []  # proof_test_cases_block_80
proof_test_cases_block_81 = []  # proof_test_cases_block_81
proof_test_cases_block_82 = []  # proof_test_cases_block_82
proof_test_cases_block_83 = []  # proof_test_cases_block_83
proof_test_cases_block_84 = []  # proof_test_cases_block_84
proof_test_cases_block_85 = []  # proof_test_cases_block_85
proof_test_cases_block_86 = []  # proof_test_cases_block_86
proof_test_cases_block_87 = []  # proof_test_cases_block_87
proof_test_cases_block_88 = []  # proof_test_cases_block_88
proof_test_cases_block_89 = []  # proof_test_cases_block_89
proof_test_cases_block_90 = []  # proof_test_cases_block_90
proof_test_cases_block_91 = []  # proof_test_cases_block_91
proof_test_cases_block_92 = []  # proof_test_cases_block_92
proof_test_cases_block_93 = []  # proof_test_cases_block_93
proof_test_cases_block_94 = []  # proof_test_cases_block_94
proof_test_cases_block_95 = []  # proof_test_cases_block_95
proof_test_cases_block_96 = []  # proof_test_cases_block_96
proof_test_cases_block_97 = []  # proof_test_cases_block_97
proof_test_cases_block_98 = []  # proof_test_cases_block_98
proof_test_cases_block_99 = []  # proof_test_cases_block_99
proof_test_cases_block_100 = []  # proof_test_cases_block_100
proof_test_cases_block_101 = []  # proof_test_cases_block_101
proof_test_cases_block_102 = []  # proof_test_cases_block_102
proof_test_cases_block_103 = []  # proof_test_cases_block_103
proof_test_cases_block_104 = []  # proof_test_cases_block_104
proof_test_cases_block_105 = []  # proof_test_cases_block_105
proof_test_cases_block_106 = []  # proof_test_cases_block_106
proof_test_cases_block_107 = []  # proof_test_cases_block_107
proof_test_cases_block_108 = []  # proof_test_cases_block_108
proof_test_cases_block_109 = []  # proof_test_cases_block_109
proof_test_cases_block_110 = []  # proof_test_cases_block_110
proof_test_cases_block_111 = []  # proof_test_cases_block_111
proof_test_cases_block_112 = []  # proof_test_cases_block_112
proof_test_cases_block_113 = []  # proof_test_cases_block_113
proof_test_cases_block_114 = []  # proof_test_cases_block_114
proof_test_cases_block_115 = []  # proof_test_cases_block_115
proof_test_cases_block_116 = []  # proof_test_cases_block_116
proof_test_cases_block_117 = []  # proof_test_cases_block_117
proof_test_cases_block_118 = []  # proof_test_cases_block_118
proof_test_cases_block_119 = []  # proof_test_cases_block_119
proof_test_cases_block_120 = []  # proof_test_cases_block_120
proof_test_cases_block_121 = []  # proof_test_cases_block_121
proof_test_cases_block_122 = []  # proof_test_cases_block_122
proof_test_cases_block_123 = []  # proof_test_cases_block_123
proof_test_cases_block_124 = []  # proof_test_cases_block_124
proof_test_cases_block_125 = []  # proof_test_cases_block_125
proof_test_cases_block_126 = []  # proof_test_cases_block_126
proof_test_cases_block_127 = []  # proof_test_cases_block_127
proof_test_cases_block_128 = []  # proof_test_cases_block_128
proof_test_cases_block_129 = []  # proof_test_cases_block_129
proof_test_cases_block_130 = []  # proof_test_cases_block_130
proof_test_cases_block_131 = []  # proof_test_cases_block_131
proof_test_cases_block_132 = []  # proof_test_cases_block_132
proof_test_cases_block_133 = []  # proof_test_cases_block_133
proof_test_cases_block_134 = []  # proof_test_cases_block_134
proof_test_cases_block_135 = []  # proof_test_cases_block_135
proof_test_cases_block_136 = []  # proof_test_cases_block_136
proof_test_cases_block_137 = []  # proof_test_cases_block_137
proof_test_cases_block_138 = []  # proof_test_cases_block_138
proof_test_cases_block_139 = []  # proof_test_cases_block_139
proof_test_cases_block_140 = []  # proof_test_cases_block_140
proof_test_cases_block_141 = []  # proof_test_cases_block_141
proof_test_cases_block_142 = []  # proof_test_cases_block_142
proof_test_cases_block_143 = []  # proof_test_cases_block_143
proof_test_cases_block_144 = []  # proof_test_cases_block_144
proof_test_cases_block_145 = []  # proof_test_cases_block_145
proof_test_cases_block_146 = []  # proof_test_cases_block_146
proof_test_cases_block_147 = []  # proof_test_cases_block_147
proof_test_cases_block_148 = []  # proof_test_cases_block_148
proof_test_cases_block_149 = []  # proof_test_cases_block_149
proof_test_cases_block_150 = []  # proof_test_cases_block_150
proof_test_cases_block_151 = []  # proof_test_cases_block_151
proof_test_cases_block_152 = []  # proof_test_cases_block_152
proof_test_cases_block_153 = []  # proof_test_cases_block_153
proof_test_cases_block_154 = []  # proof_test_cases_block_154
proof_test_cases_block_155 = []  # proof_test_cases_block_155
proof_test_cases_block_156 = []  # proof_test_cases_block_156
proof_test_cases_block_157 = []  # proof_test_cases_block_157
proof_test_cases_block_158 = []  # proof_test_cases_block_158
proof_test_cases_block_159 = []  # proof_test_cases_block_159
proof_test_cases_block_160 = []  # proof_test_cases_block_160
proof_test_cases_block_161 = []  # proof_test_cases_block_161
proof_test_cases_block_162 = []  # proof_test_cases_block_162
proof_test_cases_block_163 = []  # proof_test_cases_block_163
proof_test_cases_block_164 = []  # proof_test_cases_block_164
proof_test_cases_block_165 = []  # proof_test_cases_block_165
proof_test_cases_block_166 = []  # proof_test_cases_block_166
proof_test_cases_block_167 = []  # proof_test_cases_block_167
proof_test_cases_block_168 = []  # proof_test_cases_block_168
proof_test_cases_block_169 = []  # proof_test_cases_block_169
proof_test_cases_block_170 = []  # proof_test_cases_block_170
proof_test_cases_block_171 = []  # proof_test_cases_block_171
proof_test_cases_block_172 = []  # proof_test_cases_block_172
proof_test_cases_block_173 = []  # proof_test_cases_block_173
proof_test_cases_block_174 = []  # proof_test_cases_block_174
proof_test_cases_block_175 = []  # proof_test_cases_block_175
proof_test_cases_block_176 = []  # proof_test_cases_block_176
proof_test_cases_block_177 = []  # proof_test_cases_block_177
proof_test_cases_block_178 = []  # proof_test_cases_block_178
proof_test_cases_block_179 = []  # proof_test_cases_block_179
proof_test_cases_block_180 = []  # proof_test_cases_block_180
proof_test_cases_block_181 = []  # proof_test_cases_block_181

t_proof_test_cases: list[ProofTestCase] = list(
    chain.from_iterable(
        cases
        for name, cases in globals().items()
        if name.startswith("proof_test_cases_block_") and cases
    )
)

"""T 粤文 proof test cases."""

__all__ = [
    "t_proof_test_cases",
]
