#!/usr/bin/python
# -*- coding: utf-8 -*-
#   test_ImageSubtitle.py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from filecmp import cmp
from os import remove
from os.path import expandvars, isfile, isdir
from shutil import rmtree
from scinoephile.ocr import ImageSubtitleSeries
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
        subs = ImageSubtitleSeries.load(path=infile, verbosity=verbosity)
    else:
        subs = ImageSubtitleSeries(verbosity=verbosity)

    # Test that properites have loaded in accurately
    if md5s is not None:
        if verbosity >= 2:
            print(f"{'Property':<34s}{'Observed':<34s}{'Expected':<34s}")
        if "data" in md5s:
            check_md5("data",
                      subs.data)
        if "events_char_bounds" in md5s:
            check_md5("events_char_bounds",
                      [e.char_bounds for e in subs.events])
        if "events_char_count" in md5s:
            check_md5("events_char_count",
                      [e.char_count for e in subs.events])
        if "events_char_separations" in md5s:
            check_md5("events_char_separations",
                      [e.char_separations for e in subs.events])
        if "events_char_widths" in md5s:
            check_md5("events_char_widths",
                      [e.char_widths for e in subs.events])
        if "events_ends" in md5s:
            check_md5("events_ends",
                      [e.end for e in subs.events])
        if "events_images" in md5s:
            check_md5("events_images",
                      [e.full_data.tostring() for e in subs.events])
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
        if "spec" in md5s:
            check_md5("spec",
                      str(subs.spec))
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
            elif isdir(outfile):
                rmtree(outfile)
            subs.save(path=outfile)

            if infile is not None and not isdir(outfile):
                if ((infile.endswith(".hdf5") or infile.endswith(".h5")) and
                        (outfile.endswith(".hdf5")
                         or outfile.endswith(".h5"))):
                    assert (cmp_h5(infile, outfile))
                elif infile.split(".")[-1] == outfile.split(".")[-1]:
                    assert (cmp(infile, outfile))


#################################### TESTS ####################################
def test_ImageSubtitle_hdf5_chinese_simplified(**kwargs):
    """Tests reading simplified Chinese subtitles in srt format"""
    run_tests(
        infile=f"{input_dir}/mcdull_prince_de_la_bun/cmn-Hans.h5",
        md5s=dict(
            data="3c745f0e394724ce2a28bbba614dfa6e",
            events_char_bounds="326c5b3901a605d176d425d5dbbdc7e1",
            events_char_count="9bbbf134d009857b20e5687c77326797",
            events_char_separations="2a0771dbd3a5740190206cfed3f40307",
            events_char_widths="3850d33adfa610c87a4c762d216f3c8c",
            events_ends="7818b23b519ee573d0d4e87d44aa87c4",
            events_images="7c419dabe0924fc1c30019a223ba8349",
            events_series="946c84f3c93e818bb367954a88782d4f",
            events_starts="f23a20cebaee31a99d58d61a2e28ab53",
            events_strs="4d8e4f77b1b51e22396e34f62ba07735",
            events_texts="02827e2ec172bb596741c8bfe2d59966",
            str="b257f040185902df5bae94f8ad411710"),
        outfiles=[
            f"{output_dir}/mcdull_prince_de_la_bun/cmn-Hans.srt",
            f"{output_dir}/mcdull_prince_de_la_bun/cmn-Hans.h5",
            f"{output_dir}/mcdull_prince_de_la_bun/cmn-Hans/"],
        **kwargs)


def test_ImageSubtitle_sup_chinese_simplified(**kwargs):
    """Tests reading simplified Chinese subtitles in sup format"""
    run_tests(
        infile=f"{input_dir}/mcdull_prince_de_la_bun/original/cmn-Hans.sup",
        md5s=dict(
            data="3c745f0e394724ce2a28bbba614dfa6e",
            events_char_bounds="326c5b3901a605d176d425d5dbbdc7e1",
            events_char_count="9bbbf134d009857b20e5687c77326797",
            events_char_separations="2a0771dbd3a5740190206cfed3f40307",
            events_char_widths="3850d33adfa610c87a4c762d216f3c8c",
            events_ends="da71f05b3e0ce5f8e3a5500a88080fc8",
            events_images="7c419dabe0924fc1c30019a223ba8349",
            events_series="946c84f3c93e818bb367954a88782d4f",
            events_starts="70a2565a5446bacf21fbce71b25ab71a",
            events_strs="a9c7f05fa0a52a148a56b3b1d8823da3",
            events_texts="9e2465e25709344c0dcc1ceecdf30b90",
            str="b257f040185902df5bae94f8ad411710"),
        outfiles=[
            f"{output_dir}/mcdull_prince_de_la_bun/cmn-Hans.srt",
            f"{output_dir}/mcdull_prince_de_la_bun/cmn-Hans.h5",
            f"{output_dir}/mcdull_prince_de_la_bun/cmn-Hans/"],
        **kwargs)


#################################### MAIN #####################################
if __name__ == "__main__":
    test_ImageSubtitle_hdf5_chinese_simplified(verbosity=2)
    test_ImageSubtitle_sup_chinese_simplified(verbosity=2)
