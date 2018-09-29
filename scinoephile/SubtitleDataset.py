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
from scinoephile import CLToolBase
from IPython import embed


################################### CLASSES ###################################
class SubtitleDataset(CLToolBase):
    """
    Represents a collection of subtitles

    Todo:
      - [ ] Read from SRT
      - [ ] Write to SRT
      - [ ] Write to hdf5
      - [ ] Read from hdf5
      - [ ] Write to pandas
      - [ ] Read from pandas
      - [ ] Read from VTT
      - [ ] Reindex
      - [ ] Convert multi-line to single line
      - [ ] Document
    """

    # region Instance Variables

    help_message = ("Represents a collection of subtitles")

    # endregion

    # region Builtins

    def __init__(self, input_hdf5=None, input_pandas=None, input_srt=None,
                 output_hdf5=None, output_pandas=None, output_srt=None,
                 **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if input_hdf5 is not None:
            self.input_hdf5 = input_hdf5
        if input_pandas is not None:
            self.input_pandas = input_pandas
        if input_srt is not None:
            self.input_srt = input_srt
        if output_hdf5 is not None:
            self.output_hdf5 = output_hdf5
        if output_pandas is not None:
            self.output_pandas = output_pandas
        if output_srt is not None:
            self.output_srt = output_srt

    def __call__(self):
        """ Core logic """
        from os.path import isfile
        # Input
        if self.input_srt is not None and isfile(self.input_srt):
            self.input_srt()

        # Present IPython prompt
        if self.interactive:
            embed(**self.embed_kw)

    # endregion

    # region Public Properties

    @property
    def input_hdf5(self):
        """str: Path to input hdf5 file"""
        if not hasattr(self, "_input_hdf5"):
            self._input_hdf5 = None
        return self._input_hdf5

    @input_hdf5.setter
    def input_hdf5(self, value):
        from os.path import expandvars

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
        self._input_hdf5 = value

    @property
    def input_pandas(self):
        """str: Path to input pandas text file"""
        if not hasattr(self, "_input_pandas"):
            self._input_pandas = None
        return self._input_pandas

    @input_pandas.setter
    def input_pandas(self, value):
        from os.path import expandvars

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
        self._input_pandas = value

    @property
    def input_srt(self):
        """str: Path to input srt file"""
        if not hasattr(self, "_input_srt"):
            self._input_srt = None
        return self._input_srt

    @input_srt.setter
    def input_srt(self, value):
        from os.path import expandvars

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
        self._input_srt = value

    @property
    def output_hdf5(self):
        """str: Path to output hdf5 file"""
        if not hasattr(self, "_output_hdf5"):
            self._output_hdf5 = None
        return self._output_hdf5

    @output_hdf5.setter
    def output_hdf5(self, value):
        from os import access, getcwd, R_OK, W_OK
        from os.path import dirname, expandvars, isfile

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
            elif isfile(value) and not access(value, R_OK):
                raise ValueError(self._generate_setter_exception(value))
            elif dirname(value) == "" and not access(getcwd(), W_OK):
                raise ValueError(self._generate_setter_exception(value))
            elif not access(dirname(value), W_OK):
                raise ValueError(self._generate_setter_exception(value))
        self._output_hdf5 = value

    @property
    def output_pandas(self):
        """str: Path to output pandas file"""
        if not hasattr(self, "_output_pandas"):
            self._output_pandas = None
        return self._output_pandas

    @output_pandas.setter
    def output_pandas(self, value):
        from os import access, getcwd, R_OK, W_OK
        from os.path import dirname, expandvars, isfile

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
            elif isfile(value) and not access(value, R_OK):
                raise ValueError(self._generate_setter_exception(value))
            elif dirname(value) == "" and not access(getcwd(), W_OK):
                raise ValueError(self._generate_setter_exception(value))
            elif not access(dirname(value), W_OK):
                raise ValueError(self._generate_setter_exception(value))
        self._output_pandas = value

    @property
    def output_srt(self):
        """str: Path to output srt file"""
        if not hasattr(self, "_output_srt"):
            self._output_srt = None
        return self._output_srt

    @output_srt.setter
    def output_srt(self, value):
        from os import access, getcwd, R_OK, W_OK
        from os.path import dirname, expandvars, isfile

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
            elif isfile(value) and not access(value, R_OK):
                raise ValueError(self._generate_setter_exception(value))
            elif dirname(value) == "" and not access(getcwd(), W_OK):
                raise ValueError(self._generate_setter_exception(value))
            elif not access(dirname(value), W_OK):
                raise ValueError(self._generate_setter_exception(value))
        self._output_srt = value

    @property
    def subtitles(self):
        """pandas.core.frame.DataFrame: Subtitles"""
        if not hasattr(self, "_subtitles"):
            self._subtitles = None
        return self._subtitles

    @subtitles.setter
    def subtitles(self, value):
        import pandas as pd

        if not isinstance(value, pd.DataFrame):
            raise ValueError()
        # TODO: Improve validation
        self._subtitles = value

    # endregion

    # region Private Properties

    # endregion

    # region Public Methods
    def read_srt(self, infile=None):
        import re
        import pandas as pd
        from datetime import datetime
        from os.path import expandvars

        re_index = re.compile("^(?P<index>\d+)$")
        re_time = re.compile("^(?P<start>\d\d:\d\d:\d\d[,.]\d\d\d) --> "
                             "(?P<end>\d\d:\d\d:\d\d[,.]\d\d\d)(\sX1:0)?$")
        re_blank = re.compile("^\s*$")

        if infile is None:
            infile = self.input_srt
        else:
            infile = expandvars(infile)
        # TODO: Validate that srt file can be read

        if self.verbosity >= 1:
            print(f"Reading subtitles from '{infile}'")
        with open(infile, "r") as infile:
            index = start = end = text = None
            indexes = []
            starts = []
            ends = []
            texts = []
            while True:
                line = infile.readline()
                if line == "":
                    break
                if self.verbosity >= 3:
                    print(line.strip())
                match_index = re_index.match(line)
                match_time = re_time.match(line)
                match_blank = re_blank.match(line)
                if match_index and index is None:
                    index = int(match_index.groupdict()["index"])
                elif match_time:
                    start = datetime.strptime(match_time.groupdict()["start"],
                                              "%H:%M:%S,%f").time()
                    end = datetime.strptime(match_time.groupdict()["end"],
                                            "%H:%M:%S,%f").time()
                elif match_blank:
                    if (index is None or start is None
                            or end is None or text is None):
                        raise ValueError()
                    indexes.append(index)
                    starts.append(start)
                    ends.append(end)
                    texts.append(text)
                    index = start = end = text = None
                else:
                    if text is None:
                        text = line.strip()
                    else:
                        text += "\n" + line.strip()
        subtitles = pd.DataFrame.from_items([("index", indexes),
                                             ("start", starts),
                                             ("end", ends),
                                             ("text", texts)])
        subtitles.set_index("index", inplace=True)
        self.subtitles = subtitles

    def write_srt(self, outfile):
        from os.path import expandvars

        if outfile is None:
            outfile = self.output_srt
        else:
            outfile = expandvars(outfile)
        # TODO: Validate that srt file can be written

        if self.verbosity >= 1:
            print(f"Writing subtitles to '{outfile}'")
        with open(outfile, "w") as outfile:
            for index, subtitle in self.subtitles.iterrows():
                start = subtitle["start"].strftime("%H:%M:%S,%f")[:-3]
                end = subtitle["end"].strftime("%H:%M:%S,%f")[:-3]
                text = subtitle["text"]
                outfile.write(f"{index}\n")
                outfile.write(f"{start} --> {end}\n")
                outfile.write(f"{text}\n")
                outfile.write("\n")

    # endregion

    # region Private Methods

    # endregion
