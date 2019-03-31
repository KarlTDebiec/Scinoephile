#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.SubtitleSeries.py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
import numpy as np
from pysubs2 import SSAFile
from scinoephile import Base, SubtitleEvent
from IPython import embed


################################### CLASSES ###################################
class SubtitleSeries(Base, SSAFile):
    """
    A series of subtitles

    Extension of pysubs2's SSAFile with additional features. Includes code
    for loading to and saving from hdf5. While these are part of separate
    classes in pysubs.SSAFile, this separation is not really beneficial here.

    Attributes:
        event_class (class): Class of individual subtitle events
    """

    # region Class Attributes

    event_class = SubtitleEvent

    # endregion

    # region Builtins

    def __init__(self, **kwargs):
        """
        Initializes

        Args:
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # SSAFile.__init__ accepts no arguments
        SSAFile.__init__(self)

    def __repr__(self):
        """
        Provides a string representation

        Returns:
            str: String representation of this series
        """
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

    def save(self, path, format=None, **kwargs):
        """
        Saves subtitles to an output file

        Note:
            pysubs2.SSAFile.save expects an open text file, so we open the
            hdf5 file here for consistency.

        Args:
            path (str): Path to output file
            format (str, optional): Output file format
            **kwargs: Additional keyword arguments
        """
        from os.path import expandvars

        # Process arguments
        path = expandvars(path).replace("//", "/")
        if self.verbosity >= 1:
            print(f"Writing subtitles to '{path}'")

        # Check if hdf5
        if format == "hdf5" or path.endswith(".hdf5") or path.endswith(".h5"):
            import h5py

            with h5py.File(path) as fp:
                self._save_hdf5(fp, **kwargs)
        # Otherwise, continue as superclass SSAFile
        else:
            SSAFile.save(self, path, format_=format, **kwargs)

    # endregion

    # region Public Class Methods

    @classmethod
    def load(cls, path, encoding="utf-8", format_=None, verbosity=1, **kwargs):
        """
        Loads subtitles from an input file

        Notes:
            pysubs2.SSAFile.from_file expects an open text file, so we open
             the hdf5 file here for consistency

        Args:
            infile (str): Path to input file
            encoding (str, optional): Input file encoding
            format_ (str, optional): Input file format
            verbosity (int, optional): Level of verbose output
            **kwargs: Additional keyword arguments

        Returns:
            SubtitleSeries: Loaded subtitles
        """
        from os.path import expandvars

        # Process arguments
        path = expandvars(path).replace("//", "/")
        if verbosity >= 1:
            print(f"Reading subtitles from '{path}'")

        # Check if hdf5
        if format_ == "hdf5" or path.endswith(".hdf5") or path.endswith(".h5"):
            import h5py

            with h5py.File(path) as fp:
                return cls._load_hdf5(fp, verbosity=verbosity, **kwargs)
        # Otherwise, use SSAFile.from_file
        else:
            with open(path, encoding=encoding) as fp:
                subs = cls.from_file(fp, format_=format_, **kwargs)
                subs.verbosity = verbosity
                for event in subs.events:
                    event.verbosity = verbosity
                return subs

    # endregion

    # region Private Methods

    def _save_hdf5(self, fp, **kwargs):
        """
        Saves subtitles to an output hdf5 file

        Todo:
            * Save project info

        Args:
            fp (h5py._hl.files.File): Open hdf5 output file
            **kwargs: Additional keyword arguments
        """
        from pysubs2.substation import EVENT_FIELDS, STYLE_FIELDS

        def style_value_to_string(field, style):
            """
            Converts values of Substation style to string format

            Args:
                field (str): Name of fields
                style (pysubs2.ssastyle.SSAStyle): SubStation Alpha style

            Returns:
                str: Value of field in string format
            """
            from numbers import Number
            from pysubs2.common import Color
            from pysubs2.substation import color_to_ass_rgba, ms_to_timestamp

            value = getattr(style, field)

            if field in {"start", "end"}:
                return ms_to_timestamp(value)
            elif field == "marked":
                return f"Marked={value:d}"
            elif isinstance(value, bool):
                return "-1" if value else "0"
            elif isinstance(value, (str, Number)):
                return str(value)
            elif isinstance(value, Color):
                return color_to_ass_rgba(value)
            else:
                raise TypeError(f"Unexpected type when writing a SubStation "
                                f"field {value:!r} for line {style:!r}")

        # Save info
        for k, v in self.info.items():
            fp.attrs[k] = v

        # Save styles
        if "styles" in fp:
            del fp["styles"]
        dtypes = [("name", "S255"),
                  *((field.strip(), "S255") for field in STYLE_FIELDS["ass"])]
        styles = []
        for name, style in self.styles.items():
            styles += [(name.encode("utf8"),
                        *(style_value_to_string(field, style).encode("utf8")
                          for field in STYLE_FIELDS["ass"]))]
        styles = np.array(styles, dtype=dtypes)
        fp.create_dataset("styles",
                          data=styles, dtype=dtypes,
                          chunks=True, compression="gzip")

        # Save subtitles
        if "events" in fp:
            del fp["events"]
        dtypes = [("type", "S255"),
                  *((field.strip(), "S255") for field in EVENT_FIELDS["ass"])]
        events = []
        for event in self.events:
            events += [(event.type.encode("utf8"),
                        *(style_value_to_string(field, event).encode("utf8")
                          for field in EVENT_FIELDS["ass"]))]
        events = np.array(events, dtype=dtypes)
        fp.create_dataset("events",
                          data=events, dtype=dtypes,
                          chunks=True, compression="gzip")

    # endregion

    # region Private Class Methods

    @classmethod
    def _load_hdf5(cls, fp, verbosity=1, **kwargs):
        """
        Loads subtitles from an input hdf5 file

         Todo:
            * Load project info

        Args:
            fp (h5py._hl.files.File): Open hdf5 input file
            verbosity (int, optional): Level of verbose output
            **kwargs: Additional keyword arguments

        Returns:
            SubtitleSeries: Loaded subtitles
        """
        from pysubs2 import SSAStyle

        def style_value_from_string(field, value):
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

        # Initialize
        subs = cls(verbosity=verbosity)
        subs.format = "hdf5"

        # Load info
        for k, v in fp.attrs.items():
            subs.info[k] = v

        # Load styles
        if "styles" in fp:
            styles = np.array(fp["styles"])
            for style in styles:
                style = {field.lower(): style_value_from_string(field,
                                                                value.decode(
                                                                    "utf8"))
                         for field, value in zip(styles.dtype.names, style)}
                name = style.pop("name")
                subs.styles[name] = SSAStyle(**style)

        # Load subtitles
        if "events" in fp:
            events = np.array(fp["events"])
            for event in events:
                event = {field.lower(): style_value_from_string(field,
                                                                value.decode(
                                                                    "utf8"))
                         for field, value in zip(event.dtype.names, event)}
                subs.events.append(cls.event_class(verbosity=verbosity,
                                                   series=subs,
                                                   **event))

        return subs

    # endregion
