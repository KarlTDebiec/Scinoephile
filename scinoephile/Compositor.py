#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.Compositor.py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
import re
import numpy as np
import pandas as pd
from os.path import expandvars, isfile
from IPython import embed
from scinoephile import (merge_subtitles, CLToolBase, SubtitleSeries)

################################## SETTINGS ###################################
pd.set_option("display.width", 110)
pd.set_option("display.max_colwidth", 16)
pd.set_option("display.max_rows", None)


################################### CLASSES ###################################
class Compositor(CLToolBase):
    """
    Compiles Chinese and English subtitles

    .. todo::
        - [ ] Refactor and improve code for handling dashes
        - [ ] Clean up merging code
        - [ ] Apply timings from one infile directly to another, provided they
              have the same number of subtitles
        - [ ] Address warnings
          - .../Compositor.py:762:         FutureWarning: from_items is
            deprecated. Please use DataFrame.from_dict(dict(items), ...)
            instead. DataFrame.from_dict(OrderedDict(items)) may be used to
            preserve the key order. [("start", [start]), ("end", [time])]),
            .../lib/python3.6/site-packages/pandas/core/frame.py:6211:
          - FutureWarning: Sorting because non-concatenation axis is not
            aligned. A future version of pandas will change to not sort by
            default. To accept the future behavior, pass 'sort=False'. To
            retain the current behavior and silence the warning, pass
            'sort=True'. sort=sort)
          - .../lib/python3.6/site-packages/pandas/core/generic.py:4405:
            SettingWithCopyWarning: A value is trying to be set on a copy of a
            slice from a DataFrame. See the caveats in the documentation:
            http://pandas.pydata.org/pandas-docs/stable/
            indexing.html#indexing-view-versus-copy self[name] = value
        - [ ] Document
    """
    import re

    # region Instance Variables
    help_message = ("Compiles Chinese and English subtitles into a single "
                    "file, optionally adding Mandarin or Cantonese "
                    "romanization, converting traditional characters to "
                    "simplified, or adding machine translation.")
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

    re_index = re.compile(r"^(?P<index>\d+)$")
    re_time = re.compile(r"^(?P<start>\d\d:\d\d:\d\d[,.]\d\d\d) --> "
                         r"(?P<end>\d\d:\d\d:\d\d[,.]\d\d\d)(\sX1:0)?$")
    re_blank = re.compile(r"^\s*$")
    re_hanzi = re.compile(r"[\u4e00-\u9fff]")
    re_hanzi_rare = re.compile(r"[\u3400-\u4DBF]")
    re_western = re.compile(r"[a-zA-Z0-9]")
    re_jyutping = re.compile(r"[a-z]+\d")

    # endregion

    # region Builtins
    def __init__(self, bilingual=False, english=False, hanzi=False,
                 pinyin=False, **kwargs):
        """
        Initializes tool

        Args:
            chinese_infile (str): Path to SRT file containing Chinese character
              text
            english_infile (str): Path to SRT file containing English text
            c_offset (float): Time offset applied to Chinese subtitles
              (seconds)
            simplified (bool): Convert traditional Chinese to simplified
            mandarin (bool): Add Mandarin romanization to Chinese subtitles
            cantonese (bool): Add Cantonese romanzation to Chinese subtitles
            translate (bool): Add English translation to Chinese subtitles
            e_offset (float): Time offset applied to English subtitles
              (seconds)
            truecase (bool): Apply standard capitalization to English subtitles
            outfile (str): Path to output SRT file
            spacing (str): Space between syllables or words of Mandarin
              romanization
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        if bilingual:
            if isinstance(bilingual, str):
                bilingual = expandvars(bilingual)
                if isfile(bilingual):
                    self.bilingual_subtitles = SubtitleSeries.load(
                        bilingual, verbosity=self.verbosity)
        if english:
            if isinstance(english, str):
                english = expandvars(english)
                if isfile(english):
                    self.english_subtitles = SubtitleSeries.load(
                        english, verbosity=self.verbosity)
        if hanzi:
            if isinstance(hanzi, str):
                hanzi = expandvars(hanzi)
                if isfile(hanzi):
                    self.hanzi_subtitles = SubtitleSeries.load(
                        hanzi, verbosity=self.verbosity)
        if pinyin:
            if isinstance(pinyin, str):
                pinyin = expandvars(pinyin)
                if isfile(pinyin):
                    self.pinyin_subtitles = SubtitleSeries.load(
                        pinyin, verbosity=self.verbosity)

    def __call__(self):
        """
        Core logic
        """
        if (self.english_subtitles is not None
                and self.hanzi_subtitles is not None):

            for e in self.english_subtitles.events:
                e.text = re.sub(r"^\s*-?\s*(.*)\s*[\n\s]\s*-\s*(.+)\s*$",
                                r"- \1    - \2", e.text, re.M)
                e.text = re.sub(r"^\s*(.*)\s*\n\s*(.+)\s*$",
                                r"\1 \2", e.text, re.M)
            for e in self.hanzi_subtitles.events:
                e.text = re.sub(r"^\s*﹣?\s*(.*)\s+﹣(.+)\s*$",
                                r"﹣\1　　﹣\2", e.text, re.M)
                e.text = re.sub(r"^\s*(.*)\s*\n\s*(.+)\s*$",
                                r"\1　\2", e.text, re.M)
            english_df = self.english_subtitles.get_dataframe()
            hanzi_df = self.hanzi_subtitles.get_dataframe()

            merged_df = self.merge_subtitles(hanzi_df, english_df)
            merged_df = self.merge_chinese_english_2(merged_df)

            # merged_df = merge_subtitles(self.hanzi_subtitles,
            #                             self.english_subtitles)
            merged_df["text"] = [f"{e['upper text']}\n{e['lower text']}"
                                 for _, e in merged_df.iterrows()]
            self.bilingual_subtitles = SubtitleSeries.from_dataframe(merged_df)
            self.bilingual_subtitles.save("$HOME/ZE.srt")

    # endregion

    # region Properties

    @property
    def bilingual_subtitles(self):
        """SubtitleSeries: Bilingual subtitles"""
        if not hasattr(self, "_bilingual_subtitles"):
            self._bilingual_subtitles = None
        return self._bilingual_subtitles

    @bilingual_subtitles.setter
    def bilingual_subtitles(self, value):
        if not isinstance(value, SubtitleSeries):
            raise ValueError(self._generate_setter_exception(value))
        self._bilingual_subtitles = value

    @property
    def english_subtitles(self):
        """SubtitleSeries: English subtitles"""
        if not hasattr(self, "_english_subtitles"):
            self._english_subtitles = None
        return self._english_subtitles

    @english_subtitles.setter
    def english_subtitles(self, value):
        if not isinstance(value, SubtitleSeries):
            raise ValueError(self._generate_setter_exception(value))
        self._english_subtitles = value

    @property
    def hanzi_subtitles(self):
        """SubtitleSeries: Hanzi Chinse subtitles"""
        if not hasattr(self, "_hanzi_subtitles"):
            self._hanzi_subtitles = None
        return self._hanzi_subtitles

    @hanzi_subtitles.setter
    def hanzi_subtitles(self, value):
        if not isinstance(value, SubtitleSeries):
            raise ValueError(self._generate_setter_exception(value))
        self._hanzi_subtitles = value

    @property
    def pinyin_subtitles(self):
        """SubtitleSeries: Romanized Chinese subtitles"""
        if not hasattr(self, "_pinyin_subtitles"):
            self._pinyin_subtitles = None
        return self._pinyin_subtitles

    @pinyin_subtitles.setter
    def pinyin_subtitles(self, value):
        if not isinstance(value, SubtitleSeries):
            raise ValueError(self._generate_setter_exception(value))
        self._pinyin_subtitles = value

    # endregion

    # region Old Properties
    # @property
    # def c_offset(self):
    #     """float: Time offset applied to Chinese subtitles (seconds)"""
    #     if not hasattr(self, "_c_offset"):
    #         self._c_offset = 0
    #     return self._c_offset
    #
    # @c_offset.setter
    # def c_offset(self, value):
    #     if value is None:
    #         value = 0
    #     elif not isinstance(value, float):
    #         try:
    #             value = float(value)
    #         except Exception as e:
    #             raise e
    #     self._c_offset = value
    #
    # @property
    # def cantonese(self):
    #     """bool: Add Cantonese romanzation to Chinese subtitles"""
    #     if not hasattr(self, "_cantonese"):
    #         self._cantonese = False
    #     return self._cantonese
    #
    # @cantonese.setter
    # def cantonese(self, value):
    #     if not isinstance(value, bool):
    #         raise ValueError()
    #     self._cantonese = value
    #
    # @property
    # def cantonese_corpus(self):
    #     """pycantonese.corpus.CantoneseCHATReader: Corpus for Cantonese
    #          romanization"""
    #     if not hasattr(self, "_cantonese_corpus"):
    #         import pycantonese as pc
    #         self._cantonese_corpus = pc.hkcancor()
    #         self._cantonese_corpus.add(
    #             f"{self.package_root}/data/romanization/unmatched.cha")
    #     return self._cantonese_corpus
    #
    # @property
    # def chinese(self):
    #     """bool: Chinese character subtitles present"""
    #     return self.chinese_infile is not None

    # @property
    # def e_offset(self):
    #     """float: Time offset applied to English subtitles (seconds)"""
    #     if not hasattr(self, "_e_offset"):
    #         self._e_offset = 0
    #     return self._e_offset
    #
    # @e_offset.setter
    # def e_offset(self, value):
    #     if value is None:
    #         value = 0
    #     elif not isinstance(value, float):
    #         try:
    #             value = float(value)
    #         except Exception as e:
    #             raise e
    #     self._e_offset = value
    #
    # @property
    # def english(self):
    #     """bool: English subtitles present"""
    #     return self.english_infile is not None
    #
    # @property
    # def mandarin(self):
    #     """bool: Add Mandarin romanization to Chinese subtitles"""
    #     if not hasattr(self, "_mandarin"):
    #         self._mandarin = False
    #     return self._mandarin
    #
    # @mandarin.setter
    # def mandarin(self, value):
    #     if not isinstance(value, bool):
    #         raise ValueError()
    #     self._mandarin = value
    #
    # @property
    # def outfile(self):
    #     """str: Path to output SRT file"""
    #     if not hasattr(self, "_outfile"):
    #         self._outfile = None
    #     return self._outfile
    #
    # @outfile.setter
    # def outfile(self, value):
    #     from os import access, W_OK
    #     from os.path import dirname, expandvars
    #
    #     if not isinstance(value, str) and value is not None:
    #         raise ValueError()
    #     else:
    #         value = expandvars(value)
    #         if dirname(value) != "" and not access(dirname(value), W_OK):
    #             raise ValueError()
    #
    #     self._outfile = value
    #
    # @property
    # def simplified(self):
    #     """bool: Convert traditional Chinese to simplified"""
    #     if not hasattr(self, "_simplified"):
    #         self._simplified = False
    #     return self._simplified
    #
    # @simplified.setter
    # def simplified(self, value):
    #     if not isinstance(value, bool):
    #         raise ValueError()
    #     self._simplified = value
    #
    # @property
    # def spacing(self):
    #     """string: Space between syllables or words of Mandarin romanization"""
    #     if not hasattr(self, "_spacing"):
    #         self._spacing = "words"
    #     return self._spacing
    #
    # @spacing.setter
    # def spacing(self, value):
    #     if value not in ["words", "syllables"]:
    #         raise ValueError()
    #     self._spacing = value
    #
    # @property
    # def translate(self):
    #     """bool: Add English translation to Chinese subtitles"""
    #     if not hasattr(self, "_translate"):
    #         self._translate = False
    #     return self._translate
    #
    # @translate.setter
    # def translate(self, value):
    #     if not isinstance(value, bool):
    #         raise ValueError()
    #     self._translate = value
    #
    # @property
    # def translate_client(self):
    #     """google.cloud.translate_v2.client.Client: Google Translate client"""
    #     if not hasattr(self, "_translate_client"):
    #         from google.cloud import translate
    #         self._translate_client = translate.Client()
    #     return self._translate_client
    #
    # @property
    # def truecase(self):
    #     """bool: Apply standard capitalization to English subtitles"""
    #     if not hasattr(self, "_truecase"):
    #         self._truecase = False
    #     return self._truecase
    #
    # @truecase.setter
    # def truecase(self, value):
    #     if not isinstance(value, bool):
    #         raise ValueError()
    #     self._truecase = value

    # endregion Properties

    # region Old Methods
    # def add_cantonese_romanization(self, subtitles):
    #     import pycantonese as pc
    #     from collections import Counter
    #     from hanziconv import HanziConv
    #
    #     def identify_cantonese_romanization(character):
    #         matches = self.cantonese_corpus.search(character=character)
    #
    #         if len(matches) == 0:
    #             # Character not found in corpus, search for traditional version
    #             traditional_character = HanziConv.toTraditional(character)
    #             if traditional_character != character:
    #                 if self.verbosity >= 3:
    #                     print(
    #                         f"{character} not found, searching for traditional")
    #                 return identify_cantonese_romanization(
    #                     traditional_character)
    #
    #             # Truly no instance of character in corpus
    #             if self.verbosity >= 1:
    #                 print(f"{character} not found in corpus")
    #             return None
    #
    #         # If character is found in corpus alone, use most common instance
    #         character_matches = [m[2] for m in matches if len(m[0]) == 1]
    #         if len(character_matches) > 0:
    #             jyutping = Counter(character_matches).most_common(1)[0][0]
    #             if self.verbosity >= 3:
    #                 print(f"{character} found as single character")
    #
    #         # If character is not found in corpus alone, use most common word
    #         else:
    #             most_common_word = Counter(matches).most_common(1)[0][0]
    #             index = most_common_word[0].index(character)
    #             jyutping = self.re_jyutping.findall(most_common_word[2])[index]
    #             if self.verbosity >= 3:
    #                 print(f"{character} found in word")
    #
    #         try:
    #             yale = pc.jyutping2yale(jyutping)
    #         except ValueError:
    #             if self.verbosity >= 1:
    #                 print(
    #                     f"{character} found but could not be converted from jyutping to Yale")
    #             return None
    #         return yale
    #
    #     if self.verbosity >= 1:
    #         print("Adding Cantonese romanization")
    #
    #     romanizations = []
    #     character_to_cantonese = {}
    #     unmatched = set()
    #
    #     for index, subtitle in subtitles.iterrows():
    #         text = subtitle.text
    #         if self.verbosity >= 2:
    #             start = subtitle.start.strftime("%H:%M:%S,%f")[:-3]
    #             end = subtitle.end.strftime("%H:%M:%S,%f")[:-3]
    #             print(f"{index}\n{start} --> {end}\n{text}")
    #
    #         romanization = ""
    #         for character in text:
    #             if (self.re_hanzi.match(character)
    #                     or self.re_hanzi_rare.match(character)):
    #                 if character in character_to_cantonese:
    #                     yale = character_to_cantonese[character]
    #                     romanization += " " + yale
    #                     continue
    #                 elif character in unmatched:
    #                     romanization += " " + character
    #                     continue
    #                 else:
    #                     yale = identify_cantonese_romanization(character)
    #                     if yale is not None:
    #                         romanization += " " + yale
    #                         character_to_cantonese[character] = yale
    #                     else:
    #                         romanization += " " + character
    #                         unmatched.add(character)
    #             elif self.re_western.match(character):
    #                 romanization += character
    #                 continue
    #             elif character in self.punctuation:
    #                 romanization = romanization.strip() + self.punctuation[
    #                     character]
    #                 continue
    #             else:
    #                 if self.verbosity >= 1:
    #                     print(
    #                         f"{character} is unrecognized as Chinese, western, or punctuation")
    #                     unmatched.add(character)
    #                 continue
    #
    #         romanization = romanization.strip().replace("\n ", "\n")
    #         romanizations += [romanization]
    #         if self.verbosity >= 2:
    #             print(f"{romanization}\n")
    #
    #     subtitles["cantonese"] = pd.Series(romanizations,
    #                                        index=subtitles.index)
    #     if self.verbosity >= 1 and len(unmatched) > 0:
    #         print(
    #             f"The following {len(unmatched)} characters were not "
    #             f"recognized:")
    #         print("".join(unmatched))
    #
    # def add_english_translation(self, subtitles):
    #
    #     if self.verbosity >= 1:
    #         print("Adding English translation")
    #
    #     translations = []
    #     for i in range(0, len(subtitles), 100):
    #         translations += [c["translatedText"] for c in
    #                          self.translate_client.translate(
    #                              list(subtitles.iloc[i:i + 100].text),
    #                              source_language="zh",
    #                              target_language="en")]
    #     subtitles["translation"] = pd.Series(translations,
    #                                          index=subtitles.index)
    #
    #     if self.verbosity >= 2:
    #         for index, subtitle in subtitles.iterrows():
    #             start = subtitle.start.strftime("%H:%M:%S,%f")[:-3]
    #             end = subtitle.end.strftime("%H:%M:%S,%f")[:-3]
    #             print(f"{index}\n{start} --> {end}\n{subtitle.text}\n"
    #                   f"{subtitle.translation}\n")
    #
    # def add_mandarin_romanization(self, subtitles):
    #     from snownlp import SnowNLP
    #     from pypinyin import pinyin
    #
    #     if self.verbosity >= 1:
    #         print("Adding Mandarin romanization")
    #
    #     romanizations = []
    #
    #     for index, subtitle in subtitles.iterrows():
    #         text = subtitle["text"]
    #
    #         if self.verbosity >= 2:
    #             start = subtitle.start.strftime("%H:%M:%S,%f")[:-3]
    #             end = subtitle.end.strftime("%H:%M:%S,%f")[:-3]
    #             print(f"{index}\n{start} --> {end}\n{text}")
    #
    #         romanization = ""
    #         if self.spacing == "words":
    #             for line in text.split("\n"):
    #                 line_romanization = ""
    #                 for section in line.split():
    #                     section_romanization = ""
    #                     for word in SnowNLP(section).words:
    #                         if word in self.punctuation:
    #                             section_romanization += \
    #                                 self.punctuation[word]
    #                         else:
    #                             section_romanization += " " + "".join(
    #                                 [a[0] for a in pinyin(word)])
    #                     line_romanization += "  " + section_romanization.strip()
    #                 romanization += "\n" + line_romanization.strip()
    #         romanization = romanization.strip()
    #
    #         romanizations += [romanization]
    #
    #         if self.verbosity >= 2:
    #             print(f"{romanization}\n")
    #
    #     subtitles["mandarin"] = pd.Series(romanizations,
    #                                       index=subtitles.index)
    #
    # def apply_offset(self, subtitles, offset):
    #     from datetime import timedelta
    #     from datetime import date
    #     from datetime import datetime
    #
    #     if self.verbosity >= 1:
    #         print(f"Applying offset of {offset} seconds")
    #
    #     offset = timedelta(seconds=offset)
    #     subtitles["start"] = subtitles["start"].apply(
    #         lambda s: (datetime.combine(date.today(), s) + offset).time())
    #     subtitles["end"] = subtitles["end"].apply(
    #         lambda s: (datetime.combine(date.today(), s) + offset).time())
    #     return subtitles
    #
    # def apply_truecase(self, subtitles):
    #     import nltk
    #     import re
    #
    #     if self.verbosity >= 1:
    #         print("Applying truecase to English subtitles")
    #
    #     for index, subtitle in subtitles.iterrows():
    #         text = subtitle["text"]
    #
    #         if self.verbosity >= 2:
    #             start = subtitle.start.strftime("%H:%M:%S,%f")[:-3]
    #             end = subtitle.end.strftime("%H:%M:%S,%f")[:-3]
    #             print(f"{index}\n{start} --> {end}\n{text}")
    #
    #             tagged = nltk.pos_tag(
    #                 [word.lower() for word in nltk.word_tokenize(text)])
    #             normalized = [w.capitalize() if t in ["NN", "NNS"] else w
    #                           for (w, t) in tagged]
    #             normalized[0] = normalized[0].capitalize()
    #             truecased = re.sub(r" (?=[\.,'!?:;])", "",
    #                                ' '.join(normalized))
    #
    #             # Could probably use a more appropriate tokenization function,
    #             # but cleaning up in this way is fine for now.
    #             truecased = truecased.replace(" n't", "n't")
    #             truecased = truecased.replace(" i ", " I ")
    #             truecased = truecased.replace("``", "\"")
    #             truecased = truecased.replace("''", "\"")
    #             truecased = re.sub(
    #                 r"(\A\w)|(?<!\.\w)([\.?!] )\w|\w(?:\.\w)|(?<=\w\.)\w",
    #                 lambda s: s.group().upper(), truecased)
    #
    #             if self.verbosity >= 2:
    #                 print(f"{truecased}\n")
    #
    #             subtitle["text"] = truecased

    @staticmethod
    def merge_subtitles(upper, lower):
        def add_merged_subtitle():
            if start == time:
                return merged_subtitles
            return merged_subtitles.append(
                pd.concat([
                    pd.DataFrame.from_items(
                        [("start", [start]), ("end", [time])]),
                    current_upper_subtitle,
                    current_lower_subtitle],
                    axis=1),
                ignore_index=True)

        transitions = []
        for _, subtitle in upper.iterrows():
            transitions += [
                [subtitle["start"], "upper_start",
                 subtitle.drop(["start", "end"])],
                [subtitle["end"], "upper_end", None]]
        for _, subtitle in lower.iterrows():
            transitions += [
                [subtitle["start"], "lower_start",
                 subtitle.drop(["start", "end"])],
                [subtitle["end"], "lower_end", None]]
        transitions.sort()

        merged_subtitles = pd.DataFrame()

        start = current_upper_subtitle = current_lower_subtitle = None
        for time, kind, subtitle in transitions:
            if kind == "upper_start":
                if start is None:
                    # Transition from __ -> C_
                    pass
                else:
                    # Transition from _E -> CE
                    merged_subtitles = add_merged_subtitle()
                current_upper_subtitle = pd.DataFrame(
                    subtitle).transpose().reset_index(drop=True).rename(
                    columns={"text": "upper text"})
                start = time
            elif kind == "upper_end":
                merged_subtitles = add_merged_subtitle()
                current_upper_subtitle = None
                if current_lower_subtitle is None:
                    # Transition from C_ -> __
                    start = None
                else:
                    # Transition from CE -> _C
                    start = time
            elif kind == "lower_start":
                if start is None:
                    # Transition from __ -> _E
                    pass
                else:
                    # Transition from C_ -> CE
                    merged_subtitles = add_merged_subtitle()
                current_lower_subtitle = pd.DataFrame(
                    subtitle).transpose().reset_index(drop=True).rename(
                    columns={"text": "lower text"})
                start = time
            elif kind == "lower_end":
                merged_subtitles = add_merged_subtitle()
                current_lower_subtitle = None
                if current_upper_subtitle is None:
                    # Transition from _E -> __
                    start = None
                else:
                    # Transition from CE -> E_
                    start = time

        merged_subtitles = merged_subtitles[
            ["upper text", "lower text", "start", "end"]]
        merged_subtitles.index += 1

        return merged_subtitles

    @staticmethod
    def merge_chinese_english_2(merged):

        cleaned_subs = [merged.iloc[0].copy()]

        for index in range(1, merged.index.size):
            last = cleaned_subs[-1]
            next = merged.iloc[index].copy()
            # print(index, last.values, next.values)
            if last["upper text"] == next["upper text"]:
                if isinstance(last["lower text"], float) and np.isnan(
                        last["lower text"]):
                    # Chinese started before English
                    last["lower text"] = next["lower text"]
                    last["end"] = next["end"]
                elif isinstance(next["lower text"], float) and np.isnan(
                        next["lower text"]):
                    # English started before Chinese
                    last["end"] = next["end"]
                else:
                    # Single Chinese subtitle given two English subtitles
                    gap = next["start"] - last["end"]
                    if gap < 500:
                        # Probably long Chinese split into two English
                        last["end"] = next["start"] = last["end"] + (gap / 2)
                        cleaned_subs += [next]
                    else:
                        # Probably Chinese repeated with different English
                        cleaned_subs += [next]
            elif last["lower text"] == next["lower text"]:
                if isinstance(last["upper text"], float) and np.isnan(
                        last["upper text"]):
                    # English started before Chinese
                    last["upper text"] = next["upper text"]
                    last["end"] = next["end"]
                elif isinstance(next["upper text"], float) and np.isnan(
                        next["upper text"]):
                    # Chinese started before English
                    if last.end < next["start"]:
                        cleaned_subs += [next]
                    else:
                        last["end"] = next["end"]
                else:
                    gap = next["start"] - last["end"]
                    if gap < 500:
                        # Probably long English split into two Chinese
                        last["end"] = next["start"] = last["end"] + (gap / 2)
                        cleaned_subs += [next]
                    else:
                        # Probably English repeated with different Chinese
                        cleaned_subs += [next]
            else:
                cleaned_subs += [next]

        cleaned_subs = pd.DataFrame(cleaned_subs)

        return cleaned_subs

    # def simplify(self, subtitles):
    #     from hanziconv import HanziConv
    #
    #     if self.verbosity >= 1:
    #         print("Converting traditional characters to simplified")
    #
    #     for index, subtitle in subtitles.iterrows():
    #         text = subtitle["text"]
    #
    #         if self.verbosity >= 2:
    #             start = subtitle.start.strftime("%H:%M:%S,%f")[:-3]
    #             end = subtitle.end.strftime("%H:%M:%S,%f")[:-3]
    #             print(f"{index}\n{start} --> {end}\n{text}")
    #
    #         simplified = ""
    #         for character in text:
    #             if (self.re_hanzi.match(character)
    #                     or self.re_hanzi_rare.match(character)):
    #                 simplified += HanziConv.toSimplified(character)
    #             else:
    #                 simplified += character
    #
    #         if self.verbosity >= 2:
    #             print(f"{simplified}\n")
    #
    #         subtitle["text"] = simplified

    # endregion

    # region Class Methods
    @classmethod
    def construct_argparser(cls, parser=None):
        """
        Constructs argument parser

        Returns:
            parser (argparse.ArgumentParser): Argument parser
        """
        import argparse

        # Prepare parser
        if isinstance(parser, argparse.ArgumentParser):
            parser = parser
        elif isinstance(parser, argparse._SubParsersAction):
            parser = parser.add_parser(name="extraction",
                                       description=cls.help_message,
                                       help=cls.help_message)
        elif parser is None:
            parser = argparse.ArgumentParser(description=cls.help_message)
        super().construct_argparser(parser)

        # Input
        parser_file = parser.add_argument_group(
            "file arguments (at least one required)")
        parser_file.add_argument("-b", "--bilingual", type=str,
                                 nargs="?", default=False, const=True,
                                 metavar="FILE",
                                 help="Bilingual subtitles")
        parser_file.add_argument("-c", "--chinese", "--hanzi", type=str,
                                 nargs="?", default=False, const=True,
                                 metavar="FILE", dest="hanzi",
                                 help="Chinese Hanzi subtitles")
        parser_file.add_argument("-e", "--english", type=str,
                                 nargs="?", default=False, const=True,
                                 metavar="FILE",
                                 help="English subtitles")
        parser_file.add_argument("-p", "--pinyin", type=str,
                                 nargs="?", default=False, const=True,
                                 metavar="FILE",
                                 help="Chinese Pinyin subtitles")

        # Operation
        # parser_ops = parser.add_argument_group("operation arguments")
        # parser_ops.add_argument("--c_offset", type=float, default=0,
        #                         help="apply offset to Chinese subtitle "
        #                              "timings")
        # parser_ops.add_argument("-s", "--simplified", action="store_true",
        #                         help="convert traditional characters to "
        #                              "simplified")
        # parser_ops.add_argument("-m", "--mandarin", action="store_true",
        #                         help="add Mandarin Hanyu pinyin (汉语拼音)")
        # parser_ops.add_argument("-y", "--yue", action="store_true",
        #                         dest="cantonese",
        #                         help="add Cantonese Yale pinyin (耶鲁粤语拼音)")
        # parser_ops.add_argument("-t", "--translate", action="store_true",
        #                         dest="translate",
        #                         help="add English machine translation "
        #                              "generated using Google Translate; "
        #                              "requires key for Google Cloud Platform")
        # parser_ops.add_argument("--e_offset", type=float, default=0,
        #                         help="apply offset to English subtitle "
        #                              "timings")
        # parser_ops.add_argument("--truecase", action="store_true",
        #                         help="apply standard capitalization to "
        #                              "English subtitles")

        return parser

    @classmethod
    def validate_args(cls, parser, args):
        """
        Validates arguments

        Args:
            parser (argparse.ArgumentParser): Argument parser
            args (argparse.Namespace): Arguments

        Raises:
            ValueError: Incompatibility between provided arguments

        """
        from io import StringIO

        with StringIO() as helptext:
            parser.print_help(helptext)
            try:
                pass
            # if args.chinese_infile is None and args.english_infile is None:
            #     raise ValueError("Either argument '-c/--chinese_infile' "
            #                      "or '-e/--english_infile' is required")
            # if args.chinese_infile is None:
            #     if args.c_offset != 0:
            #         raise ValueError("Argument '--c_offset' requires "
            #                          "argument '-c/--chinese_infile'")
            #     if args.simplified:
            #         raise ValueError("Argument '-s' requires "
            #                          "argument '-c/--chinese_infile'")
            #     if args.mandarin:
            #         raise ValueError("Argument '-m' requires "
            #                          "argument '-c/--chinese_infile'")
            #     if args.cantonese:
            #         raise ValueError("Argument '-y' requires "
            #                          "argument '-c/--chinese_infile'")
            #     if args.translate:
            #         raise ValueError("Argument '-t' requires "
            #                          "argument '-c/--chinese_infile'")
            # if args.english_infile is None:
            #     if args.e_offset != 0:
            #         raise ValueError("Argument '--e_offset' requires "
            #                          "argument '-e/--english_infile'")
            #     if args.truecase:
            #         raise ValueError("Argument '--truecase' requires "
            #                          "argument '-e/--english_infile'")
            # if args.english_infile is not None:
            #     if args.translate:
            #         raise ValueError("Argument '-t' incompatible with "
            #                          "argument '-e/--english_infile'")
            except ValueError as e:
                print(helptext.getvalue())
                raise e

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    Compositor.main()
