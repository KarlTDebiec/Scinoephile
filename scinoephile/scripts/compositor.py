#!/usr/bin/env python
#   scinoephile/scripts/compositor.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""
Compiles Chinese and English subtitles into a single file, optionally adding
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
####################################### MODULES ########################################
from argparse import ArgumentParser
from copy import deepcopy
from os import environ
from os.path import isfile
from typing import Any, Dict, List, Optional

import numpy as np
from IPython import embed

from scinoephile.common import (
    ArgumentConflictError,
    CLTool,
    GetterError,
    SetterError,
    embed_kw,
)
from scinoephile.core import (
    SubtitleSeries,
    align_subtitles,
    get_pinyin,
    get_simplified_hanzi,
    get_single_line_text,
    get_truecase,
    merge_subtitles,
)


####################################### CLASSES ########################################
class Compositor(CLTool):
    """Compiles Chinese and English subtitles into a single file."""

    # region Builtins

    def __init__(
        self,
        align_to: Optional[str] = None,
        bilingual_infile: Optional[str] = None,
        bilingual_outfile: Optional[str] = None,
        combine_lines: bool = False,
        english_infile: Optional[str] = None,
        english_outfile: Optional[str] = None,
        hanzi_infile: Optional[str] = None,
        hanzi_outfile: Optional[str] = None,
        interactive: bool = False,
        overwrite: bool = False,
        pinyin_infile: Optional[str] = None,
        pinyin_outfile: Optional[str] = None,
        pinyin_language: Optional[str] = None,
        simplify: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Initializes command-line tool and compiles list of operations.

        Args:
            align_to (Optional[str]): Subtitle track to which to align others,
              may be 'chinese' or 'english'
            bilingual_infile (Optional[str]): Path to bilingual subtitle infile
            bilingual_outfile (Optional[str]): Path to bilingual subtitle
              outfile
            combine_lines (bool): combine multi-line subtitles into a single
              line
            english_infile (Optional[str]): Path to English subtitle infile
            english_outfile (Optional[str]): Path to English subtitle outfile
            hanzi_infile (Optional[str]): Path to Chinese Hanzi subtitle infile
            hanzi_outfile (Optional[str]): Path to Chinese Hanzi subtitle
              outfile
            interactive (bool): show IPython prompt after loading and
              processing
            overwrite (bool): Overwrite outfiles if they exist
            pinyin_infile (Optional[str]): Path to pinyin Chinese subtitle
              infile
            pinyin_outfile (Optional[str]): Path to pinyin Chinese subtitle
              outfile
            pinyin_language (Optional[str]): Langauge for which to add pinyin;
              may be 'mandarin' or 'cantonese'
            simplify (bool): Convert traditional Hanzi to simplified
            **kwargs (Any): Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Compile input operations
        if not (bilingual_infile or english_infile or hanzi_infile or pinyin_infile):
            raise ArgumentConflictError("At least one infile required")
        if bilingual_infile:
            self.operations["load_bilingual"] = bilingual_infile
        if english_infile:
            self.operations["load_english"] = english_infile
        if hanzi_infile:
            self.operations["load_hanzi"] = hanzi_infile
        if pinyin_infile:
            self.operations["load_pinyin"] = pinyin_infile

        # Compile output operations
        if bilingual_outfile:
            if isfile(bilingual_outfile) and not overwrite:
                raise FileExistsError(
                    f"Bilingual subtitle outfile '{bilingual_outfile}' already exists"
                )
            self.operations["save_bilingual"] = bilingual_outfile
        if english_outfile:
            if isfile(english_outfile) and not overwrite:
                raise FileExistsError(
                    f"English subtitle outfile '{english_outfile}' already exists"
                )
            self.operations["save_english"] = english_outfile
        if hanzi_outfile:
            if isfile(hanzi_outfile) and not overwrite:
                raise FileExistsError(
                    f"Chinese Hanzi subtitle outfile '{hanzi_outfile}' already exists"
                )
            self.operations["save_hanzi"] = hanzi_outfile
        if pinyin_outfile:
            if isfile(pinyin_outfile) and not overwrite:
                raise FileExistsError(
                    f"Chinese pinyin subtitle outfile '{pinyin_outfile}' already exists"
                )
            self.operations["save_pinyin"] = pinyin_outfile
        if interactive:
            self.operations["interactive"] = True

        # Compile conversion operations
        if "save_english" in self.operations and "load_english" not in self.operations:
            if "load_hanzi" in self.operations:
                if "GOOGLE_APPLICATION_CREDENTIALS" in environ:
                    self.operations["translate_english"] = True
                else:
                    raise EnvironmentError(
                        "Translation requires that GOOGLE_APPLICATION_CREDENTIALS is "
                        "set to the path to a Google service account key"
                    )
            else:
                raise ArgumentConflictError(
                    "English subtitle output requires either English or Chinese Hanzi "
                    "subtitle input"
                )
        if "save_hanzi" in self.operations and "load_hanzi" not in self.operations:
            if "load_english" in self.operations:
                if "GOOGLE_APPLICATION_CREDENTIALS" in environ:
                    self.operations["translate_chinese"] = True
                else:
                    raise EnvironmentError(
                        "Translation requires that GOOGLE_APPLICATION_CREDENTIALS is "
                        "set to the path to a Google service account key"
                    )
            else:
                raise ArgumentConflictError(
                    "Chinese Hanzi subtitle output requires either Chinese Hanzi or "
                    "English subtitle input"
                )
        if align_to:
            if align_to == "chinese":
                if {"load_hanzi", "load_english"}.issubset(self.operations):
                    self.operations["align_english_to_chinese"] = True
                else:
                    raise ArgumentConflictError(
                        "Alignment of English subtitles to Chinese requires English "
                        "and Chinese hanzi subtitle input"
                    )
            else:
                if {"load_hanzi", "load_english"}.issubset(self.operations):
                    self.operations["align_chinese_to_english"] = True
                else:
                    raise ArgumentConflictError(
                        "Alignment of Chinese subtitles to English requires English "
                        "and Chinese hanzi subtitle input"
                    )
        if combine_lines:
            if {"load_english", "translate_english"}.intersection(self.operations):
                self.operations["combine_english_lines"] = True
            if {"load_hanzi", "translate_chinese"}.intersection(self.operations):
                self.operations["combine_hanzi_lines"] = True
            if {
                "load_pinyin",
                "convert_pinyin_mandarin",
                "convert_pinyin_canontese",
            }.intersection(self.operations):
                self.operations["combine_pinyin_lines"] = True
        if simplify:
            if {"load_hanzi", "translate_chinese"}.intersection(self.operations):
                self.operations["simplify_chinese"] = True
            else:
                raise ArgumentConflictError(
                    "Conversion to simplified Hanzi characters requires Chinese Hanzi "
                    "subtitle input"
                )
        if "save_pinyin" in self.operations and "load_pinyin" not in self.operations:
            if {"load_hanzi", "translate_chinese"}.intersection(self.operations):
                self.operations[f"convert_pinyin_{pinyin_language}"] = True
            else:
                raise ArgumentConflictError(
                    "Chinese pinyin subtitle output requires either Chinese Hanzi, "
                    "Chinese pinyin, or English subtitle input"
                )
        if (
            "save_bilingual" in self.operations
            and "load_bilingual" not in self.operations
        ):
            if "load_english" not in self.operations:
                if "load_hanzi" in self.operations:
                    if "GOOGLE_APPLICATION_CREDENTIALS" in environ:
                        self.operations["translate_english"] = True
                    else:
                        raise EnvironmentError(
                            "Translation requires that GOOGLE_APPLICATION_CREDENTIALS "
                            "is set to the path to a Google service account key"
                        )
                else:
                    raise ArgumentConflictError(
                        "Bilingual subtitle output requires either Chinese Hanzi or "
                        "English subtitle input"
                    )
            if "load_hanzi" not in self.operations:
                if "load_english" in self.operations:
                    if "GOOGLE_APPLICATION_CREDENTIALS" in environ:
                        self.operations["translate_english"] = True
                    else:
                        raise EnvironmentError(
                            "Translation requires that GOOGLE_APPLICATION_CREDENTIALS "
                            "is set to the path to a Google service account key"
                        )
                else:
                    raise ArgumentConflictError(
                        "Bilingual subtitle output requires either Chinese Hanzi or "
                        "English subtitle input"
                    )
            self.operations["merge_bilingual"] = True

    def __call__(self) -> None:
        """Performs operations."""

        # Load infiles
        if "load_bilingual" in self.operations:
            self.bilingual_subtitles = SubtitleSeries.load(
                self.operations["load_bilingual"], verbosity=self.verbosity
            )
        if "load_english" in self.operations:
            self.english_subtitles = SubtitleSeries.load(
                self.operations["load_english"], verbosity=self.verbosity
            )
        if "load_hanzi" in self.operations:
            self.hanzi_subtitles = SubtitleSeries.load(
                self.operations["load_hanzi"], verbosity=self.verbosity
            )
        if "load_pinyin" in self.operations:
            self.pinyin_subtitles = SubtitleSeries.load(
                self.operations["load_pinyin"], verbosity=self.verbosity
            )

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
        if "combine_english_lines" in self.operations:
            self._combine_lines("english")
        if "combine_hanzi_lines" in self.operations:
            self._combine_lines("hanzi")
        if "combine_pinyin_lines" in self.operations:
            self._combine_lines("pinyin")
        if "align_chinese_to_english" in self.operations:
            self.hanzi_subtitles, self.english_subtitles = align_subtitles(
                self.hanzi_subtitles, self.english_subtitles, (0, 0)
            )
        if "align_english_to_chinese" in self.operations:
            self.english_subtitles, self.hanzi_subtitles = align_subtitles(
                self.english_subtitles, self.hanzi_subtitles, (0, 0)
            )
        if "merge_bilingual" in self.operations:
            self._initialize_bilingual_subtitles()
        if "interactive" in self.operations:
            embed(**embed_kw())

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
    def bilingual_subtitles(self) -> Optional[SubtitleSeries]:
        """Optional[SubtitleSeries]: Bilingual subtitles."""
        if not hasattr(self, "_bilingual_subtitles"):
            self._bilingual_subtitles: Optional[SubtitleSeries] = None
        return self._bilingual_subtitles

    @bilingual_subtitles.setter
    def bilingual_subtitles(self, value: Optional[SubtitleSeries]) -> None:
        if not (isinstance(value, SubtitleSeries) or value is None):
            raise SetterError(self, value)
        self._bilingual_subtitles = value

    @property
    def english_subtitles(self) -> Optional[SubtitleSeries]:
        """Optional[SubtitleSeries]: English subtitles"""
        if not hasattr(self, "_english_subtitles"):
            self._english_subtitles: Optional[SubtitleSeries] = None
        return self._english_subtitles

    @english_subtitles.setter
    def english_subtitles(self, value: Optional[SubtitleSeries]) -> None:
        if not (isinstance(value, SubtitleSeries) or value is None):
            raise SetterError(self, value)
        self._english_subtitles = value

    @property
    def hanzi_subtitles(self) -> Optional[SubtitleSeries]:
        """Optional[SubtitleSeries]: Hanzi Chinese subtitles"""
        if not hasattr(self, "_hanzi_subtitles"):
            self._hanzi_subtitles: Optional[SubtitleSeries] = None
        return self._hanzi_subtitles

    @hanzi_subtitles.setter
    def hanzi_subtitles(self, value: Optional[SubtitleSeries]) -> None:
        if not (isinstance(value, SubtitleSeries) or value is None):
            raise SetterError(self, value)
        self._hanzi_subtitles = value

    @property
    def operations(self) -> Dict[str, Any]:
        """Dict[str, Any]: Operations to perform, with associated arguments."""
        if not hasattr(self, "_operations"):
            self._operations: Dict[str, Any] = {}
        return self._operations

    @property
    def pinyin_subtitles(self) -> Optional[SubtitleSeries]:
        """Optional[SubtitleSeries]: Pinyin Chinese subtitles"""
        if not hasattr(self, "_pinyin_subtitles"):
            self._pinyin_subtitles: Optional[SubtitleSeries] = None
        return self._pinyin_subtitles

    @pinyin_subtitles.setter
    def pinyin_subtitles(self, value: Optional[SubtitleSeries]) -> None:
        if not (isinstance(value, SubtitleSeries) or value is None):
            raise SetterError(self, value)
        self._pinyin_subtitles = value

    # endregion

    # region Private Methods

    def _combine_lines(self, language: str) -> None:
        if language not in ["english", "hanzi", "pinyin"]:
            raise ValueError(
                "Invalid value provided for argument 'language'; must be 'english', "
                "'hanzi', or 'pinyin'"
            )
        elif language == "english":
            if self.english_subtitles is None:
                raise GetterError(
                    "Combining of english lines requres initialized English subtitles"
                )
            for i, e in enumerate(self.english_subtitles.events):
                e.text = get_single_line_text(e.text, "english")
        elif language == "hanzi":
            if self.hanzi_subtitles is None:
                raise GetterError(
                    "Combining of hanzi lines requires initialized hanzi subtitles"
                )
            for e in self.hanzi_subtitles.events:
                e.text = get_single_line_text(e.text, "hanzi")
        elif language == "pinyin":
            if self.pinyin_subtitles is None:
                raise GetterError(
                    "Combining of pinyin lines requires initialized pinyin subtitles"
                )
            for e in self.pinyin_subtitles.events:
                e.text = get_single_line_text(e.text, "pinyin")

    def _convert_traditional_to_simplified_hanzi(self) -> None:

        # Process arguments
        if self._hanzi_subtitles is None:
            raise GetterError(
                "Conversion of traditional hanzi to simplified requires initialized "
                "hanzi subtitles"
            )

        if self.verbosity >= 1:
            print("Converting traditional characters to simplified")

        for event in self._hanzi_subtitles:
            event.text = get_simplified_hanzi(event.text, self.verbosity)

    def _convert_capital_english_to_truecase(self) -> None:

        # Process arguments
        if self._english_subtitles is None:
            raise GetterError(
                "Conversion of English to truecase requires English subtitles"
            )

        if self.verbosity >= 1:
            print("Converting capitalized English to truecase")

        for event in self._english_subtitles:
            event.text = get_truecase(event.text)

    def _initialize_bilingual_subtitles(self, chinese: str = "hanzi") -> None:

        # Process arguments
        if self.english_subtitles is None:
            raise GetterError(
                "Initialization of bilingual subtitles requires English subtitles"
            )
        if (chinese == "hanzi" and self.hanzi_subtitles is None) or (
            chinese == "pinyin" and self.pinyin_subtitles is None
        ):
            raise GetterError(
                "Initialization of bilingual subtitles requires Chinese subtitles"
            )
        if chinese == "hanzi":
            chinese_subtitles = deepcopy(self.hanzi_subtitles)
        elif chinese == "pinyin":
            chinese_subtitles = deepcopy(self.pinyin_subtitles)
        else:
            raise ValueError("Argument 'chinese'; must be 'hanzi' or 'pinyin'")
        english_subtitles = deepcopy(self.english_subtitles)

        if self.verbosity >= 1:
            print("Preparing bilingual subtitles")

        # Merge
        merged_df = merge_subtitles(chinese_subtitles, english_subtitles)
        merged_text: List[str] = []
        for _, e in merged_df.iterrows():
            if isinstance(e["upper text"], float) and np.isnan(e["upper text"]):
                merged_text += [e["lower text"]]
            elif isinstance(e["lower text"], float) and np.isnan(e["lower text"]):
                merged_text += [e["upper text"]]
            else:
                merged_text += [f"{e['upper text']}\n{e['lower text']}"]
        merged_df["text"] = merged_text

        self.bilingual_subtitles = SubtitleSeries.from_dataframe(merged_df)

    def _initialize_pinyin_subtitles(self, language: str = "mandarin") -> None:
        from copy import deepcopy

        # Process arguments
        if self.hanzi_subtitles is None:
            raise GetterError(
                "Initialization of pinyin subtitles requires initialized hanzi "
                "subtitles"
            )
        if language not in ["cantonese", "mandarin"]:
            raise ValueError(
                "Invalid value provided for argument 'language'; must be either "
                "'cantonese' or 'mandarin'"
            )
        pinyin_subtitles = deepcopy(self.hanzi_subtitles)

        if self.verbosity >= 1:
            if language == "mandarin":
                print("Adding Mandarin romanization")
            elif language == "cantonese":
                print("Adding Cantonese romanization")

        # Copy and convert to pinyin
        for event in pinyin_subtitles.events:
            event.text = get_pinyin(event.text, language, verbosity=self.verbosity)

        self.pinyin_subtitles = pinyin_subtitles

    def _translate_chinese_to_english(self) -> None:
        # TODO: Move most to language-independent function
        from scinoephile.translation import translate_client

        # Process arguments
        if self.hanzi_subtitles is None:
            raise GetterError(
                "English translation requires Chinese subtitles as source"
            )
        english_subtitles = deepcopy(self.hanzi_subtitles)

        if self.verbosity >= 1:
            print("Initializing English translation")

        # Translate
        texts = [e.text for e in self.hanzi_subtitles.events]
        translations: List[str] = []
        for i in range(0, len(texts), 100):
            translations += [
                e["translatedText"]
                for e in translate_client.translate(
                    list(texts[i : i + 100]), source_language="zh", target_language="en"
                )
            ]
        for i, translation in enumerate(translations):
            if self.verbosity >= 2:
                print(f"{english_subtitles.events[i].text} -> " f"{translation}")
            english_subtitles.events[i].text = translation

        self.english_subtitles = english_subtitles

    def _translate_english_to_chinese(self) -> None:
        # TODO: Move most to language-independent function
        from scinoephile.translation import translate_client

        # Process arguments
        if self.english_subtitles is None:
            raise GetterError(
                "Chinese translation requires English subtitles as source"
            )
        hanzi_subtitles = deepcopy(self.english_subtitles)

        if self.verbosity >= 1:
            print("Initializing Chinese translation")

        # Translate
        texts = [e.text for e in self.english_subtitles.events]
        translations: List[str] = []
        for i in range(0, len(texts), 100):
            translations += [
                e["translatedText"]
                for e in translate_client.translate(
                    list(texts[i : i + 100]), source_language="en", target_language="zh"
                )
            ]
        for i, translation in enumerate(translations):
            if self.verbosity >= 2:
                print(f"{hanzi_subtitles.events[i].text} -> " f"{translation}")
            hanzi_subtitles.events[i].text = translation

        self.hanzi_subtitles = hanzi_subtitles

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser.

        Returns:
            parser (ArgumentParser): Argument parser
        """
        parser = super().construct_argparser(description=__doc__, **kwargs)

        # Input
        parser_input = parser.add_argument_group("input arguments")
        parser_input.add_argument(
            "-bif",
            "--bilingual_infile",
            metavar="FILE",
            type=cls.input_path_arg(),
            help="bilingual subtitle infile",
        )
        parser_input.add_argument(
            "-cif",
            "--chinese_infile",
            dest="hanzi_infile",
            metavar="FILE",
            type=cls.input_path_arg(),
            help="Chinese Hanzi subtitle infile",
        )
        parser_input.add_argument(
            "-eif",
            "--english_infile",
            metavar="FILE",
            type=cls.input_path_arg(),
            help="English subtitle infile",
        )
        parser_input.add_argument(
            "-pif",
            "--pinyin_infile",
            metavar="FILE",
            type=cls.input_path_arg(),
            help="Chinese pinyin subtitle infile",
        )

        # Operations
        parser_ops = parser.add_argument_group("operation arguments")
        align_to = parser_ops.add_mutually_exclusive_group()
        align_to.add_argument(
            "-ac",
            "--align_to_chinese",
            action="store_const",
            const="chinese",
            dest="align_to",
            help="align English subtitle times to Chinese",
        )
        align_to.add_argument(
            "-ae",
            "--align_to_english",
            action="store_const",
            const="english",
            dest="align_to",
            help="align Chinese subtitle times to English",
        )
        parser_ops.add_argument(
            "-l",
            "--line",
            action="store_true",
            dest="combine_lines",
            help="combine multi-line subtitles into a single line",
        )
        pinyin_language = parser_ops.add_mutually_exclusive_group()
        pinyin_language.add_argument(
            "-c",
            "--cantonese",
            action="store_const",
            const="cantonese",
            dest="pinyin_language",
            help="add Cantonese Yale pinyin (耶鲁粤语拼音); mainly useful for older Hong "
            "Kong movies (1980s to early 1990s) whose Chinese subtitles are in 粤文 "
            "(i.e. using 係, 喺, and 唔 rather than 是, 在, and 不, etc.)",
        )
        pinyin_language.add_argument(
            "-m",
            "--mandarin",
            action="store_const",
            const="mandarin",
            default="mandarin",
            dest="pinyin_language",
            help="add Mandarin Hanyu pinyin (汉语拼音)",
        )
        parser_ops.add_argument(
            "-s",
            "--simplify",
            action="store_true",
            help="convert traditional Hanzi characters to simplified",
        )
        parser_ops.add_argument(
            "-i",
            "--interactive",
            action="store_true",
            help="show IPython prompt after loading and processing",
        )

        # Output
        parser_output = parser.add_argument_group("output arguments")
        parser_output.add_argument(
            "-bof",
            "--bilingual_outfile",
            metavar="FILE",
            type=cls.output_path_arg(),
            help="bilingual subtitle outfile",
        )
        parser_output.add_argument(
            "-cof",
            "--chinese_outfile",
            dest="hanzi_outfile",
            metavar="FILE",
            type=cls.output_path_arg(),
            help="Chinese Hanzi subtitle outfile",
        )
        parser_output.add_argument(
            "-eof",
            "--english_outfile",
            metavar="FILE",
            type=cls.output_path_arg(),
            help="English subtitle outfile",
        )
        parser_output.add_argument(
            "-pof",
            "--pinyin_outfile",
            metavar="FILE",
            type=cls.output_path_arg(),
            help="Chinese pinyin subtitle outfile",
        )
        parser_output.add_argument(
            "-o",
            "--overwrite",
            action="store_true",
            help="overwrite outfiles if they exist",
        )

        return parser

    # endregion


######################################### MAIN #########################################
if __name__ == "__main__":
    Compositor.main()
