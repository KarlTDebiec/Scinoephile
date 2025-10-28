#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for KOB."""

from __future__ import annotations

from scinoephile.audio.cantonese.review.abcs import ReviewTestCase
from scinoephile.core.english.proofing.abcs import EnglishProofTestCase

# noinspection PyArgumentList
proof_test_case_block_0 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Young master, we are ready",
    prompt=True,
    verified=True,
)  # proof_test_case_block_0
# noinspection PyArgumentList
proof_test_case_block_1 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="What's a hard job for you,\nyoung master",
    subtitle_2="The towel, young master",
    verified=True,
)  # proof_test_case_block_1
# noinspection PyArgumentList
proof_test_case_block_2 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="What did he write?",
    subtitle_2="His name!",
    subtitle_3="Great! Young master know how to\nwrite his name!",
    subtitle_4="Yes!",
    subtitle_5="Damn!",
    revised_3="Great! Young master knows how to\nwrite his name!",
    note_3="Corrected 'know' to 'knows'.",
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
    revised_14="he will be a scholar one day",
    note_14="Added 'a' before 'scholar'.",
    revised_26="I am so pleased that you are that\nhard-working and filial",
    note_26="Added a hyphen in 'hard-working'.",
    revised_27="Listen to me, I am notorious for being\na spendthrift",
    note_27="Corrected 'of being' to 'for being'.",
    revised_32="The cheque is worth 100,000 taels!\nDon't be an extravagant spender",
    note_32="Corrected 'cheques worths' to 'cheque is worth'.",
    revised_39="You are like a beggar!",
    note_39="Added 'a' before 'beggar'.",
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
    revised_3="But, I appreciate\nto view this",
    note_3="Corrected 'am appreciated' to 'appreciate'.",
    revised_32="Has your dad passed away?",
    note_32="Corrected 'Is your dad passed away?' to 'Has your dad passed away?'.",
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
    revised_2="Congratulations!",
    note_2="Corrected 'Congratulation' to 'Congratulations'.",
    revised_5="We have some new girls,\nyou must be satisfied with them",
    note_5="Corrected 'it' to 'them' to agree with 'girls'.",
    revised_14="I won't mind,\nevery woman is just the same",
    note_14="Corrected 'women' to 'woman'.",
    difficulty=1,
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
    revised_7="Tempting, and I smell blood.\nI haven't seen such eyesight before.",
    note_7="Added period after 'blood' to separate sentences correctly.",
    revised_9="Miss Yushang comes to be a part-time\nhooker only",
    note_9="Added 'a' before 'part-time' and included a hyphen in "
    "'part-time' for grammatical accuracy.",
    difficulty=1,
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
    revised_5="May I be excused?",
    note_5="Added a question mark to indicate a request for permission.",
    revised_7="How are you, Mr Chiu?",
    note_7="Added a comma for direct address and a question mark for the question.",
    difficulty=1,
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
    revised_5="You are not welcome",
    note_5="Changed 'welcomed' to 'welcome'.",
    revised_11="Yushang will sleep with whomever",
    note_11="Changed 'whom' to 'whomever' for proper grammatical "
    "structure in this context.",
    difficulty=1,
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
    revised_2="Mr Chiu, I will wait for\nyou in my room",
    note_2="Added 'for' to complete the phrase 'wait for'.",
    revised_3="Is the pearl worth $100,000?",
    note_3="Corrected 'Does the pearl worth' to 'Is the pearl worth'.",
    difficulty=1,
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
    verified=True,
)  # proof_test_case_block_11
# noinspection PyArgumentList
proof_test_case_block_12 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="Mantis Fist?\nIt seems to be powerful",
    subtitle_2="Music!",
    verified=True,
)  # proof_test_case_block_12
# noinspection PyArgumentList
proof_test_case_block_13 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="Keep this",
    subtitle_2="See my Crane's Fists!",
    subtitle_3="The Tiger's Claws!",
    difficulty=1,
    prompt=True,
    verified=True,
)  # proof_test_case_block_13
# noinspection PyArgumentList
proof_test_case_block_14 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="How can a mantis fight with a tiger?",
    subtitle_2="I know Tiger Claws\nand Crane's Fists too!",
    subtitle_3="Well, try me mantis!",
    revised_3="Well, try me, mantis!",
    note_3="Added a comma after 'me' for correct direct address.",
    difficulty=1,
    verified=True,
)  # proof_test_case_block_14
# noinspection PyArgumentList
proof_test_case_block_15 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="Bravo...",
    subtitle_2="Your Tiger's claws are defeated",
    subtitle_3="Actually it's not Tiger's Claws,",
    subtitle_4="it's beggar's fists!",
    subtitle_5="That's why it's too weak",
    verified=True,
)  # proof_test_case_block_15
# noinspection PyArgumentList
proof_test_case_block_16 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="You move fast!",
    subtitle_2="It seems to be powerful...",
    subtitle_3="Kid, you don't know how\nthe wind blows",
    verified=True,
)  # proof_test_case_block_16
# noinspection PyArgumentList
proof_test_case_block_17 = EnglishProofTestCase.get_test_case_cls(12)(
    subtitle_1="The general of\nCanton has arrived",
    subtitle_2="Get lost...",
    subtitle_3="Who dares bully my son,\nlet me teach him a lesson",
    subtitle_4="Master",
    subtitle_5="Don't panic, Chan who bullied you?",
    subtitle_6="It's me who bullied others",
    subtitle_7="What? You bullied others?",
    subtitle_8="How much does he have?\nIs he qualified to be bullied by you?",
    subtitle_9="Master, they are the ones",
    subtitle_10="Who are they?",
    subtitle_11="Just take a look",
    subtitle_12="The King of Iron Hat?",
    revised_3="Who dares bully my son?\nLet me teach him a lesson.",
    note_3="Added a question mark after 'my son' and capitalized 'Let' "
    "to separate into two sentences for clarity.",
    revised_8="How much does he have?\nIs he even qualified to be bullied by you?",
    note_8="Added 'even' for natural phrasing.",
    difficulty=1,
    verified=True,
)  # proof_test_case_block_17
# noinspection PyArgumentList
proof_test_case_block_18 = EnglishProofTestCase.get_test_case_cls(6)(
    subtitle_1="Send the gift",
    subtitle_2="Chan",
    subtitle_3="They send you so valuable present,\nyou'd stop bullying them",
    subtitle_4="Come on, give tips to the girls here",
    subtitle_5="Master",
    subtitle_6="King of Iron Hat, Seng-ko-lin-ch'in\nis written on the medal",
    revised_3="They sent you such a valuable present,\nyou should stop bullying them.",
    note_3="Changed 'send' to 'sent', 'so' to 'such a', and 'you'd' to "
    "'you should' for correct grammar and clarity.",
    revised_6="King of Iron Hat, Seng-ko-lin-ch'in,\nis written on the medal.",
    note_6="Added a comma after 'Seng-ko-lin-ch'in' for clarity.",
    difficulty=1,
    verified=True,
)  # proof_test_case_block_18
# noinspection PyArgumentList
proof_test_case_block_19 = EnglishProofTestCase.get_test_case_cls(19)(
    subtitle_1="How dare you seize the medal\nof His Majesty?",
    subtitle_2="Cuff him",
    subtitle_3="Hold it, according to the Ching's law,",
    subtitle_4="Courtier is to allowed hooking",
    subtitle_5="Now, you are in the brothel",
    subtitle_6="Do you know you have committed\nthe laws of Ching?",
    subtitle_7="How about you?",
    subtitle_8="- You mean me?\n-Yes!",
    subtitle_9="That's right, I come...",
    subtitle_10="- to arrest...\n- You!",
    subtitle_11="- Him!\n- Arrest him!",
    subtitle_12="I am the general of Canton,",
    subtitle_13="so I should arrest\nthose bad people",
    subtitle_14="By the way...",
    subtitle_15="What else? Go ahead",
    subtitle_16="Today is the birthday of\nthe Ex-Empress Dowager",
    subtitle_17="So your crime is doubled",
    subtitle_18="It may cause to capital punishment",
    subtitle_19="Kill him...",
    revised_4="Courtiers are not allowed to partake in hooking",
    note_4="Reworded for clarity and corrected 'Courtier is to allowed "
    "hooking' to 'Courtiers are not allowed to partake in "
    "hooking.",
    revised_6="Do you know you have violated\nthe laws of Ching?",
    note_6="Changed 'committed the laws' to 'violated the laws' for accuracy.",
    revised_8="- You mean me?\n- Yes!",
    note_8="Added a space after the hyphen for consistency.",
    revised_18="It may result in capital punishment",
    note_18="Changed 'cause to capital punishment' to 'result in capital "
    "punishment' for correct usage.",
    difficulty=1,
    verified=True,
)  # proof_test_case_block_19
# noinspection PyArgumentList
proof_test_case_block_20 = EnglishProofTestCase.get_test_case_cls(18)(
    subtitle_1="According to the Ching laws,",
    subtitle_2="anyone without a tail should be killed",
    subtitle_3="So you...",
    subtitle_4="Do you want to see my hair?",
    subtitle_5="You can see as much as you want!\nFat-headed",
    subtitle_6="Cut the crap, just kill him",
    subtitle_7="OK, it's finished",
    subtitle_8="General So, let's play happily together,\nso forget it",
    subtitle_9="I haven't played!",
    subtitle_10="Your Majesty,",
    subtitle_11="a rascal has ruined\nthe atmosphere here,",
    subtitle_12="I should be blamed\nfor poor arrangement",
    subtitle_13="None of your business",
    subtitle_14="Let's go",
    subtitle_15="Master, you can't fool this guy\nLet's go",
    subtitle_16="OK, go",
    subtitle_17="Just forget the trouble",
    subtitle_18="Young master, your hat",
    revised_5="You can see as much as you want!\nFathead.",
    note_5="Changed 'Fat-headed' to 'Fathead.' for natural usage and punctuation.",
    revised_8="General So, let's play happily together,\nso just forget it.",
    note_8="Added 'just' for clarity and natural phrasing.",
    revised_15="Master, you can't fool this guy.\nLet's go.",
    note_15="Added a period to separate the two sentences for clarity.",
    difficulty=1,
    verified=True,
)  # proof_test_case_block_20
# noinspection PyArgumentList
proof_test_case_block_21 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="He is great!",
    verified=True,
)  # proof_test_case_block_21
# noinspection PyArgumentList
proof_test_case_block_22 = EnglishProofTestCase.get_test_case_cls(14)(
    subtitle_1="Uncle Mok, the dishes\nare all poisoned",
    subtitle_2="Chiu assassinated our Master",
    subtitle_3="and some generals of\nThe Taiping Reign",
    subtitle_4="And he framed us, the Beggars Association,\nto be the assassinators",
    subtitle_5="Thus made us",
    subtitle_6="being despised by the world",
    subtitle_7="Saying that we became the dogs\nof the government",
    subtitle_8="I should ask him to pay for it",
    subtitle_9="His initial power is harmful",
    subtitle_10="Don't take action\nuntil he is trapped",
    subtitle_11="Because we can't defeat him even\nwe group together",
    subtitle_12="I will try my best to seduce\nhim to the bed",
    subtitle_13="Senior, somebody is coming",
    subtitle_14="Get ready...",
    revised_4="And he framed us, the Beggars Association,\nto be the assassins",
    note_4="Changed 'assassinators' to 'assassins'.",
    revised_6="to be despised by the world",
    note_6="Changed 'being despised' to 'to be despised' for grammatical correctness.",
    revised_11="Because we can't defeat him even\nif we group together",
    note_11="Added 'if' to correct the conditional clause: 'even if we "
    "group together'.",
    difficulty=1,
    verified=True,
)  # proof_test_case_block_22
# noinspection PyArgumentList
proof_test_case_block_23 = EnglishProofTestCase.get_test_case_cls(16)(
    subtitle_1="Miss Yushang, we meet again",
    subtitle_2="Why do you come here?\nWhere is Mister Chiu?",
    subtitle_3="The pearl of Mr Chiu is broken",
    subtitle_4="by Mr So and become pearl powder",
    subtitle_5="I have drunk it",
    subtitle_6="Don't judge Mr So from his hair,",
    subtitle_7="he is really romantic and funny",
    subtitle_8="But...",
    subtitle_9="Stop, I have taken his money,\n100,000 taels you know?",
    subtitle_10="I won't give it back",
    subtitle_11="About the personality of Mr So...",
    subtitle_12="Cut the crap, pimp!",
    subtitle_13="Leave here first",
    subtitle_14="Yes, you are right",
    subtitle_15="Miss Seven...",
    subtitle_16="Just accept this",
    revised_3="The pearl of Mr. Chiu is broken",
    note_3="Added a period after 'Mr' for consistency: 'Mr. Chiu'.",
    revised_4="by Mr. So and became pearl powder",
    note_4="Added a period after 'Mr' for consistency and changed "
    "'become' to 'became' for correct tense.",
    difficulty=1,
    verified=True,
)  # proof_test_case_block_23
# noinspection PyArgumentList
proof_test_case_block_24 = EnglishProofTestCase.get_test_case_cls(14)(
    subtitle_1="Who is this guy?",
    subtitle_2="I don't know",
    subtitle_3="Miss, first of all, I have a good\nnews to you",
    subtitle_4="I love you",
    subtitle_5="To me, this is a bad news",
    subtitle_6="I know you will reply like this",
    subtitle_7="Cut the crap",
    subtitle_8="I wish to pay you 100 pearls",
    subtitle_9="for you your company tonight",
    subtitle_10="I don't want to talk to you",
    subtitle_11="Please get out",
    subtitle_12="I haven't chosen a wrong one",
    subtitle_13="OK, I will drink this wine first",
    subtitle_14="No...",
    revised_3="Miss, first of all, I have good news for you",
    note_3="Changed 'a good news to you' to 'good news for you'.",
    revised_9="for your company tonight",
    note_9="Removed extra 'you' to correct the phrase to 'for your company tonight'.",
    revised_12="I haven't chosen the wrong one",
    note_12="Changed 'a wrong one' to 'the wrong one'.",
    difficulty=1,
    verified=True,
)  # proof_test_case_block_24
# noinspection PyArgumentList
proof_test_case_block_25 = EnglishProofTestCase.get_test_case_cls(16)(
    subtitle_1="It surprised me",
    subtitle_2="Miss",
    subtitle_3="Hands off!",
    subtitle_4="You know Kung-fu?",
    subtitle_5="No, I don't know Kung-fu at all",
    subtitle_6="I beg you, stop bothering me",
    subtitle_7="I won't accompany you",
    subtitle_8="Yushang, no one treats\nme like this",
    subtitle_9="I have found that\nI am in love with you",
    subtitle_10="What?",
    subtitle_11="I have been in love with you",
    subtitle_12="Are you kidding?",
    subtitle_13="I am not kidding,\nI decided to marry you",
    subtitle_14="Are you nuts?",
    subtitle_15="Kidding?",
    subtitle_16="Are there anyone hiding here?",
    revised_16="Is anyone hiding here?",
    note_16="Changed 'Are there anyone hiding here?' to 'Is anyone hiding "
    "here?' for correct grammar.",
    difficulty=1,
    verified=True,
)  # proof_test_case_block_25
# noinspection PyArgumentList
proof_test_case_block_26 = EnglishProofTestCase.get_test_case_cls(13)(
    subtitle_1="That's good, I want a witness",
    subtitle_2="Witness?",
    subtitle_3="Yes, I swear in front of your sword",
    subtitle_4="I do want to marry Miss Yushang\nas my wife, I am sincere",
    subtitle_5="If I cheat,\nI will be killed by thunder",
    subtitle_6="Sister, I feel excited for you",
    subtitle_7="Hey",
    subtitle_8="Don't you know it's that easy\nto be my husband?",
    subtitle_9="How can I be your husband?",
    subtitle_10="I want him to be the superior\nKung-fu master",
    subtitle_11="Be the top of all",
    subtitle_12="Can you do that?",
    subtitle_13="Let me think for one second",
    revised_8="Don't you know it isn't that easy\nto be my husband?",
    note_8="Changed 'it's that easy' to 'it isn't that easy' to match "
    "the intended meaning.",
    difficulty=1,
    verified=True,
)  # proof_test_case_block_26
# noinspection PyArgumentList
proof_test_case_block_27 = EnglishProofTestCase.get_test_case_cls(8)(
    subtitle_1="I can do it",
    subtitle_2="OK",
    subtitle_3="Do it first and then look for me",
    subtitle_4="Well, I think we should fix a date\nfor our wedding",
    subtitle_5="Because, this is too easy to me\nto be the Kung-fu scholar!",
    subtitle_6="OK, but you'd give me some time\nto consider it",
    subtitle_7="No problem, I will wait for your answer\noutside the garden",
    subtitle_8="I won't leave until seeing you",
    revised_5="Because this is too easy for me\nto be the Kung-fu scholar!",
    note_5="Changed 'to me' to 'for me'.",
    revised_6="OK, but you should give me some time\nto consider it",
    note_6="Changed 'you'd' to 'you should'.",
    difficulty=1,
    verified=True,
)  # proof_test_case_block_27
# noinspection PyArgumentList
proof_test_case_block_28 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Crazy!",
    verified=True,
)  # proof_test_case_block_28
# noinspection PyArgumentList
proof_test_case_block_29 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="We come for the Beggars Association,\n"
    "those unrelated persons leave at once",
    revised_1="We come from the Beggars Association,\nThose unrelated,  leave at once.",
    note_1="Changed 'for' to 'from'.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # proof_test_case_block_29
# noinspection PyArgumentList
proof_test_case_block_30 = EnglishProofTestCase.get_test_case_cls(4)(
    subtitle_1="Sir, the timing is fit",
    subtitle_2="The road is safe now, please go",
    subtitle_3="Good, very good",
    subtitle_4="Let's go!",
    revised_1="Sir, the timing is right",
    note_1="Changed 'fit' to 'right' for natural phrasing.",
    difficulty=1,
    verified=True,
)  # proof_test_case_block_30
# noinspection PyArgumentList
proof_test_case_block_31 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="Shit, we are late",
    subtitle_2="That Manchurian should be blamed",
)  # proof_test_case_block_31
# noinspection PyArgumentList
proof_test_case_block_32 = EnglishProofTestCase.get_test_case_cls(6)(
    subtitle_1="Sister...",
    subtitle_2="What's the matter?",
    subtitle_3="The idiot is still there",
    subtitle_4="Let's kill him",
    subtitle_5="Forget it,\nhe doesn't mean to bother us",
    subtitle_6="Let him go",
)  # proof_test_case_block_32
# noinspection PyArgumentList
proof_test_case_block_33 = EnglishProofTestCase.get_test_case_cls(9)(
    subtitle_1="Are you fond of him?",
    subtitle_2="What did you say?",
    subtitle_3="I won't fall in love with anybody",
    subtitle_4="until Chiu is killed",
    subtitle_5="Especially him",
    subtitle_6="Chiu is good at Kung-fu",
    subtitle_7="Mok said, we can't defeat him unless\n"
    'using the "Dragon Killing Palms"',
    subtitle_8="So, I can never marry!",
    subtitle_9="Let's go, if you want to marry",
    revised_9="Let's go, if you want to get married",
    note_9="Changed 'marry' to 'get married' for natural phrasing.",
    difficulty=1,
)  # proof_test_case_block_33
# noinspection PyArgumentList
proof_test_case_block_34 = EnglishProofTestCase.get_test_case_cls(11)(
    subtitle_1="What evil are you?\nHow dare you scare me?",
    subtitle_2="Mr So, it's me!",
    subtitle_3="You are the pimp?!",
    subtitle_4="Yes!",
    subtitle_5="You have flat figure,\nwhere are your busts?",
    subtitle_6="It's early in the morning,\nthey haven't waken up yet",
    subtitle_7="It's lucky of you\nfor not being killed",
    subtitle_8="Don't go around if you haven't\nmade up yet",
    subtitle_9="I won't do it again",
    subtitle_10="Stop waiting for Miss Yushang,\nshe left",
    subtitle_11="What?",
    revised_5="You have a flat figure,\nwhere is your bust?",
    note_5="Added 'a' before 'flat figure' and changed 'where are your "
    "busts?' to 'where is your bust?' for grammatical "
    "correctness.",
    revised_6="It's early in the morning,\nit hasn't woken up yet.",
    note_6="Changed 'they haven't waken up yet' to 'it hasn't woken up "
    "yet' to match the singular 'bust' and correct verb form.",
    revised_7="You're lucky\nnot to have been killed.",
    note_7="Changed 'It's lucky of you for not being killed' to 'You're "
    "lucky not to have been killed.' for natural phrasing.",
    revised_8="Don't go around if you haven't\nput on your makeup yet.",
    note_8="Changed 'made up' to 'put on your makeup' for clarity and naturalness.",
    difficulty=1,
)  # proof_test_case_block_34
# noinspection PyArgumentList
proof_test_case_block_35 = EnglishProofTestCase.get_test_case_cls(67)(
    subtitle_1="Where is she going?",
    subtitle_2="She... she is going to Peking",
    subtitle_3="Peking?",
    subtitle_4="Men should contribute to the country",
    subtitle_5="Where should I put my pig-tail?",
    subtitle_6="Swing and swing...",
    subtitle_7="I pull it and play it...",
    subtitle_8="Dad!",
    subtitle_9="I decided to join the examination for the\nscholar of Martial Arts",
    subtitle_10="Chan",
    subtitle_11="I have been longing for this word\nfor 25 years",
    subtitle_12="For the family of us, you should do that",
    subtitle_13="Don't misunderstand it,\nI do it not for no one",
    subtitle_14="But for a woman",
    subtitle_15="What a hero!",
    subtitle_16="For a girl, you want to be the scholar\nof Martial Arts!",
    subtitle_17="Who is that girl?",
    subtitle_18="The hooker of Yee Hung Brothel,\nMiss Yushang",
    subtitle_19="For a hooker?",
    subtitle_20="What's wrong with it?",
    subtitle_21="You have different taste,\nyou are great!",
    subtitle_22="I am admiring you!",
    subtitle_23="I will accompany you to Peking",
    subtitle_24="2, 3, 4, 5, 6",
    subtitle_25="I am coming",
    subtitle_26="Young master is going for the examination,\nlet's move to Peking too",
    subtitle_27="Stop chasing,",
    subtitle_28="we won't take the hens with us",
    subtitle_29="Be careful!",
    subtitle_30="If you break my stuff,\nI will teach you good lesson",
    subtitle_31="Be careful!",
    subtitle_32="Good morning dad",
    subtitle_33="Good morning",
    subtitle_34="You want to move\neverything to Peking?",
    subtitle_35="Sure",
    subtitle_36="Please leave me a clothe",
    subtitle_37="You are only a kid,\nyou don't need this",
    subtitle_38="But I am no small",
    subtitle_39="Are you bigger than mine?",
    subtitle_40="You despise me!",
    subtitle_41="Mine will be bigger\nthan yours one day",
    subtitle_42="Let's find something,\nsay trousers to cover it",
    subtitle_43="I don't want to see it",
    subtitle_44="Why are you standing here for?\nWhy don't you remove it?",
    subtitle_45="It's a hard job to remove\nsuch a big house!",
    subtitle_46="Please, work hard men!",
    subtitle_47="Ready, 1, 2, 3, push!",
    subtitle_48="Push!",
    subtitle_49="Be careful!",
    subtitle_50="Tie it well...",
    subtitle_51="Master, do you want to\nmove the tree too?",
    subtitle_52="Sure,",
    subtitle_53="or how can I eat Lychee in Peking?",
    subtitle_54="Push it over...",
    subtitle_55="Be careful",
    subtitle_56="Take care of my Lychee,\nyou fat headed!",
    subtitle_57="Chiu helped me to terminate",
    subtitle_58="the Hairy Gang in Kwangsi",
    subtitle_59="So I bring him here\nto greet Your Majesty",
    subtitle_60="Fine, I am now appointing you to be\nthe Deputy Secretary",
    subtitle_61="Hope you will serve our Ching Dynasty\nwhole-heartedly",
    subtitle_62="Thank you, Your Majesty",
    subtitle_63="Your Majesty, Mr Chiu is a magician",
    subtitle_64="Why don't you ask him to\nshow you something?",
    subtitle_65="Magic?",
    subtitle_66="Mr Chiu, then show me your magic",
    subtitle_67="Yes, Your Majesty",
    revised_2="She... she is going to Peking.",
    note_2="Added period at the end for consistency.",
    revised_5="Where should I put my pigtail?",
    note_5="Changed 'pig-tail' to 'pigtail'.",
    revised_9="I decided to join the examination for the\nScholar of Martial Arts.",
    note_9="Capitalized 'Scholar' for consistency with other uses.",
    revised_12="For our family, you should do that.",
    note_12="Changed 'the family of us' to 'our family' for natural phrasing.",
    revised_13="Don't misunderstand it,\nI do it not for no one.",
    note_13="No change needed; double negative is used for emphasis in dialogue.",
    revised_16="For a girl, you want to be the Scholar\nof Martial Arts!",
    note_16="Capitalized 'Scholar' for consistency.",
    revised_22="I admire you!",
    note_22="Changed 'I am admiring you!' to 'I admire you!' for correct tense.",
    revised_30="If you break my stuff,\nI will teach you a good lesson.",
    note_30="Added 'a' before 'good lesson'.",
    revised_32="Good morning, Dad.",
    note_32="Added comma and capitalized 'Dad'.",
    revised_36="Please leave me a cloth.",
    note_36="Changed 'clothe' to 'cloth'.",
    revised_38="But I am not small.",
    note_38="Changed 'no' to 'not'.",
    revised_46="Please, work hard, men!",
    note_46="Added comma for clarity.",
    revised_56="Take care of my lychee,\nyou fathead!",
    note_56="Changed 'Lychee' to lowercase and 'fat headed' to 'fathead'.",
    revised_61="Hope you will serve our Ching Dynasty\nwholeheartedly.",
    note_61="Changed 'whole-heartedly' to 'wholeheartedly'.",
    difficulty=1,
)  # proof_test_case_block_35
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
