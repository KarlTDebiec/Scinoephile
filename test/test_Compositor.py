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
from os.path import expandvars
from scinoephile.Compositor import Compositor

################################ CONFIGURATION ################################
input_dir = expandvars("$HOME/Desktop/subtitles/test/input")
output_dir = expandvars("$HOME/Desktop/subtitles/test/output/")


################################## FUNCTIONS ##################################
def run_tests(md5s=None, verbosity=1, **kwargs):
    compositor = Compositor(verbosity=verbosity, **kwargs)
    compositor()


#################################### TESTS ####################################
def test_Compositor_yuewen_to_cantonese_pinyin(**kwargs):
    run_tests(
        hanzi=f"{input_dir}/king_of_beggars/original/yue-Hans.srt",
        pinyin=f"{output_dir}/king_of_beggars/yue-Yale.srt",
        pinyin_overwrite=True,
        pinyin_language="cantonese",
        **kwargs)


def test_Compositor_zhongwen_to_cantonese_pinyin(**kwargs):
    run_tests(
        hanzi=f"{input_dir}/saving_mr_wu/original/cmn-Hant.srt",
        pinyin=f"{output_dir}/saving_mr_wu/cmn-Yale.srt",
        pinyin_overwrite=True,
        pinyin_language="cantonese",
        **kwargs)


def test_Compositor_argparser(**kwargs):
    Compositor.construct_argparser()


#################################### MAIN #####################################
if __name__ == "__main__":
    # Merging

    # Mandarin Pinyin

    # Cantonese Pinyin
    test_Compositor_yuewen_to_cantonese_pinyin(verbosity=2)
    test_Compositor_zhongwen_to_cantonese_pinyin(verbosity=2)

    # Simplification

    # Argument parsers
    test_Compositor_argparser(verbosity=2)
