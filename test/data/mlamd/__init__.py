#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MLAMD."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.core import Series
from scinoephile.testing import test_data_root

# ruff: noqa: F401 F403
from test.data.mlamd.core.english.proof import mlamd_english_proof_test_cases
from test.data.mlamd.core.zhongwen.proofreading import (
    test_cases as mlamd_zhongwen_proofreading_test_cases,
)
from test.data.mlamd.distribution import mlamd_distribute_test_cases
from test.data.mlamd.image.english.fusion import (
    test_cases as mlamd_english_fusion_test_cases,
)
from test.data.mlamd.image.zhongwen.fusion import (
    test_cases as mlamd_zhongwen_fusion_test_cases,
)
from test.data.mlamd.merging import mlamd_merge_test_cases
from test.data.mlamd.proofing import mlamd_proof_test_cases
from test.data.mlamd.review import mlamd_review_test_cases
from test.data.mlamd.shifting import mlamd_shift_test_cases
from test.data.mlamd.translation import mlamd_translate_test_cases

title = Path(__file__).parent.name
input_dir = test_data_root / title / "input"
output_dir = test_data_root / title / "output"


# 简体中文 (OCR)
@pytest.fixture
def mlamd_zho_hans_lens() -> Series:
    """MLAMD 简体中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hans_lens.srt")


@pytest.fixture
def mlamd_zho_hans_paddle() -> Series:
    """MLAMD 简体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hans_paddle.srt")


@pytest.fixture
def mlamd_zho_hans_fuse() -> Series:
    """MLAMD 简体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse.srt")


@pytest.fixture
def mlamd_zho_hans_fuse_proofread() -> Series:
    """MLAMD 简体中文 fused and proofread subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_proofread.srt")


@pytest.fixture
def mlamd_zho_hans_fuse_proofread_clean() -> Series:
    """MLAMD 简体中文 fused, proofread, and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_proofread_clean.srt")


@pytest.fixture
def mlamd_zho_hans_fuse_proofread_clean_flatten() -> Series:
    """MLAMD 简体中文 fused, proofread, cleaned, and flattened subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_proofread_clean_flatten.srt")


# English (OCR)
@pytest.fixture
def mlamd_eng_lens() -> Series:
    """MLAMD English subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "english_lens.srt")


@pytest.fixture
def mlamd_eng_tesseract() -> Series:
    """MLAMD English subtitles OCRed using Tesseract."""
    return Series.load(input_dir / "english_tesseract.srt")


@pytest.fixture
def mlamd_eng_fuse() -> Series:
    """MLAMD English fused subtitles."""
    return Series.load(output_dir / "english_fuse.srt")


___all__ = [
    "mlamd_zho_hans_lens",
    "mlamd_zho_hans_paddle",
    "mlamd_zho_hans_fuse",
    "mlamd_zho_hans_fuse_proofread",
    "mlamd_zho_hans_fuse_proofread_clean",
    "mlamd_zho_hans_fuse_proofread_clean_flatten",
    "mlamd_eng_lens",
    "mlamd_eng_tesseract",
    "mlamd_eng_fuse",
    "mlamd_distribute_test_cases",
    "mlamd_shift_test_cases",
    "mlamd_merge_test_cases",
    "mlamd_proof_test_cases",
    "mlamd_translate_test_cases",
    "mlamd_review_test_cases",
    "mlamd_english_fusion_test_cases",
    "mlamd_english_proof_test_cases",
    "mlamd_zhongwen_fusion_test_cases",
    "mlamd_zhongwen_proofreading_test_cases",
]
