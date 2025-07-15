#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Answer for 粤文 proofreading."""

from __future__ import annotations

from pydantic import Field

from scinoephile.core.abcs import Answer


class ProofreadAnswer(Answer):
    """Answer for 粤文 proofreading."""

    yuewen_proofread: str = Field(..., description="Proofread 粤文 text.")
    note: str = Field(..., description="Description of corrections made.")
