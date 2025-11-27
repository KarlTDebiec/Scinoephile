#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for T."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.core import Series
from scinoephile.testing import test_data_root

# ruff: noqa: F401 F403
from test.data.t.core.english.proofreading import (
    test_cases as t_english_proofreading_test_cases,
)
from test.data.t.core.zhongwen.proofreading import (
    test_cases as t_zhongwen_proofreading_test_cases,
)
from test.data.t.image.english.fusion import (
    test_cases as t_english_fusion_test_cases,
)
from test.data.t.image.zhongwen.fusion import (
    test_cases as t_zhongwen_fusion_test_cases,
)

title = Path(__file__).parent.name
input_dir = test_data_root / title / "input"
output_dir = test_data_root / title / "output"


# 简体中文 (OCR)
@pytest.fixture
def t_zho_hans_lens() -> Series:
    """T 简体中文 subtitles OCRed using Google Lens OCR."""
    return Series.load(input_dir / "zho-Hans_lens.srt")


@pytest.fixture
def t_zho_hans_paddle() -> Series:
    """T 简体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hans_paddle.srt")


@pytest.fixture
def t_zho_hans_fuse() -> Series:
    """T 简体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse.srt")


@pytest.fixture
def t_zho_hans_fuse_proofread() -> Series:
    """T 简体中文 fused and proofread subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_proofread.srt")


# 繁體中文 (OCR)
@pytest.fixture
def t_zho_hant_lens() -> Series:
    """T 繁體中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hant_lens.srt")


@pytest.fixture
def t_zho_hant_paddle() -> Series:
    """T 繁體中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hant_paddle.srt")


# English (OCR)
@pytest.fixture
def t_eng_lens() -> Series:
    """T English subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "eng_lens.srt")


@pytest.fixture
def t_eng_tesseract() -> Series:
    """T English subtitles OCRed using Tesseract."""
    return Series.load(input_dir / "eng_tesseract.srt")


@pytest.fixture
def t_eng_fuse() -> Series:
    """T English fused subtitles."""
    return Series.load(output_dir / "eng_fuse.srt")


@pytest.fixture
def t_eng_fuse_proofread() -> Series:
    """T English fused and proofread subtitles."""
    return Series.load(output_dir / "eng_fuse_proofread.srt")


# 简体中文 (SRT)
@pytest.fixture
def t_zho_hans() -> Series:
    """T 简体中文 series."""
    return Series.load(input_dir / "zho-Hans.srt")


@pytest.fixture
def t_zho_hans_clean() -> Series:
    """T 简体中文 cleaned series."""
    return Series.load(output_dir / "zho-Hans_clean.srt")


@pytest.fixture
def t_zho_hans_clean_flatten() -> Series:
    """T 简体中文 cleaned and flattened series."""
    return Series.load(output_dir / "zho-Hans_clean_flatten.srt")


# 繁体中文
@pytest.fixture
def t_zho_hant() -> Series:
    """T 繁体中文 series."""
    return Series.load(input_dir / "zho-Hant.srt")


@pytest.fixture
def t_zho_hant_simplify() -> Series:
    """T 繁体中文 simplified series."""
    return Series.load(output_dir / "zho-Hant_simplify.srt")


# English (SRT)
@pytest.fixture
def t_eng() -> Series:
    """T English series."""
    return Series.load(input_dir / "eng.srt")


@pytest.fixture
def t_eng_clean() -> Series:
    """T English cleaned series."""
    return Series.load(output_dir / "eng_clean.srt")


@pytest.fixture
def t_eng_clean_flatten() -> Series:
    """T English cleaned and flattened series."""
    return Series.load(output_dir / "eng_clean_flatten.srt")


# Bilingual 简体中文 and English
@pytest.fixture
def t_zho_hans_eng() -> Series:
    """T Bilingual 简体粤文 and English series."""
    return Series.load(output_dir / "zho-Hans_eng.srt")


___all__ = [
    "t_zho_hans_lens",
    "t_zho_hans_paddle",
    "t_zho_hans_fuse",
    "t_zho_hans_fuse_proofread",
    "t_zho_hans_fuse_proofread_clean",
    "t_zho_hans_fuse_proofread_clean_flatten",
    "t_zho_hans",
    "t_zho_hans_clean",
    "t_zho_hans_flatten",
    "t_zho_hans_clean_flatten",
    "t_zho_hant",
    "t_zho_hant_simplify",
    "t_eng",
    "t_eng_clean",
    "t_eng_flatten",
    "t_eng_proof",
    "t_eng_proof_clean_flatten",
    "t_zho_hans_eng",
    "t_english_fusion_test_cases",
    "t_english_proofreading_test_cases",
    "t_zhongwen_fusion_test_cases",
    "t_zhongwen_proofreading_test_cases",
]
