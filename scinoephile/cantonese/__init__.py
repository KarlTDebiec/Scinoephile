#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.cantonese.__init__.py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
import re
import pycantonese as pc
from collections import Counter
from hanziconv import HanziConv
from scinoephile import package_root

################################## VARIABLES ##################################

corpus = pc.hkcancor()
corpus.add(f"{package_root}/data/romanization/unmatched.cha")
hanzi_to_pinyin = {}
unmatched = set()
re_jyutping = re.compile(r"[a-z]+\d")


################################## FUNCTIONS ##################################
def get_cantonese_pinyin(hanzi):
    """
    Gets the Yale Cantonese romanization of a provided Hanzi

    Args:
        hanzi (str): Hanzi chinese character

    Returns:
        str: Yale Cantonese romanization of hanzi
    """
    # If known to be unmatched, stop early
    if hanzi in unmatched:
        return None

    # If cached, use that value
    elif hanzi in hanzi_to_pinyin:
        return hanzi_to_pinyin[hanzi]

    # Otherwise search corpus for value
    else:
        matches = corpus.search(character=hanzi)

        # If not found, try traditional alternative
        if len(matches) == 0:
            trad_hanzi = HanziConv.toTraditional(hanzi)
            if trad_hanzi != hanzi:
                return get_cantonese_pinyin(trad_hanzi)

            # Truly no instance of hanzi in corpus
            unmatched.add(hanzi)
            return None

        # If found in corpus alone, use most common instance
        character_matches = [m[2] for m in matches if len(m[0]) == 1]
        if len(character_matches) > 0:
            jyutping = Counter(character_matches).most_common(1)[0][0]

        # Otherwise use most common word
        else:
            most_common_word = Counter(matches).most_common(1)[0][0]
            index = most_common_word[0].index(hanzi)
            jyutping = re_jyutping.findall(most_common_word[2])[index]

        # Convert from jyutping to yale
        try:
            yale = pc.jyutping2yale(jyutping)
            hanzi_to_pinyin[hanzi] = yale
            return yale
        except ValueError:
            unmatched.add(hanzi)
            return None
