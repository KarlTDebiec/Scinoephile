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
from scinoephile.core.text import is_low_information_text

from .manager import TranscriptionManager
from .models import (
    TranscriptionAnswer,
    TranscriptionQuery,
    TranscriptionSource,
    TranscriptionTestCase,
)
from .prompt import TranscriptionPrompt

__all__ = ["TranscriptionProcessor", "TranscriptionRequestResult"]

logger = getLogger(__name__)

_REQUEST_PAUSE_CHARACTERS = 4
"""Shared pause columns required to start a separate LLM request."""
_REQUEST_PAUSE_SECONDS = 1.0
"""Continuous shared-pause duration required to start a separate request."""


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
    answer_evidence_column_indexes: tuple[int, ...] = ()
    """Complete-alignment columns corroborating answer characters."""


class TranscriptionProcessor(Processor):
    """Transcribe from reference-free aligned ASR evidence."""

    prompt: TranscriptionPrompt
    """Text for transcription."""
    manager_cls = TranscriptionManager
    """Manager used to construct prompt-specific models."""

    def process(
        self, sources: Sequence[TranscriptionSource], speaker: str
    ) -> TranscriptionAnswer:
        """Transcribe one complete aligned ASR block.

        Arguments:
            sources: named equal-status aligned ASR rows
            speaker: aligned speaker row
        Returns:
            consensus transcript divided into subtitles
        """
        request_results = self.process_requests(sources, speaker)
        return TranscriptionAnswer(
            text="".join(result.answer.text for result in request_results)
        )

    def process_requests(
        self,
        sources: Sequence[TranscriptionSource],
        speaker: str,
        *,
        pause_intervals_seconds: Sequence[tuple[float, float] | None] | None = None,
    ) -> tuple[TranscriptionRequestResult, ...]:
        """Transcribe aligned ASR evidence as separately timed requests.

        Arguments:
            sources: named equal-status aligned ASR rows
            speaker: aligned speaker row
            pause_intervals_seconds: optional interval for each alignment column
        Returns:
            request answers with their complete-alignment column spans
        """
        test_case_cls = cast(type[TranscriptionTestCase], self.test_case_cls)
        query_cls = test_case_cls.query_cls
        validated_query = query_cls.model_validate(
            {
                "sources": [source.model_dump(mode="json") for source in sources],
                "speaker": speaker,
            }
        )
        request_results = []
        for query, (start_column, end_column) in _get_request_queries(
            validated_query, pause_intervals_seconds
        ):
            if _get_usable_source_count(query) < 2:
                request_results.append(
                    TranscriptionRequestResult(
                        start_column,
                        end_column,
                        TranscriptionAnswer(text=""),
                        query.key_sha256,
                    )
                )
                logger.info(
                    "Omitted transcription request at alignment columns "
                    f"{start_column}-{end_column}: fewer than two sources contain "
                    "usable text."
                )
                continue
            if _contains_only_low_information_text(query):
                request_results.append(
                    TranscriptionRequestResult(
                        start_column,
                        end_column,
                        TranscriptionAnswer(text=""),
                        query.key_sha256,
                    )
                )
                logger.info(
                    "Omitted transcription request at alignment columns "
                    f"{start_column}-{end_column}: sources contain only "
                    "low-information vocalizations."
                )
                continue
            test_case = test_case_cls(query=query)
            try:
                test_case = self.queryer(test_case)
            except ValidationError:
                answer = cast(TranscriptionAnswer, test_case.get_no_op_answer())
                try:
                    test_case = test_case_cls.model_validate(
                        {
                            **test_case.model_dump(mode="json"),
                            "answer": answer.model_dump(mode="json"),
                            "few_shot": False,
                            "verified": False,
                        }
                    )
                except ValidationError:
                    logger.warning(
                        "Deterministic column consensus could not satisfy strict "
                        "transcription validation; returning its conservative "
                        "cross-source consensus without storing it as a test case."
                    )
                else:
                    test_case = self.queryer.store_answered_test_case(test_case)
                logger.warning(
                    "LLM exhausted valid transcription answers; used deterministic "
                    f"column consensus: {answer.text!r}"
                )
            else:
                answer = cast(TranscriptionAnswer, test_case.answer)
            if is_low_information_text(answer.transcript):
                logger.info(
                    "Omitted transcription request at alignment columns "
                    f"{start_column}-{end_column}: consensus contains only "
                    "low-information vocalizations."
                )
                answer = TranscriptionAnswer(text="")
            validation = test_case_cls.alignment_scorer.score(
                tuple(source.text for source in query.sources), answer.transcript
            )
            answer_evidence_column_indexes = tuple(
                start_column + column_idx
                for column_idx in validation.answer_evidence_column_indexes
            )
            request_results.append(
                TranscriptionRequestResult(
                    start_column,
                    end_column,
                    answer,
                    query.key_sha256,
                    answer_evidence_column_indexes,
                )
            )

        self.save_encountered_test_cases()
        return tuple(request_results)


def _get_flat_content_spans(
    rows: tuple[str, ...], width: int
) -> tuple[tuple[int, int], ...]:
    """Get content spans separated by long rendered pause runs.

    Arguments:
        rows: equal-width source and annotation rows
        width: alignment column count
    Returns:
        content spans between long shared pause runs
    """
    content_spans = []
    content_start = 0
    pause_start: int | None = None
    for column_idx in range(width + 1):
        is_shared_pause = column_idx < width and all(
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
    if content_start < width:
        content_spans.append((content_start, width))
    return tuple(content_spans)


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
    return query.model_copy(update=update)


def _get_request_queries(
    query: TranscriptionQuery,
    pause_intervals_seconds: Sequence[tuple[float, float] | None] | None = None,
) -> tuple[tuple[TranscriptionQuery, tuple[int, int]], ...]:
    """Split a validated alignment query at long continuous shared pauses.

    Arguments:
        query: validated complete-block alignment query
        pause_intervals_seconds: optional interval for each alignment column
    Returns:
        request queries and their complete-alignment column spans
    Raises:
        ValueError: if structured pause intervals do not match the query
    """
    rows = (query.speaker, *(source.text for source in query.sources))
    if pause_intervals_seconds is None:
        content_spans = _get_flat_content_spans(rows, len(query.speaker))
    else:
        content_spans = _get_timed_content_spans(
            rows, pause_intervals_seconds, len(query.speaker)
        )

    requests = []
    for content_start, content_end in content_spans:
        request = _get_query_slice(query, content_start, content_end)
        if any(_has_usable_content(source.text) for source in request.sources):
            requests.append((request, (content_start, content_end)))
    return tuple(requests)


def _get_timed_content_spans(
    rows: tuple[str, ...],
    pause_intervals_seconds: Sequence[tuple[float, float] | None],
    width: int,
) -> tuple[tuple[int, int], ...]:
    """Get content spans separated by long continuous timed pauses.

    Arguments:
        rows: equal-width source and annotation rows
        pause_intervals_seconds: interval for each alignment column
        width: alignment column count
    Returns:
        content spans between long continuous shared pauses
    Raises:
        ValueError: if structured pause intervals do not match the rows
    """
    if len(pause_intervals_seconds) != width:
        raise ValueError(
            "Timed pause intervals must match the transcription alignment width."
        )

    content_spans = []
    content_start = 0
    pause_start: int | None = None
    pause_interval_start: float | None = None
    pause_interval_end: float | None = None
    for column_idx in range(width + 1):
        pause_interval = None
        if column_idx < width:
            pause_interval = pause_intervals_seconds[column_idx]
        if pause_interval is not None:
            if not all(row[column_idx] == "・" for row in rows):
                raise ValueError(
                    "Timed pause intervals require shared transcription pause columns."
                )
            if (
                pause_start is not None
                and pause_interval_end is not None
                and abs(pause_interval[0] - pause_interval_end) <= 1e-9
            ):
                pause_interval_end = pause_interval[1]
                continue
        if pause_start is not None:
            if (
                pause_interval_start is not None
                and pause_interval_end is not None
                and pause_interval_end - pause_interval_start >= _REQUEST_PAUSE_SECONDS
            ):
                if content_start < pause_start:
                    content_spans.append((content_start, pause_start))
                content_start = column_idx
            pause_start = None
            pause_interval_start = None
            pause_interval_end = None
        if pause_interval is not None:
            pause_start = column_idx
            pause_interval_start, pause_interval_end = pause_interval
    if content_start < width:
        content_spans.append((content_start, width))
    return tuple(content_spans)


def _get_usable_source_count(query: TranscriptionQuery) -> int:
    """Count sources containing usable content in one request.

    Arguments:
        query: one pause-delimited transcription query
    Returns:
        number of sources containing nonblank, non-pause text
    """
    return sum(_has_usable_content(source.text) for source in query.sources)


def _contains_only_low_information_text(query: TranscriptionQuery) -> bool:
    """Check whether every usable source contains only vocalizations.

    Arguments:
        query: one pause-delimited transcription query
    Returns:
        whether all usable source text is low-information
    """
    usable_texts = [
        source.text for source in query.sources if _has_usable_content(source.text)
    ]
    return bool(usable_texts) and all(
        is_low_information_text(text) for text in usable_texts
    )


def _has_usable_content(text: str) -> bool:
    """Check whether aligned text contains usable content.

    Arguments:
        text: aligned transcription text
    Returns:
        whether the text contains nonblank, non-pause content
    """
    return any(character != "・" and not character.isspace() for character in text)
