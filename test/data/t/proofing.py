#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for T."""

from __future__ import annotations

from itertools import chain

from scinoephile.audio.cantonese.proofing import ProofTestCase

proof_test_cases_block_0 = [
    ProofTestCase(
        zhongwen="警察",
        yuewen="喂，警察",
        yuewen_proofread="喂，警察",
        note="",
        verified=True,
    ),
    ProofTestCase(
        zhongwen="拿身份证出来",
        yuewen="攞我新闻证出嚟睇",
        yuewen_proofread="攞身份证出嚟",
        note="Corrected '新闻证' (sān màn jing) to '身份证' (sān fan jing).",
        difficulty=1,
        prompt=True,
        verified=True,
    ),
]  # proof_test_cases_block_0
proof_test_cases_block_1 = [
    ProofTestCase(
        zhongwen="﹣检查一下　　﹣收到",
        yuewen="﹣查下咩料　　﹣收到",
        yuewen_proofread="﹣查下咩里　　﹣收到",
        note="Corrected '料' (liuh) to '里' (léih).",
        difficulty=1,
        prompt=True,
        verified=True,
    ),
    ProofTestCase(
        zhongwen="﹣袋子里装什么？　　﹣总机",
        yuewen="﹣角度系袋住啲咩呀？　　﹣通话电台",
        yuewen_proofread="﹣嗰度系袋住啲咩呀？　　﹣通话电台",
        note="Corrected '角度' (gok douh) to '嗰度' (gó douh).",
        difficulty=1,
        verified=True,
    ),
    ProofTestCase(
        zhongwen="﹣打开来看看　　﹣身份证号码：C532743",
        yuewen="查查个牌匙：C532743",
        yuewen_proofread="﹣打开嚟睇下　　﹣查吓个牌匙：C532743",
        note="Manually overridden; low confidence.",
        difficulty=3,
        verified=True,
    ),
    ProofTestCase(
        zhongwen="尾数一，季正雄",
        yuewen="尾数1，贵正红",
        yuewen_proofread="尾数一，季正雄",
        note="Adjusted '1' to '一'; corrected '贵正红' (gwai jing hùhng) to "
        "'季正雄' (gwai jing hùhng).",
        difficulty=2,
        prompt=True,
        verified=True,
    ),
    ProofTestCase(
        zhongwen="打开",
        yuewen="打佢",
        yuewen_proofread="打开",
        note="Corrected '佢' (kéuih) to '开' (hōi) to convey 'open' as in '打开'.",
        difficulty=1,
        verified=True,
    ),
]  # proof_test_cases_block_1
proof_test_cases_block_2 = [
    ProofTestCase(
        zhongwen="协议中有关香港的安排",
        yuewen="嘅 arrangements for Hong Kong contained in",
        yuewen_proofread="",
        note="Manually overridden; the zhongwen is a Chinese translation "
        "of transcribed spoken English.",
        difficulty=3,
        verified=True,
    ),
    ProofTestCase(
        zhongwen="不是权宜之计",
        yuewen="the agreement 而 not measures of expediency",
        yuewen_proofread="",
        note="Manually overridden; the zhongwen is a Chinese translation "
        "of transcribed spoken English.",
        difficulty=3,
        verified=True,
    ),
    ProofTestCase(
        zhongwen="这些安排是长期的政策",
        yuewen="嘅好 long term policies",
        yuewen_proofread="",
        note="Manually overridden; the zhongwen is a Chinese translation "
        "of transcribed spoken English.",
        difficulty=3,
        verified=True,
    ),
    ProofTestCase(
        zhongwen="它们将写入为香港制定的基本法",
        yuewen="Which will be incorporated in the basic law for Hong",
        yuewen_proofread="",
        note="Manually overridden; the zhongwen is a Chinese translation "
        "of transcribed spoken English.",
        difficulty=3,
        verified=True,
    ),
    ProofTestCase(
        zhongwen="五十年不变",
        yuewen="Kong And preserved in tact For 50 years from 1997",
        yuewen_proofread="",
        note="Manually overridden; the zhongwen is a Chinese translation "
        "of transcribed spoken English.",
        difficulty=3,
        verified=True,
    ),
    ProofTestCase(
        zhongwen="也是我们双方共同的责任",
        yuewen="也是我们双方共同的",
        yuewen_proofread="",
        note="Manually overridden; the zhongwen is a transcription of spoken Mandarin.",
        difficulty=3,
        verified=True,
    ),
]  # proof_test_cases_block_2
proof_test_cases_block_3 = [
    ProofTestCase(
        zhongwen="今天下午观塘发生械劫案",
        yuewen="今日下昼观塘发生鞋劫案",
        yuewen_proofread="今日下昼观塘发生械劫案",
        note="Corrected '鞋劫案' (hàaih gip ngon) to '械劫案' (haaih gip ngon).",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="四名持枪械匪徒",
        yuewen="四名持枪鞋匪徒",
        yuewen_proofread="四名持枪械匪徒",
        note="Corrected '枪鞋' (cheung hàaih) to '枪械' (cheung hàaih).",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="连环打劫物华街五间金行",
        yuewen="连环打劫立华街五间金行",
        yuewen_proofread="连环打劫物华街五间金行",
        note="Corrected '立华街' (lahp wàh gāai) to '物华街' (maht wàh gāai).",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="由观众提供片段，见到贼人离开的时候",
        yuewen="由观众提供片段，见到贼人离开嘅时候",
        yuewen_proofread="由观众提供片段，见到贼人离开嘅时候",
        note="",
    ),
    ProofTestCase(
        zhongwen="在附近秘密执勤的飞虎队员发生枪战",
        yuewen="同喺附近秘密执勤嘅飞虎队员发生枪战，双方",
        yuewen_proofread="喺附近秘密执勤嘅飞虎队员发生枪战",
        note="Removed extra conjunction '同' (tùng), as it's not present in "
        "the zhongwen.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="双方开枪过百发",
        yuewen="开枪过白房，事件中",
        yuewen_proofread="双方开枪过百发",
        note="Corrected '白房' (baahk fòhng) to '百发' (baak faat) and added "
        "'双方' (sēung fōng).",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="事件中，两名途人及三名军装警员受伤",
        yuewen="两名逃人及三名军人警察获杀，现间有狂，黑洞",
        yuewen_proofread="",
        note="The yuewen '逃人及三名军人警察获杀，现间有狂，黑洞' does not correspond to the "
        "zhongwen and appears to be a complete mistranscription.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="五间金行合共损失大约一千万",
        yuewen="损失大约三次万",
        yuewen_proofread="损失大约一千万",
        note="Corrected '三次' (sāam chi) to '一千' (yāt chīn) to match '一千万'.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="警方相信，今次械劫案的主谋",
        yuewen="警方相信，今次鞋劫案嘅主谋",
        yuewen_proofread="警方相信，今次械劫案嘅主谋",
        note="Corrected '鞋劫案' (hàaih gip ngon) to '械劫案' (haaih gip ngon).",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="是「头号通缉犯」叶国欢",
        yuewen="系「头号通缉犯」叶国宽",
        yuewen_proofread="系「头号通缉犯」叶国欢",
        note="Corrected '叶国宽' (yihp gwok kuān) to '叶国欢' (yihp gwok hwān).",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="一夫当关，万夫莫敌！",
        yuewen="一孤当关，万夫莫敌！真系威吓",
        yuewen_proofread="一夫当关，万夫莫敌！真系威吓",
        note="Corrected '孤' (gū) to '夫' (fū).",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="真是威风！欢哥！",
        yuewen="宽哥！",
        yuewen_proofread="威风！欢哥！",
        note="Added '威风！' as it was missing from the original yuewen.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="但大事不妙了！",
        yuewen="但系大剂啦！",
        yuewen_proofread="但系大事不妙啦！",
        note="Corrected '大剂' (daaih jai) to '大事不妙' (daaih sih bāt miuh).",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="都说放多些报纸！",
        yuewen="都话，贱到啲报纸㗎喇！",
        yuewen_proofread="",
        note="The yuewen transcription does not match the zhongwen, "
        "indicating a complete mistranscription of the spoken "
        "Cantonese.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="你看！到处都是血！",
        yuewen="睇吓睇吓！周围都系血！",
        yuewen_proofread="睇吓睇吓！周围都系血！",
        note="",
    ),
    ProofTestCase(
        zhongwen="拿去吧，混蛋！",
        yuewen="攞去啦，仆街！",
        yuewen_proofread="攞去啦，仆街！",
        note="",
    ),
]  # proof_test_cases_block_3
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
