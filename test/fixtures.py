#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Fixtures for tests."""
from __future__ import annotations

import pytest

from scinoephile.core import SubtitleSeries
from scinoephile.testing import get_test_file_path


@pytest.fixture
def mnt_english():
    return SubtitleSeries.load(get_test_file_path("mnt/input/en-US.srt"))


@pytest.fixture
def mnt_hanzi():
    return SubtitleSeries.load(get_test_file_path("mnt/input/cmn-Hant.srt"))
