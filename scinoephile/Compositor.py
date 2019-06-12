#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.Compositor.py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Compiles Chinese and English subtitles into a single file, optionally adding
Mandarin or Cantonese pinyin, converting traditional characters to simplified,
or adding machine translation.

Operations are inferred from provided arguments, e.g.:

  Translate Chinese to English:
    Compositor.py -e /nonexisting/english/outfile
                  -c /existing/chinese/infile

  Translate English to Chinese:
    Compositor.py -e /existing/english/infile
                  -c /nonexisting/chinese/outfile

  Merge Chinese and English:
    Compositor.py -e /existing/english/infile
                  -c /existing/chinese/infile
                  -b /nonexisting/bilingual/outfile

  Convert traditional Chinese to simplified, translate to English, and merge:
    Compositor.py -c /existing/chinese/infile
                  -b /nonexisting/bilingual/outfile
                  --simplify
"""
################################### MODULES ###################################
import numpy as np
import pandas as pd
from os.path import expandvars, isfile
from IPython import embed
from scinoephile import (get_pinyin, get_simplified_hanzi,
                         get_single_line_text, get_truecase, merge_subtitles,
                         CLToolBase, Metavar, SubtitleSeries)


################################### CLASSES ###################################
class Compositor(CLToolBase):
    """
    Compiles Chinese and English subtitles
    """

    # region Builtins

    def __init__(self, bilingual=False, bilingual_overwrite=False,
                 english=False, english_overwrite=False, hanzi=False,
                 hanzi_overwrite=False, pinyin=False, pinyin_overwrite=False,
                 simplify=False, pinyin_language="mandarin", **kwargs):
        """
        Initializes command-line tool and selects operations

        Args:
            bilingual (str): Path to bilingual infile or outfile
            bilingual_overwrite (bool): Overwrite bilingual file
            english (str): Path to English infile or outfile
            english_overwrite (bool): Overwrite English file
            hanzi (str): Path to hanzi Chinese infile or outfile
            hanzi_overwrite (bool): Overwrite hanzi Chinese file
            pinyin (str): Path to pinyin Chinese infile or outfile
            pinyin_overwrite (bool): Overwrite pinyin Chinese file
            simplify (bool): Convert traditional hanzi to simplified
            pinyin_language (str): Langauge for which to add pinyin; may be
              'madarin' or 'cantonese'
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)
        # embed(**self.embed_kw)

        # Read in files if they exist
        if bilingual and isinstance(bilingual, str):
            bilingual = expandvars(bilingual)
            if isfile(bilingual) and not bilingual_overwrite:
                self.operations["read_bilingual"] = bilingual
            else:
                self.operations["write_bilingual"] = bilingual
        if english and isinstance(english, str):
            english = expandvars(english)
            if isfile(english) and not english_overwrite:
                self.operations["read_english"] = english
            else:
                self.operations["write_english"] = english
        if hanzi and isinstance(hanzi, str):
            hanzi = expandvars(hanzi)
            if isfile(hanzi) and not hanzi_overwrite:
                self.operations["read_hanzi"] = hanzi
            else:
                self.operations["write_hanzi"] = hanzi
        if pinyin and isinstance(pinyin, str):
            pinyin = expandvars(pinyin)
            if isfile(pinyin) and not pinyin_overwrite:
                self.operations["read_pinyin"] = pinyin
            else:
                self.operations["write_pinyin"] = pinyin

        # Create subtitles if they do not exist
        if ("write_english" in self.operations
                and "read_english" not in self.operations):
            if "read_hanzi" in self.operations:
                self.operations["translate_english"] = True
            else:
                raise ValueError()
        if ("write_hanzi" in self.operations
                and "read_hanzi" not in self.operations):
            if "read_english" in self.operations:
                self.operations["translate_chinese"] = True
            else:
                raise ValueError()
        if ("write_pinyin" in self.operations
                and "read_pinyin" not in self.operations):
            if ("read_hanzi" in self.operations
                    or "translate_chinese" in self.operations):
                self.operations[f"convert_pinyin_{pinyin_language}"] = True
            else:
                raise ValueError()
        if ("write_bilingual" in self.operations
                and "read_bilingual" not in self.operations):
            if "read_english" not in self.operations:
                if "read_hanzi" in self.operations:
                    self.operations["translate_english"] = True
                else:
                    raise ValueError()
            if "read_hanzi" not in self.operations:
                if "read_english" in self.operations:
                    self.operations["translate_english"] = True
                else:
                    raise ValueError()
            self.operations["merge_bilingual"] = True

        # Perform additional operations
        if simplify:
            if ("read_hanzi" in self.operations
                    or "translate_chinese" in self.operations):
                self.operations["simplify_chinese"] = True
            else:
                raise ValueError()

    def __call__(self):
        """
        Performs operations
        """

        # Read infiles
        if "read_bilingual" in self.operations:
            self.bilingual_subtitles = SubtitleSeries.load(
                self.operations["read_bilingual"], verbosity=self.verbosity)
        if "read_english" in self.operations:
            self.english_subtitles = SubtitleSeries.load(
                self.operations["read_english"], verbosity=self.verbosity)
        if "read_hanzi" in self.operations:
            self.hanzi_subtitles = SubtitleSeries.load(
                self.operations["read_hanzi"], verbosity=self.verbosity)
        if "read_pinyin" in self.operations:
            self.pinyin_subtitles = SubtitleSeries.load(
                self.operations["read_pinyin"], verbosity=self.verbosity)

        # Perform operations
        if "translate_english" in self.operations:
            self._translate_chinese_to_english()
        if "translate_chinese" in self.operations:
            self._translate_english_to_chinese()
        if "simplify_chinese" in self.operations:
            self._convert_traditional_to_simplified_hanzi()
        if "convert_pinyin_mandarin" in self.operations:
            self._initialize_pinyin_subtitles("mandarin")
        if "convert_pinyin_cantonese" in self.operations:
            self._initialize_pinyin_subtitles("cantonese")
        if "merge_bilingual" in self.operations:
            self._initialize_bilingual_subtitles()

        # Write outfiles
        if "write_bilingual" in self.operations:
            self.bilingual_subtitles.save(self.operations["write_bilingual"])
        if "write_english" in self.operations:
            self.english_subtitles.save(self.operations["write_english"])
        if "write_hanzi" in self.operations:
            self.hanzi_subtitles.save(self.operations["write_hanzi"])
        if "write_pinyin" in self.operations:
            self.pinyin_subtitles.save(self.operations["write_pinyin"])

    # endregion

    # region Properties

    @property
    def bilingual_subtitles(self):
        """SubtitleSeries: Bilingual subtitles"""
        if not hasattr(self, "_bilingual_subtitles"):
            if (hasattr(self, "_english_subtitles")
                    and self.english_subtitles is not None):
                if (hasattr(self, "_hanzi_subtitles")
                        and self.hanzi_subtitles is not None):
                    self._initialize_bilingual_subtitles("hanzi")
                elif (hasattr(self, "_pinyin_subtitles")
                      and self.pinyin_subtitles is not None):
                    self._initialize_bilingual_subtitles("pinyin")
                else:
                    self._bilingual_subtitles = None
            else:
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
            if (hasattr(self, "_hanzi_subtitles")
                    and self.hanzi_subtitles is not None):
                self._translate_chinese_to_english()
            else:
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
            if (hasattr(self, "_english_subtitles")
                    and self.english_subtitles is not None):
                self._translate_english_to_chinese()
            else:
                self._hanzi_subtitles = None
        return self._hanzi_subtitles

    @hanzi_subtitles.setter
    def hanzi_subtitles(self, value):
        if not isinstance(value, SubtitleSeries):
            raise ValueError(self._generate_setter_exception(value))
        self._hanzi_subtitles = value

    @property
    def operations(self):
        """dict: Collection of operations to perform, with associated
        arguments"""
        if not hasattr(self, "_operations"):
            self._operations = {}
        return self._operations

    @property
    def pinyin_subtitles(self):
        """SubtitleSeries: Pinyin Chinese subtitles"""
        if not hasattr(self, "_pinyin_subtitles"):
            if (hasattr(self, "_hanzi_subtitles")
                    and self.hanzi_subtitles is not None):
                self._initialize_pinyin_subtitles()
            else:
                self._pinyin_subtitles = None
        return self._pinyin_subtitles

    @pinyin_subtitles.setter
    def pinyin_subtitles(self, value):
        if not isinstance(value, SubtitleSeries):
            raise ValueError(self._generate_setter_exception(value))
        self._pinyin_subtitles = value

    # endregion

    # region Private Methods

    def _convert_traditional_to_simplified_hanzi(self):

        # Process arguments
        if self.hanzi_subtitles is None:
            raise ValueError("Conversion of traditional hanzi to simplified "
                             "requires initialized hanzi subtitles")

        if self.verbosity >= 1:
            print("Converting traditional characters to simplified")

        for event in self._hanzi_subtitles:
            event.text = get_simplified_hanzi(event.text, self.verbosity)

    def _convert_capital_english_to_truecase(self):

        # Process arguments
        if self.english_subtitles is None:
            raise ValueError("Conversion of capitalized English to truecase "
                             "requires initialized English subtitles")

        if self.verbosity >= 1:
            print("Converting capitalized English to truecase")

        for event in self._english_subtitles:
            event.text = get_truecase(event.text)

    def _initialize_bilingual_subtitles(self, chinese="hanzi"):
        from copy import deepcopy

        # Process arguments
        if self.english_subtitles is None:
            raise ValueError("Initialization of bilingual subtitles requires "
                             "initialized English subtitles")
        if (chinese == "hanzi" and self.hanzi_subtitles is None
                or (chinese == "pinyin" and self.pinyin_subtitles is None)):
            raise ValueError("Initialization of bilingual subtitles requires "
                             "initialized Chinese subtitles")
        if chinese == "hanzi":
            chinese_subtitles = deepcopy(self.hanzi_subtitles)
        elif chinese == "pinyin":
            chinese_subtitles = deepcopy(self.pinyin_subtitles)
        else:
            raise ValueError("Invalid value provided for argument 'chinese'; "
                             "must be 'hanzi' or 'pinyin'")
        english_subtitles = deepcopy(self.english_subtitles)

        if self.verbosity >= 1:
            print("Preparing bilingual subtitles")

        # Convert each language to a single line
        if chinese == "hanzi":
            for e in chinese_subtitles.events:
                e.text = get_single_line_text(e.text, "hanzi")
        elif chinese == "pinyin":
            for e in chinese_subtitles.events:
                e.text = get_single_line_text(e.text, "pinyin")
        for e in english_subtitles.events:
            e.text = get_single_line_text(e.text, "english")

        # Merge
        merged_df = merge_subtitles(chinese_subtitles,
                                    english_subtitles)
        merged_text = []
        for _, e in merged_df.iterrows():
            if (isinstance(e["upper text"], float)
                    and np.isnan(e["upper text"])):
                merged_text += [e['lower text']]
            elif (isinstance(e["lower text"], float)
                  and np.isnan(e["lower text"])):
                merged_text += [e["upper text"]]
            else:
                merged_text += [f"{e['upper text']}\n{e['lower text']}"]
        merged_df["text"] = merged_text

        self._bilingual_subtitles = SubtitleSeries.from_dataframe(merged_df)

    def _initialize_pinyin_subtitles(self, language="mandarin"):
        from copy import deepcopy

        # Process arguments
        if self.hanzi_subtitles is None:
            raise ValueError("Initialization of pinyin subtitles requires "
                             "initialized hanzi subtitles")
        if language not in ["cantonese", "mandarin"]:
            raise ValueError("Invalid value provided for argument 'language'; "
                             "must of 'cantonese' or 'mandarin'")

        if self.verbosity >= 1:
            if language == "mandarin":
                print("Adding Mandarin romanization")
            elif language == "cantonese":
                print("Adding Cantonese romanization")

        # Copy and convert to pinyin
        self._pinyin_subtitles = deepcopy(self.hanzi_subtitles)
        for event in self._pinyin_subtitles.events:
            event.text = get_pinyin(event.text, language,
                                    verbosity=self.verbosity)

    def _translate_chinese_to_english(self):
        from copy import deepcopy
        from scinoephile.translation import client

        # Process arguments
        if self.hanzi_subtitles is None:
            raise ValueError("Initialization of English translation requires "
                             "initialized hanzi subtitles")

        if self.verbosity >= 1:
            print("Initializing English translation")

        # Translate
        self._english_subtitles = deepcopy(self.hanzi_subtitles)
        texts = [e.text for e in self._english_subtitles.events]
        translations = []
        for i in range(0, len(texts), 100):
            translations += [e["translatedText"] for e in
                             client.translate(list(texts[i:i + 100]),
                                              source_language="zh",
                                              target_language="en")]
        for i, translation in enumerate(translations):
            if self.verbosity >= 2:
                print(f"{self._english_subtitles.events[i].text} -> "
                      f"{translation}")
            self._english_subtitles.events[i].text = translation

    def _translate_english_to_chinese(self):
        from copy import deepcopy
        from scinoephile.translation import client

        # Process arguments
        if self.english_subtitles is None:
            raise ValueError("Initialization of Chinese translation requires "
                             "initialized English subtitles")

        if self.verbosity >= 1:
            print("Initializing Chinese translation")

        # Translate
        self._hanzi_subtitles = deepcopy(self.english_subtitles)
        texts = [e.text for e in self._hanzi_subtitles.events]
        translations = []
        for i in range(0, len(texts), 100):
            translations += [e["translatedText"] for e in
                             client.translate(list(texts[i:i + 100]),
                                              source_language="en",
                                              target_language="zh")]
        for i, translation in enumerate(translations):
            if self.verbosity >= 2:
                print(f"{self._hanzi_subtitles.events[i].text} -> "
                      f"{translation}")
            self._hanzi_subtitles.events[i].text = translation

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

        if isinstance(parser, argparse.ArgumentParser):
            parser = parser
        elif isinstance(parser, argparse._SubParsersAction):
            parser = parser.add_parser(
                name=cls.__name__.lower(),
                description=__doc__,
                help=__doc__,
                formatter_class=argparse.RawDescriptionHelpFormatter)
        elif parser is None:
            parser = argparse.ArgumentParser(
                description=__doc__,
                formatter_class=argparse.RawDescriptionHelpFormatter)
        super().construct_argparser(parser)

        # Files
        parser_file = parser.add_argument_group("file arguments")
        parser_file.add_argument("-b", "--bilingual", type=str,
                                 nargs="+",
                                 action=cls.get_filepath_action(),
                                 metavar=Metavar(["FILE", "overwrite"]),
                                 help="bilingual subtitles")
        parser_file.add_argument("-c", "--chinese", type=str,
                                 nargs="+",
                                 action=cls.get_filepath_action(),
                                 metavar=Metavar(["FILE", "overwrite"]),
                                 dest="hanzi",
                                 help="Chinese Hanzi subtitles")
        parser_file.add_argument("-e", "--english", type=str,
                                 nargs="+",
                                 action=cls.get_filepath_action(),
                                 metavar=Metavar(["FILE", "overwrite"]),
                                 help="English subtitles")
        parser_file.add_argument("-p", "--pinyin", type=str,
                                 nargs="+",
                                 action=cls.get_filepath_action(),
                                 metavar=Metavar(["FILE", "overwrite"]),
                                 help="Chinese Pinyin subtitles")

        # Operation
        parser_ops = parser.add_argument_group("operation arguments")
        parser_ops.add_argument("-s", "--simplify", action="store_true",
                                help="convert traditional characters to "
                                     "simplified")
        parser_ops.add_argument("-m", "--mandarin", action="store_const",
                                dest="pinyin_language", default="mandarin",
                                const="mandarin",
                                help="add Mandarin Hanyu pinyin (汉语拼音)")
        parser_ops.add_argument("-y", "--yue", action="store_const",
                                dest="pinyin_language", const="cantonese",
                                help="add Cantonese Yale pinyin (耶鲁粤语拼音)")

        return parser

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    Compositor.main()
