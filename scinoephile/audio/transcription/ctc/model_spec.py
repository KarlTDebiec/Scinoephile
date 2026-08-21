#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CTC model specifications."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.ml import ModelSpec
from scinoephile.core.script import ChineseScript

__all__ = ["CANTONESE_MODEL", "CHINESE_MODEL", "ENGLISH_MODEL", "CtcModelSpec"]


@dataclass(frozen=True, slots=True)
class CtcModelSpec(ModelSpec):
    """Complete specification of one CTC model."""

    script: ChineseScript | None
    """Chinese script used by the tokenizer, or None when not applicable."""


ENGLISH_MODEL = CtcModelSpec(
    name="facebook/wav2vec2-base-960h",
    revision="22aad52d435eb6dbaf354bdad9b0da84ce7d6156",
    script=None,
)
"""Default English CTC model specification."""

CANTONESE_MODEL = CtcModelSpec(
    name="ctl/wav2vec2-large-xlsr-cantonese",
    revision="11cb21cb68b4ed15f4c6633494ae6cc90a89bc34",
    script="Hant",
)
"""Default Cantonese CTC model specification."""

CHINESE_MODEL = CtcModelSpec(
    name="jonatasgrosman/wav2vec2-large-xlsr-53-chinese-zh-cn",
    revision="99ccb2737be22b8bb50dcfcc39ad4d567fb90cfd",
    script="Hans",
)
"""Default Chinese CTC model specification."""
