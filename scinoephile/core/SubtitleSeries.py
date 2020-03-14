#!python
#   scinoephile.core.SubtitleSeries.py
#
#   Copyright (C) 2017-2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from numbers import Number
from os.path import expandvars
from typing import Any, Optional, List, Tuple

import numpy as np
import pandas as pd
import h5py

from pysubs2 import SSAFile, SSAStyle
from pysubs2.common import Color
from pysubs2.substation import (EVENT_FIELDS, STYLE_FIELDS, ass_rgba_to_color,
                                color_to_ass_rgba, ms_to_timestamp)
from pysubs2.time import TIMESTAMP, ms_to_str, timestamp_to_ms
from scinoephile.core.Base import Base
from scinoephile.core.SubtitleEvent import SubtitleEvent


################################### CLASSES ###################################
class SubtitleSeries(Base, SSAFile):  # type: ignore
    """
    A series of subtitles

    Extension of pysubs2's SSAFile with additional features. Includes code
    for loading to and saving from hdf5. While these are part of separate
    classes in pysubs.SSAFile, this separation is not really beneficial here.
    """

    # region Class Attributes

    event_class = SubtitleEvent
    """Class of individual subtitle events"""

    # endregion

    # region Builtins

    def __init__(self, **kwargs: Any) -> None:
        """
        Initializes

        Args:
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # SSAFile.__init__ accepts no arguments
        SSAFile.__init__(self)

    def __str__(self) -> str:
        """
        Provides a string representation of series

        Returns:
            str: String representation of this series
        """
        if self.events:
            return f"<{self.__class__.__name__} " \
                   f"with {len(self.events):d} events " \
                   f"and {len(self.styles):d} styles, " \
                   f"last timestamp " \
                   f"{ms_to_str(max(e.end for e in self.events)):s}>"
        else:
            return f"<SubtitleSeries with 0 events " \
                   f"and {len(self.styles):d} styles>"

    # endregion

    # region Public Methods

    def get_dataframe(self) -> pd.DataFrame:
        df = pd.DataFrame.from_records(
            data=[(e.text, e.start, e.end) for e in self.events],
            columns=["text", "start", "end"])
        return df

    def save(self, path: str, format_: Optional[str] = None,
             **kwargs: Any) -> None:
        """
        Saves subtitles to an output file

        Note:
            pysubs2.SSAFile.save expects an open text file, so we open the
            hdf5 file here for consistency.

        Args:
            path (str): Path to output file
            format_ (str, optional): Output file format
            **kwargs: Additional keyword arguments
        """
        # Process arguments
        path = expandvars(path).replace("//", "/")
        if self.verbosity >= 1:
            print(f"Writing subtitles to '{path}'")

        # Check if hdf5
        if format_ == "hdf5" or path.endswith(".hdf5") or path.endswith(".h5"):
            import h5py

            with h5py.File(path) as fp:
                self._save_hdf5(fp, **kwargs)
        # Otherwise, continue as superclass SSAFile
        else:
            SSAFile.save(self, path, format_=format_, **kwargs)

    # endregion

    # region Public Class Methods

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, verbosity: int = 1,
                       **kwargs: Any) -> "SubtitleSeries":
        subs = cls(verbosity=verbosity)

        for _, event in df.iterrows():
            subs.events.append(cls.event_class(
                text=event["text"], start=event["start"], end=event["end"],
                verbosity=verbosity, series=subs))

        return subs

    @classmethod
    def load(cls, path: str, encoding: str = "utf-8",
             format_: Optional[str] = None, verbosity: int = 1,
             **kwargs: Any) -> "SubtitleSeries":
        """
        Loads subtitles from an input file

        Notes:
            pysubs2.SSAFile.from_file expects an open text file, so we open
             the hdf5 file here for consistency

        Args:
            path (str): Path to input file
            encoding (str, optional): Input file encoding
            format_ (str, optional): Input file format
            verbosity (int, optional): Level of verbose output
            **kwargs: Additional keyword arguments

        Returns:
            SubtitleSeries: Loaded subtitles
        """

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
            events = []
            for ssaevent in subs.events:
                events.append(cls.event_class(verbosity=verbosity,
                                              series=subs,
                                              **ssaevent.as_dict()))
            subs.events = events

            return subs  # type:ignore

    # endregion

    # region Private Methods

    def _save_hdf5(self, fp: Any, **kwargs: Any) -> None:
        """
        Saves subtitles to an output hdf5 file

        TODO: Save project info

        Args:
            fp (h5py._hl.files.File): Open hdf5 output file
            **kwargs: Additional keyword arguments
        """

        def style_value_to_string(field: str, style_: SSAStyle) -> str:
            """
            Converts values of Substation style to string format

            Args:
                field (str): Name of fields
                style_ (SSAStyle): SubStation Alpha style

            Returns:
                str: Value of field in string format
            """
            value = getattr(style_, field)

            if field in {"start", "end"}:
                return str(ms_to_timestamp(value))
            elif field == "marked":
                return f"Marked={value:d}"
            elif isinstance(value, bool):
                return "-1" if value else "0"
            elif isinstance(value, (str, Number)):
                return str(value)
            elif isinstance(value, Color):
                return str(color_to_ass_rgba(value))
            else:
                raise TypeError(f"Unexpected type when writing a SubStation "
                                f"field {value:!r} for line {style_:!r}")

        # Save info
        for k, v in self.info.items():
            fp.attrs[k] = v

        # Save styles
        if "styles" in fp:
            del fp["styles"]
        dtypes = [("name", "S255"),
                  *((field.strip(), "S255") for field in STYLE_FIELDS["ass"])]
        styles: List[Tuple[Any,...]] = []
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
        events: List[Tuple[Any,...]] = []
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
    def _load_hdf5(cls, fp: h5py._hl.files.File, verbosity: int = 1,
                   **kwargs: Any) -> "SubtitleSeries":
        """
        Loads subtitles from an input hdf5 file

         TODO: Load project info

        Args:
            fp (h5py._hl.files.File): Open hdf5 input file
            verbosity (int, optional): Level of verbose output
            **kwargs: Additional keyword arguments

        Returns:
            SubtitleSeries: Loaded subtitles
        """

        def style_value_from_string(field: str, value: Any) -> Any:

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
