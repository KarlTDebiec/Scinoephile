#!python
#   scinoephile.core.__init__.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from typing import List

from scinoephile.core.Base import Base
from scinoephile.core.CLToolBase import CLToolBase
from scinoephile.core.StdoutLogger import StdoutLogger
from scinoephile.core.SubtitleEvent import SubtitleEvent
from scinoephile.core.SubtitleSeries import SubtitleSeries
from scinoephile.core.cltools import infile_argument, outfile_argument
from scinoephile.core.general import merge_subtitles
from scinoephile.core.text import (get_pinyin, get_simplified_hanzi,
                                   get_single_line_text, get_truecase)

##################################### ALL #####################################
__all__: List[str] = [
    "Base",
    "CLToolBase",
    "StdoutLogger",
    "SubtitleEvent",
    "SubtitleSeries",
    "get_pinyin",
    "get_simplified_hanzi",
    "get_single_line_text",
    "get_truecase",
    "infile_argument",
    "outfile_argument",
    "merge_subtitles"
]
