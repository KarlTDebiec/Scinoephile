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
from .models import TranscriptionAnswer, TranscriptionSource, TranscriptionTestCase
from .prompt import TranscriptionPrompt
from .request_partitioning import partition_transcription_query

__all__ = ["TranscriptionProcessor", "TranscriptionRequestResult"]

logger = getLogger(__name__)


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
    answer_character_evidence_column_indexes: tuple[int | None, ...] = ()
    """Corroborating complete-alignment column for each lexical answer character."""

    @property
    def answer_evidence_column_indexes(self) -> tuple[int, ...]:
        """Get complete-alignment columns corroborating lexical answer characters."""
        return tuple(
            column_idx
            for column_idx in self.answer_character_evidence_column_indexes
            if column_idx is not None
        )


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
        for query, (start_column, end_column) in partition_transcription_query(
            validated_query, pause_intervals_seconds
        ):
            omission_reason = None
            usable_texts = [
                source.text
                for source in query.sources
                if any(
                    character != "・" and not character.isspace()
                    for character in source.text
                )
            ]
            if len(usable_texts) < 2:
                omission_reason = "fewer than two sources contain usable text"
            elif all(is_low_information_text(text) for text in usable_texts):
                omission_reason = "sources contain only low-information vocalizations"
            if omission_reason is not None:
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
                    f"{start_column}-{end_column}: {omission_reason}."
                )
                continue
            test_case = test_case_cls(query=query)
            try:
                test_case = self.queryer(test_case)
            except ValidationError:
                answer = test_case.get_no_op_answer()
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
            answer_character_evidence_column_indexes: list[int | None] = []
            for column_idx in validation.answer_character_evidence_column_indexes:
                if column_idx is None:
                    answer_character_evidence_column_indexes.append(None)
                else:
                    answer_character_evidence_column_indexes.append(
                        start_column + column_idx
                    )
            request_results.append(
                TranscriptionRequestResult(
                    start_column,
                    end_column,
                    answer,
                    query.key_sha256,
                    tuple(answer_character_evidence_column_indexes),
                )
            )

        self.save_encountered_test_cases()
        return tuple(request_results)
