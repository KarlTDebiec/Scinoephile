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

################################## SETTINGS ###################################
pd.set_option("display.width", 110)
pd.set_option("display.max_colwidth", 16)
pd.set_option("display.max_rows", None)

################################### CLASSES ###################################
class SubtitleManager(object):
    """
    Class for managing subtitles

    TODO:
        - Document
        - Clean up merging
        - OCR features? (someday)
    """

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
                   "─": "─",
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
    re_time = re.compile("^(?P<start>\d\d:\d\d:\d\d[,.]\d\d\d) --> "
                         "(?P<end>\d\d:\d\d:\d\d[,.]\d\d\d)(\sX1:0)?$")
    re_blank = re.compile("^\s*$")

    re_hanzi = re.compile("[\u4e00-\u9fff]")
    re_hanzi_rare = re.compile("[\u3400-\u4DBF]")
    re_western = re.compile("[a-zA-Z0-9]")
    re_jyutping = re.compile("[a-z]+\d")

    # endregion

    # region Builtins
    def __init__(self, verbosity=1, interactive=False, chinese_infile=None,
                 english_infile=None, c_offset=0, simplified=False,
                 mandarin=False, cantonese=False, translate=False, e_offset=0,
                 truecase=False, outfile=None, spacing="words", **kwargs):
        self.verbosity = verbosity
        self.interactive = interactive
        self.chinese_infile = chinese_infile
        self.english_infile = english_infile
        self.c_offset = c_offset
        self.simplified = simplified
        self.mandarin = mandarin
        self.cantonese = cantonese
        self.translate = translate
        self.e_offset = e_offset
        self.truecase = truecase
        self.spacing = spacing
        self.outfile = outfile

    def __call__(self):
        """
        Core logic

        TODO:
            - Decide between setting within each function or returning
            - Move actual merging to another function 'complile_subtitles'
        """
        # Load infiles
        if self.chinese:
            if self.chinese_infile.endswith("vtt"):
                self.chinese_subtitles = self.read_vtt(self.chinese_infile)
            else:
                self.chinese_subtitles = self.read_srt(self.chinese_infile)
        if self.english:
            if self.english_infile.endswith("vtt"):
                self.english_subtitles = self.read_vtt((self.english_infile))
            else:
                self.english_subtitles = self.read_srt((self.english_infile))

        # Apply operations to Chinese
        if self.chinese:
            if self.c_offset != 0:
                self.chinese_subtitles = self.apply_offset(
                    self.chinese_subtitles, self.c_offset)
            if self.simplified:
                self.simplify(self.chinese_subtitles)
            if self.mandarin:
                self.add_mandarin_romanization(self.chinese_subtitles)
            if self.cantonese:
                self.add_cantonese_romanization(self.chinese_subtitles)
            if self.translate:
                self.add_english_translation(self.chinese_subtitles)

        # Apply operations to English
        if self.english:
            if self.e_offset != 0:
                self.english_subtitles = self.apply_offset(
                    self.english_subtitles, self.e_offset)
            if self.truecase:
                self.apply_truecase(self.english_subtitles)

        # Merge Chinese and English
        if self.chinese and self.english:
            self.merged_subtitles = self.merge_chinese_english(
                self.chinese_subtitles,
                self.english_subtitles)
            self.merged_subtitles = self.merge_chinese_english_2(
                self.merged_subtitles)

        # Interactive
        if self.interactive:
            embed()

        # Write outfile
        if self.outfile is not None:
            if self.chinese and self.english:
                output_subtitles = self.merged_subtitles.copy().rename(
                    columns={"chinese": "text"})
                empty_line = "|"
            elif self.chinese:
                output_subtitles = self.chinese_subtitles.copy()
                empty_line = " "
            else:
                output_subtitles = self.english_subtitles.copy()
                empty_line = " "
            output_subtitles["text"].replace(np.nan, empty_line, inplace=True)
            output_subtitles["text"] = \
                output_subtitles["text"].apply(
                    lambda s: s.replace("\n-", "    -")).apply(
                    lambda s: s.replace("\n", " "))

            if self.chinese:
                if self.mandarin:
                    output_subtitles["mandarin"].replace(np.nan, empty_line,
                                                         inplace=True)
                    output_subtitles["mandarin"] = \
                        output_subtitles["mandarin"].apply(
                            lambda s: s.replace("\n-", "    -")).apply(
                            lambda s: s.replace("\n", " "))
                    output_subtitles["text"] += "\n"
                    output_subtitles["text"] += output_subtitles["mandarin"]

                if self.cantonese:
                    output_subtitles["cantonese"].replace(np.nan, empty_line,
                                                          inplace=True)
                    output_subtitles["cantonese"] = \
                        output_subtitles["cantonese"].apply(
                            lambda s: s.replace("\n-", "    -")).apply(
                            lambda s: s.replace("\n", " "))
                    output_subtitles["text"] += "\n"
                    output_subtitles["text"] += output_subtitles["cantonese"]
                if self.translate:
                    output_subtitles["text"] += "\n"
                    output_subtitles["text"] += output_subtitles["translation"]

                if self.english:
                    output_subtitles["english"].replace(np.nan, empty_line,
                                                        inplace=True)
                    output_subtitles["english"] = \
                        output_subtitles["english"].apply(
                            lambda s: s.replace("\n-", "    -")).apply(
                            lambda s: s.replace("\n", " "))
                    output_subtitles["text"] += "\n"
                    output_subtitles["text"] += output_subtitles["english"]

            self.write_outfile(output_subtitles, self.outfile)

    # endregion

    # region Properties
    @property
    def c_offset(self):
        """float: Time offset applied to Chinese subtitles (seconds)"""
        if not hasattr(self, "_c_offset"):
            self._c_offset = 0
        return self._c_offset

    @c_offset.setter
    def c_offset(self, value):
        if value is None:
            value = 0
        elif not isinstance(value, float):
            try:
                value = float(value)
            except Exception as e:
                raise e
        self._c_offset = value

    @property
    def cantonese(self):
        """bool: Add Cantonese romanzation to Chinese subtitles"""
        if not hasattr(self, "_cantonese"):
            self._cantonese = False
        return self._cantonese

    @cantonese.setter
    def cantonese(self, value):
        if not isinstance(value, bool):
            raise ValueError()
        self._cantonese = value

    @property
    def cantonese_corpus(self):
        """pycantonese.corpus.CantoneseCHATReader: Corpus for Cantonese romanization"""
        if not hasattr(self, "_cantonese_corpus"):
            import pycantonese as pc
            self._cantonese_corpus = pc.hkcancor()
            self._cantonese_corpus.add(
                f"{self.directory}/data/romanization/unmatched.cha")
        return self._cantonese_corpus

    @property
    def chinese(self):
        """bool: Chinese character subtitles present"""
        return self.chinese_infile is not None

    @property
    def chinese_infile(self):
        """str: Path to SRT file containing Chinese character text"""
        if not hasattr(self, "_chinese_infile"):
            self._chinese_infile = None
        return self._chinese_infile

    @chinese_infile.setter
    def chinese_infile(self, value):
        if not isinstance(value, str) and value is not None:
            raise ValueError()
        self._chinese_infile = value

    @property
    def chinese_subtitles(self):
        """pandas.core.frame.DataFrame: Chinese character subtitles"""
        if not hasattr(self, "_chinese_subtitles"):
            self._chinese_subtitles = None
        return self._chinese_subtitles

    @chinese_subtitles.setter
    def chinese_subtitles(self, value):
        if not isinstance(value, pd.DataFrame):
            raise ValueError()
        self._chinese_subtitles = value

    @property
    def directory(self):
        """str: Path to this Python file"""
        if not hasattr(self, "_directory"):
            import os
            self._directory = os.path.dirname(os.path.realpath(__file__))
        return self._directory

    @property
    def e_offset(self):
        """float: Time offset applied to English subtitles (seconds)"""
        if not hasattr(self, "_e_offset"):
            self._e_offset = 0
        return self._e_offset

    @e_offset.setter
    def e_offset(self, value):
        if value is None:
            value = 0
        elif not isinstance(value, float):
            try:
                value = float(value)
            except Exception as e:
                raise e
        self._e_offset = value

    @property
    def english(self):
        """bool: English subtitles present"""
        return self.english_infile is not None

    @property
    def english_infile(self):
        """str: Path to SRT file containing English text"""
        if not hasattr(self, "_english_infile"):
            self._english_infile = None
        return self._english_infile

    @english_infile.setter
    def english_infile(self, value):
        if not isinstance(value, str) and value is not None:
            raise ValueError()
        self._english_infile = value

    @property
    def english_subtitles(self):
        """pandas.core.frame.DataFrame: English subtitles"""
        if not hasattr(self, "_english_subtitles"):
            self._english_subtitles = None
        return self._english_subtitles

    @english_subtitles.setter
    def english_subtitles(self, value):
        if not isinstance(value, pd.DataFrame):
            raise ValueError()
        self._english_subtitles = value

    @property
    def interactive(self):
        """bool: Present IPython prompt after processing subtitles"""
        if not hasattr(self, "_interactive"):
            self._interactive = False
        return self._interactive

    @interactive.setter
    def interactive(self, value):
        if not isinstance(value, bool):
            raise ValueError()
        self._interactive = value

    @property
    def mandarin(self):
        """bool: Add Mandarin romanization to Chinese subtitles"""
        if not hasattr(self, "_mandarin"):
            self._mandarin = False
        return self._mandarin

    @mandarin.setter
    def mandarin(self, value):
        if not isinstance(value, bool):
            raise ValueError()
        self._mandarin = value

    @property
    def merged_subtitles(self):
        """pandas.core.frame.DataFrame: Merged Chinese/English subtitles"""
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
        """str: Path to output SRT file"""
        if not hasattr(self, "_outfile"):
            self._outfile = None
        return self._outfile

    @outfile.setter
    def outfile(self, value):
        if not (isinstance(value, str) or value is None):
            raise ValueError()
        self._outfile = value

    @property
    def simplified(self):
        """bool: Convert traditional Chinese to simplified"""
        if not hasattr(self, "_simplified"):
            self._simplified = False
        return self._simplified

    @simplified.setter
    def simplified(self, value):
        if not isinstance(value, bool):
            raise ValueError()
        self._simplified = value

    @property
    def spacing(self):
        """string: Space between syllables or words of Mandarin romanization"""
        if not hasattr(self, "_spacing"):
            self._spacing = "words"
        return self._spacing

    @spacing.setter
    def spacing(self, value):
        if value not in ["words", "syllables"]:
            raise ValueError()
        self._spacing = value

    @property
    def translate(self):
        """bool: Add English translation to Chinese subtitles"""
        if not hasattr(self, "_translate"):
            self._translate = False
        return self._translate

    @translate.setter
    def translate(self, value):
        if not isinstance(value, bool):
            raise ValueError()
        self._translate = value

    @property
    def translate_client(self):
        """google.cloud.translate_v2.client.Client: Google Translate client"""
        if not hasattr(self, "_translate_client"):
            from google.cloud import translate
            self._translate_client = translate.Client()
        return self._translate_client

    @property
    def truecase(self):
        """bool: Apply standard capitalization to English subtitles"""
        if not hasattr(self, "_truecase"):
            self._truecase = False
        return self._truecase

    @truecase.setter
    def truecase(self, value):
        if not isinstance(value, bool):
            raise ValueError()
        self._truecase = value

    @property
    def verbosity(self):
        """int: Level of output to provide"""
        if not hasattr(self, "_verbosity"):
            self._verbosity = 1
        return self._verbosity

    @verbosity.setter
    def verbosity(self, value):
        if not isinstance(value, int) and value >= 0:
            raise ValueError()
        self._verbosity = value

    # endregion Properties

    # region Methods
    def add_cantonese_romanization(self, subtitles):
        """
        Adds Yale-style romanization of Cantonese to Chinese subtitles

        Args:
            subtitles (pandas.DataFrame): Subtitles, including chinese
              character text in column named 'text'; adds column named
              'cantonese' with romanization

        TODO:
            * Add support for Jyupting
            * Support source field names other than 'text'
            * Look into word segmentation
            * Look into capitalization
        """
        import pycantonese as pc
        from collections import Counter
        from hanziconv import HanziConv

        def identify_cantonese_romanization(character):
            matches = self.cantonese_corpus.search(character=character)

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

        romanizations = []
        character_to_cantonese = {}
        unmatched = set()

        for index, subtitle in subtitles.iterrows():
            text = subtitle.text
            if self.verbosity >= 2:
                start = subtitle.start.strftime("%H:%M:%S,%f")[:-3]
                end = subtitle.end.strftime("%H:%M:%S,%f")[:-3]
                print(f"{index}\n{start} --> {end}\n{text}")

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
                print(f"{romanization}\n")

        subtitles["cantonese"] = pd.Series(romanizations,
                                           index=subtitles.index)
        if self.verbosity >= 1 and len(unmatched) > 0:
            print(
                f"The following {len(unmatched)} characters were not recognized:")
            print("".join(unmatched))

    def add_english_translation(self, subtitles):
        """
        Adds English translation (Google Translate) to Chinese subtitles

        subtitles (pandas.DataFrame): Subtitles, including chinese
              character text in column named 'text'; adds column named
              'english' with translation
        """
        if self.verbosity >= 1:
            print("Adding English translation")

        translations = []
        for i in range(0, len(subtitles), 100):
            translations += [c["translatedText"] for c in
                             self.translate_client.translate(
                                 list(subtitles.iloc[i:i + 100].text),
                                 source_language="zh",
                                 target_language="en")]
        subtitles["translation"] = pd.Series(translations,
                                             index=subtitles.index)

        if self.verbosity >= 2:
            for index, subtitle in subtitles.iterrows():
                start = subtitle.start.strftime("%H:%M:%S,%f")[:-3]
                end = subtitle.end.strftime("%H:%M:%S,%f")[:-3]
                print(f"{index}\n{start} --> {end}\n{subtitle.text}\n"
                      f"{subtitle.translation}\n")

    def add_mandarin_romanization(self, subtitles):
        """
        Adds Hanyu Pinyin romanization of Mandarin to Chinese subtitles

        subtitles (pandas.DataFrame): Subtitles, including chinese
              character text in column named 'text'; adds column named
              'mandarin' with romanization

        TODO:
            * Support source field names other than 'text'
            * Implement option to enable/disable word segmentation
            * Look into capitalization
        """
        from snownlp import SnowNLP
        from pypinyin import pinyin

        if self.verbosity >= 1:
            print("Adding Mandarin romanization")

        romanizations = []

        for index, subtitle in subtitles.iterrows():
            text = subtitle["text"]

            if self.verbosity >= 2:
                start = subtitle.start.strftime("%H:%M:%S,%f")[:-3]
                end = subtitle.end.strftime("%H:%M:%S,%f")[:-3]
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
                print(f"{romanization}\n")

        subtitles["mandarin"] = pd.Series(romanizations,
                                          index=subtitles.index)

    def apply_offset(self, subtitles, offset):
        """

        Args:
            subtitles:
            offset:

        Returns:

        """

        if self.verbosity >= 1:
            print(f"Applying offset of {offset} seconds")

        offset = datetime.timedelta(seconds=offset)
        subtitles["start"] = subtitles["start"].apply(
            lambda s: (datetime.datetime.combine(datetime.date.today(), s) + offset).time())
        subtitles["end"] = subtitles["end"].apply(
            lambda s: (datetime.datetime.combine(datetime.date.today(), s) + offset).time())
        return subtitles

    def apply_truecase(self, subtitles):
        """

        Args:
            subtitles:

        Returns:

        """
        import nltk

        if self.verbosity >= 1:
            print("Applying truecase to English subtitles")

        for index, subtitle in subtitles.iterrows():
            text = subtitle["text"]

            if self.verbosity >= 2:
                start = subtitle.start.strftime("%H:%M:%S,%f")[:-3]
                end = subtitle.end.strftime("%H:%M:%S,%f")[:-3]
                print(f"{index}\n{start} --> {end}\n{text}")

                tagged = nltk.pos_tag(
                    [word.lower() for word in nltk.word_tokenize(text)])
                normalized = [w.capitalize() if t in ["NN", "NNS"] else w
                              for (w, t) in tagged]
                normalized[0] = normalized[0].capitalize()
                truecased = re.sub(" (?=[\.,'!?:;])", "", ' '.join(normalized))

                # Could probably use a more appropriate tokenization function,
                # but cleaning up in this way is fine for now.
                truecased = truecased.replace(" n't", "n't")
                truecased = truecased.replace(" i ", " I ")
                truecased = truecased.replace("``", "\"")
                truecased = truecased.replace("''", "\"")
                truecased = re.sub(
                    "(\A\w)|(?<!\.\w)([\.?!] )\w|\w(?:\.\w)|(?<=\w\.)\w",
                    lambda s: s.group().upper(), truecased)

                if self.verbosity >= 2:
                    print(f"{truecased}\n")

                subtitle["text"] = truecased

    def merge_chinese_english(self, chinese_subtitles, english_subtitles):
        def add_merged_subtitle():
            if start == time:
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

    def merge_chinese_english_2(self, merged_subtitles):

        cleaned_subs = pd.DataFrame([merged_subtitles.iloc[0]])

        for index in self.merged_subtitles.index[1:]:
            last = cleaned_subs.iloc[-1]
            next = merged_subtitles.loc[index]
            if last.chinese == next.chinese:
                if isinstance(last.english, float) and np.isnan(last.english):
                    # Chinese started before English
                    last.english = next.english
                    last.end = next.end
                    cleaned_subs.iloc[-1] = last  # Apparently necessary
                elif isinstance(next.english, float) and np.isnan(next.english):
                    # English started before Chinese
                    last.end = next.end
                    cleaned_subs.iloc[-1] = last  # Apparently not necessary
                else:
                    # Single Chinese subtitle given two English subtitles
                    gap = (datetime.datetime.combine(datetime.date.today(),
                                                     next.start) -
                           datetime.datetime.combine(datetime.date.today(),
                                                     last.end))
                    if gap.total_seconds() < 0.5:
                        # Probably long Chinese split into two English
                        mid = (datetime.datetime.combine(datetime.date.today(),
                                                         last.end) +
                               (gap / 2)).time()
                        last.end = mid
                        next.start = mid
                        cleaned_subs.iloc[-1] = last  # Apparently not necessary
                        cleaned_subs = cleaned_subs.append(next)

                    else:
                        # Probably Chinese repeated with different English
                        cleaned_subs = cleaned_subs.append(next)

            elif last.english == next.english:
                if isinstance(last.chinese, float) and np.isnan(last.chinese):
                    # English started before Chinese
                    last.chinese = next.chinese
                    if hasattr(next, "mandarin"):
                        last.mandarin = next.mandarin
                    if hasattr(next, "cantonese"):
                        last.cantonese = next.cantonese
                    last.end = next.end
                    cleaned_subs.iloc[-1] = last  # Apparently necessary
                elif isinstance(next.chinese, float) and np.isnan(next.chinese):
                    # Chinese started before English
                    if last.end < next.start:
                        cleaned_subs = cleaned_subs.append(next)
                    else:
                        last.end = next.end
                        cleaned_subs.iloc[-1] = last  # Apparently not necessary
                else:
                    gap = (datetime.datetime.combine(datetime.date.today(),
                                                     next.start) -
                           datetime.datetime.combine(datetime.date.today(),
                                                     last.end))
                    if gap.total_seconds() < 0.5:
                        # Probably long English split into two Chinese
                        mid = (datetime.datetime.combine(datetime.date.today(),
                                                         last.end) +
                               (gap / 2)).time()
                        last.end = mid
                        next.start = mid
                        cleaned_subs.iloc[-1] = last  # Apparently not necessary
                        cleaned_subs = cleaned_subs.append(next)
                    else:
                        # Probably English repeated with different Chinese
                        cleaned_subs = cleaned_subs.append(next)
            else:
                cleaned_subs = cleaned_subs.append(next)

        cleaned_subs = cleaned_subs.reset_index(drop=True)
        cleaned_subs.index += 1

        return cleaned_subs

    def read_srt(self, infile):
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
                        raise Exception(f"{index} {start} {end} {title}")
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

    def read_vtt(self, infile):
        if self.verbosity >= 1:
            print(f"Reading subtitles from '{infile}'")

        with open(infile, "r") as infile:
            start = end = text = None
            starts = []
            ends = []
            texts = []
            line = infile.readline()
            line = infile.readline()
            line = infile.readline()
            line = infile.readline()
            while True:
                line = infile.readline()
                if line == "":
                    break
                if self.verbosity >= 3:
                    print(line.strip())
                if self.re_time.match(line):
                    start = datetime.datetime.strptime(
                        self.re_time.match(line).groupdict()["start"],
                        "%H:%M:%S.%f").time()
                    end = datetime.datetime.strptime(
                        self.re_time.match(line).groupdict()["end"],
                        "%H:%M:%S.%f").time()
                elif self.re_blank.match(line):
                    if (start is None
                            or end is None
                            or text is None):
                        raise Exception(f"{start} {end} {text}")
                    starts.append(start)
                    ends.append(end)
                    texts.append(text)
                    start = end = text = None
                else:
                    if text is None:
                        text = line.strip()
                    else:
                        text += "\n" + line.strip()
        subtitles = pd.DataFrame.from_items([("index", range(1, len(texts) + 1)),
                                             ("start", starts),
                                             ("end", ends),
                                             ("text", texts)])
        subtitles.set_index("index", inplace=True)
        return subtitles

    def simplify(self, subtitles):
        from hanziconv import HanziConv

        if self.verbosity >= 1:
            print("Converting traditional characters to simplified")

        for index, subtitle in subtitles.iterrows():
            text = subtitle["text"]

            if self.verbosity >= 2:
                start = subtitle.start.strftime("%H:%M:%S,%f")[:-3]
                end = subtitle.end.strftime("%H:%M:%S,%f")[:-3]
                print(f"{index}\n{start} --> {end}\n{text}")

            simplified = ""
            for character in text:
                if (self.re_hanzi.match(character)
                        or self.re_hanzi_rare.match(character)):
                    simplified += HanziConv.toSimplified(character)
                else:
                    simplified += character

            if self.verbosity >= 2:
                print(f"{simplified}\n")

            subtitle["text"] = simplified

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

    # region Static Methods
    @staticmethod
    def construct_argparser():
        """
        Prepares argument parser

        Returns:
            parser (argparse.ArgumentParser): Argument parser
        """
        import argparse

        help_message = ("Modify Chinese subtitles by adding Mandarin or "
                        "Cantonese romanization, converting traditional "
                        "characters to simplified, and merging with English "
                        "translation.")

        parser = argparse.ArgumentParser(description=help_message)

        # General
        verbosity = parser.add_mutually_exclusive_group()
        verbosity.add_argument("-v", "--verbose", action="count",
                               dest="verbosity", default=1,
                               help="enable verbose output, may be specified "
                                    "more than once")
        verbosity.add_argument("-q", "--quiet", action="store_const",
                               dest="verbosity", const=0,
                               help="disable verbose output")
        parser.add_argument("-i", "--interactive", action="store_true",
                            dest="interactive",
                            help="present IPython prompt after loading and "
                                 "processing")

        # Input
        parser_inp = parser.add_argument_group(
            "input arguments (at least one required)")
        parser_inp.add_argument("-c", "--chinese_infile", type=str, nargs="?",
                                metavar="INFILE",
                                help="Chinese subtitles in SRT format")
        parser_inp.add_argument("-e", "--english_infile", type=str, nargs="?",
                                metavar="INFILE",
                                help="English subtitles in SRT format")

        # Operation
        parser_ops = parser.add_argument_group("operation arguments")
        parser_ops.add_argument("--c_offset", type=float, default=0,
                                help="offset added to Chinese subtitle "
                                     "timestamps")
        parser_ops.add_argument("-s", "--simplified", action="store_true",
                                help="convert traditional characters to "
                                     "simplified")
        parser_ops.add_argument("-m", "--mandarin", action="store_true",
                                help="add Mandarin/Putonghua pinyin "
                                     "(汉语拼音)")
        parser_ops.add_argument("-y", "--yue", action="store_true",
                                dest="cantonese",
                                help="add Cantonese/Guangdonghua/Yue "
                                     "Yale-style pinyin (耶鲁粤语拼音)")
        parser_ops.add_argument("-t", "--translate", action="store_true",
                                dest="translate",
                                help="generate English translation using "
                                     "Google Translate; requires key for "
                                     "Google Cloud Platform")
        parser_ops.add_argument("--e_offset", type=float, default=0,
                                help="offset added to English subtitle "
                                     "timestamps")
        parser_ops.add_argument("--truecase", action="store_true",
                                help="apply standard capitalization to "
                                     "English subtitles")

        # Output
        parser_out = parser.add_argument_group("output arguments")
        parser_out.add_argument("-o", "--outfile", type=str, nargs="?",
                                help="output file (optional)")

        return parser

    @staticmethod
    def validate_args(parser, args):
        """
        Validates arguments

        Args:
            parser (argparse.ArgumentParser): Argument parser
            args: Arguments

        """
        from io import StringIO

        with StringIO() as helptext:
            parser.print_help(helptext)
            try:
                if args.chinese_infile is None and args.english_infile is None:
                    raise ValueError("Either argument '-c/--chinese_infile' "
                                     "or '-e/--english_infile' is required")
                if args.chinese_infile is None:
                    if args.c_offset != 0:
                        raise ValueError("Argument '--c_offset' requires "
                                         "argument '-c/--chinese_infile'")
                    if args.simplified:
                        raise ValueError("Argument '-s' requires "
                                         "argument '-c/--chinese_infile'")
                    if args.mandarin:
                        raise ValueError("Argument '-m' requires "
                                         "argument '-c/--chinese_infile'")
                    if args.cantonese:
                        raise ValueError("Argument '-y' requires "
                                         "argument '-c/--chinese_infile'")
                    if args.translate:
                        raise ValueError("Argument '-t' requires "
                                         "argument '-c/--chinese_infile'")
                if args.english_infile is None:
                    if args.e_offset != 0:
                        raise ValueError("Argument '--e_offset' requires "
                                         "argument '-e/--english_infile'")
                    if args.truecase:
                        raise ValueError("Argument '--truecase' requires "
                                         "argument '-e/--english_infile'")
                if args.english_infile is not None:
                    if args.translate:
                        raise ValueError("Argument '-t' incompatible with "
                                         "argument '-e/--english_infile'")
            except ValueError as e:
                print(helptext.getvalue())
                raise e

    # endregion

    @classmethod
    def main(cls):
        """
        Parses and validates arguments

        TODO:
            - General method of requiring one or more of a group of arguments
            - General method of having arguments require one another
        """

        parser = cls.construct_argparser()
        args = parser.parse_args()
        cls.validate_args(parser, args)
        cls(**vars(args))()


#################################### MAIN #####################################
if __name__ == "__main__":
    SubtitleManager.main()