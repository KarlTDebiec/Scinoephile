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

Operations are inferred from provided infiles and outfiles, e.g.:

  Merge Chinese and English:
    Compositor.py -cif /chinese/infile
                  -eif /english/infile
                  -bof /bilingual/outfile

  Convert Chinese Hanzi to Cantonese Yale pinyin:
    Compositor.py -cif /chinese/infile
                  -pof /chinese/outfile
                  --cantonese

  Translate Chinese Hanzi to English, overwriting if necessary:
    Compositor.py -cif /chinese/infile
                  -eof /english/outfile
                  -o

  Convert traditional Chinese to simplified, translate to English, and merge:
    Compositor.py -cif /chinese/infile
                  -bof /bilingual/outfile
                  --simplify
"""
################################### MODULES ###################################
import numpy as np
from scinoephile import (get_pinyin, get_simplified_hanzi,
                         get_single_line_text, get_truecase, merge_subtitles,
                         CLToolBase, SubtitleSeries)


################################### CLASSES ###################################
class Compositor(CLToolBase):
    """
    Combines Chinese and English subtitles into synchronized bilingual
    subtitles
    """

    # region Builtins

    def __init__(self, bilingual_infile=None, bilingual_outfile=None,
                 english_infile=None, english_outfile=None,
                 hanzi_infile=None, hanzi_outfile=None, overwrite=False,
                 pinyin_infile=None, pinyin_outfile=None,
                 pinyin_language=None, simplify=False, **kwargs):
        """
        Initializes command-line tool and compiles list of operations

        Args:
            bilingual_infile (str): Path to bilingual subtitle infile
            bilingual_outfile (str): Path to bilingual subtitle outfile
            english_infile (str): Path to English subtitle infile
            english_outfile (str): Path to English subtitle outfile
            hanzi_infile (str): Path to Chinese Hanzi subtitle infile
            hanzi_outfile (str): Path to Chinese Hanzi subtitle outfile
            overwrite (bool): Overwrite outfiles if they exist
            pinyin_infile (str): Path to pinyin Chinese subtitle infile
            pinyin_outfile (str): Path to pinyin Chinese subtitle outfile
            pinyin_language (bool, str): Langauge for which to add pinyin; may
              be 'mandarin' or 'cantonese'
            simplify (bool): Convert traditional Hanzi to simplified
            **kwargs: Additional keyword arguments
        """
        from os import access, environ, R_OK, W_OK
        from os.path import dirname, expandvars, isfile

        super().__init__(**kwargs)

        # Compile input operations
        if not (bilingual_infile or english_infile or hanzi_infile
                or pinyin_infile):
            raise ValueError("At least one infile required")
        if bilingual_infile:
            bilingual_infile = expandvars(str(bilingual_infile))
            if isfile(bilingual_infile) and access(bilingual_infile, R_OK):
                self.operations["load_bilingual"] = bilingual_infile
            else:
                raise IOError(f"Bilingual subtitle infile "
                              f"'{bilingual_infile}' cannot be read")
        if english_infile:
            english_infile = expandvars(str(english_infile))
            if isfile(english_infile) and access(english_infile, R_OK):
                self.operations["load_english"] = english_infile
            else:
                raise IOError(f"English subtitle infile "
                              f"'{english_infile}' cannot be read")
        if hanzi_infile:
            hanzi_infile = expandvars(str(hanzi_infile))
            if isfile(hanzi_infile) and access(hanzi_infile, R_OK):
                self.operations["load_hanzi"] = hanzi_infile
            else:
                raise IOError(f"Chinese Hanzi subtitle infile "
                              f"'{hanzi_infile}' cannot be read")
        if pinyin_infile:
            pinyin_infile = expandvars(str(pinyin_infile))
            if isfile(pinyin_infile) and access(pinyin_infile, R_OK):
                self.operations["load_pinyin"] = pinyin_infile
            else:
                raise IOError(f"Chinese pinyin subtitle infile "
                              f"'{pinyin_infile}' cannot be read")

        # Compile output operations
        if bilingual_outfile:
            bilingual_outfile = expandvars(str(bilingual_outfile))
            if access(dirname(bilingual_outfile), W_OK):
                if not isfile(bilingual_outfile) or overwrite:
                    self.operations["save_bilingual"] = bilingual_outfile
                else:
                    raise IOError(f"Bilingual subtitle outfile "
                                  f"'{bilingual_outfile}' already exists")
            else:
                raise IOError(f"Bilingual subtitle outfile "
                              f"'{bilingual_outfile}' is not writable")
        if english_outfile:
            english_outfile = expandvars(str(english_outfile))
            if access(dirname(english_outfile), W_OK):
                if not isfile(english_outfile) or overwrite:
                    self.operations["save_english"] = english_outfile
                else:
                    raise IOError(f"English subtitle outfile "
                                  f"'{english_outfile}' already exists")
            else:
                raise IOError(f"English subtitle outfile "
                              f"'{english_outfile}' is not writable")
        if hanzi_outfile:
            hanzi_outfile = expandvars(str(hanzi_outfile))
            if access(dirname(hanzi_outfile), W_OK):
                if not isfile(hanzi_outfile) or overwrite:
                    self.operations["save_hanzi"] = hanzi_outfile
                else:
                    raise IOError(f"Chinese Hanzi subtitle outfile "
                                  f"'{hanzi_outfile}' already exists")
            else:
                raise IOError(f"Chinese Hanzi subtitle outfile "
                              f"'{hanzi_outfile}' is not writable")
        if pinyin_outfile:
            pinyin_outfile = expandvars(str(pinyin_outfile))
            if access(dirname(pinyin_outfile), W_OK):
                if not isfile(pinyin_outfile) or overwrite:
                    self.operations["save_pinyin"] = pinyin_outfile
                else:
                    raise IOError(f"Chinese pinyin subtitle outfile "
                                  f"'{pinyin_outfile}' already exists")
            else:
                raise IOError(f"Chinese pinyin subtitle outfile "
                              f"'{pinyin_outfile}' is not writable")

        # Compile conversion operations
        if ("save_english" in self.operations
                and "load_english" not in self.operations):
            if "load_hanzi" in self.operations:
                if "GOOGLE_APPLICATION_CREDENTIALS" in environ:
                    self.operations["translate_english"] = True
                else:
                    raise ValueError("Transation requires that "
                                     "GOOGLE_APPLICATION_CREDENTIALS is "
                                     "set to the path to a Google service "
                                     "account key")
            else:
                raise ValueError("English subtitle output requires either "
                                 "English or Chinese Hanzi subtitle input")
        if ("save_hanzi" in self.operations
                and "load_hanzi" not in self.operations):
            if "load_english" in self.operations:
                if "GOOGLE_APPLICATION_CREDENTIALS" in environ:
                    self.operations["translate_chinese"] = True
                else:
                    raise ValueError("Transation requires that "
                                     "GOOGLE_APPLICATION_CREDENTIALS is "
                                     "set to the path to a Google service "
                                     "account key")
            else:
                raise ValueError("Chinese Hanzi subtitle output requires "
                                 "either Chinese Hanzi or English subtitle "
                                 "input")
            if simplify:
                if "load_hanzi" in self.operations:
                    self.operations["simplify_chinese"] = True
                else:
                    raise ValueError("Conversion to simplified Hanzi "
                                     "characters requires Chinese Hanzi "
                                     "subtitle input")
        if ("save_pinyin" in self.operations
                and "load_pinyin" not in self.operations):
            if ("load_hanzi" in self.operations
                    or "translate_chinese" in self.operations):
                if pinyin_language:
                    pinyin_language = str(pinyin_language).lower()
                    if pinyin_language in ["mandarin", "cantonese"]:
                        self.operations[f"convert_pinyin_{pinyin_language}"] \
                            = True
                    else:
                        raise ValueError(f"Pinyin language must be either "
                                         f"'mandarin' or 'cantonese'; "
                                         f"'{pinyin_language}' provided")
            else:
                raise ValueError("Chinese pinyin subtitle output requires "
                                 "either Chinese Hanzi, Chinese pinyin, or "
                                 "English subtitle input")
        if ("save_bilingual" in self.operations
                and "load_bilingual" not in self.operations):
            if "load_english" not in self.operations:
                if "load_hanzi" in self.operations:
                    if "GOOGLE_APPLICATION_CREDENTIALS" in environ:
                        self.operations["translate_english"] = True
                    else:
                        raise ValueError("Transation requires that "
                                         "GOOGLE_APPLICATION_CREDENTIALS is "
                                         "set to the path to a Google service "
                                         "account key")
                else:
                    raise ValueError("Bilingual subtitle output requires "
                                     "either Chinese Hanzi or English "
                                     "subtitle input")
            if "load_hanzi" not in self.operations:
                if "load_english" in self.operations:
                    if "GOOGLE_APPLICATION_CREDENTIALS" in environ:
                        self.operations["translate_english"] = True
                    else:
                        raise ValueError("Transation requires that "
                                         "GOOGLE_APPLICATION_CREDENTIALS is "
                                         "set to the path to a Google service "
                                         "account key")
                else:
                    raise ValueError("Bilingual subtitle output requires "
                                     "either Chinese Hanzi or English "
                                     "subtitle input")
            self.operations["merge_bilingual"] = True

    def __call__(self):
        """
        Performs operations
        """

        # Load infiles
        if "load_bilingual" in self.operations:
            self.bilingual_subtitles = SubtitleSeries.load(
                self.operations["load_bilingual"], verbosity=self.verbosity)
        if "load_english" in self.operations:
            self.english_subtitles = SubtitleSeries.load(
                self.operations["load_english"], verbosity=self.verbosity)
        if "load_hanzi" in self.operations:
            self.hanzi_subtitles = SubtitleSeries.load(
                self.operations["load_hanzi"], verbosity=self.verbosity)
        if "load_pinyin" in self.operations:
            self.pinyin_subtitles = SubtitleSeries.load(
                self.operations["load_pinyin"], verbosity=self.verbosity)

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

        # Save outfiles
        if "save_bilingual" in self.operations:
            self.bilingual_subtitles.save(self.operations["save_bilingual"])
        if "save_english" in self.operations:
            self.english_subtitles.save(self.operations["save_english"])
        if "save_hanzi" in self.operations:
            self.hanzi_subtitles.save(self.operations["save_hanzi"])
        if "save_pinyin" in self.operations:
            self.pinyin_subtitles.save(self.operations["save_pinyin"])

    # endregion

    # region Public Properties

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
        # TODO: Move most to language-independent function
        from copy import deepcopy
        from scinoephile.translation import client

        # Process arguments
        if self.hanzi_subtitles is None:
            raise ValueError("English translation requires Chinese subtitles "
                             "as source")

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
        # TODO: Move most to language-independent function
        from copy import deepcopy
        from scinoephile.translation import client

        # Process arguments
        if self.english_subtitles is None:
            raise ValueError("Chinese translation requires English subtitles "
                             "as source")

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
    def construct_argparser(cls, **kwargs):
        """
        Constructs argument parser

        Returns:
            parser (argparse.ArgumentParser): Argument parser
        """
        parser = super().construct_argparser(description=__doc__, **kwargs)

        # Input
        parser_input = parser.add_argument_group("input arguments")
        parser_input.add_argument("-bif", "--bilingual_infile",
                                  help="bilingual subtitle infile",
                                  metavar="FILE")
        parser_input.add_argument("-cif", "--chinese_infile",
                                  dest="hanzi_infile",
                                  help="Chinese Hanzi subtitle infile",
                                  metavar="FILE")
        parser_input.add_argument("-eif", "--english_infile",
                                  help="English subtitle infile",
                                  metavar="FILE")
        parser_input.add_argument("-pif", "--pinyin_infile",
                                  help="Chinese pinyin subtitle infile",
                                  metavar="FILE")

        # Operations
        parser_ops = parser.add_argument_group("operation arguments")
        parser_ops.add_argument("-c", "--cantonese",
                                action="store_const",
                                const="cantonese",
                                dest="pinyin_language",
                                help="add Cantonese Yale pinyin (耶鲁粤语拼音); "
                                     "mainly useful for older Hong Kong "
                                     "movies (1980s to early 1990s) whose "
                                     "Chinese subtitles are in 粤文 (i.e. "
                                     "using 係, 喺, and 唔 rather than 是, 在, "
                                     "and 不, etc.)")
        parser_ops.add_argument("-m", "--mandarin",
                                action="store_const",
                                const="mandarin",
                                default="mandarin",
                                dest="pinyin_language",
                                help="add Mandarin Hanyu pinyin (汉语拼音)")
        parser_ops.add_argument("-s", "--simplify",
                                action="store_true",
                                help="convert traditional Hanzi characters to "
                                     "simplified")

        # Output
        parser_output = parser.add_argument_group("output arguments")
        parser_output.add_argument("-bof", "--bilingual_outfile",
                                   help="bilingual subtitle outfile",
                                   metavar="FILE")
        parser_output.add_argument("-cof", "--chinese_outfile",
                                   dest="hanzi_outfile",
                                   help="Chinese Hanzi subtitle outfile",
                                   metavar="FILE")
        parser_output.add_argument("-eof", "--english_outfile",
                                   help="English subtitle outfile",
                                   metavar="FILE")
        parser_output.add_argument("-pof", "--pinyin_outfile",
                                   help="Chinese pinyin subtitle outfile",
                                   metavar="FILE")
        parser_output.add_argument("-o", "--overwrite",
                                   action="store_true",
                                   help="overwrite outfiles if they exist")

        return parser

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    Compositor.main()
