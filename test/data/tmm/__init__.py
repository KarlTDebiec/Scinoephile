#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for TMM."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.core.subtitles import Series
from test.helpers import test_data_root

__all__ = [
    "tmm_eng_lens",
    "tmm_eng_tesseract",
    "tmm_yue_hans_lens",
    "tmm_yue_hans_paddle",
    "tmm_yue_hant_lens",
    "tmm_yue_hant_paddle",
    "tmm_zho_hans_lens",
    "tmm_zho_hans_paddle",
    "tmm_zho_hant_lens",
    "tmm_zho_hant_paddle",
    "tmm_yue_hant_fuse",
    "tmm_yue_hant_fuse_clean",
]

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"


@pytest.fixture
def tmm_eng_lens() -> Series:
    """TMM English subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "eng_lens.srt")


@pytest.fixture
def tmm_eng_tesseract() -> Series:
    """TMM English subtitles OCRed using Tesseract."""
    return Series.load(input_dir / "eng_tesseract.srt")


@pytest.fixture
def tmm_yue_hans_lens() -> Series:
    """TMM 简体粤文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "yue-Hans_lens.srt")


@pytest.fixture
def tmm_yue_hans_paddle() -> Series:
    """TMM 简体粤文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "yue-Hans_paddle.srt")


@pytest.fixture
def tmm_yue_hant_lens() -> Series:
    """TMM 繁體粵文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "yue-Hant_lens.srt")


@pytest.fixture
def tmm_yue_hant_paddle() -> Series:
    """TMM 繁體粵文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "yue-Hant_paddle.srt")


@pytest.fixture
def tmm_yue_hant_fuse() -> Series:
    """TMM 繁體粵文 fused subtitles."""
    return Series.load(output_dir / "yue-Hant_fuse.srt")


@pytest.fixture
def tmm_yue_hant_fuse_clean() -> Series:
    """TMM 繁體粵文 fused and cleaned subtitles."""
    return Series.load(output_dir / "yue-Hant_fuse_clean.srt")


@pytest.fixture
def tmm_zho_hans_lens() -> Series:
    """TMM 简体中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hans_lens.srt")


@pytest.fixture
def tmm_zho_hans_paddle() -> Series:
    """TMM 简体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hans_paddle.srt")


@pytest.fixture
def tmm_zho_hant_lens() -> Series:
    """TMM 繁体中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hant_lens.srt")


@pytest.fixture
def tmm_zho_hant_paddle() -> Series:
    """TMM 繁体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hant_paddle.srt")
