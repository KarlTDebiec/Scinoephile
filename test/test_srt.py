#!/usr/bin/python
# -*- coding: utf-8 -*-
#   test_srt.py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from filecmp import cmp
from hashlib import md5
from os import getcwd
from os.path import expandvars
from scinoephile import SubtitleSeries

################################ CONFIGURATION ################################
input_dir = expandvars("$HOME/Desktop/subtitles/")
output_dir = f"{getcwd()}/"


################################## FUNCTIONS ##################################
def read_test(movie, language, starts_md5, ends_md5, texts_md5, verbosity=1,
              **kwargs):
    infile = f"{input_dir}/{movie}/{language}.srt"

    subs = SubtitleSeries.load(path=infile, verbosity=verbosity)
    starts = md5("_".join([str(e.start) for e in subs.events]).encode("utf-8")
                 ).hexdigest()
    ends = md5("_".join([str(e.end) for e in subs.events]).encode("utf-8")
               ).hexdigest()
    texts = md5("_".join([e.text for e in subs.events]).encode("utf-8")
                ).hexdigest()
    if verbosity >= 2:
        print(f"starts md5: {starts}")
        print(f"ends   md5: {ends}")
        print(f"texts  md5: {texts}")

    assert (starts == starts_md5)
    assert (ends == ends_md5)
    assert (texts == texts_md5)


def write_test(movie, language, verbosity=1, **kwargs):
    infile = f"{input_dir}/{movie}/{language}.srt"
    outfile = f"{output_dir}/{language}.srt"

    subs = SubtitleSeries.load(path=infile, verbosity=verbosity)
    subs.save(path=outfile, format_="srt")
    assert (cmp(infile, outfile))


#################################### TESTS ####################################
def test_srt_read_chinese_simplified(**kwargs):
    """Tests reading simplified Chinese subtitles in srt format"""
    read_test("mcdull_prince_de_la_bun", "cmn-Hans",
              "f23a20cebaee31a99d58d61a2e28ab53",
              "7818b23b519ee573d0d4e87d44aa87c4",
              "02827e2ec172bb596741c8bfe2d59966",
              **kwargs)


def test_srt_read_english(**kwargs):
    """Tests reading English subtitles in srt format"""
    read_test("mcdull_prince_de_la_bun", "en-HK",
              "3f6014e26a4a6f08681f30c3b151a3ad",
              "f5d3cd18e4b4f8060daae6a78c79a261",
              "61030c42223ace7abd4298e10792d26f",
              **kwargs)


def test_srt_write_chinese_simplified(**kwargs):
    """Tests writing simplified Chinese subtitles in srt format"""
    write_test("mcdull_prince_de_la_bun", "cmn-Hans", **kwargs)


def test_srt_write_english(**kwargs):
    """Tests writing English subtitles in srt format"""
    write_test("mcdull_prince_de_la_bun", "en-HK", **kwargs)


#################################### MAIN #####################################
if __name__ == "__main__":
    test_srt_read_chinese_simplified(verbosity=2)
    test_srt_read_english(verbosity=2)
    test_srt_write_chinese_simplified(verbosity=2)
    test_srt_write_english(verbosity=2)
