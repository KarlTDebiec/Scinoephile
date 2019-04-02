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
def get_md5(x):
    return md5("_".join(x).encode("utf-8")).hexdigest()


def read_test(movie, language, md5s, verbosity=1, **kwargs):
    infile = f"{input_dir}/{movie}/{language}.sup"
    outfile = f"{output_dir}/{language}.h5"
    subs = ImageSubtitleSeries.load(path=infile, verbosity=1)

    if "starts" in md5s:
        starts = get_md5([str(e.start) for e in subs.events])
        assert (starts == md5s["starts"])
    if "ends" in md5s:
        ends = get_md5([str(e.end) for e in subs.events])
        assert (ends == md5s["ends"])
    if "images" in md5s:
        images = get_md5([str(e.full_data.tostring()) for e in subs.events])
        assert (images == md5s["images"])
    if "char_bounds" in md5s:
        char_bounds = get_md5([str(e.char_bounds) for e in subs.events])
        assert (char_bounds == md5s["char_bounds"])
    if "char_count" in md5s:
        char_count = get_md5([str(e.char_count) for e in subs.events])
        assert (char_count == md5s["char_count"])
    if "char_separations" in md5s:
        char_separations = get_md5(
            [str(e.char_separations) for e in subs.events])
        assert (char_separations == md5s["char_separations"])
    if "char_widths" in md5s:
        char_widths = get_md5([str(e.char_widths) for e in subs.events])
        assert (char_widths == md5s["char_widths"])


#################################### TESTS #####################################
def test_sup_read_chinese_simplified(**kwargs):
    """Tests reading simplified Chinese subtitles in sup format"""
    read_test("mcdull_prince_de_la_bun", "cmn-Hans",
              md5s=dict(
                  starts="70a2565a5446bacf21fbce71b25ab71a",
                  ends="da71f05b3e0ce5f8e3a5500a88080fc8",
                  images="7c419dabe0924fc1c30019a223ba8349",
                  char_bounds="326c5b3901a605d176d425d5dbbdc7e1",
                  char_count="9bbbf134d009857b20e5687c77326797",
                  char_separations="2a0771dbd3a5740190206cfed3f40307",
                  char_widths="3850d33adfa610c87a4c762d216f3c8c"),
              **kwargs)


def test_sup_read_chinese_traditional(**kwargs):
    """Tests reading traditional Chinese subtitles in sup format"""
    read_test("mcdull_prince_de_la_bun", "cmn-Hant",
              md5s=dict(
                  starts="70a2565a5446bacf21fbce71b25ab71a",
                  ends="da71f05b3e0ce5f8e3a5500a88080fc8",
                  images="9212af805d216db9a556ae52c4ae0673",
                  char_bounds="b3126a27f9c93d9839465496716d45f1",
                  char_count="cfb8ca1f7961cdbc82bec8ecc96da7b0",
                  char_separations="6697f0098245e62618b74174749473d9",
                  char_widths="d9e041fdb11bd772c2efadcc54da5876"),
              **kwargs)


def test_sup_read_english(**kwargs):
    """Tests reading English subtitles in sup format"""
    read_test("mcdull_prince_de_la_bun", "en-HK",
              md5s=dict(
                  starts="70a2565a5446bacf21fbce71b25ab71a",
                  ends="da71f05b3e0ce5f8e3a5500a88080fc8",
                  images="c57046952067d827dd192b784088dfc3",
                  char_bounds="4aa4d6d5c6bef0479c53f75b3142224a",
                  char_count="2f9015937b93f4a10831c0751064271b",
                  char_separations="7a4173e1ed7de7a1b69c5171eef7a53e",
                  char_widths="05d717ecb1faf4efde2843051b0460a3"),
              **kwargs)


#################################### MAIN #####################################
if __name__ == "__main__":
    test_sup_read_chinese_simplified(verbosity=2)
    test_sup_read_chinese_traditional(verbosity=2)
    test_sup_read_english(verbosity=2)
