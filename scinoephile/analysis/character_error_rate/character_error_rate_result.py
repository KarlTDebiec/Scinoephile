#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Character error rate result record."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["CharacterErrorRateResult"]


@dataclass(frozen=True)
class CharacterErrorRateResult:
    """Aggregate character error rate results."""

    cer: float
    """Character error rate."""

    substitutions: int
    """Number of character substitutions."""

    insertions: int
    """Number of character insertions."""

    deletions: int
    """Number of character deletions."""

    correct: int
    """Number of correctly matched reference characters."""

    reference_length: int
    """Number of characters in the normalized reference text."""

    def __str__(self) -> str:
        """String representation.

        Returns:
            formatted character error rate summary
        """
        return (
            f"CER: {self.cer}\n"
            f"Correct: {self.correct}\n"
            f"Substitutions: {self.substitutions}\n"
            f"Insertions: {self.insertions}\n"
            f"Deletions: {self.deletions}\n"
            f"Reference length: {self.reference_length}"
        )
