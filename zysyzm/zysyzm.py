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
import numpy as np
import pandas as pd
from IPython import embed

if __name__ == "__main__":
    __package__ = str("zysyzm")
    import zysyzm

pd.set_option("display.width", 110)
pd.set_option("display.max_colwidth", 16)


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
                   "...": "...",
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
    def __init__(self, verbosity, cantonese, mandarin, chinese_infile,
                 english_infile=None, outfile=None, spacing="words", **kwargs):
        self.verbosity = verbosity
        self.chinese_infile = chinese_infile
        self.english_infile = english_infile
        self.cantonese = cantonese
        self.mandarin = mandarin
        self.spacing = spacing
        self.outfile = outfile

    def __call__(self):
        self.chinese_subtitles = self.read_infile(self.chinese_infile)
        if self.english:
            self.english_subtitles = self.read_infile((self.english_infile))

        if self.cantonese:
            self.add_cantonese_romanization(self.chinese_subtitles)
        if self.mandarin:
            self.add_mandarin_romanization(self.chinese_subtitles)
        if self.english:
            self.merged_subtiles = self.merge_chinese_english(
                self.chinese_subtitles,
                self.english_subtitles)

        if self.outfile is not None:
            if self.english:
                output_subtitles = self.merged_subtiles.copy().rename(
                    columns={"chinese": "text"})
                empty_line = "|"
            else:
                output_subtitles = self.chinese_subtitles.copy()
                empty_line = " "
            output_subtitles["text"].replace(np.nan, empty_line, inplace=True)
            output_subtitles["text"] = output_subtitles["text"].apply(
                lambda s: s.replace("\n", "    "))

            if self.cantonese:
                output_subtitles["cantonese"].replace(np.nan, empty_line,
                                                      inplace=True)
                output_subtitles["cantonese"] = \
                    output_subtitles["cantonese"].apply(
                        lambda s: s.replace("\n", "    "))
                output_subtitles["text"] += "\n"
                output_subtitles["text"] += output_subtitles["cantonese"]

            if self.mandarin:
                output_subtitles["mandarin"].replace(np.nan, empty_line,
                                                     inplace=True)
                output_subtitles["mandarin"] = \
                    output_subtitles["mandarin"].apply(
                        lambda s: s.replace("\n", "    "))
                output_subtitles["text"] += "\n"
                output_subtitles["text"] += output_subtitles["mandarin"]

            if self.english:
                output_subtitles["english"].replace(np.nan, empty_line,
                                                    inplace=True)
                output_subtitles["english"] = \
                    output_subtitles["english"].apply(
                        lambda s: s.replace("\n", "    "))
                output_subtitles["text"] += "\n"
                output_subtitles["text"] += output_subtitles["english"]

            self.write_outfile(output_subtitles, self.outfile)

    # endregion

    # region Properties
    @property
    def cantonese(self):
        return self._cantonese

    @cantonese.setter
    def cantonese(self, value):
        if not isinstance(value, bool):
            raise ValueError()
        self._cantonese = value

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
        if not hasattr(self, "_chinese_subtitles"):
            self._chinese_subtitles = None
        return self._chinese_subtitles

    @chinese_subtitles.setter
    def chinese_subtitles(self, value):
        if not isinstance(value, pd.DataFrame):
            raise ValueError()
        self._chinese_subtitles = value

    @property
    def english(self):
        return self.english_infile is not None

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
        if not hasattr(self, "_english_subtitles"):
            self._english_subtitles = None
        return self._english_subtitles

    @english_subtitles.setter
    def english_subtitles(self, value):
        if not isinstance(value, pd.DataFrame):
            raise ValueError()
        self._english_subtitles = value

    @property
    def mandarin(self):
        return self._mandarin

    @mandarin.setter
    def mandarin(self, value):
        if not isinstance(value, bool):
            raise ValueError()
        self._mandarin = value

    @property
    def merged_subtitles(self):
        if not hasattr(self, "_merged_subtitles"):
            self._merged_subtitles = None
        return self._merged_subtitles

    @merged_subtitles.setter
    def merged_subtitles(self, value):
        if not isinstance(value, pd.DataFrame):
            raise ValueError()
        self._merged_subtitles = value

    @property
    def outfile(self):
        return self._outfile

    @outfile.setter
    def outfile(self, value):
        if not (isinstance(value, str) or value is None):
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
        import argparse

        help_message = """Script to add romanization and optionally English
                          translation to Chinese subtitles."""
        parser = argparse.ArgumentParser(description=help_message)

        parser.add_argument("chinese_infile", type=str,
                            help="Chinese subtitles in SRT format")
        parser.add_argument("english_infile", type=str, nargs="?",
                            help="English subtitles in SRT format (optional)")
        parser.add_argument("-o", "--outfile", type=str, nargs="?",
                            help="Output file (optional)")

        verbosity = parser.add_mutually_exclusive_group()
        verbosity.add_argument("-v", "--verbose", action="count",
                               dest="verbosity", default=1,
                               help="""enable verbose output, may be specified
                                       more than once""")
        verbosity.add_argument("-q", "--quiet", action="store_const",
                               dest="verbosity", const=0,
                               help="disable verbose output")

        parser.add_argument("-c", "--cantonese", action="store_true",
                            help="""add Cantonese/Guangdonghua Yale-style
                                   pinyin (耶鲁广东话拼音)""")
        parser.add_argument("-m", "--mandarin", action="store_true",
                            help="add Mandarin/Putonghua pinyin (汉语拼音)")

        # spacing = parser.add_mutually_exclusive_group()
        # spacing.add_argument("-w", "--words", action="store_const",
        #                      dest="spacing", default="words", const="words",
        #                      help="""add spaces between words only""")
        # spacing.add_argument("-s", "--syllables", action="store_const",
        #                      dest="spacing", const="syllables",
        #                      help="add spaces between all syllables")

        return parser

    def add_cantonese_romanization(self, subtitles):
        import os
        import pycantonese as pc
        from collections import Counter
        from hanziconv import HanziConv

        def identify_cantonese_romanization(character):
            matches = corpus.search(character=character)

            if len(matches) == 0:
                # Character not found in corpus, search for traditional version
                traditional_character = HanziConv.toTraditional(character)
                if traditional_character != character:
                    if self.verbosity >= 3:
                        print(
                            f"{character} not found, searching for traditional")
                    return identify_cantonese_romanization(
                        traditional_character)

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
                    print(f"{character} found in word")

            try:
                yale = pc.jyutping2yale(jyutping)
            except ValueError:
                if self.verbosity >= 1:
                    print(
                        f"{character} found but could not be converted from jyutping to Yale")
                return None
            return yale

        if self.verbosity >= 1:
            print("Adding Cantonese romanization")

        corpus = pc.hkcancor()
        corpus.add(f"{os.path.dirname(os.path.realpath(__file__))}/data/romanization/unmatched.cha")
        romanizations = []
        character_to_cantonese = {}
        unmatched = set()

        for index, subtitle in subtitles.iterrows():
            text = subtitle["text"]
            if self.verbosity >= 2:
                start = subtitle.start.strftime("%H:%M:%S,%f")[:-3]
                end = subtitle.end.strftime("%H:%M:%S,%f")[:-3]
                print(index)
                print(f"{start} --> {end}")
                print(text)

            romanization = ""
            for character in text:
                if (self.re_hanzi.match(character)
                        or self.re_hanzi_rare.match(character)):
                    if character in character_to_cantonese:
                        yale = character_to_cantonese[character]
                        romanization += " " + yale
                        continue
                    elif character in unmatched:
                        romanization += " " + character
                        continue
                    else:
                        yale = identify_cantonese_romanization(character)
                        if yale is not None:
                            romanization += " " + yale
                            character_to_cantonese[character] = yale
                        else:
                            romanization += " " + character
                            unmatched.add(character)
                elif self.re_western.match(character):
                    romanization += character
                    continue
                elif character in self.punctuation:
                    romanization = romanization.strip() + self.punctuation[
                        character]
                    continue
                else:
                    if self.verbosity >= 1:
                        print(
                            f"{character} is unrecognized as Chinese, western, or punctuation")
                        unmatched.add(character)
                    continue

            romanization = romanization.strip().replace("\n ", "\n")
            romanizations += [romanization]
            if self.verbosity >= 2:
                print(romanization)
                print()

        subtitles["cantonese"] = pd.Series(romanizations,
                                           index=subtitles.index)
        if self.verbosity >= 1 and len(unmatched) > 0:
            print(
                f"The following {len(unmatched)} characters were not recognized:")
            print("".join(unmatched))

    def add_mandarin_romanization(self, subtitles):
        from snownlp import SnowNLP
        from pypinyin import pinyin

        if self.verbosity >= 1:
            print("Adding Mandarin romanization")

        romanizations = []

        for index, row in subtitles.iterrows():
            text = row["text"]

            if self.verbosity >= 2:
                start = row.start.strftime("%H:%M:%S,%f")[:-3]
                end = row.end.strftime("%H:%M:%S,%f")[:-3]
                print(f"{index}\n{start} --> {end}\n{text}")

            romanization = ""
            if self.spacing == "words":
                for line in text.split("\n"):
                    line_romanization = ""
                    for section in line.split():
                        section_romanization = ""
                        for word in SnowNLP(section).words:
                            if word in self.punctuation:
                                section_romanization += \
                                    self.punctuation[word]
                            else:
                                section_romanization += " " + "".join(
                                    [a[0] for a in pinyin(word)])
                        line_romanization += "  " + section_romanization.strip()
                    romanization += "\n" + line_romanization.strip()
            romanization = romanization.strip()

            romanizations += [romanization]

            if self.verbosity >= 2:
                print(romanization)
                print()

        subtitles["mandarin"] = pd.Series(romanizations,
                                          index=subtitles.index)

    def merge_chinese_english(self, chinese_subtitles, english_subtitles):
        def add_merged_subtitle():
            if start == time:
                return merged_subtitles
            duration = datetime.datetime.combine(datetime.date.today(), time) \
                       - datetime.datetime.combine(datetime.date.today(), start)
            if duration.total_seconds() <= 0.1:
                return merged_subtitles
            return merged_subtitles.append(
                pd.concat([
                    pd.DataFrame.from_items(
                        [("start", [start]), ("end", [time])]),
                    current_chinese_subtitle,
                    current_english_subtitle],
                    axis=1),
                ignore_index=True)

        if self.verbosity >= 1:
            print("Merging Chinese and English subtitles")

        transitions = []
        for _, subtitle in chinese_subtitles.iterrows():
            transitions += [
                [subtitle["start"], "chinese_start",
                 subtitle.drop(["start", "end"])],
                [subtitle["end"], "chinese_end", None]]
        for _, subtitle in english_subtitles.iterrows():
            transitions += [
                [subtitle["start"], "english_start",
                 subtitle.drop(["start", "end"])],
                [subtitle["end"], "english_end", None]]
        transitions.sort()

        merged_subtitles = pd.DataFrame()

        start = current_chinese_subtitle = current_english_subtitle = None
        for time, kind, subtitle in transitions:
            if kind == "chinese_start":
                if start is None:
                    # Transition from __ -> C_
                    pass
                else:
                    # Transition from _E -> CE
                    merged_subtitles = add_merged_subtitle()
                current_chinese_subtitle = pd.DataFrame(
                    subtitle).transpose().reset_index(drop=True).rename(
                    columns={"text": "chinese"})
                start = time
            elif kind == "chinese_end":
                merged_subtitles = add_merged_subtitle()
                current_chinese_subtitle = None
                if current_english_subtitle is None:
                    # Transition from C_ -> __
                    start = None
                else:
                    # Transition from CE -> _C
                    start = time
            elif kind == "english_start":
                if start is None:
                    # Transition from __ -> _E
                    pass
                else:
                    # Transition from C_ -> CE
                    merged_subtitles = add_merged_subtitle()
                current_english_subtitle = pd.DataFrame(
                    subtitle).transpose().reset_index(drop=True).rename(
                    columns={"text": "english"})
                start = time
            elif kind == "english_end":
                merged_subtitles = add_merged_subtitle()
                current_english_subtitle = None
                if current_chinese_subtitle is None:
                    # Transition from _E -> __
                    start = None
                else:
                    # Transition from CE -> E_
                    start = time

        if self.cantonese and self.mandarin:
            merged_subtitles = merged_subtitles[
                ["start", "end", "chinese", "cantonese", "mandarin", "english"]]
        elif self.cantonese:
            merged_subtitles = merged_subtitles[
                ["start", "end", "chinese", "cantonese", "english"]]
        elif self.mandarin:
            merged_subtitles = merged_subtitles[
                ["start", "end", "chinese", "mandarin", "english"]]
        else:
            merged_subtitles = merged_subtitles[
                ["start", "end", "chinese", "english"]]
        merged_subtitles.index += 1

        return merged_subtitles

    def read_infile(self, infile):
        if self.verbosity >= 1:
            print(f"Reading subtitles from '{infile}'")

        with open(infile, "r") as infile:
            index = start = end = title = None
            indexes = []
            starts = []
            ends = []
            texts = []
            while True:
                line = infile.readline()
                if line == "":
                    break
                if self.verbosity >= 3:
                    print(line.strip())
                if self.re_index.match(line) and index is None:
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
                    texts.append(title)
                    index = start = end = title = None
                else:
                    if title is None:
                        title = line.strip()
                    else:
                        title += "\n" + line.strip()
        subtitles = pd.DataFrame.from_items([("index", indexes),
                                             ("start", starts),
                                             ("end", ends),
                                             ("text", texts)])
        subtitles.set_index("index", inplace=True)
        return subtitles

    def write_outfile(self, subtitles, outfile):
        if self.verbosity >= 1:
            print(f"Writing subtitles to '{outfile}'")

        with open(outfile, "w") as outfile:
            for index, subtitle in subtitles.iterrows():
                start = subtitle.start.strftime("%H:%M:%S,%f")[:-3]
                end = subtitle.end.strftime("%H:%M:%S,%f")[:-3]
                text = subtitle["text"]
                outfile.write(f"{index}\n")
                outfile.write(f"{start} --> {end}\n")
                outfile.write(f"{text}\n")
                outfile.write("\n")

    # endregion

    @classmethod
    def main(cls):
        cls(**vars(cls.construct_argparser().parse_args()))()


#################################### MAIN #####################################
if __name__ == "__main__":
    SubtitleManager.main()
