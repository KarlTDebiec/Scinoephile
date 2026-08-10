#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processor for aligned transcription merge LLM queries."""

from __future__ import annotations

from collections.abc import Sequence
from typing import cast

from scinoephile.core.llms import Processor

from .manager import AlignedTranscriptionMergeManager
from .models import (
    AlignedTranscriptionMergeAnswer,
    AlignedTranscriptionMergeQuery,
    AlignedTranscriptionMergeSource,
)
from .prompt import AlignedTranscriptionMergePrompt
from .splitting import get_alignment_content_spans

__all__ = ["AlignedTranscriptionMergeProcessor"]

_PAUSE_CHARACTER = "・"
"""Wide middle dot used for shared timed pauses."""
_REQUEST_PAUSE_CHARACTERS = 4
"""Shared pause columns required to start a separate LLM request."""


class AlignedTranscriptionMergeProcessor(Processor):
    """Merge reference-free aligned ASR evidence into consensus subtitles."""

    prompt: AlignedTranscriptionMergePrompt
    """Text for aligned transcription merging."""
    manager_cls = AlignedTranscriptionMergeManager
    """Manager used to construct prompt-specific models."""
    last_request_answers: tuple[AlignedTranscriptionMergeAnswer, ...] = ()
    """Individual answers returned for the latest separate requests."""
    last_request_queries: tuple[AlignedTranscriptionMergeQuery, ...] = ()
    """Exact semantic queries used by the latest separate requests."""
    last_request_spans: tuple[tuple[int, int], ...] = ()
    """Alignment-column spans used by the latest separate requests."""

    def process(
        self,
        sources: Sequence[AlignedTranscriptionMergeSource],
        speaker: str,
        *,
        language_trace: str | None = None,
        music_trace: str | None = None,
        singing_trace: str | None = None,
    ) -> AlignedTranscriptionMergeAnswer:
        """Merge one complete aligned transcription block.

        Arguments:
            sources: named equal-status aligned ASR rows
            speaker: aligned speaker and voice-activity row
            language_trace: optional aligned spoken-language row
            music_trace: optional aligned music row
            singing_trace: optional aligned singing row
        Returns:
            consensus transcript divided into subtitles
        """
        self.last_request_answers = ()
        self.last_request_queries = ()
        self.last_request_spans = ()

        query_cls = self.test_case_cls.query_cls
        validated_query = cast(
            AlignedTranscriptionMergeQuery,
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
            return AlignedTranscriptionMergeAnswer(text="")

        request_queries, self.last_request_spans = _get_request_queries(validated_query)
        self.last_request_queries = request_queries

        request_answers = []
        for query in request_queries:
            test_case = self.test_case_cls(query=query)
            test_case = self.queryer(test_case)
            answer = cast(AlignedTranscriptionMergeAnswer, test_case.answer)
            request_answers.append(answer)

        self.last_request_answers = tuple(request_answers)
        self.save_encountered_test_cases()
        return AlignedTranscriptionMergeAnswer(
            text="".join(answer.text for answer in request_answers)
        )


def _get_query_slice(
    query: AlignedTranscriptionMergeQuery, start: int, end: int
) -> AlignedTranscriptionMergeQuery:
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


def _get_request_queries(
    query: AlignedTranscriptionMergeQuery,
) -> tuple[tuple[AlignedTranscriptionMergeQuery, ...], tuple[tuple[int, int], ...]]:
    """Split a validated alignment query at long shared pause runs."""
    shared_pause_columns = tuple(
        query.speaker[column_idx] == _PAUSE_CHARACTER
        and all(source.text[column_idx] == _PAUSE_CHARACTER for source in query.sources)
        for column_idx in range(len(query.speaker))
    )
    content_spans = get_alignment_content_spans(
        shared_pause_columns, _REQUEST_PAUSE_CHARACTERS
    )

    requests = []
    request_spans = []
    for content_start, content_end in content_spans:
        request = _get_query_slice(query, content_start, content_end)
        if any(
            character != _PAUSE_CHARACTER and not character.isspace()
            for source in request.sources
            for character in source.text
        ):
            requests.append(request)
            request_spans.append((content_start, content_end))
    return tuple(requests), tuple(request_spans)
