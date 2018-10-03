#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.HDF5Format.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from pysubs2.formatbase import FormatBase
from IPython import embed


################################### CLASSES ###################################
class HDF5Format(FormatBase):
    """
    Subtitle format for hdf5

    TODO:
      - [ ] Save individual characters
      - [ ] Load individual characters
      - [ ] Consider if separating image output to a subclass makes sense
      - [ ] Document
    """

    # region Public Class Methods

    @classmethod
    def from_file(cls, subs, fp, verbosity=1, **kwargs):
        """
        TODO:
          - [ ] Load project info
          - [ ] Support verbosity
        """
        import numpy as np
        from pysubs2 import SSAEvent, SSAStyle

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

        # Load images, if applicable
        if "images" in fp and "events" in fp:
            from scinoephile.ocr import ImageSubtitleEvent

            events = np.array(fp["events"])
            for i, event in enumerate(events):
                event = {field.lower(): string_to_field(field,
                                                        value.decode("utf8"))
                         for field, value in zip(event.dtype.names, event)}
                image = np.array(fp["images"][f"{i:04d}"], np.uint8)
                subs.events.append(ImageSubtitleEvent(image=image, **event))

        # Load subtitles
        elif "events" in fp:
            events = np.array(fp["events"])
            for event in events:
                event = {field.lower(): string_to_field(field,
                                                        value.decode("utf8"))
                         for field, value in zip(event.dtype.names, event)}
                subs.events.append(SSAEvent(**event))

        return subs

    @classmethod
    def to_file(cls, subs, fp, format_, verbosity=1, **kwargs):
        """
        TODO:
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
        fp.create_dataset("styles", data=styles, dtype=dtypes, chunks=True,
                          compression="gzip")

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
        fp.create_dataset("events", data=events, dtype=dtypes, chunks=True,
                          compression="gzip")

        # Save images
        if "images" in fp:
            del fp["images"]
        fp.create_group("images")
        for i, event in enumerate(subs.events):
            if hasattr(event, "image"):
                fp["images"].create_dataset(f"{i:04d}", data=event.image,
                                            dtype=np.uint8, chunks=True,
                                            compression="gzip")

    # endregion
