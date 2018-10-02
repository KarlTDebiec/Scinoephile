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
from scinoephile import Base, CLToolBase
from IPython import embed
from pysubs2 import SSAFile, SSAEvent
from pysubs2.formatbase import FormatBase


################################### CLASSES ###################################
class HDF5Format(FormatBase):
    """
    Subtitle format for hdf5

    TODO:
      - [x] Save to hdf5
      - [x] Load from hdf5
      - [ ] Document
    """

    @classmethod
    def from_file(cls, subs, fp, **kwargs):
        """
        TODO:
          - [x] Load info
          - [x] Load styles
          - [x] Load events
          - [x] Clean up
          - [ ] Load project info
        """
        from pysubs2.ssastyle import SSAStyle
        import numpy as np

        def string_to_field(field, value):
            from pysubs2.time import timestamp_to_ms
            from pysubs2.time import TIMESTAMP
            from pysubs2.substation import ass_rgba_to_color

            if field in {"start", "end"}:
                return timestamp_to_ms(TIMESTAMP.match(value).groups())
            elif "color" in field:
                return ass_rgba_to_color(value)
            elif field in {"bold", "underline", "italic", "strikeout"}:
                return value == "-1"
            elif field in {"borderstyle", "encoding", "marginl", "marginr",
                           "marginv", "layer", "alphalevel"}:
                return int(value)
            elif field in {"fontsize", "scalex", "scaley", "spacing", "angle",
                           "outline", "shadow"}:
                return float(value)
            elif field == "marked":
                return value.endswith("1")
            elif field == "alignment":
                i = int(value)
                return i
            else:
                return value

        subs.info.clear()
        subs.aegisub_project.clear()
        subs.styles.clear()

        # Load info
        for k, v in fp.attrs.items():
            subs.info[k] = v

        # Load styles
        if "styles" in fp:
            styles = np.array(fp["styles"])
            for style in styles:
                style = {field.lower(): string_to_field(field,
                                                        value.decode("utf8"))
                         for field, value in zip(styles.dtype.names, style)}
                name = style.pop("name")
                subs.styles[name] = SSAStyle(**style)

        # Load subtitles
        if "events" in fp:
            events = np.array(fp["events"])
            for event in events:
                event = {field.lower(): string_to_field(field,
                                                        value.decode("utf8"))
                         for field, value in zip(event.dtype.names, event)}
                subs.events.append(SSAEvent(**event))

        return subs

    @classmethod
    def to_file(cls, subs, fp, format_, **kwargs):
        """
        TODO:
          - [x] Save info
          - [x] Save styles
          - [x] Save events
          - [x] Clean up
          - [ ] Save project info
        """
        from pysubs2.substation import EVENT_FIELDS, STYLE_FIELDS
        import numpy as np

        def field_to_string(field, item):
            from pysubs2.common import text_type, Color
            from pysubs2.substation import color_to_ass_rgba, ms_to_timestamp
            from numbers import Number

            value = getattr(item, field)

            if field in {"start", "end"}:
                return ms_to_timestamp(value)
            elif field == "marked":
                return f"Marked={value:d}"
            elif isinstance(value, bool):
                return "-1" if value else "0"
            elif isinstance(value, (text_type, Number)):
                return text_type(value)
            elif isinstance(value, Color):
                return color_to_ass_rgba(value)
            else:
                raise TypeError(f"Unexpected type when writing a SubStation "
                                f"field {value:!r} for line {item:!r}")

        # Save info
        for k, v in subs.info.items():
            fp.attrs[k] = v

        # Save styles
        if "styles" in fp:
            del fp["styles"]
        dtypes = [("name", "S255"),
                  *((field.strip(), "S255") for field in STYLE_FIELDS["ass"])]
        styles = []
        for name, style in subs.styles.items():
            styles += [(name.encode("utf8"),
                        *(field_to_string(field, style).encode("utf8")
                          for field in STYLE_FIELDS["ass"]))]
        styles = np.array(styles, dtype=dtypes)
        fp.create_dataset("styles", data=styles, dtype=dtypes)

        # Save subtitles
        if "events" in fp:
            del fp["events"]
        dtypes = [("type", "S255"),
                  *((field.strip(), "S255") for field in EVENT_FIELDS["ass"])]
        events = []
        for event in subs.events:
            events += [(event.type.encode("utf8"),
                        *(field_to_string(field, event).encode("utf8")
                          for field in EVENT_FIELDS["ass"]))]
        events = np.array(events, dtype=dtypes)
        fp.create_dataset("events", data=events, dtype=dtypes)


class SubtitleSeries(SSAFile, Base):
    """
    Extension of pysubs2's SSAFile with additional features

    TODO:
      - [x] Save to hdf5
      - [x] Load from hdf5
      - [x] Print with class name of SubtitleSeries
      - [x] Print with actual live class name (will then work for subclasses)
      - [x] Add verbosity argument to __init__
      - [ ] Print as a pandas table
      - [ ] Document
    """

    # region Builtins

    def __init__(self, verbosity=None):
        super().__init__()

        if verbosity is not None:
            self.verbosity = verbosity

    def __repr__(self):
        if self.events:
            from pysubs2.time import ms_to_str

            return f"<{self.__class__.__name__} with {len(self):d} events " \
                   f"and {len(self.styles):d} styles, " \
                   f"last timestamp {ms_to_str(max(e.end for e in self)):s}>"
        else:
            return f"<SubtitleSeries with 0 events " \
                   f"and {len(self.styles):d} styles>"

    # endregion

    # region Public Methods

    def save(self, path, format_=None, **kwargs):
        """
        SSAFile.save expects an open text file, so we open hdf5 here
        """
        # Check if hdf5
        if (format_ == "hdf5" or path.endswith(".hdf5")
                or path.endswith(".h5")):
            import h5py

            with h5py.File(path) as fp:
                HDF5Format.to_file(self, fp, format_=format_, **kwargs)
        # Otherwise, continue as superclass SSAFile
        else:
            SSAFile.save(self, path, format_=format_, **kwargs)

    # endregion

    # region Public Class Methods

    @classmethod
    def load(cls, path, encoding="utf-8", **kwargs):
        """
        SSAFile.from_file expects an open text file, so we open hdf5 here
        """

        # Check if hdf5
        if (encoding == "hdf5" or path.endswith(".hdf5")
                or path.endswith(".h5")):
            import h5py

            with h5py.File(path) as fp:
                subs = cls()
                subs.format = "hdf5"
                return HDF5Format.from_file(subs, fp, **kwargs)
        # Otherwise, continue as superclass SSAFile
        else:
            with open(path, encoding=encoding) as fp:
                return cls.from_file(fp, **kwargs)

    # endregion


class SubtitleEvent(SSAEvent, Base):
    """
    Extension of pysubs2's SSAEvent with additional features
    """

    def __repr__(self):
        from pysubs2.time import ms_to_str

        return f"<{self.__class__.__name__} " \
               f"type={self.type} " \
               f"start={ms_to_str(self.start)} " \
               f"end={ms_to_str(self.end)} " \
               f"text='{self.text}'>"


class SubtitleDataset(CLToolBase):
    """
    Represents a collection of subtitles

    TODO:
      - [ ] Document
    """

    # region Instance Variables

    help_message = ("Represents a collection of subtitles")

    # endregion

    # region Builtins

    def __init__(self, infile=None, outfile=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if infile is not None:
            self.infile = infile
        if outfile is not None:
            self.outfile = outfile

        # Temporary manual configuration for testing
        self.infile = \
            "/Users/kdebiec/Dropbox/code/subtitles/" \
            "youth/" \
            "Youth.en-US.srt"
        self.outfile = \
            "/Users/kdebiec/Dropbox/code/subtitles/" \
            "youth/" \
            "youth.hdf5"

    def __call__(self):
        """ Core logic """
        from os.path import isfile
        # Input
        if self.infile is not None and isfile(self.infile):
            self.read()

        # Output
        if self.outfile is not None:
            self.write()

        # Present IPython prompt
        if self.interactive:
            embed(**self.embed_kw)

    # endregion

    # region Public Properties

    @property
    def infile(self):
        """str: Path to input file"""
        if not hasattr(self, "_infile"):
            self._infile = None
        return self._infile

    @infile.setter
    def infile(self, value):
        from os.path import expandvars

        if value is not None:
            if not isinstance(value, str):
                raise ValueError(self._generate_setter_exception(value))
            value = expandvars(value)
            if value == "":
                raise ValueError(self._generate_setter_exception(value))
        self._infile = value

    @property
    def outfile(self):
        """str: Path to output file"""
        if not hasattr(self, "_outfile"):
            self._outfile = None
        return self._outfile

    @outfile.setter
    def outfile(self, value):
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
        self._outfile = value

    @property
    def subtitles(self):
        """pandas.core.frame.DataFrame: Subtitles"""
        if not hasattr(self, "_subtitles"):
            self._subtitles = SubtitleSeries(verbosity=self.verbosity)
        return self._subtitles

    @subtitles.setter
    def subtitles(self, value):
        if value is not None:
            if not isinstance(value, SubtitleSeries):
                raise ValueError()
        self._subtitles = value

    # endregion

    # region Private Properties

    # endregion

    # region Public Methods

    def read(self, infile=None):
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
        self.subtitles = SubtitleSeries.load(infile)
        self.subtitles.verbosity = self.verbosity

    def write(self, outfile=None):
        from os.path import expandvars

        if outfile is not None:
            outfile = expandvars(outfile)
        elif self.outfile is not None:
            outfile = self.outfile
        else:
            raise ValueError()

        if self.verbosity >= 1:
            print(f"Writing subtitles to '{outfile}'")

        self.subtitles.save(outfile)

    # endregion

    # region Private Methods

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    SubtitleDataset.main()
