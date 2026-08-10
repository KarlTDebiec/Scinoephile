#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processor for transcription LLM queries."""

from __future__ import annotations

from collections.abc import Sequence
from typing import cast

from scinoephile.core.llms import Processor

from .manager import TranscriptionManager
from .models import TranscriptionAnswer, TranscriptionQuery, TranscriptionSource
from .prompt import TranscriptionPrompt

__all__ = ["TranscriptionProcessor"]

_PAUSE_CHARACTER = "・"
"""Wide middle dot used for shared timed pauses."""
_REQUEST_PAUSE_CHARACTERS = 4
"""Shared pause columns required to start a separate LLM request."""


class TranscriptionProcessor(Processor):
    """Transcribe from reference-free aligned ASR evidence."""

    prompt: TranscriptionPrompt
    """Text for transcription."""
    manager_cls = TranscriptionManager
    """Manager used to construct prompt-specific models."""

    def process(
        self,
        sources: Sequence[TranscriptionSource],
        speaker: str,
        *,
        language_trace: str | None = None,
        music_trace: str | None = None,
        singing_trace: str | None = None,
    ) -> TranscriptionAnswer:
        """Transcribe one complete aligned ASR block.

        Arguments:
            sources: named equal-status aligned ASR rows
            speaker: aligned speaker and voice-activity row
            language_trace: optional aligned spoken-language row
            music_trace: optional aligned music row
            singing_trace: optional aligned singing row
        Returns:
            consensus transcript divided into subtitles
        """
        query_cls = self.test_case_cls.query_cls
        validated_query = cast(
            TranscriptionQuery,
            query_cls.model_validate(
                {
                    "sources": [source.model_dump(mode="json") for source in sources],
                    "speaker": speaker,
                    "language_trace": language_trace,
                    "singing_trace": singing_trace,
                    "music_trace": music_trace,
                }
            ),
        )
        if self.queryer.no_op:
            return TranscriptionAnswer(text="")

        request_answers = []
        for query in _get_request_queries(validated_query):
            test_case = self.test_case_cls(query=query)
            test_case = self.queryer(test_case)
            answer = cast(TranscriptionAnswer, test_case.answer)
            request_answers.append(answer)

        self.save_encountered_test_cases()
        return TranscriptionAnswer(
            text="".join(answer.text for answer in request_answers)
        )


def _get_query_slice(
    query: TranscriptionQuery, start: int, end: int
) -> TranscriptionQuery:
    """Get one alignment-column slice of a validated query.

    Arguments:
        query: validated complete-block alignment query
        start: inclusive alignment column index
        end: exclusive alignment column index
    Returns:
        sliced request query
    """
    update: dict[str, object] = {
        "sources": [
            source.model_copy(update={"text": source.text[start:end]})
            for source in query.sources
        ],
        "speaker": query.speaker[start:end],
    }
    if query.language_trace is not None:
        update["language_trace"] = query.language_trace[start:end]
    if query.music_trace is not None:
        update["music_trace"] = query.music_trace[start:end]
    if query.singing_trace is not None:
        update["singing_trace"] = query.singing_trace[start:end]
    return query.model_copy(update=update)


def _get_request_queries(query: TranscriptionQuery) -> tuple[TranscriptionQuery, ...]:
    """Split a validated alignment query at long shared pause runs."""
    requests = []
    content_spans = []
    content_start = 0
    pause_start: int | None = None
    for column_idx in range(len(query.speaker) + 1):
        is_shared_pause = column_idx < len(query.speaker) and (
            query.speaker[column_idx] == _PAUSE_CHARACTER
            and all(
                source.text[column_idx] == _PAUSE_CHARACTER for source in query.sources
            )
        )
        if is_shared_pause:
            if pause_start is None:
                pause_start = column_idx
            continue
        if pause_start is not None:
            if column_idx - pause_start >= _REQUEST_PAUSE_CHARACTERS:
                if content_start < pause_start:
                    content_spans.append((content_start, pause_start))
                content_start = column_idx
            pause_start = None
    if content_start < len(query.speaker):
        content_spans.append((content_start, len(query.speaker)))

    for content_start, content_end in content_spans:
        request = _get_query_slice(query, content_start, content_end)
        if any(
            character != _PAUSE_CHARACTER and not character.isspace()
            for source in request.sources
            for character in source.text
        ):
            requests.append(request)
    return tuple(requests)
