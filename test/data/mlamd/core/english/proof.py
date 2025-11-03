#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""MLAMD English proof test cases."""

from __future__ import annotations

from scinoephile.core.english.proofing.abcs import EnglishProofTestCase

# noinspection PyArgumentList
test_case_block_0 = EnglishProofTestCase.get_test_case_cls(33)(
    subtitle_1="When Mrs. McBing was in labour...",
    subtitle_2="A pan appeared in the sky.",
    subtitle_3="It flied along Garden Street...",
    subtitle_4="Turned left, and stopped\n"
               "at the Beef ball King.",
    subtitle_5="Correction:",
    subtitle_6="It first arrived at the Market Building...",
    subtitle_7="Lingered a bit...Correction:",
    subtitle_8="It flied over the railway, turned right...",
    subtitle_9="And headed directly for the Bazaar.",
    subtitle_10="It flied on...",
    subtitle_11="At last coming into the maternity ward.",
    subtitle_12="There, on the right hand side of\n"
                "Mrs. McBing.",
    subtitle_13="Correction: Left hand side.",
    subtitle_14="The pan stayed.",
    subtitle_15="Mrs. McBing,\n"
                "convinced that this was a miracle,",
    subtitle_16="Made a wish...",
    subtitle_17="Thinking of her soon-to-be-born son.",
    subtitle_18="Please make him\n"
                "a clever and smart boy!",
    subtitle_19="The pan didn't seem to hear her words.",
    subtitle_20="So Mrs. McBing amended her wish:",
    subtitle_21="Or make him a smart businessman?",
    subtitle_22="Or maybe...",
    subtitle_23="Or make him really handsome.",
    subtitle_24="As handsome as Chow Yun Fat or\n"
                "Tony Leung!",
    subtitle_25="The pan didn't respond.",
    subtitle_26="Mrs. McBing, in panic...",
    subtitle_27="Made a final amendment:",
    subtitle_28="Her boy needed not to be\n"
                "smart or handsome",
    subtitle_29="As long as luck be with him!",
    subtitle_30="It's nice to depend on oneself...",
    subtitle_31="But luck is essential still.",
    subtitle_32="Of course Chow and Leung are\n"
                "lucky guys...",
    subtitle_33="But then they are smart too!",
    revised_3="It flew along Garden Street...",
    note_3="Changed 'flied' to 'flew'.",
    revised_4="Turned left, and stopped\n"
              "at the Beefball King.",
    note_4="Changed 'Beef ball' to 'Beefball'.",
    revised_7="Lingered a bit... Correction:",
    note_7="Added a space after ellipsis before 'Correction:'.",
    revised_8="It flew over the railway, turned right...",
    note_8="Changed 'flied' to 'flew'.",
    revised_10="It flew on...",
    note_10="Changed 'flied' to 'flew'.",
    revised_28="Her boy need not be\n"
               "smart or handsome",
    note_28="Changed 'needed not to be' to 'need not be' for correct "
            "phrasing.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_0
# noinspection PyArgumentList
test_case_block_1 = EnglishProofTestCase.get_test_case_cls(13)(
    subtitle_1="Finally, the pan dropped to the floor...",
    subtitle_2="Mrs. McBing,\n"
               "believing her wish granted...",
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
    subtitle_1="\\\"My School\\\"",
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
    subtitle_12="Only 10 minutes walk from\n"
                "the MTR Station!",
    subtitle_13="Spring Flower Kindergarten,\n"
                "good environment...",
    subtitle_14="With white teachers for English class!",
    subtitle_15="White teachers for English class?",
    subtitle_16="Yeah!",
    subtitle_17="Spring Flower offer white teachers!",
    revised_1="\"My School\"",
    note_1="Removed unnecessary escape characters from the quotation "
           "marks.",
    revised_12="Only 10 minutes' walk from\n"
               "the MTR Station!",
    note_12="Added possessive apostrophe to 'minutes'' for correct "
            "phrasing.",
    revised_17="Spring Flower offers white teachers!",
    note_17="Changed 'offer' to 'offers' for subject-verb agreement.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_2
# noinspection PyArgumentList
test_case_block_3 = EnglishProofTestCase.get_test_case_cls(23)(
    subtitle_1="\"We are all happy children...\"",
    subtitle_2="\"Wee sing everyday!\"",
    subtitle_3="\"We learn as we grow...\"",
    subtitle_4="\"We are the flowers of spring!\"",
    subtitle_5="This piggy kid in a rabbit outfit...",
    subtitle_6="Who doesn't look the least\n"
               "like Chow or Leung...",
    subtitle_7="That's me, McDull.",
    subtitle_8="This is my kindergarten.",
    subtitle_9="The headmaster came from\n"
               "the countryside...",
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
    subtitle_21="Children, have you handed in\n"
                "the school fee?",
    subtitle_22="Yes!",
    subtitle_23="Great! Now move to class.",
    revised_2="\"We sing every day!\"",
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
    subtitle_1="You might conclude that\n"
               "this is a shabby school.",
    subtitle_2="But, for me and my mates...",
    subtitle_3="This is the most beautiful paradise!",
    subtitle_4="...Also, there is Miss Chan.",
    subtitle_5="Who adores us in\n"
               "her absent-minded way.",
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
    subtitle_47="There are so many things that\n"
                "I don't understand.",
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
    subtitle_3="- Fishball noodle, please.\n"
               "No noodle left.",
    subtitle_4="- Fishball rice noodle then.\n"
               "No fishball left.",
    subtitle_5="Chicken wing noodle then.\n"
               "No noodle left.",
    subtitle_6="How about fishball congee?\n"
               "- No fishball left.",
    subtitle_7="Nothing left today?",
    subtitle_8="How about beef noodle?\n"
               "- No noodle left.",
    subtitle_9="Again?",
    subtitle_10="Fried chicken wing with fishball...\n"
                "No fishball left.",
    subtitle_11="Hey, fishball and noodle are both gone...",
    subtitle_12="You can't combine them with other things.",
    subtitle_13="Can't combine them?",
    subtitle_14="- A bowl of fishball then.\n"
                "- No fishball left.",
    subtitle_15="- A bowl of noodle?\n"
                "- No noodle left.",
    subtitle_16="By now...",
    subtitle_17="you can probably tell how smart I am.",
    subtitle_18="Nothing worried me, all things were fine.",
    subtitle_19="No fishball left? Let's get some noodle.",
    subtitle_20="Shoot, Dull!",
    revised_3="- Fishball noodles, please.\n"
              "- No noodles left.",
    note_3="Changed 'noodle' to 'noodles' for correct plural usage; "
           "added missing hyphen before 'No noodles left.' for "
           "consistency.",
    revised_4="- Fishball rice noodles then.\n"
              "- No fishballs left.",
    note_4="Changed 'noodle' to 'noodles' and 'fishball' to 'fishballs' "
           "for correct plural usage; added missing hyphen for "
           "consistency.",
    revised_5="- Chicken wing noodles then.\n"
              "- No noodles left.",
    note_5="Changed 'noodle' to 'noodles' for correct plural usage.; "
           "added missing hyphens for consistency.",
    revised_6="- How about fishball congee?\n"
              "- No fishballs left.",
    note_6="Changed 'fishball' to 'fishballs' for correct plural usage; "
           "added missing hyphen before 'How about fishball congee?' for "
           "consistency.",
    revised_8="- How about beef noodles?\n"
              "- No noodles left.",
    note_8="Changed 'noodle' to 'noodles' for correct plural usage; "
           "added missing hyphen before 'How about beef noodles?' for "
           "consistency.",
    revised_10="- Fried chicken wing with fishballs...\n"
               "- No fishballs left.",
    note_10="Changed 'fishball' to 'fishballs' for correct plural usage; "
            "added missing hyphens for consistency.",
    revised_14="- A bowl of fishballs then.\n"
               "- No fishballs left.",
    note_14="Changed 'fishball' to 'fishballs' for correct plural usage.",
    revised_15="- A bowl of noodles?\n"
               "- No noodles left.",
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
    subtitle_4="You mean\n"
               "A\\\" ll Things Bright and Beautiful\\\"?",
    subtitle_5="Yes, all are fine!",
    subtitle_6="All things on earth...",
    subtitle_7="They are fine!!",
    revised_4="You mean\n"
              "\"All Things Bright and Beautiful\"?",
    note_4="Removed unnecessary escape characters from the quotation "
           "marks and corrected spacing.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_7
# noinspection PyArgumentList
test_case_block_8 = EnglishProofTestCase.get_test_case_cls(1)(
    subtitle_1="\\\"My Mother\\\"",
    revised_1="\"My Mother\"",
    note_1="Removed unnecessary escape characters from the quotation "
           "marks.",
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
    note_1="Added spaces after commas and corrected ellipsis to three "
           "dots.",
    revised_4="The middle-aged swine is Mrs. McBing,",
    note_4="Added hyphen in 'middle-aged'.",
    difficulty=1,
    prompt=True,
    verified=True,
)  # test_case_block_9
# noinspection PyArgumentList
test_case_block_10 = EnglishProofTestCase.get_test_case_cls(15)(
    subtitle_1="Yes, she is really something.",
    subtitle_2="She works in insurance,\n"
               "real estate and trading.",
    subtitle_3="At the height of IT,\n"
               "she even sets up her cooking site...",
    subtitle_4="www.MrsMcBing.com",
    subtitle_5="Offering brilliant dishes.",
    subtitle_6="Welcome to \"Mrs. Mc Can Cook\".",
    subtitle_7="Today we're doing a simple dish,",
    subtitle_8="Paper Chicken.",
    subtitle_9="Kids at home would love it.",
    subtitle_10="The ingredient: a chicken bun.",
    subtitle_11="Slowly, we tear the paper away\n"
                "from the bun",
    subtitle_12="Now we have a bun paper.",
    subtitle_13="Turn the paper over like this...",
    subtitle_14="Voila! Simple, isn't it?",
    subtitle_15="Thank you, everyone!",
    revised_3="At the height of IT,\n"
              "she even set up her cooking site...",
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
    subtitle_3="First, unwrap the chicken\n"
               "from the paper.",
    subtitle_4="Now we have a paper and\n"
               "a piece of chicken.",
    subtitle_5="Use the bun paper to wrap up\n"
               "the chicken like this...",
    subtitle_6="And then wrap it like this...",
    subtitle_7="The delicious Chicken Bun Paper\n"
               "Bunning a Bun!",
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
    subtitle_13="Every night,\n"
                "she tells me a story before sleep.",
    subtitle_14="Once upon a time, a boy lied. One day...",
    subtitle_15="He died.",
    subtitle_16="Once upon a time, a boy studied hard.",
    subtitle_17="He grew up and got rich.",
    subtitle_18="Once upon a time, a boy was naughty.\n"
                "One day...",
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
    subtitle_1="Once upon a time, a boy slept a lot.\n"
               "Next day...",
    subtitle_2="He died.",
    subtitle_3="That is my mother's direct approach.",
    subtitle_4="Her love for me is direct.",
    subtitle_5="Her expectation of me is direct.",
    subtitle_6="For her, it is always...",
    subtitle_7="'no pain no gain\\...",
    revised_7="\"no pain no gain\".",
    note_7="Corrected quotation marks.",
    difficulty=1,
    verified=True,
)  # test_case_block_14
# noinspection PyArgumentList
test_case_block_15 = EnglishProofTestCase.get_test_case_cls(27)(
    subtitle_1="But there are things that\n"
               "simply cannot be gained.",
    subtitle_2="Days come and go.",
    subtitle_3="Talking about Chow look-alike...",
    subtitle_4="You still think it's going happen?",
    subtitle_5="When it comes to luck...",
    subtitle_6="The lottery numbers that\n"
               "mother obliges to draw...",
    subtitle_7="Failed even to bring her one cent!",
    subtitle_8="As for being smart...",
    subtitle_9="I did try hard, but then...",
    subtitle_10="But then, I still have dreams.",
    subtitle_11="\"My Ideal World\"",
    subtitle_12="Maldives, a world outside our world.",
    subtitle_13="The sky blue, clouds white,\n"
                "the trees tall and water bright.",
    subtitle_14="The colourful world of the tropical sea.",
    subtitle_15="The primitive ocean of primitive energy.",
    subtitle_16="Experience a world that\n"
                "knows no boundary!",
    subtitle_17="Enjoy a trip to your ideal world.",
    subtitle_18="Brilliant Touring Agency,\n"
                "license no. 350999",
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
    revised_6="The lottery numbers that\n"
              "Mother obliges to draw...",
    note_6="Capitalized 'Mother' for consistency as a proper noun.",
    revised_19="Mother, do you know where the Maldives is?",
    note_19="Added 'do' for correct question structure and 'the' before "
            "'Maldives'.",
    difficulty=1,
    verified=True,
)  # test_case_block_15
# noinspection PyArgumentList
test_case_block_16 = EnglishProofTestCase.get_test_case_cls(19)(
    subtitle_1="Good morning, sir!",
    subtitle_2="Good day, sir!",
    subtitle_3="Where is your favourite place?",
    subtitle_4="My favourite place is Japan.",
    subtitle_5="They have Disneyland and\n"
               "Hello Kitty Land.",
    subtitle_6="I bought my hairpin there.",
    subtitle_7="My favourite place is Canada.",
    subtitle_8="Grandma and my uncles live there.",
    subtitle_9="My favourite place is Bangkok.",
    subtitle_10="They have water sports and\n"
                "shark's fin soup.",
    subtitle_11="My favourite place is that...",
    subtitle_12="What's-it's name.",
    subtitle_13="They have Fun World and Food Mall.",
    subtitle_14="Their chicken rice fills you up.",
    subtitle_15="Right, that's Silver City Centre.",
    subtitle_16="They serve huge bowls of rice.",
    subtitle_17="As for the place I most want to go, wow!",
    subtitle_18="There, the sky is blue,\n"
                "clouds white, the trees tall...",
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
    subtitle_6="Sweetie, we will go to Maldives once\n"
               "you get well.",
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
    subtitle_4="But you've taken everything edible\n"
               "at home.",
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
    subtitle_8="Maldives, where the trees tall and\n"
               "water bright...",
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
    revised_8="Maldives, where the trees are tall and\n"
              "water bright...",
    note_8="Added 'are' for grammatical correctness: 'trees are tall'.",
    revised_10="Those words have flair.",
    note_10="Changed 'flare' to 'flair' (correct word for style or "
            "eloquence).",
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
    subtitle_1="Mother, do I need to bring\n"
               "my birth certificate?",
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
    subtitle_4="The most beautiful day\n"
               "in my childhood experience...",
    subtitle_5="Passed.",
    subtitle_6="Do you think paper is\n"
               "a good chicken wrapper?",
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
    subtitle_3="Has just won the first gold medal\n"
               "in Hong Kong history!",
    subtitle_4="San San, when confirmed her winning...",
    subtitle_5="Told reporters that her result...",
    subtitle_6="Help proves that\n"
               "Hong Kong athletes are horrible...",
    subtitle_7="Excuse me, it should be \"honourable \".",
    subtitle_8="Hong Kong athletes\n"
               "are honourable athletes.",
    subtitle_9="End of special report.",
    revised_3="has just won the first gold medal\n"
              "in Hong Kong history!",
    note_3="Changed 'Has' to lowercase 'has' to continue the sentence "
           "from previous subtitle.",
    revised_4="San San, when her win was confirmed...",
    note_4="Changed 'when confirmed her winning' to 'when her win was "
           "confirmed' for grammatical correctness.",
    revised_5="told reporters that her result...",
    note_5="Changed 'Told' to lowercase 'told' to continue the sentence "
           "from previous subtitle.",
    revised_6="helped prove that\n"
              "Hong Kong athletes are horrible...",
    note_6="Changed 'Help proves' to 'helped prove' for correct tense "
           "and subject-verb agreement.",
    revised_7="Excuse me, it should be \"honourable\".",
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
    subtitle_5="\"Looking for Logan\"",
    subtitle_6="And so, while one dream lingers on...",
    subtitle_7="Another one begins.",
    subtitle_8="\"aka: How Does a Calf Become a Calf?\"",
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
    subtitle_2="You raised San San,\n"
               "now you will raise me!",
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
    subtitle_2="Lamma Island?\n"
               "Where Chow Yun Fat grew up?",
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
)  # test_case_block_37
# noinspection PyArgumentList
test_case_block_38 = EnglishProofTestCase.get_test_case_cls(2)(
    subtitle_1="I shall have this calf!",
    subtitle_2="Master!",
)  # test_case_block_38
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
