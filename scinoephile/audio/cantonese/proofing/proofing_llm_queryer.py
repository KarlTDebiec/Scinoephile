#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Proofreads 粤文 subtitles based on 中文."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.audio.cantonese.proofing.proofing_answer import ProofingAnswer
from scinoephile.audio.cantonese.proofing.proofing_llm_text import ProofingLLMText
from scinoephile.audio.cantonese.proofing.proofing_query import ProofingQuery
from scinoephile.audio.cantonese.proofing.proofing_test_case import ProofingTestCase
from scinoephile.core.abcs import LLMQueryer


class ProofingLLMQueryer(
    LLMQueryer[ProofingQuery, ProofingAnswer, ProofingTestCase], ABC
):
    """Proofreads 粤文 text based on the corresponding 中文."""

    text: ClassVar[type[ProofingLLMText]] = ProofingLLMText
    """Text strings to be used for corresponding with LLM."""
