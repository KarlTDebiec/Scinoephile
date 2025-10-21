#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for T."""

from __future__ import annotations

from itertools import chain

from scinoephile.audio.cantonese.proofing import ProofTestCase

proof_test_cases_block_0 = [
    ProofTestCase(
        zhongwen="警察",
        yuewen="喂警察",
        yuewen_proofread="警察",
        note="Removed '喂' as it is not present in the 中文 and is likely a "
        "mishearing or extraneous addition.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="拿身份证出来",
        yuewen="攞我新闻证出嚟睇",
        yuewen_proofread="攞身份证出嚟",
        note="新闻证 (san1 man4 zing3) is a mishearing of 身份证 (san1 fan6 "
        "zing3); corrected to match the intended meaning.",
        difficulty=1,
    ),
]  # proof_test_cases_block_0
proof_test_cases_block_1 = [
    ProofTestCase(
        zhongwen="﹣检查一下　　﹣收到",
        yuewen="﹣查下咩料　　﹣收到",
        yuewen_proofread="﹣查下咩料　　﹣收到",
        note="",
    ),
    ProofTestCase(
        zhongwen="﹣袋子里装什么？　　﹣总机",
        yuewen="角度系袋住啲咩呀？",
        yuewen_proofread="袋入面装住咩呀？",
        note="Corrected '角度系袋住啲咩呀？' to '袋入面装住咩呀？' because '角度' is a clear "
        "mishearing of '袋' (bag), which matches the context of "
        "'袋子里装什么？'.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="﹣打开来看看　　﹣身份证号码：C532743",
        yuewen="通话电台 查 查个牌匙 C532743 尾数1",
        yuewen_proofread="打開嚟睇下，身份證號碼：C532743",
        note="Corrected '通话电台 查 查个牌匙' to '打開嚟睇下，身份證號碼' as the original was "
        "a clear mistranscription with no correspondence to the "
        "Chinese subtitle.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="尾数一，季正雄",
        yuewen="贵正红，",
        yuewen_proofread="季正雄，",
        note="Corrected '贵正红' to '季正雄' as it is a clear phonetic "
        "mishearing of the name in the original speech.",
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
        yuewen="嘅arrangements for Hong Kong contained in",
        yuewen_proofread="协议中有关香港嘅安排",
        note="Corrected '嘅arrangements for Hong Kong contained in' to "
        "'协议中有关香港嘅安排' to match the intended meaning and fix the clear "
        "transcription error where English was mistakenly transcribed "
        "instead of the Cantonese phrase.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="不是权宜之计",
        yuewen="the agreement 而not measures of expediency",
        yuewen_proofread="",
        note="The 粤文 subtitle is in English and does not correspond to the "
        "中文 subtitle at all, indicating a complete mistranscription.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="这些安排是长期的政策",
        yuewen="嘅好long term policies。",
        yuewen_proofread="呢啲安排係長期嘅政策。",
        note="Corrected '嘅好long term policies' to '呢啲安排係長期嘅政策' as the "
        "original 粤文 was a mistranscription with no correspondence to "
        "the 中文; the speaker likely said something closer to the 中文 "
        "line.",
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
proof_test_cases_block_3 = [
    ProofTestCase(
        zhongwen="今天下午观塘发生械劫案",
        yuewen="今日下昼观塘发生鞋劫案",
        yuewen_proofread="今日下昼观塘发生械劫案",
        note="Corrected '鞋劫案' (shoe robbery) to '械劫案' (armed robbery), as "
        "'械' and '鞋' are phonetically similar and the original is a "
        "clear mishearing.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="四名持枪械匪徒",
        yuewen="四名持枪鞋匪徒",
        yuewen_proofread="四名持枪械匪徒",
        note="Corrected '枪鞋' to '枪械' as '鞋' is a likely mishearing of '械' "
        "in this context.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="连环打劫物华街五间金行",
        yuewen="连环打劫立华街五间金行",
        yuewen_proofread="连环打劫物华街五间金行",
        note="Corrected '立华街' to '物华街' as it is a plausible mishearing and "
        "matches the 中文 subtitle.",
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
        yuewen="同喺附近秘密执勤嘅飞虎队员发生枪战",
        yuewen_proofread="同喺附近秘密执勤嘅飞虎队员发生枪战",
        note="",
    ),
    ProofTestCase(
        zhongwen="双方开枪过百发",
        yuewen="双方开枪过白房",
        yuewen_proofread="双方开枪过百发",
        note="Corrected '白房' to '百发' as it is a clear phonetic "
        "transcription error; '百发' matches the meaning of '过百发' (over "
        "a hundred shots) in the 中文.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="事件中，两名途人及三名军装警员受伤",
        yuewen="事件中，两名逃人及三名军人警察获杀",
        yuewen_proofread="事件中，两名途人及三名军装警员受伤",
        note="Corrected '逃人' to '途人', '军人警察' to '军装警员', and '获杀' to '受伤' "
        "as these are clear mishearings of the intended words.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="五间金行合共损失大约一千万",
        yuewen="现间有狂黑洞损失大约三次万",
        yuewen_proofread="五间金行合共损失大约一千万",
        note="Corrected '现间有狂黑洞损失大约三次万' to '五间金行合共损失大约一千万' as the original "
        "was a clear mistranscription with no phonetic or semantic "
        "correspondence to the Chinese subtitle.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="警方相信，今次械劫案的主谋",
        yuewen="警方相信，今次鞋劫案嘅主谋",
        yuewen_proofread="警方相信，今次械劫案嘅主谋",
        note="Corrected '鞋劫案' (shoe robbery) to '械劫案' (armed robbery), as "
        "this is a clear phonetic transcription error.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="是「头号通缉犯」叶国欢",
        yuewen="系头号通缉犯叶国宽",
        yuewen_proofread="系头号通缉犯叶国欢",
        note="Corrected '叶国宽' to '叶国欢' as it is a likely mishearing of the "
        "name, matching the 中文 subtitle.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="一夫当关，万夫莫敌！",
        yuewen="一孤当关，万夫莫敌！",
        yuewen_proofread="一夫当关，万夫莫敌！",
        note="Corrected '一孤' to '一夫' as it is a likely mishearing; the "
        "correct phrase is '一夫当关'.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="真是威风！欢哥！",
        yuewen="真系威吓！宽哥！",
        yuewen_proofread="真系威风！欢哥！",
        note="Corrected '威吓' to '威风' and '宽哥' to '欢哥' as both are likely "
        "misheard transcription errors based on the similar "
        "pronunciation and the corresponding 中文.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="但大事不妙了！",
        yuewen="但系大剂啦！",
        yuewen_proofread="但系大事不妙啦！",
        note="Corrected '大剂' to '大事不妙' as '大剂' is a mishearing of the "
        "intended phrase, which should match the meaning of '大事不妙' in "
        "the context.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="都说放多些报纸！",
        yuewen="都话贱到啲报纸㗎喇！",
        yuewen_proofread="都话放多啲报纸㗎喇！",
        note="Corrected '贱到' to '放多' as it is a likely mishearing; the "
        "intended meaning is to put more newspapers, matching the "
        "context.",
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
proof_test_cases_block_4 = [
    ProofTestCase(
        zhongwen="真是很不妙！",
        yuewen="喂,真系好大只呀！",
        yuewen_proofread="",
        note="The 粤文 subtitle '喂,真系好大只呀！' does not correspond at all to "
        "the 中文 '真是很不妙！', indicating a complete mistranscription.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="两折，不好意思，最多两折！",
        yuewen="两折,唔好意思,最多两折！",
        yuewen_proofread="两折,唔好意思,最多两折！",
        note="",
    ),
    ProofTestCase(
        zhongwen="说好四折",
        yuewen="讲好四折㗎",
        yuewen_proofread="讲好四折㗎",
        note="",
    ),
    ProofTestCase(
        zhongwen="还有道义吗？",
        yuewen="㖞，讲唔讲道义㗎？",
        yuewen_proofread="㖞，讲唔讲道义㗎？",
        note="",
    ),
    ProofTestCase(
        zhongwen="一千万货你只给两百万？",
        yuewen="成千万货你哋畀两搞？",
        yuewen_proofread="成千万货你哋畀两百万？",
        note="Corrected '两搞' to '两百万' as '搞' is a likely mishearing of "
        "'百万', which matches the context and the 中文 subtitle.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="以前至少五折！",
        yuewen="以前除少都五只啦！",
        yuewen_proofread="以前至少都五折啦！",
        note="Corrected '除少' to '至少' as it is a clear phonetic "
        "transcription error; '除少' is a mishearing of '至少'.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="你们销赃的全赚了！",
        yuewen="你哋班消庄佬赞晒呀！",
        yuewen_proofread="你哋班销赃佬赚晒呀！",
        note="Corrected '消庄' to '销赃' and '赞晒' to '赚晒' as these are likely "
        "mishearings of the intended words.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="赚你个屁！",
        yuewen="赞你条毛咩！",
        yuewen_proofread="赚你条毛咩！",
        note="Corrected '赞' to '赚' as it is a plausible mishearing and "
        "matches the meaning of the 中文 subtitle.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="今时不同往日",
        yuewen="今时唔同往日",
        yuewen_proofread="今时唔同往日",
        note="",
    ),
    ProofTestCase(
        zhongwen="外面的警察盯得很紧！",
        yuewen="喇喂,出面啲差异睇得好紧㗎！",
        yuewen_proofread="喇喂,出面啲差佬睇得好紧㗎！",
        note="Corrected '差异' to '差佬' as '差异' is a mishearing of '差佬', "
        "which means 'police' in Cantonese and matches the context of "
        "the 中文 subtitle.",
        difficulty=1,
    ),
]  # proof_test_cases_block_4
proof_test_cases_block_5 = [
    ProofTestCase(
        zhongwen="尤其是你的货，欢哥！",
        yuewen="系，尤其是你嗰批货啊，宽哥！",
        yuewen_proofread="系，尤其是你嗰批货啊，欢哥！",
        note="Corrected '宽哥' to '欢哥' as it is a likely phonetic "
        "transcription error; '宽' and '欢' sound similar in Cantonese.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="上次那一批，销了两年，足足两年！",
        yuewen="上次嗰批，烧咗两年，足足两年啊！",
        yuewen_proofread="上次嗰批，销咗两年，足足两年啊！",
        note="Corrected '烧咗' to '销咗' as the intended meaning is 'sold' (销) "
        "rather than 'burned' (烧), which is a plausible phonetic "
        "confusion.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="炒股、炒楼、炒栗子更能赚钱！",
        yuewen="真系炒股、炒楼、炒栗子都好过啦！系吧",
        yuewen_proofread="真系炒股、炒楼、炒栗子更能赚钱啦！",
        note="Replaced '都好过啦！系吧' with '更能赚钱啦！' to correct a likely "
        "mishearing, as the original 粤文 did not correspond to the "
        "meaning of the 中文 and '更能赚钱' is a plausible phonetic match "
        "for the intended phrase.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="帮个忙",
        yuewen="都说说畀我",
        yuewen_proofread="",
        note="The 粤文 '都说说畀我' does not correspond at all to the 中文 '帮个忙', "
        "indicating a complete mistranscription.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="四折！",
        yuewen="死绝！",
        yuewen_proofread="四折！",
        note="Corrected '死绝' to '四折' as the transcriber likely misheard "
        "the similar-sounding words; '四折' matches the intended "
        "meaning of 'fourfold discount' in the 中文.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="欢哥开口，怎么着都行！",
        yuewen="既然宽哥出到声，点话点好啦！",
        yuewen_proofread="既然欢哥出到声，点话点好啦！",
        note="Corrected '宽哥' to '欢哥' to match the intended name, as '宽' "
        "and '欢' are phonetically similar and this is a likely "
        "mishearing.",
        difficulty=1,
    ),
]  # proof_test_cases_block_5
proof_test_cases_block_6 = [
    ProofTestCase(
        zhongwen="不如你找其它买家？",
        yuewen="唔好呀，唔好呀？",
        yuewen_proofread="",
        note="The 粤文 subtitle '唔好呀，唔好呀？' does not correspond at all to the "
        "中文 '不如你找其它买家？', indicating a complete mistranscription.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="我都买不下手，我看没人敢收⋯",
        yuewen="唔好呀，唔好呀⋯",
        yuewen_proofread="",
        note="There is no correspondence between the 粤文 and 中文 subtitles, "
        "indicating a complete mistranscription of the spoken "
        "Cantonese.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="去你妈的！",
        yuewen="唔好呀唔好呀唔好呀唔好呀唔好呀！",
        yuewen_proofread="",
        note="There is zero correspondence between the 粤文 and 中文; the 粤文 "
        "is a complete mistranscription of the spoken Cantonese.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="开保险箱！",
        yuewen="唔好呀唔好呀！",
        yuewen_proofread="",
        note="The 粤文 subtitle ('唔好呀唔好呀！') has no correspondence to the 中文 "
        "('开保险箱！'), indicating a complete mistranscription.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="你算是抢我？",
        yuewen="唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀唔好呀？",
        yuewen_proofread="",
        note="The 粤文 subtitle has no correspondence to the 中文 subtitle and "
        "appears to be a complete mistranscription of the spoken "
        "Cantonese.",
        difficulty=1,
    ),
]  # proof_test_cases_block_6
proof_test_cases_block_7 = [
    ProofTestCase(
        zhongwen="不要逼我自己动手",
        yuewen="唔好要我自己嚟哗",
        yuewen_proofread="唔好逼我自己嚟哗",
        note="Corrected '要' to '逼' as it is a plausible mishearing and "
        "matches the meaning of the 中文 subtitle.",
        difficulty=1,
    ),
]  # proof_test_cases_block_7
proof_test_cases_block_8 = [
    ProofTestCase(
        zhongwen="真的多谢了，欢哥！",
        yuewen="真系多谢晒你呀，宽哥！",
        yuewen_proofread="真系多谢晒你呀，欢哥！",
        note="Corrected '宽哥' to '欢哥' as it is a likely mishearing; '宽' and "
        "'欢' are phonetically similar in Cantonese.",
        difficulty=1,
    ),
    ProofTestCase(
        zhongwen="以后别来找我",
        yuewen="以后咪嚟揾我",
        yuewen_proofread="以后咪嚟揾我",
        note="",
    ),
    ProofTestCase(
        zhongwen="不要再合作",
        yuewen="唔好再合作啦",
        yuewen_proofread="唔好再合作啦",
        note="",
    ),
    ProofTestCase(
        zhongwen="各走各路！",
        yuewen="各行各路啊！",
        yuewen_proofread="各走各路啊！",
        note="Corrected '各行各路' to '各走各路' as '行' and '走' are "
        "similar-sounding, but '走' matches the intended meaning and "
        "the original Chinese subtitle.",
        difficulty=1,
    ),
]  # proof_test_cases_block_8
proof_test_cases_block_9 = [
    ProofTestCase(
        zhongwen="欢哥，火！",
        yuewen="阿花香，回来了！",
        yuewen_proofread="",
        note="There is no correspondence between the 粤文 and 中文 subtitles, "
        "indicating a complete mistranscription.",
        difficulty=1,
    ),
]  # proof_test_cases_block_9
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
