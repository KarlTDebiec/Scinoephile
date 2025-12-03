#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Proofreads 粤文 subtitles based on 中文."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.abcs import LLMQueryer

from .answer import ProofingAnswer
from .prompt import ProofingPrompt
from .query import ProofingQuery
from .test_case import ProofingTestCase

__all__ = ["ProofingLLMQueryer"]


class ProofingLLMQueryer(LLMQueryer[ProofingQuery, ProofingAnswer, ProofingTestCase]):
    """Proofreads 粤文 text based on the corresponding 中文."""

    text: ClassVar[type[ProofingPrompt]] = ProofingPrompt
    """Text strings to be used for corresponding with LLM."""
