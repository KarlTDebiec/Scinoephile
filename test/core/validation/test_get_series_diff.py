#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.validation.get_series_diff."""

# ruff: noqa: E501

from __future__ import annotations

from scinoephile.core.subtitles import Series
from scinoephile.core.validation import get_series_diff


def _get_series_diff(
    ocr_series: Series,
    srt_series: Series,
) -> list[str]:
    """Get get_series_diff output.

    Arguments:
        ocr_series: OCR subtitle series
        srt_series: SRT subtitle series
    Returns:
        list of differences
    """
    return get_series_diff(
        ocr_series,
        srt_series,
        one_label="OCR",
        two_label="SRT",
    )


def _assert_expected_differences(
    differences: list[str],
    expected: list[str],
) -> None:
    """Assert that expected differences are present.

    Arguments:
        differences: list of differences to check
        expected: list of expected difference strings
    """
    missing = [diff for diff in expected if diff not in differences]
    if missing:
        formatted = "\n".join(missing)
        raise AssertionError(f"Missing expected differences:\n{formatted}")


def test_get_series_diff_kob(
    kob_eng_fuse_clean_validate_proofread_flatten: Series,
    kob_eng_timewarp_clean_proofread_flatten: Series,
):
    """Test get_series_diff with KOB English subtitles.

    Arguments:
        kob_eng_fuse_clean_validate_proofread_flatten: OCR English subtitles
        kob_eng_timewarp_clean_proofread_flatten: timewarped SRT English subtitles
    """
    differences = _get_series_diff(
        kob_eng_fuse_clean_validate_proofread_flatten,
        kob_eng_timewarp_clean_proofread_flatten,
    )
    # NOTE: Do not change expected entries through OCR[249]/SRT[260]; only adjust below.
    expected = [
        "insert: SRT[8] 'Damn!' not present in OCR",
        "insert: SRT[31] 'What?' not present in OCR",
        "insert: SRT[58] 'Tips. Tips…' not present in OCR",
        "split: OCR[59] -> SRT[62-63]: ['- Please give me some money    - Kidding? Damn you beggar!'] -> ['Please give me some money', 'Kidding? Damn you beggar!']",
        "split: OCR[62] -> SRT[66-67]: ['- Give him tips    - Yes, young master'] -> ['Give him tips', 'Yes, young master']",
        "split_edit: OCR[71] -> SRT[76-77]: ['- Come into my room.    - Please follow me'] -> ['Please follow me', 'Come into my room…']",
        "shift: OCR[103-104] -> SRT[109-110]: ['What?', \"Who dared so? I will hit that bastard's mouth for you\"] -> ['What? Who dared so?', \"I will hit that bastard's mouth for you\"]",
        "shift: OCR[122-123] -> SRT[128-129]: ['- May I be excused,    - Mr Chiu,', 'Miss Yushang has arrived'] -> ['May I be excused', 'Mr Chiu, Miss Yushang has arrived']",
        "split: OCR[133] -> SRT[139-140]: ['If any of you can offer more than 100,000 taels'] -> ['If any of you can offer', 'more than 100,000 taels']",
        'split: OCR[135] -> SRT[142-143]: ["Don\'t quarrel because of such a small amount, isn\'t it right?"] -> ["Don\'t quarrel because of such a small amount,", "isn\'t it right?"]',
        "split_edit: OCR[143] -> SRT[151-152]: [\"I love money too. But, I don't like you\"] -> ['I love money too', \"But, I don't like you\"]",
        "split: OCR[150] -> SRT[159-160]: [\"Don't worry, I have many pretty girls here\"] -> [\"Don't worry,\", 'I have many pretty girls here']",
        "split: OCR[185] -> SRT[195-196]: ['- Come on, give tips to the girls here    - Master'] -> ['Come on, give tips to the girls here', 'Master']",
        "edit: OCR[247] -> SRT[258]: 'Stop, I have taken his money, 100,000 taels you know?' -> 'Stop, I have taken his money, 100,000 taels, you know?'",
        'edit: OCR[248] -> SRT[259]: "I won\'t give it back" -> "I won\'t give it back."',
        "edit: OCR[249] -> SRT[260]: 'About the personality of Mr So…' -> 'About the personality of Mr. So…'",
        "edit: OCR[251] -> SRT[262]: 'Leave here first' -> 'Leave here first.'",
        "edit: OCR[252] -> SRT[263]: 'Yes, you are right' -> 'Yes, you are right.'",
        "merge_edit: OCR[253] -> SRT[264-265]: ['- Miss Seven…    - Just accept this'] -> ['Miss Seven…', 'Just accept this.']",
        "edit: OCR[256] -> SRT[268]: 'Miss, first of all, I have good news for you' -> 'Miss, first of all, I have a good news for you'",
        "edit: OCR[258] -> SRT[270]: 'To me, this is a bad news' -> 'To me, this is bad news'",
        "shift: OCR[285-286] -> SRT[297-298]: ['- Witness?    - Yes', 'I swear in front of your sword'] -> ['Witness?', 'Yes, I swear in front of your sword']",
        "edit: OCR[291] -> SRT[303]: \"Don't you know it isn't that easy to be my husband?\" -> \"Don't you know it's not that easy to be my husband?\"",
        'edit: OCR[302] -> SRT[314]: "OK, but you\'d give me some time to consider it" -> "OK, but you\'d give me some time to consider it."',
        "edit: OCR[394] -> SRT[406]: 'Take care of my lychee, you fathead!' -> 'Take care of my Lychee, you fathead!'",
        "edit: OCR[414] -> SRT[426]: 'Hide in' -> 'Hide in here'",
        "edit: OCR[419] -> SRT[431]: 'You are great! I love it' -> 'You are great! I love it.'",
        "edit: OCR[422] -> SRT[434]: 'You are bad, how can you say so to me?' -> 'You are bad, how can you say that to me?'",
        "edit: OCR[428] -> SRT[440]: 'I wanted to trick you actually, you are really smart' -> 'I wanted to trick you actually, you are really smart.'",
        "split: OCR[477] -> SRT[489-490]: [\"- You shouldn't put it that way    - What?\"] -> [\"You shouldn't put it that way\", 'What?']",
        "insert: SRT[530] 'Bravo…' not present in OCR",
        "split: OCR[539] -> SRT[553-554]: ['What did you say?'] -> ['What did', 'you say?']",
        "split: OCR[544] -> SRT[559-560]: ['Damn you Cheng! You betrayed me!'] -> ['Damn you Cheng!', 'You betrayed me!']",
        "delete: OCR[562] 'You… You…' not present in SRT",
        "delete: OCR[566] 'OK' not present in SRT",
        "edit: OCR[567] -> SRT[581]: 'I want to take a statement from you as record' -> 'I want to take some statements from you as record'",
        "edit: OCR[570] -> SRT[584]: 'Is Miss Yushang his mom?' -> 'Is Miss Yushang your mom?'",
        "split: OCR[599] -> SRT[613-614]: ['- Kill me    - No, kill me'] -> ['Kill me', 'No, kill me']",
        "split_edit: OCR[600] -> SRT[615-616]: [\"- Kill me.    - Your Majesty, you'd better kill me\"] -> ['Kill me', \"Your Majesty, you'd better kill me\"]",
        "split: OCR[607] -> SRT[623-624]: [\"So's family should be sentenced to death\"] -> [\"So's family should be\", 'sentenced to death']",
        'edit: OCR[612] -> SRT[629]: "So, he didn\'t miscarry out any duty" -> "So, he didn\'t miscarry any duty"',
        "merge: OCR[621-622] -> SRT[638]: [\"Why couldn't you find out\", 'they cheated during the examination?'] -> [\"Why couldn't you find out they cheated during the examination?\"]",
        'edit: OCR[632] -> SRT[648]: "you\'d be hardworking to learn how to write" -> "you\'d be hard working to learn how to write"',
        "edit: OCR[637] -> SRT[653]: 'Master, I will take good care of the little turtle' -> 'Master, I will take good care of little turtle'",
        "split: OCR[642] -> SRT[658-659]: ['If I did better, you could have many babies'] -> ['If I did better,', 'you could have many babies']",
        "split: OCR[643] -> SRT[660-661]: ['But I think Chan is enough for me'] -> ['But I think', 'Chan is enough for me']",
        "insert: SRT[671] 'How is it?' not present in OCR",
        "insert: SRT[673] 'What happened?' not present in OCR",
        "split_edit: OCR[660] -> SRT[680-681]: ['Son. Have you kept any money?'] -> ['Son', 'Have you kept any money?']",
        "split: OCR[664] -> SRT[685-686]: ['Be merciful, please give money to us'] -> ['Be merciful,', 'please give money to us']",
        'edit: OCR[677] -> SRT[699]: "Even the Gods won\'t let me be a beggar" -> "Even the Gods won\'t let me be beggars"',
        "split: OCR[686] -> SRT[708-709]: ['Let me take a seat, maybe we can have something to eat tonight'] -> ['Let me take a seat,', 'maybe we can have something to eat tonight']",
        "split: OCR[695] -> SRT[718-719]: ['- Yes    - Just give it to me'] -> ['Yes', 'Just give it to me']",
        "edit: OCR[712] -> SRT[736]: 'Have you had any idea?' -> 'Have you had any ideas?'",
        'edit: OCR[725] -> SRT[749]: "The one wearing red dress who stands under the lantern, that\'s her" -> "The one wearing the red dress who stands under the lantern, that\'s her"',
        "edit: OCR[743] -> SRT[767]: 'I am carrying out my duty only, men!' -> 'I am carrying my duty only. Men!'",
        "split: OCR[744] -> SRT[768-769]: ['- Yes!    - Remove all the things'] -> ['Yes!', 'Remove all the things']",
        "split: OCR[751] -> SRT[776-777]: [\"- No, we can't move it    - Let me do it\"] -> [\"No, we can't move it\", 'Let me do it']",
        "edit: OCR[753] -> SRT[779]: 'Last time you escaped from Yee Hung Hostel' -> 'Last time you could escape from Yee Hung Hostel'",
        "split: OCR[756] -> SRT[782-783]: [\"I've got to defeat him by one powerful strike\"] -> [\"I've got to defeat him\", 'by one powerful strike']",
        "split: OCR[760] -> SRT[787-788]: ['Your legs and hands are all broken by me'] -> ['Your legs and hands', 'are all broken by me']",
        "edit: OCR[767] -> SRT[795]: \"Don't panic, you'll be alright… Chan!\" -> \"Don't panic, you'll be all right… Chan!\"",
        'delete: OCR[768] "Don\'t panic" not present in SRT',
        'edit: OCR[772] -> SRT[799]: "He is Seng-ko-lin-ch\'in, that bastard" -> "He is Seng-ko-lin-ch\'in, that bastard."',
        "edit: OCR[775] -> SRT[802]: 'Let me stop here first, I want a smoke' -> 'Let me stop here first, I want a smoke.'",
        'edit: OCR[776] -> SRT[803]: "It\'s better to smoke now" -> "It\'s better to smoke now."',
        'edit: OCR[777] -> SRT[804]: "Yes, it\'s better" -> "Yes, it\'s better."',
        "edit: OCR[779] -> SRT[806]: 'the Yee Hung Brothel' -> 'the Yee Hung Brothel.'",
        "edit: OCR[780] -> SRT[807]: 'But he framed us in return' -> 'But he framed us in return.'",
        "edit: OCR[782] -> SRT[809]: 'during the examination' -> 'during the examination.'",
        "insert: SRT[811] 'He finally won the race' not present in OCR",
        "edit: OCR[791] -> SRT[819]: 'Because being the scholar is too simple for me' -> 'Because being the scholar is too simple to me'",
        "split: OCR[797] -> SRT[825-826]: [\"Although you have taken 2 months' rest,\"] -> ['Although you have taken', \"2 months' rest,\"]",
        "edit: OCR[798] -> SRT[827]: 'your legs and hands have not been totally recovered' -> 'your legs and hands have not been totally recovered.'",
        "edit: OCR[799] -> SRT[828]: '- Mr. Ha Yee    - Coming' -> 'Coming'",
        "split: OCR[801] -> SRT[830-831]: ['I will make the last herbal tea for you later'] -> ['I will make the last herbal tea', 'for you later']",
        'edit: OCR[812] -> SRT[842]: "We can\'t beg for food if we are late!" -> "We can\'t beg for good if we are late!"',
        'delete: OCR[814] "You\'re not a master now." not present in SRT',
        "edit: OCR[815] -> SRT[844]: 'Give me money please' -> 'Give me money, please'",
        "edit: OCR[823] -> SRT[852]: 'You are off duty, so I just want to lend it' -> 'You are off duty, so I just want to lend it.'",
        "split: OCR[847] -> SRT[876-877]: ['- May I…    - No'] -> ['May I…', 'No']",
        "edit: OCR[851] -> SRT[881]: 'Beggar, do you want the broken charcoal?' -> 'Beggar, do you want the broken carbon?'",
        "edit: OCR[863] -> SRT[893]: 'You are mistaken, he is not So Chan' -> 'You have mistaken, he is not So Chan'",
        "shift: OCR[870-871] -> SRT[900-901]: ['Sister,', \"he wouldn't be that poor if it were not for you\"] -> [\"Sister, he wouldn't be that poor\", 'if it were not for you']",
        'edit: OCR[873] -> SRT[903]: "I can\'t stand the hunger" -> "I can\'t stand the hunger."',
        "edit: OCR[874] -> SRT[904]: 'So I bit the dumpling of the kid' -> 'So I bit the dumpling of the kid.'",
        "edit: OCR[877] -> SRT[907]: 'if I chopped yours' -> 'if I chopped yours?'",
        "split: OCR[885] -> SRT[915-916]: ['Are they going to treat me some food?'] -> ['Are they going to treat me', 'some food?']",
        'edit: OCR[898] -> SRT[929]: "Dad. It\'s quite delicious" -> "It\'s quite delicious"',
        "edit: OCR[908] -> SRT[939]: 'I want to save it for midnight snack' -> 'I want to save it for a midnight snack'",
        "split: OCR[931] -> SRT[962-963]: ['One cloth is for you and the other is for Chan'] -> ['One cloth is for you', 'and the other is for Chan']",
        "split: OCR[935] -> SRT[967-968]: ['- Give them to me, come on    - What for?'] -> ['Give them to me, come on', 'What for?']",
        "split_edit: OCR[936] -> SRT[969-970]: [\"It's new year, you should receive a red packet\"] -> [\"It's new year,\", 'you should receive red pocket']",
        "split_edit: OCR[939] -> SRT[973-974]: ['- Wish you ever beauty    - Thank you'] -> ['Wish you ever beauty', 'Thank you…']",
        "edit: OCR[945] -> SRT[980]: 'I will cook you some new year cake' -> 'I will cook you some new year cakes'",
        'edit: OCR[950] -> SRT[985]: "To fight against Chiu, we need a union of the Beggar\'s Association" -> "To fight against Chiu, we need a union of the Beggars\' Association"',
        'edit: OCR[955] -> SRT[990]: "Uncle, I don\'t have faith to defeat them" -> "Uncle, I don\'t have faith in defeating them"',
        "merge: OCR[963-964] -> SRT[998]: ['He was a scholar of Martial Arts', 'before…'] -> ['He was a scholar of Martial Arts before…']",
        "edit: OCR[976] -> SRT[1010]: 'you can achieve something' -> 'you can achieve something.'",
        "split: OCR[986] -> SRT[1020-1021]: ['Son, I tried very hard to get this for you'] -> ['Son,', 'I tried very hard to get this for you']",
        "edit: OCR[995] -> SRT[1030]: \"It's ugly, it's right to wipe it away\" -> \"It's ugly, it's right to wipe it away.\"",
        "split: OCR[1000] -> SRT[1035-1036]: ['- Is there anything to eat?    - No'] -> ['Is there anything to eat?', 'No']",
        "split: OCR[1002] -> SRT[1038-1039]: [\"See your look, it's a waste for you not to beg\"] -> ['See your look,', \"it's a waste for you not to beg\"]",
        "edit: OCR[1028] -> SRT[1065]: 'Who are you?' -> 'What are you?'",
        'edit: OCR[1050] -> SRT[1087]: "I won\'t care who you are, I just want to stop the conversation" -> "I won\'t care who you are, I just want to stop the conversation."',
        'edit: OCR[1051] -> SRT[1088]: "Please step aside, don\'t stop me from sleeping" -> "Please step aside, don\'t stop me from sleeping."',
        "merge_edit: OCR[1053-1054] -> SRT[1090]: ['No… I just want to sleep', 'with you'] -> ['No… I just want to sleep with you.']",
        "edit: OCR[1065] -> SRT[1101]: 'Hope you can make good use of it. Come on' -> 'Hope you can make good use of it Come on'",
        "shift: OCR[1085-1086] -> SRT[1121-1122]: [\"- Let's chase them    - Stop!\", 'The Emperor is setting off soon'] -> [\"Let's chase them\", 'Stop The Emperor is setting off soon']",
        "insert: SRT[1127] 'Ask that old bag to hand us the waddy' not present in OCR",
        'edit: OCR[1099] -> SRT[1136]: "I think you won\'t come back" -> "I think you won\'t come back."',
        'edit: OCR[1102] -> SRT[1139]: "We\'d better find someone to compete for the leadership" -> "We\'d find someone to compete for the leadership."',
        "edit: OCR[1122] -> SRT[1159]: 'I won' -> 'I won.'",
        "edit: OCR[1125] -> SRT[1162]: 'You are not qualified to be the leader of us' -> 'You are not qualified to be the leader of us.'",
        'edit: OCR[1129] -> SRT[1166]: "But it\'s different from the standard stances!" -> "But it\'s unlike from the standard stances!"',
        "edit: OCR[1138] -> SRT[1175]: 'We becomes the biggest association' -> 'We become the biggest association'",
        "edit: OCR[1155] -> SRT[1192]: 'whole-heartedly, to care much for him, maybe, treat him dinner' -> 'whole-heartedly, to care much for him, maybe treat him dinner'",
        "edit: OCR[1162] -> SRT[1199]: 'They are easily to be cheated, I am really a genius!' -> 'They are easily cheated, I am really a genius!'",
        'edit: OCR[1163] -> SRT[1200]: "We\'ll have better living" -> "We\'ll have a better living"',
        "edit: OCR[1166] -> SRT[1203]: 'Bravo…' -> 'You should have faith, you won, bravo…'",
        "delete: OCR[1179] 'Chan,' not present in SRT",
        "split: OCR[1180] -> SRT[1216-1217]: ['do you understand everything written in this book?'] -> ['Do you understand everything', 'written in this book?']",
        "edit: OCR[1182] -> SRT[1219]: 'After getting the help of Taiwan Pill' -> 'After getting the help of Taiwan Pill,'",
        "edit: OCR[1186] -> SRT[1223]: 'there is no picture or description of it' -> 'there is no picture or description of it.'",
        'edit: OCR[1187] -> SRT[1224]: "I can\'t understand at all" -> "I can\'t understand it at all"',
        "split: OCR[1216] -> SRT[1253-1254]: ['- Check what has happened    - Yes'] -> ['Check what has happened', 'Yes']",
        "split_edit: OCR[1253] -> SRT[1291-1292]: [\"- Go on after I've left    - Sure\"] -> ['Go on after I left', 'Sure']",
        "split_edit: OCR[1255] -> SRT[1294-1295]: ['- Get ready the Unicom Smoke.    - Yes.'] -> ['Get ready the Unicom Smoke', 'Yes']",
        "shift: OCR[1295-1296] -> SRT[1335-1336]: ['- Really?    - Yes', 'Then I want to eat a sweet potato'] -> ['Really?', 'Yes, then I want to eat a sweet potato']",
        "edit: OCR[1306] -> SRT[1346]: 'What are you telling him?' -> 'Are you telling him?'",
        "edit: OCR[1312] -> SRT[1352]: 'Yes. Look at you, you are like beggar too' -> 'Yes. Look at you, you are like a beggar too'",
        "edit: OCR[1313] -> SRT[1353]: 'Are you interested to join us?' -> 'Are you interested in joining us?'",
        'edit: OCR[1334] -> SRT[1374]: "I\'ve got it. Just mix the 17 stances," -> "I\'ve got it Just mix the 17 stances,"',
        "edit: OCR[1344] -> SRT[1384]: 'You are great!' -> 'Sister!'",
        "edit: OCR[1345] -> SRT[1385]: 'Chan! Are you okay?' -> 'Tracy!'",
        'edit: OCR[1352] -> SRT[1392]: "Chiu\'s fellows have all been caught by us" -> "Chiu\'s fellows are all caught by us"',
        "edit: OCR[1356] -> SRT[1396]: 'Yes, be the top of all' -> 'Yes, be the top of all.'",
        'edit: OCR[1359] -> SRT[1399]: "But I don\'t like Scholar at all" -> "But I don\'t like Scholar at all."',
        "edit: OCR[1361] -> SRT[1401]: 'You first, I will go after you' -> 'You first, I will go after you.'",
        "delete: OCR[1372] 'Pick me up' not present in SRT",
        "edit: OCR[1374] -> SRT[1413]: 'Put me down' -> 'Put it down'",
        'edit: OCR[1377] -> SRT[1416]: "If so, you needn\'t squat to talk to me" -> "If so, you needn\'t squat and talk to me"',
        "split: OCR[1388] -> SRT[1427-1428]: [\"- It's reasonable    - Be smart\"] -> [\"It's reasonable\", 'Be smart']",
        "shift: OCR[1392-1393] -> SRT[1432-1433]: ['Long life…', '- … to Your Majesty    - Get up'] -> ['Long life to Your Majesty', 'Get up']",
        "delete: OCR[1411] 'Hurry up' not present in SRT",
        "delete: OCR[1412] 'Follow me… go…' not present in SRT",
    ]
    _assert_expected_differences(differences, expected)
    print()
    for i, diff in enumerate(differences, 1):
        print(f"{i:>3d}: {diff}")
