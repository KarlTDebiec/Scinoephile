#!/usr/bin/env python3
#   test_Compositor.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
import difflib
from collections import namedtuple
from os.path import expandvars
from typing import Any

import pytest

from scinoephile.Compositor import Compositor

################################ CONFIGURATION ################################
input_directory = expandvars("$SUBTITLES_ROOT/input")
expected_output_directory = expandvars("$SUBTITLES_ROOT/expected_output/")
observed_output_directory = expandvars("$SUBTITLES_ROOT/observed_output/")

################################## VARIABLES ##################################
Movie = namedtuple("Movie", ["input", "expected_output", "observed_output"])

@pytest.fixture(scope="module",
                params=["king_of_beggars",
                        "mcdull_prince_de_la_bun",
                        "saving_mr_wu",
                        "trivisa"])
def movie(name):
    smtp_connection = smtplib.SMTP(request.param, 587, timeout=5)
    yield smtp_connection
    print("finalizing {}".format(smtp_connection))
    smtp_connection.close()


king_of_beggars = Movie(
    f"{input_directory}/king_of_beggars",
    f"{expected_output_directory}/king_of_beggars",
    f"{observed_output_directory}/king_of_beggars")
mcdull_prince_de_la_bun = Movie(
    f"{input_directory}/mcdull_prince_de_la_bun",
    f"{expected_output_directory}/mcdull_prince_de_la_bun",
    f"{observed_output_directory}/mcdull_prince_de_la_bun")
saving_mr_wu = Movie(
    f"{input_directory}/saving_mr_wu",
    f"{expected_output_directory}/saving_mr_wu",
    f"{observed_output_directory}/saving_mr_wu")
trivisa = Movie(
    f"{input_directory}/trivisa",
    f"{expected_output_directory}/trivisa",
    f"{observed_output_directory}/trivisa")


#################################### TESTS ####################################


# def test_argparser_helptext(**kwargs: Any) -> None:
#     Compositor.construct_argparser().print_help()
#
#
# @pytest.mark.xfail(raises=SystemExit)
# def test_argparser_missing(**kwargs: Any) -> None:
#     Compositor.main()
#
#
# @pytest.mark.parametrize(
#     "bilingual_infile",
#     [f"{m.expected_output}/cmn-hans_en.srt"
#      for m in [mcdull_prince_de_la_bun, saving_mr_wu, trivisa]])
# def test_read_bilingual(bilingual_infile: str, **kwargs: Any) -> None:
#     Compositor(bilingual_infile=bilingual_infile, **kwargs)()
#
#
# @pytest.mark.parametrize(
#     "english_infile",
#     [f"{m.input}/en.srt"
#      for m in [king_of_beggars, mcdull_prince_de_la_bun, saving_mr_wu,
#                trivisa]])
# def test_read_english(english_infile: str, **kwargs: Any) -> None:
#     Compositor(english_infile=english_infile, **kwargs)()
#
#
# @pytest.mark.parametrize(
#     "hanzi_infile",
#     [f"{m.input}/cmn-hans.srt"
#      for m in [mcdull_prince_de_la_bun, saving_mr_wu, trivisa]] +
#     [f"{m.input}/yue-hans.srt"
#      for m in [king_of_beggars]])
# def test_read_hanzi(hanzi_infile: str, **kwargs: Any) -> None:
#     Compositor(hanzi_infile=hanzi_infile, **kwargs)()
#
#
# @pytest.mark.parametrize(
#     "pinyin_infile",
#     [f"{m.expected_output}/cmn-pinyin.srt"
#      for m in [saving_mr_wu]] +
#     [f"{m.expected_output}/yue-pinyin.srt"
#      for m in [king_of_beggars]])
# def test_read_pinyin(pinyin_infile: str, **kwargs: Any) -> None:
#     Compositor(pinyin_infile=pinyin_infile, **kwargs)()


@pytest.mark.parametrize(
    ("bilingual_outfile",
     "english_infile",
     "hanzi_infile",
     "expected_bilingual_outfile"),
    [(f"{m.observed_output}/cmn-hans_en.srt",
      f"{m.input}/en.srt",
      f"{m.input}/cmn-Hans.srt",
      f"{m.expected_output}/cmn-hans_en.srt")
     for m in [mcdull_prince_de_la_bun, saving_mr_wu, trivisa]] +
    [(f"{m.observed_output}/yue-hans_en.srt",
      f"{m.input}/en.srt",
      f"{m.input}/yue-Hans.srt",
      f"{m.expected_output}/yue-hans_en.srt")
     for m in [king_of_beggars]])
def test_merge_hanzi_english(bilingual_outfile: str, english_infile: str,
                             hanzi_infile: str,
                             expected_bilingual_outfile: str,
                             **kwargs: Any) -> None:
    Compositor(bilingual_outfile=bilingual_outfile,
               english_infile=english_infile, hanzi_infile=hanzi_infile,
               overwrite=True, combine_lines=True, **kwargs)()
    observed = open(bilingual_outfile).readlines()
    expected = open(expected_bilingual_outfile).readlines()
    print(list(difflib.unified_diff(observed, expected)))


# @pytest.mark.parametrize(
#     ("hanzi_infile",
#      "pinyin_language",
#      "pinyin_outfile",
#      "expected_pinyin_outfile"),
#     [(f"{m.input}/cmn-hans.srt",
#       "mandarin",
#       f"{m.observed_output}/cmn-pinyin.srt",
#       f"{m.expected_output}/cmn-pinyin.srt",)
#      for m in [saving_mr_wu]] +
#     [(f"{m.input}/yue-hans.srt",
#       "cantonese",
#       f"{m.observed_output}/yue-pinyin.srt",
#       f"{m.expected_output}/yue-pinyin.srt")
#      for m in [king_of_beggars]])
# def test_read_hanzi_write_pinyin(hanzi_infile: str, pinyin_language: str,
#                                  pinyin_outfile: str,
#                                  expected_pinyin_outfile: str,
#                                  **kwargs: Any) -> None:
#     Compositor(hanzi_infile=hanzi_infile, overwrite=True,
#                pinyin_outfile=pinyin_outfile, pinyin_language=pinyin_language,
#                **kwargs)()
#     observed = open(pinyin_outfile).readlines()
#     expected = open(expected_pinyin_outfile).readlines()
#     print(list(difflib.unified_diff(observed, expected)))
