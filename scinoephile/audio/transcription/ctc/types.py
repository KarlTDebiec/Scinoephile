#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Types used by CTC transcription alignment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

__all__ = ["CtcCharacterTiming", "CtcPathStep", "CtcResult", "CtcTokenizer"]


@dataclass(frozen=True, slots=True)
class CtcCharacterTiming:
    """Timing and confidence assigned to one transcript character."""

    start: float
    """Start time in seconds."""

    end: float
    """End time in seconds."""

    confidence: float
    """Mean CTC path probability."""


@dataclass(frozen=True, slots=True)
class CtcPathStep:
    """One frame in the best CTC alignment path."""

    token_idx: int
    """Index in the target token sequence."""

    frame_idx: int
    """Index in the model output frames."""

    probability: float
    """Probability of the selected model token at this frame."""


@dataclass(frozen=True, slots=True)
class CtcResult:
    """Output prepared by a CTC model for alignment."""

    log_probs: np.ndarray
    """Log probabilities for each frame and token."""

    token_ids: list[int]
    """Model token IDs corresponding to supported transcript characters."""

    char_indices: list[int]
    """Transcript character indices corresponding to model token IDs."""

    blank_token_id: int
    """Model token ID representing the CTC blank label."""


class CtcTokenizer(Protocol):
    """Tokenizer interface required by CTC alignment."""

    @property
    def unk_token_id(self) -> int | None:
        """Get the model's unknown token ID."""
        ...

    def convert_tokens_to_ids(self, token: str) -> int | None:
        """Convert one token to its model ID.

        Arguments:
            token: token text
        Returns:
            model token ID, or None when unavailable
        """
        ...
