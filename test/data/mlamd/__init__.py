#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MLAMD."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from scinoephile.core import Series
from scinoephile.image import ImageSeries
from scinoephile.testing import test_data_root

# ruff: noqa: F401 F403
from test.data.mlamd.core.english.proof import mlamd_english_proof_test_cases
from test.data.mlamd.core.zhongwen.proofreading import (
    test_cases as mlamd_zhongwen_proofreading_test_cases,
)
from test.data.mlamd.distribution import mlamd_distribute_test_cases
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


# region 简体中文
@pytest.fixture
def mlamd_zho_hans_lens() -> Series:
    """MLAMD 简体中文 subtitles OCRed using Google Lens OCR."""
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


# endregion


# region English
@pytest.fixture
def mlamd_eng() -> Series:
    """MLAMD English subtitles."""
    return Series.load(input_dir / "eng.srt")


@pytest.fixture
def mlamd_eng_clean() -> Series:
    """MLAMD English cleaned subtitles."""
    return Series.load(output_dir / "eng_clean.srt")


@pytest.fixture
def mlamd_eng_flatten() -> Series:
    """MLAMD English flattened subtitles."""
    return Series.load(output_dir / "eng_flatten.srt")


@pytest.fixture
def mlamd_eng_proof() -> Series:
    """MLAMD English proofed subtitles."""
    return Series.load(output_dir / "eng_proof.srt")


@pytest.fixture
def mlamd_eng_proof_clean_flatten() -> Series:
    """MLAMD English proofed, cleaned and flattened subtitles."""
    return Series.load(output_dir / "eng_proof_clean_flatten.srt")


# endregion


___all__ = [
    "mlamd_zho_hans_lens",
    "mlamd_zho_hans_paddle",
    "mlamd_zho_hans_fuse",
    "mlamd_zho_hans_fuse_proofread",
    "mlamd_zho_hans_fuse_proofread_clean",
    "mlamd_zho_hans_fuse_proofread_clean_flatten",
    "mlamd_eng",
    "mlamd_eng_clean",
    "mlamd_eng_flatten",
    "mlamd_eng_proof",
    "mlamd_eng_proof_clean_flatten",
    "mlamd_distribute_test_cases",
    "mlamd_shift_test_cases",
    "mlamd_merge_test_cases",
    "mlamd_proof_test_cases",
    "mlamd_translate_test_cases",
    "mlamd_review_test_cases",
    "mlamd_english_proof_test_cases",
    "mlamd_zhongwen_fusion_test_cases",
    "mlamd_zhongwen_proofreading_test_cases",
]
