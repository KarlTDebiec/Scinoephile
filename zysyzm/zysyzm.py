#!/usr/bin/python
# -*- coding: utf-8 -*-
#   zysyzm.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
import datetime
import re
import pandas as pd
from IPython import embed

if __name__ == "__main__":
    __package__ = str("zysyzm")
    import zysyzm


################################### CLASSES ###################################
class SubtitleManager(object):
    """"""

    # region Instance Variables
    punctuation = {"\n": "\n",
                   "　": " ",
                   " ": " ",
                   "？": "?",
                   "，": ",",
                   "、": ",",
                   ".": ".",
                   "！": "!",
                   "…": "...",
                   "﹣": "-",
                   "-": "-",
                   "“": "\"",
                   "”": "\"",
                   "\"": "\"",
                   "《": "<",
                   "》": ">",
                   "「": "[",
                   "」": "]",
                   "：": ":"}

    re_index = re.compile("^(?P<index>\d+)$")
    re_time = re.compile("^(?P<start>\d\d:\d\d:\d\d,\d\d\d) --> "
                         "(?P<end>\d\d:\d\d:\d\d,\d\d\d)(\sX1:0)?$")
    re_blank = re.compile("^\s*$")

    re_hanzi = re.compile("[\u4e00-\u9fff]")
    re_hanzi_rare = re.compile("[\u3400-\u4DBF]")
    re_western = re.compile("[a-zA-Z0-9]")
    re_jyutping = re.compile("[a-z]+\d")

    # endregion

    # region Builtins
    def __init__(self, verbosity, language, chinese_infile,
                 english_infile=None, spacing="words", **kwargs):
        self.verbosity = verbosity
        self.language = language
        self.spacing = spacing
        self.chinese_infile = chinese_infile
        self.english_infile = english_infile
        self.outfile = "out.srt"

    def __call__(self):
        self.chinese_subtitles = self.read_infile(self.chinese_infile)
        if self.english_infile is not None:
            self.english_subtitles = self.read_infile((self.english_infile))

        if self.language == "mandarin":
            self.add_hanyu_pinyin(self.chinese_subtitles)
        elif self.language == "cantonese":
            self.add_cantonese_pinyin(self.chinese_subtitles)

    # endregion

    # region Properties
    @property
    def chinese_infile(self):
        return self._chinese_infile

    @chinese_infile.setter
    def chinese_infile(self, value):
        if not isinstance(value, str):
            raise ValueError()
        self._chinese_infile = value

    @property
    def chinese_subtitles(self):
        return self._chinese_subtitles

    @chinese_subtitles.setter
    def chinese_subtitles(self, value):
        if not isinstance(value, pd.DataFrame):
            raise ValueError()
        self._chinese_subtitles = value

    @property
    def english_infile(self):
        return self._english_infile

    @english_infile.setter
    def english_infile(self, value):
        if not (isinstance(value, str) or value is None):
            raise ValueError()
        self._english_infile = value

    @property
    def english_subtitles(self):
        return self._english_subtitles

    @english_subtitles.setter
    def english_subtitles(self, value):
        if not isinstance(value, pd.DataFrame):
            raise ValueError()
        self._english_subtitles = value

    @property
    def language(self):
        return self._language

    @language.setter
    def language(self, value):
        if value not in ["cantonese", "mandarin"]:
            raise ValueError()
        self._language = value

    @property
    def outfile(self):
        return self._outfile

    @outfile.setter
    def outfile(self, value):
        if not isinstance(value, str):
            raise ValueError()
        self._outfile = value

    @property
    def spacing(self):
        return self._spacing

    @spacing.setter
    def spacing(self, value):
        if value not in ["words", "syllables"]:
            raise ValueError()
        self._spacing = value

    @property
    def verbosity(self):
        return self._verbosity

    @verbosity.setter
    def verbosity(self, value):
        if not isinstance(value, int) and value >= 0:
            raise ValueError()
        self._verbosity = value

    # endregion

    # region Methods
    @staticmethod
    def construct_argparser():
        """"""
        import argparse

        help_message = """Process data"""
        parser = argparse.ArgumentParser(description=help_message)

        parser.add_argument("chinese_infile", type=str,
                            help="Chinese subtitles in SRT format")
        # parser.add_argument("english_infile", type=str, nargs="?",
        #                    help="English subtitles in SRT format (optional)")
        # parser.add_argument("-o", "--outfile", type=str, nargs="?",
        #                     help="Output file (optional)")

        verbosity = parser.add_mutually_exclusive_group()
        verbosity.add_argument("-v", "--verbose", action="count",
                               dest="verbosity", default=1,
                               help="""enable verbose output, may be specified
                                       more than once""")
        verbosity.add_argument("-q", "--quiet", action="store_const",
                               dest="verbosity", const=0,
                               help="disable verbose output")

        language = parser.add_mutually_exclusive_group()
        language.add_argument("-m", "--mandarin", action="store_const",
                              dest="language", default="mandarin",
                              const="mandarin",
                              help="""add Mandarin/Putonghua pinyin
                              (汉语拼音)""")
        language.add_argument("-c", "--cantonese", action="store_const",
                              const="cantonese", dest="language",
                              help="""add Cantonese/Guangdonghua Yale-style
                                   pinyin (耶鲁广东话拼音)""")

        # spacing = parser.add_mutually_exclusive_group()
        # spacing.add_argument("-w", "--words", action="store_const",
        #                     dest="spacing", default="words", const="words",
        #                     help="""add spaces between words only""")
        # spacing.add_argument("-s", "--syllables", action="store_const",
        #                     dest="spacing", const="syllables",
        #                     help="add spaces between all syllables")

        return parser

    def add_cantonese_pinyin(self, subtitles):
        """"""
        import pycantonese as pc
        from collections import Counter
        from hanziconv import HanziConv

        def identify_cantonese_pinyin(character):
            """"""
            matches = corpus.search(character=character)

            if len(matches) == 0:
                # Character not found in corpus, search for traditional version
                traditional_character = HanziConv.toTraditional(character)
                if traditional_character != character:
                    if self.verbosity >= 3:
                        print(
                            f"{character} not found, searching for traditional")
                    return identify_cantonese_pinyin(traditional_character)

                # Truly no instance of character in corpus
                if self.verbosity >= 1:
                    print(f"{character} not found in corpus")
                return None

            # If character is found in corpus alone, use most common instance
            character_matches = [m[2] for m in matches if len(m[0]) == 1]
            if len(character_matches) > 0:
                jyutping = Counter(character_matches).most_common(1)[0][0]
                if self.verbosity >= 3:
                    print(f"{character} found as single character")

            # If character is not found in corpus alone, use most common word
            else:
                most_common_word = Counter(matches).most_common(1)[0][0]
                index = most_common_word[0].index(character)
                jyutping = self.re_jyutping.findall(most_common_word[2])[index]
                if self.verbosity >= 3:
                    print("{character} found in word")

            try:
                yale = pc.jyutping2yale(jyutping)
            except ValueError:
                if self.verbosity >= 1:
                    print(
                        f"{character} found but could not be converted from jyutping to Yale")
                return None
            return yale

        corpus = pc.hkcancor()
        corpus.add("data/romanization/unmatched.cha")
        character_to_cantonese = {}
        unmatched = set()

        for index, datum in subtitles.iterrows():
            subtitle = datum["subtitle"]
            if self.verbosity >= 2:
                start = datum.start.strftime("%H:%M:%S,%f")[:-3]
                end = datum.end.strftime("%H:%M:%S,%f")[:-3]
                print(index)
                print(f"{start} --> {end}")
                print(subtitle)

            romanized = ""
            for character in subtitle:
                if self.re_hanzi.match(character):
                    pass
                elif self.re_hanzi_rare.match(character):
                    pass
                elif self.re_western.match(character):
                    romanized += character
                    continue
                elif character in self.punctuation:
                    romanized = romanized.strip() + self.punctuation[character]
                    continue
                else:
                    if self.verbosity >= 1:
                        print(
                            f"{character} is unrecognized as Chinese, western, or punctuation")
                        unmatched.add(character)
                    continue

                # Character is a Hanzi, is its romanization known?
                if character in character_to_cantonese:
                    yale = character_to_cantonese[character]
                    romanized += " " + yale
                    continue
                elif character in unmatched:
                    romanized += " " + character
                    continue
                else:
                    yale = identify_cantonese_pinyin(character)
                    if yale is not None:
                        romanized += " " + yale
                        character_to_cantonese[character] = yale
                    else:
                        romanized += " " + character
                        unmatched.add(character)

            romanized = romanized.strip()
            if self.verbosity >= 2:
                print(romanized)
                print()
        if self.verbosity >= 1 and len(unmatched) >= 0:
            print(
                f"The following {len(unmatched)} characters were not recognized:")
            print("".join(unmatched))

    def add_hanyu_pinyin(self, subtitles):
        """"""
        from snownlp import SnowNLP
        from pypinyin import pinyin

        for index, datum in subtitles.iterrows():
            subtitle = datum["subtitle"]
            if self.verbosity >= 2:
                start = datum.start.strftime("%H:%M:%S,%f")[:-3]
                end = datum.end.strftime("%H:%M:%S,%f")[:-3]
                print(index)
                print(f"{start} --> {end}")
                print(subtitle)

            romanized = ""
            for word in SnowNLP(subtitle).words:
                if word in self.punctuation:
                    romanized = romanized.strip() + self.punctuation[word]
                    continue
                romanized += " " + "".join([a[0] for a in pinyin(word)])

            romanized = romanized.strip()
            if self.verbosity >= 2:
                print(romanized)
                print()

    def read_infile(self, infile):
        with open(infile, "r") as infile:
            index = start = end = title = None
            indexes = []
            starts = []
            ends = []
            titles = []
            while True:
                line = infile.readline()
                if line == "":
                    break
                if self.re_index.match(line):
                    index = int(self.re_index.match(line).groupdict()["index"])
                elif self.re_time.match(line):
                    start = datetime.datetime.strptime(
                        self.re_time.match(line).groupdict()["start"],
                        "%H:%M:%S,%f").time()
                    end = datetime.datetime.strptime(
                        self.re_time.match(line).groupdict()["end"],
                        "%H:%M:%S,%f").time()
                elif self.re_blank.match(line):
                    if (index is None
                            or start is None
                            or end is None
                            or title is None):
                        raise Exception()
                    indexes.append(index)
                    starts.append(start)
                    ends.append(end)
                    titles.append(title)
                    index = start = end = title = None
                else:
                    if title is None:
                        title = line.strip()
                    else:
                        title += "\n" + line.strip()
        return pd.DataFrame.from_items([("index", indexes),
                                        ("start", starts),
                                        ("end", ends),
                                        ("subtitle", titles)])

    # endregion

    @classmethod
    def main(cls):
        """"""
        subtitle_manager = cls(**vars(cls.construct_argparser().parse_args()))
        subtitle_manager()


#################################### MAIN #####################################
if __name__ == "__main__":
    SubtitleManager.main()
