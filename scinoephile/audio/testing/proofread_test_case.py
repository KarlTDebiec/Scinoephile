# Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
# and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test case for 粤文 proofreading; may also be used for few-shot prompt."""

from __future__ import annotations

from scinoephile.audio.models import ProofreadAnswer, ProofreadQuery
from scinoephile.core.abcs import TestCase


class ProofreadTestCase(
    ProofreadQuery, ProofreadAnswer, TestCase[ProofreadQuery, ProofreadAnswer]
):
    """Test case for 粤文 proofreading; may also be used for few-shot prompt."""

    pass
