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
import pandas as pd
from collections import OrderedDict
from os.path import expandvars, isfile
from IPython import embed
from scinoephile import (get_pinyin, get_simplified_hanzi,
                         get_single_line_text, get_truecase, merge_subtitles,
                         CLToolBase, SubtitleSeries)

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

    # region Instance Variables
    help_message = ("Compiles Chinese and English subtitles into a single "
                    "file, optionally adding Mandarin or Cantonese "
                    "romanization, converting traditional characters to "
                    "simplified, or adding machine translation.")

    # endregion

    # region Builtins
    def __init__(self, bilingual=False, english=False, hanzi=False,
                 pinyin=False, simplify=True, pinyin_language="mandarin",
                 **kwargs):
        """
        Initializes tool

        Args:
            bilingual (str): Path to bilingual infile or outfile
            english (str): Path to English infile or outfile
            hanzi (str): Path to hanzi Chinese infile or outfile
            pinyin (str): Path to pinyin Chinese infile or outfile
            **kwargs: Additional keyword arguments
        """

        super().__init__(**kwargs)

        # Read in files if they exist
        if bilingual and isinstance(bilingual, str):
            bilingual = expandvars(bilingual)
            if isfile(bilingual):
                self.operations["read_bilingual"] = bilingual
            else:
                self.operations["write_bilingual"] = bilingual
        if english and isinstance(english, str):
            english = expandvars(english)
            if isfile(english):
                self.operations["read_english"] = english
            else:
                self.operations["write_english"] = english
        if hanzi and isinstance(hanzi, str):
            hanzi = expandvars(hanzi)
            if isfile(hanzi):
                self.operations["read_hanzi"] = hanzi
            else:
                self.operations["write_hanzi"] = hanzi
        if pinyin and isinstance(pinyin, str):
            pinyin = expandvars(pinyin)
            if isfile(pinyin):
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
                self.operations["translate_hanzi"] = True
            else:
                raise ValueError()
        if ("write_pinyin" in self.operations
                and "read_pinyin" not in self.operations):
            if ("read_hanzi" in self.operations
                    or "translate_hanzi" in self.operations):
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
                    or "translate_hanzi" in self.operations):
                self.operations["simplify_chinese"] = True
            else:
                raise ValueError()

    def __call__(self):
        """
        Core logic
        """
        print(self.operations)

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
            if (isinstance(self.hanzi_subtitles, SubtitleSeries)
                    and isinstance(self.english_subtitles, SubtitleSeries)):
                self._initialize_bilingual_subtitles()
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
            if isinstance(self.hanzi_subtitles, SubtitleSeries):
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
            if isinstance(self.english_subtitles, SubtitleSeries):
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
        if not hasattr(self, "_operations"):
            self._operations = OrderedDict()
        return self._operations

    @property
    def pinyin_subtitles(self):
        """SubtitleSeries: Romanized Chinese subtitles"""
        if not hasattr(self, "_pinyin_subtitles"):
            if isinstance(self.hanzi_subtitles, SubtitleSeries):
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
        merged_df["text"] = [f"{e['upper text']}\n{e['lower text']}"
                             for _, e in merged_df.iterrows()]

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
            if language == "mandarin":
                event.text = get_pinyin(event.text, "mandarin")
            elif language == "cantonese":
                event.text = get_pinyin(event.text, "cantonese")

    def _convert_traditional_to_simplified_hanzi(self):

        # Process arguments
        if self.hanzi_subtitles is None:
            raise ValueError("Conversion of traditional hanzi to simplified "
                             "requires initialized hanzi subtitles")

        if self.verbosity >= 1:
            print("Converting traditional characters to simplified")

        for event in self._hanzi_subtitles:
            event.text = get_simplified_hanzi(event.text)

    def _convert_capital_english_to_truecase(self):

        # Process arguments
        if self.english_subtitles is None:
            raise ValueError("Conversion of capitalized English to truecase "
                             "requires initialized English subtitles")

        if self.verbosity >= 1:
            print("Converting capitalized English to truecase")

        for event in self._english_subtitles:
            event.text = get_truecase(event.text)

    def _translate_chinese_to_english(self):
        from copy import deepcopy
        from scinoephile.translation import client

        # Process arguments
        if self.hanzi_subtitles is None:
            raise ValueError("Initialization of English translation requires "
                             "initialized hanzi subtitles")

        if self.verbosity >= 1:
            print("Initializing English translation")

        # Copy and translate
        self._english_subtitles = deepcopy(self.hanzi_subtitles)
        texts = [e.text for e in self._english_subtitles.events]
        translations = []
        for i in range(0, len(texts), 100):
            translations += [e["translatedText"] for e in
                             client.translate(list(texts[i:i + 100]),
                                              source_language="zh",
                                              target_language="en")]
        for i, translation in enumerate(translations):
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

        # Copy and translate
        self._hanzi_subtitles = deepcopy(self.english_subtitles)
        texts = [e.text for e in self._hanzi_subtitles.events]
        translations = []
        for i in range(0, len(texts), 100):
            translations += [e["translatedText"] for e in
                             client.translate(list(texts[i:i + 100]),
                                              source_language="en",
                                              target_language="zh")]
        for i, translation in enumerate(translations):
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

        # Files
        parser_file = parser.add_argument_group("file arguments")
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
