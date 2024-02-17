#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
from __future__ import annotations

from abc import ABC, abstractmethod

from scinoephile.ocr import ImageSubtitleSeries, OCRDataset


class OCRTestDataset(OCRDataset, ABC):
    """
    A collection of labeled character images for testing
    """

    # region Builtins

    def __init__(self, chars=None, subtitle_series=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if chars is not None:
            self.chars = chars
        if subtitle_series is not None:
            self.subtitle_series = subtitle_series

    # endregion

    # region Public Properties

    @property
    def subtitle_series(self):
        """list(ImageSubtitleSeries): Subtitles to test against"""
        if not hasattr(self, "_subtitle_series"):
            self._subtitle_series = None
        return self._subtitle_series

    @subtitle_series.setter
    def subtitle_series(self, value):
        if not isinstance(value, list):
            value = [value]
        for v in value:
            if not isinstance(v, ImageSubtitleSeries):
                raise ValueError(self._generate_setter_exception(value))
        self._subtitle_series = value
        self._initialize_data()

    # endregion

    # region Private Methods

    @abstractmethod
    def _initialize_data(self):
        """
        Initializes image data structure
        """
        pass

    # endregion
