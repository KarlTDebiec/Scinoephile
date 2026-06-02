#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for ACOPTC."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.core.subtitles import Series
from test.helpers import test_data_root

__all__ = [
    "acoptc_eng",
    "acoptc_yue_hans_ocr_lens",
    "acoptc_yue_hans_ocr_paddle",
    "acoptc_yue_hant_ocr_lens",
    "acoptc_yue_hant_ocr_paddle",
    "acoptc_zho_hans",
    "acoptc_zho_hans_ocr_lens",
    "acoptc_zho_hans_ocr_paddle",
    "acoptc_zho_hant",
    "acoptc_zho_hant_ocr_lens",
    "acoptc_zho_hant_ocr_paddle",
]

title_root = test_data_root / Path(__file__).parent.name
input_path = title_root / "input"


@pytest.fixture
def acoptc_eng() -> Series:
    """ACOPTC English subtitles."""
    return Series.load(input_path / "eng.srt")


@pytest.fixture
def acoptc_yue_hans_ocr_lens() -> Series:
    """ACOPTC 简体粤文 subtitles OCRed using Google Lens."""
    return Series.load(input_path / "yue-Hans_ocr/lens.srt")


@pytest.fixture
def acoptc_yue_hans_ocr_paddle() -> Series:
    """ACOPTC 简体粤文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_path / "yue-Hans_ocr/paddle.srt")


@pytest.fixture
def acoptc_yue_hant_ocr_lens() -> Series:
    """ACOPTC 繁體粵文 subtitles OCRed using Google Lens."""
    return Series.load(input_path / "yue-Hant_ocr/lens.srt")


@pytest.fixture
def acoptc_yue_hant_ocr_paddle() -> Series:
    """ACOPTC 繁體粵文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_path / "yue-Hant_ocr/paddle.srt")


@pytest.fixture
def acoptc_zho_hans() -> Series:
    """ACOPTC 简体中文 subtitles."""
    return Series.load(input_path / "zho-Hans.srt")


@pytest.fixture
def acoptc_zho_hans_ocr_lens() -> Series:
    """ACOPTC 简体中文 subtitles OCRed using Google Lens."""
    return Series.load(input_path / "zho-Hans_ocr/lens.srt")


@pytest.fixture
def acoptc_zho_hans_ocr_paddle() -> Series:
    """ACOPTC 简体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_path / "zho-Hans_ocr/paddle.srt")


@pytest.fixture
def acoptc_zho_hant() -> Series:
    """ACOPTC 繁体中文 subtitles."""
    return Series.load(input_path / "zho-Hant.srt")


@pytest.fixture
def acoptc_zho_hant_ocr_lens() -> Series:
    """ACOPTC 繁体中文 subtitles OCRed using Google Lens."""
    return Series.load(input_path / "zho-Hant_ocr/lens.srt")


@pytest.fixture
def acoptc_zho_hant_ocr_paddle() -> Series:
    """ACOPTC 繁体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_path / "zho-Hant_ocr/paddle.srt")
