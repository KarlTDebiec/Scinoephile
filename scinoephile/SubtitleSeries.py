#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.SubtitleSeries.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from pysubs2 import SSAFile
from scinoephile import Base, SubtitleEvent
from IPython import embed


################################### CLASSES ###################################
class SubtitleSeries(SSAFile, Base):
    """
    A series of subtitles

    Extension of pysubs2's SSAFile with additional features. Includes code for
    loading to and saving from hdf5. While these are part of separate classes
    in pysubs.SSAFile, this additional separation is not beneficial here.
    """

    # region Class Attributes

    event_class = SubtitleEvent

    # endregion

    # region Builtins

    def __init__(self, verbosity=None, **kwargs):
        super().__init__()  # SSAFile.__init__ accepts no arguments

        # Store property values
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
        Saves subtitles to an output file

        pysubs2.SSAFile.save expects an open text file, so we open the hdf5
        file here for consistency.
        """

        # Check if hdf5
        if (format_ == "hdf5" or path.endswith(".hdf5")
                or path.endswith(".h5")):
            import h5py

            with h5py.File(path) as fp:
                self._save_hdf5(fp, **kwargs)
        # Otherwise, continue as superclass SSAFile
        else:
            SSAFile.save(self, path, format_=format_, **kwargs)

    # endregion

    # region Private Methods

    def _save_hdf5(self, fp, **kwargs):
        """
        Saves subtitles to an output hdf5 file

        .. todo::
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
                        *(field_to_string(field, style).encode("utf8")
                          for field in STYLE_FIELDS["ass"]))]
        styles = np.array(styles, dtype=dtypes)
        fp.create_dataset("styles", data=styles, dtype=dtypes, chunks=True,
                          compression="gzip")

        # Save subtitles
        if "events" in fp:
            del fp["events"]
        dtypes = [("type", "S255"),
                  *((field.strip(), "S255") for field in EVENT_FIELDS["ass"])]
        events = []
        for event in self.events:
            events += [(event.type.encode("utf8"),
                        *(field_to_string(field, event).encode("utf8")
                          for field in EVENT_FIELDS["ass"]))]
        events = np.array(events, dtype=dtypes)
        fp.create_dataset("events", data=events, dtype=dtypes, chunks=True,
                          compression="gzip")

    # endregion

    # region Public Class Methods

    @classmethod
    def load(cls, path, encoding="utf-8", verbosity=1, **kwargs):
        """
        Loads subtitles from an input file

        pysubs2.SSAFile.from_file expects an open text file, so we open the
        hdf5 file here for consistency
        """

        # Check if hdf5
        if (encoding == "hdf5" or path.endswith(".hdf5")
                or path.endswith(".h5")):
            import h5py

            with h5py.File(path) as fp:
                return cls._load_hdf5(fp, verbosity=verbosity, **kwargs)
        # Otherwise, use SSAFile.from_file
        else:
            with open(path, encoding=encoding) as fp:
                subs = cls.from_file(fp, **kwargs)
                subs.verbosity = verbosity
                for event in subs.events:
                    event.verbosity = verbosity
                return subs

    # endregion

    # region Private Class Methods

    @classmethod
    def _load_hdf5(cls, fp, verbosity=1, **kwargs):
        """
        Loads subtitles from an hdf5 file into a nascent SubtitleSeries

        .. todo::
          - [ ] Load project info
        """
        import numpy as np
        from pysubs2 import SSAStyle

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
                subs.events.append(cls.event_class(verbosity=verbosity,
                                                   **event))

        return subs

    # endregion
