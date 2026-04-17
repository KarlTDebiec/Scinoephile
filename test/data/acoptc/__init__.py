#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for ACOPTC."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.core.subtitles import Series
from test.helpers import test_data_root

__all__ = [
    "acoptc_itunes_eng_6",
    "acoptc_itunes_zho_3",
    "acoptc_itunes_zho_4",
    "acoptc_itunes_zho_5",
    "acoptc_yue_hans_lens",
    "acoptc_yue_hans_paddle",
    "acoptc_yue_hant_lens",
    "acoptc_yue_hant_paddle",
    "acoptc_zho_hans_lens",
    "acoptc_zho_hans_paddle",
    "acoptc_zho_hant_lens",
    "acoptc_zho_hant_paddle",
]

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
itunes_input_dir = input_dir / "itunes"


@pytest.fixture
def acoptc_yue_hans_lens() -> Series:
    """ACOPTC 简体粤文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "yue-Hans_lens.srt")


@pytest.fixture
def acoptc_yue_hans_paddle() -> Series:
    """ACOPTC 简体粤文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "yue-Hans_paddle.srt")


@pytest.fixture
def acoptc_yue_hant_lens() -> Series:
    """ACOPTC 繁體粵文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "yue-Hant_lens.srt")


@pytest.fixture
def acoptc_yue_hant_paddle() -> Series:
    """ACOPTC 繁體粵文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "yue-Hant_paddle.srt")


@pytest.fixture
def acoptc_zho_hans_lens() -> Series:
    """ACOPTC 简体中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hans_lens.srt")


@pytest.fixture
def acoptc_zho_hans_paddle() -> Series:
    """ACOPTC 简体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hans_paddle.srt")


@pytest.fixture
def acoptc_zho_hant_lens() -> Series:
    """ACOPTC 繁体中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hant_lens.srt")


@pytest.fixture
def acoptc_zho_hant_paddle() -> Series:
    """ACOPTC 繁体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hant_paddle.srt")


@pytest.fixture
def acoptc_itunes_eng_6() -> Series:
    """ACOPTC iTunes English subtitles."""
    return Series.load(itunes_input_dir / "eng-6.srt")


@pytest.fixture
def acoptc_itunes_zho_3() -> Series:
    """ACOPTC iTunes 中文 subtitles track 3."""
    return Series.load(itunes_input_dir / "zho-3.srt")


@pytest.fixture
def acoptc_itunes_zho_4() -> Series:
    """ACOPTC iTunes 中文 subtitles track 4."""
    return Series.load(itunes_input_dir / "zho-4.srt")


@pytest.fixture
def acoptc_itunes_zho_5() -> Series:
    """ACOPTC iTunes 中文 subtitles track 5."""
    return Series.load(itunes_input_dir / "zho-5.srt")
