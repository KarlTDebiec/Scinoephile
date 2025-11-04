#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""KOB English proof test cases."""

from __future__ import annotations

from scinoephile.core.english.proofing.abcs import EnglishProofTestCase

# noinspection PyArgumentList
test_case_block_0 = EnglishProofTestCase.get_test_case_cls(33)(
    subtitle_1="When Mrs. McBing was in labour...",
    subtitle_2="A pan appeared in the sky.",
    subtitle_3="It flied along Garden Street...",
    subtitle_4="Turned left, and stopped\nat the Beef ball King.",
    subtitle_5="Correction:",
    subtitle_6="It first arrived at the Market Building...",
    subtitle_7="Lingered a bit...Correction:",
    subtitle_8="It flied over the railway, turned right...",
    subtitle_9="And headed directly for the Bazaar.",
    subtitle_10="It flied on...",
    subtitle_11="At last coming into the maternity ward.",
    subtitle_12="There, on the right hand side of\nMrs. McBing.",
    subtitle_13="Correction: Left hand side.",
    subtitle_14="The pan stayed.",
    subtitle_15="Mrs. McBing,\nconvinced that this was a miracle,",
    subtitle_16="Made a wish...",
    subtitle_17="Thinking of her soon-to-be-born son.",
    subtitle_18="Please make him\na clever and smart boy!",
    subtitle_19="The pan didn't seem to hear her words.",
    subtitle_20="So Mrs. McBing amended her wish:",
    subtitle_21="Or make him a smart businessman?",
    subtitle_22="Or maybe...",
    subtitle_23="Or make him really handsome.",
    subtitle_24="As handsome as Chow Yun Fat or\nTony Leung!",
    subtitle_25="The pan didn't respond.",
    subtitle_26="Mrs. McBing, in panic...",
    subtitle_27="Made a final amendment:",
    subtitle_28="Her boy needed not to be\nsmart or handsome",
    subtitle_29="As long as luck be with him!",
    subtitle_30="It's nice to depend on oneself...",
    subtitle_31="But luck is essential still.",
    subtitle_32="Of course Chow and Leung are\nlucky guys...",
    subtitle_33="But then they are smart too!",
    revised_3="It flew along Garden Street...",
    note_3="Changed 'flied' to 'flew'.",
    revised_4="Turned left, and stopped\nat the Beefball King.",
    note_4="Changed 'Beef ball' to 'Beefball'.",
    revised_7="Lingered a bit... Correction:",
    note_7="Added a space after ellipsis before 'Correction:'.",
    revised_8="It flew over the railway, turned right...",
    note_8="Changed 'flied' to 'flew'.",
    revised_10="It flew on...",
    note_10="Changed 'flied' to 'flew'.",
    revised_28="Her boy need not be\nsmart or handsome",
    note_28="Changed 'needed not to be' to 'need not be' for correct phrasing.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_0
# noinspection PyArgumentList
test_case_block_1 = EnglishProofTestCase.get_test_case_cls(13)(
    subtitle_1="Finally, the pan dropped to the floor...",
    subtitle_2="Mrs. McBing,\nbelieving her wish granted...",
    subtitle_3="Thought that was magnificent!",
    subtitle_4="But what had the pan granted her?",
    subtitle_5="A smart boy? A lucky boy?",
    subtitle_6="Or a Chow look-alike?",
    subtitle_7="To commemorate this, Mrs. McBing...",
    subtitle_8="Decided to name her son McNificient.",
    subtitle_9="No! It's better to be humble!",
    subtitle_10="I'll name him McDull!",
    subtitle_11="Dear all...",
    subtitle_12="I am the boy, no more McNificient...",
    subtitle_13="I'm McDull!",
    prompt=True,
    verified=True,
)  # test_case_block_1
# noinspection PyArgumentList
test_case_block_2 = EnglishProofTestCase.get_test_case_cls(17)(
    subtitle_1='\\"My School\\"',
    subtitle_2="Oh dear,",
    subtitle_3="your calves have grown strong.",
    subtitle_4="I've been desperately...",
    subtitle_5="looking for a school!",
    subtitle_6="Why not try the one...",
    subtitle_7="at the Emporium?",
    subtitle_8="The Spring Flower Kindergarten?",
    subtitle_9="Yeah! The one at the junction...",
    subtitle_10="Right next to Silver City Food Mall.",
    subtitle_11="The Spring Flower Kindergarten!",
    subtitle_12="Only 10 minutes walk from\nthe MTR Station!",
    subtitle_13="Spring Flower Kindergarten,\ngood environment...",
    subtitle_14="With white teachers for English class!",
    subtitle_15="White teachers for English class?",
    subtitle_16="Yeah!",
    subtitle_17="Spring Flower offer white teachers!",
    revised_1='"My School"',
    note_1="Corrected quotation marks.",
    revised_12="Only 10 minutes' walk from\nthe MTR Station!",
    note_12="Added possessive apostrophe to 'minutes'' for correct phrasing.",
    revised_17="Spring Flower offers white teachers!",
    note_17="Changed 'offer' to 'offers' for subject-verb agreement.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_2
# noinspection PyArgumentList
test_case_block_3 = EnglishProofTestCase.get_test_case_cls(23)(
    subtitle_1='"We are all happy children..."',
    subtitle_2='"Wee sing everyday!"',
    subtitle_3='"We learn as we grow..."',
    subtitle_4='"We are the flowers of spring!"',
    subtitle_5="This piggy kid in a rabbit outfit...",
    subtitle_6="Who doesn't look the least\nlike Chow or Leung...",
    subtitle_7="That's me, McDull.",
    subtitle_8="This is my kindergarten.",
    subtitle_9="The headmaster came from\nthe countryside...",
    subtitle_10="As a result, he speaks with an accent.",
    subtitle_11="For many years...",
    subtitle_12="I had difficulty hearing him.",
    subtitle_13="- Tart! - Tart!",
    subtitle_14="Duck dumpling! - Duck dumpling!",
    subtitle_15="The 97 Rule... - The 97 Rule...",
    subtitle_16="Shall be replaced by the 98 Rule!",
    subtitle_17="Shall be replaced by the 98 Rule!",
    subtitle_18="Good, children!",
    subtitle_19="We are sharing an important issue...",
    subtitle_20="this morning:",
    subtitle_21="Children, have you handed in\nthe school fee?",
    subtitle_22="Yes!",
    subtitle_23="Great! Now move to class.",
    revised_2='"We sing every day!"',
    note_2="Changed 'Wee sing everyday!' to 'We sing every day!' for "
    "correct spelling and phrasing.",
    revised_14="- Duck dumpling! - Duck dumpling!",
    note_14="Added missing hyphen before 'Duck dumpling!' for consistency "
    "with previous subtitle.",
    revised_15="- The 97 Rule... - The 97 Rule...",
    note_15="Added missing hyphen before 'The 97 Rule...' for consistency "
    "with previous subtitle.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_3
# noinspection PyArgumentList
test_case_block_4 = EnglishProofTestCase.get_test_case_cls(55)(
    subtitle_1="You might conclude that\nthis is a shabby school.",
    subtitle_2="But, for me and my mates...",
    subtitle_3="This is the most beautiful paradise!",
    subtitle_4="...Also, there is Miss Chan.",
    subtitle_5="Who adores us in\nher absent-minded way.",
    subtitle_6="Also, she is a Faye Wong wannabe.",
    subtitle_7="Actually, Kelly Chan will do!",
    subtitle_8="Roll call now.",
    subtitle_9="- McMug! - Present!",
    subtitle_10="- Fai! - Present!",
    subtitle_11="Goosie! - Present!",
    subtitle_12="Darby! - Present!",
    subtitle_13="- May! - Present!",
    subtitle_14="- June! - Present!",
    subtitle_15="- May! - Present!",
    subtitle_16="- McMug! - Present!",
    subtitle_17="May!",
    subtitle_18="Miss Chan, I've been called twice!",
    subtitle_19="Oops!",
    subtitle_20="Good morning, sir!",
    subtitle_21="Good day, sir!",
    subtitle_22="Back to roll call.",
    subtitle_23="- Fai! - Present!",
    subtitle_24="- Fai! - Present!",
    subtitle_25="Darby! - Present!",
    subtitle_26="- May! - Present!",
    subtitle_27="- McMug! - Present!",
    subtitle_28="Goosie! - Present!",
    subtitle_29="Goosie! - Present!",
    subtitle_30="Have I missed anyone?",
    subtitle_31="McDull!",
    subtitle_32="McDull!",
    subtitle_33="McDull!",
    subtitle_34="McDull!",
    subtitle_35="Hey, I don't understand...",
    subtitle_36="I keep feeling that...",
    subtitle_37="Someone is calling me.",
    subtitle_38="Don't think that I've been daydreaming.",
    subtitle_39="I was contemplating something academic:",
    subtitle_40="How does this universe work?",
    subtitle_41="I mean, I ate 6 oranges that morning...",
    subtitle_42="And my stomach wouldn't stop.",
    subtitle_43="Then I ate 3 bananas this morning.",
    subtitle_44="Again my stomach wouldn't stop...",
    subtitle_45="It just wouldn't stop!",
    subtitle_46="How are these two things related?",
    subtitle_47="There are so many things that\nI don't understand.",
    subtitle_48="But I am not afraid.",
    subtitle_49="One day, when I finish kindergarten...",
    subtitle_50="I shall move up...",
    subtitle_51="And get my degree.",
    subtitle_52="When I graduate from university, I know...",
    subtitle_53="I shall understand everything!",
    subtitle_54="And then...",
    subtitle_55="I will buy my mother a house!",
    revised_11="- Goosie! - Present!",
    note_11="Added missing hyphen before 'Goosie!' for consistency with "
    "previous subtitle.",
    revised_12="- Darby! - Present!",
    note_12="Added missing hyphen before 'Darby!' for consistency with "
    "previous subtitle.",
    revised_25="- Darby! - Present!",
    note_25="Added missing hyphen before 'Darby!' for consistency with "
    "previous subtitle.",
    revised_28="- Goosie! - Present!",
    note_28="Added missing hyphen before 'Goosie!' for consistency with "
    "previous subtitle.",
    revised_29="- Goosie! - Present!",
    note_29="Added missing hyphen before 'Goosie!' for consistency with "
    "previous subtitle.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_4
# noinspection PyArgumentList
test_case_block_5 = EnglishProofTestCase.get_test_case_cls(20)(
    subtitle_1="Our headmaster runs a tea stand...",
    subtitle_2="Which we kids frequent after class.",
    subtitle_3="- Fishball noodle, please.\nNo noodle left.",
    subtitle_4="- Fishball rice noodle then.\nNo fishball left.",
    subtitle_5="Chicken wing noodle then.\nNo noodle left.",
    subtitle_6="How about fishball congee?\n- No fishball left.",
    subtitle_7="Nothing left today?",
    subtitle_8="How about beef noodle?\n- No noodle left.",
    subtitle_9="Again?",
    subtitle_10="Fried chicken wing with fishball...\nNo fishball left.",
    subtitle_11="Hey, fishball and noodle are both gone...",
    subtitle_12="You can't combine them with other things.",
    subtitle_13="Can't combine them?",
    subtitle_14="- A bowl of fishball then.\n- No fishball left.",
    subtitle_15="- A bowl of noodle?\n- No noodle left.",
    subtitle_16="By now...",
    subtitle_17="you can probably tell how smart I am.",
    subtitle_18="Nothing worried me, all things were fine.",
    subtitle_19="No fishball left? Let's get some noodle.",
    subtitle_20="Shoot, Dull!",
    revised_3="- Fishball noodles, please.\n- No noodles left.",
    note_3="Changed 'noodle' to 'noodles' for correct plural usage; "
    "added missing hyphen before 'No noodles left.' for "
    "consistency.",
    revised_4="- Fishball rice noodles then.\n- No fishballs left.",
    note_4="Changed 'noodle' to 'noodles' and 'fishball' to 'fishballs' "
    "for correct plural usage; added missing hyphen for "
    "consistency.",
    revised_5="- Chicken wing noodles then.\n- No noodles left.",
    note_5="Changed 'noodle' to 'noodles' for correct plural usage.; "
    "added missing hyphens for consistency.",
    revised_6="- How about fishball congee?\n- No fishballs left.",
    note_6="Changed 'fishball' to 'fishballs' for correct plural usage; "
    "added missing hyphen before 'How about fishball congee?' for "
    "consistency.",
    revised_8="- How about beef noodles?\n- No noodles left.",
    note_8="Changed 'noodle' to 'noodles' for correct plural usage; "
    "added missing hyphen before 'How about beef noodles?' for "
    "consistency.",
    revised_10="- Fried chicken wing with fishballs...\n- No fishballs left.",
    note_10="Changed 'fishball' to 'fishballs' for correct plural usage; "
    "added missing hyphens for consistency.",
    revised_14="- A bowl of fishballs then.\n- No fishballs left.",
    note_14="Changed 'fishball' to 'fishballs' for correct plural usage.",
    revised_15="- A bowl of noodles?\n- No noodles left.",
    note_15="Changed 'noodle' to 'noodles' for correct plural usage.",
    revised_19="No fishballs left? Let's get some noodles.",
    note_19="Changed 'fishball' to 'fishballs' and 'noodle' to 'noodles' "
    "for correct plural usage.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_5
# noinspection PyArgumentList
test_case_block_6 = EnglishProofTestCase.get_test_case_cls(4)(
    subtitle_1="Watching myself grow and grow...",
    subtitle_2="Everyday...",
    subtitle_3="I feel full of strength!",
    subtitle_4="The world is beautiful!",
    revised_2="Every day...",
    note_2="Changed 'Everyday' to 'Every day' for correct usage.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_6
# noinspection PyArgumentList
test_case_block_7 = EnglishProofTestCase.get_test_case_cls(7)(
    subtitle_1="There is a song Miss Chan loves...",
    subtitle_2="Which I always want to learn...",
    subtitle_3="But it just comes out different.",
    subtitle_4='You mean\nA\\" ll Things Bright and Beautiful\\"?',
    subtitle_5="Yes, all are fine!",
    subtitle_6="All things on earth...",
    subtitle_7="They are fine!!",
    revised_4='You mean\n"All Things Bright and Beautiful"?',
    note_4="Corrected quotation marks and spacing.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_7
# noinspection PyArgumentList
test_case_block_8 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1='\\"My Mother\\"',
    revised_1='"My Mother"',
    note_1="Corrected quotation marks.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_8
# noinspection PyArgumentList
test_case_block_9 = EnglishProofTestCase.get_test_case_cls(7)(
    subtitle_1="1,2,3,4,5,6,7…..",
    subtitle_2="No pain no gain!",
    subtitle_3="Monday till Sunday... No pain no gain!",
    subtitle_4="The middleaged swine is Mrs. McBing,",
    subtitle_5="my mother...",
    subtitle_6="A brilliant woman...",
    subtitle_7="carrying the world!",
    revised_1="1, 2, 3, 4, 5, 6, 7...",
    note_1="Added spaces after commas and corrected ellipsis to three dots.",
    revised_4="The middle-aged swine is Mrs. McBing,",
    note_4="Added hyphen in 'middle-aged'.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_9
# noinspection PyArgumentList
test_case_block_10 = EnglishProofTestCase.get_test_case_cls(15)(
    subtitle_1="Yes, she is really something.",
    subtitle_2="She works in insurance,\nreal estate and trading.",
    subtitle_3="At the height of IT,\nshe even sets up her cooking site...",
    subtitle_4="www.MrsMcBing.com",
    subtitle_5="Offering brilliant dishes.",
    subtitle_6='Welcome to "Mrs. Mc Can Cook".',
    subtitle_7="Today we're doing a simple dish,",
    subtitle_8="Paper Chicken.",
    subtitle_9="Kids at home would love it.",
    subtitle_10="The ingredient: a chicken bun.",
    subtitle_11="Slowly, we tear the paper away\nfrom the bun",
    subtitle_12="Now we have a bun paper.",
    subtitle_13="Turn the paper over like this...",
    subtitle_14="Voila! Simple, isn't it?",
    subtitle_15="Thank you, everyone!",
    revised_3="At the height of IT,\nshe even set up her cooking site...",
    note_3="Changed 'sets' to 'set' for correct past tense.",
    difficulty=1,
    verified=True,
)  # test_case_block_10
# noinspection PyArgumentList
test_case_block_11 = EnglishProofTestCase.get_test_case_cls(6)(
    subtitle_1="How time flies since last episode!",
    subtitle_2="Now we shall do a Paper Bun.",
    subtitle_3="The ingredient takes only a paper.",
    subtitle_4="Do it like this...",
    subtitle_5="And we have a Paper Bun.",
    subtitle_6="Isn't this a lovely bun?",
    revised_1="How time flies since the last episode!",
    note_1="Added 'the' before 'last episode' for correct phrasing.",
    revised_3="The only ingredient is paper.",
    note_3="Changed 'The ingredient takes only a paper.' to 'The only "
    "ingredient is paper.' for clarity and natural phrasing.",
    difficulty=1,
    verified=True,
)  # test_case_block_11
# noinspection PyArgumentList
test_case_block_12 = EnglishProofTestCase.get_test_case_cls(9)(
    subtitle_1="A novelty today for everyone:",
    subtitle_2="Chicken Bun Paper Bunning a Bun.",
    subtitle_3="First, unwrap the chicken\nfrom the paper.",
    subtitle_4="Now we have a paper and\na piece of chicken.",
    subtitle_5="Use the bun paper to wrap up\nthe chicken like this...",
    subtitle_6="And then wrap it like this...",
    subtitle_7="The delicious Chicken Bun Paper\nBunning a Bun!",
    subtitle_8="Such a simple dish!",
    subtitle_9="See if the chicken is good!",
    difficulty=1,
    verified=True,
)  # test_case_block_12
# noinspection PyArgumentList
test_case_block_13 = EnglishProofTestCase.get_test_case_cls(20)(
    subtitle_1="Kids are bound to love...",
    subtitle_2="today's dish...",
    subtitle_3="Bunning a Chicken Bun Paper...",
    subtitle_4="Bunning the Paper Chicken.",
    subtitle_5="It takes simple work.",
    subtitle_6="Use the chicken bun to bun...",
    subtitle_7="the chicken bun...",
    subtitle_8="Then use the chicken bun paper to...",
    subtitle_9="bun and bun...",
    subtitle_10="Paper, bun, bun, paper, bun...",
    subtitle_11="Paper, chicken, bun, bun, chicken...",
    subtitle_12="But my mother has her tender side.",
    subtitle_13="Every night,\nshe tells me a story before sleep.",
    subtitle_14="Once upon a time, a boy lied. One day...",
    subtitle_15="He died.",
    subtitle_16="Once upon a time, a boy studied hard.",
    subtitle_17="He grew up and got rich.",
    subtitle_18="Once upon a time, a boy was naughty.\nOne day...",
    subtitle_19="He twisted his ankle.",
    subtitle_20="Mother, I want to sleep.",
    revised_5="It's simple work.",
    note_5="Changed 'It takes simple work.' to 'It's simple work.' for "
    "natural phrasing.",
    difficulty=1,
    verified=True,
)  # test_case_block_13
# noinspection PyArgumentList
test_case_block_14 = EnglishProofTestCase.get_test_case_cls(7)(
    subtitle_1="Once upon a time, a boy slept a lot.\nNext day...",
    subtitle_2="He died.",
    subtitle_3="That is my mother's direct approach.",
    subtitle_4="Her love for me is direct.",
    subtitle_5="Her expectation of me is direct.",
    subtitle_6="For her, it is always...",
    subtitle_7="'no pain no gain\\...",
    revised_7='"no pain no gain".',
    note_7="Corrected quotation marks.",
    difficulty=1,
    verified=True,
)  # test_case_block_14
# noinspection PyArgumentList
test_case_block_15 = EnglishProofTestCase.get_test_case_cls(27)(
    subtitle_1="But there are things that\nsimply cannot be gained.",
    subtitle_2="Days come and go.",
    subtitle_3="Talking about Chow look-alike...",
    subtitle_4="You still think it's going happen?",
    subtitle_5="When it comes to luck...",
    subtitle_6="The lottery numbers that\nmother obliges to draw...",
    subtitle_7="Failed even to bring her one cent!",
    subtitle_8="As for being smart...",
    subtitle_9="I did try hard, but then...",
    subtitle_10="But then, I still have dreams.",
    subtitle_11='"My Ideal World"',
    subtitle_12="Maldives, a world outside our world.",
    subtitle_13="The sky blue, clouds white,\nthe trees tall and water bright.",
    subtitle_14="The colourful world of the tropical sea.",
    subtitle_15="The primitive ocean of primitive energy.",
    subtitle_16="Experience a world that\nknows no boundary!",
    subtitle_17="Enjoy a trip to your ideal world.",
    subtitle_18="Brilliant Touring Agency,\nlicense no. 350999",
    subtitle_19="Mother, you know where Maldives is?",
    subtitle_20="Far.",
    subtitle_21="How far?",
    subtitle_22="You need to fly there.",
    subtitle_23="Mother will you take me there?",
    subtitle_24="One day when I am rich.",
    subtitle_25="When will you get rich?",
    subtitle_26="Soon...",
    subtitle_27="In my dream!",
    revised_4="You still think it's going to happen?",
    note_4="Added 'to' in 'going to happen' for correct phrasing.",
    revised_6="The lottery numbers that\nMother obliges to draw...",
    note_6="Capitalized 'Mother' for consistency as a proper noun.",
    revised_19="Mother, do you know where the Maldives is?",
    note_19="Added 'do' for correct question structure and 'the' before 'Maldives'.",
    difficulty=1,
    verified=True,
)  # test_case_block_15
# noinspection PyArgumentList
test_case_block_16 = EnglishProofTestCase.get_test_case_cls(19)(
    subtitle_1="Good morning, sir!",
    subtitle_2="Good day, sir!",
    subtitle_3="Where is your favourite place?",
    subtitle_4="My favourite place is Japan.",
    subtitle_5="They have Disneyland and\nHello Kitty Land.",
    subtitle_6="I bought my hairpin there.",
    subtitle_7="My favourite place is Canada.",
    subtitle_8="Grandma and my uncles live there.",
    subtitle_9="My favourite place is Bangkok.",
    subtitle_10="They have water sports and\nshark's fin soup.",
    subtitle_11="My favourite place is that...",
    subtitle_12="What's-it's name.",
    subtitle_13="They have Fun World and Food Mall.",
    subtitle_14="Their chicken rice fills you up.",
    subtitle_15="Right, that's Silver City Centre.",
    subtitle_16="They serve huge bowls of rice.",
    subtitle_17="As for the place I most want to go, wow!",
    subtitle_18="There, the sky is blue,\nclouds white, the trees tall...",
    subtitle_19="It is a world outside our world.",
    revised_12="What's-its-name.",
    note_12="Added hyphens to 'What's-its-name.' for correct phrasing.",
    difficulty=1,
    verified=True,
)  # test_case_block_16
# noinspection PyArgumentList
test_case_block_17 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="Rise and shine, kiddo.",
    subtitle_2="Oh?",
    subtitle_3="Mother!",
    verified=True,
)  # test_case_block_17
# noinspection PyArgumentList
test_case_block_18 = EnglishProofTestCase.get_test_case_cls(8)(
    subtitle_1="Take some medicine and he'll be fine.",
    subtitle_2="Will he not what after the medicine?",
    subtitle_3="No!",
    subtitle_4="Need he not what for the medicine?",
    subtitle_5="No! I'll give him a shot.",
    subtitle_6="A shot?",
    subtitle_7="He's scared of shots.",
    subtitle_8="Is he scared of dying?",
    revised_2="After the medicine, will he need some other thing?",
    note_2="Revised to clarify speaker's avoidance of referring directly "
    "to the prospect of her son receiving a shot.",
    revised_4="So with the medicine, he won't need some other thing?",
    note_4="Changed 'Need he not what for the medicine?' to 'Does he "
    "need anything with the medicine?' for clarity and correct "
    "English.",
    difficulty=3,
    verified=True,
)  # test_case_block_18
# noinspection PyArgumentList
test_case_block_19 = EnglishProofTestCase.get_test_case_cls(9)(
    subtitle_1="How are you doing? Take the medicine.",
    subtitle_2="Mother I don't want medicine.",
    subtitle_3="Please mother, no.",
    subtitle_4="I don't want the strawberry drink!",
    subtitle_5="You won't get well without the medicine.",
    subtitle_6="Sweetie, we will go to Maldives once\nyou get well.",
    subtitle_7="Really?",
    subtitle_8="Has mother ever lied before?",
    subtitle_9="Now, drink up.",
    revised_2="Mother, I don't want medicine.",
    note_2="Added a comma after 'Mother' for correct punctuation.",
    revised_8="Has Mother ever lied before?",
    note_8="Capitalized 'Mother' as it is used as a proper noun.",
    difficulty=1,
    verified=True,
)  # test_case_block_19
# noinspection PyArgumentList
test_case_block_20 = EnglishProofTestCase.get_test_case_cls(7)(
    subtitle_1="Yes, Maldives!",
    subtitle_2="Maldives!",
    subtitle_3="Maldives!",
    subtitle_4="Maldives!",
    subtitle_5="Mother, when will we go?",
    subtitle_6="I will book the ticket once you get well.",
    subtitle_7="Come on, drink up!",
    verified=True,
)  # test_case_block_20
# noinspection PyArgumentList
test_case_block_21 = EnglishProofTestCase.get_test_case_cls(7)(
    subtitle_1="Look, mother!",
    subtitle_2="Mother, I am well!",
    subtitle_3="I've taken all the medicine.",
    subtitle_4="But you've taken everything edible\nat home.",
    subtitle_5="You see, the whole bottle was filled...",
    subtitle_6="And I gulped it down bit by bit...",
    subtitle_7="I did it!",
    verified=True,
)  # test_case_block_21
# noinspection PyArgumentList
test_case_block_22 = EnglishProofTestCase.get_test_case_cls(26)(
    subtitle_1="Now I am a good boy!",
    subtitle_2="Now I am not sick!",
    subtitle_3="Mother...",
    subtitle_4="What?",
    subtitle_5="When are we going to Maldives?",
    subtitle_6="Maldives?",
    subtitle_7="You said we would go once I get well.",
    subtitle_8="Maldives, where the trees tall and\nwater bright...",
    subtitle_9="The world outside our world!",
    subtitle_10="Those words have flare.",
    subtitle_11="I am happy for you.",
    subtitle_12="Mother, you promised...",
    subtitle_13="We'd go to Maldives once I get well.",
    subtitle_14="I meant once I get rich.",
    subtitle_15="No, that wasn't what you mean.",
    subtitle_16="You said we'd go once I get well.",
    subtitle_17="You promised!",
    subtitle_18="Now stop crying.",
    subtitle_19="We will go to Maldives.",
    subtitle_20="Really? - Yes.",
    subtitle_21="When?",
    subtitle_22="Once I get rich.",
    subtitle_23="But you are rich.",
    subtitle_24="Sure, sure, I am rich.",
    subtitle_25="We will go next week, ok?",
    subtitle_26="Bravo!",
    revised_7="You said we would go once I got well.",
    note_7="Changed 'get' to 'got' for correct tense.",
    revised_8="Maldives, where the trees are tall and\nwater bright...",
    note_8="Added 'are' for grammatical correctness: 'trees are tall'.",
    revised_10="Those words have flair.",
    note_10="Changed 'flare' to 'flair' (correct word for style or eloquence).",
    revised_13="We'd go to Maldives once I got well.",
    note_13="Changed 'get' to 'got' for correct tense.",
    revised_15="No, that wasn't what you meant.",
    note_15="Changed 'mean' to 'meant' for correct tense.",
    revised_16="You said we'd go once I got well.",
    note_16="Changed 'get' to 'got' for correct tense.",
    revised_20="- Really? - Yes.",
    note_20="Added missing hyphen before 'Really?' for consistency.",
    revised_25="We will go next week, OK?",
    note_25="Capitalized 'OK' for standard usage.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_22
# noinspection PyArgumentList
test_case_block_23 = EnglishProofTestCase.get_test_case_cls(14)(
    subtitle_1="This is McDull.",
    subtitle_2="Hey, I'm leaving tomorrow.",
    subtitle_3="- Yes... - Is that right?",
    subtitle_4="The food on board is horrible?",
    subtitle_5="Be it so!",
    subtitle_6="We couldn't bring our own food, right?",
    subtitle_7="Still chatting away?",
    subtitle_8="You need to pack.",
    subtitle_9="Tell them I'm going to Maldives tomorrow.",
    subtitle_10="Where the trees tall and water bright...",
    subtitle_11="Hey, you!",
    subtitle_12="Coming!",
    subtitle_13="I need to pack now. Talk to you later.",
    subtitle_14="See you!",
    revised_10="Where the trees are tall and water bright...",
    note_10="Added 'are' for grammatical correctness: 'trees are tall'.",
    difficulty=1,
    verified=True,
)  # test_case_block_23
# noinspection PyArgumentList
test_case_block_24 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="Mother, do I need to bring\nmy birth certificate?",
    subtitle_2="I guess so.",
    subtitle_3="And school report?",
    subtitle_4="We don't need that.",
    subtitle_5="Wow, I'm saved!",
    verified=True,
)  # test_case_block_24
# noinspection PyArgumentList
test_case_block_25 = EnglishProofTestCase.get_test_case_cls(4)(
    subtitle_1="I found it!",
    subtitle_2="I found my birth certificate!",
    subtitle_3="Mother, you keep it and don't lose it...",
    subtitle_4="Or else we're stuck.",
    verified=True,
)  # test_case_block_25
# noinspection PyArgumentList
test_case_block_26 = EnglishProofTestCase.get_test_case_cls(8)(
    subtitle_1="Leave on the morning, return at night.",
    subtitle_2="Mother said that'd make things worthy.",
    subtitle_3="Hence...",
    subtitle_4="The most beautiful day\nin my childhood experience...",
    subtitle_5="Passed.",
    subtitle_6="Do you think paper is\na good chicken wrapper?",
    subtitle_7="Maybe.",
    subtitle_8="If only for one small piece.",
    verified=True,
)  # test_case_block_26
# noinspection PyArgumentList
test_case_block_27 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Goodnight, mother! - Goodnight!",
    revised_1="- Good night, Mother! - Good night!",
    note_1="Added missing hyphen before 'Good night, Mother!' for "
    "consistency; corrected 'Goodnight' to 'Good night'; "
    "capitalized 'Mother' as it is used as a proper noun.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_27
# noinspection PyArgumentList
test_case_block_28 = EnglishProofTestCase.get_test_case_cls(9)(
    subtitle_1="The Hong Kong...",
    subtitle_2="windsurfing athlete San San Li...",
    subtitle_3="Has just won the first gold medal\nin Hong Kong history!",
    subtitle_4="San San, when confirmed her winning...",
    subtitle_5="Told reporters that her result...",
    subtitle_6="Help proves that\nHong Kong athletes are horrible...",
    subtitle_7='Excuse me, it should be "honourable ".',
    subtitle_8="Hong Kong athletes\nare honourable athletes.",
    subtitle_9="End of special report.",
    revised_3="has just won the first gold medal\nin Hong Kong history!",
    note_3="Changed 'Has' to lowercase 'has' to continue the sentence "
    "from previous subtitle.",
    revised_4="San San, when her win was confirmed...",
    note_4="Changed 'when confirmed her winning' to 'when her win was "
    "confirmed' for grammatical correctness.",
    revised_5="told reporters that her result...",
    note_5="Changed 'Told' to lowercase 'told' to continue the sentence "
    "from previous subtitle.",
    revised_6="helped prove that\nHong Kong athletes are horrible...",
    note_6="Changed 'Help proves' to 'helped prove' for correct tense "
    "and subject-verb agreement.",
    revised_7='Excuse me, it should be "honourable".',
    note_7="Removed extra space inside the quotation marks.",
    difficulty=1,
    verified=True,
)  # test_case_block_28
# noinspection PyArgumentList
test_case_block_29 = EnglishProofTestCase.get_test_case_cls(12)(
    subtitle_1="Then, mother seemed inspired.",
    subtitle_2="Handsome, lucky, smart...",
    subtitle_3="So much for those plans.",
    subtitle_4="Now how about something physical?",
    subtitle_5='"Looking for Logan"',
    subtitle_6="And so, while one dream lingers on...",
    subtitle_7="Another one begins.",
    subtitle_8='"aka: How Does a Calf Become a Calf?"',
    subtitle_9="It's about the Calf!",
    subtitle_10="I know it is not easy.",
    subtitle_11="I know it is not easy to find Logan.",
    subtitle_12="I know it is not easy for him to take me in.",
    difficulty=1,
    verified=True,
)  # test_case_block_29
# noinspection PyArgumentList
test_case_block_30 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="No matter how difficult this is...",
    subtitle_2="Logan will be my master!",
    subtitle_3="I shall get an Olympic medal!",
    verified=True,
)  # test_case_block_30
# noinspection PyArgumentList
test_case_block_31 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="Cheung Chau!",
    subtitle_2="You raised San San,\nnow you will raise me!",
    subtitle_3="When I receive my Olympic medal...",
    subtitle_4="I shall tell the world:",
    subtitle_5="HK athletes are honourable athletes!",
    verified=True,
)  # test_case_block_31
# noinspection PyArgumentList
test_case_block_32 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Cheung Chau, I finally make it here.",
    revised_1="Cheung Chau, I finally made it here.",
    note_1="Changed 'make' to 'made' for correct past tense.",
    difficulty=1,
    verified=True,
)  # test_case_block_32
# noinspection PyArgumentList
test_case_block_33 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="I must kiss this holy land!",
    verified=True,
)  # test_case_block_33
# noinspection PyArgumentList
test_case_block_34 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="Kiddo, this is Lamma Island.",
    subtitle_2="Lamma Island?\nWhere Chow Yun Fat grew up?",
    verified=True,
)  # test_case_block_34
# noinspection PyArgumentList
test_case_block_35 = EnglishProofTestCase.get_test_case_cls(10)(
    subtitle_1="I came into hiding on this island...",
    subtitle_2="To stay away from the paparazzi.",
    subtitle_3="And so many kids came to seek me out.",
    subtitle_4="So I came to live here.",
    subtitle_5="You want me to be your master?",
    subtitle_6="Forget it!",
    subtitle_7="You city kids are all spoiled...",
    subtitle_8="Good for nothing!",
    subtitle_9="You want to get an Olympic medal too?",
    subtitle_10="Dream on!",
    verified=True,
)  # test_case_block_35
# noinspection PyArgumentList
test_case_block_36 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Kiddo, look!",
    verified=True,
)  # test_case_block_36
# noinspection PyArgumentList
test_case_block_37 = EnglishProofTestCase.get_test_case_cls(10)(
    subtitle_1="This calf...",
    subtitle_2="So thick, so strong!",
    subtitle_3="And so muscular!",
    subtitle_4="With steely veins running down...",
    subtitle_5="Hair sticking out like wire...",
    subtitle_6="And those tough toenails!",
    subtitle_7="How many hills must it travel...",
    subtitle_8="How many seas must it pass...",
    subtitle_9="How much pain must it bear...",
    subtitle_10="Before a calf becomes a calf?",
    verified=True,
)  # test_case_block_37
# noinspection PyArgumentList
test_case_block_38 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="I shall have this calf!",
    subtitle_2="Master!",
    verified=True,
)  # test_case_block_38
# noinspection PyArgumentList
test_case_block_39 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Can I take a pee?",
    verified=True,
)  # test_case_block_39
# noinspection PyArgumentList
test_case_block_40 = EnglishProofTestCase.get_test_case_cls(26)(
    subtitle_1="Whenever I sing this song, I need to pee.",
    subtitle_2="Taking a pee first would not help.",
    subtitle_3="But I must sing it now.",
    subtitle_4="With this song, I hope...",
    subtitle_5="Logan will think better of me.",
    subtitle_6="Logan will be my master!",
    subtitle_7="The song goes like this...",
    subtitle_8="'Big bun, have two more...\\\" '",
    subtitle_9="'Big bun, have two more...\\\" '",
    subtitle_10='\\"Forget about indigestion.\\"',
    subtitle_11="'Big bun, have two more...\\\" '",
    subtitle_12="'Big bun, have two more...\\\" '",
    subtitle_13='\\"Forget about indigestion.\\"',
    subtitle_14="'Big bun, have two more...\\\" '",
    subtitle_15="'Big bun, have two more...\\\" '",
    subtitle_16='\\"Forget about indigestion.\\"',
    subtitle_17='\\"Eat the bun, grow a calf...\\"',
    subtitle_18="'Respect my mother.\\\"",
    subtitle_19="'Eat the bun, toughen my calf...\\\" '",
    subtitle_20='\\"Serve my country.\\"',
    subtitle_21="'Big bun, have two more...\\\" '",
    subtitle_22="'Big bun, have two more...\\\" '",
    subtitle_23='\\"Forget about indigestion.\\"',
    subtitle_24="'Big bun, have two more...\\\" '",
    subtitle_25="'Big bun, have two more...\\\" '",
    subtitle_26='\\"Forget about indigestion.\\"',
    revised_8='"Big bun, have two more..."',
    note_8="Corrected quotation marks.",
    revised_9='"Big bun, have two more..."',
    note_9="Corrected quotation marks.",
    revised_10='"Forget about indigestion."',
    note_10="Corrected quotation marks.",
    revised_11='"Big bun, have two more..."',
    note_11="Corrected quotation marks.",
    revised_12='"Big bun, have two more..."',
    note_12="Corrected quotation marks.",
    revised_13='"Forget about indigestion."',
    note_13="Corrected quotation marks.",
    revised_14='"Big bun, have two more..."',
    note_14="Corrected quotation marks.",
    revised_15='"Big bun, have two more..."',
    note_15="Corrected quotation marks.",
    revised_16='"Forget about indigestion."',
    note_16="Corrected quotation marks.",
    revised_17='"Eat the bun, grow a calf..."',
    note_17="Corrected quotation marks.",
    revised_18='"Respect my mother."',
    note_18="Corrected quotation marks.",
    revised_19='"Eat the bun, toughen my calf..."',
    note_19="Corrected quotation marks.",
    revised_20='"Serve my country."',
    note_20="Corrected quotation marks.",
    revised_21='"Big bun, have two more..."',
    note_21="Corrected quotation marks.",
    revised_22='"Big bun, have two more..."',
    note_22="Corrected quotation marks.",
    revised_23='"Forget about indigestion."',
    note_23="Corrected quotation marks.",
    revised_24='"Big bun, have two more..."',
    note_24="Corrected quotation marks.",
    revised_25='"Big bun, have two more..."',
    note_25="Corrected quotation marks.",
    revised_26='"Forget about indigestion."',
    note_26="Corrected quotation marks.",
    difficulty=1,
    verified=True,
)  # test_case_block_40
# noinspection PyArgumentList
test_case_block_41 = EnglishProofTestCase.get_test_case_cls(8)(
    subtitle_1="Logan looks strange after the song.",
    subtitle_2="I must grab my chance.",
    subtitle_3="Master! Please be my master!",
    subtitle_4="Or let me kneel here forever!",
    subtitle_5="Get up...",
    subtitle_6="Thank you master!",
    subtitle_7="Silly, help me get up.",
    subtitle_8="My calf has gone numb!",
    revised_6="Thank you, Master!",
    note_6="Added a comma and capitalized 'Master' as a form of address.",
    difficulty=1,
    verified=True,
)  # test_case_block_41
# noinspection PyArgumentList
test_case_block_42 = EnglishProofTestCase.get_test_case_cls(12)(
    subtitle_1="I tell mother what happened today.",
    subtitle_2="She won't say a word...",
    subtitle_3="But starts to defreeze a chicken.",
    subtitle_4="At dinner,\nmother offers 3 glasses of wine...",
    subtitle_5="Oranges and the chicken to\nthe ancestral tablet.",
    subtitle_6="Mother then tells me to kneel down.",
    subtitle_7="She mumbles something when...",
    subtitle_8="We pay our respect to our ancestor.",
    subtitle_9="As mother pours the wine on the floor...",
    subtitle_10="She says in her solemn, tender voice:",
    subtitle_11="Be good,",
    subtitle_12="learn with the master and\nhonour the ancestor.",
    revised_1="I tell Mother what happened today.",
    note_1="Capitalized 'Mother' as it is used as a proper noun.",
    revised_3="But starts to defrost a chicken.",
    note_3="Changed 'defreeze' to 'defrost' for correct usage.",
    revised_4="At dinner,\nMother offers 3 glasses of wine...",
    note_4="Capitalized 'Mother' as it is used as a proper noun.",
    revised_8="We pay our respect to our ancestors.",
    note_8="Changed 'ancestor' to plural 'ancestors' for correct usage.",
    revised_12="learn with the master and\nhonour the ancestors.",
    note_12="Changed 'ancestor' to plural 'ancestors' for correct usage.",
    difficulty=1,
    verified=True,
)  # test_case_block_42
# noinspection PyArgumentList
test_case_block_43 = EnglishProofTestCase.get_test_case_cls(25)(
    subtitle_1="In honour of my master,\nmother throws a banquet.",
    subtitle_2="As I am the last disciple of the master...",
    subtitle_3="Everyone on Cheung Chau comes.",
    subtitle_4="San San's lover thinks...",
    subtitle_5="I have a nice thick back.",
    subtitle_6="San San is in training and couldn't come.",
    subtitle_7="LA I my mates are there too...",
    subtitle_8="Bringing school report,\nmedals and big buns.",
    subtitle_9="They hope Logan will take them in also.",
    subtitle_10="After the soup, the ceremony begins.",
    subtitle_11="Mother pours a cup of tea and\nI offer it to the master.",
    subtitle_12="After all the hardship looking for Logan...",
    subtitle_13="Now I can windsurf together with\nSan San!",
    subtitle_14="I offer the tea to Logan...",
    subtitle_15="He drinks the tea and\nbecomes my master.",
    subtitle_16="All the guests look happy.",
    subtitle_17="And everyone from\nCheung Chau applauds.",
    subtitle_18="Thank you for honouring me!",
    subtitle_19="In my life, I have two skills that\nI'm proud of.",
    subtitle_20="One is windsurfing.",
    subtitle_21="That I have passed onto San San.",
    subtitle_22="The other, I shall pass onto\nmy new disciple...",
    subtitle_23="Let him show the world...",
    subtitle_24="what a marvelous skill that is!",
    subtitle_25="Can you tell us what skill is that?",
    revised_7="All my mates are there too...",
    note_7="Corrected 'LA I my mates' to 'All my mates'.",
    revised_25="Can you tell us what skill that is?",
    note_25="Changed 'what skill is that' to 'what skill that is' for "
    "correct word order.",
    difficulty=3,
    verified=True,
)  # test_case_block_43
# noinspection PyArgumentList
test_case_block_44 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="That is...",
    subtitle_2="Bun snatching!",
    verified=True,
)  # test_case_block_44
# noinspection PyArgumentList
test_case_block_45 = EnglishProofTestCase.get_test_case_cls(19)(
    subtitle_1="Bun snatching?",
    subtitle_2='\\"Bun Snatching\\",\nfor our uninformed audience...',
    subtitle_3="Is a unique Cheung Chau tradition.",
    subtitle_4="Each year, in the forth month,",
    subtitle_5="Cheung Chau people...",
    subtitle_6="Set up 3 stacks of bun to celebrate.",
    subtitle_7="Stacks of bun?",
    subtitle_8="Literally speaking...",
    subtitle_9="A stack of bun is a stack of many buns!",
    subtitle_10="Each stack coming up to 6, 7 storeys.",
    subtitle_11="Imagine how high that is.",
    subtitle_12="Bun snatching is to snatch those buns!",
    subtitle_13="When the time comes,",
    subtitle_14="hundreds of youth would rush up...",
    subtitle_15="The higher the bun you snatch,\nthe more blessed you are.",
    subtitle_16="And the more praises you get.",
    subtitle_17="In 1978, 2 stacks tumbled down,\nhurting many.",
    subtitle_18='\\"Bun Snatching\\" was thus banned!',
    subtitle_19="And the unique tradition is lost.",
    revised_2='"Bun Snatching",\nfor our uninformed audience...',
    note_2="Removed unnecessary escape characters from the quotation marks.",
    revised_4="Each year, in the fourth month,",
    note_4="Corrected 'forth' to 'fourth'.",
    revised_6="Set up 3 stacks of buns to celebrate.",
    note_6="Changed 'bun' to 'buns' for correct plural usage.",
    revised_7="Stacks of buns?",
    note_7="Changed 'bun' to 'buns' for correct plural usage.",
    revised_9="A stack of buns is a stack of many buns!",
    note_9="Changed 'bun' to 'buns' for correct plural usage.",
    revised_10="Each stack coming up to 6 or 7 storeys.",
    note_10="Changed comma to 'or' for natural phrasing.",
    revised_16="And the more praise you get.",
    note_16="Changed 'praises' to singular 'praise' for correct usage.",
    revised_18='"Bun Snatching" was thus banned!',
    note_18="Removed unnecessary escape characters from the quotation marks.",
    difficulty=1,
    verified=True,
)  # test_case_block_45
# noinspection PyArgumentList
test_case_block_46 = EnglishProofTestCase.get_test_case_cls(16)(
    subtitle_1="The Olympic medal...\nit has slipped away.",
    subtitle_2="Every Saturday,\nI'd take a ferry to Cheung Chau...",
    subtitle_3="To practice bun snatching.",
    subtitle_4="A game with no medal,\nno competitor, no competition...",
    subtitle_5="A game nobody knows of.",
    subtitle_6="A game with no bun to snatch!",
    subtitle_7="All I do is to go to the master's home...",
    subtitle_8="And crawl around the shelf.",
    subtitle_9="My win!",
    subtitle_10="Keep going, lazy bone!",
    subtitle_11="One day, San San arrives!",
    subtitle_12="San San, my idol!",
    subtitle_13="Seeing San San...",
    subtitle_14="Makes me forget all these weeks'\nhard work.",
    subtitle_15="San San!",
    subtitle_16="San yourself! Work!",
    difficulty=1,
    verified=True,
)  # test_case_block_46
# noinspection PyArgumentList
test_case_block_47 = EnglishProofTestCase.get_test_case_cls(8)(
    subtitle_1="You hear me?",
    subtitle_2="So San San leaves without seeing me.",
    subtitle_3="In despair, I crawl up the shelf.",
    subtitle_4="I have had a lot of things said to me...",
    subtitle_5='But\\"San yourself\\"...',
    subtitle_6="hurts like never before.",
    subtitle_7="I... I...",
    subtitle_8="I am quitting!",
    revised_5='But "San yourself"...',
    note_5="Removed unnecessary escape characters from the quotation marks.",
    difficulty=1,
    verified=True,
)  # test_case_block_47
# noinspection PyArgumentList
test_case_block_48 = EnglishProofTestCase.get_test_case_cls(4)(
    subtitle_1="Today is the first time\nI sit down with Logan.",
    subtitle_2="He must be around 50,",
    subtitle_3="with a baby face.",
    subtitle_4="Fresh from the oven!",
    verified=True,
)  # test_case_block_48
# noinspection PyArgumentList
test_case_block_49 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="This thing...",
    subtitle_2="What does it look like?",
    verified=True,
)  # test_case_block_49
# noinspection PyArgumentList
test_case_block_50 = EnglishProofTestCase.get_test_case_cls(21)(
    subtitle_1="Dull... he's not a bad student.",
    subtitle_2="Logan then proceeds to tell me a lot...",
    subtitle_3="His ambition, his expectation of Dull.",
    subtitle_4="He says he'll teach all he knows to Dull.",
    subtitle_5="The more he talks,\nthe more excited he gets.",
    subtitle_6="He tells me windsurfing\nis not his strongest.",
    subtitle_7="His strongest is really bun snatching...",
    subtitle_8="Something combining Fist,",
    subtitle_9="ritual and gymnastic.",
    subtitle_10="He says bun snatching is\nhis lifelong achievement.",
    subtitle_11="Move your feet!",
    subtitle_12="Look!",
    subtitle_13="This calf... so thick, so strong!",
    subtitle_14="And so muscular!",
    subtitle_15="With steely veins running down...",
    subtitle_16="Hair sticking out like wire...",
    subtitle_17="And those tough toenails!",
    subtitle_18="How many hills must it travel...",
    subtitle_19="How many seas must it pass...",
    subtitle_20="How much pain must it bear...",
    subtitle_21="Before a calf becomes a calf?",
    revised_3="His ambition, his expectations of Dull.",
    note_3="Changed 'expectation' to 'expectations' for correct plural usage.",
    revised_8="Something combining martial arts,",
    note_8="Changed 'Fist' to 'martial arts' for clarity and natural phrasing.",
    revised_9="acrobatic opera, and gymnastics.",
    note_9="Changed 'ritual' to 'acrobatic opera' for clarity and "
    "natural phrasing; changed 'gymnastic' to 'gymnastics' for "
    "correct noun form.",
    difficulty=3,
    verified=True,
)  # test_case_block_50
# noinspection PyArgumentList
test_case_block_51 = EnglishProofTestCase.get_test_case_cls(6)(
    subtitle_1="My son...",
    subtitle_2="Your son, he will get this calf.",
    subtitle_3="I have no idea why would Dull need...",
    subtitle_4="such a calf.",
    subtitle_5="But, looking at those steely veins...",
    subtitle_6="I am reminded of Dull's pa, Bing.",
    revised_3="I have no idea why Dull would need...",
    note_3="Changed word order for correct phrasing: 'why would Dull "
    "need' to 'why Dull would need'.",
    difficulty=1,
    verified=True,
)  # test_case_block_51
# noinspection PyArgumentList
test_case_block_52 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="The electronic dictionary\ncannot be found.",
    subtitle_2="Where could it be?",
    subtitle_3="Could it be that...?",
    verified=True,
)  # test_case_block_52
# noinspection PyArgumentList
test_case_block_53 = EnglishProofTestCase.get_test_case_cls(35)(
    subtitle_1="So mother has been using the dictionary?",
    subtitle_2="But why is she writing in English?",
    subtitle_3="The letter is short.",
    subtitle_4="Mother must have translated it\nword by word.",
    subtitle_5="I use the machine to turn it back\ninto Chinese.",
    subtitle_6="It is addressed to\nthe Olympic Committee Chairman.",
    subtitle_7='\\"Dear Chairman:\\"',
    subtitle_8="'How are you? I am fine.\\\"",
    subtitle_9='\\"You like bun? I like bun!\\"',
    subtitle_10='"We Hong Kong people here love bun."',
    subtitle_11='\\"Buns of all sort.\\"',
    subtitle_12="'Dear friend,",
    subtitle_13='it is important to snatch buns.\\"',
    subtitle_14='\\"It is a game, no joke.\\"',
    subtitle_15='\\"One needs energy,\nand many night congee.\\"',
    subtitle_16='\\"In my stupid opinion...\\"',
    subtitle_17="'Snatching bun is an Olympic game.",
    subtitle_18='\\"Let athletes all over the world snatch!\\"',
    subtitle_19='\'And there will be peace.\\" \\"',
    subtitle_20='\\"Do you have children?\\"',
    subtitle_21='\\"I have a boy, Dull.\\"',
    subtitle_22="She's talking about me!",
    subtitle_23='\\"He is a good boy.\\"',
    subtitle_24='\\"He knows how to snatch buns.\\"',
    subtitle_25='\\"One day,\nI can see him snatching buns...\\"',
    subtitle_26='\\"Ending up snatching\nan Olympic medal.\\"',
    subtitle_27='\\"That is the biggest comfort\na mother can get.\\"',
    subtitle_28='\\"Let the world know\nthe talent of your children.\\"',
    subtitle_29='\\"Parents will do anything for that.\\"',
    subtitle_30='\\"That is why I write you this sudden letter.\\"',
    subtitle_31="'Although you don't know\nhumble things like me.\\\"",
    subtitle_32='\'But my boy is big, very big.\\" \\"',
    subtitle_33='"One day, you will know him too."',
    subtitle_34='\\"Thank you for your cooperation.\\"',
    subtitle_35='\\"Yours faithfully, Mrs. Mc\\"',
    revised_7='"Dear Chairman:"',
    note_7="Corrected quotation marks.",
    revised_8='"How are you? I am fine."',
    note_8="Corrected quotation marks.",
    revised_9='"You like bun? I like bun!"',
    note_9="Corrected quotation marks.",
    revised_11='"Buns of all sort."',
    note_11="Corrected quotation marks.",
    revised_12='"Dear friend,',
    note_12="Corrected quotation marks.",
    revised_13='it is important to snatch buns."',
    note_13="Corrected quotation marks.",
    revised_14='"It is a game, no joke."',
    note_14="Corrected quotation marks.",
    revised_15='"One needs energy,\nand many night congee."',
    note_15="Corrected quotation marks.",
    revised_16='"In my stupid opinion..."',
    note_16="Corrected quotation marks.",
    revised_17='"Snatching bun is an Olympic game."',
    note_17="Corrected quotation marks.",
    revised_18='"Let athletes all over the world snatch!"',
    note_18="Corrected quotation marks.",
    revised_19='"And there will be peace."',
    note_19="Corrected quotation marks.",
    revised_20='"Do you have children?"',
    note_20="Corrected quotation marks.",
    revised_21='"I have a boy, Dull."',
    note_21="Corrected quotation marks.",
    revised_23='"He is a good boy."',
    note_23="Corrected quotation marks.",
    revised_24='"He knows how to snatch buns."',
    note_24="Corrected quotation marks.",
    revised_25='"One day,\nI can see him snatching buns..."',
    note_25="Corrected quotation marks.",
    revised_26='"Ending up snatching\nan Olympic medal."',
    note_26="Corrected quotation marks.",
    revised_27='"That is the biggest comfort\na mother can get."',
    note_27="Corrected quotation marks.",
    revised_28='"Let the world know\nthe talent of your children."',
    note_28="Corrected quotation marks.",
    revised_29='"Parents will do anything for that."',
    note_29="Corrected quotation marks.",
    revised_30='"That is why I write you this sudden letter."',
    note_30="Corrected quotation marks.",
    revised_31='"Although you don\'t know\nhumble things like me."',
    note_31="Corrected quotation marks.",
    revised_32='"But my boy is big, very big."',
    note_32="Corrected quotation marks.",
    revised_34='"Thank you for your cooperation."',
    note_34="Corrected quotation marks.",
    revised_35='"Yours faithfully, Mrs. Mc"',
    note_35="Corrected quotation marks.",
    difficulty=3,
    verified=True,
)  # test_case_block_53
# noinspection PyArgumentList
test_case_block_54 = EnglishProofTestCase.get_test_case_cls(24)(
    subtitle_1="After reading mother's letter...",
    subtitle_2="I go back to Cheung Chau to practice.",
    subtitle_3="Not because of San San.",
    subtitle_4="I don't know why I want to snatch a bun.",
    subtitle_5="And I don't think it will ever become\nan Olympic item.",
    subtitle_6="But I keep learning.",
    subtitle_7="Because I love my mother.",
    subtitle_8="Master thinks my crawling has passed.",
    subtitle_9='Now I\'ll learn the\n\\"12 Bun Snatching Hands\\".',
    subtitle_10="Master says these 12 hands,",
    subtitle_11="in its prime...",
    subtitle_12="Was much admired by Butcher Lin!",
    subtitle_13="Later, I learn from McMug...",
    subtitle_14="Butcher Lin was a disciple of\nthe great Kung Fu king.",
    subtitle_15="I don't know much about Kung Fu kings...",
    subtitle_16="But I must be the ultimate pork...",
    subtitle_17="The pork that struts about",
    subtitle_18="with buns in hands.",
    subtitle_19="My mind boggles as I practice, after all...",
    subtitle_20="I am not a fan of bun snatching.",
    subtitle_21="I am only doing this for mother.",
    subtitle_22="Hence I hang on...",
    subtitle_23="Step by step, claw by claw...",
    subtitle_24='I make it pass\nthe\\"12 Bun Snatching Hands\\".',
    revised_9='Now I\'ll learn the\n"12 Bun Snatching Hands".',
    note_9="Corrected quotation marks.",
    revised_24='I make it past\nthe "12 Bun Snatching Hands".',
    note_24="Changed 'pass' to 'past' for correct usage and corrected quotation marks.",
    difficulty=1,
    verified=True,
)  # test_case_block_54
# noinspection PyArgumentList
test_case_block_55 = EnglishProofTestCase.get_test_case_cls(51)(
    subtitle_1='\\"There is no deformity,\nbut saves us from a dream\\"',
    subtitle_2="This is Dull.",
    subtitle_3="Dull the big guy, not Dull the boy.",
    subtitle_4="The two Dulls have different voices,\nand then...",
    subtitle_5="Dull the boy's world is still filled\nwith fantasy...",
    subtitle_6="Filled with hopes.",
    subtitle_7="Hope... Disappointment...",
    subtitle_8="Hope...",
    subtitle_9="Disappointment.",
    subtitle_10="On and on, he became Dull the big guy.",
    subtitle_11="But I shall tell more about Dull the boy.",
    subtitle_12="Dull the boy hoped a lot.",
    subtitle_13="He hoped there WAS a Santa Claus.",
    subtitle_14="And he hoped to eat a Christmas turkey.",
    subtitle_15="Right, I haven't eaten any turkey then.",
    subtitle_16="Everything about turkey...",
    subtitle_17="The sparkling tinkling Christmas tree...",
    subtitle_18="Like stars falling from the sky...",
    subtitle_19="Coming down by the fireplace.",
    subtitle_20="Each slice of meat looks purer than snow.",
    subtitle_21="Right in front of us...",
    subtitle_22="The aroma attacks our soul...",
    subtitle_23="Waking even the guardian angels.",
    subtitle_24="Who float around the aromatic and\nholy dish...",
    subtitle_25="Floating in the Christmas night, floating...",
    subtitle_26="All this about turkey was\nonly my imagination.",
    subtitle_27="I had never eaten a turkey.",
    subtitle_28="I had never even smelt one.",
    subtitle_29="Mother claimed turkey was too big.",
    subtitle_30="The two of us would never finish it.",
    subtitle_31="One Christmas we celebrated with\nroast duck.",
    subtitle_32="I was really, really disappointed.",
    subtitle_33="Another year,\nshe bought a mini-oven at 60% off...",
    subtitle_34="At a closed own sale.",
    subtitle_35="Thanks to the oven...",
    subtitle_36="Mother decided one day...",
    subtitle_37="We would go shopping for a turkey.",
    subtitle_38="On the way home, with turkey in hand...",
    subtitle_39="That was the happiest moment in my life.",
    subtitle_40="The turkey was ready.",
    subtitle_41="Following mother,\nwith salt on both hands...",
    subtitle_42="I rubbed the turkey's thick chest.",
    subtitle_43="When sewing up...",
    subtitle_44="Some of the stuffing...",
    subtitle_45="leaked out.",
    subtitle_46="I cried: the turkey's stomach won't stop!",
    subtitle_47="We managed to stuff the turkey\ninto the oven.",
    subtitle_48="24th, December",
    subtitle_49="Rising smoke stirred the stars with\na crunchy smell.",
    subtitle_50="The oven hummed. Hummed.",
    subtitle_51="It was like early blessing from the angels.",
    revised_1='"There is no deformity,\nbut saves us from a dream"',
    note_1="verified=True,.",
    revised_15="Right, I hadn't eaten any turkey then.",
    note_15="Changed 'haven't' to 'hadn't' for correct tense.",
    revised_34="At a close-down sale.",
    note_34="Changed 'closed own sale' to 'close-down sale'.",
    revised_48="24th December",
    note_48="Removed comma after '24th'.",
    difficulty=1,
    verified=True,
)  # test_case_block_55
# noinspection PyArgumentList
test_case_block_56 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="Such a beautiful night!",
    subtitle_2="Mother and me sat at the seafront.",
    subtitle_3="Lights shimmered on the sea.",
    subtitle_4="Beautiful and gentle.",
    subtitle_5="So beautiful!",
    revised_2="Mother and I sat at the seafront.",
    note_2="Changed 'me' to 'I' for correct grammar.",
    difficulty=1,
    verified=True,
)  # test_case_block_56
# noinspection PyArgumentList
test_case_block_57 = EnglishProofTestCase.get_test_case_cls(6)(
    subtitle_1="I had never tasted anything so strong.",
    subtitle_2="Cup noodles or roast duck\nwere not as strong.",
    subtitle_3="The taste embedded\nevery single taste bud...",
    subtitle_4="Then exploded.",
    subtitle_5="Like everything tonight...",
    subtitle_6="Most beautiful, brilliant, and tender.",
    verified=True,
)  # test_case_block_57
# noinspection PyArgumentList
test_case_block_58 = EnglishProofTestCase.get_test_case_cls(56)(
    subtitle_1="I woke up late the next day.",
    subtitle_2="The sweetness was still there\nafter washing.",
    subtitle_3="As we had a late breakfast...",
    subtitle_4="There was only corn soup for lunch.",
    subtitle_5="I idly found diced turkey...",
    subtitle_6="in the soup.",
    subtitle_7="That night finally came the long awaited...",
    subtitle_8="Christmas turkey dinner!",
    subtitle_9="Slices of meat,\naccompanied by guard and potato...",
    subtitle_10="Were dressed with soy sauce.",
    subtitle_11="It was an exciting,\nsatisfactory moment for us.",
    subtitle_12="The following week,",
    subtitle_13="turkey sandwich for breakfast.",
    subtitle_14="Sunday,",
    subtitle_15="I boldly suggested eating out.",
    subtitle_16="Mother said I was ungrateful...",
    subtitle_17="But took me out anyway.",
    subtitle_18="HT en mother got inspired again.",
    subtitle_19="What was left of the turkey was sliced...",
    subtitle_20="With me helping out at times.",
    subtitle_21="It was not easy to get rid of...",
    subtitle_22="the turkey's smell.",
    subtitle_23="Fried noodle with sliced turkey, yummy.",
    subtitle_24="Steaming chestnut bowl with\nsliced turkey.",
    subtitle_25="Peanut congee with turkey bone.",
    subtitle_26="Paper turkey bun.",
    subtitle_27="Paper turkey paper bun.",
    subtitle_28="Turkey Pete with bread.",
    subtitle_29="I shouldn't have said anything about\nthe turkey's stomach.",
    subtitle_30="Came Dragon Boat Festival,\nwhen I dug into the dumpling...",
    subtitle_31="And found more pieces of turkey...",
    subtitle_32="I lost it. I cried.",
    subtitle_33="Oh please!",
    subtitle_34="When mother finally disposed of\nthe turkey...",
    subtitle_35="It was already half year later.",
    subtitle_36="My beautiful dream ended with\nmy nightmare.",
    subtitle_37="Later, I learned that...",
    subtitle_38="A serving turkey needs only be raised...",
    subtitle_39="For a few months.",
    subtitle_40="The time the turkey spent with us...",
    subtitle_41="Was in fact longer than its life.",
    subtitle_42="I realized also, with turkey...",
    subtitle_43="Taking the first bite is all it matters.",
    subtitle_44='Afterwards,\nit is just\\" be over and done with it\\".',
    subtitle_45="I am no philosopher.",
    subtitle_46="I could not come up with any profundity.",
    subtitle_47="But, such thoughts...",
    subtitle_48="After I grew up...",
    subtitle_49="On days unrelated to Christmas...",
    subtitle_50="Did come up again a couple of times.",
    subtitle_51="Once, it was at my wedding.",
    subtitle_52="Once...",
    subtitle_53="It was at my mother's cremation.",
    subtitle_54="That day, I was looking at\nthe smoke rising up.",
    subtitle_55="Suddenly, the smell of\nthe turkey returned.",
    subtitle_56="I regretted I made mother\nthrew the turkey away.",
    revised_9="Slices of meat,\naccompanied by gourd and potato...",
    note_9="Changed 'guard' to 'gourd'.",
    revised_18="Then mother got inspired again.",
    note_18="Corrected 'HT en mother' to 'Then mother'.",
    revised_28="Turkey pâté with bread.",
    note_28="Changed 'Pete' to 'pâté'.",
    revised_35="It was already half a year later.",
    note_35="Added 'a' for correct phrasing: 'half a year'.",
    revised_38="A serving turkey needs only to be raised...",
    note_38="Added 'to' for correct infinitive form: 'needs only to be raised'.",
    revised_43="Taking the first bite is all that matters.",
    note_43="Changed 'is all it matters' to 'is all that matters'.",
    revised_44='Afterwards,\nit is just "be over and done with it".',
    note_44="Removed unnecessary escape characters from the quotation marks.",
    revised_56="I regretted I made mother\nthrow the turkey away.",
    note_56="Changed 'threw' to 'throw' for correct verb form after 'made'.",
    difficulty=1,
    verified=True,
)  # test_case_block_58
# noinspection PyArgumentList
test_case_block_59 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1='\\"Special Report\\"',
    revised_1='"Special Report"',
    note_1="Corrected quotation marks.",
    difficulty=1,
    verified=True,
)  # test_case_block_59
# noinspection PyArgumentList
test_case_block_60 = EnglishProofTestCase.get_test_case_cls(23)(
    subtitle_1="'Special Report\\\"",
    subtitle_2="Olympic medal winner San San Li\nwill compete again...",
    subtitle_3="To prove to the world that...",
    subtitle_4="HK athletes are horrible.",
    subtitle_5="Also...",
    subtitle_6="The local federation...",
    subtitle_7="officially announced today:",
    subtitle_8="HK will apply to host the Asian Games.",
    subtitle_9="Response from\nall sides has been enthusiastic.",
    subtitle_10="Among them,\nthe Bamboo Game Association...",
    subtitle_11="Is proposing Mahjong for official game.",
    subtitle_12="While Tearoom Serving Groups...",
    subtitle_13="have vowed...",
    subtitle_14='To campaign for\\"Tart Throwing\\".',
    subtitle_15="As for the Cold Cut and\nRoasting Association...",
    subtitle_16="They believe...",
    subtitle_17='\\"Duck Hanging\\"\nwould make an ideal addition.',
    subtitle_18="More interesting,\nCIC Insurance is joining force with...",
    subtitle_19="Children from...",
    subtitle_20="Spring Flower Primary School...",
    subtitle_21="In support of...",
    subtitle_22="'Bun Snatching\\\"...",
    subtitle_23="A game thought extinct.",
    revised_1='"Special Report"',
    note_1="Corrected quotation marks.",
    revised_11="is proposing Mahjong as an official game.",
    note_11="Changed 'for official game' to 'as an official game' for "
    "correct phrasing and lowercased 'is' to match sentence flow.",
    revised_14='To campaign for "Tart Throwing".',
    note_14="Corrected quotation marks.",
    revised_17='"Duck Hanging"\nwould make an ideal addition.',
    note_17="Corrected quotation marks.",
    revised_18="More interestingly,\nCIC Insurance is joining forces with...",
    note_18="Changed 'interesting' to 'interestingly' and 'joining force' "
    "to 'joining forces' for correct adverb and plural usage.",
    revised_22='"Bun Snatching"...',
    note_22="Corrected quotation marks.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_60
# noinspection PyArgumentList
test_case_block_61 = EnglishProofTestCase.get_test_case_cls(11)(
    subtitle_1="In the end...",
    subtitle_2="Nothing came of anything.",
    subtitle_3='\\"Tart Throwing\\"\nwas chosen as the highlight.',
    subtitle_4="As for the official slogan...",
    subtitle_5='\\"HK, One Big Tart\\" was a logical choice.',
    subtitle_6="Then San San Li lost.",
    subtitle_7="And the hosting right of\nthe Asian Games...",
    subtitle_8="Went to a place Hong Kong people\nhave never heard of.",
    subtitle_9="Tearoom workers,\nthose aspiring athletes...",
    subtitle_10="Went back to where\nthey used to throw their tarts.",
    subtitle_11="Everything went on as usual.",
    revised_3='"Tart Throwing"\nwas chosen as the highlight.',
    note_3="Removed unnecessary escape characters from the quotation marks.",
    revised_5='"HK, One Big Tart" was a logical choice.',
    note_5="Removed unnecessary escape characters from the quotation marks.",
    difficulty=1,
    verified=True,
)  # test_case_block_61
# noinspection PyArgumentList
test_case_block_62 = EnglishProofTestCase.get_test_case_cls(6)(
    subtitle_1="In secondary school,\nI stopped practicing the 12 hands.",
    subtitle_2="Sometimes, when I went out with mother...",
    subtitle_3="I'd still snatch a bun for her.",
    subtitle_4="Then they stopped selling buns.",
    subtitle_5="Carts were replaced by ordering sheet.",
    subtitle_6="Everything came to nothing.",
    revised_5="Carts were replaced by order sheets.",
    note_5="Changed 'ordering sheet' to 'order sheets' for correct "
    "plural and phrasing.",
    difficulty=1,
    verified=True,
)  # test_case_block_62
# noinspection PyArgumentList
test_case_block_63 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="At times, I'd go to Cheung Chau\nfor barbecue.",
    subtitle_2="The master looked older...",
    subtitle_3="Each time I saw him.",
    verified=True,
)  # test_case_block_63
# noinspection PyArgumentList
test_case_block_64 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="For environmental reason...",
    subtitle_2="They'd changed to snatch plastic buns.",
    subtitle_3="Master thought they stunk.",
    revised_1="For environmental reasons...",
    note_1="Changed 'reason' to 'reasons' for correct usage.",
    revised_2="They'd changed to snatching plastic buns.",
    note_2="Changed 'to snatch' to 'to snatching' for correct gerund "
    "usage after 'changed to'.",
    difficulty=1,
    verified=True,
)  # test_case_block_64
# noinspection PyArgumentList
test_case_block_65 = EnglishProofTestCase.get_test_case_cls(34)(
    subtitle_1="On Cheung Chau\nwas a Cheung Po Tsai Cave.",
    subtitle_2="Where legend claimed\nthe pirate hid his treasure.",
    subtitle_3="As I was the one who could crawl...",
    subtitle_4="My mates said I should take a look and\nmaybe get rich.",
    subtitle_5="So I crawled along the dark and\nnarrow cave.",
    subtitle_6="Crawling.",
    subtitle_7="There was nothing but a box.",
    subtitle_8="I opened the box...",
    subtitle_9="Inside, there was an unfinished bun.",
    subtitle_10="Maybe the pirate didn't get to finish it.",
    subtitle_11="'Eating 6 buns last night...\\\"",
    subtitle_12="'Still left me hungry.\\\"",
    subtitle_13='"Eating 1½lb white bread last night..."',
    subtitle_14="'Still left me hungry.\\\"",
    subtitle_15="'Excelled 6 sets of steps\nwhen I was young...\\\"",
    subtitle_16="'Still left me empty.\\\"",
    subtitle_17='\\"Brought up San San\nwhen I am old! Still...\\"',
    subtitle_18="Bun in hand, I suddenly realized...",
    subtitle_19="There are things that cannot be forced.",
    subtitle_20="A no is a no.",
    subtitle_21="No fishball, no noodle, no Maldives...",
    subtitle_22="No medal, no pirate's treasure.",
    subtitle_23="And the pirate took no bite.",
    subtitle_24="Stupid is not funny.",
    subtitle_25="Stupid leads to failure...",
    subtitle_26="To disappointment.",
    subtitle_27="Disappointed is not funny.",
    subtitle_28="Fatness is not funny too.",
    subtitle_29="Fatness is not powerful.",
    subtitle_30="Power doesn't mean yes.",
    subtitle_31="Bun in hand, I suddenly thought...",
    subtitle_32="Growing up, facing this sordid world...",
    subtitle_33="This not so dreamy, not so funny world...",
    subtitle_34="What shall I be?",
    revised_1="On Cheung Chau\nthere was a Cheung Po Tsai Cave.",
    note_1="Changed 'was' to 'there was' for correct phrasing.",
    revised_2="Where legend claims\na pirate hid his treasure.",
    note_2="Changed 'claimed' to 'claims' for present tense consistency "
    "with the legend.",
    revised_11='"Eating 6 buns last night..."',
    note_11="Corrected quotation marks.",
    revised_12='"Still left me hungry."',
    note_12="Corrected quotation marks.",
    revised_13='"Eating 1 ½lb white bread last night..."',
    note_13="Corrected spacing in '1½lb' to '1 ½lb'.",
    revised_14='"Still left me hungry."',
    note_14="Corrected quotation marks.",
    revised_15='"Excelled 6 sets of steps\nwhen I was young..."',
    note_15="Corrected quotation marks.",
    revised_16='"Still left me empty."',
    note_16="Corrected quotation marks.",
    revised_17='"Brought up San San\nwhen I am old! Still..."',
    note_17="Corrected quotation marks.",
    revised_28="Fatness is not funny either.",
    note_28="Changed 'too' to 'either' for natural phrasing in negative context.",
    difficulty=1,
    verified=True,
)  # test_case_block_65
# noinspection PyArgumentList
test_case_block_66 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="'... Nothing shall be done!\\\"",
    revised_1='"... Nothing shall be done!"',
    note_1="Corrected quotation marks.",
    difficulty=1,
    verified=True,
)  # test_case_block_66
# noinspection PyArgumentList
test_case_block_67 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1='\\"I Have Grown Up\\"',
    revised_1='"I Have Grown Up"',
    note_1="Corrected quotation marks.",
    difficulty=1,
    verified=True,
)  # test_case_block_67
# noinspection PyArgumentList
test_case_block_68 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1='\\"Fat, Still\\"',
    subtitle_2="'Powerful\\\"",
    revised_1='"Fat, Still"',
    note_1="Corrected quotation marks.",
    revised_2='"Powerful"',
    note_2="Corrected quotation marks.",
    difficulty=1,
    verified=True,
)  # test_case_block_68
# noinspection PyArgumentList
test_case_block_69 = EnglishProofTestCase.get_test_case_cls(26)(
    subtitle_1="Right, I am McDull the big guy.",
    subtitle_2="Fat, with raw power.",
    subtitle_3="Not doing too well.",
    subtitle_4="Negative property.",
    subtitle_5="With a pair of really thick calves.",
    subtitle_6="Very muscular...",
    subtitle_7="With steely veins running down.",
    subtitle_8="As for the toenails...",
    subtitle_9="I got bored one time and stared at it...",
    subtitle_10="They're tough, no kidding!",
    subtitle_11="Yes, the story ends here.",
    subtitle_12="This is a try.",
    subtitle_13="Error... Try...",
    subtitle_14="No guarantee that one would make it.",
    subtitle_15="In the end...",
    subtitle_16="Zero gain? Not really.",
    subtitle_17="I have my calves.",
    subtitle_18="But, standing here like this...",
    subtitle_19="When the waves hit...",
    subtitle_20="I feel great.",
    subtitle_21="You see, smart guys like me\ndon't really know...",
    subtitle_22="How to make a lesson out of\nhis own story.",
    subtitle_23="With calves in water...",
    subtitle_24="When the wind blows, I'd think...",
    subtitle_25="If mother could see me like this...",
    subtitle_26="She'd be happy.",
    revised_7="With steely veins running down them.",
    note_7="Added 'them' for clarity and grammatical correctness.",
    revised_9="I got bored one time and stared at them...",
    note_9="Changed 'it' to 'them' to match plural 'toenails'.",
    revised_22="How to make a lesson out of\ntheir own story.",
    note_22="Changed 'his' to 'their' for first-person consistency.",
    difficulty=1,
    verified=True,
)  # test_case_block_69
# noinspection PyArgumentList
test_case_block_70 = EnglishProofTestCase.get_test_case_cls(14)(
    subtitle_1="I've come up with a lesson!",
    subtitle_2="Mother got inspired after\nher dot com failed.",
    subtitle_3="She published a cookbook.",
    subtitle_4='The last recipe was\\"Roast Chicken\\".',
    subtitle_5="A simple dish no less.",
    subtitle_6='\\"Roast Chicken\\".',
    subtitle_7="Ingredient: chicken.",
    subtitle_8="Method: roast the chicken.",
    subtitle_9="That way, you have a roast chicken.",
    subtitle_10="There was a remark in the cookbook:",
    subtitle_11="If you want a delicious chicken...",
    subtitle_12="A chicken that wouldn't upset you...",
    subtitle_13="The secret is: please, roast it well!",
    subtitle_14="Thank you!",
    revised_4='The last recipe was "Roast Chicken".',
    note_4="Corrected quotation marks.",
    revised_6='"Roast Chicken".',
    note_6="Corrected quotation marks.",
    difficulty=1,
    verified=True,
)  # test_case_block_70
# noinspection PyArgumentList
test_case_block_71 = EnglishProofTestCase.get_test_case_cls(13)(
    subtitle_1="One Regular, please.",
    subtitle_2="What's a Regular?",
    subtitle_3="The same as Special.",
    subtitle_4="What's a Special?",
    subtitle_5="Same as Quickie.",
    subtitle_6="What's a Quickie?",
    subtitle_7="A Quickie is a Lunch.",
    subtitle_8="What's for Lunch?",
    subtitle_9="The same as Supper.",
    subtitle_10="What's for Supper?",
    subtitle_11="Same as Regular.",
    subtitle_12="We'll have the Regular.",
    subtitle_13="Our Regular today is fantastic!",
    verified=True,
)  # test_case_block_71
# noinspection PyArgumentList
test_case_block_72 = EnglishProofTestCase.get_test_case_cls(26)(
    subtitle_1="Sorry, Regular is gone.",
    subtitle_2="We can have the Special.",
    subtitle_3="What's a Special?",
    subtitle_4="A Special is a Lunch.",
    subtitle_5="What's for Lunch?",
    subtitle_6="What you get for Supper.",
    subtitle_7="What's for Supper?",
    subtitle_8="Same as Quickie.",
    subtitle_9="What's for Quickie?",
    subtitle_10="A Quickie is a Regular.",
    subtitle_11="But you said Regular is gone!",
    subtitle_12="Regular sure is gone.\nHow about the Special?",
    subtitle_13="It's the Special, then.",
    subtitle_14="Sorry, Special is gone.",
    subtitle_15="Mother, let's have the Quickie.",
    subtitle_16="What's for Quickie?",
    subtitle_17="A Quickie is a Regular.",
    subtitle_18="What's for Regular?",
    subtitle_19="A Regular is a Lunch.",
    subtitle_20="What's for Lunch?",
    subtitle_21="Same as Supper.",
    subtitle_22="And Supper?",
    subtitle_23="Supper is like Special.",
    subtitle_24="But you said the Special is gone.",
    subtitle_25="The Special sure is gone.\nTry Quickie. It's the same.",
    subtitle_26="We'll have Quickie.",
    difficulty=1,
    verified=True,
)  # test_case_block_72
# noinspection PyArgumentList
test_case_block_73 = EnglishProofTestCase.get_test_case_cls(10)(
    subtitle_1="Sorry, Quickie is gone.",
    subtitle_2="This is too much!\nIs there anything we can eat here?",
    subtitle_3="Try the Lunch. It's fantastic!",
    subtitle_4="How so?",
    subtitle_5="It's like the Supper.",
    subtitle_6="What about the Supper?",
    subtitle_7="It's like the Regular.",
    subtitle_8="And what about the Regular?",
    subtitle_9="The Regular is gone. Isn't that fantastic?",
    subtitle_10="Great! We'll have Lunch.",
    verified=True,
)  # test_case_block_73
# noinspection PyArgumentList
test_case_block_74 = EnglishProofTestCase.get_test_case_cls(6)(
    subtitle_1="Sorry, Lunch is gone.",
    subtitle_2="Try our Supper. It's all the same.",
    subtitle_3="I'm not having supper\nunder board daylight!",
    subtitle_4="What's in a name?\nIt's the same as Lunch.",
    subtitle_5="Great! Whatever you say!\nAnd make it quick!",
    subtitle_6="You want it quick? Try Quickie!",
    revised_3="I'm not having supper\nunder broad daylight!",
    note_3="Changed 'board daylight' to 'broad daylight'.",
    difficulty=1,
    verified=True,
)  # test_case_block_74
# noinspection PyArgumentList
test_case_block_75 = EnglishProofTestCase.get_test_case_cls(29)(
    subtitle_1="Thank you",
    subtitle_2="Why should I give you money?",
    subtitle_3="Why do you ask so many questions?",
    subtitle_4="But I should know the reason",
    subtitle_5="Anyway, you should pay it",
    subtitle_6="No, let's fix it up first",
    subtitle_7="Just give it to us, why are you\nasking so much?",
    subtitle_8="Hands off",
    subtitle_9="You mean robbing?",
    subtitle_10="Robbery...",
    subtitle_11="I am not robbing, I am begging",
    subtitle_12="Begging? How dare are you, you beggar,\nyou are cheating me!",
    subtitle_13="Don't you think I am stupid?\nI am smart, you know?",
    subtitle_14="Hey, two days passed,",
    subtitle_15="It's cold and I am hungry now",
    subtitle_16="Have you had any idea?",
    subtitle_17="I have a friend's girl-friend",
    subtitle_18="who is living in Peking",
    subtitle_19="She always admires you",
    subtitle_20="Really?",
    subtitle_21="Yes, if you are\nwilling to date her",
    subtitle_22="I think she will help us to\ngo back to Canton",
    subtitle_23="But, you have to sacrifice",
    subtitle_24="Do you mean...",
    subtitle_25="For our family,\njust as you said",
    subtitle_26="I know it's very hard for you",
    subtitle_27="Cut the crap,\nlet's go and find her",
    subtitle_28="I have arranged it",
    subtitle_29="The one wearing red dress who stands\nunder the lantern, that's her",
    revised_12="Begging? How dare you, you beggar,\nyou are cheating me!",
    note_12="Removed 'are' from 'How dare are you' to correct the phrase "
    "to 'How dare you'.",
    revised_17="I have a friend's girlfriend",
    note_17="Changed 'girl-friend' to 'girlfriend'.",
    revised_29="The one wearing the red dress who stands\n"
    "under the lantern, that's her",
    note_29="Added 'the' before 'red dress' for natural phrasing.",
    difficulty=1,
    verified=True,
)  # test_case_block_75
# noinspection PyArgumentList
test_case_block_76 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Ghost!",
    verified=True,
)  # test_case_block_76
# noinspection PyArgumentList
test_case_block_77 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="It's a benefit of you!",
    subtitle_2="Why don't you go yourself?",
    revised_1="It's to your benefit!",
    note_1="Changed 'It's a benefit of you!' to 'It's to your benefit!' "
    "for natural phrasing.",
    difficulty=1,
    verified=True,
)  # test_case_block_77
# noinspection PyArgumentList
test_case_block_78 = EnglishProofTestCase.get_test_case_cls(8)(
    subtitle_1="Chan, I haven't tried this before",
    subtitle_2="Be careful!",
    subtitle_3="Don't worry",
    subtitle_4="I'll take care of you",
    subtitle_5="You want to earn money for\nshark-fins, right?",
    subtitle_6="Right...",
    subtitle_7="Get lost...",
    subtitle_8="No show here",
    revised_5="You want to earn money for\nshark fin, right?",
    note_5="Changed 'shark-fins' to 'shark fin' for correct usage "
    "(referring to the dish or ingredient, not literal fins).",
    difficulty=1,
    verified=True,
)  # test_case_block_78
# noinspection PyArgumentList
test_case_block_79 = EnglishProofTestCase.get_test_case_cls(20)(
    subtitle_1="We just want to earn some money",
    subtitle_2="to go back to Canton",
    subtitle_3="Don't be that mean to us",
    subtitle_4="It's the Royal instruction that,",
    subtitle_5="the So's family'd\nbe beggars for life",
    subtitle_6="You two can only be beggars",
    subtitle_7="I am carrying my duty only\nMen!",
    subtitle_8="Yes!",
    subtitle_9="Remove all the things",
    subtitle_10="Yes",
    subtitle_11="Help!",
    subtitle_12="Master Chiu, it's hard\nfor one to carry it",
    subtitle_13="Ask more men to remove it",
    subtitle_14="Yes",
    subtitle_15="What do you want?",
    subtitle_16="No, we can't move it",
    subtitle_17="Let me do it",
    subtitle_18="You want a fight, don't you?",
    subtitle_19="Last time you can escape from\nYee Hung Hostel",
    subtitle_20="But you won't be\nthat lucky this time",
    revised_4="It's the Royal instruction that\nthe So family be beggars for life.",
    note_4="Removed unnecessary comma and corrected 'the So's family'd' "
    "to 'the So family be' for clarity and grammar.",
    revised_7="I am only carrying out my duty.\nMen!",
    note_7="Changed word order to 'only carrying out my duty' for "
    "natural phrasing and added punctuation.",
    revised_19="Last time you escaped from\nYee Hung Hostel,",
    note_19="Changed 'can escape' to 'escaped' for correct tense and "
    "added comma for continuity.",
    difficulty=1,
    verified=True,
)  # test_case_block_79
# noinspection PyArgumentList
test_case_block_80 = EnglishProofTestCase.get_test_case_cls(4)(
    subtitle_1="He is powerful!",
    subtitle_2="I've to defeat him",
    subtitle_3="by one powerful strike",
    subtitle_4="I can't give him another chance\nto counter attack",
    revised_2="I have to defeat him",
    note_2="Changed contraction 'I've' to 'I have' for clarity and formality.",
    revised_4="I can't give him another chance\nto counterattack",
    note_4="Changed 'counter attack' to 'counterattack' (one word).",
    difficulty=1,
    verified=True,
)  # test_case_block_80
# noinspection PyArgumentList
test_case_block_81 = EnglishProofTestCase.get_test_case_cls(9)(
    subtitle_1="Chan...",
    subtitle_2="Chan...",
    subtitle_3="Your legs and hands",
    subtitle_4="are all broken by me",
    subtitle_5="You will be cripple for the\nrest of your life",
    subtitle_6="You want to fight? Not now!",
    subtitle_7="But, you can beg for money",
    subtitle_8="Be a good beggar",
    subtitle_9="Go, go away...",
    revised_5="You will be a cripple for the\nrest of your life",
    note_5="Added 'a' before 'cripple' for correct grammar.",
    difficulty=1,
    verified=True,
)  # test_case_block_81
# noinspection PyArgumentList
test_case_block_82 = EnglishProofTestCase.get_test_case_cls(26)(
    subtitle_1="Don't panic, Chan, it's OK",
    subtitle_2="Don't panic, you'll be\nalright... Chan!",
    subtitle_3="I went to the examination hall",
    subtitle_4="with my son,",
    subtitle_5="don't you know who\nwas the examiner?",
    subtitle_6="He is Seng-ko-lin-ch'in,\nthat bastard",
    subtitle_7="He was the enemy of us!",
    subtitle_8="About our story...",
    subtitle_9="Let me stop here first,\nI want a smoke",
    subtitle_10="It's better to smoke now",
    subtitle_11="Yes, it's better",
    subtitle_12="We let him go in",
    subtitle_13="the Yee Hung Brothel",
    subtitle_14="But he framed us in return",
    subtitle_15="He tricked my son",
    subtitle_16="during the examination",
    subtitle_17="But, my son was really\nsmart and great",
    subtitle_18="He finally won the race",
    subtitle_19="To be the greatest Kung-fu\nfighter, invincible",
    subtitle_20="Be the top",
    subtitle_21="Can you do that?",
    subtitle_22="Sure!",
    subtitle_23="Well",
    subtitle_24="Come back to me\nif you can do that",
    subtitle_25="I think we should fix our\nwedding date first",
    subtitle_26="Because being the scholar is\ntoo simple to me",
    revised_7="He was our enemy!",
    note_7="Changed 'the enemy of us' to 'our enemy' for natural phrasing.",
    revised_19="To be the greatest Kung Fu\nfighter, invincible",
    note_19="Changed 'Kung-fu' to 'Kung Fu'.",
    revised_26="Because being a scholar is\ntoo simple for me.",
    note_26="Changed 'the scholar' to 'a scholar' and 'to me' to 'for me' "
    "for natural phrasing.",
    difficulty=1,
    verified=True,
)  # test_case_block_82
# noinspection PyArgumentList
test_case_block_83 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Write your name at once",
    verified=True,
)  # test_case_block_83
# noinspection PyArgumentList
test_case_block_84 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="I don't know how to write",
    verified=True,
)  # test_case_block_84
# noinspection PyArgumentList
test_case_block_85 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Chan, what's wrong with you?",
    verified=True,
)  # test_case_block_85
# noinspection PyArgumentList
test_case_block_86 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="Nightmare again?",
    subtitle_2="Don't think so much!",
    verified=True,
)  # test_case_block_86
# noinspection PyArgumentList
test_case_block_87 = EnglishProofTestCase.get_test_case_cls(10)(
    subtitle_1="Although you have taken",
    subtitle_2="2 months' rest,",
    subtitle_3="your legs and hands have not been\ntotally recovered",
    subtitle_4="Coming",
    subtitle_5="I am going to beg for food",
    subtitle_6="I will make the last herbal tea",
    subtitle_7="for you later",
    subtitle_8="Dad, you go begging again?",
    subtitle_9="This job should leave to me",
    subtitle_10="You are the Scholar...",
    revised_3="your legs and hands have not totally recovered",
    note_3="Removed 'been' for correct grammar.",
    revised_9="This job should be left to me",
    note_9="Changed 'should leave to me' to 'should be left to me'.",
    difficulty=1,
    verified=True,
)  # test_case_block_87
# noinspection PyArgumentList
test_case_block_88 = EnglishProofTestCase.get_test_case_cls(9)(
    subtitle_1="Chan, to be a beggar,",
    subtitle_2="there is some lessons!",
    subtitle_3="You can't just show your hand\nand beg for money",
    subtitle_4="At least you should have a bowl,\nthat represents your class",
    subtitle_5="Is it ridiculous?",
    subtitle_6="Hurry up",
    subtitle_7="I am coming",
    subtitle_8="We can't beg for good\nif we are late!",
    subtitle_9="Yes...",
    revised_2="there are some lessons!",
    note_2="Changed 'is' to 'are' for subject-verb agreement.",
    revised_8="We can't beg well\nif we are late!",
    note_8="Changed 'beg for good' to 'beg well' for natural phrasing.",
    difficulty=1,
    verified=True,
)  # test_case_block_88
# noinspection PyArgumentList
test_case_block_89 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="Give me money please",
    subtitle_2="Go, go , I won't give you money",
    subtitle_3="Go, don't stop me\nfrom doing business",
    revised_2="Go, go, I won't give you money",
    note_2="Removed extra space after the second 'go'.",
    difficulty=1,
    verified=True,
)  # test_case_block_89
# noinspection PyArgumentList
test_case_block_90 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Chan, dad is leaving",
    verified=True,
)  # test_case_block_90
# noinspection PyArgumentList
test_case_block_91 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Thank you...",
    verified=True,
)  # test_case_block_91
# noinspection PyArgumentList
test_case_block_92 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Thank you...",
    verified=True,
)  # test_case_block_92
# noinspection PyArgumentList
test_case_block_93 = EnglishProofTestCase.get_test_case_cls(4)(
    subtitle_1="Are you that mean?",
    subtitle_2="Why don't you write it yourself?",
    subtitle_3="You are off duty, so I just\nwant to lend it",
    subtitle_4="Don't you think I am idiot?",
    revised_3="You are off duty, so I just\nwant to borrow it",
    note_3="Changed 'lend' to 'borrow' for correct usage.",
    revised_4="Do you think I'm an idiot?",
    note_4="Changed 'Don't' to 'Do' and 'I am idiot' to 'I'm an idiot?'.",
    difficulty=1,
    verified=True,
)  # test_case_block_93
# noinspection PyArgumentList
test_case_block_94 = EnglishProofTestCase.get_test_case_cls(13)(
    subtitle_1="Dad!",
    subtitle_2="What are you doing?",
    subtitle_3="I am cold... I am cold... Chan",
    subtitle_4="No, your body is as hot as fire",
    subtitle_5="Are you sick?",
    subtitle_6="I am not...",
    subtitle_7="It's late",
    subtitle_8="I have to search for food",
    subtitle_9="Lie down, I will go this time",
    subtitle_10="Are you go for begging?",
    subtitle_11="I have my own way to get food",
    subtitle_12="Take a rest now",
    subtitle_13="I will take you to the doctor after\ngetting some money",
    revised_10="Are you going begging?",
    note_10="Changed 'Are you go for begging?' to 'Are you going "
    "begging?' for correct grammar.",
    difficulty=1,
    verified=True,
)  # test_case_block_94
# noinspection PyArgumentList
test_case_block_95 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="You bastard, why don't you eat?",
    subtitle_2="You should eat more so as\nto be strong!",
    verified=True,
)  # test_case_block_95
# noinspection PyArgumentList
test_case_block_96 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="Finish it",
    subtitle_2="No, I am full",
    subtitle_3="You should take all the food",
    subtitle_4="OK, just forget it,\nlet's go home",
    subtitle_5="Come on, eat them all",
    difficulty=1,
    verified=True,
)  # test_case_block_96
# noinspection PyArgumentList
test_case_block_97 = EnglishProofTestCase.get_test_case_cls(4)(
    subtitle_1="Little kid!",
    subtitle_2="What?",
    subtitle_3="May I...",
    subtitle_4="No",
    verified=True,
)  # test_case_block_97
# noinspection PyArgumentList
test_case_block_98 = EnglishProofTestCase.get_test_case_cls(11)(
    subtitle_1="Be merciful!",
    subtitle_2="Be merciful to me please",
    subtitle_3="My dad is dying!",
    subtitle_4="Beggar, do you want\nthe broken carbon?",
    subtitle_5="Thank you",
    subtitle_6="Can you give me some coins?",
    subtitle_7="It's you!",
    subtitle_8="No, you have mistaken",
    subtitle_9="Sister, it's him",
    subtitle_10="No, no",
    subtitle_11="Sister, he is So Chan",
    revised_4="Beggar, do you want\nthe broken charcoal?",
    note_4="Changed 'carbon' to 'charcoal' for correct context.",
    revised_8="No, you are mistaken",
    note_8="Changed 'have mistaken' to 'are mistaken' for correct usage.",
    difficulty=1,
    verified=True,
)  # test_case_block_98
# noinspection PyArgumentList
test_case_block_99 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Wait!",
    verified=True,
)  # test_case_block_99
# noinspection PyArgumentList
test_case_block_100 = EnglishProofTestCase.get_test_case_cls(9)(
    subtitle_1="Miss, who are you looking for?",
    subtitle_2="I am sorry, I have mistaken",
    subtitle_3="Tracy, take some dumpling out",
    subtitle_4="You have mistake,\nhe is not So Chan",
    subtitle_5="You are like my friend",
    subtitle_6="Come to get some dumplings if you\nget nothing to eat",
    subtitle_7="We always have surplus",
    subtitle_8="Dumpling",
    subtitle_9="Take it",
    revised_2="I am sorry, I made a mistake",
    note_2="Changed 'I have mistaken' to 'I made a mistake' for correct usage.",
    revised_3="Tracy, take some dumplings out",
    note_3="Changed 'dumpling' to 'dumplings' for correct plural usage.",
    revised_4="You are mistaken,\nhe is not So Chan",
    note_4="Changed 'You have mistake' to 'You are mistaken' for correct phrasing.",
    revised_8="Dumplings",
    note_8="Changed 'Dumpling' to 'Dumplings' for correct plural usage.",
    difficulty=1,
    verified=True,
)  # test_case_block_100
# noinspection PyArgumentList
test_case_block_101 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="Thank you...",
    subtitle_2="Sister, he wouldn't\nbe that poor",
    subtitle_3="if not were you",
    revised_3="if it were not for you",
    note_3="Changed 'if not were you' to 'if it were not for you' for correct grammar.",
    difficulty=1,
    verified=True,
)  # test_case_block_101
# noinspection PyArgumentList
test_case_block_102 = EnglishProofTestCase.get_test_case_cls(15)(
    subtitle_1="Dad, what are you doing?",
    subtitle_2="I can't stand the hunger",
    subtitle_3="So I bit the dumpling of the kid",
    subtitle_4="I have dumpling, take it back",
    subtitle_5="Could I pay you another head",
    subtitle_6="if I chopped yours",
    subtitle_7="Are you the Scholar?",
    subtitle_8="Yes, are you the Scholar?",
    subtitle_9="I was nearly the Scholar",
    subtitle_10="He is the Scholar!",
    subtitle_11="We should give him face",
    subtitle_12="Thank you",
    subtitle_13="Hold it",
    subtitle_14="Are they going to treat me",
    subtitle_15="some food?",
    revised_4="I have a dumpling, take it back",
    note_4="Added 'a' before 'dumpling' for correct grammar.",
    revised_5="Could I pay you with another head",
    note_5="Added 'with' for clarity and natural phrasing.",
    revised_14="Are they going to treat me to",
    note_14="Added 'to' for correct idiomatic expression (connects to next subtitle).",
    difficulty=1,
    verified=True,
)  # test_case_block_102
# noinspection PyArgumentList
test_case_block_103 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="The dog's rice",
    subtitle_2="Sir, I will let your dad go if you eat\nthe dog's rice now",
    verified=True,
)  # test_case_block_103
# noinspection PyArgumentList
test_case_block_104 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="What's the matter?",
    subtitle_2="Come on",
    verified=True,
)  # test_case_block_104
# noinspection PyArgumentList
test_case_block_105 = EnglishProofTestCase.get_test_case_cls(7)(
    subtitle_1="Chan, don't eat that",
    subtitle_2="You can't face the\nothers if you eat this",
    subtitle_3="Let's forget about me",
    subtitle_4="Sir, I was a general in Canton",
    subtitle_5="So what?",
    subtitle_6="Stop fighting",
    subtitle_7="Stand properly",
    verified=True,
)  # test_case_block_105
# noinspection PyArgumentList
test_case_block_106 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="The Scholar eats the dog's food",
    subtitle_2="It's quite delicious",
    subtitle_3="Try some. Come on",
    verified=True,
)  # test_case_block_106
# noinspection PyArgumentList
test_case_block_107 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="It's delicious, isn't it?",
    verified=True,
)  # test_case_block_107
# noinspection PyArgumentList
test_case_block_108 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="Dad, look!",
    subtitle_2="There is a slice of meat here",
    subtitle_3="It's pock chop!",
    revised_3="It's pork chop!",
    note_3="Corrected 'pock chop' to 'pork chop'.",
    difficulty=1,
    verified=True,
)  # test_case_block_108
# noinspection PyArgumentList
test_case_block_109 = EnglishProofTestCase.get_test_case_cls(9)(
    subtitle_1="They are as hungry as dogs!",
    subtitle_2="Enjoy the dog food!",
    subtitle_3="Hurry, finish it",
    subtitle_4="That's too delicious!",
    subtitle_5="I want to save it\nfor midnight snack",
    subtitle_6="It's very clever of you!",
    subtitle_7="You deserve to be beggars",
    subtitle_8="The Scholar is eating dog's food",
    subtitle_9="Come on, let's go and\neat the man's food",
    revised_8="The Scholar is eating dog food",
    note_8="Changed 'dog's food' to 'dog food' for natural phrasing.",
    difficulty=1,
    verified=True,
)  # test_case_block_109
# noinspection PyArgumentList
test_case_block_110 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Uncle So!",
    verified=True,
)  # test_case_block_110
# noinspection PyArgumentList
test_case_block_111 = EnglishProofTestCase.get_test_case_cls(13)(
    subtitle_1="You are...",
    subtitle_2="My dad was the Master of the\nBeggar's Association",
    subtitle_3="Why don't you join our Beggar's\nAssociation",
    subtitle_4="Uncle Mok, isn't it a good idea?",
    subtitle_5="Good",
    subtitle_6="Isn't it the association\nfor beggars?",
    subtitle_7="Yes!",
    subtitle_8="That's right,\nwe are being beggars",
    subtitle_9="It's wise to join the Beggars' Association\nso as to be taken care",
    subtitle_10="Chan...\nwhere is that fool going?",
    subtitle_11="Where is Chan?",
    subtitle_12="OK, we will join you!",
    subtitle_13="Chan... Chan...",
    revised_2="My dad was the Master of the\nBeggars' Association",
    note_2="Changed 'Beggar's Association' to 'Beggars' Association' for "
    "consistency and correct plural possessive.",
    revised_3="Why don't you join our Beggars'\nAssociation?",
    note_3="Changed 'Beggar's Association' to 'Beggars' Association' and "
    "added a question mark.",
    revised_9="It's wise to join the Beggars' Association\nso as to be taken care of",
    note_9="Changed 'Beggars' Association' for consistency and added "
    "'of' to complete the phrase 'taken care of'.",
    difficulty=1,
    verified=True,
)  # test_case_block_111
# noinspection PyArgumentList
test_case_block_112 = EnglishProofTestCase.get_test_case_cls(26)(
    subtitle_1="Yushang, good year!",
    subtitle_2="Uncle Mok, happy new year!",
    subtitle_3="This is for you",
    subtitle_4="Thank you",
    subtitle_5="One clothe is for you",
    subtitle_6="and the other is for Chan",
    subtitle_7="Thank you. Put it down first",
    subtitle_8="Do you have any coins?",
    subtitle_9="Yes!",
    subtitle_10="Give them to me, come on",
    subtitle_11="What for?",
    subtitle_12="It's new year,",
    subtitle_13="you should receive red pocket",
    subtitle_14="Come on, happy new year",
    subtitle_15="Good year!",
    subtitle_16="Wish you ever beauty",
    subtitle_17="Thank you...",
    subtitle_18="Uncle Mok, we needn't give red\npocket to each other",
    subtitle_19="How about Chan",
    subtitle_20="Chan?",
    subtitle_21="He is still sleeping",
    subtitle_22="Don't wake him up",
    subtitle_23="I will cook you some new year cake",
    subtitle_24="Let me help you",
    subtitle_25="How can he sleep on the\n1st day of this year?",
    subtitle_26="He is useless",
    revised_5="One cloth is for you",
    note_5="Changed 'clothe' to 'cloth'.",
    revised_13="you should receive a red packet",
    note_13="Changed 'red pocket' to 'red packet' and added 'a'.",
    revised_16="Wish you everlasting beauty",
    note_16="Changed 'ever beauty' to 'everlasting beauty'.",
    revised_18="Uncle Mok, we don't need to give red\npackets to each other",
    note_18="Changed 'needn't' to 'don't need to' and 'red pocket' to 'red packets'.",
    revised_23="I will cook you some New Year cake",
    note_23="Capitalized 'New Year'.",
    revised_25="How can he sleep on the\nfirst day of the year?",
    note_25="Changed '1st day of this year' to 'first day of the year' "
    "for clarity and natural phrasing.",
    difficulty=1,
    verified=True,
)  # test_case_block_112
# noinspection PyArgumentList
test_case_block_113 = EnglishProofTestCase.get_test_case_cls(21)(
    subtitle_1="Are you all here?",
    subtitle_2="To fight against Chiu, we need a union of\nthe Beggar's Association",
    subtitle_3="So we must choose a new master to\nin-charge the association",
    subtitle_4="Yushang...",
    subtitle_5="To defeat the Lotus position\nof the three seniors",
    subtitle_6="You should try your best",
    subtitle_7="Uncle, I don't have\nfaith to defeat them",
    subtitle_8="Judging from my kung-fu now,",
    subtitle_9="how can I defeat them and become\nthe new master?",
    subtitle_10="Take this Taiwan pill, after this,\nyour power will be improved",
    subtitle_11="No, this is the only medicine to cure\nyour inner injury",
    subtitle_12="How can I take this?",
    subtitle_13="Don't worry,",
    subtitle_14="you can ask my\nson to fight for you",
    subtitle_15="He was a scholar\nof Martial Arts before...",
    subtitle_16="Before...",
    subtitle_17="Look at him, he is son lazy,",
    subtitle_18="he knows sleeping only",
    subtitle_19="He is not even\nqualified to be beggar!",
    subtitle_20="Don't be that frank, can you?",
    subtitle_21="Don't shout that loudly, OK?",
    revised_2="To fight against Chiu, we need a union of\nthe Beggars' Association",
    note_2="Changed 'Beggar's Association' to 'Beggars' Association' for "
    "correct plural possessive.",
    revised_3="So we must choose a new master to\nbe in charge of the association",
    note_3="Changed 'to in-charge the association' to 'to be in charge "
    "of the association'.",
    revised_5="To defeat the Lotus Position\nof the three seniors",
    note_5="Capitalized 'Position' for consistency as a martial arts term.",
    revised_7="Uncle, I don't have\nfaith that I can defeat them",
    note_7="Added 'that I can' for clarity and natural phrasing.",
    revised_10="Take this Taiwanese pill, after this,\nyour power will be improved",
    note_10="Changed 'Taiwan' to 'Taiwanese'.",
    revised_15="He was a Scholar\nof Martial Arts before...",
    note_15="Capitalized 'Scholar' for consistency with previous usage.",
    revised_17="Look at him, he is so lazy,",
    note_17="Changed 'son lazy' to 'so lazy'.",
    revised_18="he only knows how to sleep",
    note_18="Changed 'he knows sleeping only' to 'he only knows how to "
    "sleep' for natural phrasing.",
    revised_19="He is not even\nqualified to be a beggar!",
    note_19="Added 'a' before 'beggar'.",
    difficulty=1,
    verified=True,
)  # test_case_block_113
# noinspection PyArgumentList
test_case_block_114 = EnglishProofTestCase.get_test_case_cls(9)(
    subtitle_1="Chan, no matter\nhow they despise you,",
    subtitle_2="I have faith on you",
    subtitle_3="Although you lost your power",
    subtitle_4="With your background,",
    subtitle_5="only you try hard,",
    subtitle_6="you can achieve something",
    subtitle_7="But I am now powerless,\nI don't want to fight again",
    subtitle_8="You have power!",
    subtitle_9="Come on, beat me",
    revised_2="I have faith in you",
    note_2="Changed 'faith on you' to 'faith in you'.",
    revised_5="if only you try hard,",
    note_5="Changed 'only you try hard,' to 'if only you try hard,' for "
    "correct phrasing.",
    difficulty=1,
    verified=True,
)  # test_case_block_114
# noinspection PyArgumentList
test_case_block_115 = EnglishProofTestCase.get_test_case_cls(4)(
    subtitle_1="See, that was powerful",
    subtitle_2="Well, being a people...",
    subtitle_3="Forget it, don't waste time",
    subtitle_4="Why don't you let me sleep?",
    revised_2="Well, being a person...",
    note_2="Changed 'people' to 'person' for correct singular usage.",
    difficulty=1,
    verified=True,
)  # test_case_block_115
# noinspection PyArgumentList
test_case_block_116 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="Why did you lock the door?",
    subtitle_2="Enjoy sleeping",
    verified=True,
)  # test_case_block_116
# noinspection PyArgumentList
test_case_block_117 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="Son,",
    subtitle_2="I tried very hard\nto get this for you",
    subtitle_3="Try hard to practise, be good",
    difficulty=1,
    verified=True,
)  # test_case_block_117
# noinspection PyArgumentList
test_case_block_118 = EnglishProofTestCase.get_test_case_cls(4)(
    subtitle_1="Why do you go up?",
    subtitle_2="Even you want me\nto practise Kung-fu,",
    subtitle_3="you should give me a waddy first",
    subtitle_4="I am sorry, catch it",
    revised_2="Even if you want me\nto practise Kung Fu,",
    note_2="Added 'if' for correct conditional phrasing; changed "
    "'Kung-fu' to 'Kung Fu'.",
    difficulty=1,
    verified=True,
)  # test_case_block_118
# noinspection PyArgumentList
test_case_block_119 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="Before being appointed\nimportant task,",
    subtitle_2="God will give you severe\ntraining for soul and flesh.",
    revised_1="Before being appointed to an\nimportant task,",
    note_1="Added 'to an' for correct phrasing.",
    revised_2="God will give you severe\ntraining for your soul and flesh.",
    note_2="Added 'your' for natural phrasing.",
    difficulty=1,
    verified=True,
)  # test_case_block_119
# noinspection PyArgumentList
test_case_block_120 = EnglishProofTestCase.get_test_case_cls(9)(
    subtitle_1="Did you write it?",
    subtitle_2="It's ugly, it's right\nto wipe it away",
    subtitle_3="Hey, beggar?",
    subtitle_4="Yes",
    subtitle_5="Me too",
    subtitle_6="Congratulation",
    subtitle_7="Are there anything to eat?",
    subtitle_8="No",
    subtitle_9="Luckily, I have",
    revised_6="Congratulations",
    note_6="Changed 'Congratulation' to 'Congratulations'.",
    revised_7="Is there anything to eat?",
    note_7="Changed 'Are there anything to eat?' to 'Is there anything "
    "to eat?' for correct grammar.",
    difficulty=1,
    verified=True,
)  # test_case_block_120
# noinspection PyArgumentList
test_case_block_121 = EnglishProofTestCase.get_test_case_cls(19)(
    subtitle_1="See your look,",
    subtitle_2="it's a waste\nfor you not to beg",
    subtitle_3="None of your damn business",
    subtitle_4="You are too lazy to be a beggar!",
    subtitle_5="Your fellows despise you",
    subtitle_6="I was always respected by others",
    subtitle_7="But now, I am despised",
    subtitle_8="Dislike from you,",
    subtitle_9="no one respected me before",
    subtitle_10="Listen to me. Don't go!",
    subtitle_11="I remembered once in Canton",
    subtitle_12="A fool paid my living,\nincluding hooking",
    subtitle_13="What a weird man",
    subtitle_14="Kid, I remembered you",
    subtitle_15="Me too",
    subtitle_16="Hey, hurry up",
    subtitle_17="Repay my money,\nI am in urgent need",
    subtitle_18="If I had money,",
    subtitle_19="I wouldn't be beggar!",
    revised_19="I wouldn't be a beggar!",
    note_19="Added 'a' before 'beggar' for correct grammar.",
    difficulty=1,
    verified=True,
)  # test_case_block_121
# noinspection PyArgumentList
test_case_block_122 = EnglishProofTestCase.get_test_case_cls(30)(
    subtitle_1="But, don't worry,\nyou were my benefitor,",
    subtitle_2="I will repay you one day",
    subtitle_3="Thank you very much",
    subtitle_4="But, you can't buy\nback what you lost",
    subtitle_5="even you have money again",
    subtitle_6="What did I lose?",
    subtitle_7="Pride and faith",
    subtitle_8="And your woman too",
    subtitle_9="What are you?",
    subtitle_10="I am Hung Yat-sun,\nnicked name Old Bag Sun",
    subtitle_11="I am the most senior\none among the beggars",
    subtitle_12="It's good to be beggar",
    subtitle_13="You can do everything you want",
    subtitle_14="You can do the same",
    subtitle_15="Tell me, what do you want?\nI will make your wish come true",
    subtitle_16="I want to be human again",
    subtitle_17="Don't you think you\nare not human like?",
    subtitle_18="Not at all",
    subtitle_19="So you have to be beggar now",
    subtitle_20="Very good! Very good!",
    subtitle_21="But I won't cheat you,\nfrom your head to toes",
    subtitle_22="Every parts of you are beggar like",
    subtitle_23="So what?",
    subtitle_24="That means, you will be beggar\nfor your life",
    subtitle_25="I don't want to talk to you,\nI want a sleep first",
    subtitle_26="Don't go, you can achieve\nin your profession",
    subtitle_27="From my judgement,",
    subtitle_28="you will be the king of beggars",
    subtitle_29="King of beggars,\nwhat does that mean?",
    subtitle_30="That is beggar",
    revised_1="But, don't worry,\nyou were my benefactor,",
    note_1="Corrected 'benefitor' to 'benefactor'.",
    revised_5="even if you have money again",
    note_5="Added 'if' for correct conditional phrasing.",
    revised_10="I am Hung Yat-sun,\nnicknamed Old Bag Sun",
    note_10="Changed 'nicked name' to 'nicknamed'.",
    revised_12="It's good to be a beggar",
    note_12="Added 'a' before 'beggar'.",
    revised_17="Don't you think you\nare not human-like?",
    note_17="Added hyphen to 'human-like'.",
    revised_19="So you have to be a beggar now",
    note_19="Added 'a' before 'beggar'.",
    revised_22="Every part of you is beggar-like",
    note_22="Changed 'Every parts' to 'Every part' and added hyphen to 'beggar-like'.",
    revised_24="That means, you will be a beggar\nfor your life",
    note_24="Added 'a' before 'beggar'.",
    revised_25="I don't want to talk to you,\nI want to sleep first",
    note_25="Changed 'a sleep' to 'to sleep'.",
    revised_30="That is a beggar",
    note_30="Added 'a' before 'beggar'.",
    difficulty=1,
    verified=True,
)  # test_case_block_122
# noinspection PyArgumentList
test_case_block_123 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="I won't care who you are,\nI just want to stop the conversation",
    subtitle_2="Please step aside,\ndon't stop me from sleeping",
    subtitle_3="Damn you!",
    subtitle_4="No... I just want to sleep with you",
    subtitle_5="Idiot!",
    revised_1="I don't care who you are,\nI just want to stop the conversation",
    note_1="Changed 'I won't care' to 'I don't care' for correct tense "
    "and natural phrasing.",
    difficulty=1,
    verified=True,
)  # test_case_block_123
# noinspection PyArgumentList
test_case_block_124 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Kid, see you in the dream",
    difficulty=1,
    verified=True,
)  # test_case_block_124
# noinspection PyArgumentList
test_case_block_125 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="Before the Buddha, the Disciples\nreturns to your position",
    subtitle_2="To suppress the dragon and tight",
    revised_1="Before the Buddha, the disciples\nreturn to your positions",
    note_1="Changed 'Disciples returns' to 'disciples return' and 'your "
    "position' to 'your positions' for subject-verb agreement and "
    "plural consistency.",
    revised_2="To suppress the dragon and tiger",
    note_2="Changed 'tight' to 'tiger' to match the common phrase 'dragon and tiger'.",
    difficulty=1,
    verified=True,
)  # test_case_block_125
# noinspection PyArgumentList
test_case_block_126 = EnglishProofTestCase.get_test_case_cls(7)(
    subtitle_1="So Chan, you enjoyed the\nprosperity of the world",
    subtitle_2="And you tasted the bitter\nfruit of the world too",
    subtitle_3="Now you regretted",
    subtitle_4="On behalf of Master Hung",
    subtitle_5='I appoint you to be the\n"Sleeping Disciple"',
    subtitle_6='Now, I will teach you the\n"Sleeping Disciple\'s Fist"!',
    subtitle_7="Hope you can make good use of it\nCome on",
    revised_3="Now you regret it",
    note_3="Changed 'regretted' to 'regret it' for correct tense and phrasing.",
    revised_7="Hope you can make good use of it.\nCome on",
    note_7="Added a period after 'it' to separate the two sentences.",
    difficulty=1,
    verified=True,
)  # test_case_block_126
# noinspection PyArgumentList
test_case_block_127 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Senior...",
    verified=True,
)  # test_case_block_127
# noinspection PyArgumentList
test_case_block_128 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="The bitter pasted",
    revised_1="The bitter past",
    note_1="Corrected 'pasted' to 'past'.",
    difficulty=1,
    verified=True,
)  # test_case_block_128
# noinspection PyArgumentList
test_case_block_129 = EnglishProofTestCase.get_test_case_cls(4)(
    subtitle_1="Long life to you...",
    subtitle_2="Here comes the white Goat",
    subtitle_3="My mother, give me power",
    subtitle_4="To save the people!",
    revised_2="Here comes the White Goat",
    note_2="Capitalized 'White Goat' as it appears to be a title or name.",
    difficulty=1,
    verified=True,
)  # test_case_block_129
# noinspection PyArgumentList
test_case_block_130 = EnglishProofTestCase.get_test_case_cls(7)(
    subtitle_1="Tomorrow the Emperor\nwill go hunting",
    subtitle_2="I will send him a pretty girl,\nso as to get close to him",
    subtitle_3="Yuen Ling, you should\nseduce him tomorrow",
    subtitle_4="Yes",
    subtitle_5="If we can kill the Emperor,",
    subtitle_6="I can take over his reign",
    subtitle_7="I will give you a share of wealth!",
    verified=True,
)  # test_case_block_130
# noinspection PyArgumentList
test_case_block_131 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="Long life to you",
    subtitle_2="Senior!",
    subtitle_3="Let's go back now",
    verified=True,
)  # test_case_block_131
# noinspection PyArgumentList
test_case_block_132 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="Senior!",
    subtitle_2="Let's go!",
    verified=True,
)  # test_case_block_132
# noinspection PyArgumentList
test_case_block_133 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Senior!",
    verified=True,
)  # test_case_block_133
# noinspection PyArgumentList
test_case_block_134 = EnglishProofTestCase.get_test_case_cls(4)(
    subtitle_1="Let's chase them",
    subtitle_2="Stop\nThe Emperor is setting off soon",
    subtitle_3="You killed woman...",
    subtitle_4="You should replace her to be\na gift to the Emperor!",
    revised_3="You killed a woman...",
    note_3="Added 'a' before 'woman'.",
    revised_4="You should replace her as\na gift to the Emperor!",
    note_4="Changed 'replace her to be' to 'replace her as' for correct usage.",
    difficulty=1,
    verified=True,
)  # test_case_block_134
# noinspection PyArgumentList
test_case_block_135 = EnglishProofTestCase.get_test_case_cls(8)(
    subtitle_1="No one dares come up to fight for\nthe leadership?",
    subtitle_2='Ask Mok to give us the\n"Dog Hitting Waddy"!',
    subtitle_3="Ask that old bag to\nhand us the waddy",
    subtitle_4="Where have they been?",
    subtitle_5="I don't know,",
    subtitle_6="I saw them chat,",
    subtitle_7="then they went away",
    subtitle_8="Are there any affair between them?",
    revised_8="Is there any affair between them?",
    note_8="Changed 'Are there any affair' to 'Is there any affair' for "
    "correct subject-verb agreement.",
    difficulty=1,
    verified=True,
)  # test_case_block_135
# noinspection PyArgumentList
test_case_block_136 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Now, we are going to choose\nthe new leader",
    verified=True,
)  # test_case_block_136
# noinspection PyArgumentList
test_case_block_137 = EnglishProofTestCase.get_test_case_cls(6)(
    subtitle_1="Uncle Mok...",
    subtitle_2="I am scared,",
    subtitle_3="I think you won't come back",
    subtitle_4="How is it? Where is sister?",
    subtitle_5="Your sister is caught by Chiu",
    subtitle_6="We'd find someone to compete\nfor the leadership",
    revised_4="How is it? Where is my sister?",
    note_4="Changed 'sister' to 'my sister'.",
    revised_6="We need to find someone to compete\nfor the leadership",
    note_6="Changed 'We'd find' to 'We need to find' for correct meaning and grammar.",
    difficulty=1,
    verified=True,
)  # test_case_block_137
# noinspection PyArgumentList
test_case_block_138 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Who should go?",
    verified=True,
)  # test_case_block_138
# noinspection PyArgumentList
test_case_block_139 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="I'll do it",
    subtitle_2="Uncle Mok",
    subtitle_3="Why don't you let me try?",
    verified=True,
)  # test_case_block_139
# noinspection PyArgumentList
test_case_block_140 = EnglishProofTestCase.get_test_case_cls(7)(
    subtitle_1="Chan,",
    subtitle_2="you are not qualified, come down",
    subtitle_3="Since you don't have a good candidate,\nI'll give you some advantage",
    subtitle_4="Chan, it's not a game",
    subtitle_5="You will be killed, come down",
    subtitle_6="It doesn't matter, I have forgotten\nmy life already",
    subtitle_7="Bull shit, throw him to death",
    revised_7="Bullshit, throw him to his death",
    note_7="Changed 'Bull shit' to 'Bullshit' and 'throw him to death' "
    "to 'throw him to his death' for correct usage.",
    difficulty=1,
    verified=True,
)  # test_case_block_140
# noinspection PyArgumentList
test_case_block_141 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Well, I will make\nyour wish come true",
    verified=True,
)  # test_case_block_141
# noinspection PyArgumentList
test_case_block_142 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="What is he doing?",
    subtitle_2="Sleeping",
    verified=True,
)  # test_case_block_142
# noinspection PyArgumentList
test_case_block_143 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="Isn't this stance...",
    subtitle_2="Uncle Sun's \"Sleeping Disciple's Fists'?",
    subtitle_3="Set the position!",
    revised_2="Uncle Sun's \"Sleeping Disciple's Fists\"?",
    note_2="Corrected quotes.",
    difficulty=1,
    verified=True,
)  # test_case_block_143
# noinspection PyArgumentList
test_case_block_144 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Is it dawn?",
    verified=True,
)  # test_case_block_144
# noinspection PyArgumentList
test_case_block_145 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="I am sorry!",
    subtitle_2="I won",
    subtitle_3="What is the use for defeating us?",
    subtitle_4='You don\'t know how to use the\n"Dog Hitting Waddy".',
    subtitle_5="You are not qualified to be\nthe leader of us",
    revised_3="What is the use of defeating us?",
    note_3="Changed 'for' to 'of' for correct phrasing.",
    revised_5="You are not qualified to be our leader",
    note_5="Changed 'the leader of us' to 'our leader' for natural phrasing.",
    difficulty=1,
    verified=True,
)  # test_case_block_145
# noinspection PyArgumentList
test_case_block_146 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1='"Dog Hitting Waddy"?',
    difficulty=1,
    verified=True,
)  # test_case_block_146
# noinspection PyArgumentList
test_case_block_147 = EnglishProofTestCase.get_test_case_cls(4)(
    subtitle_1="It's for hitting dogs",
    subtitle_2="I do know how to use this waddy!",
    subtitle_3="But it's dislike\nfrom the standard stances!",
    subtitle_4="It's quite powerful!",
    revised_3="But it's different\nfrom the standard stances!",
    note_3="Changed 'dislike' to 'different' for correct meaning.",
    difficulty=1,
    verified=True,
)  # test_case_block_147
# noinspection PyArgumentList
test_case_block_148 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="He broke the waddy!",
    subtitle_2="He broke the treasure of our Association,\nlet's kill him!",
    verified=True,
)  # test_case_block_148
# noinspection PyArgumentList
test_case_block_149 = EnglishProofTestCase.get_test_case_cls(33)(
    subtitle_1="I am Master Hung,\nwho dares go against me?",
    subtitle_2="I set the rules of the association",
    subtitle_3="Any student who defeated\nthe Lotus Position",
    subtitle_4="could be the leader",
    subtitle_5="Have you all forgotten?",
    subtitle_6="We becomes the\nbiggest association",
    subtitle_7="because of being united",
    subtitle_8='I left you the\n"Dog Hitting Waddy",',
    subtitle_9="is just for memory",
    subtitle_10="The waddy is meaningless",
    subtitle_11="But you fools take\nthis as treasure",
    subtitle_12="And fight among yourselves for\nthis damn waddy!",
    subtitle_13="In these five years, you have had no\nleader, don't you feel shy?",
    subtitle_14="So Chan broke the waddy,",
    subtitle_15="so you won't fight\nfor this anymore",
    subtitle_16="He is correct to do so",
    subtitle_17="This youngster is so junior,",
    subtitle_18="but he is a genius, a smart ass",
    subtitle_19="He is being taught by my disciple\nHung Yat Sun",
    subtitle_20="Who doesn't respect him is going\nagainst me too",
    subtitle_21="You should respect him,",
    subtitle_22="your new leader,\nand you'd love him,",
    subtitle_23="whole-heartedly, to care much for him,\nmaybe, treat him dinner",
    subtitle_24="Then, although I am in heaven,",
    subtitle_25="I will bless all of you,\nall the best",
    subtitle_26="Isn't it true?",
    subtitle_27="You'd better trust it",
    subtitle_28="Master Hung's soul talked to us,",
    subtitle_29="we are blessed",
    subtitle_30="They are easily to be cheated,\nI am really a genius!",
    subtitle_31="We'll have better living",
    subtitle_32="What happened?",
    subtitle_33="Let's greet the new Master",
    revised_3="Any student who defeats\nthe Lotus Position",
    note_3="Changed 'defeated' to 'defeats' for correct tense agreement.",
    revised_6="We became the\nbiggest association",
    note_6="Changed 'becomes' to 'became' for correct tense.",
    revised_9="is just for remembrance",
    note_9="Changed 'for memory' to 'for remembrance' for natural phrasing.",
    revised_13="In these five years, you have had no\nleader. Don't you feel ashamed?",
    note_13="Changed 'don't you feel shy?' to 'Don't you feel ashamed?' "
    "for natural phrasing and split into two sentences.",
    revised_18="but he is a genius, a smartass",
    note_18="Changed 'smart ass' to 'smartass' (one word, informal slang).",
    revised_20="Whoever doesn't respect him is going\nagainst me too",
    note_20="Changed 'Who doesn't respect him' to 'Whoever doesn't "
    "respect him' for correct grammar.",
    revised_22="your new leader,\nand you should love him,",
    note_22="Changed 'you'd love him' to 'you should love him' for clarity and tone.",
    revised_23="wholeheartedly, care for him,\nmaybe treat him to dinner",
    note_23="Changed 'whole-heartedly, to care much for him, maybe, treat "
    "him dinner' to 'wholeheartedly, care for him, maybe treat "
    "him to dinner' for natural phrasing and removed unnecessary "
    "commas.",
    revised_30="They are easily cheated,\nI am really a genius!",
    note_30="Changed 'easily to be cheated' to 'easily cheated' for correct phrasing.",
    revised_31="We'll have a better life",
    note_31="Changed 'better living' to 'a better life' for natural phrasing.",
    difficulty=1,
    verified=True,
)  # test_case_block_149
# noinspection PyArgumentList
test_case_block_150 = EnglishProofTestCase.get_test_case_cls(10)(
    subtitle_1="You should have faith,\nyou won, bravo...",
    subtitle_2="Uncle Mok, my son is really great!",
    subtitle_3="I can't guess you have learnt the\n\"Sleeping Disciple's Fists\"?!",
    subtitle_4="From now on, you are the new leader of us",
    subtitle_5='This is the book of\n"Dragon Suppressing Stances"',
    subtitle_6="And, I will give you the Taiwan Pill",
    subtitle_7="Hope you will be a good leader",
    subtitle_8="I just want to save Yushang as\nsoon as possible",
    subtitle_9="Yushang didn't make a wrong choice",
    subtitle_10="Bravo! Bravo!",
    revised_3="I can't believe you have learnt the\n\"Sleeping Disciple's Fists\"?!",
    note_3="Changed 'guess' to 'believe'.",
    revised_4="From now on, you are our new leader",
    note_4="Changed 'the new leader of us' to 'our new leader' for natural phrasing.",
    difficulty=1,
    verified=True,
)  # test_case_block_150
# noinspection PyArgumentList
test_case_block_151 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="Uncle Mok, how are you?",
    subtitle_2="Uncle Mok!",
    subtitle_3="Uncle Mok...",
    verified=True,
)  # test_case_block_151
# noinspection PyArgumentList
test_case_block_152 = EnglishProofTestCase.get_test_case_cls(12)(
    subtitle_1="Do you understand everything",
    subtitle_2="written in this book?",
    subtitle_3="Don't think that I am so foolish",
    subtitle_4="After getting the\nhelp of Taiwan Pill",
    subtitle_5="My initial power is increased",
    subtitle_6="I can control the 17th stances",
    subtitle_7="But the last stance,",
    subtitle_8="there is no picture\nor description of it",
    subtitle_9="I can't understand at all",
    subtitle_10="But Uncle Mok is dead, what'll we do now?",
    subtitle_11="Just go ahead",
    subtitle_12="No matter how, I have to save\nYushang first",
    revised_6="I can control the first 17 stances",
    note_6="Changed '17th' to 'first 17'.",
    difficulty=1,
    verified=True,
)  # test_case_block_152
# noinspection PyArgumentList
test_case_block_153 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="Check whether the camp is ready or not?",
    subtitle_2="Yes!",
    verified=True,
)  # test_case_block_153
# noinspection PyArgumentList
test_case_block_154 = EnglishProofTestCase.get_test_case_cls(13)(
    subtitle_1="Chiu,",
    subtitle_2="why do you bring this woman here?",
    subtitle_3="I know the Emperor\nloves pretty woman",
    subtitle_4="So I want to send him this gift",
    subtitle_5="And I want to meet him too",
    subtitle_6="There is no order from the Emperor",
    subtitle_7="Men, come and take\nthis woman to the camp",
    subtitle_8="Yes",
    subtitle_9="Go!",
    subtitle_10="Sir, you look great!",
    subtitle_11="I think you should go back",
    subtitle_12="to your own position",
    subtitle_13="Yes",
    revised_3="I know the Emperor\nloves pretty women",
    note_3="Changed 'woman' to 'women' for correct plural usage.",
    difficulty=1,
    verified=True,
)  # test_case_block_154
# noinspection PyArgumentList
test_case_block_155 = EnglishProofTestCase.get_test_case_cls(6)(
    subtitle_1="Your Majesty,",
    subtitle_2="Officer Chiu brings this woman to you",
    subtitle_3="Woman?",
    subtitle_4="Chiu knows my hobby!",
    subtitle_5="I want to take a bath first,\nbring her to me later",
    subtitle_6="Yes",
    verified=True,
)  # test_case_block_155
# noinspection PyArgumentList
test_case_block_156 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="This bastard wants\nto see the Emperor,",
    subtitle_2="if I let him see His Majesty oftenly,\nmy post will be taken away",
    revised_2="if I let him see His Majesty often,\nmy post will be taken away",
    note_2="Changed 'oftenly' to 'often'.",
    difficulty=1,
    verified=True,
)  # test_case_block_156
# noinspection PyArgumentList
test_case_block_157 = EnglishProofTestCase.get_test_case_cls(4)(
    subtitle_1="Men",
    subtitle_2="Sir",
    subtitle_3="Check what had happened",
    subtitle_4="Yes",
    revised_3="Check what has happened",
    note_3="Changed 'had happened' to 'has happened' for correct tense.",
    difficulty=1,
    verified=True,
)  # test_case_block_157
# noinspection PyArgumentList
test_case_block_158 = EnglishProofTestCase.get_test_case_cls(6)(
    subtitle_1="Sir, there are many people coming\nfrom the forest",
    subtitle_2="Who are they?",
    subtitle_3="I don't know!",
    subtitle_4="Release the alarm smoke",
    subtitle_5="Be alert",
    subtitle_6="Yes",
    verified=True,
)  # test_case_block_158
# noinspection PyArgumentList
test_case_block_159 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="There is smoke ahead,\nlet's get armed",
    subtitle_2="Yes",
    verified=True,
)  # test_case_block_159
# noinspection PyArgumentList
test_case_block_160 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Damn you beggars",
    verified=True,
)  # test_case_block_160
# noinspection PyArgumentList
test_case_block_161 = EnglishProofTestCase.get_test_case_cls(10)(
    subtitle_1="So Chan, what are you doing?",
    subtitle_2="Nothing, I just want\nto beg for money",
    subtitle_3="Shit, do you want to be killed",
    subtitle_4="It's you who will be killed",
    subtitle_5="Chiu wants to raise a rebel,",
    subtitle_6="he is going to\nassassinate the king",
    subtitle_7="You fat-headed",
    subtitle_8="Who do you think you are?",
    subtitle_9="How dare you frame the courtier?",
    subtitle_10="I will kill you if you step forward",
    revised_3="Shit, do you want to get killed?",
    note_3="Changed 'be killed' to 'get killed' for natural phrasing and "
    "added a question mark.",
    revised_7="You fathead!",
    note_7="Changed 'fat-headed' to 'fathead' and added exclamation mark "
    "for natural insult.",
    difficulty=1,
    verified=True,
)  # test_case_block_161
# noinspection PyArgumentList
test_case_block_162 = EnglishProofTestCase.get_test_case_cls(19)(
    subtitle_1="Chan, how can we fight with them?",
    subtitle_2="- Senior\n- Yes",
    subtitle_3="Where are the rest of our men?",
    subtitle_4="They are coming",
    subtitle_5="We have no time,",
    subtitle_6="you stay here to wait for the others",
    subtitle_7="I will go first",
    subtitle_8="I will follow",
    subtitle_9="Be serious",
    subtitle_10="Master, don't worry",
    subtitle_11="Am I going to die?",
    subtitle_12="Say something lucky, OK?",
    subtitle_13="Sure! Happy birthday to you...",
    subtitle_14="Happy birthday to you...",
    subtitle_15="Happy birthday to you...",
    subtitle_16="That's enough",
    subtitle_17="I haven't finished",
    subtitle_18="Go on after I left",
    subtitle_19="Sure",
    revised_18="Go on after I've left",
    note_18="Changed 'I left' to 'I've left' for correct tense.",
    difficulty=1,
    verified=True,
)  # test_case_block_162
# noinspection PyArgumentList
test_case_block_163 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="There is smoke ahead,\nsomeone must have alarmed them",
    verified=True,
)  # test_case_block_163
# noinspection PyArgumentList
test_case_block_164 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="Get ready the Unicom Smoke",
    subtitle_2="Yes",
    subtitle_3="Attack the main camp",
    revised_1="Get the Kirin Smokes ready",
    note_1="Changed word order for natural phrasing; corrected 'Unicom "
    "Smoke' to 'Kirin Smokes'.",
    difficulty=3,
    verified=True,
)  # test_case_block_164
# noinspection PyArgumentList
test_case_block_165 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1="Rebel! Help!",
    subtitle_2="They should be killed",
    subtitle_3="The one who didn't kill you\nshould be killed",
    subtitle_4="Shit, the poisoned smoke",
    subtitle_5="is blowing to the Royal camp",
    revised_5="is blowing toward the Royal camp",
    note_5="Changed 'to' to 'toward' for natural phrasing.",
    difficulty=1,
    verified=True,
)  # test_case_block_165
# noinspection PyArgumentList
test_case_block_166 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="No, the wind direction changed",
    subtitle_2="Yes, wait for me",
    subtitle_3="If the beggars don't retreat now,\nwe will kill with no mercy",
    revised_3="If the beggars don't retreat now,\nwe will kill without mercy",
    note_3="Changed 'with no mercy' to 'without mercy' for natural phrasing.",
    difficulty=1,
    verified=True,
)  # test_case_block_166
# noinspection PyArgumentList
test_case_block_167 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Have a look",
    verified=True,
)  # test_case_block_167
# noinspection PyArgumentList
test_case_block_168 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="The Unicom Smoke of\nthe Tin Li Sect",
    revised_1="The Kirin Smokes of\nthe Tin Li Sect",
    note_1="Corrected 'Unicom Smoke' to 'Kirin Smokes'.",
    difficulty=3,
    verified=True,
)  # test_case_block_168
# noinspection PyArgumentList
test_case_block_169 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="Be calm, urine is the antidote\nto the poison",
    subtitle_2="Come and piss",
    verified=True,
)  # test_case_block_169
# noinspection PyArgumentList
test_case_block_170 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="How about me?",
    subtitle_2="Don't worry,\nI can give you some urine",
    subtitle_3="Come on, hold it",
    verified=True,
)  # test_case_block_170
# noinspection PyArgumentList
test_case_block_171 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Rush in!",
    verified=True,
)  # test_case_block_171
# noinspection PyArgumentList
test_case_block_172 = EnglishProofTestCase.get_test_case_cls(12)(
    subtitle_1="How is the situation?",
    subtitle_2="Thanks for Your Majesty's luck,\nthe wind direction changed",
    subtitle_3="The smoke is going\nto the other direction",
    subtitle_4="How about our armies?",
    subtitle_5="They are all dead",
    subtitle_6="Take me the sword",
    subtitle_7="Don't... don't!",
    subtitle_8="Get lost! Get lost!",
    subtitle_9="Your Majesty, it's dangerous,\ndon't go!",
    subtitle_10="Get lost, don't you want\nto wait for death, get lost",
    subtitle_11="You are ordered to get away",
    subtitle_12="You can't go!",
    revised_2="Thanks to Your Majesty's luck,\nthe wind direction changed",
    note_2="Changed 'for' to 'to' for correct expression: 'Thanks to "
    "Your Majesty's luck'.",
    revised_3="The smoke is going\nin the other direction",
    note_3="Changed 'to' to 'in' for correct phrasing: 'going in the other direction'.",
    revised_6="Bring me the sword",
    note_6="Changed 'Take me the sword' to 'Bring me the sword' for natural phrasing.",
    revised_10="Get lost! Don't you want\nto wait for death? Get lost!",
    note_10="Added question mark and split for clarity and punctuation.",
    difficulty=1,
    verified=True,
)  # test_case_block_172
# noinspection PyArgumentList
test_case_block_173 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Protect me",
    verified=True,
)  # test_case_block_173
# noinspection PyArgumentList
test_case_block_174 = EnglishProofTestCase.get_test_case_cls(16)(
    subtitle_1="Chan?",
    subtitle_2="Yushang",
    subtitle_3="How did you get here?",
    subtitle_4="It's a long story",
    subtitle_5="We left our base last night",
    subtitle_6="We reached the Great Wall",
    subtitle_7="this morning",
    subtitle_8="We stayed one hour for lunch",
    subtitle_9="I pissed once",
    subtitle_10="Really?",
    subtitle_11="Yes, then I want to\neat a sweet potato",
    subtitle_12="But only dumpling left",
    subtitle_13="You know, I don't\nlike eating dumpling",
    subtitle_14="I am late to save you,\nplease forgive me",
    subtitle_15="To protect to Emperor",
    subtitle_16="Yes",
    revised_11="Yes, then I wanted to\neat a sweet potato",
    note_11="Changed 'want' to 'wanted' for correct tense.",
    revised_12="But only dumplings were left",
    note_12="Changed 'dumpling' to 'dumplings' and added 'were' for "
    "grammatical correctness.",
    revised_13="You know, I don't\nlike eating dumplings",
    note_13="Changed 'dumpling' to 'dumplings' for consistency.",
    revised_15="To protect the Emperor",
    note_15="Changed 'to Emperor' to 'the Emperor'.",
    difficulty=1,
    verified=True,
)  # test_case_block_174
# noinspection PyArgumentList
test_case_block_175 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="You betrayer!",
    subtitle_2="Catch him",
    revised_1="You traitor!",
    note_1="Changed 'betrayer' to 'traitor' for natural English usage.",
    difficulty=1,
    verified=True,
)  # test_case_block_175
# noinspection PyArgumentList
test_case_block_176 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Your Majesty",
    verified=True,
)  # test_case_block_176
# noinspection PyArgumentList
test_case_block_177 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="You bastard, give your kingdom to me",
    subtitle_2="Are you telling him?",
    verified=True,
)  # test_case_block_177
# noinspection PyArgumentList
test_case_block_178 = EnglishProofTestCase.get_test_case_cls(4)(
    subtitle_1="It's you",
    subtitle_2="Yes, I am Beggar So",
    subtitle_3="Why don't you sleep in your hut?",
    subtitle_4="Well, I am a little bit sleepy",
    verified=True,
)  # test_case_block_178
# noinspection PyArgumentList
test_case_block_179 = EnglishProofTestCase.get_test_case_cls(5)(
    subtitle_1='"Sleeping Disciple"?',
    subtitle_2="Yes. Look at you, you are\nlike beggar too",
    subtitle_3="Are you interested to join us?",
    subtitle_4="I can't guess you could recover!",
    subtitle_5="Yes, it's all because of you",
    revised_2="Yes. Look at you, you are\nlike a beggar too",
    note_2="Added 'a' before 'beggar'.",
    revised_4="I couldn't have guessed you would recover!",
    note_4="Changed 'can't guess you could' to 'couldn't have guessed "
    "you would' for correct tense and natural phrasing.",
    difficulty=1,
    verified=True,
)  # test_case_block_179
# noinspection PyArgumentList
test_case_block_180 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Did you generate all your force?\nI didn't",
    revised_1="Did you use all your force?\nI didn't",
    note_1="Changed 'generate' to 'use' for natural phrasing.",
    difficulty=1,
    verified=True,
)  # test_case_block_180
# noinspection PyArgumentList
test_case_block_181 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1='Fool, only the "Dragon Suppressing\nStances" scare me',
    subtitle_2="I won't give a damn\nto any other stances",
    revised_2="I don't give a damn\nabout any other stances",
    note_2="Changed 'I won't give a damn to any other stances' to 'I "
    "don't give a damn about any other stances' for correct "
    "idiomatic usage.",
    difficulty=1,
    verified=True,
)  # test_case_block_181
# noinspection PyArgumentList
test_case_block_182 = EnglishProofTestCase.get_test_case_cls(10)(
    subtitle_1='"Dragon Suppress Stances"',
    subtitle_2='"Dragon in the sky"',
    subtitle_3='"Dragon swings its tail"',
    subtitle_4='"Dragon steals the heart"',
    subtitle_5="Dragon swims,\ndragon in the field,",
    subtitle_6="dragon dances...",
    subtitle_7="Dragon's descendant,",
    subtitle_8="dragon's wish...",
    subtitle_9="Dragon's spirit, dragon's couple",
    subtitle_10="Finished",
    revised_9="Dragon's spirit, dragon's mate",
    note_9="Changed 'couple' to 'mate' for a more natural phrase in this context.",
    difficulty=1,
    verified=True,
)  # test_case_block_182
# noinspection PyArgumentList
test_case_block_183 = EnglishProofTestCase.get_test_case_cls(4)(
    subtitle_1="You can't finish the last stance,",
    subtitle_2="you can defeat me",
    subtitle_3="after learning the 18th stance",
    subtitle_4="But you have no chance",
    verified=True,
)  # test_case_block_183
# noinspection PyArgumentList
test_case_block_184 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Chan!",
    verified=True,
)  # test_case_block_184
# noinspection PyArgumentList
test_case_block_185 = EnglishProofTestCase.get_test_case_cls(3)(
    subtitle_1="I've got it\nJust mix the 17 stances,",
    subtitle_2="it's the 18th stance then",
    subtitle_3="I am too smart!",
    revised_1="I've got it!\nJust mix the 17 stances,",
    note_1="Added exclamation mark for natural speech.",
    revised_2="Then it's the 18th stance",
    note_2="Reordered for natural phrasing and removed 'then' from the end.",
    difficulty=1,
    verified=True,
)  # test_case_block_185
# noinspection PyArgumentList
test_case_block_186 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1='The 18 stance, "It\'s a regret to\nkill the Dragon"!',
    revised_1='The 18th stance, "It\'s a regret to\nkill the Dragon"!',
    note_1="Changed '18 stance' to '18th stance' for correct ordinal usage.",
    difficulty=1,
    verified=True,
)  # test_case_block_186
# noinspection PyArgumentList
test_case_block_187 = EnglishProofTestCase.get_test_case_cls(6)(
    subtitle_1="Chan, are you alright?",
    subtitle_2="See, don't you\nthink I am alright?",
    subtitle_3="Your post is really smart",
    subtitle_4="But your look is awful!",
    subtitle_5="Idiot, I am fine",
    subtitle_6="I can marry tonight",
    revised_3="Your pose is really smart",
    note_3="Changed 'post' to 'pose'.",
    difficulty=1,
    verified=True,
)  # test_case_block_187
# noinspection PyArgumentList
test_case_block_188 = EnglishProofTestCase.get_test_case_cls(9)(
    subtitle_1="Sister!",
    subtitle_2="Tracy!",
    subtitle_3="Where is Chiu?",
    subtitle_4="He is around",
    subtitle_5="Around?",
    subtitle_6="He became ash",
    subtitle_7="Damn it!",
    subtitle_8="Master",
    subtitle_9="Chiu's fellows are\nall caught by us",
    revised_6="He became ashes",
    note_6="Changed 'ash' to 'ashes' for correct usage.",
    revised_9="Chiu's fellows have\nall been caught by us",
    note_9="Changed 'are all caught' to 'have all been caught' for correct tense.",
    difficulty=1,
    verified=True,
)  # test_case_block_188
# noinspection PyArgumentList
test_case_block_189 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="Thank you, buddies",
    verified=True,
)  # test_case_block_189
# noinspection PyArgumentList
test_case_block_190 = EnglishProofTestCase.get_test_case_cls(8)(
    subtitle_1="Yushang",
    subtitle_2="We have an agreement,\ndo you remember?",
    subtitle_3="Yes, be the top of all",
    subtitle_4="Invincible",
    subtitle_5="But, I can't be the Scholar",
    subtitle_6="But I don't like Scholar at all",
    subtitle_7="I love beggar",
    subtitle_8="You first, I will go after you",
    revised_6="But I don't like to be the Scholar at all",
    note_6="Changed 'Scholar' to 'to be a Scholar'",
    revised_7="I love to be a beggar",
    note_7="Changed 'beggar' to 'to be a beggar'.",
    difficulty=2,
    verified=True,
)  # test_case_block_190
# noinspection PyArgumentList
test_case_block_191 = EnglishProofTestCase.get_test_case_cls(9)(
    subtitle_1="Seng-ko-lin-ch'in,\nyou are really a fool",
    subtitle_2="You bring a thief to harm me",
    subtitle_3="Now, you are titled to be a beggar",
    subtitle_4="You have potential to be beggar",
    subtitle_5="Report duty in the temple tomorrow",
    subtitle_6="If there anyone bullies you,\njust tell them my name",
    subtitle_7="Thank you, thank you master",
    subtitle_8="So Chan, what do you want as reward?",
    subtitle_9="Don't you have anything to tell me?",
    revised_3="Now, you are entitled to be a beggar",
    note_3="Changed 'titled' to 'entitled'.",
    revised_4="You have potential to be a beggar",
    note_4="Added 'a' before 'beggar'.",
    revised_6="If anyone bullies you,\njust tell them my name",
    note_6="Removed 'there' for correct phrasing.",
    difficulty=1,
    verified=True,
)  # test_case_block_191
# noinspection PyArgumentList
test_case_block_192 = EnglishProofTestCase.get_test_case_cls(23)(
    subtitle_1="Nothing special, let's go",
    subtitle_2="Mister So!",
    subtitle_3="Put it down",
    subtitle_4="Although you have saved me,",
    subtitle_5="if you don't respect me, I will kill you",
    subtitle_6="If so, you needn't\nsquat and talk to me",
    subtitle_7="Don't move, it'll\nattract their attention",
    subtitle_8="Actually we have no relation,",
    subtitle_9="we have nothing to chat",
    subtitle_10="You have billions of fellows",
    subtitle_11="Your force makes me worry",
    subtitle_12="The number of fellow doesn't\ndepend on me,",
    subtitle_13="but you",
    subtitle_14="What?",
    subtitle_15="If you are great, making the\nsociety peace and wealthy,",
    subtitle_16="no one wishes to be beggar, right?",
    subtitle_17="It's reasonable",
    subtitle_18="Be smart",
    subtitle_19="But,",
    subtitle_20="give me some face",
    subtitle_21="Yes",
    subtitle_22="Long life to Your Majesty",
    subtitle_23="Get up",
    revised_6="If so, you needn't\nsquat to talk to me",
    note_6="Changed 'squat and talk to me' to 'squat to talk to me' for "
    "natural phrasing.",
    revised_9="we have nothing to chat about",
    note_9="Added 'about' to complete the phrase 'chat about'.",
    revised_12="The number of fellows doesn't\ndepend on me,",
    note_12="Changed 'fellow' to 'fellows' for subject-verb agreement: "
    "'number of fellows'.",
    revised_15="If you are great, making the\nsociety peaceful and wealthy,",
    note_15="Changed 'peace and wealthy' to 'peaceful and wealthy'.",
    revised_16="no one wishes to be a beggar, right?",
    note_16="Added 'a' before 'beggar'.",
    difficulty=1,
    verified=True,
)  # test_case_block_192
# noinspection PyArgumentList
test_case_block_193 = EnglishProofTestCase.get_test_case_cls(15)(
    subtitle_1="Pal, do you know me?",
    subtitle_2="Of course! You beggar",
    subtitle_3="You beg with your girl, you think I'll\ngive you money out of mercy?",
    subtitle_4="Yes, please give me money",
    subtitle_5="No mercy, go away",
    subtitle_6="No, you should pay me",
    subtitle_7="It's a must, pal",
    subtitle_8="A must? Kidding?",
    subtitle_9="It's true, be quick",
    subtitle_10="It's bad luck to meet you",
    subtitle_11="Stop",
    subtitle_12="What?",
    subtitle_13="See my family? Give more",
    subtitle_14="How much?",
    subtitle_15="Not less than a thousand, got me?",
    verified=True,
)  # test_case_block_193
# noinspection PyArgumentList
test_case_block_194 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="Say thank you now",
    subtitle_2="Thank you, uncle",
    verified=True,
)  # test_case_block_194
# noinspection PyArgumentList
test_case_block_195 = None  # test_case_block_195

kob_english_proof_test_cases: list[EnglishProofTestCase] = [
    test_case
    for name, test_case in globals().items()
    if name.startswith("test_case_block_") and test_case is not None
]
"""KOB English proof test cases."""

__all__ = [
    "kob_english_proof_test_cases",
]
