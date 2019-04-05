#!/usr/bin/python
# -*- coding: utf-8 -*-
#   test_Subtitle.py
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
from scinoephile.utils.testing import cmp_h5, get_md5

################################ CONFIGURATION ################################
input_dir = expandvars("$HOME/Desktop/subtitles/test/input")
output_dir = expandvars("$HOME/Desktop/subtitles/test/output/")


################################## FUNCTIONS ##################################
def run_tests(infile=None, md5s=None, outfile=None, verbosity=1, **kwargs):
    def check_md5(key, value):
        """
        Checks if the md5 of an object matches a cached value

        Args:
            key (str): Name of object
            value (object): Object to test
        """
        md5 = get_md5(value)

        if md5s[key] is not None:
            if verbosity >= 2:
                print(f"{key:<16s}{md5:<34s}{md5s[key]:<34s}")
            assert (md5 == md5s[key])
        elif verbosity >= 2:
            print(f"{key:<16s}{md5:<34s}")

    # Load infile
    if infile is not None:
        subs = SubtitleSeries.load(path=infile, verbosity=verbosity)
    else:
        subs = SubtitleSeries()

    # Test that properites have loaded in accurately
    if md5s is not None:
        if "event_ends" in md5s:
            check_md5("event_ends", [e.end for e in subs.events])
        if "series_str" in md5s:
            check_md5("series_str", str(subs))
        if "event_series" in md5s:
            check_md5("event_series", [e.series for e in subs.events])
        if "event_starts" in md5s:
            check_md5("event_starts", [e.start for e in subs.events])
        if "event_strs" in md5s:
            check_md5("event_strs", [str(e) for e in subs.events])
        if "event_texts" in md5s:
            check_md5("event_texts", [e.text for e in subs.events])

    # Test output
    if outfile is not None:
        if isfile(outfile):
            remove(outfile)
        subs.save(path=outfile, format_="srt")

        if infile is not None:
            if ((infile.endswith(".hdf5") or infile.endswith(".h5")) and
                    (outfile.endswith(".hdf5") or outfile.endswith(".h5"))):
                assert (cmp_h5(infile, outfile))
            elif infile.split(".")[-1] == infile.split(".")[-1]:
                assert (cmp(infile, outfile))


#################################### TESTS ####################################
def test_Subtitle(**kwargs):
    """Tests empty subtitle series"""
    run_tests(
        md5s=dict(
            event_ends="d41d8cd98f00b204e9800998ecf8427e",
            event_series="d41d8cd98f00b204e9800998ecf8427e",
            event_strs="d41d8cd98f00b204e9800998ecf8427e",
            event_starts="d41d8cd98f00b204e9800998ecf8427e",
            event_texts="d41d8cd98f00b204e9800998ecf8427e",
            series_str="a1d55e2eb3efc7ae4aa50833ac885d3a"),
        **kwargs)


def test_Subtitle_srt_chinese_simplified(**kwargs):
    """Tests reading and writing simplified Chinese subtitles in srt format"""
    run_tests(infile=f"{input_dir}/mcdull_prince_de_la_bun/cmn-Hans.srt",
              md5s=dict(
                  event_ends="7818b23b519ee573d0d4e87d44aa87c4",
                  event_series="b4cbefcc5af1f073d7733a3cfcb0bd6c",
                  event_strs="4fa79a5b7405be4d74da1f6062fc96da",
                  event_starts="f23a20cebaee31a99d58d61a2e28ab53",
                  event_texts="02827e2ec172bb596741c8bfe2d59966",
                  series_str="fc249d74ac6c838b0d9365793a4988a2"),
              outfile=f"{output_dir}/mcdull_prince_de_la_bun/cmn-Hans.srt",
              **kwargs)


def test_Subtitle_srt_english(**kwargs):
    """Tests reading and writing English subtitles in srt format"""
    run_tests(infile=f"{input_dir}/mcdull_prince_de_la_bun/en-HK.srt",
              md5s=dict(
                  event_ends="f5d3cd18e4b4f8060daae6a78c79a261",
                  event_series="7e2924a1d9d4b3c671b9b8d7083c7c1d",
                  event_strs="d7f82116d76a9befe99cdaf1bb467315",
                  event_starts="3f6014e26a4a6f08681f30c3b151a3ad",
                  event_texts="61030c42223ace7abd4298e10792d26f",
                  series_str="dd57be09939d6eec40c7f41c2ef8ceca"),
              outfile=f"{output_dir}/mcdull_prince_de_la_bun/en-HK.srt",
              **kwargs)


def test_Subtitle_hdf5_chinese_simplified(**kwargs):
    """Tests reading and writing simplified Chinese subtitles in hdf5 format"""
    run_tests(infile=f"{input_dir}/mcdull_prince_de_la_bun/cmn-Hans.h5",
              md5s=dict(
                  event_ends="7818b23b519ee573d0d4e87d44aa87c4",
                  event_series="b4cbefcc5af1f073d7733a3cfcb0bd6c",
                  event_strs="4fa79a5b7405be4d74da1f6062fc96da",
                  event_starts="f23a20cebaee31a99d58d61a2e28ab53",
                  event_texts="02827e2ec172bb596741c8bfe2d59966",
                  series_str="fc249d74ac6c838b0d9365793a4988a2"),
              outfile=f"{output_dir}/mcdull_prince_de_la_bun/cmn-Hans.h5",
              **kwargs)


def test_Subtitle_hdf5_english(**kwargs):
    """Tests reading and writing English subtitles in hdf5 format"""
    run_tests(infile=f"{input_dir}/mcdull_prince_de_la_bun/en-HK.h5",
              md5s=dict(
                  # event_ends="f5d3cd18e4b4f8060daae6a78c79a261",
                  event_series="7e2924a1d9d4b3c671b9b8d7083c7c1d",
                  event_strs="d7f82116d76a9befe99cdaf1bb467315",
                  # event_starts="3f6014e26a4a6f08681f30c3b151a3ad",
                  event_texts="61030c42223ace7abd4298e10792d26f",
                  series_str="dd57be09939d6eec40c7f41c2ef8ceca"),
              outfile=f"{output_dir}/mcdull_prince_de_la_bun/en-HK.h5",
              **kwargs)


#################################### MAIN #####################################
if __name__ == "__main__":
    test_Subtitle(verbosity=2)
    test_Subtitle_srt_chinese_simplified(verbosity=2)
    test_Subtitle_srt_english(verbosity=2)
    test_Subtitle_hdf5_chinese_simplified(verbosity=2)
    test_Subtitle_hdf5_english(verbosity=2)
