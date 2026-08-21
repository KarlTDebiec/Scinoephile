#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shapes CTC character timings into transcribed words."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from scinoephile.audio.transcription.transcribed_word import TranscribedWord
from scinoephile.core import Language

__all__ = ["get_transcribed_words"]


def get_transcribed_words(
    language: Language,
    text: str,
    timed_chars: Mapping[int, tuple[float, float, float]],
    duration_seconds: float,
) -> list[TranscribedWord]:
    """Build transcribed words covering aligned and unaligned characters.

    Arguments:
        language: transcription language
        text: transcription text
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
        run_text = text[run_start_idx:run_end_idx]

        boundary_pending_text = _attach_boundary_text(
            run_text, words, char_idx < len(text)
        )
        if boundary_pending_text is not None:
            pending_text = boundary_pending_text
            continue

        previous_end = words[-1].end if words else 0.0
        next_start = duration_seconds
        if char_idx < len(text):
            next_timing = timed_chars.get(char_idx)
            if next_timing is not None:
                next_start = next_timing[0]

        gap_seconds = max(next_start - previous_end, 0.0)
        if gap_seconds == 0.0:
            if not words:
                pending_text = run_text
                continue
            prefix_start_idx = next(
                (
                    idx
                    for idx in range(len(run_text) - 1, -1, -1)
                    if run_text[idx].isspace()
                ),
                len(run_text),
            )
            words[-1].text += run_text[:prefix_start_idx]
            pending_text = run_text[prefix_start_idx:]
            continue

        run_length = run_end_idx - run_start_idx
        char_duration = gap_seconds / run_length
        for offset, unaligned_char_idx in enumerate(range(run_start_idx, run_end_idx)):
            start = previous_end + (offset * char_duration)
            end = previous_end + ((offset + 1) * char_duration)
            words.append(
                TranscribedWord(
                    text=text[unaligned_char_idx], start=start, end=end, confidence=0.0
                )
            )

    if language is Language.eng:
        return _group_english_words(words)
    return words


def _attach_boundary_text(
    run_text: str, words: list[TranscribedWord], has_next_timing: bool
) -> str | None:
    """Attach unaligned boundary punctuation or whitespace to a timed character.

    Arguments:
        run_text: unaligned text at a transcript boundary
        words: transcribed words built so far
        has_next_timing: whether an aligned character follows the run
    Returns:
        pending prefix text when handled, otherwise None
    """
    if words and not has_next_timing and not any(char.isalnum() for char in run_text):
        words[-1].text += run_text
        return ""
    if not words and run_text.isspace():
        return run_text
    return None


def _group_english_words(
    character_words: Sequence[TranscribedWord],
) -> list[TranscribedWord]:
    """Group English character timings into whitespace-delimited words.

    Arguments:
        character_words: individually timed characters
    Returns:
        whitespace-delimited words with aggregate timings and confidence
    """
    word_parts: list[list[TranscribedWord]] = []
    for character_word in character_words:
        if (
            character_word.text[0].isspace()
            and word_parts
            and not all(part.text.isspace() for part in word_parts[-1])
        ):
            word_parts.append([])
        elif not word_parts:
            word_parts.append([])
        word_parts[-1].append(character_word)

    if (
        len(word_parts) > 1
        and word_parts[-1]
        and all(part.text.isspace() for part in word_parts[-1])
    ):
        word_parts[-2].extend(word_parts.pop())

    words: list[TranscribedWord] = []
    for parts in word_parts:
        durations = [max(part.end - part.start, 0.0) for part in parts]
        total_duration = sum(durations)
        if total_duration > 0.0:
            confidence = (
                sum(
                    part.confidence * duration
                    for part, duration in zip(parts, durations, strict=True)
                )
                / total_duration
            )
        else:
            confidence = sum(part.confidence for part in parts) / len(parts)
        words.append(
            TranscribedWord(
                text="".join(part.text for part in parts),
                start=parts[0].start,
                end=parts[-1].end,
                confidence=round(confidence, 3),
            )
        )
    return words
