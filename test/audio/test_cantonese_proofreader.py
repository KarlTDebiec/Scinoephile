# Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
# and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.audio.transcription.CantoneseProofreader."""

from __future__ import annotations

from scinoephile.audio.models import ProofreadQuery
from scinoephile.audio.transcription import CantoneseProofreader
from scinoephile.testing.mark import skip_if_ci


@skip_if_ci()
def test_proofreader_dummy() -> None:
    """CantoneseProofreader runs without error."""
    proofreader = CantoneseProofreader()
    query = ProofreadQuery(zhongwen="测试", yuewen="測試")
    answer = proofreader(query)
    assert isinstance(answer.yuewen_proofread, str)
