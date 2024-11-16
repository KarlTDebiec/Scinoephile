#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for PDP."""
from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.testing import get_test_file_path


@pytest.fixture
def pdp_input_en():
    return Series.load(get_test_file_path("pdp/input/en.srt"))


@pytest.fixture
def pdp_input_cmn_hant():
    return Series.load(get_test_file_path("pdp/input/cmn-Hant.srt"))


@pytest.fixture
def pdp_input_yue_hant():
    return Series.load(get_test_file_path("pdp/input/yue-Hant.srt"))


@pytest.fixture
def pdp_output_en_merge():
    return Series.load(get_test_file_path("pdp/output/en_merge.srt"))


@pytest.fixture()
def pdp_output_yue_hans():
    return Series.load(get_test_file_path("pdp/output/yue-Hans.srt"))


@pytest.fixture
def pdp_output_yue_hans_merge():
    return Series.load(get_test_file_path("pdp/output/yue-Hans_merge.srt"))


@pytest.fixture
def pdp_output_yue_hant_merge():
    return Series.load(get_test_file_path("pdp/output/yue-Hant_merge.srt"))


__all__ = [
    "pdp_input_en",
    "pdp_input_cmn_hant",
    "pdp_input_yue_hant",
    "pdp_output_en_merge",
    "pdp_output_yue_hans",
    "pdp_output_yue_hans_merge",
    "pdp_output_yue_hant_merge",
]
