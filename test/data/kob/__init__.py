#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for KOB."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.core import Series
from scinoephile.testing import test_data_root

# ruff: noqa: F401 F403
from test.data.kob.core.zhongwen.proofreading import (
    test_cases as kob_zhongwen_proofreading_test_cases,
)
from test.data.kob.image.english.fusion import (
    test_cases as kob_english_fusion_test_cases,
)
from test.data.kob.image.zhongwen.fusion import (
    test_cases as kob_zhongwen_fusion_test_cases,
)

title = Path(__file__).parent.name
input_dir = test_data_root / title / "input"
output_dir = test_data_root / title / "output"


# 繁體中文 (OCR)
@pytest.fixture
def kob_zho_hant_lens() -> Series:
    """KOB 繁體中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hant_lens.srt")


@pytest.fixture
def kob_zho_hant_paddle() -> Series:
    """KOB 繁體中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hant_paddle.srt")


@pytest.fixture
def kob_zho_hant_fuse() -> Series:
    """KOB 繁體中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse.srt")


@pytest.fixture
def kob_zho_hant_fuse_proofread() -> Series:
    """KOB 简体粤文 fused and proofread subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse_proofread.srt")


# 简体粤文
@pytest.fixture
def kob_yue_hans() -> Series:
    """KOB 简体粤文 subtitles."""
    return Series.load(input_dir / "yue-Hans.srt")


@pytest.fixture
def kob_yue_hans_clean() -> Series:
    """KOB 简体粤文 cleaned subtitles."""
    return Series.load(output_dir / "yue-Hans_clean.srt")


@pytest.fixture
def kob_yue_hans_flatten() -> Series:
    """KOB 简体粤文 flattened subtitles."""
    return Series.load(output_dir / "yue-Hans_flatten.srt")


@pytest.fixture
def kob_yue_hans_clean_flatten() -> Series:
    """KOB 简体粤文 cleaned and flattened subtitles."""
    return Series.load(output_dir / "yue-Hans_clean_flatten.srt")


# 繁体粤文
@pytest.fixture
def kob_yue_hant() -> Series:
    """KOB 繁体粤文 subtitles."""
    return Series.load(input_dir / "yue-Hant.srt")


@pytest.fixture
def kob_yue_hant_simplify() -> Series:
    """KOB 繁体粤文 simplified subtitles."""
    return Series.load(output_dir / "yue-Hant_simplify.srt")


# English (OCR)
@pytest.fixture
def kob_eng_lens() -> Series:
    """KOB English subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "eng_lens.srt")


@pytest.fixture
def kob_eng_tesseract() -> Series:
    """KOB English subtitles OCRed using Tesseract."""
    return Series.load(input_dir / "eng_tesseract.srt")


@pytest.fixture
def kob_eng_fuse() -> Series:
    """KOB English fused subtitles."""
    return Series.load(output_dir / "eng_fuse.srt")


# English
@pytest.fixture
def kob_eng() -> Series:
    """KOB English subtitles."""
    return Series.load(input_dir / "eng.srt")


@pytest.fixture
def kob_eng_clean() -> Series:
    """KOB English cleaned subtitles."""
    return Series.load(output_dir / "eng_clean.srt")


@pytest.fixture
def kob_eng_flatten() -> Series:
    """KOB English flattened subtitles."""
    return Series.load(output_dir / "eng_flatten.srt")


@pytest.fixture
def kob_eng_proof() -> Series:
    """KOB English proofed subtitles."""
    return Series.load(output_dir / "eng_proof.srt")


@pytest.fixture
def kob_eng_proof_clean_flatten() -> Series:
    """KOB English proofed, cleaned and flattened subtitles."""
    return Series.load(output_dir / "eng_proof_clean_flatten.srt")


# Bilingual 简体粤文 and English
@pytest.fixture()
def kob_yue_hans_eng() -> Series:
    """KOB Bilingual 简体粤文 and English subtitles."""
    return Series.load(output_dir / "yue-Hans_eng.srt")


___all__ = [
    "kob_zho_hant_fuse",
    "kob_zho_hant_fuse_proofread",
    "kob_yue_hans",
    "kob_yue_hans_clean",
    "kob_yue_hans_flatten",
    "kob_yue_hans_clean_flatten",
    "kob_yue_hant",
    "kob_yue_hant_simplify",
    "kob_eng_lens",
    "kob_eng_tesseract",
    "kob_eng_fuse",
    "kob_eng",
    "kob_eng_clean",
    "kob_eng_flatten",
    "kob_eng_proof",
    "kob_eng_proof_clean_flatten",
    "kob_yue_hans_eng",
    "kob_english_fusion_test_cases",
    "kob_english_proof_test_cases",
    "kob_zhongwen_fusion_test_cases",
    "kob_zhongwen_proofreading_test_cases",
]
