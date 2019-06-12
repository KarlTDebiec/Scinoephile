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
from time import sleep
from scinoephile import SubtitleSeries
from scinoephile.Compositor import Compositor

################################ CONFIGURATION ################################
input_dir = expandvars("$HOME/Desktop/subtitles/test/input")
output_dir = expandvars("$HOME/Desktop/subtitles/test/output/")


################################## FUNCTIONS ##################################
def run_tests(md5s=None, verbosity=1, **kwargs):
    compositor = Compositor(verbosity=verbosity, **kwargs)
    compositor()


#################################### TESTS ####################################
def test_Compositor_translate_chinese_to_english(**kwargs):
    run_tests(
        english=f"{output_dir}/trivisa/en-HK.srt",
        english_overwrite=True,
        hanzi=f"{input_dir}/trivisa/original/cmn-Hant.srt",
        **kwargs)


def test_Compositor_bilingual(**kwargs):
    run_tests(
        bilingual=f"{output_dir}/trivisa/ZE.srt",
        **kwargs)


def test_Compositor_merge_hanzi_english(**kwargs):
    run_tests(
        bilingual=f"{input_dir}/trivisa/ZE.srt",
        bilingual_overwrite=True,
        english=f"{input_dir}/trivisa/original/en-HK.srt",
        hanzi=f"{input_dir}/trivisa/original/cmn-Hans.srt",
        **kwargs)


def test_Compositor_miscellaneous(**kwargs):
    # Test classmethods
    Compositor.construct_argparser().print_help()
    try:
        Compositor.main()
    except SystemExit:
        pass

    # Test instantiation of empty object
    compositor = Compositor(**kwargs)
    compositor()
    compositor.verbosity = 1
    print(compositor.embed_kw)
    compositor.verbosity = 2
    print(compositor.embed_kw)

    # Test that private methods fail appropriately with missing data
    try:
        compositor._convert_traditional_to_simplified_hanzi()
        assert (False)
    except ValueError:
        pass
    try:
        compositor._initialize_bilingual_subtitles()
        assert (False)
    except ValueError:
        pass
    try:
        compositor._initialize_pinyin_subtitles()
        assert (False)
    except ValueError:
        pass
    try:
        compositor._translate_chinese_to_english()
        assert (False)
    except ValueError:
        pass
    try:
        compositor._translate_english_to_chinese()
        assert (False)
    except ValueError:
        pass

    # Test default values of properites
    _ = compositor.bilingual_subtitles
    _ = compositor.english_subtitles
    _ = compositor.hanzi_subtitles
    _ = compositor.pinyin_subtitles

    # Test setter validation
    try:
        compositor.bilingual_subtitles = False
        assert (False)
    except ValueError:
        pass
    compositor.bilingual_subtitles = SubtitleSeries()
    try:
        compositor.english_subtitles = False
        assert (False)
    except ValueError:
        pass
    compositor.english_subtitles = SubtitleSeries()
    try:
        compositor.hanzi_subtitles = False
        assert (False)
    except ValueError:
        pass
    compositor.hanzi_subtitles = SubtitleSeries()
    try:
        compositor.pinyin_subtitles = False
        assert (False)
    except ValueError:
        pass
    compositor.pinyin_subtitles = SubtitleSeries()


def test_Compositor_pinyin(**kwargs):
    run_tests(
        pinyin=f"{output_dir}/saving_mr_wu/cmn-pinyin.srt",
        **kwargs)


def test_Compositor_pinyin_yuewen_to_cantonese(**kwargs):
    run_tests(
        hanzi=f"{input_dir}/king_of_beggars/original/yue-Hans.srt",
        pinyin=f"{output_dir}/king_of_beggars/yue-Yale.srt",
        pinyin_language="cantonese",
        pinyin_overwrite=True,
        **kwargs)


def test_Compositor_pinyin_zhongwen_to_cantonese(**kwargs):
    run_tests(
        hanzi=f"{input_dir}/saving_mr_wu/original/cmn-Hant.srt",
        pinyin=f"{output_dir}/saving_mr_wu/cmn-Yale.srt",
        pinyin_language="cantonese",
        pinyin_overwrite=True,
        **kwargs)


def test_Compositor_pinyin_zhongwen_to_mandarin(**kwargs):
    run_tests(
        hanzi=f"{input_dir}/saving_mr_wu/original/cmn-Hant.srt",
        pinyin=f"{output_dir}/saving_mr_wu/cmn-pinyin.srt",
        pinyin_language="mandarin",
        pinyin_overwrite=True,
        simplify=True,
        **kwargs)


def test_Compositor_translate_english_to_chinese(**kwargs):
    run_tests(
        english=f"{input_dir}/trivisa/original/en-HK.srt",
        hanzi=f"{output_dir}/trivisa/cmn-Hans.srt",
        hanzi_overwrite=True,
        **kwargs)


#################################### MAIN #####################################
if __name__ == "__main__":
    test_Compositor_bilingual(verbosity=2)
    test_Compositor_pinyin(verbosity=2)
    test_Compositor_merge_hanzi_english(verbosity=2)
    test_Compositor_pinyin_yuewen_to_cantonese(verbosity=2)
    test_Compositor_pinyin_zhongwen_to_cantonese(verbosity=2)
    test_Compositor_pinyin_zhongwen_to_mandarin(verbosity=2)
    test_Compositor_translate_chinese_to_english(verbosity=2)
    test_Compositor_translate_english_to_chinese(verbosity=2)
    test_Compositor_miscellaneous(verbosity=2)
