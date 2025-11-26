#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""T English proofreading test cases."""

from __future__ import annotations

from scinoephile.core.english.proofreading import EnglishProofreadingTestCase

# noinspection PyArgumentList
test_cases = [
    EnglishProofreadingTestCase.get_test_case_cls(2)(
        subtitle_1="Police.",
        subtitle_2="Show me your ID.",
        verified=True,
    ),
    EnglishProofreadingTestCase.get_test_case_cls(5)(
        subtitle_1="- Check his ID.\n- Yes sir.",
        subtitle_2="- What's in your bag?\n- Headquarter,",
        subtitle_3="- Let me see.\n- please verify ID number C532743…",
        subtitle_4="Bracket 1, Kwai Ching-hung.",
        subtitle_5="Open it.",
        verified=True,
    ),
    EnglishProofreadingTestCase.get_test_case_cls(8)(
        subtitle_1="The arrangement for Hong Kong",
        subtitle_2="contained in the agreement\nare not measures of expediency.",
        subtitle_3="They are long-term policies\nwhich will be incorporated",
        subtitle_4="in the Basic Law for Hong Kong",
        subtitle_5="and preserved intact for 50 years from 1997.",
        subtitle_6="It is the common interests",
        subtitle_7="as well as shared\nresponsibilities of China and Britain",
        subtitle_8="to ensure the Joint Declaration is fully\n"
        "implemented with no encumbrances.",
        revised_6="It is the common interest",
        note_6="Corrected 'interests' to 'interest' to match the singular "
        "subject 'It is the common interest'.",
        difficulty=1,
    ),
    EnglishProofreadingTestCase.get_test_case_cls(15)(
        subtitle_1="An armed robbery took place this afternoon in Kwun Tong.",
        subtitle_2="4 armed suspects robbed 5 gold shops\non Mut Wah Street.",
        subtitle_3="Fuck you!",
        subtitle_4="In the footage provided by our audience,",
        subtitle_5="the robbers exchanged fire",
        subtitle_6="with the Special Duties Unit.",
        subtitle_7="2 passersby and 3 policemen\nwere injured in the incident.",
        subtitle_8="The 5 gold shops lost $10M in total.",
        subtitle_9="The police believe the mastermind",
        subtitle_10='is the "Most Wanted" Yip Kwok-foon.',
        subtitle_11="Bro foon, you're unbeatable!",
        subtitle_12="But shit has hit the fan!",
        subtitle_13="I told you to put more newspaper underneath!",
        subtitle_14="Look, there's blood everywhere!",
        subtitle_15="Take it, jerk!",
        verified=True,
    ),
    EnglishProofreadingTestCase.get_test_case_cls(10)(
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
        revised_9="Times have changed.",
        note_9="Corrected 'Time has changed.' to 'Times have changed.'",
        difficulty=1,
    ),
    EnglishProofreadingTestCase.get_test_case_cls(6)(
        subtitle_1="Especially for your swag, Bro foon!",
        subtitle_2="It took us 2 years to fence it last time!",
        subtitle_3="Stocks, real estate,\nand even chestnuts are more profitable!",
        subtitle_4="Do me a favor.",
        subtitle_5="40%.",
        subtitle_6="Bro foon, you always have your way!",
        revised_1="Especially for your swag, Bro Foon!",
        note_1="Corrected 'Bro foon' to 'Bro Foon' to capitalise the name as "
        "is standard for proper nouns.",
        revised_6="Bro Foon, you always have your way!",
        note_6="Corrected 'Bro foon' to 'Bro Foon' to capitalise the name as "
        "is standard for proper nouns.",
        difficulty=1,
    ),
    EnglishProofreadingTestCase.get_test_case_cls(5)(
        subtitle_1="How about you find another fence?",
        subtitle_2="If I can't take it, I doubt others would dare to!",
        subtitle_3="Fuck you!",
        subtitle_4="Open the safe!",
        subtitle_5="Are you robbing me?",
        verified=True,
    ),
    EnglishProofreadingTestCase.get_test_case_cls(1)(
        subtitle_1="Don't make me do it.",
        verified=True,
    ),
    EnglishProofreadingTestCase.get_test_case_cls(4)(
        subtitle_1="Thanks so much, Bro foon.",
        subtitle_2="Don't look me up in the future.",
        subtitle_3="There's no more business between us!",
        subtitle_4="We go separate ways!",
        revised_1="Thanks so much, Bro Foon.",
        note_1="Corrected 'Bro foon.' to 'Bro Foon.' (capitalized proper noun).",
        difficulty=1,
    ),
    EnglishProofreadingTestCase.get_test_case_cls(1)(
        subtitle_1="Light, Bro foon.",
        revised_1="Light, Bro Foon.",
        note_1="Corrected 'foon.' to 'Foon.' to capitalize the proper noun.",
        difficulty=1,
    ),
]  # test_cases
"""T English proofreading test cases."""

__all__ = [
    "test_cases",
]
