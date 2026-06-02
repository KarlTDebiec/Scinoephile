#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Configuration of tests of scinoephile."""

from __future__ import annotations

import pytest
from PIL import Image

from scinoephile.image.subtitles import ImageSeries, ImageSubtitle

# ruff: noqa: F401 F403
from test.data.acopopb import *
from test.data.kob import *
from test.data.mlamd import *
from test.data.mnt import *
from test.data.t import *


@pytest.fixture
def tiny_image_series() -> ImageSeries:
    """Small image subtitle series for tests that do not need full fixtures."""
    return ImageSeries(
        events=[
            ImageSubtitle(
                start=1000,
                end=2000,
                img=Image.new("LA", (4, 3), (255, 255)),
                text="recognized",
            ),
            ImageSubtitle(
                start=3000,
                end=4000,
                img=Image.new("LA", (2, 5), (255, 255)),
                text="validated",
            ),
        ]
    )
