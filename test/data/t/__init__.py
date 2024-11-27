#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.

from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.testing.file import get_test_file_path


@pytest.fixture
def t_input_english():
    return Series.load(get_test_file_path("t/input/en-HK.srt"))


@pytest.fixture
def t_input_hanzi():
    return Series.load(get_test_file_path("t/input/cmn-Hans.srt"))


@pytest.fixture
def t_output_english():
    return Series.load(get_test_file_path("t/output/en-HK.srt"))


@pytest.fixture
def t_output_hanzi():
    return Series.load(get_test_file_path("t/output/cmn-Hans.srt"))


test_cases = []
___all__ = [
    "t_input_english",
    "t_input_hanzi",
    "t_output_english",
    "t_output_hanzi",
]
