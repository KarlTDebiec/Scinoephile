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
    AlignedTranscriptionMergeSubtitle,
)
from .prompt import AlignedTranscriptionMergePrompt
from .splitting import get_alignment_content_spans

__all__ = ["AlignedTranscriptionMergeProcessor"]

_PAUSE_CHARACTER = "・"
"""Wide middle dot used for shared timed pauses."""


class AlignedTranscriptionMergeProcessor(Processor):
    """Merge reference-free aligned ASR evidence into consensus subtitles."""

    prompt: AlignedTranscriptionMergePrompt
    """Text for aligned transcription merging."""
    manager_cls = AlignedTranscriptionMergeManager
    """Manager used to construct prompt-specific models."""
    last_request_count: int = 0
    """Number of separate merge requests used by the latest process call."""
    last_request_spans: tuple[tuple[int, int], ...] = ()
    """Alignment-column spans used by the latest separate requests."""
    last_request_answers: tuple[AlignedTranscriptionMergeAnswer, ...] = ()
    """Individual answers returned for the latest separate requests."""

    def process(
        self,
        sources: Sequence[AlignedTranscriptionMergeSource],
        speaker: str,
        *,
        language_trace: str | None = None,
        music_trace: str | None = None,
        request_pause_characters: int = 4,
        singing_trace: str | None = None,
    ) -> AlignedTranscriptionMergeAnswer:
        """Merge one complete aligned transcription block.

        Arguments:
            sources: named equal-status aligned ASR rows
            speaker: aligned speaker and voice-activity row
            language_trace: optional aligned spoken-language row
            music_trace: optional aligned music row
            request_pause_characters: shared consecutive pauses separating requests
            singing_trace: optional aligned singing row
        Returns:
            consensus transcript divided into subtitles
        Raises:
            ValueError: if the request pause threshold is not positive
        """
        if request_pause_characters <= 0:
            raise ValueError("Merge request pause character count must be positive.")
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
        request_queries, self.last_request_spans = _get_request_queries(
            validated_query, request_pause_characters
        )
        self.last_request_count = len(request_queries)

        subtitle_texts = []
        request_answers = []
        for request_query in request_queries:
            query = query_cls.model_validate(
                {
                    "sources": [
                        source.model_dump(mode="json")
                        for source in request_query.sources
                    ],
                    "speaker": request_query.speaker,
                    "language_trace": request_query.language_trace,
                    "singing_trace": request_query.singing_trace,
                    "music_trace": request_query.music_trace,
                }
            )
            test_case = self.test_case_cls(query=query)
            test_case = self.queryer(test_case)
            answer = cast(AlignedTranscriptionMergeAnswer, test_case.answer)
            request_answers.append(answer)
            subtitle_texts.extend(subtitle.text for subtitle in answer.subtitles)

        self.last_request_answers = tuple(request_answers)
        self.save_encountered_test_cases()
        return AlignedTranscriptionMergeAnswer(
            subtitles=[
                AlignedTranscriptionMergeSubtitle(index=index, text=text)
                for index, text in enumerate(subtitle_texts, start=1)
            ]
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
    return AlignedTranscriptionMergeQuery(
        sources=[
            AlignedTranscriptionMergeSource(
                name=source.name, text=source.text[start:end]
            )
            for source in query.sources
        ],
        speaker=query.speaker[start:end],
        language_trace=(
            None if query.language_trace is None else query.language_trace[start:end]
        ),
        singing_trace=(
            None if query.singing_trace is None else query.singing_trace[start:end]
        ),
        music_trace=(
            None if query.music_trace is None else query.music_trace[start:end]
        ),
    )


def _get_request_queries(
    query: AlignedTranscriptionMergeQuery, request_pause_characters: int
) -> tuple[tuple[AlignedTranscriptionMergeQuery, ...], tuple[tuple[int, int], ...]]:
    """Split a validated alignment query at long shared pause runs."""
    shared_pause_columns = tuple(
        query.speaker[column_idx] == _PAUSE_CHARACTER
        and all(source.text[column_idx] == _PAUSE_CHARACTER for source in query.sources)
        for column_idx in range(len(query.speaker))
    )
    content_spans = get_alignment_content_spans(
        shared_pause_columns, request_pause_characters
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
