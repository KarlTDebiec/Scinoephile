#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.SubtitleDataset.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from scinoephile import DatasetBase, SubtitleSeries
from IPython import embed


################################### CLASSES ###################################
class SubtitleDataset(DatasetBase):
    """
    A collection of subtitles

    Serves as an additional layer around SubtitleSeries and SubtitleEvent to
    separate scinoephile and pysubs2 styles.
    """

    # region Class Attributes

    series_class = SubtitleSeries

    # endregion

    @property
    def subtitles(self):
        """pandas.core.frame.DataFrame: Subtitles"""
        if not hasattr(self, "_subtitles"):
            self._subtitles = self.series_class(interactive=self.interactive,
                                                verbosity=self.verbosity)
        return self._subtitles

    @subtitles.setter
    def subtitles(self, value):
        if value is not None:
            if not isinstance(value, self.series_class):
                raise ValueError()
        self._subtitles = value

    # endregion

    # region Public Methods

    def load(self, infile=None):
        from os.path import expandvars

        # Process arguments
        if infile is not None:
            infile = expandvars(infile)
        elif self.infile is not None:
            infile = self.infile
        else:
            raise ValueError()

        # Load infile
        if self.verbosity >= 1:
            print(f"Reading subtitles from '{infile}'")
        self.subtitles = self.series_class.load(infile,
                                                verbosity=self.verbosity)
        self.subtitles.verbosity = self.verbosity

    def save(self, outfile=None):
        from os.path import expandvars

        # Process arguments
        if outfile is not None:
            outfile = expandvars(outfile)
        elif self.outfile is not None:
            outfile = self.outfile
        else:
            raise ValueError()

        # Write outfile
        if self.verbosity >= 1:
            print(f"Writing subtitles to '{outfile}'")
        self.subtitles.save(outfile)

    # endregion
