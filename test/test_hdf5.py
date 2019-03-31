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
from filecmp import cmp
from hashlib import md5
from os import getcwd
from os.path import expandvars
from scinoephile.ocr import ImageSubtitleSeries

################################ CONFIGURATION ################################
input_dir = expandvars("$HOME/Desktop/subtitles/")
output_dir = f"{getcwd()}/"


################################## FUNCTIONS ##################################
def read_test(movie, language, starts_md5, ends_md5, texts_md5, images_md5,
              verbosity=1, **kwargs):
    infile = f"{input_dir}/{movie}/{language}_8bit.h5"

    subs = ImageSubtitleSeries.load(path=infile, verbosity=verbosity)
    starts = md5("_".join([str(e.start) for e in subs.events]).encode("utf-8")
                 ).hexdigest()
    ends = md5("_".join([str(e.end) for e in subs.events]).encode("utf-8")
               ).hexdigest()
    texts = md5("_".join([e.text for e in subs.events]).encode("utf-8")
                ).hexdigest()
    images = md5("_".join([str(e.full_data.tostring()) for e in subs.events]
                          ).encode("utf-8")).hexdigest()
    if verbosity >= 2:
        print(f"starts md5: {starts}")
        print(f"ends   md5: {ends}")
        print(f"texts  md5: {texts}")
        print(f"images md5: {images}")

    assert (starts == starts_md5)
    assert (ends == ends_md5)
    assert (texts == texts_md5)
    assert (images == images_md5)


#################################### TESTS ####################################
def test_hdf5_read_chinese_simplified(**kwargs):
    """Tests reading simplified Chinese subtitles in srt format"""
    read_test("mcdull_prince_de_la_bun", "cmn-Hans",
              "f23a20cebaee31a99d58d61a2e28ab53",
              "7818b23b519ee573d0d4e87d44aa87c4",
              "02827e2ec172bb596741c8bfe2d59966",
              "7c419dabe0924fc1c30019a223ba8349",
              **kwargs)


#################################### MAIN #####################################
if __name__ == "__main__":
    test_hdf5_read_chinese_simplified(verbosity=2)
