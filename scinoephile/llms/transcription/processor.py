#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processor for transcription LLM queries."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from logging import getLogger
from typing import cast

from pydantic import ValidationError

from scinoephile.core.llms import Processor

from .manager import TranscriptionManager
from .models import TranscriptionAnswer, TranscriptionQuery, TranscriptionSource
from .prompt import TranscriptionPrompt

__all__ = ["TranscriptionProcessor", "TranscriptionRequestResult"]

logger = getLogger(__name__)

_REQUEST_PAUSE_CHARACTERS = 4
"""Shared pause columns required to start a separate LLM request."""


@dataclass(frozen=True, slots=True)
class TranscriptionRequestResult:
    """Consensus answer and alignment span for one LLM request."""

    start_column: int
    """Inclusive alignment column index."""
    end_column: int
    """Exclusive alignment column index."""
    answer: TranscriptionAnswer
    """Consensus subtitles returned for the request."""
    query_key_sha256: str
    """Digest of the request's semantic query key."""


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
        language: str | None = None,
        music: str | None = None,
        singing: str | None = None,
    ) -> TranscriptionAnswer:
        """Transcribe one complete aligned ASR block.

        Arguments:
            sources: named equal-status aligned ASR rows
            speaker: aligned speaker and voice-activity row
            language: optional aligned spoken-language row
            music: optional aligned music row
            singing: optional aligned singing row
        Returns:
            consensus transcript divided into subtitles
        """
        request_results = self.process_requests(
            sources, speaker, language=language, music=music, singing=singing
        )
        return TranscriptionAnswer(
            text="".join(result.answer.text for result in request_results)
        )

    def process_requests(
        self,
        sources: Sequence[TranscriptionSource],
        speaker: str,
        *,
        language: str | None = None,
        music: str | None = None,
        singing: str | None = None,
    ) -> tuple[TranscriptionRequestResult, ...]:
        """Transcribe aligned ASR evidence as separately timed requests.

        Arguments:
            sources: named equal-status aligned ASR rows
            speaker: aligned speaker and voice-activity row
            language: optional aligned spoken-language row
            music: optional aligned music row
            singing: optional aligned singing row
        Returns:
            request answers with their complete-alignment column spans
        """
        query_cls = self.test_case_cls.query_cls
        validated_query = cast(
            TranscriptionQuery,
            query_cls.model_validate(
                {
                    "sources": [source.model_dump(mode="json") for source in sources],
                    "speaker": speaker,
                    "language": language,
                    "singing": singing,
                    "music": music,
                }
            ),
        )
        request_results = []
        for query, (start_column, end_column) in _get_request_queries(validated_query):
            test_case = self.test_case_cls(query=query)
            try:
                test_case = self.queryer(test_case)
            except ValidationError:
                answer = test_case.get_no_op_answer()
                test_case = self.test_case_cls.model_validate(
                    {
                        **test_case.model_dump(mode="json"),
                        "answer": answer.model_dump(mode="json"),
                        "few_shot": False,
                        "verified": False,
                    }
                )
                test_case = self.queryer.store_answered_test_case(test_case)
                logger.warning(
                    "LLM exhausted valid transcription answers; used deterministic "
                    f"column consensus: {query.key_str}"
                )
            answer = cast(TranscriptionAnswer, test_case.answer)
            request_results.append(
                TranscriptionRequestResult(
                    start_column, end_column, answer, query.key_sha256
                )
            )

        self.save_encountered_test_cases()
        return tuple(request_results)


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
    if query.language is not None:
        update["language"] = query.language[start:end]
    if query.music is not None:
        update["music"] = query.music[start:end]
    if query.singing is not None:
        update["singing"] = query.singing[start:end]
    return query.model_copy(update=update)


def _get_request_queries(
    query: TranscriptionQuery,
) -> tuple[tuple[TranscriptionQuery, tuple[int, int]], ...]:
    """Split a validated alignment query at long shared pause runs."""
    requests = []
    content_spans = []
    content_start = 0
    pause_start: int | None = None
    rows = (
        query.speaker,
        *(source.text for source in query.sources),
        *(
            annotation
            for annotation in (query.language, query.singing, query.music)
            if annotation is not None
        ),
    )
    for column_idx in range(len(query.speaker) + 1):
        is_shared_pause = column_idx < len(query.speaker) and all(
            row[column_idx] == "・" for row in rows
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
            character != "・" and not character.isspace()
            for source in request.sources
            for character in source.text
        ):
            requests.append((request, (content_start, content_end)))
    return tuple(requests)
