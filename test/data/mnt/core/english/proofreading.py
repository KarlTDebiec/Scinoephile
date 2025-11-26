#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""MNT English proofreading test cases."""

from __future__ import annotations

from scinoephile.core.english.proofreading import EnglishProofreadingTestCase

# noinspection PyArgumentList
test_cases = [
    EnglishProofreadingTestCase.get_test_case_cls(11)(
        subtitle_1="♪ Hey, let's go ♪",
        subtitle_2="♪ Hey, let's go ♪",
        subtitle_3="♪ I'm happy as can be ♪",
        subtitle_4="♪ Let's go walking\nYou and me ♪",
        subtitle_5="♪ Ready, set\nCome on, let's go ♪",
        subtitle_6="♪ Over the hill\nAcross the field ♪",
        subtitle_7="Through the tunnel we'll go♪",
        subtitle_8="♪ We'll run across the bridge ♪",
        subtitle_9="♪ And down the bumpy gravel road ♪",
        subtitle_10="♪ Right beneath the spider's web ♪",
        subtitle_11="♪ Ready, set, let's go ♪",
        revised_7="♪ Through the tunnel we'll go ♪",
        note_7="Added missing opening music note at the start of the "
        "subtitle for consistency with other lines.",
        difficulty=1,
    ),
    EnglishProofreadingTestCase.get_test_case_cls(13)(
        subtitle_1="♪ Hey, let's go ♪",
        subtitle_2="♪ Hey, let's go ♪",
        subtitle_3="♪ I'm happy as can be ♪",
        subtitle_4="♪ Let's go walking\nYou and me ♪",
        subtitle_5="♪ Ready, set\nCome on, let's go ♪",
        subtitle_6="♪ The foxes and the badgers, too ♪",
        subtitle_7="♪ All come out to play ♪",
        subtitle_8="♪ They all want to explore ♪",
        subtitle_9="♪ The deep and wonderful woods all day ♪",
        subtitle_10="♪ Look at all my many friends ♪",
        subtitle_11="♪ Ready, set, let's go ♪",
        subtitle_12="♪ Look at all my many friends ♪",
        subtitle_13="♪ Ready, set, let's go ♪",
        verified=True,
    ),
    EnglishProofreadingTestCase.get_test_case_cls(1)(
        subtitle_1="(ENGINE RUMBLING)",
        verified=True,
    ),
    EnglishProofreadingTestCase.get_test_case_cls(4)(
        subtitle_1="(GASPS)",
        subtitle_2="- Hey Dad, want some caramel?\n- Thanks. How you doing back there?",
        subtitle_3="- Fine.\n- Are you tired? Oop!",
        subtitle_4="- Mmm-mmm.\n- We're almost there.",
        verified=True,
    ),
    EnglishProofreadingTestCase.get_test_case_cls(1)(
        subtitle_1="Mei, hide.",
        verified=True,
    ),
    EnglishProofreadingTestCase.get_test_case_cls(3)(
        subtitle_1="Whoops. I thought\nthat was a policeman.",
        subtitle_2="Hi!",
        subtitle_3="(BOTH LAUGHING)",
        verified=True,
    ),
    EnglishProofreadingTestCase.get_test_case_cls(7)(
        subtitle_1="Hello there. Are your parents around?\nWe're your new neighbors.",
        subtitle_2="Great. Thanks.",
        subtitle_3="Hello! Hi, we're the Kusakabes!\nWe're moving in down the street.",
        subtitle_4="Why don't you and your\nfamily stop by sometime?",
        subtitle_5="MAN: Okay, Sure. Good to meet you.",
        subtitle_6="Uh!",
        subtitle_7="Hey, thanks a lot.",
        revised_5="MAN: Okay, sure. Good to meet you.",
        note_5="Changed 'Okay, Sure.' to 'Okay, sure.' to correct "
        "capitalization after the comma.",
        difficulty=1,
    ),
    EnglishProofreadingTestCase.get_test_case_cls(1)(
        subtitle_1="(WATER RUNNING)",
        verified=True,
    ),
    EnglishProofreadingTestCase.get_test_case_cls(5)(
        subtitle_1="This is it, girls.",
        subtitle_2="(GRUNTING)",
        subtitle_3="- Wait up!\n- Here you go.",
        subtitle_4="Mei, look at this bridge.",
        subtitle_5="A bridge?",
        verified=True,
    ),
    EnglishProofreadingTestCase.get_test_case_cls(7)(
        subtitle_1="There's a fish! Oh, look!\nThere's another one!",
        subtitle_2="So, how do you like the new place?",
        subtitle_3="Dad, it's perfect.",
        subtitle_4="Look at this. A tunnel of trees.",
        subtitle_5="Oh, wow! Look!",
        subtitle_6="(GIGGLING)",
        subtitle_7="Dad, hurry!",
        verified=True,
    ),
]  # test_cases
"""MNT English proofreading test cases."""

__all__ = [
    "test_cases",
]
