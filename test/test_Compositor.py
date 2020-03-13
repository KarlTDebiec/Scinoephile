#!python
#   test_Compositor.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from os.path import expandvars
from typing import Any

from scinoephile.Compositor import Compositor

################################ CONFIGURATION ################################
input_directory = expandvars("$SUBTITLES_ROOT/input")
expected_output_directory = expandvars("$SUBTITLES_ROOT/expected_output/")
actual_output_directory = expandvars("$SUBTITLES_ROOT/actual_output/")


################################## FUNCTIONS ##################################
def run_tests(**kwargs: Any) -> None:
    compositor = Compositor(**kwargs)
    compositor()


#################################### TESTS ####################################
def test_Compositor_miscellaneous(**kwargs: Any) -> None:
    Compositor.construct_argparser().print_help()
    try:
        Compositor.main()
    except SystemExit:
        pass
    except ValueError:
        pass


def test_Compositor_read_bilingual(**kwargs: Any) -> None:
    run_tests(
        bilingual_infile=f"{input_directory}/trivisa/cmn-hans_en.srt",
        **kwargs)


def test_Compositor_read_english(**kwargs: Any) -> None:
    run_tests(
        bilingual_infile=f"{input_directory}/trivisa/en.srt",
        **kwargs)


def test_Compositor_read_hanzi(**kwargs: Any) -> None:
    run_tests(
        bilingual_infile=f"{input_directory}/trivisa/cmn-Hans.srt",
        **kwargs)


def test_Compositor_merge_hanzi_english(**kwargs: Any) -> None:
    run_tests(
        bilingual_outfile=f"{actual_output_directory}/trivisa/cmn-hans_en.srt",
        english_infile=f"{input_directory}/trivisa/en.srt",
        hanzi_infile=f"{input_directory}/trivisa/cmn-Hans.srt",
        overwrite=True,
        **kwargs)
    # TODO: Valudate that actual_output matches expected_output


# def test_Compositor_read_pinyin(**kwargs: Any) -> None:
#     run_tests(pinyin_infile=f"{input_directory}/trivisa/cmn-pinyin.srt",
#               **kwargs)


# def test_Compositor_read_hanzi_write_pinyin_cantonese(**kwargs: Any) -> None:
#     run_tests(
#         hanzi_infile=f"{input_directory}/trivisa/yue-Hans.srt",
#         overwrite=True,
#         pinyin_outfile=f"{actual_output_directory}/trivisa/yue-Yale.srt",
#         pinyin_language="cantonese",
#         **kwargs)
#     # TODO: Valudate that actual_output matches expected_output


# def test_Compositor_pinyin_zhongwen_to_mandarin(**kwargs: Any) -> None:
#     run_tests(
#         hanzi_infile=f"{input_directory}/trivisa/cmn-Hant.srt",
#         overwrite=True,
#         pinyin_outfile=f"{actual_output_directory}/trivisa/cmn-pinyin.srt",
#         pinyin_language="mandarin",
#         simplify=True,
#         **kwargs)
#     # TODO: Valudate that actual_output matches expected_output

# def test_Compositor_translate_chinese_to_english(**kwargs):
#    run_tests(
#        english=f"{output_dir}/trivisa/en-HK.srt",
#        english_overwrite=True,
#        hanzi=f"{input_dir}/trivisa/original/cmn-Hant.srt",
#        **kwargs)
#     # TODO: Valudate that actual_output matches expected_output

# def test_Compositor_translate_english_to_chinese(**kwargs):
#    run_tests(
#        english=f"{input_dir}/trivisa/original/en-HK.srt",
#        hanzi=f"{output_dir}/trivisa/cmn-Hans.srt",
#        hanzi_overwrite=True,
#        **kwargs)
#     # TODO: Valudate that actual_output matches expected_output


#################################### MAIN #####################################
if __name__ == "__main__":
    # test_Compositor_bilingual(verbosity=2)
    # test_Compositor_pinyin(verbosity=2)
    test_Compositor_merge_hanzi_english(verbosity=2)
    test_Compositor_miscellaneous(verbosity=2)
    # test_Compositor_pinyin_yuewen_to_cantonese(verbosity=2)
    # test_Compositor_pinyin_zhongwen_to_cantonese(verbosity=2)
    # test_Compositor_pinyin_zhongwen_to_mandarin(verbosity=2)
    # test_Compositor_translate_chinese_to_english(verbosity=2)
    # test_Compositor_translate_english_to_chinese(verbosity=2)
