#!python
#   test_Compositor.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from collections import namedtuple
from os.path import expandvars
from typing import Any
import pytest

from scinoephile.Compositor import Compositor

################################ CONFIGURATION ################################
input_directory = expandvars("$SUBTITLES_ROOT/input")
expected_output_directory = expandvars("$SUBTITLES_ROOT/expected_output/")
actual_output_directory = expandvars("$SUBTITLES_ROOT/actual_output/")

################################## VARIABLES ##################################
Movie = namedtuple("Movie", ["input", "output"])

king_of_beggars = Movie(f"{input_directory}/king_of_beggars",
                        f"{actual_output_directory}/king_of_beggars")
saving_mr_wu = Movie(f"{input_directory}/saving_mr_wu",
                     f"{actual_output_directory}/saving_mr_wu")
trivisa = Movie(f"{input_directory}/trivisa",
                f"{actual_output_directory}/trivisa")


#################################### TESTS ####################################


def test_argparser_helptext(**kwargs: Any) -> None:
    Compositor.construct_argparser().print_help()


@pytest.mark.xfail(raises=SystemExit)
def test_argparser_missing(**kwargs: Any) -> None:
    Compositor.main()


@pytest.mark.parametrize(
    "bilingual_infile",
    [f"{m.input}/cmn-hans_en.srt" for m in [saving_mr_wu, trivisa]])
def test_read_bilingual(bilingual_infile: str, **kwargs: Any) -> None:
    Compositor(bilingual_infile=bilingual_infile, **kwargs)()


@pytest.mark.parametrize(
    "english_infile",
    [f"{m.input}/en.srt" for m in [king_of_beggars, saving_mr_wu, trivisa]])
def test_read_english(english_infile: str, **kwargs: Any) -> None:
    Compositor(english_infile=english_infile, **kwargs)()


@pytest.mark.parametrize(
    "hanzi_infile",
    [f"{m.input}/cmn-hans.srt" for m in [saving_mr_wu, trivisa]] +
    [f"{m.input}/yue-hans.srt" for m in [king_of_beggars]])
def test_read_hanzi(hanzi_infile: str, **kwargs: Any) -> None:
    Compositor(hanzi_infile=hanzi_infile, **kwargs)()


@pytest.mark.parametrize(
    "pinyin_infile",
    [f"{m.input}/cmn-pinyin.srt" for m in [saving_mr_wu]] +
    [f"{m.input}/yue-pinyin.srt" for m in [king_of_beggars]])
def test_read_pinyin(pinyin_infile: str, **kwargs: Any) -> None:
    Compositor(pinyin_infile=pinyin_infile, **kwargs)()


@pytest.mark.parametrize(
    ("bilingual_outfile", "english_infile", "hanzi_infile"),
    [(f"{m.output}/cmn-hans_en.srt", f"{m.input}/en.srt",
      f"{m.input}/cmn-Hans.srt") for m in [saving_mr_wu, trivisa]] +
    [(f"{m.output}/yue-hans_en.srt", f"{m.input}/en.srt",
      f"{m.input}/yue-Hans.srt") for m in [king_of_beggars]])
def test_merge_hanzi_english(bilingual_outfile: str, english_infile: str,
                             hanzi_infile: str, **kwargs: Any) -> None:
    Compositor(bilingual_outfile=bilingual_outfile,
               english_infile=english_infile, hanzi_infile=hanzi_infile,
               overwrite=True, combine_lines=True, **kwargs)()
    # TODO: Validate that actual_output matches expected_output


@pytest.mark.parametrize(
    ("hanzi_infile", "pinyin_language", "pinyin_outfile"),
    [(f"{m.input}/cmn-hans.srt", "mandarin", f"{m.output}/cmn-pinyin.srt")
     for m in [saving_mr_wu]] +
    [(f"{m.input}/yue-hans.srt", "cantonese", f"{m.output}/yue-pinyin.srt")
     for m in [king_of_beggars]])
def test_read_hanzi_write_pinyin(hanzi_infile: str, pinyin_language: str,
                                 pinyin_outfile: str, **kwargs: Any) -> None:
    Compositor(hanzi_infile=hanzi_infile, overwrite=True,
               pinyin_outfile=pinyin_outfile, pinyin_language=pinyin_language,
               **kwargs)()
    # TODO: Validate that actual_output matches expected_output

#################################### MAIN #####################################
# if __name__ == "__main__":
#     test_Compositor_bilingual(verbosity=2)
#     test_Compositor_pinyin(verbosity=2)
#     test_Compositor_merge_hanzi_english(verbosity=2)
#     test_Compositor_miscellaneous(verbosity=2)
#     test_Compositor_pinyin_yuewen_to_cantonese(verbosity=2)
#     test_Compositor_pinyin_zhongwen_to_cantonese(verbosity=2)
#     test_Compositor_pinyin_zhongwen_to_mandarin(verbosity=2)
#     test_Compositor_translate_chinese_to_english(verbosity=2)
#     test_Compositor_translate_english_to_chinese(verbosity=2)
