#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Finds and times the best path through CTC model output."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from scinoephile.audio.transcription.exceptions import (
    TranscriptionAlignmentError,
    TranscriptionAlignmentIncompleteError,
)

__all__ = ["get_best_path", "get_character_timings"]


def get_best_path(
    log_probs: np.ndarray, token_ids: Sequence[int], blank_token_id: int
) -> list[tuple[int, int, float]]:
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
    frame_count = _validate_best_path_inputs(log_probs, token_ids, blank_token_id)

    # Insert required blanks between adjacent repeated labels
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

    # Initialize and populate the alignment trellis
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

    # Select the best completed alignment
    final_column = trellis[:, alignment_token_count]
    if np.all(np.isneginf(final_column)):
        raise TranscriptionAlignmentIncompleteError(
            "CTC alignment did not reach all tokens."
        )
    frame_idx = int(np.argmax(final_column))

    # Backtrack through the trellis to recover token frame spans
    alignment_token_idx = alignment_token_count
    path: list[tuple[int, int, float]] = []
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
            score_token_id = token_id
        else:
            score_token_id = blank_token_id
        path.append(
            (
                path_token_indices[alignment_token_idx - 1],
                trellis_frame_idx - 1,
                float(np.exp(log_probs[trellis_frame_idx - 1, score_token_id])),
            )
        )
        if change_score > stay_score:
            alignment_token_idx -= 1
            if alignment_token_idx == 0:
                break
    else:
        raise TranscriptionAlignmentError("CTC alignment backtrack failed.")

    path.reverse()
    return path


def get_character_timings(
    path: Sequence[tuple[int, int, float]],
    char_indices: Sequence[int],
    frame_count: int,
    duration_seconds: float,
) -> dict[int, tuple[float, float, float]]:
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

    # Collapse consecutive frames assigned to each transcript character
    timed_chars: dict[int, tuple[float, float, float]] = {}
    path_idx = 0
    while path_idx < len(path):
        segment_end_idx = path_idx
        while (
            segment_end_idx < len(path)
            and path[path_idx][0] == path[segment_end_idx][0]
        ):
            segment_end_idx += 1

        token_idx = path[path_idx][0]
        if token_idx < 0 or token_idx >= len(char_indices):
            raise TranscriptionAlignmentError("CTC path token index is out of range.")
        char_idx = char_indices[token_idx]
        start = path[path_idx][1] * frame_duration
        end = (path[segment_end_idx - 1][1] + 1) * frame_duration
        confidence = sum(item[2] for item in path[path_idx:segment_end_idx]) / (
            segment_end_idx - path_idx
        )
        timed_chars[char_idx] = (round(start, 3), round(end, 3), round(confidence, 3))
        path_idx = segment_end_idx
    return timed_chars


def _validate_best_path_inputs(
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
