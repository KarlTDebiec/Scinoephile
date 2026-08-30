#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Finds character timings through CTC output probabilities."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from scinoephile.audio.transcription.exceptions import (
    TranscriptionAlignmentError,
    TranscriptionAlignmentIncompleteError,
)

from .types import CtcCharacterTiming, CtcPathStep

__all__ = ["get_best_path", "get_character_timings"]


def get_best_path(
    log_probs: np.ndarray, token_ids: Sequence[int], blank_token_id: int
) -> list[CtcPathStep]:
    """Get the best CTC path through a transcript-token trellis.

    Arguments:
        log_probs: frame-by-token log probabilities
        token_ids: target token IDs
        blank_token_id: model blank token ID
    Returns:
        path entries as transcript token index, frame index, and probability
    Raises:
        TranscriptionAlignmentError: if no complete path can be found
    """
    frame_count = _validate_inputs(log_probs, token_ids, blank_token_id)

    alignment_token_ids: list[int] = []
    path_token_indices: list[int] = []
    for token_idx, token_id in enumerate(token_ids):
        if token_id < 0 or token_id >= log_probs.shape[1]:
            raise TranscriptionAlignmentError("CTC target token ID is out of range.")
        if token_idx > 0 and token_id == token_ids[token_idx - 1]:
            alignment_token_ids.append(blank_token_id)
            path_token_indices.append(token_idx - 1)
        alignment_token_ids.append(token_id)
        path_token_indices.append(token_idx)

    alignment_token_count = len(alignment_token_ids)
    trellis = np.empty((frame_count + 1, alignment_token_count + 1))
    trellis[0, 0] = 0.0
    trellis[1:, 0] = np.cumsum(log_probs[:, blank_token_id])
    trellis[0, -alignment_token_count:] = -np.inf
    trellis[-alignment_token_count:, 0] = np.inf
    for frame_idx in range(frame_count):
        stay_scores = trellis[frame_idx, 1:] + log_probs[frame_idx, blank_token_id]
        token_log_probs = log_probs[frame_idx, alignment_token_ids]
        change_scores = trellis[frame_idx, :-1] + token_log_probs
        trellis[frame_idx + 1, 1:] = np.maximum(stay_scores, change_scores)

    final_column = trellis[:, alignment_token_count]
    if np.all(np.isneginf(final_column)):
        raise TranscriptionAlignmentIncompleteError(
            "CTC alignment did not reach all tokens."
        )
    frame_idx = int(np.argmax(final_column))

    alignment_token_idx = alignment_token_count
    path: list[CtcPathStep] = []
    for trellis_frame_idx in range(frame_idx, 0, -1):
        token_id = alignment_token_ids[alignment_token_idx - 1]
        stay_score = (
            trellis[trellis_frame_idx - 1, alignment_token_idx]
            + log_probs[trellis_frame_idx - 1, blank_token_id]
        )
        change_score = (
            trellis[trellis_frame_idx - 1, alignment_token_idx - 1]
            + log_probs[trellis_frame_idx - 1, token_id]
        )
        if change_score > stay_score:
            if token_id != blank_token_id:
                path.append(
                    CtcPathStep(
                        token_idx=path_token_indices[alignment_token_idx - 1],
                        frame_idx=trellis_frame_idx - 1,
                        probability=float(
                            np.exp(log_probs[trellis_frame_idx - 1, token_id])
                        ),
                    )
                )
            alignment_token_idx -= 1
            if alignment_token_idx == 0:
                break
    else:
        raise TranscriptionAlignmentError("CTC alignment backtrack failed.")

    path.reverse()
    return path


def get_character_timings(
    path: Sequence[CtcPathStep],
    char_indices: Sequence[int],
    frame_count: int,
    duration_seconds: float,
) -> dict[int, CtcCharacterTiming]:
    """Convert a CTC path into original-text character timings.

    Arguments:
        path: CTC alignment path
        char_indices: original text indices for path token indices
        frame_count: number of audio frames represented by the CTC output
        duration_seconds: source audio duration in seconds
    Returns:
        character index mapped to start, end, and confidence
    Raises:
        TranscriptionAlignmentError: if path entries are inconsistent
    """
    if frame_count == 0:
        raise TranscriptionAlignmentError("CTC alignment received no audio frames.")
    frame_duration = duration_seconds / frame_count

    timed_chars: dict[int, CtcCharacterTiming] = {}
    for step in path:
        token_idx = step.token_idx
        if token_idx < 0 or token_idx >= len(char_indices):
            raise TranscriptionAlignmentError("CTC path token index is out of range.")
        char_idx = char_indices[token_idx]
        timed_chars[char_idx] = CtcCharacterTiming(
            start=round(step.frame_idx * frame_duration, 3),
            end=round((step.frame_idx + 1) * frame_duration, 3),
            confidence=round(step.probability, 3),
        )
    return timed_chars


def _validate_inputs(
    log_probs: np.ndarray, token_ids: Sequence[int], blank_token_id: int
) -> int:
    """Validate CTC path inputs.

    Arguments:
        log_probs: frame-by-token log probabilities
        token_ids: target token IDs
        blank_token_id: model blank token ID
    Returns:
        frame count
    Raises:
        TranscriptionAlignmentError: if CTC inputs are malformed
    """
    if log_probs.ndim != 2:
        raise TranscriptionAlignmentError("CTC log probabilities must be 2D.")
    frame_count = log_probs.shape[0]
    if frame_count == 0:
        raise TranscriptionAlignmentError("CTC alignment received no audio frames.")
    if not token_ids:
        raise TranscriptionAlignmentError("CTC alignment received no target tokens.")
    if blank_token_id < 0 or blank_token_id >= log_probs.shape[1]:
        raise TranscriptionAlignmentError("CTC blank token ID is out of range.")
    return frame_count
