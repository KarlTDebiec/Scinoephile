#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Align and punctuate a complete transcription block using sparse LLM changes."""

from __future__ import annotations

from collections.abc import Sequence
from logging import getLogger
from typing import cast

from pydantic import ValidationError

from scinoephile.audio.subtitles import AudioSeries, AudioSubtitle
from scinoephile.core.llms import Processor, TestCase, TestCaseSubtitle
from scinoephile.core.subtitles import Series
from scinoephile.core.synchronization import SyncGroup
from scinoephile.core.text import replace_control_characters
from scinoephile.llms.block_delineation import (
    BlockDelineationAnswer,
    BlockDelineationProcessor,
    BlockDelineationTestCase,
)
from scinoephile.llms.block_punctuation import (
    BlockPunctuationAnswer,
    BlockPunctuationProcessor,
    BlockPunctuationTestCase,
)

from .alignment import TranscriptionAlignment

__all__ = ["BlockTranscriptionAligner"]


logger = getLogger(__name__)


class BlockTranscriptionAligner:
    """Align and punctuate a transcription using two queries per populated block."""

    def __init__(
        self,
        delineation_processor: BlockDelineationProcessor,
        punctuation_processor: BlockPunctuationProcessor,
        *,
        fallback_to_no_op: bool = False,
    ):
        """Initialize.

        Arguments:
            delineation_processor: processor for block delineation queries
            punctuation_processor: processor for block punctuation queries
            fallback_to_no_op: whether invalid answers fall back to sparse no-op
        """
        self.delineation_processor = delineation_processor
        """Redistribute target characters across all guide indexes in one query."""
        self.punctuation_processor = punctuation_processor
        """Punctuate all delineated target subtitles in one query."""
        self.fallback_to_no_op = fallback_to_no_op
        """Whether exhausted invalid answers fall back to sparse no-op answers."""

    def align(
        self, reference_subs: Series, transcription_subs: AudioSeries
    ) -> TranscriptionAlignment:
        """Align and punctuate one complete transcription block.

        Arguments:
            reference_subs: guide subtitles for one block
            transcription_subs: raw timestamped transcription for the block
        Returns:
            guide-aligned sparse transcription
        """
        alignment = TranscriptionAlignment(reference_subs, transcription_subs)
        targets = [
            "".join(
                alignment.transcription[transcription_idx].text
                for transcription_idx in transcription_idxs
            )
            for _, transcription_idxs in alignment.sync_groups
        ]
        if not any(targets):
            self._set_output(alignment, targets)
            return alignment

        guides = [subtitle.text for subtitle in alignment.reference]
        delineated = targets
        if len(guides) > 1:
            delineated = self._delineate(guides, targets)
        punctuated = self._punctuate(guides, delineated)
        self._set_output(alignment, punctuated)
        return alignment

    def update_all_test_cases(self):
        """Persist block test cases encountered during the current run."""
        self.delineation_processor.save_test_cases()
        self.punctuation_processor.save_test_cases()

    def _delineate(self, guides: list[str], targets: list[str]) -> list[str]:
        """Delineate one complete block using sparse replacements.

        Arguments:
            guides: complete guide text by index
            targets: timing-based initial target assignment by index
        Returns:
            delineated target text by index
        """
        test_case_cls = self.delineation_processor.test_case_cls
        query = test_case_cls.query_cls.model_validate(
            {
                "guides": self._get_indexed_items(guides),
                "targets": self._get_indexed_items(targets),
            }
        )
        test_case = test_case_cls(query=query)
        test_case = cast(
            BlockDelineationTestCase,
            self._query_with_fallback(
                self.delineation_processor, test_case, "block delineation"
            ),
        )
        answer = cast(BlockDelineationAnswer, test_case.answer)
        return self._apply_changes(targets, answer.changes)

    def _punctuate(self, guides: list[str], targets: list[str]) -> list[str]:
        """Punctuate one complete block using sparse replacements.

        Arguments:
            guides: complete guide text by index
            targets: delineated target text by index
        Returns:
            punctuated target text by index
        """
        test_case_cls = self.punctuation_processor.test_case_cls
        query = test_case_cls.query_cls.model_validate(
            {
                "guides": self._get_indexed_items(guides),
                "targets": self._get_indexed_items(targets),
            }
        )
        test_case = test_case_cls(query=query)
        test_case = cast(
            BlockPunctuationTestCase,
            self._query_with_fallback(
                self.punctuation_processor, test_case, "block punctuation"
            ),
        )
        answer = cast(BlockPunctuationAnswer, test_case.answer)
        return self._apply_changes(targets, answer.changes)

    def _query_with_fallback(
        self, processor: Processor, test_case: TestCase, operation: str
    ) -> TestCase:
        """Query an operation and optionally persist a no-op after invalid answers.

        Arguments:
            processor: processor whose queryer should execute the test case
            test_case: unanswered block test case
            operation: human-readable operation name for logging
        Returns:
            answered LLM or no-op test case
        Raises:
            ValidationError: if answers remain invalid and fallback is disabled
        """
        try:
            return processor.queryer(test_case)
        except ValidationError as exc:
            if not self.fallback_to_no_op:
                raise

            fallback_test_case = type(test_case).model_validate(
                {
                    **test_case.model_dump(mode="json"),
                    "answer": test_case.get_no_op_answer().model_dump(mode="json"),
                    "few_shot": False,
                    "verified": False,
                }
            )
            processor.queryer.log_encountered_test_case(fallback_test_case)
            logger.warning(
                f"Falling back to an unverified no-op answer for {operation} after "
                f"invalid LLM responses: {exc}"
            )
            return fallback_test_case

    def _set_output(
        self, alignment: TranscriptionAlignment, output_texts: Sequence[str]
    ):
        """Replace alignment transcription with sparse guide-timed output.

        Arguments:
            alignment: alignment to update
            output_texts: complete output text by guide index
        """
        events: list[AudioSubtitle] = []
        sync_groups: list[SyncGroup] = []
        for reference_idx, (reference, output_text) in enumerate(
            zip(alignment.reference, output_texts, strict=True)
        ):
            normalized_output_text = replace_control_characters(output_text)
            if not normalized_output_text:
                sync_groups.append(([reference_idx], []))
                continue
            output_idx = len(events)
            events.append(
                AudioSubtitle(
                    start=reference.start,
                    end=reference.end,
                    text=normalized_output_text,
                )
            )
            sync_groups.append(([reference_idx], [output_idx]))

        alignment.transcription = AudioSeries(
            audio=alignment.transcription.audio, events=events
        )
        alignment._sync_groups_override = sync_groups

    @staticmethod
    def _apply_changes(
        targets: list[str], changes: Sequence[TestCaseSubtitle]
    ) -> list[str]:
        """Overlay sparse indexed changes onto complete target text.

        Arguments:
            targets: complete target text by guide index
            changes: sparse one-based target replacements
        Returns:
            complete target text with replacements applied
        """
        output = list(targets)
        for change in changes:
            output[change.index - 1] = change.text
        return output

    @staticmethod
    def _get_indexed_items(texts: Sequence[str]) -> list[dict[str, int | str]]:
        """Get one-based indexed text mappings.

        Arguments:
            texts: complete text sequence
        Returns:
            indexed mappings accepted by block query models
        """
        return [{"index": index, "text": text} for index, text in enumerate(texts, 1)]
