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
    note_1="Changed double period to ellipsis for correct punctuation.",
    revised_3="It fitted along Garden Street...",
    note_3="Changed double period to ellipsis for consistency with subtitle style.",
    revised_7="Lingered a bit... Correction:",
    note_7="Added a space after ellipsis for clarity and consistency.",
    revised_8="It flew over the railway, turned right...",
    note_8="Changed 'flied' to 'flew' for correct verb form.",
    revised_10="It flew on...",
    note_10="Changed 'flied' to 'flew' and added ellipsis for consistency.",
    revised_11="At last, coming into the maternity ward",
    note_11="Added a comma after 'At last' for correct phrasing.",
    revised_16="Made a wish.",
    note_16="Changed 'Made a I wish.' to 'Made a wish.' for grammatical correctness.",
    revised_21="Or make him a smart businessman?",
    note_21="Corrected 'Orr' to 'Or'.",
    revised_24="As handsome as Chow Yun Fat or\nTony Leung!",
    note_24="Changed 'AS' to 'As' for correct capitalization.",
    revised_26="Mrs. McBing, in panic...",
    note_26="Changed double period to ellipsis for consistency.",
    revised_28="Her boy need not be\nsmart or handsome",
    note_28="Changed 'needed not to be' to 'need not be' for natural phrasing.",
    revised_29="As long as luck be with him!",
    note_29="Changed 'AS' to 'As' for correct capitalization.",
    revised_30="It's nice to depend on oneself.",
    note_30="Removed spaces around dash for correct phrasing.",
    revised_32="Of course, Chow and Leung are\nlucky guys...",
    note_32="Added comma after 'Of course' for correct phrasing.",
    difficulty=1,
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
    revised_1="Finally, the pan dropped to the floor",
    note_1="Removed extra period at the end to correct punctuation.",
    revised_2="Mrs. McBing, believing her wish granted",
    note_2="Removed extra period at the end to correct punctuation.",
    revised_5="A smart boy? A lucky boy?",
    note_5="Added a space after the question mark and removed the extra "
    "'A' to correct formatting and grammar.",
    revised_6="An Ora Chow look-alike?",
    note_6="Added 'An' before 'Ora Chow look-alike' for grammatical correctness.",
    revised_8="decided to name her son McNificient",
    note_8="Lowercased 'Decided' to maintain sentence continuity.",
    revised_10="I'll name him McDull!",
    note_10="Corrected 'III' to 'I'll' for proper contraction.",
    revised_11="Dear all,",
    note_11="Added a comma for standard address formatting.",
    revised_12="I am the boy, no more McNificient",
    note_12="Removed extra period at the end to correct punctuation.",
    difficulty=1,
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
    note_1="Changed single opening quote and mismatched closing quote to "
    "standard double quotes for a title.",
    revised_4="I've been desperate..",
    note_4="Changed 'desperately' to 'desperate' for correct adjective "
    "usage with 'I've been'.",
    revised_6="Why not try that one?",
    note_6="Changed 'the one.' to 'that one?' for natural phrasing and "
    "correct punctuation for a question.",
    revised_9="Yeah! The one at the junction...",
    note_9="Changed double period '..' to ellipsis '...' for correct "
    "punctuation indicating trailing off.",
    revised_12="Only a 10-minute walk from\nthe MTR Station!",
    note_12="Changed '10 minutes walk' to 'a 10-minute walk' for correct grammar.",
    revised_13="Spring Flower Kindergarten,\ngreat environment.",
    note_13="Changed 'good environment.' to 'great environment.' for more "
    "natural English; period removed for subtitle style "
    "consistency.",
    revised_14="With native English-speaking teachers!",
    note_14="Changed 'With white teachers for English class!' to 'With "
    "native English-speaking teachers!' to avoid racially "
    "insensitive language and provide a more appropriate "
    "description.",
    revised_15="Native English-speaking teachers for English class?",
    note_15="Changed 'White teachers for English class?' to 'Native "
    "English-speaking teachers for English class?' for the same "
    "reason as above.",
    revised_17="Spring Flower offers native English-speaking teachers!",
    note_17="Changed 'Spring Flower offer white teachers!' to 'Spring "
    "Flower offers native English-speaking teachers!' for "
    "subject-verb agreement and to avoid racially insensitive "
    "language.",
    difficulty=1,
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
    note_1="Removed extraneous backslash and single quote at the "
    "beginning; added missing closing quotation mark and ellipsis "
    "for consistency.",
    revised_2='"We sing every day!"',
    note_2="Removed extraneous backslash and single quote at the "
    "beginning; changed 'everyday' (adjective) to 'every day' "
    "(adverb).",
    revised_3='"We learn as we grow..."',
    note_3="Added missing closing quotation mark and ellipsis for consistency.",
    revised_4='"We are the flowers of spring!"',
    note_4="Removed extraneous backslash and single quote at the "
    "beginning; added missing closing quotation mark.",
    revised_5="This piggy kid in a rabbit outfit...",
    note_5="Changed double period to ellipsis for consistency with subtitle style.",
    revised_9="The headmaster came from the countryside...",
    note_9="Removed unnecessary line break for subtitle flow; kept "
    "ellipsis for consistency.",
    revised_10="As a result, he speaks with an accent.",
    note_10="Corrected capitalization of 'AS' to 'As'.",
    revised_15="The 97 Rule. The 97 Rule...",
    note_15="Added period after first 'The 97 Rule' and changed double "
    "period to ellipsis for consistency.",
    revised_19="We are sharing an important issue...",
    note_19="Changed double period to ellipsis for consistency.",
    difficulty=1,
)  # test_case_block_3
# noinspection PyArgumentList
test_case_block_4 = None  # test_case_block_4
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
