#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for KOB."""

from __future__ import annotations

from scinoephile.audio.cantonese.review.abcs import ReviewTestCase
from scinoephile.core.english.proofing.abcs import EnglishProofTestCase

# noinspection PyArgumentList
proof_test_case_block_0 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Young master, we are ready",
    revised_1="",
    note_1="",
    prompt=True,
    verified=True,
)  # proof_test_case_block_0
# noinspection PyArgumentList
proof_test_case_block_1 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="What's a hard job for you,\nyoung master",
    subtitle_2="The towel, young master",
    revised_1="",
    note_1="",
    revised_2="",
    note_2="",
    verified=True,
)  # proof_test_case_block_1
# noinspection PyArgumentList
proof_test_case_block_2 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="What did he write?",
    subtitle_2="His name!",
    subtitle_3="Great! Young master know how to\nwrite his name!",
    subtitle_4="Yes!",
    subtitle_5="Damn!",
    revised_1="",
    note_1="",
    revised_2="",
    note_2="",
    revised_3="Great! Young master knows how to\nwrite his name!",
    note_3="Corrected 'know' to 'knows'.",
    revised_4="",
    note_4="",
    revised_5="",
    note_5="",
    difficulty=1,
    prompt=True,
    verified=True,
)  # proof_test_case_block_2
# noinspection PyArgumentList
proof_test_case_block_3 = EnglishProofTestCase.get_test_case_cls(40)(
    subtitle_1="Nice calligraphy",
    subtitle_2="Get lost",
    subtitle_3="Nice calligraphy!\nSo Cha Ha Yee Chan!",
    subtitle_4="It's reversed, Master",
    subtitle_5="Chan Yee Ha Cha So",
    subtitle_6="Good boy, but, don't be proud!\nGot me?",
    subtitle_7="Dad, since the first\nemperor of the Ching Dynasty,",
    subtitle_8="our family",
    subtitle_9="has been illiterate",
    subtitle_10="But not, my son,\nthat's your grandson,",
    subtitle_11="he knows how to write his name!",
    subtitle_12="Dad, it's very great!",
    subtitle_13="He knows writing now,",
    subtitle_14="he will be scholar one day",
    subtitle_15="Now, he knows how to write his name,",
    subtitle_16="he will have a son later",
    subtitle_17="Young master,\nyou should try hard to learn",
    subtitle_18="Chan, I think,\nwe should mount it",
    subtitle_19="OK",
    subtitle_20="Professor, show it in\nsome obvious places",
    subtitle_21="By the way, one minute,",
    subtitle_22="why don't you carry it with traditional\ndecoration in the street?",
    subtitle_23="What?",
    subtitle_24="Let's go!",
    subtitle_25="Chan, come and sit...",
    subtitle_26="I am so pleased that you are that hard\nworking and filial",
    subtitle_27="Listen to me, I am notorious of being\na spendthrift",
    subtitle_28="My fortune is almost used up",
    subtitle_29="If I die one day,",
    subtitle_30="you should depend on yourself",
    subtitle_31="I used to depend on myself",
    subtitle_32="The cheques worths 100,000 taels!\nDon't be an extravagant spender",
    subtitle_33="Give me the imported hat",
    subtitle_34="Where are you going?\nChan!",
    subtitle_35="I am having a grand\nbirthday party tonight",
    subtitle_36="How old are you?",
    subtitle_37="25 years old. Come earlier",
    subtitle_38="But you should dress up first",
    subtitle_39="You are like beggar!",
    subtitle_40="How can a beggar be that rich?!\nI do want to be a rich beggar!",
    revised_1="",
    note_1="",
    revised_2="",
    note_2="",
    revised_3="",
    note_3="",
    revised_4="",
    note_4="",
    revised_5="",
    note_5="",
    revised_6="",
    note_6="",
    revised_7="",
    note_7="",
    revised_8="",
    note_8="",
    revised_9="",
    note_9="",
    revised_10="",
    note_10="",
    revised_11="",
    note_11="",
    revised_12="",
    note_12="",
    revised_13="",
    note_13="",
    revised_14="he will be a scholar one day",
    note_14="Added 'a' before 'scholar'.",
    revised_15="",
    note_15="",
    revised_16="",
    note_16="",
    revised_17="",
    note_17="",
    revised_18="",
    note_18="",
    revised_19="",
    note_19="",
    revised_20="",
    note_20="",
    revised_21="",
    note_21="",
    revised_22="",
    note_22="",
    revised_23="",
    note_23="",
    revised_24="",
    note_24="",
    revised_25="",
    note_25="",
    revised_26="I am so pleased that you are that\nhard-working and filial",
    note_26="Added a hyphen in 'hard-working'.",
    revised_27="Listen to me, I am notorious for being\na spendthrift",
    note_27="Corrected 'of being' to 'for being'.",
    revised_28="",
    note_28="",
    revised_29="",
    note_29="",
    revised_30="",
    note_30="",
    revised_31="",
    note_31="",
    revised_32="The cheque is worth 100,000 taels!\nDon't be an extravagant spender",
    note_32="Corrected 'cheques worths' to 'cheque is worth'.",
    revised_33="",
    note_33="",
    revised_34="",
    note_34="",
    revised_35="",
    note_35="",
    revised_36="",
    note_36="",
    revised_37="",
    note_37="",
    revised_38="",
    note_38="",
    revised_39="You are like a beggar!",
    note_39="Added 'a' before 'beggar'.",
    revised_40="",
    note_40="",
    difficulty=1,
    prompt=True,
    verified=True,
)  # proof_test_case_block_3
# noinspection PyArgumentList
proof_test_case_block_4 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="That fat-headed...",
    subtitle_2="Come over here",
    subtitle_3="What's the matter?",
    subtitle_4="The invitation card\nof my son is great!",
    subtitle_5="If I hold a birthday party in future,\n"
    "I want a better invitation card!",
    revised_1="",
    note_1="",
    revised_2="",
    note_2="",
    revised_3="",
    note_3="",
    revised_4="",
    note_4="",
    revised_5="If I hold a birthday party in the future,\n"
    "I want a better invitation card!",
    note_5="Added 'the' before 'future'.",
    difficulty=1,
    verified=True,
)  # proof_test_case_block_4
# noinspection PyArgumentList
proof_test_case_block_5 = EnglishProofTestCase.get_test_case_cls(38)(
    subtitle_1="Your Majesty, how do you think about\nthe Cantonese Opera?",
    subtitle_2="For sure, it can't compete\nwith Peking Opera!",
    subtitle_3="But, I am appreciated\nto view this",
    subtitle_4="Money...",
    subtitle_5="Tips. Tips...",
    subtitle_6="Happy birthday to you, Mr So",
    subtitle_7="I am homeless and sick...",
    subtitle_8="I am poor, I am damn poor!",
    subtitle_9="Please give me some money",
    subtitle_10="Kidding? Damn you beggar!",
    subtitle_11="How can you beg here?",
    subtitle_12="Go to hell!",
    subtitle_13="Give him tips",
    subtitle_14="Yes, young master",
    subtitle_15="Are you kidding?\nHow can you give him tips?",
    subtitle_16="A beggar is a man too",
    subtitle_17="Everyone can come here\nif he has money",
    subtitle_18="Your living,",
    subtitle_19="including the expenditure for hooking,\nI will pay for you!",
    subtitle_20="You pay it?",
    subtitle_21="So what?",
    subtitle_22="Nothing!",
    subtitle_23="Please follow me",
    subtitle_24="Come into my room...",
    subtitle_25="Mr So!",
    subtitle_26="Hello...",
    subtitle_27="How are you, Madam Pimp?",
    subtitle_28="It's very bad of\nyou to call me that!",
    subtitle_29="Just be frank, why not?",
    subtitle_30="You should be frank!",
    subtitle_31="Your hat, is like\nthe mourning uniform!",
    subtitle_32="Is your dad passed away?",
    subtitle_33="I feel happy to talk in this way",
    subtitle_34="Mr Chiu, you helped me to terminate\nthe Hairy Gang,",
    subtitle_35="the emperor will\ngive you award for this",
    subtitle_36="I'll appreciate it if you",
    subtitle_37="speak something nice in front of\nthe emperor",
    subtitle_38="Please have the towel",
    revised_1="",
    note_1="",
    revised_2="",
    note_2="",
    revised_3="But, I appreciate\nto view this",
    note_3="Corrected 'am appreciated' to 'appreciate'.",
    revised_4="",
    note_4="",
    revised_5="",
    note_5="",
    revised_6="",
    note_6="",
    revised_7="",
    note_7="",
    revised_8="",
    note_8="",
    revised_9="",
    note_9="",
    revised_10="",
    note_10="",
    revised_11="",
    note_11="",
    revised_12="",
    note_12="",
    revised_13="",
    note_13="",
    revised_14="",
    note_14="",
    revised_15="",
    note_15="",
    revised_16="",
    note_16="",
    revised_17="",
    note_17="",
    revised_18="",
    note_18="",
    revised_19="",
    note_19="",
    revised_20="",
    note_20="",
    revised_21="",
    note_21="",
    revised_22="",
    note_22="",
    revised_23="",
    note_23="",
    revised_24="",
    note_24="",
    revised_25="",
    note_25="",
    revised_26="",
    note_26="",
    revised_27="",
    note_27="",
    revised_28="",
    note_28="",
    revised_29="",
    note_29="",
    revised_30="",
    note_30="",
    revised_31="",
    note_31="",
    revised_32="Has your dad passed away?",
    note_32="Corrected 'Is your dad passed away?' to 'Has your dad passed away?'.",
    revised_33="",
    note_33="",
    revised_34="",
    note_34="",
    revised_35="",
    note_35="",
    revised_36="",
    note_36="",
    revised_37="",
    note_37="",
    revised_38="",
    note_38="",
    difficulty=1,
    prompt=True,
    verified=True,
)  # proof_test_case_block_5
# noinspection PyArgumentList
proof_test_case_block_6 = EnglishProofTestCase.get_test_case_cls(15)(
    subtitle_1="Mr So has come",
    subtitle_2="Congratulation!",
    subtitle_3="This way...",
    subtitle_4="Mr So, today is your big day,\nyou must be very happy!",
    subtitle_5="We have some new girls,\nyou must be satisfied with it",
    subtitle_6="What are they?\nGold fish, or cooked fish?",
    subtitle_7="What does that mean?",
    subtitle_8="You idiot! Gold fish is\nfor watching only",
    subtitle_9="Cooked fish can be eaten",
    subtitle_10="Cooked fish of course",
    subtitle_11="You, cooked fishes, why don't you\ncome and serve Mr So?",
    subtitle_12="Mr So, you are the\nsuperior master today",
    subtitle_13="What kind of woman do you want?\nJust tell me",
    subtitle_14="I won't mind,\nevery women is just the same",
    subtitle_15="Nothing special",
    revised_1="",
    note_1="",
    revised_2="Congratulations!",
    note_2="Corrected 'Congratulation' to 'Congratulations'.",
    revised_3="",
    note_3="",
    revised_4="",
    note_4="",
    revised_5="We have some new girls,\nyou must be satisfied with them",
    note_5="Corrected 'it' to 'them' to agree with 'girls'.",
    revised_6="",
    note_6="",
    revised_7="",
    note_7="",
    revised_8="",
    note_8="",
    revised_9="",
    note_9="",
    revised_10="",
    note_10="",
    revised_11="",
    note_11="",
    revised_12="",
    note_12="",
    revised_13="",
    note_13="",
    revised_14="I won't mind,\nevery woman is just the same",
    note_14="Corrected 'women' to 'woman'.",
    revised_15="",
    note_15="",
    verified=True,
)  # proof_test_case_block_6
# noinspection PyArgumentList
proof_test_case_block_7 = EnglishProofTestCase.get_test_case_cls(17)(
    subtitle_1="Mr So, what's the matter?",
    subtitle_2="I am attacked",
    subtitle_3="What? Who dared so?",
    subtitle_4="I will hit that\nbastard's mouth for you",
    subtitle_5="She didn't use her mouth",
    subtitle_6="She used her eyes",
    subtitle_7="Tempting, and I smell blood\nI haven't seen such eyesight before",
    subtitle_8="Who is she?",
    subtitle_9="Miss Yushang comes to be part time\nhooker only",
    subtitle_10="Is Mr Chiu interested to sleep with her?",
    subtitle_11="You should ask His Majesty first",
    subtitle_12="How is it? Your Majesty?",
    subtitle_13="We are friends,\njust go ahead if you want!",
    subtitle_14="Mr Chiu, help yourself",
    subtitle_15="Thank you then",
    subtitle_16="The room service please",
    subtitle_17="Yushang, come and greet Mr Chiu",
    revised_1="",
    note_1="",
    revised_2="",
    note_2="",
    revised_3="",
    note_3="",
    revised_4="",
    note_4="",
    revised_5="",
    note_5="",
    revised_6="",
    note_6="",
    revised_7="Tempting, and I smell blood.\nI haven't seen such eyesight before.",
    note_7="Added period after 'blood' to separate sentences correctly.",
    revised_8="",
    note_8="",
    revised_9="Miss Yushang comes to be a part-time\nhooker only",
    note_9="Added 'a' before 'part-time' and included a hyphen in "
    "'part-time' for grammatical accuracy.",
    revised_10="",
    note_10="",
    revised_11="",
    note_11="",
    revised_12="",
    note_12="",
    revised_13="",
    note_13="",
    revised_14="",
    note_14="",
    revised_15="",
    note_15="",
    revised_16="",
    note_16="",
    revised_17="",
    note_17="",
    verified=True,
)  # proof_test_case_block_7
# noinspection PyArgumentList
proof_test_case_block_8 = EnglishProofTestCase.get_test_case_cls(7)(
    subtitle_1="Sister, he is the one we want",
    subtitle_2="He killed dad",
    subtitle_3="I know, stay calm",
    subtitle_4="Let's go",
    subtitle_5="May I be excused",
    subtitle_6="Mr Chiu, Miss Yushang has arrived",
    subtitle_7="How are you? Mr Chiu",
    revised_1="",
    note_1="",
    revised_2="",
    note_2="",
    revised_3="",
    note_3="",
    revised_4="",
    note_4="",
    revised_5="May I be excused?",
    note_5="Added a question mark to indicate a request for permission.",
    revised_6="",
    note_6="",
    revised_7="How are you, Mr Chiu?",
    note_7="Added a comma for direct address and a question mark for the question.",
    verified=True,
)  # proof_test_case_block_8
# noinspection PyArgumentList
proof_test_case_block_9 = EnglishProofTestCase.get_test_case_cls(16)(
    subtitle_1="A pretty woman!",
    subtitle_2="Mr Chiu, about tonight...",
    subtitle_3="$100,000",
    subtitle_4="if Miss Yushang sleeps with our\nyoung master tonight...",
    subtitle_5="You are not welcomed",
    subtitle_6="I am sorry, I am damn sorry",
    subtitle_7="Don't you have any objection?",
    subtitle_8="Let me say something fair",
    subtitle_9="If any of you can offer",
    subtitle_10="more than $100,000",
    subtitle_11="Yushang will sleep with whom",
    subtitle_12="Don't quarrel because of such\nsmall amount,",
    subtitle_13="isn't it right?",
    subtitle_14="Pal, you are a big spender",
    subtitle_15="The cheque is too simple to me",
    subtitle_16="I have a pearl which is granted by the\n"
    "Royal family, it's invaluable!",
    revised_1="",
    note_1="",
    revised_2="",
    note_2="",
    revised_3="",
    note_3="",
    revised_4="",
    note_4="",
    revised_5="You are not welcome",
    note_5="Changed 'welcomed' to 'welcome'.",
    revised_6="",
    note_6="",
    revised_7="",
    note_7="",
    revised_8="",
    note_8="",
    revised_9="",
    note_9="",
    revised_10="",
    note_10="",
    revised_11="Yushang will sleep with whomever",
    note_11="Changed 'whom' to 'whomever' for proper grammatical "
    "structure in this context.",
    revised_12="",
    note_12="",
    revised_13="",
    note_13="",
    revised_14="",
    note_14="",
    revised_15="",
    note_15="",
    revised_16="",
    note_16="",
    verified=True,
)  # proof_test_case_block_9
# noinspection PyArgumentList
proof_test_case_block_10 = EnglishProofTestCase.get_test_case_cls(6)(
    subtitle_1="I love the pearl more",
    subtitle_2="Mr Chiu, I will wait\nyou in my room",
    subtitle_3="Does the pearl worth $100,000?",
    subtitle_4="Don't you think that's\ntoo little for you?",
    subtitle_5="I love money too",
    subtitle_6="But, I don't like you",
    revised_1="",
    note_1="",
    revised_2="Mr Chiu, I will wait for\nyou in my room",
    note_2="Added 'for' to complete the phrase 'wait for'.",
    revised_3="Is the pearl worth $100,000?",
    note_3="Corrected 'Does the pearl worth' to 'Is the pearl worth'.",
    revised_4="",
    note_4="",
    revised_5="",
    note_5="",
    revised_6="",
    note_6="",
    verified=True,
)  # proof_test_case_block_10
# noinspection PyArgumentList
proof_test_case_block_11 = EnglishProofTestCase.get_test_case_cls(11)(
    subtitle_1="You are frank!\nI love it very much",
    subtitle_2="Mr So...",
    subtitle_3="It doesn't matter,",
    subtitle_4="I think, my hat doesn't match me",
    subtitle_5="Yushang doesn't like me,\nI deserve it",
    subtitle_6="I am glad you understand this",
    subtitle_7="Don't worry,",
    subtitle_8="I have many pretty girls here",
    subtitle_9="I trust your arrangement",
    subtitle_10="None of my business",
    subtitle_11="How bold are you?",
    revised_1="You are frank!\nI love it!",
    note_1="Removed 'very much' since the expression 'I love it!' is "
    "typically used with enthusiasm and doesn't require 'very "
    "much'.",
    revised_2="",
    note_2="",
    revised_3="",
    note_3="",
    revised_4="",
    note_4="",
    revised_5="",
    note_5="",
    revised_6="",
    note_6="",
    revised_7="",
    note_7="",
    revised_8="",
    note_8="",
    revised_9="",
    note_9="",
    revised_10="",
    note_10="",
    revised_11="",
    note_11="",
)  # proof_test_case_block_11
# noinspection PyArgumentList
proof_test_case_block_12 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="Mantis Fist?\nIt seems to be powerful",
    subtitle_2="Music!",
    revised_1="",
    note_1="",
    revised_2="",
    note_2="",
)  # proof_test_case_block_12
# noinspection PyArgumentList
proof_test_case_block_13 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="Keep this",
    subtitle_2="See my Crane's Fists!",
    subtitle_3="The Tiger's Claws!",
    revised_1="",
    note_1="",
    revised_2="Watch my Crane Fists!",
    note_2="Replaced 'See my Crane's Fists!' with 'Watch my Crane "
    "Fists!' for clarity and style consistency.",
    revised_3="The Tiger Claws!",
    note_3="Changed 'The Tiger's Claws!' to 'The Tiger Claws!' to match "
    "parallel structure with 'Crane Fists'.",
)  # proof_test_case_block_13
# noinspection PyArgumentList
proof_test_case_block_14 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="How can a mantis fight with a tiger?",
    subtitle_2="I know Tiger Claws\nand Crane's Fists too!",
    subtitle_3="Well, try me mantis!",
    revised_1="",
    note_1="",
    revised_2="",
    note_2="",
    revised_3="Well, try me, mantis!",
    note_3="Added a comma after 'try me' for clarity.",
)  # proof_test_case_block_14
# noinspection PyArgumentList
proof_test_case_block_15 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="Bravo...",
    subtitle_2="Your Tiger's claws are defeated",
    subtitle_3="Actually it's not Tiger's Claws,",
    subtitle_4="it's beggar's fists!",
    subtitle_5="That's why it's too weak",
    revised_1="",
    note_1="",
    revised_2="",
    note_2="",
    revised_3="Actually, it's not Tiger's Claws,",
    note_3="Added a comma after 'Actually' for proper punctuation.",
    revised_4="it's a beggar's fists!",
    note_4="Added 'a' before 'beggar's fists'.",
    revised_5="",
    note_5="",
)  # proof_test_case_block_15
# noinspection PyArgumentList
proof_test_case_block_16 = None  # proof_test_case_block_16
# noinspection PyArgumentList
proof_test_case_block_17 = None  # proof_test_case_block_17
# noinspection PyArgumentList
proof_test_case_block_18 = None  # proof_test_case_block_18
# noinspection PyArgumentList
proof_test_case_block_19 = None  # proof_test_case_block_19
# noinspection PyArgumentList
proof_test_case_block_20 = None  # proof_test_case_block_20
# noinspection PyArgumentList
proof_test_case_block_21 = None  # proof_test_case_block_21
# noinspection PyArgumentList
proof_test_case_block_22 = None  # proof_test_case_block_22
# noinspection PyArgumentList
proof_test_case_block_23 = None  # proof_test_case_block_23
# noinspection PyArgumentList
proof_test_case_block_24 = None  # proof_test_case_block_24
# noinspection PyArgumentList
proof_test_case_block_25 = None  # proof_test_case_block_25
# noinspection PyArgumentList
proof_test_case_block_26 = None  # proof_test_case_block_26
# noinspection PyArgumentList
proof_test_case_block_27 = None  # proof_test_case_block_27
# noinspection PyArgumentList
proof_test_case_block_28 = None  # proof_test_case_block_28
# noinspection PyArgumentList
proof_test_case_block_29 = None  # proof_test_case_block_29
# noinspection PyArgumentList
proof_test_case_block_30 = None  # proof_test_case_block_30
# noinspection PyArgumentList
proof_test_case_block_31 = None  # proof_test_case_block_31
# noinspection PyArgumentList
proof_test_case_block_32 = None  # proof_test_case_block_32
# noinspection PyArgumentList
proof_test_case_block_33 = None  # proof_test_case_block_33
# noinspection PyArgumentList
proof_test_case_block_34 = None  # proof_test_case_block_34
# noinspection PyArgumentList
proof_test_case_block_35 = None  # proof_test_case_block_35
# noinspection PyArgumentList
proof_test_case_block_36 = None  # proof_test_case_block_36
# noinspection PyArgumentList
proof_test_case_block_37 = None  # proof_test_case_block_37
# noinspection PyArgumentList
proof_test_case_block_38 = None  # proof_test_case_block_38
# noinspection PyArgumentList
proof_test_case_block_39 = None  # proof_test_case_block_39
# noinspection PyArgumentList
proof_test_case_block_40 = None  # proof_test_case_block_40
# noinspection PyArgumentList
proof_test_case_block_41 = None  # proof_test_case_block_41
# noinspection PyArgumentList
proof_test_case_block_42 = None  # proof_test_case_block_42
# noinspection PyArgumentList
proof_test_case_block_43 = None  # proof_test_case_block_43
# noinspection PyArgumentList
proof_test_case_block_44 = None  # proof_test_case_block_44
# noinspection PyArgumentList
proof_test_case_block_45 = None  # proof_test_case_block_45
# noinspection PyArgumentList
proof_test_case_block_46 = None  # proof_test_case_block_46
# noinspection PyArgumentList
proof_test_case_block_47 = None  # proof_test_case_block_47
# noinspection PyArgumentList
proof_test_case_block_48 = None  # proof_test_case_block_48
# noinspection PyArgumentList
proof_test_case_block_49 = None  # proof_test_case_block_49
# noinspection PyArgumentList
proof_test_case_block_50 = None  # proof_test_case_block_50
# noinspection PyArgumentList
proof_test_case_block_51 = None  # proof_test_case_block_51
# noinspection PyArgumentList
proof_test_case_block_52 = None  # proof_test_case_block_52
# noinspection PyArgumentList
proof_test_case_block_53 = None  # proof_test_case_block_53
# noinspection PyArgumentList
proof_test_case_block_54 = None  # proof_test_case_block_54
# noinspection PyArgumentList
proof_test_case_block_55 = None  # proof_test_case_block_55
# noinspection PyArgumentList
proof_test_case_block_56 = None  # proof_test_case_block_56
# noinspection PyArgumentList
proof_test_case_block_57 = None  # proof_test_case_block_57
# noinspection PyArgumentList
proof_test_case_block_58 = None  # proof_test_case_block_58
# noinspection PyArgumentList
proof_test_case_block_59 = None  # proof_test_case_block_59
# noinspection PyArgumentList
proof_test_case_block_60 = None  # proof_test_case_block_60
# noinspection PyArgumentList
proof_test_case_block_61 = None  # proof_test_case_block_61
# noinspection PyArgumentList
proof_test_case_block_62 = None  # proof_test_case_block_62
# noinspection PyArgumentList
proof_test_case_block_63 = None  # proof_test_case_block_63
# noinspection PyArgumentList
proof_test_case_block_64 = None  # proof_test_case_block_64
# noinspection PyArgumentList
proof_test_case_block_65 = None  # proof_test_case_block_65
# noinspection PyArgumentList
proof_test_case_block_66 = None  # proof_test_case_block_66
# noinspection PyArgumentList
proof_test_case_block_67 = None  # proof_test_case_block_67
# noinspection PyArgumentList
proof_test_case_block_68 = None  # proof_test_case_block_68
# noinspection PyArgumentList
proof_test_case_block_69 = None  # proof_test_case_block_69
# noinspection PyArgumentList
proof_test_case_block_70 = None  # proof_test_case_block_70
# noinspection PyArgumentList
proof_test_case_block_71 = None  # proof_test_case_block_71
# noinspection PyArgumentList
proof_test_case_block_72 = None  # proof_test_case_block_72
# noinspection PyArgumentList
proof_test_case_block_73 = None  # proof_test_case_block_73
# noinspection PyArgumentList
proof_test_case_block_74 = None  # proof_test_case_block_74
# noinspection PyArgumentList
proof_test_case_block_75 = None  # proof_test_case_block_75
# noinspection PyArgumentList
proof_test_case_block_76 = None  # proof_test_case_block_76
# noinspection PyArgumentList
proof_test_case_block_77 = None  # proof_test_case_block_77
# noinspection PyArgumentList
proof_test_case_block_78 = None  # proof_test_case_block_78
# noinspection PyArgumentList
proof_test_case_block_79 = None  # proof_test_case_block_79
# noinspection PyArgumentList
proof_test_case_block_80 = None  # proof_test_case_block_80
# noinspection PyArgumentList
proof_test_case_block_81 = None  # proof_test_case_block_81
# noinspection PyArgumentList
proof_test_case_block_82 = None  # proof_test_case_block_82
# noinspection PyArgumentList
proof_test_case_block_83 = None  # proof_test_case_block_83
# noinspection PyArgumentList
proof_test_case_block_84 = None  # proof_test_case_block_84
# noinspection PyArgumentList
proof_test_case_block_85 = None  # proof_test_case_block_85
# noinspection PyArgumentList
proof_test_case_block_86 = None  # proof_test_case_block_86
# noinspection PyArgumentList
proof_test_case_block_87 = None  # proof_test_case_block_87
# noinspection PyArgumentList
proof_test_case_block_88 = None  # proof_test_case_block_88
# noinspection PyArgumentList
proof_test_case_block_89 = None  # proof_test_case_block_89
# noinspection PyArgumentList
proof_test_case_block_90 = None  # proof_test_case_block_90
# noinspection PyArgumentList
proof_test_case_block_91 = None  # proof_test_case_block_91
# noinspection PyArgumentList
proof_test_case_block_92 = None  # proof_test_case_block_92
# noinspection PyArgumentList
proof_test_case_block_93 = None  # proof_test_case_block_93
# noinspection PyArgumentList
proof_test_case_block_94 = None  # proof_test_case_block_94
# noinspection PyArgumentList
proof_test_case_block_95 = None  # proof_test_case_block_95
# noinspection PyArgumentList
proof_test_case_block_96 = None  # proof_test_case_block_96
# noinspection PyArgumentList
proof_test_case_block_97 = None  # proof_test_case_block_97
# noinspection PyArgumentList
proof_test_case_block_98 = None  # proof_test_case_block_98
# noinspection PyArgumentList
proof_test_case_block_99 = None  # proof_test_case_block_99
# noinspection PyArgumentList
proof_test_case_block_100 = None  # proof_test_case_block_100
# noinspection PyArgumentList
proof_test_case_block_101 = None  # proof_test_case_block_101
# noinspection PyArgumentList
proof_test_case_block_102 = None  # proof_test_case_block_102
# noinspection PyArgumentList
proof_test_case_block_103 = None  # proof_test_case_block_103
# noinspection PyArgumentList
proof_test_case_block_104 = None  # proof_test_case_block_104
# noinspection PyArgumentList
proof_test_case_block_105 = None  # proof_test_case_block_105
# noinspection PyArgumentList
proof_test_case_block_106 = None  # proof_test_case_block_106
# noinspection PyArgumentList
proof_test_case_block_107 = None  # proof_test_case_block_107
# noinspection PyArgumentList
proof_test_case_block_108 = None  # proof_test_case_block_108
# noinspection PyArgumentList
proof_test_case_block_109 = None  # proof_test_case_block_109
# noinspection PyArgumentList
proof_test_case_block_110 = None  # proof_test_case_block_110
# noinspection PyArgumentList
proof_test_case_block_111 = None  # proof_test_case_block_111
# noinspection PyArgumentList
proof_test_case_block_112 = None  # proof_test_case_block_112
# noinspection PyArgumentList
proof_test_case_block_113 = None  # proof_test_case_block_113
# noinspection PyArgumentList
proof_test_case_block_114 = None  # proof_test_case_block_114
# noinspection PyArgumentList
proof_test_case_block_115 = None  # proof_test_case_block_115
# noinspection PyArgumentList
proof_test_case_block_116 = None  # proof_test_case_block_116
# noinspection PyArgumentList
proof_test_case_block_117 = None  # proof_test_case_block_117
# noinspection PyArgumentList
proof_test_case_block_118 = None  # proof_test_case_block_118
# noinspection PyArgumentList
proof_test_case_block_119 = None  # proof_test_case_block_119
# noinspection PyArgumentList
proof_test_case_block_120 = None  # proof_test_case_block_120
# noinspection PyArgumentList
proof_test_case_block_121 = None  # proof_test_case_block_121
# noinspection PyArgumentList
proof_test_case_block_122 = None  # proof_test_case_block_122
# noinspection PyArgumentList
proof_test_case_block_123 = None  # proof_test_case_block_123
# noinspection PyArgumentList
proof_test_case_block_124 = None  # proof_test_case_block_124
# noinspection PyArgumentList
proof_test_case_block_125 = None  # proof_test_case_block_125
# noinspection PyArgumentList
proof_test_case_block_126 = None  # proof_test_case_block_126
# noinspection PyArgumentList
proof_test_case_block_127 = None  # proof_test_case_block_127
# noinspection PyArgumentList
proof_test_case_block_128 = None  # proof_test_case_block_128
# noinspection PyArgumentList
proof_test_case_block_129 = None  # proof_test_case_block_129
# noinspection PyArgumentList
proof_test_case_block_130 = None  # proof_test_case_block_130
# noinspection PyArgumentList
proof_test_case_block_131 = None  # proof_test_case_block_131
# noinspection PyArgumentList
proof_test_case_block_132 = None  # proof_test_case_block_132
# noinspection PyArgumentList
proof_test_case_block_133 = None  # proof_test_case_block_133
# noinspection PyArgumentList
proof_test_case_block_134 = None  # proof_test_case_block_134
# noinspection PyArgumentList
proof_test_case_block_135 = None  # proof_test_case_block_135
# noinspection PyArgumentList
proof_test_case_block_136 = None  # proof_test_case_block_136
# noinspection PyArgumentList
proof_test_case_block_137 = None  # proof_test_case_block_137
# noinspection PyArgumentList
proof_test_case_block_138 = None  # proof_test_case_block_138
# noinspection PyArgumentList
proof_test_case_block_139 = None  # proof_test_case_block_139
# noinspection PyArgumentList
proof_test_case_block_140 = None  # proof_test_case_block_140
# noinspection PyArgumentList
proof_test_case_block_141 = None  # proof_test_case_block_141
# noinspection PyArgumentList
proof_test_case_block_142 = None  # proof_test_case_block_142
# noinspection PyArgumentList
proof_test_case_block_143 = None  # proof_test_case_block_143
# noinspection PyArgumentList
proof_test_case_block_144 = None  # proof_test_case_block_144
# noinspection PyArgumentList
proof_test_case_block_145 = None  # proof_test_case_block_145
# noinspection PyArgumentList
proof_test_case_block_146 = None  # proof_test_case_block_146
# noinspection PyArgumentList
proof_test_case_block_147 = None  # proof_test_case_block_147
# noinspection PyArgumentList
proof_test_case_block_148 = None  # proof_test_case_block_148
# noinspection PyArgumentList
proof_test_case_block_149 = None  # proof_test_case_block_149
# noinspection PyArgumentList
proof_test_case_block_150 = None  # proof_test_case_block_150
# noinspection PyArgumentList
proof_test_case_block_151 = None  # proof_test_case_block_151
# noinspection PyArgumentList
proof_test_case_block_152 = None  # proof_test_case_block_152
# noinspection PyArgumentList
proof_test_case_block_153 = None  # proof_test_case_block_153
# noinspection PyArgumentList
proof_test_case_block_154 = None  # proof_test_case_block_154
# noinspection PyArgumentList
proof_test_case_block_155 = None  # proof_test_case_block_155
# noinspection PyArgumentList
proof_test_case_block_156 = None  # proof_test_case_block_156
# noinspection PyArgumentList
proof_test_case_block_157 = None  # proof_test_case_block_157
# noinspection PyArgumentList
proof_test_case_block_158 = None  # proof_test_case_block_158
# noinspection PyArgumentList
proof_test_case_block_159 = None  # proof_test_case_block_159
# noinspection PyArgumentList
proof_test_case_block_160 = None  # proof_test_case_block_160
# noinspection PyArgumentList
proof_test_case_block_161 = None  # proof_test_case_block_161
# noinspection PyArgumentList
proof_test_case_block_162 = None  # proof_test_case_block_162
# noinspection PyArgumentList
proof_test_case_block_163 = None  # proof_test_case_block_163
# noinspection PyArgumentList
proof_test_case_block_164 = None  # proof_test_case_block_164
# noinspection PyArgumentList
proof_test_case_block_165 = None  # proof_test_case_block_165
# noinspection PyArgumentList
proof_test_case_block_166 = None  # proof_test_case_block_166
# noinspection PyArgumentList
proof_test_case_block_167 = None  # proof_test_case_block_167
# noinspection PyArgumentList
proof_test_case_block_168 = None  # proof_test_case_block_168
# noinspection PyArgumentList
proof_test_case_block_169 = None  # proof_test_case_block_169
# noinspection PyArgumentList
proof_test_case_block_170 = None  # proof_test_case_block_170
# noinspection PyArgumentList
proof_test_case_block_171 = None  # proof_test_case_block_171
# noinspection PyArgumentList
proof_test_case_block_172 = None  # proof_test_case_block_172
# noinspection PyArgumentList
proof_test_case_block_173 = None  # proof_test_case_block_173
# noinspection PyArgumentList
proof_test_case_block_174 = None  # proof_test_case_block_174
# noinspection PyArgumentList
proof_test_case_block_175 = None  # proof_test_case_block_175
# noinspection PyArgumentList
proof_test_case_block_176 = None  # proof_test_case_block_176
# noinspection PyArgumentList
proof_test_case_block_177 = None  # proof_test_case_block_177
# noinspection PyArgumentList
proof_test_case_block_178 = None  # proof_test_case_block_178
# noinspection PyArgumentList
proof_test_case_block_179 = None  # proof_test_case_block_179
# noinspection PyArgumentList
proof_test_case_block_180 = None  # proof_test_case_block_180
# noinspection PyArgumentList
proof_test_case_block_181 = None  # proof_test_case_block_181
# noinspection PyArgumentList
proof_test_case_block_182 = None  # proof_test_case_block_182
# noinspection PyArgumentList
proof_test_case_block_183 = None  # proof_test_case_block_183
# noinspection PyArgumentList
proof_test_case_block_184 = None  # proof_test_case_block_184
# noinspection PyArgumentList
proof_test_case_block_185 = None  # proof_test_case_block_185
# noinspection PyArgumentList
proof_test_case_block_186 = None  # proof_test_case_block_186
# noinspection PyArgumentList
proof_test_case_block_187 = None  # proof_test_case_block_187
# noinspection PyArgumentList
proof_test_case_block_188 = None  # proof_test_case_block_188
# noinspection PyArgumentList
proof_test_case_block_189 = None  # proof_test_case_block_189
# noinspection PyArgumentList
proof_test_case_block_190 = None  # proof_test_case_block_190
# noinspection PyArgumentList
proof_test_case_block_191 = None  # proof_test_case_block_191
# noinspection PyArgumentList
proof_test_case_block_192 = None  # proof_test_case_block_192
# noinspection PyArgumentList
proof_test_case_block_193 = None  # proof_test_case_block_193
# noinspection PyArgumentList
proof_test_case_block_194 = None  # proof_test_case_block_194
# noinspection PyArgumentList
proof_test_case_block_195 = None  # proof_test_case_block_195

kob_proof_test_cases: list[ReviewTestCase] = [
    test_case
    for name, test_case in globals().items()
    if name.startswith("proof_test_case_block_") and test_case is not None
]
"""KOB proof test cases."""

__all__ = [
    "kob_proof_test_cases",
]
