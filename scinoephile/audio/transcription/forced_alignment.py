#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Forced alignment for text-only transcription backends."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any, cast

import numpy as np

from .transcribed_segment import TranscribedSegment
from .transcribed_word import TranscribedWord

__all__ = [
    "TranscriptionAlignmentError",
    "align_mimo_transcription",
]

_WHISPERX_EXTRA_MESSAGE = (
    "MiMo timestamp alignment requires optional WhisperX dependencies in the "
    "selected runtime."
)
_CTC_WILDCARD_TOKEN_ID = -1
_CTC_COMPONENTS_BY_MODEL_AND_DEVICE: dict[tuple[str, str], tuple[object, object]] = {}


class TranscriptionAlignmentError(RuntimeError):
    """Raised when text-only transcription cannot be timestamp-aligned."""


def align_mimo_transcription(
    audio_path: Path,
    text: str,
    *,
    duration_seconds: float,
    aligner_backend: str = "whisperx",
    aligner_language: str = "zh",
    aligner_model_name: str | None = None,
    aligner_worker_command: Sequence[str] | None = None,
    aligner_worker_timeout_seconds: float | None = None,
    device: str = "cpu",
) -> list[TranscribedSegment]:
    """Align MiMo transcript text to source audio.

    Arguments:
        audio_path: source audio path to align against
        text: authoritative MiMo transcript text
        duration_seconds: source audio duration in seconds
        aligner_backend: forced-alignment backend identifier
        aligner_language: language code for the aligner
        aligner_model_name: optional aligner model checkpoint name
        aligner_worker_command: optional external aligner worker command
        aligner_worker_timeout_seconds: optional aligner worker timeout
        device: device identifier passed to the alignment backend
    Returns:
        timestamped transcription segments
    Raises:
        TranscriptionAlignmentError: if alignment cannot recover word timings
    """
    transcript_text = text.strip()
    if not transcript_text:
        raise TranscriptionAlignmentError("Cannot align empty transcript.")

    if aligner_worker_command is not None:
        result = _run_alignment_worker(
            audio_path=audio_path,
            text=transcript_text,
            duration_seconds=duration_seconds,
            aligner_backend=aligner_backend,
            aligner_language=aligner_language,
            aligner_model_name=aligner_model_name,
            aligner_worker_command=aligner_worker_command,
            aligner_worker_timeout_seconds=aligner_worker_timeout_seconds,
            device=device,
        )
        return _get_transcribed_segments_from_alignment_result(result)

    if aligner_backend == "ctc":
        return _align_with_ctc(
            audio_path=audio_path,
            text=transcript_text,
            duration_seconds=duration_seconds,
            aligner_model_name=aligner_model_name,
            device=device,
        )
    if aligner_backend != "whisperx":
        raise TranscriptionAlignmentError(
            f"Unsupported timestamp aligner backend: {aligner_backend}"
        )

    whisperx = _get_whisperx_module()
    load_align_model_kwargs: dict[str, object] = {
        "language_code": aligner_language,
        "device": device,
    }
    if aligner_model_name is not None:
        load_align_model_kwargs["model_name"] = aligner_model_name
    align_model, align_metadata = whisperx.load_align_model(**load_align_model_kwargs)

    transcript = [
        {"start": 0.0, "end": float(duration_seconds), "text": transcript_text}
    ]
    result = whisperx.align(
        transcript=transcript,
        model=align_model,
        align_model_metadata=align_metadata,
        audio=str(audio_path),
        device=device,
        return_char_alignments=False,
    )
    return _get_transcribed_segments_from_alignment_result(result)


def _align_with_ctc(
    *,
    audio_path: Path,
    text: str,
    duration_seconds: float,
    aligner_model_name: str | None,
    device: str,
) -> list[TranscribedSegment]:
    """Align transcript text with an in-house CTC trellis.

    Arguments:
        audio_path: source audio path to align against
        text: authoritative transcript text
        duration_seconds: source audio duration in seconds
        aligner_model_name: optional CTC model checkpoint name
        device: device identifier passed to the model backend
    Returns:
        timestamped transcription segment
    Raises:
        TranscriptionAlignmentError: if CTC alignment cannot recover timings
    """
    log_probs, token_ids, char_indices, blank_token_id = _get_ctc_alignment_inputs(
        audio_path=audio_path,
        text=text,
        aligner_model_name=aligner_model_name,
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
    aligner_model_name: str | None,
    device: str,
) -> tuple[np.ndarray, list[int], list[int], int]:
    """Get CTC log probabilities and transcript token mapping.

    Arguments:
        audio_path: source audio path to align against
        text: authoritative transcript text
        aligner_model_name: optional CTC model checkpoint name
        device: device identifier passed to the model backend
    Returns:
        log probabilities, token IDs, text character indices, and blank token ID
    Raises:
        ImportError: if CTC dependencies are unavailable
        TranscriptionAlignmentError: if transcript tokens cannot be prepared
    """
    model_name = (
        aligner_model_name or "jonatasgrosman/wav2vec2-large-xlsr-53-chinese-zh-cn"
    )
    processor, model = _get_ctc_components(model_name=model_name, device=device)
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
    if _CTC_WILDCARD_TOKEN_ID in token_ids:
        non_blank_mask = np.ones(log_probs.shape[1], dtype=bool)
        non_blank_mask[blank_token_id] = False
        if not non_blank_mask.any():
            raise TranscriptionAlignmentError("CTC wildcard needs non-blank tokens.")
        wildcard_column = np.max(log_probs[:, non_blank_mask], axis=1)
        wildcard_token_id = log_probs.shape[1]
        log_probs = np.concatenate(
            [log_probs, wildcard_column.reshape(-1, 1)],
            axis=1,
        )
        token_ids = [
            wildcard_token_id if token_id == _CTC_WILDCARD_TOKEN_ID else token_id
            for token_id in token_ids
        ]
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


def _get_ctc_components(*, model_name: str, device: str) -> tuple[object, object]:
    """Load or reuse a CTC processor and model from Hugging Face.

    Arguments:
        model_name: model checkpoint name or local path
        device: device identifier passed to the model backend
    Returns:
        processor and model
    Raises:
        ImportError: if Hugging Face CTC dependencies are unavailable
    """
    cache_key = (model_name, device)
    cached_components = _CTC_COMPONENTS_BY_MODEL_AND_DEVICE.get(cache_key)
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

    processor = AutoProcessor.from_pretrained(model_name)
    model = AutoModelForCTC.from_pretrained(model_name)
    if hasattr(model, "to"):
        model = model.to(device)
    if hasattr(model, "eval"):
        model.eval()
    components = (processor, model)
    _CTC_COMPONENTS_BY_MODEL_AND_DEVICE[cache_key] = components
    return components


def _get_ctc_token_id(*, char: str, tokenizer: object) -> int | None:
    """Get an aligner token ID for one transcript character.

    Arguments:
        char: transcript character
        tokenizer: Hugging Face tokenizer
    Returns:
        token ID, a wildcard sentinel for unknown non-space characters, or None
    """
    if char.isspace():
        return None

    unk_token_id = getattr(tokenizer, "unk_token_id", None)
    candidates = [char]
    lowered = char.lower()
    if lowered != char:
        candidates.append(lowered)

    convert_tokens_to_ids = getattr(tokenizer, "convert_tokens_to_ids", None)
    if not callable(convert_tokens_to_ids):
        return None
    for candidate in candidates:
        token_id = convert_tokens_to_ids(candidate)
        if isinstance(token_id, int) and token_id != unk_token_id:
            return token_id
    return _CTC_WILDCARD_TOKEN_ID


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
        one transcribed word per source character
    """
    words: list[TranscribedWord] = []
    char_idx = 0
    while char_idx < len(text):
        timing = timed_chars.get(char_idx)
        if timing is not None:
            start, end, confidence = timing
            words.append(
                TranscribedWord(
                    text=text[char_idx],
                    start=start,
                    end=end,
                    confidence=confidence,
                )
            )
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


def _parse_alignment_worker_stdout(stdout_text: str) -> Mapping[str, object]:
    """Parse alignment worker stdout, accepting logging before JSON.

    Arguments:
        stdout_text: worker stdout
    Returns:
        parsed worker payload
    Raises:
        TranscriptionAlignmentError: if no JSON object is found
    """
    for line in reversed(stdout_text.splitlines()):
        stripped_line = line.strip()
        if not stripped_line:
            continue
        try:
            payload = json.loads(stripped_line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, Mapping):
            return cast(Mapping[str, object], payload)
    raise TranscriptionAlignmentError("Alignment worker did not return a JSON object.")


def _run_alignment_worker(
    *,
    audio_path: Path,
    text: str,
    duration_seconds: float,
    aligner_backend: str,
    aligner_language: str,
    aligner_model_name: str | None,
    aligner_worker_command: Sequence[str],
    aligner_worker_timeout_seconds: float | None,
    device: str,
) -> Mapping[str, object]:
    """Run an external forced-alignment worker.

    Arguments:
        audio_path: source audio path to align against
        text: authoritative transcript text
        duration_seconds: source audio duration in seconds
        aligner_backend: forced-alignment backend identifier
        aligner_language: language code for the aligner
        aligner_model_name: optional aligner model checkpoint name
        aligner_worker_command: external aligner worker command
        aligner_worker_timeout_seconds: optional aligner worker timeout
        device: device identifier passed to the alignment backend
    Returns:
        parsed alignment payload
    Raises:
        TranscriptionAlignmentError: if the worker fails or returns malformed output
    """
    request = {
        "audio_path": str(audio_path),
        "backend": aligner_backend,
        "text": text,
        "duration_seconds": duration_seconds,
        "language": aligner_language,
        "model_name": aligner_model_name,
        "device": device,
    }
    try:
        result = subprocess.run(
            list(aligner_worker_command),
            input=json.dumps(request, ensure_ascii=False),
            text=True,
            capture_output=True,
            check=False,
            timeout=aligner_worker_timeout_seconds,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise TranscriptionAlignmentError(
            f"Unable to run alignment worker: {exc}"
        ) from exc
    if result.returncode != 0:
        raise TranscriptionAlignmentError(
            f"Alignment worker exited with status {result.returncode}: "
            f"{result.stderr.strip()}"
        )
    return _parse_alignment_worker_stdout(result.stdout)


def _get_transcribed_segments_from_alignment_result(
    result: Mapping[str, object],
) -> list[TranscribedSegment]:
    """Convert a WhisperX alignment result into transcribed segments.

    Arguments:
        result: WhisperX alignment result
    Returns:
        timestamped transcription segments
    Raises:
        TranscriptionAlignmentError: if segment or word timing data is unusable
    """
    raw_segments = result.get("segments")
    if not isinstance(raw_segments, Sequence):
        raise TranscriptionAlignmentError("Alignment result did not contain segments.")

    segments: list[TranscribedSegment] = []
    for segment_id, raw_segment_obj in enumerate(raw_segments):
        if not isinstance(raw_segment_obj, Mapping):
            raise TranscriptionAlignmentError("Alignment segment is malformed.")
        raw_segment = cast(Mapping[str, object], raw_segment_obj)

        segment_text = _get_text(raw_segment, "text")
        if not segment_text.strip():
            continue

        raw_words = raw_segment.get("words")
        if not isinstance(raw_words, Sequence) or not raw_words:
            raise TranscriptionAlignmentError(
                f"Alignment segment {segment_id} missing word timings."
            )
        words = _get_transcribed_words(segment_text, raw_words, segment_id=segment_id)
        if not words:
            raise TranscriptionAlignmentError(
                f"Alignment segment {segment_id} missing word timings."
            )

        segments.append(
            TranscribedSegment(
                id=segment_id,
                seek=0,
                start=_get_required_float(raw_segment, "start"),
                end=_get_required_float(raw_segment, "end"),
                text=segment_text,
                words=words,
            )
        )

    if not segments:
        raise TranscriptionAlignmentError("Alignment did not produce timed segments.")
    return segments


def _get_text(mapping: Mapping[str, object], key: str) -> str:
    """Get a required text value from a mapping.

    Arguments:
        mapping: mapping to read
        key: key to read
    Returns:
        text value
    Raises:
        TranscriptionAlignmentError: if the value is missing or malformed
    """
    value = mapping.get(key)
    if not isinstance(value, str):
        raise TranscriptionAlignmentError(f"Alignment field {key!r} is missing.")
    return value


def _get_optional_float(mapping: Mapping[str, object], key: str) -> float | None:
    """Get an optional float-compatible value from a mapping.

    Arguments:
        mapping: mapping to read
        key: key to read
    Returns:
        float value, if present
    Raises:
        TranscriptionAlignmentError: if the value is malformed
    """
    value = mapping.get(key)
    if value is None:
        return None
    if isinstance(value, int | float):
        return float(value)
    raise TranscriptionAlignmentError(f"Alignment field {key!r} is malformed.")


def _get_required_float(mapping: Mapping[str, object], key: str) -> float:
    """Get a required float-compatible value from a mapping.

    Arguments:
        mapping: mapping to read
        key: key to read
    Returns:
        float value
    Raises:
        TranscriptionAlignmentError: if the value is missing or malformed
    """
    value = _get_optional_float(mapping, key)
    if value is None:
        raise TranscriptionAlignmentError(f"Alignment field {key!r} is missing.")
    return value


def _get_transcribed_words(
    segment_text: str,
    raw_words: Sequence[object],
    *,
    segment_id: int,
) -> list[TranscribedWord]:
    """Convert WhisperX word dictionaries into transcribed words.

    Arguments:
        segment_text: full segment text used to recover inter-word whitespace
        raw_words: WhisperX word payloads
        segment_id: segment index for error messages
    Returns:
        transcribed words with timing data
    Raises:
        TranscriptionAlignmentError: if word timing data is missing
    """
    words: list[TranscribedWord] = []
    cursor = 0
    for word_idx, raw_word_obj in enumerate(raw_words):
        if not isinstance(raw_word_obj, Mapping):
            raise TranscriptionAlignmentError(
                f"Alignment segment {segment_id} word {word_idx} is malformed."
            )
        raw_word = cast(Mapping[str, object], raw_word_obj)

        word_text = _get_word_text(raw_word)
        match_text = word_text.strip()
        if not match_text:
            continue
        start = _get_optional_float(raw_word, "start")
        end = _get_optional_float(raw_word, "end")
        if start is None or end is None:
            raise TranscriptionAlignmentError(
                f"Alignment segment {segment_id} word {word_idx} missing word timings."
            )

        matched_idx = segment_text.find(match_text, cursor)
        if matched_idx >= cursor:
            word_text = f"{segment_text[cursor:matched_idx]}{match_text}"
            cursor = matched_idx + len(match_text)

        confidence = _get_optional_float(raw_word, "score")
        if confidence is None:
            confidence = _get_optional_float(raw_word, "confidence")
        if confidence is None:
            confidence = 0.0
        words.append(
            TranscribedWord(
                text=word_text,
                start=start,
                end=end,
                confidence=confidence,
            )
        )
    if words and 0 < cursor < len(segment_text):
        trailing_text = segment_text[cursor:]
        last_word = words[-1]
        words[-1] = last_word.model_copy(
            update={"text": f"{last_word.text}{trailing_text}"}
        )
    return words


def _get_whisperx_module() -> Any:
    """Import WhisperX on demand.

    Returns:
        imported WhisperX module
    Raises:
        ImportError: if WhisperX is unavailable
    """
    try:
        import whisperx  # ty: ignore[unresolved-import]  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(_WHISPERX_EXTRA_MESSAGE) from exc
    return whisperx


def _get_word_text(raw_word: Mapping[str, object]) -> str:
    """Get word text from a WhisperX word payload.

    Arguments:
        raw_word: WhisperX word payload
    Returns:
        word text
    Raises:
        TranscriptionAlignmentError: if text is missing or malformed
    """
    value = raw_word.get("word")
    if value is None:
        value = raw_word.get("text")
    if not isinstance(value, str):
        raise TranscriptionAlignmentError("Alignment word text is missing.")
    return value
