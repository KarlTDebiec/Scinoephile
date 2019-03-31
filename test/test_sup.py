#!/usr/bin/python
# -*- coding: utf-8 -*-
#   test_sup.py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from hashlib import md5
from os import getcwd
from os.path import expandvars
from scinoephile.ocr import ImageSubtitleSeries

################################ CONFIGURATION ################################
input_dir = expandvars("$HOME/Desktop/subtitles/")
output_dir = f"{getcwd()}/"


################################## FUNCTIONS ##################################
def read_test(movie, language, starts_md5, ends_md5, images_md5, verbosity=1,
              **kwargs):
    infile = f"{input_dir}/{movie}/{language}.sup"
    outfile = f"{output_dir}/{language}.h5"
    subs = ImageSubtitleSeries.load(path=infile, verbosity=1)
    starts = md5("_".join([str(e.start) for e in subs.events]).encode("utf-8")
                 ).hexdigest()
    ends = md5("_".join([str(e.end) for e in subs.events]).encode("utf-8")
               ).hexdigest()
    images = md5("_".join([str(e.full_data.tostring()) for e in subs.events]
                          ).encode("utf-8")).hexdigest()
    if verbosity >= 2:
        print(f"starts md5: {starts}")
        print(f"ends   md5: {ends}")
        print(f"images md5: {images}")

    assert (starts == starts_md5)
    assert (ends == ends_md5)
    assert (images == images_md5)


#################################### TESTS #####################################
def test_sup_read_chinese_simplified(**kwargs):
    """Tests reading simplified Chinese subtitles in sup format"""
    read_test("mcdull_prince_de_la_bun", "cmn-Hans",
              "70a2565a5446bacf21fbce71b25ab71a",
              "da71f05b3e0ce5f8e3a5500a88080fc8",
              "7c419dabe0924fc1c30019a223ba8349",
              **kwargs)


def test_sup_read_chinese_traditional(**kwargs):
    """Tests reading traditional Chinese subtitles in sup format"""
    read_test("mcdull_prince_de_la_bun", "cmn-Hant",
              "70a2565a5446bacf21fbce71b25ab71a",
              "da71f05b3e0ce5f8e3a5500a88080fc8",
              "9212af805d216db9a556ae52c4ae0673",
              **kwargs)


def test_sup_read_english(**kwargs):
    """Tests reading English subtitles in sup format"""
    read_test("mcdull_prince_de_la_bun", "en-HK",
              "70a2565a5446bacf21fbce71b25ab71a",
              "da71f05b3e0ce5f8e3a5500a88080fc8",
              "c57046952067d827dd192b784088dfc3",
              **kwargs)


#################################### MAIN #####################################
if __name__ == "__main__":
    test_sup_read_chinese_simplified(verbosity=2)
    test_sup_read_chinese_traditional(verbosity=2)
    test_sup_read_english(verbosity=2)
