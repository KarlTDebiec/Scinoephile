#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Types used by CTC transcription alignment."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

__all__ = ["CtcResult"]


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
