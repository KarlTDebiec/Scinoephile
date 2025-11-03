#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""MLAMD English proof test cases."""

from __future__ import annotations

from scinoephile.core.english.proofing.abcs import EnglishProofTestCase

# noinspection PyArgumentList
test_case_block_0 = EnglishProofTestCase.get_test_case_cls(33)(
    subtitle_1="When Mrs. McBing was in labour..",
    subtitle_2="A pan appeared in the sky.",
    subtitle_3="It fitted along Garden Street..",
    subtitle_4="Turned left, and stopped\nat the Beef ball King.",
    subtitle_5="Correction:",
    subtitle_6="It first arrived at the Market Building.",
    subtitle_7="Lingered a bit...Correction:",
    subtitle_8="It flied over the railway, turned right...",
    subtitle_9="And headed directly for the Bazaar.",
    subtitle_10="It flied on..",
    subtitle_11="At last coming into the maternity ward",
    subtitle_12="There, on the right hand side of\nMrs. McBing.",
    subtitle_13="Correction: Left hand side.",
    subtitle_14="The pan stayed.",
    subtitle_15="Mrs. McBing,\nconvinced that this was a miracle,",
    subtitle_16="Made a I wish.",
    subtitle_17="Thinking of her soon-to-be-born son.",
    subtitle_18="Please make him\na clever and smart boy!",
    subtitle_19="The pan didn't seem to hear her words.",
    subtitle_20="So Mrs. McBing amended her wish:",
    subtitle_21="Orr make him a smart businessman?",
    subtitle_22="Or maybe..",
    subtitle_23="Or make him really handsome.",
    subtitle_24="AS handsome as Chow Yun Fat or\nTony Leung!",
    subtitle_25="The pan didn't respond.",
    subtitle_26="Mrs. McBing, in panic..",
    subtitle_27="Made a final amendment:",
    subtitle_28="Her boy needed not to be\nsmart or handsome",
    subtitle_29="AS long as luck be with him!",
    subtitle_30="It's nice to depend - on oneself.",
    subtitle_31="But luck is essential still.",
    subtitle_32="Of course Chow and Leung are\nlucky guys...",
    subtitle_33="But then they are smart too!",
    revised_1="When Mrs. McBing was in labour...",
    note_1="Changed '..' to '...'.",
    revised_2="a pan appeared in the sky.",
    note_2="Changed capital 'A' to lowercase 'a' to continue sentence "
    "from previous subtitle.",
    revised_3="It flew along Garden Street...",
    note_3="Changed 'fitted' to 'flew'; changed '..' to '...'.",
    revised_4="turned left, and stopped\nat the Beefball King.",
    note_4="Changed 'Turned' to 'turned' to continue sentence from "
    "previous subtitle; changed 'Beef ball' to 'Beefball'.",
    revised_6="It first arrived at the Market Building...",
    note_6="Added ellipsis.",
    revised_7="lingered a bit... Correction:",
    note_7="Changed 'Lingered' to 'lingered'; added space after ellipsis.",
    revised_8="it flew over the railway, turned right...",
    note_8="Changed 'It' to 'it' to continue sentence from previous "
    "subtitle; changed 'flied' to 'flew'; changed '..' to '...'.",
    revised_9="and headed directly for the Bazaar.",
    note_9="Changed 'And' to 'and' to continue sentence from previous subtitle.",
    revised_10="It flew on...",
    note_10="Changed 'flied' to 'flew'; changed '..' to '...'.",
    revised_11="at last coming into the maternity ward.",
    note_11="Changed 'At' to 'at' to continue sentence from previous "
    "subtitle; added period at end.",
    revised_16="made a wish...",
    note_16="Changed 'Made' to 'made'; removed extra 'I'; changed '.' to '...'.",
    revised_17="thinking of her soon-to-be-born son.",
    note_17="Changed 'Thinking' to 'thinking' to continue sentence from "
    "previous subtitle.",
    revised_21="Or make him a smart businessman?",
    note_21="Changed 'Orr' to 'Or'.",
    revised_22="Or maybe...",
    note_22="Changed '..' to '...'.",
    revised_23="or make him really handsome.",
    note_23="Changed 'Or' to 'or' to continue sentence from previous subtitle.",
    revised_24="As handsome as Chow Yun Fat or\nTony Leung!",
    note_24="Changed 'AS' to 'As'.",
    revised_26="Mrs. McBing, in panic...",
    note_26="Changed '..' to '...'.",
    revised_27="made a final amendment:",
    note_27="Changed 'Made' to 'made' to continue sentence from previous subtitle.",
    revised_28="Her boy need not be\nsmart or handsome",
    note_28="Changed 'needed not to be' to 'need not be'.",
    revised_29="As long as luck be with him!",
    note_29="Changed 'AS' to 'As'.",
    revised_30="It's nice to depend on oneself...",
    note_30="Removed '-'; changed '.' to '...'.",
    revised_31="but luck is essential still.",
    note_31="Changed 'But' to 'but' to continue sentence from previous subtitle.",
    revised_33="but then they are smart too!",
    note_33="Changed 'But' to 'but' to continue sentence from previous subtitle.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_0
# noinspection PyArgumentList
test_case_block_1 = EnglishProofTestCase.get_test_case_cls(13)(
    subtitle_1="Finally, the pan dropped to the floor..",
    subtitle_2="Mrs. McBing,\nbelieving her wish granted..",
    subtitle_3="Thought that was magnificent!",
    subtitle_4="But what had the pan granted her?",
    subtitle_5="A smart boy?A A lucky boy?",
    subtitle_6="Ora Chow look-alike?",
    subtitle_7="To commemorate this, Mrs. McBing",
    subtitle_8="Decided to name her son McNificient.",
    subtitle_9="No! It's better to be humble!",
    subtitle_10="III name him McDull!",
    subtitle_11="Dear all.",
    subtitle_12="I am the boy, no more McNificient..",
    subtitle_13="I'm McDull!",
    revised_1="Finally, the pan dropped to the floor...",
    note_1="Changed '..' to '...'.",
    revised_2="Mrs. McBing,\nbelieving her wish granted...",
    note_2="Changed '..' to '...'.",
    revised_3="thought that was magnificent!",
    note_3="Changed 'Thought' to 'thought' to continue sentence from "
    "previous subtitle.",
    revised_5="A smart boy? A lucky boy?",
    note_5="Removed extra 'A'.",
    revised_6="Or a Chow look-alike?",
    note_6="Changed 'Ora' to 'Or a'.",
    revised_8="decided to name her son McNificient.",
    note_8="Changed 'Decided' to 'decided' to continue sentence from "
    "previous subtitle.",
    revised_10="I'll name him McDull!",
    note_10="Changed 'III' to 'I'll'.",
    revised_11="Dear all...",
    note_11="Changed '.' to '...'.",
    revised_12="I am the boy, no more McNificient...",
    note_12="Changed '..' to '...'.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_1
# noinspection PyArgumentList
test_case_block_2 = EnglishProofTestCase.get_test_case_cls(17)(
    subtitle_1="'My School\"",
    subtitle_2="Oh dear,",
    subtitle_3="Your calves have grown strong",
    subtitle_4="I've been desperately..",
    subtitle_5="looking for a school!",
    subtitle_6="Why not try the one.",
    subtitle_7="At the Emporium?",
    subtitle_8="The Spring Flower Kindergarten?",
    subtitle_9="Yeah! The one at the junction..",
    subtitle_10="Right next to Silver City Food Mall",
    subtitle_11="The Spring Flower Kindergarten!",
    subtitle_12="Only 10 minutes walk from\nthe MTR Station!",
    subtitle_13="Spring Flower Kindergarten,\ngood environment.",
    subtitle_14="With white teachers for English class!",
    subtitle_15="White teachers for English class?",
    subtitle_16="Yeah!",
    subtitle_17="Spring Flower offer white teachers!",
    revised_1='"My School"',
    note_1="Changed single to double quotes for title.",
    revised_3="your calves have grown strong.",
    note_3="Changed 'Your' to 'your' to continue sentence from previous "
    "subtitle; added period at end.",
    revised_4="I've been desperately...",
    note_4="Changed '..' to '...'.",
    revised_6="Why not try the one...",
    note_6="Changed '.' to '...'.",
    revised_9="Yeah! The one at the junction...",
    note_9="Changed '..' to '...'.",
    revised_10="Right next to Silver City Food Mall.",
    note_10="Added period at end.",
    revised_12="Only 10 minutes' walk from\nthe MTR station!",
    note_12="Added possessive apostrophe to 'minutes'' and changed "
    "'Station' to lowercase for consistency.",
    revised_13="Spring Flower Kindergarten,\ngood environment...",
    note_13="Changed '.' to '...'.",
    revised_17="Spring Flower offers white teachers!",
    note_17="Changed 'offer' to 'offers' for subject-verb agreement.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_2
# noinspection PyArgumentList
test_case_block_3 = EnglishProofTestCase.get_test_case_cls(23)(
    subtitle_1="'\"We are all happy children...' 1",
    subtitle_2='\'"We sing everyday!"',
    subtitle_3='"We learn as we grow...',
    subtitle_4='\'"We are the flowers of spring!"',
    subtitle_5="This piggy kid in a rabbit outfit..",
    subtitle_6="Who doesn't look the least\nlike Chow or Leung.",
    subtitle_7="That's me, McDull",
    subtitle_8="This is my kindergarten.",
    subtitle_9="The headmaster came from\nthe countryside...",
    subtitle_10="AS a result, he speaks with an accent.",
    subtitle_11="For many years",
    subtitle_12="I had difficulty hearing him.",
    subtitle_13="Tart! Tart!",
    subtitle_14="- Duck dumpling! Duck dumpling!",
    subtitle_15="The 97 Rule The 97 Rule..",
    subtitle_16="Shall be replaced by the 98 Rule!",
    subtitle_17="Shall be replaced by the 98 Rule!",
    subtitle_18="Good, children!",
    subtitle_19="We are sharing an important issue..",
    subtitle_20="This morning:",
    subtitle_21="Children, have you handed in\nthe school fee?",
    subtitle_22="Yes!",
    subtitle_23="Great! Now move to class.",
    revised_1='"We are all happy children..."',
    note_1="Changed single to double quotes; removed extraneous '1' at end.",
    revised_2='"We sing every day!"',
    note_2="Changed 'everyday' to 'every day' (adverb form). Changed "
    "single to double quotes.",
    revised_3='"We learn as we grow..."',
    note_3="Added closing quote for consistency.",
    revised_4='"We are the flowers of spring!"',
    note_4="Changed single to double quotes.",
    revised_5="This piggy kid in a rabbit outfit...",
    note_5="Changed '..' to '...'.",
    revised_6="Who doesn't look the least\nlike Chow or Leung...",
    note_6="Added ellipsis at end.",
    revised_7="That's me, McDull.",
    note_7="Added period at end.",
    revised_10="As a result, he speaks with an accent.",
    note_10="Changed 'AS' to 'As'.",
    revised_11="For many years...",
    note_11="Added ellipsis.",
    revised_12="I had difficulty understanding him.",
    note_12="Changed 'hearing' to 'understanding' for clarity.",
    revised_13="- Tart!    - Tart!",
    note_13="Added extra spaces for clarity in dialogue.",
    revised_14="- Duck dumpling!    - Duck dumpling!",
    note_14="Added extra spaces for clarity in dialogue.",
    revised_15="- The 97 Rule...    - The 97 Rule...",
    note_15="Added dashes and ellipses for clarity in dialogue.",
    revised_16="shall be replaced by the 98 Rule!",
    note_16="Changed 'Shall' to lowercase 'shall' to continue sentence "
    "from previous subtitle.",
    revised_17="shall be replaced by the 98 Rule!",
    note_17="Changed 'Shall' to lowercase 'shall' to continue sentence "
    "from previous subtitle.",
    revised_19="We are sharing an important issue...",
    note_19="Changed '..' to '...'.",
    revised_20="this morning:",
    note_20="Changed 'This' to lowercase 'this' to continue sentence from "
    "previous subtitle.",
    revised_23="Great! Now move on to class.",
    note_23="Changed 'move to class' to 'move on to class' for natural phrasing.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_3
# noinspection PyArgumentList
test_case_block_4 = EnglishProofTestCase.get_test_case_cls(55)(
    subtitle_1="You might conclude that\nthis is a shabby school.",
    subtitle_2="But, for me and my mates..",
    subtitle_3="This is the most beautiful paradise!",
    subtitle_4="...Also, there is Miss Chan.",
    subtitle_5="Who adores US in\nher absent-minded way.",
    subtitle_6="Also, she is a Faye Wong wannabe.",
    subtitle_7="Actually, Kelly Chan will do!",
    subtitle_8="Roll call now.",
    subtitle_9="McMug! - Present!",
    subtitle_10="- Fai! Present!",
    subtitle_11="Goosie! Present!",
    subtitle_12="- Darby! Present!",
    subtitle_13="May! Present!",
    subtitle_14="June! Present!",
    subtitle_15="May! Present!",
    subtitle_16="- McMug! - Present!",
    subtitle_17="May!",
    subtitle_18="Miss Chan, I've been called twice!",
    subtitle_19="Oops!",
    subtitle_20="Good morning, sir!",
    subtitle_21="Good day, sir!",
    subtitle_22="Back to roll call.",
    subtitle_23="- Fai! Present!",
    subtitle_24="- Fai! Present!",
    subtitle_25="- Darby! Present!",
    subtitle_26="May! Present!",
    subtitle_27="- McMug! - Present!",
    subtitle_28="Goosie! Present!",
    subtitle_29="Goosie! Present!",
    subtitle_30="Have I missed anyone?",
    subtitle_31="McDull!",
    subtitle_32="McDull!",
    subtitle_33="McDull!",
    subtitle_34="McDull!",
    subtitle_35="Hey, I don't understand.",
    subtitle_36="1 keep feeling that.",
    subtitle_37="Someone is calling me.",
    subtitle_38="Don't think that I've been daydreaming.",
    subtitle_39="Was contemplating something academic:",
    subtitle_40="How does this universe work?",
    subtitle_41="I mean, I ate 6 oranges that morning.",
    subtitle_42="And my stomach wouldn't stop.",
    subtitle_43="Then I ate 3 bananas this morning.",
    subtitle_44="Again my stomach wouldn't stop.",
    subtitle_45="It just wouldn't stop!",
    subtitle_46="How are these two things related?",
    subtitle_47="There are SO many things that\nI don't understand.",
    subtitle_48="But I am not afraid.",
    subtitle_49="One day, when I finish kindergarten..",
    subtitle_50="I shall move up...",
    subtitle_51="And get my degree",
    subtitle_52="When I graduate from university, I know...",
    subtitle_53="I shall understand everything!",
    subtitle_54="And then",
    subtitle_55="I will buy my mother a house!",
    revised_2="But for me and my mates...",
    note_2="Removed comma after 'But' and changed '..' to '...'.",
    revised_4="...also, there is Miss Chan.",
    note_4="Changed 'Also' to lowercase to continue sentence from previous subtitle.",
    revised_5="who adores us in\nher absent-minded way.",
    note_5="Changed 'Who' to lowercase and 'US' to 'us' to continue "
    "sentence from previous subtitle and for consistency.",
    revised_9="McMug!    - Present!",
    note_9="Added extra spaces for clarity in dialogue formatting.",
    revised_10="- Fai!    - Present!",
    note_10="Added extra spaces for clarity in dialogue formatting.",
    revised_12="- Darby!    - Present!",
    note_12="Added extra spaces for clarity in dialogue formatting.",
    revised_16="- McMug!    - Present!",
    note_16="Added extra spaces for clarity in dialogue formatting.",
    revised_23="- Fai!    - Present!",
    note_23="Added extra spaces for clarity in dialogue formatting.",
    revised_24="- Fai!    - Present!",
    note_24="Added extra spaces for clarity in dialogue formatting.",
    revised_25="- Darby!    - Present!",
    note_25="Added extra spaces for clarity in dialogue formatting.",
    revised_27="- McMug!    - Present!",
    note_27="Added extra spaces for clarity in dialogue formatting.",
    revised_36="I keep feeling that...",
    note_36="Changed '1' to 'I' and added ellipsis for continuity.",
    revised_47="There are so many things that\nI don't understand.",
    note_47="Changed 'SO' to lowercase 'so'.",
    revised_49="One day, when I finish kindergarten...",
    note_49="Changed '..' to '...'.",
    revised_51="and get my degree.",
    note_51="Changed 'And' to lowercase 'and' to continue sentence from "
    "previous subtitle and added period.",
    difficulty=1,
)  # test_case_block_4
# noinspection PyArgumentList
test_case_block_5 = None  # test_case_block_5
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

mlamd_english_proof_test_cases: list[EnglishProofTestCase] = [
    test_case
    for name, test_case in globals().items()
    if name.startswith("test_case_block_") and test_case is not None
]
"""MLAMD English proof test cases."""

__all__ = [
    "mlamd_english_proof_test_cases",
]
