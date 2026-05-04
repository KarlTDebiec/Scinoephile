#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Operation specifications for written Cantonese transcription."""

from __future__ import annotations

from scinoephile.core.llms import OperationSpec
from scinoephile.llms.dual_pair import DualPairManager

from .deliniation import YueVsZhoYueHansDeliniationPrompt
from .punctuation import YueVsZhoYueHansPunctuationPrompt, YueZhoPunctuationManager

__all__ = [
    "YUE_ZHO_TRANSCRIPTION_DELINIATION_OPERATION_SPEC",
    "YUE_ZHO_TRANSCRIPTION_PUNCTUATION_OPERATION_SPEC",
]

YUE_ZHO_TRANSCRIPTION_DELINIATION_OPERATION_SPEC = OperationSpec(
    operation="yue-zho-transcription-deliniation",
    test_case_table_name="test_cases__yue_zho__transcription_deliniation",
    manager_cls=DualPairManager,
    prompt_cls=YueVsZhoYueHansDeliniationPrompt,
)
"""Operation specification for written Cantonese transcription deliniation."""

YUE_ZHO_TRANSCRIPTION_PUNCTUATION_OPERATION_SPEC = OperationSpec(
    operation="yue-zho-transcription-punctuation",
    test_case_table_name="test_cases__yue_zho__transcription_punctuation",
    manager_cls=YueZhoPunctuationManager,
    prompt_cls=YueVsZhoYueHansPunctuationPrompt,
)
"""Operation specification for written Cantonese transcription punctuation."""
