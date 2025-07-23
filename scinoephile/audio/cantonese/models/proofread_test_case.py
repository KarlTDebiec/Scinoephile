#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for 粤文 proofing; may also be used for few-shot prompt."""

from __future__ import annotations

from scinoephile.audio.cantonese.models.proofread_answer import ProofAnswer
from scinoephile.audio.cantonese.models.proofread_query import ProofQuery
from scinoephile.core.abcs import TestCase


class ProofTestCase(ProofQuery, ProofAnswer, TestCase[ProofQuery, ProofAnswer]):
    """Test case for 粤文 proofing; may also be used for few-shot prompt."""
