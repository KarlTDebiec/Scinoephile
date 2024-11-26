#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.

from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.testing import get_test_file_path


@pytest.fixture
def kob_input_english():
    return Series.load(get_test_file_path("input/en-HK.srt"))


@pytest.fixture
def kob_input_hanzi():
    return Series.load(get_test_file_path("input/cmn-Hans.srt"))


@pytest.fixture
def kob_output_english():
    return Series.load(get_test_file_path("kob/output/en-hk.srt"))


test_cases = []
___all__ = [
    "kob_input_english",
    "kob_input_hanzi",
    "kob_output_english",
]
