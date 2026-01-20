#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.validation.get_series_text_line_differences."""

from __future__ import annotations

from scinoephile.core.subtitles import Series
from scinoephile.core.validation import get_series_text_line_differences


def _get_series_text_line_differences(
    ocr_series: Series,
    srt_series: Series,
) -> list[str]:
    """Get get_series_text_line_differences output.

    Arguments:
        ocr_series: OCR subtitle series
        srt_series: SRT subtitle series
    Returns:
        list of differences
    """
    return get_series_text_line_differences(
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


def test_get_series_text_line_differences_kob(
    kob_eng_fuse_clean_validate_proofread_flatten: Series,
    kob_eng_timewarp_clean_proofread_flatten: Series,
):
    """Test get_series_text_line_differences with KOB English subtitles.

    Arguments:
        kob_eng_fuse_clean_validate_proofread_flatten: OCR English subtitles
        kob_eng_timewarp_clean_proofread_flatten: timewarped SRT English subtitles
    """
    differences = _get_series_text_line_differences(
        kob_eng_fuse_clean_validate_proofread_flatten,
        kob_eng_timewarp_clean_proofread_flatten,
    )
    # NOTE: Do not change expected entries through OCR[249]/SRT[260]; only adjust below.
    expected = [
        "added: SRT[31] 'What?' not present in OCR",
        "added: SRT[58] 'Tips. Tips…' not present in OCR",
        (
            "split: OCR[59:60] != SRT[62:64]: "
            "['- Please give me some money    - Kidding? Damn you beggar!'] != "
            "['Please give me some money', 'Kidding? Damn you beggar!']"
        ),
        (
            "split: OCR[62:63] != SRT[66:68]: "
            "['- Give him tips    - Yes, young master'] != "
            "['Give him tips', 'Yes, young master']"
        ),
        (
            "split_modified: OCR[71:72] != SRT[76:78]: "
            "['- Come into my room.    - Please follow me'] != "
            "['Please follow me', 'Come into my room…']"
        ),
        (
            "shifted: OCR[103:105] != SRT[109:111]: "
            "['What?', \"Who dared so? I will hit that bastard's mouth for you\"] != "
            "['What? Who dared so?', \"I will hit that bastard's mouth for you\"]"
        ),
        (
            "shifted: OCR[122:124] != SRT[128:130]: "
            "['- May I be excused,    - Mr Chiu,', 'Miss Yushang has arrived'] != "
            "['May I be excused', 'Mr Chiu, Miss Yushang has arrived']"
        ),
        (
            "split: OCR[133:134] != SRT[139:141]: "
            "['If any of you can offer more than 100,000 taels'] != "
            "['If any of you can offer', 'more than 100,000 taels']"
        ),
        (
            "split: OCR[135:136] != SRT[142:144]: "
            "[\"Don't quarrel because of such a small amount, isn't it right?\"] != "
            '["Don\'t quarrel because of such a small amount,", '
            '"isn\'t it right?"]'
        ),
        (
            "split_modified: OCR[143:144] != SRT[151:153]: "
            '["I love money too. But, I don\'t like you"] != '
            "['I love money too', \"But, I don't like you\"]"
        ),
        (
            "split: OCR[150:151] != SRT[159:161]: "
            '["Don\'t worry, I have many pretty girls here"] != '
            "[\"Don't worry,\", 'I have many pretty girls here']"
        ),
        (
            "split: OCR[185:186] != SRT[195:197]: "
            "['- Come on, give tips to the girls here    - Master'] != "
            "['Come on, give tips to the girls here', 'Master']"
        ),
        (
            "modified: OCR[247] != SRT[258]: "
            "'Stop, I have taken his money, 100,000 taels you know?' != "
            "'Stop, I have taken his money, 100,000 taels, you know?'"
        ),
        (
            "modified: OCR[248] != SRT[259]: "
            '"I won\'t give it back" != "I won\'t give it back."'
        ),
        (
            "modified: OCR[249] != SRT[260]: "
            "'About the personality of Mr So…' != 'About the personality of Mr. So…'"
        ),
        ("modified: OCR[251] != SRT[262]: 'Leave here first' != 'Leave here first.'"),
        (
            "modified: OCR[252] != SRT[263]: "
            "'Yes, you are right' != 'Yes, you are right.'"
        ),
        (
            "merged_modified: OCR[253:254] != SRT[264:266]: "
            "['- Miss Seven…    - Just accept this'] != "
            "['Miss Seven…', 'Just accept this.']"
        ),
        (
            "modified: OCR[256] != SRT[268]: "
            "'Miss, first of all, I have good news for you' != "
            "'Miss, first of all, I have a good news for you'"
        ),
        (
            "modified: OCR[258] != SRT[270]: "
            "'To me, this is a bad news' != 'To me, this is bad news'"
        ),
        (
            "shifted: OCR[285:287] != SRT[297:299]: "
            "['- Witness?    - Yes', 'I swear in front of your sword'] != "
            "['Witness?', 'Yes, I swear in front of your sword']"
        ),
        (
            "modified: OCR[291] != SRT[303]: "
            "\"Don't you know it isn't that easy to be my husband?\" != "
            "\"Don't you know it's not that easy to be my husband?\""
        ),
        (
            "modified: OCR[302] != SRT[314]: "
            '"OK, but you\'d give me some time to consider it" != '
            '"OK, but you\'d give me some time to consider it."'
        ),
        (
            "modified: OCR[394] != SRT[406]: "
            "'Take care of my lychee, you fathead!' != "
            "'Take care of my Lychee, you fathead!'"
        ),
        "modified: OCR[414] != SRT[426]: 'Hide in' != 'Hide in here'",
        (
            "modified: OCR[419] != SRT[431]: "
            "'You are great! I love it' != 'You are great! I love it.'"
        ),
        (
            "modified: OCR[422] != SRT[434]: "
            "'You are bad, how can you say so to me?' != "
            "'You are bad, how can you say that to me?'"
        ),
        (
            "modified: OCR[428] != SRT[440]: "
            "'I wanted to trick you actually, you are really smart' != "
            "'I wanted to trick you actually, you are really smart.'"
        ),
        (
            "split: OCR[477:478] != SRT[489:491]: "
            '["- You shouldn\'t put it that way    - What?"] != '
            "[\"You shouldn't put it that way\", 'What?']"
        ),
        "added: SRT[530] 'Bravo…' not present in OCR",
        (
            "split: OCR[539:540] != SRT[553:555]: "
            "['What did you say?'] != ['What did', 'you say?']"
        ),
        (
            "split: OCR[544:545] != SRT[559:561]: "
            "['Damn you Cheng! You betrayed me!'] != "
            "['Damn you Cheng!', 'You betrayed me!']"
        ),
        "missing: OCR[562] 'You… You…' not present in SRT",
        "missing: OCR[566] 'OK' not present in SRT",
        (
            "modified: OCR[567] != SRT[581]: "
            "'I want to take a statement from you as record' != "
            "'I want to take some statements from you as record'"
        ),
        (
            "modified: OCR[570] != SRT[584]: "
            "'Is Miss Yushang his mom?' != 'Is Miss Yushang your mom?'"
        ),
        (
            "split: OCR[599:600] != SRT[613:615]: "
            "['- Kill me    - No, kill me'] != ['Kill me', 'No, kill me']"
        ),
        (
            "split_modified: OCR[600:601] != SRT[615:617]: "
            '["- Kill me.    - Your Majesty, you\'d better kill me"] != '
            "['Kill me', \"Your Majesty, you'd better kill me\"]"
        ),
        (
            "split: OCR[607:608] != SRT[623:625]: "
            '["So\'s family should be sentenced to death"] != '
            "[\"So's family should be\", 'sentenced to death']"
        ),
        (
            "modified: OCR[612] != SRT[629]: "
            '"So, he didn\'t miscarry out any duty" != '
            '"So, he didn\'t miscarry any duty"'
        ),
        (
            "split: OCR[621:623] != SRT[638:639]: "
            "[\"Why couldn't you find out\", 'they cheated during the examination?'] "
            "!= "
            '["Why couldn\'t you find out they cheated during the examination?"]'
        ),
    ]
    _assert_expected_differences(differences, expected)
    print()
    for i, diff in enumerate(differences, 1):
        print(f"{i:>3d}: {diff}")
