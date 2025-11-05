#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""T English proof test cases."""

from __future__ import annotations

from scinoephile.core.english.proofing.abcs import EnglishProofTestCase

# noinspection PyArgumentList
test_case_block_0 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="Police.",
    subtitle_2="Show me your ID.",
    verified=True,
)  # test_case_block_0
# noinspection PyArgumentList
test_case_block_1 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="- Check his ID.\n- Yes sir.",
    subtitle_2="- What's in your bag?\n- Headquarter,",
    subtitle_3="- Let me see.\n- please verify ID number C532743...",
    subtitle_4="Bracket 1, Kwai Ching-hung.",
    subtitle_5="Open it.",
    revised_2="- What's in your bag?\n- Headquarters,",
    note_2="Corrected 'Headquarter' to 'Headquarters' for proper noun usage.",
    revised_3="- Let me see.\n- Please verify ID number C532743...",
    note_3="Capitalized 'please' at the start of the sentence.",
    difficulty=1,
    prompt=True,
    verified=True,
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
    revised_1="The arrangements for Hong Kong",
    note_1="Changed 'arrangement' to plural 'arrangements' for subject-verb agreement.",
    revised_3="contained in the agreement\nare not measures of expediency",
    note_3="Removed period at the end to match subtitle style.",
    revised_7="It is in the common interests",
    note_7="Added 'in' to correct the phrase to 'It is in the common interests'.",
    difficulty=1,
    verified=True,
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
    revised_2="Four armed suspects robbed five gold shops\non Mut Wah Street.",
    note_2="Spelled out numbers at the beginning of sentences for formal style.",
    revised_3="Four armed suspects robbed five gold shops\non Mut Wah Street.",
    note_3="Spelled out numbers at the beginning of sentences for formal style.",
    revised_8="Two passersby and three policemen\nwere injured in the incident.",
    note_8="Spelled out numbers at the beginning of sentences for formal style.",
    revised_9="The five gold shops lost $10 million in total.",
    note_9="Spelled out 'five' and '$10M' as '$10 million' for "
    "consistency and clarity.",
    difficulty=1,
    prompt=True,
    verified=True,
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
    revised_5="You're paying $2M for $10M worth of swag?",
    note_5="Removed possessive 's' from '$10M's' for correct phrasing.",
    revised_9="Times have changed.",
    note_9="Changed 'Time has changed.' to 'Times have changed.' for "
    "correct idiomatic usage.",
    difficulty=1,
    verified=True,
)  # test_case_block_4
# noinspection PyArgumentList
test_case_block_5 = EnglishProofTestCase.get_test_case_cls(6)(
    subtitle_1="Especially for your swag, Bro Foon!",
    subtitle_2="It took us 2 years to fence it last time!",
    subtitle_3="Stocks, real estate,\nand even chestnuts are more profitable!",
    subtitle_4="Do me a favor.",
    subtitle_5="40%.",
    subtitle_6="Bro Foon, you always have your way!",
    revised_2="It took us two years to fence it last time!",
    note_2="Spelled out 'two' for consistency and formality.",
    difficulty=1,
    verified=True,
)  # test_case_block_5
# noinspection PyArgumentList
test_case_block_6 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="How about you find another fence?",
    subtitle_2="If I can't take it, I doubt others would dare to!",
    subtitle_3="Fuck you!",
    subtitle_4="Open the safe!",
    subtitle_5="Are you robbing me?",
    verified=True,
)  # test_case_block_6
# noinspection PyArgumentList
test_case_block_7 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Don't make me do it.",
    verified=True,
)  # test_case_block_7
# noinspection PyArgumentList
test_case_block_8 = EnglishProofTestCase.get_test_case_cls(4)(
    subtitle_1="Thanks so much, Bro Foon.",
    subtitle_2="Don't look me up in the future.",
    subtitle_3="There's no more business between us!",
    subtitle_4="We go separate ways!",
    verified=True,
)  # test_case_block_8
# noinspection PyArgumentList
test_case_block_9 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Light, Bro Foon.",
    difficulty=1,
    verified=True,
)  # test_case_block_9
# noinspection PyArgumentList
test_case_block_10 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Fisherman!",
    verified=True,
)  # test_case_block_10
# noinspection PyArgumentList
test_case_block_11 = EnglishProofTestCase.get_test_case_cls(8)(
    subtitle_1="Don't worry.",
    subtitle_2="These ships belong to Yi Fa.",
    subtitle_3="What's Yi Fa?",
    subtitle_4="Yi Fa from Panyu, Guangzhou.",
    subtitle_5="They smuggle electric appliances.",
    subtitle_6="So pompously? So brazenly?",
    subtitle_7="They have strong backing. It's legit!",
    subtitle_8="A TV set sells for $2K\nin Hong Kong and $8K in China.",
    difficulty=1,
    verified=True,
)  # test_case_block_11
# noinspection PyArgumentList
test_case_block_12 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="They earn millions of dollars in each transaction.",
    subtitle_2="Cash keeps rolling in!",
    verified=True,
)  # test_case_block_12
# noinspection PyArgumentList
test_case_block_13 = EnglishProofTestCase.get_test_case_cls(7)(
    subtitle_1="Used notes with no consecutive serial numbers.",
    subtitle_2="I need them today!",
    subtitle_3="You have $80M over there.",
    subtitle_4="I want it by 5pm!",
    subtitle_5="You go get it. I want it now!",
    subtitle_6="Manager Shum, how much do we have?",
    subtitle_7="Manager Fok!",
    revised_3="You have $80 million over there.",
    note_3="Changed '$80M' to '$80 million' for clarity and consistency.",
    revised_4="I want it by 5 PM!",
    note_4="Changed '5pm' to '5 PM.' for standard formatting.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_13
# noinspection PyArgumentList
test_case_block_14 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="We are in love but can't be together.",
    subtitle_2="I wait day by day but you never come back...",
    subtitle_3="I want to forget you but you haunt my memory.",
    subtitle_4="Mr Cheuk,",
    subtitle_5="let's discuss the price.",
    verified=True,
)  # test_case_block_14
# noinspection PyArgumentList
test_case_block_15 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="Was it a bit flat?",
    subtitle_2="No way! Let's start over!",
    subtitle_3="Red face,",
    subtitle_4="red skirt, red scarf,",
    subtitle_5="like white paper...",
    verified=True,
)  # test_case_block_15
# noinspection PyArgumentList
test_case_block_16 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="I said let's start over. Didn't you hear me?",
    verified=True,
)  # test_case_block_16
# noinspection PyArgumentList
test_case_block_17 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="I said let's start over. Didn't you hear me?",
    subtitle_2="Let's not waste time!",
    verified=True,
)  # test_case_block_17
# noinspection PyArgumentList
test_case_block_18 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="Mr Tycoon,",
    subtitle_2="we agreed on $3 billion.",
    subtitle_3="That's final.",
    subtitle_4="It's impossible to get so much cash\nout of the blue.",
    subtitle_5="I've only got $500M on hand.",
    revised_5="I've only got $500 million on hand.",
    note_5="Changed '$500M' to '$500 million' for consistency and clarity.",
    difficulty=1,
    verified=True,
)  # test_case_block_18
# noinspection PyArgumentList
test_case_block_19 = EnglishProofTestCase.get_test_case_cls(11)(
    subtitle_1="Did I say you could go?",
    subtitle_2="Take the $500M now.",
    subtitle_3="Don't get too greedy.",
    subtitle_4="Then I'll give you back half of your son.",
    subtitle_5="You want the upper or lower half?",
    subtitle_6="Do you really think I won't call the police?",
    subtitle_7="Do the cops know where your son is?",
    subtitle_8="All they can do is arrest and torture me.",
    subtitle_9="All they can do is arrest and torture me.",
    subtitle_10="But after 48 hours, they have to release me.",
    subtitle_11="By that time, however, you son will be...",
    revised_2="Take the $500 million now.",
    note_2="Changed '$500M' to '$500 million' for clarity and consistency.",
    revised_11="By that time, however, your son will be...",
    note_11="Corrected 'you son' to 'your son'.",
    difficulty=1,
    verified=True,
)  # test_case_block_19
# noinspection PyArgumentList
test_case_block_20 = EnglishProofTestCase.get_test_case_cls(7)(
    subtitle_1="Call the Commissioner of Police!",
    subtitle_2="I said let's start over. Didn't you hear me?",
    subtitle_3="You hear me, or not?",
    subtitle_4="If you can't hear me with your ear,",
    subtitle_5="I might as well cut if off, OK?",
    subtitle_6="Please don't!",
    subtitle_7="I'm sorry! I'm sorry!",
    revised_5="I might as well cut it off, OK?",
    note_5="Changed 'if' to 'it' for correct reference to 'ear'.",
    difficulty=1,
    verified=True,
)  # test_case_block_20
# noinspection PyArgumentList
test_case_block_21 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="You should've said so earlier.",
    verified=True,
)  # test_case_block_21
# noinspection PyArgumentList
test_case_block_22 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="What's up?",
    subtitle_2="The Commissioner didn't answer?",
    verified=True,
)  # test_case_block_22
# noinspection PyArgumentList
test_case_block_23 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="You're playing me, right?",
    subtitle_2="Let's play it all the way then!",
    verified=True,
)  # test_case_block_23
# noinspection PyArgumentList
test_case_block_24 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="Leaving so soon, Officer Wu?",
    subtitle_2="Mr Tycoon is looking for you.",
    subtitle_3="Mr Tycoon, didn't you call the cops? Come here!",
    verified=True,
)  # test_case_block_24
# noinspection PyArgumentList
test_case_block_25 = EnglishProofTestCase.get_test_case_cls(21)(
    subtitle_1="Mr Ho.",
    subtitle_2="They are sending these dogs after me,",
    subtitle_3="but they are useless.",
    subtitle_4="No wonder it was easy to kidnap your son.",
    subtitle_5="So, you are willing to confess?",
    subtitle_6="Officer,",
    subtitle_7="if I said I'd fucked your mother,\ndid I really fuck her?",
    subtitle_8="Shouldn't you ask Mr Ho where his son is?",
    subtitle_9="My son...",
    subtitle_10="is all right.",
    subtitle_11="I came here to borrow money from Mr Tycoon.",
    subtitle_12="Is that a crime?",
    subtitle_13="Mr Ho, tell us if he's threatening you.",
    subtitle_14="We can arrest him right away!",
    subtitle_15="No, he's not.",
    subtitle_16="Have you heard it loud and clear, Officer?",
    subtitle_17="I said he's not threatening me!",
    subtitle_18="Calm down, Royal Hong Kong Police!",
    subtitle_19="Mr Tycoon,",
    subtitle_20='how much will you "lend" me?',
    subtitle_21="$3 billion.",
    verified=True,
)  # test_case_block_25
# noinspection PyArgumentList
test_case_block_26 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Are you in Guangzhou for business or leisure?",
    verified=True,
)  # test_case_block_26
# noinspection PyArgumentList
test_case_block_27 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="Excuse me?",
    subtitle_2="Business? Travel?",
    subtitle_3="Yea, I am a businessman.",
    revised_3="Yeah, I am a businessman.",
    note_3="Changed 'Yea' to 'Yeah' for correct informal affirmation.",
    difficulty=1,
    verified=True,
)  # test_case_block_27
# noinspection PyArgumentList
test_case_block_28 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Guangzhou Railway Station",
    verified=True,
)  # test_case_block_28
# noinspection PyArgumentList
test_case_block_29 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="I'd like to reserve a private room",
    subtitle_2="at 8pm tomorrow.",
    subtitle_3="My name is Chen. Thank you.",
    revised_2="at 8 PM tomorrow.",
    note_2="Changed '8pm' to '8 PM' for standard formatting.",
    difficulty=1,
    verified=True,
)  # test_case_block_29
# noinspection PyArgumentList
test_case_block_30 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="Hello, Commander.",
    subtitle_2="8pm tomorrow at Fengman Restaurant.",
    subtitle_3="Who the fuck am I? I'm Chiu.",
    subtitle_4="Don't make me fucking wait for you.",
    subtitle_5="That's it.",
    revised_2="8 PM tomorrow at Fengman Restaurant.",
    note_2="Changed '8pm' to '8 PM' for standard formatting.",
    difficulty=1,
    verified=True,
)  # test_case_block_30
# noinspection PyArgumentList
test_case_block_31 = EnglishProofTestCase.get_test_case_cls(13)(
    subtitle_1="Fengman Restaurant",
    subtitle_2="Almost there, Mr Fong.",
    subtitle_3="OK.",
    subtitle_4="Which room?",
    subtitle_5="OK. Coming.",
    subtitle_6="- Take it.\n- What?",
    subtitle_7="Take it. Let me put the tie on.",
    subtitle_8="Da-bao. This way.",
    subtitle_9="Mr Fong.",
    subtitle_10="Where's the vase?",
    subtitle_11="It's just a cheap one.",
    subtitle_12="Never mind. Let's go.",
    subtitle_13="Chief Chen.",
    verified=True,
)  # test_case_block_31
# noinspection PyArgumentList
test_case_block_32 = EnglishProofTestCase.get_test_case_cls(12)(
    subtitle_1="Chief Chen.",
    subtitle_2="This is Zhang Da-bao, Boss Zhang,",
    subtitle_3="This is Zhang Da-bao, Boss Zhang,",
    subtitle_4="who has bought Yi Fa.",
    subtitle_5="This is Chief Chen from Industry and Commerce.",
    subtitle_6="We're buddies.",
    subtitle_7="Nice to meet you, Chief Chen.",
    subtitle_8="Nice to meet you.",
    subtitle_9="Let's have a drink.",
    subtitle_10="Let's drink together.",
    subtitle_11="Have a seat.",
    subtitle_12="Bottoms up!",
    verified=True,
)  # test_case_block_32
# noinspection PyArgumentList
test_case_block_33 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="Boss Zhang cannot drink?",
    subtitle_2="Bottoms up!",
    subtitle_3="I said bottoms up!",
    subtitle_4="Yes!",
    subtitle_5="Bottoms up!",
    verified=True,
)  # test_case_block_33
# noinspection PyArgumentList
test_case_block_34 = EnglishProofTestCase.get_test_case_cls(34)(
    subtitle_1="Da-bao is my buddy.",
    subtitle_2="We've only met quite recently.",
    subtitle_3="But we hit it off right away!",
    subtitle_4="Chief Chen,",
    subtitle_5="Chief Chen,",
    subtitle_6="please help him.",
    subtitle_7="This vase must be expensive!",
    subtitle_8="Just a modest gift.",
    subtitle_9="Here's how it works:",
    subtitle_10="when Chief Chen grows tired of it,\nBoss Zhang can buy it back!",
    subtitle_11="It's worth at least RMB¥300K!",
    subtitle_12="Didn't we agree on RMB¥200K?",
    subtitle_13="I got the price wrong?",
    subtitle_14="Oh, even Homer sometimes nods.",
    subtitle_15="No way!",
    subtitle_16="Chief Chen is a connoisseur.",
    subtitle_17="What do we know?",
    subtitle_18="If Chief Chen says RMB¥300K, then it's RMB¥300K.",
    subtitle_19="Come get the business license tomorrow.",
    subtitle_20="I'll have it nicely framed for you.",
    subtitle_21="Thanks so much, Chief Chen.",
    subtitle_22="We're buddies.",
    subtitle_23="Boss Zhang, what would you like to eat?",
    subtitle_24="Braised pork with preserved vegetables.",
    subtitle_25="That's too oily for me.",
    subtitle_26="Let me order.",
    subtitle_27="Shall we have a seafood platter?",
    subtitle_28="Let me order it.",
    subtitle_29="Waiter!",
    subtitle_30="Mr Zhang, best of luck with your business!",
    subtitle_31="Thanks a lot.",
    subtitle_32="Cheers.",
    subtitle_33="Bottoms up!",
    subtitle_34="Bottoms up!",
    revised_11="It's worth at least ¥300,000!",
    note_11="Changed 'RMB¥300K' to '¥300,000' for clarity and standard formatting.",
    revised_12="Didn't we agree on ¥200,000?",
    note_12="Changed 'RMB¥200K' to '¥200,000' for clarity and standard formatting.",
    revised_18="If Chief Chen says ¥300,000, then it's ¥300,000.",
    note_18="Changed 'RMB¥300K' to '¥300,000' for clarity and standard formatting.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_34
# noinspection PyArgumentList
test_case_block_35 = EnglishProofTestCase.get_test_case_cls(8)(
    subtitle_1="This guy plays golf every Sunday\nin Clear Water Bay.",
    subtitle_2="One-way road. Quiet. No phone signal. It may work.",
    subtitle_3="Hey! Where's our rice?",
    subtitle_4="Next.",
    subtitle_5="This one is easy.",
    subtitle_6="A super playboy.",
    subtitle_7="Drunk every night.",
    subtitle_8="He recently has an actress as a mistress.",
    revised_8="He recently took an actress as a mistress.",
    note_8="Changed 'has' to 'took' for more natural phrasing in this context.",
    difficulty=1,
    verified=True,
)  # test_case_block_35
# noinspection PyArgumentList
test_case_block_36 = EnglishProofTestCase.get_test_case_cls(8)(
    subtitle_1="Hey!",
    subtitle_2="Where is our rice?",
    subtitle_3="Rice? Give me a second.",
    subtitle_4="Your rice is coming right away.",
    subtitle_5="Sometimes he would send his driver away.",
    subtitle_6="Sorry to keep you waiting.",
    subtitle_7="Enjoy your food.",
    subtitle_8="Close the door.",
    verified=True,
)  # test_case_block_36
# noinspection PyArgumentList
test_case_block_37 = EnglishProofTestCase.get_test_case_cls(16)(
    subtitle_1="Sir, please follow me.",
    subtitle_2="Give me a cup of tea.",
    subtitle_3="Hey! Haven't you gone to the bathroom just now?",
    subtitle_4="- Wait! Don't puke.\n- Hey! The rice is cold!",
    subtitle_5="Give me a second.",
    subtitle_6="- I'm sorry. The rice is cold?\n- I want tea.",
    subtitle_7="- Hurry up!\n- Tell me the room number...",
    subtitle_8="- I want tea.\n- Give me a second. I'll show you the way.",
    subtitle_9="Sure, I'll get you tea.",
    subtitle_10="Give me a second. I will be right back.",
    subtitle_11="Take it easy.",
    subtitle_12="We came to China to shake off those cop dogs.",
    subtitle_13="You went too far last time!",
    subtitle_14="I live life to the full.",
    subtitle_15="C'est la vie.",
    subtitle_16="There's no other way.",
    verified=True,
)  # test_case_block_37
# noinspection PyArgumentList
test_case_block_38 = EnglishProofTestCase.get_test_case_cls(6)(
    subtitle_1="We've stolen cars, committed burglaries,",
    subtitle_2="and robbed cash vans.",
    subtitle_3="We even kidnapped the tycoon's son.",
    subtitle_4="Should we do more kidnaps?",
    subtitle_5="What do you have in mind?",
    subtitle_6="Spit it out. We can discuss.",
    revised_4="Should we do more kidnappings?",
    note_4="Changed 'kidnaps' to 'kidnappings' for correct noun usage.",
    difficulty=1,
    verified=True,
)  # test_case_block_38
# noinspection PyArgumentList
test_case_block_39 = EnglishProofTestCase.get_test_case_cls(18)(
    subtitle_1="I'm a mountaineer.",
    subtitle_2="After conquering one mountain,",
    subtitle_3="I need to find a higher and harder mountain.",
    subtitle_4="That's it.",
    subtitle_5="Before finding that mountain,",
    subtitle_6="let's find the money first.",
    subtitle_7="Let's keep doing it.",
    subtitle_8="Cheng, 53 years old.",
    subtitle_9="No children. His wife is in charge.",
    subtitle_10="A mobile phone used to cost over RMB¥10K.\nWho could afford that?",
    subtitle_11="Not everyone is a child of\na high-ranking official.",
    subtitle_12="Now the cheaper, the better.",
    subtitle_13="We have a population of 10 million.",
    subtitle_14="Say RMB¥1K a set,",
    subtitle_15="RMB¥10K for 10 sets.",
    subtitle_16="We will be fatter than Chow Yun-fat!",
    subtitle_17="Beepers are already outdated.",
    subtitle_18="OK, I'll talk to you later.",
    revised_10="A mobile phone used to cost over ¥10,000.\nWho could afford that?",
    note_10="Changed 'RMB¥10K' to '¥10,000' for clarity and standard formatting.",
    revised_13="We have a population of ten million.",
    note_13="Spelled out 'ten million' for consistency and formality.",
    revised_14="Say ¥1,000 a set,",
    note_14="Changed 'RMB¥1K' to '¥1,000' for clarity and standard formatting.",
    revised_15="¥10,000 for ten sets.",
    note_15="Changed 'RMB¥10K' to '¥10,000' and '10' to 'ten' for clarity "
    "and consistency.",
    difficulty=1,
    verified=True,
)  # test_case_block_39
# noinspection PyArgumentList
test_case_block_40 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Excuse me, Boss.",
    verified=True,
)  # test_case_block_40
# noinspection PyArgumentList
test_case_block_41 = EnglishProofTestCase.get_test_case_cls(8)(
    subtitle_1="Please go on.",
    subtitle_2="Don't give us a hard time.\nWe're doing small business.",
    subtitle_3="Big Bro, these kids are great.",
    subtitle_4="The guy who came in first\nhas criminal record in Hong Kong.",
    subtitle_5="Don't know why you brought him here.",
    subtitle_6="I told you to bring some decent-looking guys.",
    subtitle_7="They all look like criminals and idiots.",
    subtitle_8="You should be out of business.",
    revised_4="The guy who came in first\nhas a criminal record in Hong Kong.",
    note_4="Added 'a' before 'criminal record' for correct phrasing.",
    difficulty=1,
    verified=True,
)  # test_case_block_41
# noinspection PyArgumentList
test_case_block_42 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="What is he staring at?",
    verified=True,
)  # test_case_block_42
# noinspection PyArgumentList
test_case_block_43 = EnglishProofTestCase.get_test_case_cls(4)(
    subtitle_1="He is smart and helpful",
    subtitle_2="I don't want the guy in blue either.",
    subtitle_3="You only need two men this time?",
    subtitle_4="Take the others to broaden their horizons.",
    verified=True,
)  # test_case_block_43
# noinspection PyArgumentList
test_case_block_44 = EnglishProofTestCase.get_test_case_cls(6)(
    subtitle_1="Got it!",
    subtitle_2="Let me see to it.",
    subtitle_3="What are you fucking looking at?",
    subtitle_4="You, you, get lost!",
    subtitle_5="Stop drinking and scram!",
    subtitle_6="You two come with me.",
    verified=True,
)  # test_case_block_44
# noinspection PyArgumentList
test_case_block_45 = EnglishProofTestCase.get_test_case_cls(12)(
    subtitle_1="Faster.",
    subtitle_2="So slow!",
    subtitle_3="Big Bro Chiu,",
    subtitle_4="Wang Lei.",
    subtitle_5="Hong Qi.",
    subtitle_6="Say Big Bro Chiu.",
    subtitle_7="Big Bro Chiu!",
    subtitle_8="They understand Cantonese?",
    subtitle_9="Of course!",
    subtitle_10="Come have a drink.",
    subtitle_11="Spruce them up before sending them to Hong Kong.",
    subtitle_12="Sure will!",
    verified=True,
)  # test_case_block_45
# noinspection PyArgumentList
test_case_block_46 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="Motherfucker.",
    subtitle_2="Sit and eat.",
    verified=True,
)  # test_case_block_46
# noinspection PyArgumentList
test_case_block_47 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="Commander,",
    subtitle_2="who's this Big Bro Chiu?",
    subtitle_3="Who cares if he is Big Bro Chiu or not?",
    verified=True,
)  # test_case_block_47
# noinspection PyArgumentList
test_case_block_48 = EnglishProofTestCase.get_test_case_cls(9)(
    subtitle_1="He is a douchebag.",
    subtitle_2="He is a sly,",
    subtitle_3="old fox who changes identities.",
    subtitle_4="He looks fucking like Kwai Ching-hung,",
    subtitle_5="the invisible King of Thieves in Hong Kong.",
    subtitle_6="Kwai Ching-hung disappeared",
    subtitle_7="after killing cops.",
    subtitle_8="Then Big Bro Chiu popped up.",
    subtitle_9="Big Bro Chiu is just a name.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_48
# noinspection PyArgumentList
test_case_block_49 = EnglishProofTestCase.get_test_case_cls(13)(
    subtitle_1="Is Fai here?",
    subtitle_2="Fai.",
    subtitle_3="What's up?",
    subtitle_4="- Someone is looking for you.\n- Hey.",
    subtitle_5="Bro Coke?",
    subtitle_6="Hey!",
    subtitle_7="She's Thai?",
    subtitle_8="Noon, go buy a dozen of Cokes.",
    subtitle_9="When did you come back?",
    subtitle_10="Just now.",
    subtitle_11="You are too kind. Come in and have a seat.",
    subtitle_12="Did you just speak Thai?",
    subtitle_13="Do you think I speak French?",
    revised_8="Noon, go buy a dozen Cokes.",
    note_8="Removed 'of' for correct phrasing: 'a dozen Cokes.'",
    difficulty=1,
    verified=True,
)  # test_case_block_49
# noinspection PyArgumentList
test_case_block_50 = EnglishProofTestCase.get_test_case_cls(20)(
    subtitle_1="You stink!",
    subtitle_2="Really?",
    subtitle_3="Bo.",
    subtitle_4="How can you be so rude?",
    subtitle_5="Come help set the table.",
    subtitle_6="Dinner will be served soon.",
    subtitle_7="Naughty girl.",
    subtitle_8="Go wash your hands.",
    subtitle_9="I did wash my hands.",
    subtitle_10="You ate yesterday. Are you going to eat today?",
    subtitle_11="Bo, slow down. Don't rush.",
    subtitle_12="Bro Coke.",
    subtitle_13="You want some?",
    subtitle_14="Shall we share it?",
    subtitle_15="Don't let her drink it.",
    subtitle_16="She was coughing.\nI don't wanna spend money on meds.",
    subtitle_17="I wasn't coughing. I just had a fever.",
    subtitle_18="It's all right to have a sip.",
    subtitle_19="Not coughing? You are being cheeky!",
    subtitle_20="I say no Coke.",
    difficulty=1,
    verified=True,
)  # test_case_block_50
# noinspection PyArgumentList
test_case_block_51 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="Fai, I'm not gonna eat. I'm running late.",
    subtitle_2="You're going now?",
    subtitle_3="Yes.",
    verified=True,
)  # test_case_block_51
# noinspection PyArgumentList
test_case_block_52 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Be a good girl.",
    verified=True,
)  # test_case_block_52
# noinspection PyArgumentList
test_case_block_53 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="Bro Coke, dig in.",
    subtitle_2="She's not eating with us?",
    subtitle_3="She has to work night shift.",
    verified=True,
)  # test_case_block_53
# noinspection PyArgumentList
test_case_block_54 = EnglishProofTestCase.get_test_case_cls(6)(
    subtitle_1="She's a legit masseuse.",
    subtitle_2="Eat some barbecued pork.",
    subtitle_3="Bo, eat some veggies.",
    subtitle_4="You seldom eat veggies.",
    subtitle_5="Shall we go to Ocean Park?",
    subtitle_6="Shall we ride the roller coaster?",
    verified=True,
)  # test_case_block_54
# noinspection PyArgumentList
test_case_block_55 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="Shall we fly higher and farther?",
    subtitle_2="Tickle, tickle.",
    verified=True,
)  # test_case_block_55
# noinspection PyArgumentList
test_case_block_56 = EnglishProofTestCase.get_test_case_cls(38)(
    subtitle_1="Stop making noise, or the landlady will be nasty.",
    subtitle_2="She's nasty because you haven't paid the rent.",
    subtitle_3="You're being cheeky. Come down.",
    subtitle_4="What a dragon lady, arguing with your father!",
    subtitle_5="This girl plays too much! Wear your slippers.",
    subtitle_6="Have you finished your homework? Homework first.",
    subtitle_7="Quick!",
    subtitle_8="- I'll spank you.\n- Good girl.",
    subtitle_9="This naughty girl!",
    subtitle_10="I've quit smoking.",
    subtitle_11="Quit?",
    subtitle_12="I've quit smoking.",
    subtitle_13='"Whoring, gambling, drinking, roaming...',
    subtitle_14='and smoking are the hobbies of a king."',
    subtitle_15="Your mantra.",
    subtitle_16="I'm on dialysis. I have to quit.",
    subtitle_17="Told you you're impotent.",
    subtitle_18="You feel dizzy when you squat.",
    subtitle_19="Fuck!",
    subtitle_20="What have you been up to?",
    subtitle_21="What can I do?",
    subtitle_22="I used to do temporary construction work.",
    subtitle_23="Now I'm a full-time babysitter.",
    subtitle_24="What about you?",
    subtitle_25="Me?",
    subtitle_26="I sell this in China.",
    subtitle_27="People won't use beepers anymore.",
    subtitle_28="Every Chinese will own\na mobile phone in the future.",
    subtitle_29="One sells for RMB¥1K, 10 for RMB¥10K.",
    subtitle_30="I'll be fatter than Chow Yun-fat.",
    subtitle_31="Fat with loads of money?",
    subtitle_32="Great.",
    subtitle_33="You're doing great. You're becoming a boss.",
    subtitle_34="Going straight is better than going astray.",
    subtitle_35="We're not fierce enough to be Kings of Thieves.",
    subtitle_36="All we did were some petty crimes.",
    subtitle_37="Our life was insecure. We couldn't sleep well.",
    subtitle_38="And we didn't earn that much.\nSo what's the point?",
    revised_29="One sells for ¥1,000, ten for ¥10,000.",
    note_29="Changed 'RMB¥1K' to '¥1,000' and '10 for RMB¥10K' to 'ten "
    "for ¥10,000' for clarity and standard formatting.",
    difficulty=1,
    verified=True,
)  # test_case_block_56
# noinspection PyArgumentList
test_case_block_57 = EnglishProofTestCase.get_test_case_cls(9)(
    subtitle_1="I'd like to stay here for a few days.",
    subtitle_2="What?",
    subtitle_3="I can sleep on the couch.",
    subtitle_4="What's that for?",
    subtitle_5="Take it. It will lessen your wife's burden.",
    subtitle_6="Dad, I can't find my school manual!",
    subtitle_7="Dad, Dad.",
    subtitle_8="Coming!",
    subtitle_9="That's fine",
    revised_9="That's fine.",
    note_9="Added a period at the end for sentence completion.",
    difficulty=1,
    verified=True,
)  # test_case_block_57
# noinspection PyArgumentList
test_case_block_58 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="(Gold shop)",
    verified=True,
)  # test_case_block_58
# noinspection PyArgumentList
test_case_block_59 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="(Jockey Club)",
    subtitle_2="Panyu Yi Fa Market",
    subtitle_3="30 sets of 29-inch TVs. RMB¥12K apiece.",
    subtitle_4="Plus 80 VCD players. RMB¥4K a piece.",
    subtitle_5="RMB¥680K, thank you.",
    revised_3="30 sets of 29-inch TVs. ¥12,000 apiece.",
    note_3="Changed 'RMB¥12K' to '¥12,000' for clarity and standard formatting.",
    revised_4="Plus 80 VCD players. ¥4,000 apiece.",
    note_4="Changed 'RMB¥4K a piece.' to '¥4,000 apiece.' for clarity "
    "and correct word usage.",
    revised_5="¥680,000, thank you.",
    note_5="Changed 'RMB¥680K' to '¥680,000' for clarity and standard formatting.",
    difficulty=1,
    verified=True,
)  # test_case_block_59
# noinspection PyArgumentList
test_case_block_60 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="You pay me RMB¥700K.",
    subtitle_2="I will notify you once the goods are delivered.",
    subtitle_3="Next.",
    subtitle_4="RMB¥30K for Chief Chen. Please count it.",
    subtitle_5="Business License",
    revised_1="You pay me ¥700,000.",
    note_1="Changed 'RMB¥700K' to '¥700,000' for clarity and standard formatting.",
    revised_4="¥30,000 for Chief Chen. Please count it.",
    note_4="Changed 'RMB¥30K' to '¥30,000' for clarity and standard formatting.",
    difficulty=1,
    verified=True,
)  # test_case_block_60
# noinspection PyArgumentList
test_case_block_61 = EnglishProofTestCase.get_test_case_cls(23)(
    subtitle_1="RMB¥30K. The amount is correct.",
    subtitle_2="Will notify you once the goods are onboard.",
    subtitle_3="Please extend my thanks to Chief Chen.",
    subtitle_4="My VCD player is broken.",
    subtitle_5="I'll give you a new one. Kam.",
    subtitle_6="Yes.",
    subtitle_7="The latest 33-inch TV set.",
    subtitle_8="Good stuff.",
    subtitle_9="I'll give it to you, too.",
    subtitle_10="Thanks so much, Boss Zhang.",
    subtitle_11="You're welcome.",
    subtitle_12="Gui, Guang, a 33-inch TV set and a VCD player.",
    subtitle_13="Gui, Guang, a 33-inch TV set and a VCD player.",
    subtitle_14="Sure.",
    subtitle_15="Da-bao Electronics",
    subtitle_16="She is greedy.",
    subtitle_17="That's business.",
    subtitle_18="Don't pull a long face all day long.",
    subtitle_19="Boss Zhang, Boss Zhang.",
    subtitle_20="No worries. They will take care of it.",
    subtitle_21="- Quick\n- What's wrong?",
    subtitle_22="Boss Zhang.",
    subtitle_23="What's wrong?",
    revised_1="¥30,000. The amount is correct.",
    note_1="Changed 'RMB¥30K' to '¥30,000' for clarity and standard formatting.",
    revised_2="Will notify you once the goods are on board.",
    note_2="Changed 'onboard' to 'on board' for correct usage.",
    revised_21="- Quick.\n- What's wrong?",
    note_21="Added period after 'Quick' for punctuation consistency.",
    difficulty=1,
    verified=True,
)  # test_case_block_61
# noinspection PyArgumentList
test_case_block_62 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="Something wrong with the goods?",
    subtitle_2="No, close the door.",
    subtitle_3="Close the door.",
    verified=True,
)  # test_case_block_62
# noinspection PyArgumentList
test_case_block_63 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Want to play tough guy? Call your wife now.",
    verified=True,
)  # test_case_block_63
# noinspection PyArgumentList
test_case_block_64 = EnglishProofTestCase.get_test_case_cls(4)(
    subtitle_1="Call your wife now.",
    subtitle_2="Tell your folks you're OK, asshole.",
    subtitle_3="If you kill me, you won't get a cent.",
    subtitle_4="Are you threatening me?",
    verified=True,
)  # test_case_block_64
# noinspection PyArgumentList
test_case_block_65 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="Cheuk, be patient.",
    subtitle_2="If he doesn't talk, don't give him food or water.",
    verified=True,
)  # test_case_block_65
# noinspection PyArgumentList
test_case_block_66 = EnglishProofTestCase.get_test_case_cls(48)(
    subtitle_1="You're so noisy.",
    subtitle_2="Hey, what are you doing?",
    subtitle_3="Get him back! Get him back!",
    subtitle_4="This is the gold shop.",
    subtitle_5="Usually there's a police wagon at the entrance.",
    subtitle_6="Jockey Club is across the street.",
    subtitle_7="We keep a close eye on the police wagon.",
    subtitle_8="As soon as it leaves at 8pm,\nwe rob the gold shop right away.",
    subtitle_9="It's the racing night. It will be crowded.\nAfter it's done...",
    subtitle_10="- There's not much money in this.\n- Follow me closely.",
    subtitle_11="What did you just say?",
    subtitle_12="You've committed big crimes.",
    subtitle_13="Why pick this small gold shop?",
    subtitle_14="Yes,",
    subtitle_15="I've heard the 3 Kings\nof Thieves would join forces.",
    subtitle_16="At least millions of dollars will be involved.",
    subtitle_17="What 3 Kings of Thieves?",
    subtitle_18="Say it!",
    subtitle_19="Bro Foon, are you making a comeback?",
    subtitle_20="This time with Cheuk Tze-keung\nand Kwai Ching-hung.",
    subtitle_21="The 3 Kings of Thieves are collaborating?",
    subtitle_22="Someone has seen you three meeting in China.",
    subtitle_23="Where did you hear this?",
    subtitle_24="Everyone is saying that.",
    subtitle_25="And you believe it?",
    subtitle_26="Didn't Big Bro say you couldn't\nmake money by toting guns?",
    subtitle_27="If I'm Kwai,",
    subtitle_28="I don't have\nto eat lunch boxes with you.",
    subtitle_29="Idiots.",
    subtitle_30="That's ridiculous!",
    subtitle_31="Yip is all noise and fury.",
    subtitle_32="Kwai is hush and shush.",
    subtitle_33="We are so different. How can it work?",
    subtitle_34="Smuggle more goods with me.",
    subtitle_35="Let's make more money together!",
    subtitle_36="Got it.",
    subtitle_37="Brilliant!",
    subtitle_38="Sometimes I feel like toting my gun again.",
    subtitle_39="Robbery! Robbery!",
    subtitle_40="That's so cool!",
    subtitle_41="You call that cool?",
    subtitle_42="Big Bro wielding AK-47 is cool!",
    subtitle_43="Not like this.",
    subtitle_44="AK-47 recoil is powerful.",
    subtitle_45="Don't hold it.",
    subtitle_46="Press it.",
    subtitle_47="Stand firm.",
    subtitle_48="Shoot the hell out of him.",
    revised_8="As soon as it leaves at 8 PM,\nwe rob the gold shop right away.",
    note_8="Changed '8pm' to '8 PM' for standard formatting.",
    revised_15="I've heard the Three Kings\nof Thieves would join forces.",
    note_15="Changed '3 Kings' to 'Three Kings' for consistency and formality.",
    revised_17="What Three Kings of Thieves?",
    note_17="Changed '3 Kings' to 'Three Kings' for consistency and formality.",
    revised_21="The Three Kings of Thieves are collaborating?",
    note_21="Changed '3 Kings' to 'Three Kings' for consistency and formality.",
    revised_38="Sometimes I feel like toting a gun again.",
    note_38="Changed 'my gun' to 'a gun' for more natural phrasing.",
    difficulty=1,
    verified=True,
)  # test_case_block_66
# noinspection PyArgumentList
test_case_block_67 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="What the fuck?! Join me",
    subtitle_2="or go home and eat shit.",
    verified=True,
)  # test_case_block_67
# noinspection PyArgumentList
test_case_block_68 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="Big Bro Chiu,",
    subtitle_2="how much can we earn from robbing this gold shop?",
    verified=True,
)  # test_case_block_68
# noinspection PyArgumentList
test_case_block_69 = EnglishProofTestCase.get_test_case_cls(6)(
    subtitle_1="You're calling or not?",
    subtitle_2="If the 3 Kings of Thieves join forces,",
    subtitle_3="even if we open a fish ball stall together,",
    subtitle_4="we will create a stir, right?",
    subtitle_5="What shall I call our stall?",
    subtitle_6="Are you calling your family or not?",
    revised_1="Are you calling or not?",
    note_1="Changed 'You're calling or not?' to 'Are you calling or "
    "not?' for correct question structure.",
    revised_2="If the Three Kings of Thieves join forces,",
    note_2="Changed '3 Kings' to 'Three Kings' for consistency and formality.",
    revised_3="even if we open a fishball stall together,",
    note_3="Changed 'fish ball' to 'fishball' for consistency with common usage.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_69
# noinspection PyArgumentList
test_case_block_70 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="Hey, wake up!",
    subtitle_2="Gold depository?",
    subtitle_3="Racecourse?",
    verified=True,
)  # test_case_block_70
# noinspection PyArgumentList
test_case_block_71 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="Kidnap Hong Kong Governor Chris Patten?",
    subtitle_2="The Head of Hong Kong and Macau Affairs, Lu Ping?",
    subtitle_3="No way.",
    verified=True,
)  # test_case_block_71
# noinspection PyArgumentList
test_case_block_72 = EnglishProofTestCase.get_test_case_cls(8)(
    subtitle_1="What are you listening?",
    subtitle_2="The 4 Heavenly Kings singing on stage together.",
    subtitle_3="What are they singing?",
    subtitle_4="I can't hear a thing. What's so good about it?",
    subtitle_5="When the 4 Heavenly Kings sing together,",
    subtitle_6="it's terrific no matter what they sing.",
    subtitle_7="Water, give me water.",
    subtitle_8="I will make the call.",
    revised_1="What are you listening to?",
    note_1="Added 'to' at the end for correct phrasing.",
    revised_2="The Four Heavenly Kings singing on stage together.",
    note_2="Spelled out '4' as 'Four' and capitalized for proper noun usage.",
    revised_5="When the Four Heavenly Kings sing together,",
    note_5="Spelled out '4' as 'Four' and capitalized for proper noun usage.",
    difficulty=1,
    verified=True,
)  # test_case_block_72
# noinspection PyArgumentList
test_case_block_73 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="How's my husband? I beg you!",
    subtitle_2="He's not in good health. Don't hurt him.",
    subtitle_3="We are not as loaded as it may seem.",
    subtitle_4="Mr Cheuk, can you let my husband go?",
    subtitle_5="Name a price. I'll pay you from my own pocket...",
    verified=True,
)  # test_case_block_73
# noinspection PyArgumentList
test_case_block_74 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="Hello?",
    subtitle_2="I have $80M in cash.",
    subtitle_3="Is it OK?",
    subtitle_4="$80M it is!",
    subtitle_5="Find Yip and Kwai!",
    revised_2="I have $80 million in cash.",
    note_2="Changed '$80M' to '$80 million' for clarity and consistency.",
    revised_4="$80 million it is!",
    note_4="Changed '$80M' to '$80 million' for clarity and consistency.",
    difficulty=1,
    verified=True,
)  # test_case_block_74
# noinspection PyArgumentList
test_case_block_75 = EnglishProofTestCase.get_test_case_cls(9)(
    subtitle_1="What the hell?",
    subtitle_2="The 3 Kings of Thieves\njoin forces for the first time.",
    subtitle_3="It will be terrific no matter what we do!",
    subtitle_4="You don't even have a plan yet,",
    subtitle_5="and you want 2 wanted men around you?",
    subtitle_6="You know I will",
    subtitle_7="come up with a plan!",
    subtitle_8="This is the mountain I'm looking for.",
    subtitle_9="Himalaya!",
    revised_2="The Three Kings of Thieves\njoin forces for the first time.",
    note_2="Spelled out '3' as 'Three' for consistency and formality.",
    revised_5="and you want two wanted men around you?",
    note_5="Spelled out '2' as 'two' for consistency and formality.",
    difficulty=1,
    verified=True,
)  # test_case_block_75
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
