#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Forced alignment for text-only transcription backends."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any, cast

import numpy as np
from opencc import OpenCC

from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.audio.transcription.transcribed_word import TranscribedWord

__all__ = [
    "CTC_MODEL_NAME",
    "TranscriptionAlignmentError",
    "align_transcription",
]

CTC_MODEL_NAME = "jonatasgrosman/wav2vec2-large-xlsr-53-chinese-zh-cn"
"""Hugging Face model used for text-only transcription alignment."""

_CTC_COMPONENTS_BY_DEVICE: dict[str, tuple[object, object]] = {}
_CTC_SIMPLIFIER = OpenCC("t2s")
"""Converter from Traditional Chinese characters to the CTC model's script."""


class TranscriptionAlignmentError(RuntimeError):
    """Raised when text-only transcription cannot be timestamp-aligned."""


def align_transcription(
    audio_path: Path,
    text: str,
    *,
    duration_seconds: float,
    device: str = "cpu",
) -> list[TranscribedSegment]:
    """Align transcript text to source audio.

    Arguments:
        audio_path: source audio path to align against
        text: authoritative transcript text
        duration_seconds: source audio duration in seconds
        device: device identifier passed to the CTC model
    Returns:
        timestamped transcription segments
    Raises:
        TranscriptionAlignmentError: if alignment cannot recover word timings
    """
    transcript_text = text.strip()
    if not transcript_text:
        raise TranscriptionAlignmentError("Cannot align empty transcript.")

    try:
        return _align_with_ctc(
            audio_path=audio_path,
            text=transcript_text,
            duration_seconds=duration_seconds,
            device=device,
        )
    except TranscriptionAlignmentError:
        raise
    except (ImportError, OSError, RuntimeError, ValueError) as exc:
        raise TranscriptionAlignmentError(
            f"Unable to run CTC transcription alignment: {exc}"
        ) from exc


def _align_with_ctc(
    *,
    audio_path: Path,
    text: str,
    duration_seconds: float,
    device: str,
) -> list[TranscribedSegment]:
    """Align transcript text with an in-house CTC trellis.

    Arguments:
        audio_path: source audio path to align against
        text: authoritative transcript text
        duration_seconds: source audio duration in seconds
        device: device identifier passed to the model backend
    Returns:
        timestamped transcription segment
    Raises:
        TranscriptionAlignmentError: if CTC alignment cannot recover timings
    """
    log_probs, token_ids, char_indices, blank_token_id = _get_ctc_alignment_inputs(
        audio_path=audio_path,
        text=text,
        device=device,
    )
    if not token_ids:
        raise TranscriptionAlignmentError("CTC alignment found no supported tokens.")

    path = _get_ctc_best_path(
        log_probs=log_probs,
        token_ids=token_ids,
        blank_token_id=blank_token_id,
    )
    timed_chars = _get_ctc_character_timings(
        path=path,
        char_indices=char_indices,
        log_probs=log_probs,
        duration_seconds=duration_seconds,
    )
    words = _get_ctc_transcribed_words(
        text=text,
        timed_chars=timed_chars,
        duration_seconds=duration_seconds,
    )
    if not words:
        raise TranscriptionAlignmentError("CTC alignment did not produce timings.")

    return [
        TranscribedSegment(
            id=0,
            seek=0,
            start=words[0].start,
            end=words[-1].end,
            text=text,
            words=words,
        )
    ]


def _get_ctc_alignment_inputs(
    *,
    audio_path: Path,
    text: str,
    device: str,
) -> tuple[np.ndarray, list[int], list[int], int]:
    """Get CTC log probabilities and transcript token mapping.

    Arguments:
        audio_path: source audio path to align against
        text: authoritative transcript text
        device: device identifier passed to the model backend
    Returns:
        log probabilities, token IDs, text character indices, and blank token ID
    Raises:
        ImportError: if CTC dependencies are unavailable
        TranscriptionAlignmentError: if transcript tokens cannot be prepared
    """
    processor, model = _get_ctc_components(device=device)
    samples = _load_ctc_audio_samples(audio_path)
    processor_callable = cast(Callable[..., Mapping[str, Any]], processor)
    inputs = processor_callable(samples, sampling_rate=16000, return_tensors="pt")
    if device != "cpu":
        inputs = {key: value.to(device) for key, value in inputs.items()}

    torch = _get_torch_module()
    model_callable = cast(Callable[..., Any], model)
    with torch.no_grad():
        output = model_callable(**inputs)
        logits = output.logits[0]
        log_probs = logits.log_softmax(dim=-1).detach().cpu().numpy()

    blank_token_id = _get_ctc_blank_token_id(processor=processor, model=model)
    token_ids, char_indices = _get_ctc_token_ids(text=text, processor=processor)
    return log_probs, token_ids, char_indices, blank_token_id


def _get_ctc_best_path(
    *,
    log_probs: np.ndarray,
    token_ids: Sequence[int],
    blank_token_id: int,
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
    frame_count, token_count = _validate_ctc_best_path_inputs(
        log_probs=log_probs,
        token_ids=token_ids,
        blank_token_id=blank_token_id,
    )

    trellis = np.empty((frame_count + 1, token_count + 1))
    trellis[0, 0] = 0.0
    trellis[1:, 0] = np.cumsum(log_probs[:, blank_token_id])
    trellis[0, -token_count:] = -np.inf
    trellis[-token_count:, 0] = np.inf

    for token_id in token_ids:
        if token_id < 0 or token_id >= log_probs.shape[1]:
            raise TranscriptionAlignmentError("CTC target token ID is out of range.")

    for frame_idx in range(frame_count):
        stay_scores = trellis[frame_idx, 1:] + log_probs[frame_idx, blank_token_id]
        change_scores = trellis[frame_idx, :-1] + log_probs[frame_idx, token_ids]
        trellis[frame_idx + 1, 1:] = np.maximum(stay_scores, change_scores)

    final_column = trellis[:, token_count]
    if np.all(np.isneginf(final_column)):
        raise TranscriptionAlignmentError("CTC alignment did not reach all tokens.")

    frame_idx = int(np.argmax(final_column))
    token_idx = token_count
    path: list[tuple[int, int, float]] = []
    for trellis_frame_idx in range(frame_idx, 0, -1):
        token_id = token_ids[token_idx - 1]
        stay_score = (
            trellis[trellis_frame_idx - 1, token_idx]
            + log_probs[trellis_frame_idx - 1, blank_token_id]
        )
        change_score = (
            trellis[trellis_frame_idx - 1, token_idx - 1]
            + log_probs[trellis_frame_idx - 1, token_id]
        )
        if change_score > stay_score:
            score_token_id = token_id
        else:
            score_token_id = blank_token_id
        path.append(
            (
                token_idx - 1,
                trellis_frame_idx - 1,
                float(np.exp(log_probs[trellis_frame_idx - 1, score_token_id])),
            )
        )
        if change_score > stay_score:
            token_idx -= 1
            if token_idx == 0:
                break
    else:
        raise TranscriptionAlignmentError("CTC alignment backtrack failed.")

    path.reverse()
    return path


def _validate_ctc_best_path_inputs(
    *,
    log_probs: np.ndarray,
    token_ids: Sequence[int],
    blank_token_id: int,
) -> tuple[int, int]:
    """Validate CTC path inputs.

    Arguments:
        log_probs: frame-by-token log probabilities
        token_ids: target token IDs
        blank_token_id: model blank token ID
    Returns:
        frame count and token count
    Raises:
        TranscriptionAlignmentError: if CTC inputs are malformed
    """
    if log_probs.ndim != 2:
        raise TranscriptionAlignmentError("CTC log probabilities must be 2D.")
    frame_count = log_probs.shape[0]
    token_count = len(token_ids)
    if frame_count == 0:
        raise TranscriptionAlignmentError("CTC alignment received no audio frames.")
    if token_count == 0:
        raise TranscriptionAlignmentError("CTC alignment received no target tokens.")
    if blank_token_id < 0 or blank_token_id >= log_probs.shape[1]:
        raise TranscriptionAlignmentError("CTC blank token ID is out of range.")
    return frame_count, token_count


def _get_ctc_blank_token_id(*, processor: object, model: object) -> int:
    """Get the blank token ID used by a CTC model.

    Arguments:
        processor: Hugging Face processor
        model: Hugging Face CTC model
    Returns:
        blank token ID
    Raises:
        TranscriptionAlignmentError: if no blank token ID is available
    """
    config = getattr(model, "config", None)
    value = getattr(config, "pad_token_id", None)
    if isinstance(value, int):
        return value

    tokenizer = getattr(processor, "tokenizer", None)
    value = getattr(tokenizer, "pad_token_id", None)
    if isinstance(value, int):
        return value

    raise TranscriptionAlignmentError("CTC aligner did not expose a blank token ID.")


def _get_ctc_character_timings(
    *,
    path: Sequence[tuple[int, int, float]],
    char_indices: Sequence[int],
    log_probs: np.ndarray,
    duration_seconds: float,
) -> dict[int, tuple[float, float, float]]:
    """Convert a CTC path into original-text character timings.

    Arguments:
        path: CTC alignment path
        char_indices: original text indices for path token indices
        log_probs: frame-by-token log probabilities
        duration_seconds: source audio duration in seconds
    Returns:
        character index mapped to start, end, and confidence
    Raises:
        TranscriptionAlignmentError: if path entries are inconsistent
    """
    frame_count = log_probs.shape[0]
    if frame_count == 0:
        raise TranscriptionAlignmentError("CTC alignment received no audio frames.")
    frame_duration = duration_seconds / frame_count
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


def _get_ctc_components(*, device: str) -> tuple[object, object]:
    """Load or reuse a CTC processor and model from Hugging Face.

    Arguments:
        device: device identifier passed to the model backend
    Returns:
        processor and model
    Raises:
        ImportError: if Hugging Face CTC dependencies are unavailable
    """
    cached_components = _CTC_COMPONENTS_BY_DEVICE.get(device)
    if cached_components is not None:
        return cached_components

    try:
        from transformers import (  # noqa: PLC0415
            AutoModelForCTC,
            AutoProcessor,
        )
    except ImportError as exc:
        raise ImportError(
            "CTC timestamp alignment requires transformers and torch dependencies."
        ) from exc

    processor = AutoProcessor.from_pretrained(CTC_MODEL_NAME)
    model = AutoModelForCTC.from_pretrained(CTC_MODEL_NAME)
    if hasattr(model, "to"):
        model = model.to(device)
    if hasattr(model, "eval"):
        model.eval()
    components = (processor, model)
    _CTC_COMPONENTS_BY_DEVICE[device] = components
    return components


def _get_ctc_token_id(*, char: str, tokenizer: object) -> int | None:
    """Get an aligner token ID for one transcript character.

    Arguments:
        char: transcript character
        tokenizer: Hugging Face tokenizer
    Returns:
        token ID, or None when the character cannot be aligned directly
    """
    if char.isspace():
        return None

    unk_token_id = getattr(tokenizer, "unk_token_id", None)
    candidates = list(dict.fromkeys((char, char.upper(), char.lower())))
    simplified = _CTC_SIMPLIFIER.convert(char)
    if len(simplified) == 1:
        candidates.extend(
            candidate
            for candidate in (simplified, simplified.upper(), simplified.lower())
            if candidate not in candidates
        )

    convert_tokens_to_ids = getattr(tokenizer, "convert_tokens_to_ids", None)
    if not callable(convert_tokens_to_ids):
        return None
    for candidate in candidates:
        token_id = convert_tokens_to_ids(candidate)
        if isinstance(token_id, int) and token_id != unk_token_id:
            return token_id
    return None


def _get_ctc_token_ids(
    *,
    text: str,
    processor: object,
) -> tuple[list[int], list[int]]:
    """Get CTC token IDs and source text indices for supported characters.

    Arguments:
        text: authoritative transcript text
        processor: Hugging Face processor
    Returns:
        token IDs and original character indices
    Raises:
        TranscriptionAlignmentError: if the processor lacks a tokenizer
    """
    tokenizer = getattr(processor, "tokenizer", None)
    if tokenizer is None:
        raise TranscriptionAlignmentError("CTC aligner processor lacks a tokenizer.")

    token_ids: list[int] = []
    char_indices: list[int] = []
    for char_idx, char in enumerate(text):
        token_id = _get_ctc_token_id(char=char, tokenizer=tokenizer)
        if token_id is None:
            continue
        token_ids.append(token_id)
        char_indices.append(char_idx)
    return token_ids, char_indices


def _get_ctc_transcribed_words(
    *,
    text: str,
    timed_chars: Mapping[int, tuple[float, float, float]],
    duration_seconds: float,
) -> list[TranscribedWord]:
    """Build transcribed words covering aligned and unaligned characters.

    Arguments:
        text: authoritative transcript text
        timed_chars: character index mapped to start, end, and confidence
        duration_seconds: source audio duration in seconds
    Returns:
        transcribed words covering every source character
    """
    words: list[TranscribedWord] = []
    pending_text = ""
    char_idx = 0
    while char_idx < len(text):
        timing = timed_chars.get(char_idx)
        if timing is not None:
            start, end, confidence = timing
            words.append(
                TranscribedWord(
                    text=f"{pending_text}{text[char_idx]}",
                    start=start,
                    end=end,
                    confidence=confidence,
                )
            )
            pending_text = ""
            char_idx += 1
            continue

        run_start_idx = char_idx
        while char_idx < len(text) and char_idx not in timed_chars:
            char_idx += 1
        run_end_idx = char_idx
        previous_end = words[-1].end if words else 0.0
        next_start = duration_seconds
        if char_idx < len(text):
            next_timing = timed_chars.get(char_idx)
            if next_timing is not None:
                next_start = next_timing[0]
        run_length = run_end_idx - run_start_idx
        gap_seconds = max(next_start - previous_end, 0.0)
        if gap_seconds == 0.0:
            run_text = text[run_start_idx:run_end_idx]
            if words and char_idx < len(text):
                whitespace_idxs = [
                    idx for idx, char in enumerate(run_text) if char.isspace()
                ]
                if whitespace_idxs:
                    prefix_start_idx = whitespace_idxs[-1]
                    words[-1].text = f"{words[-1].text}{run_text[:prefix_start_idx]}"
                    pending_text = run_text[prefix_start_idx:]
                else:
                    words[-1].text = f"{words[-1].text}{run_text}"
            elif words:
                words[-1].text = f"{words[-1].text}{run_text}"
            else:
                pending_text = run_text
            continue

        char_duration = gap_seconds / run_length if run_length else 0.0
        for offset, unaligned_char_idx in enumerate(range(run_start_idx, run_end_idx)):
            start = previous_end + (offset * char_duration)
            end = previous_end + ((offset + 1) * char_duration)
            words.append(
                TranscribedWord(
                    text=text[unaligned_char_idx],
                    start=start,
                    end=end,
                    confidence=0.0,
                )
            )

    return words


def _get_torch_module() -> Any:
    """Get the torch module.

    Returns:
        imported torch module
    Raises:
        ImportError: if torch is unavailable
    """
    try:
        import torch  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            "CTC timestamp alignment requires transformers and torch dependencies."
        ) from exc
    return torch


def _load_ctc_audio_samples(audio_path: Path) -> np.ndarray:
    """Load audio samples for CTC alignment.

    Arguments:
        audio_path: audio file to load
    Returns:
        mono 16 kHz float32 samples
    Raises:
        TranscriptionAlignmentError: if audio contains no samples
    """
    from pydub import AudioSegment  # noqa: PLC0415

    audio = (
        AudioSegment.from_file(audio_path)
        .set_channels(1)
        .set_frame_rate(16000)
        .set_sample_width(2)
    )
    samples = np.array(audio.get_array_of_samples(), dtype=np.float32) / 32768.0
    if samples.size == 0:
        raise TranscriptionAlignmentError("CTC alignment received empty audio.")
    return samples
