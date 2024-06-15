#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Data fixtures for tests."""
from __future__ import annotations

import pytest

from scinoephile.core import SubtitleSeries
from scinoephile.testing import get_test_file_path


@pytest.fixture
def kob_input_hanzi():
    return SubtitleSeries.load(get_test_file_path("kob/input/yue-hant.srt"))


@pytest.fixture
def kob_input_english():
    return SubtitleSeries.load(get_test_file_path("kob/input/en-hk.srt"))


@pytest.fixture
def kob_output_english():
    return SubtitleSeries.load(get_test_file_path("kob/output/en-hk.srt"))


@pytest.fixture
def mnt_input_english():
    return SubtitleSeries.load(get_test_file_path("mnt/input/en-US.srt"))


@pytest.fixture
def mnt_input_hanzi():
    return SubtitleSeries.load(get_test_file_path("mnt/input/cmn-Hans.srt"))


@pytest.fixture
def t_input_english():
    return SubtitleSeries.load(get_test_file_path("t/input/en-hk.srt"))


@pytest.fixture
def t_input_hanzi():
    return SubtitleSeries.load(get_test_file_path("t/input/cmn-hans.srt"))


@pytest.fixture
def t_output_english():
    return SubtitleSeries.load(get_test_file_path("t/output/en-hk.srt"))


@pytest.fixture
def t_output_hanzi():
    return SubtitleSeries.load(get_test_file_path("t/output/cmn-hans.srt"))
