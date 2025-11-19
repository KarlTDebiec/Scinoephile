#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Answer for 粤文 proofing."""

from __future__ import annotations

from pydantic import Field, model_validator

from scinoephile.core.abcs import Answer


class ProofAnswer(Answer):
    """Answer for 粤文 proofing."""

    yuewen_proofread: str = Field(..., description="Proofread 粤文 of subtitle")
    note: str = Field(..., description="Description of corrections made")

    @model_validator(mode="after")
    def validate_answer(self) -> ProofAnswer:
        """Ensure answer is internally valid."""
        if not self.yuewen_proofread and not self.note:
            raise ValueError(
                "If Answer omits proofread 粤文 of subtitle to indicate that 粤文 is "
                "believed to be a complete mistranscription of the spoken Cantonese "
                "and should be omitted, it must also include a note describing the "
                "issue."
            )
        return self
