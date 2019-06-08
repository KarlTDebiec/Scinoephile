#!/usr/bin/python
# -*- coding: utf-8 -*-
#   test_OCRRecognition.py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from filecmp import cmp
from os import remove
from os.path import expandvars, isfile
from scinoephile import SubtitleSeries
from scinoephile.utils.tests import cmp_h5, get_md5

################################ CONFIGURATION ################################
input_dir = expandvars("$HOME/Desktop/subtitles/test/input")
output_dir = expandvars("$HOME/Desktop/subtitles/test/output/")

################################## FUNCTIONS ##################################

#################################### TESTS ####################################


#################################### MAIN #####################################
if __name__ == "__main__":
    pass
