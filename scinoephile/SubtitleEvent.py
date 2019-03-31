#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.SubtitleEvent.py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from pysubs2 import SSAEvent
from scinoephile import Base
from IPython import embed


################################### CLASSES ###################################
class SubtitleEvent(Base, SSAEvent):
    """
    An individual subtitle

    Extension of pysubs2's SSAEvent with additional features.
    """

    # region Builtins

    def __init__(self, series, **kwargs):
        super().__init__(**{k: v for k, v in kwargs.items()
                            if k not in SSAEvent.FIELDS})

        # SSAEvent.__init__ accepts arguments
        SSAEvent.__init__(self, **{k: v for k, v in kwargs.items()
                                   if k in SSAEvent.FIELDS})

        # Store property values
        if series is not None:
            self.series = series

    def __repr__(self):
        from pysubs2.time import ms_to_str

        return f"<{self.__class__.__name__}— " \
            f"type={self.type} " \
            f"start={ms_to_str(self.start)} " \
            f"end={ms_to_str(self.end)} " \
            f"text='{self.text}'>"

    # endregion

    # region Public Properties

    @property
    def series(self):
        if not hasattr(self, "_series"):
            self._series = None
        return self._series

    @series.setter
    def series(self, value):
        from scinoephile import SubtitleSeries

        if not isinstance(value, SubtitleSeries):
            raise ValueError(self._generate_setter_exception(value))
        self._series = value

    # endregion
