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
from scinoephile.utils.tests import cmp_h5, get_md5

################################ CONFIGURATION ################################
input_dir = expandvars("$HOME/Desktop/subtitles/test/input")
output_dir = expandvars("$HOME/Desktop/subtitles/test/output/")


################################## FUNCTIONS ##################################
def run_tests(infile=None, md5s=None, outfiles=None, verbosity=1, **kwargs):
    """
    Runs tests for one set of subtitles

    Args:
        infile (str): Path to input file
        md5s (dict): md5s of selected subtitle properties
        outfiles (str, list): Paths to one or
        verbosity (int): Level of verbose output
        **kwargs: Additional keyword arguments
    """

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
                print(f"{key:<34s}{md5:<34s}{md5s[key]:<34s}")
            assert (md5 == md5s[key])
        elif verbosity >= 2:
            print(f"{key:<34s}{md5:<34s}")

    # Load infile
    if infile is not None:
        subs = SubtitleSeries.load(path=infile, verbosity=verbosity)
    else:
        subs = SubtitleSeries(verbosity=verbosity)

    # Test that properites have loaded in accurately
    if md5s is not None:
        if verbosity >= 2:
            print(f"{'Property':<34s}{'Observed':<34s}{'Expected':<34s}")
        if "events_ends" in md5s:
            check_md5("events_ends",
                      [e.end for e in subs.events])
        if "events_series" in md5s:
            check_md5("events_series",
                      [e.series for e in subs.events])
        if "events_starts" in md5s:
            check_md5("events_starts",
                      [e.start for e in subs.events])
        if "events_strs" in md5s:
            check_md5("events_strs",
                      [str(e) for e in subs.events])
        if "events_texts" in md5s:
            check_md5("events_texts",
                      [e.text for e in subs.events])
        if "str" in md5s:
            check_md5("str",
                      str(subs))

    # Test output
    if outfiles is not None:
        if not isinstance(outfiles, list):
            outfiles = [outfiles]
        for outfile in outfiles:
            if isfile(outfile):
                remove(outfile)
            subs.save(path=outfile)

            if infile is not None:
                if ((infile.endswith(".hdf5") or infile.endswith(".h5")) and
                        (outfile.endswith(".hdf5")
                         or outfile.endswith(".h5"))):
                    assert (cmp_h5(infile, outfile))
                elif infile.split(".")[-1] == outfile.split(".")[-1]:
                    assert (cmp(infile, outfile))


#################################### TESTS ####################################
def test_Subtitle(**kwargs):
    """Tests empty subtitle series"""
    run_tests(
        md5s=dict(
            events_ends="d41d8cd98f00b204e9800998ecf8427e",
            events_series="d41d8cd98f00b204e9800998ecf8427e",
            events_strs="d41d8cd98f00b204e9800998ecf8427e",
            events_starts="d41d8cd98f00b204e9800998ecf8427e",
            events_texts="d41d8cd98f00b204e9800998ecf8427e",
            str="a1d55e2eb3efc7ae4aa50833ac885d3a"),
        **kwargs)


def test_Subtitle_srt_chinese_simplified(**kwargs):
    """Tests reading and writing simplified Chinese subtitles in srt format"""
    run_tests(
        infile=f"{input_dir}/mcdull_prince_de_la_bun/cmn-Hans.srt",
        md5s=dict(
            events_ends="7818b23b519ee573d0d4e87d44aa87c4",
            events_series="b4cbefcc5af1f073d7733a3cfcb0bd6c",
            events_strs="4fa79a5b7405be4d74da1f6062fc96da",
            events_starts="f23a20cebaee31a99d58d61a2e28ab53",
            events_texts="02827e2ec172bb596741c8bfe2d59966",
            str="fc249d74ac6c838b0d9365793a4988a2"),
        outfiles=f"{output_dir}/mcdull_prince_de_la_bun/cmn-Hans.srt",
        **kwargs)


def test_Subtitle_srt_english(**kwargs):
    """Tests reading and writing English subtitles in srt format"""
    run_tests(
        infile=f"{input_dir}/mcdull_prince_de_la_bun/en-HK.srt",
        md5s=dict(
            events_ends="f5d3cd18e4b4f8060daae6a78c79a261",
            events_series="7e2924a1d9d4b3c671b9b8d7083c7c1d",
            events_strs="2b2068f7413e1f1d5ab35938253b12ef",
            events_starts="3f6014e26a4a6f08681f30c3b151a3ad",
            events_texts="067bbb5f80d6f3e699b3c12e6e229a85",
            str="dd57be09939d6eec40c7f41c2ef8ceca"),
        outfiles=f"{output_dir}/mcdull_prince_de_la_bun/en-HK.srt",
        **kwargs)


def test_Subtitle_hdf5_chinese_simplified(**kwargs):
    """Tests reading and writing simplified Chinese subtitles in hdf5 format"""
    run_tests(
        infile=f"{input_dir}/mcdull_prince_de_la_bun/cmn-Hans.h5",
        md5s=dict(
            events_ends="7818b23b519ee573d0d4e87d44aa87c4",
            events_series="b4cbefcc5af1f073d7733a3cfcb0bd6c",
            events_strs="4fa79a5b7405be4d74da1f6062fc96da",
            events_starts="f23a20cebaee31a99d58d61a2e28ab53",
            events_texts="02827e2ec172bb596741c8bfe2d59966",
            str="fc249d74ac6c838b0d9365793a4988a2"),
        outfiles=f"{output_dir}/mcdull_prince_de_la_bun/cmn-Hans.h5",
        **kwargs)


def test_Subtitle_hdf5_english(**kwargs):
    """Tests reading and writing English subtitles in hdf5 format"""
    run_tests(
        infile=f"{input_dir}/mcdull_prince_de_la_bun/en-HK.h5",
        md5s=dict(
            events_ends="34d744f818436f2bc47cf5a4aadb2ca9",
            events_series="7e2924a1d9d4b3c671b9b8d7083c7c1d",
            events_strs="2b2068f7413e1f1d5ab35938253b12ef",
            events_starts="ec6dc07f45c2fa6ce5c02afdd158e6a8",
            events_texts="067bbb5f80d6f3e699b3c12e6e229a85",
            str="dd57be09939d6eec40c7f41c2ef8ceca"),
        outfiles=f"{output_dir}/mcdull_prince_de_la_bun/en-HK.h5",
        **kwargs)


#################################### MAIN #####################################
if __name__ == "__main__":
    test_Subtitle(verbosity=2)
    test_Subtitle_srt_chinese_simplified(verbosity=2)
    test_Subtitle_srt_english(verbosity=2)
    test_Subtitle_hdf5_chinese_simplified(verbosity=2)
    test_Subtitle_hdf5_english(verbosity=2)
