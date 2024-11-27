#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for KOB."""
from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.testing.file import get_test_file_path


@pytest.fixture
def kob_cmn_hans_hk():
    return Series.load(get_test_file_path("kob/input/cmn-Hans-HK.srt"))


@pytest.fixture
def kob_en_hk():
    return Series.load(get_test_file_path("kob/input/en-HK.srt"))


@pytest.fixture
def kob_yue_hant_hk():
    return Series.load(get_test_file_path("kob/input/yue-Hant-HK.srt"))


___all__ = [
    "kob_cmn_hans_hk",
    "kob_en_hk",
    "kob_yue_hant_hk",
]
