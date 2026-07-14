#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Align a transcription with reference subtitles."""

from __future__ import annotations

from copy import deepcopy
from logging import getLogger
from pathlib import Path
from typing import cast

from pydantic import ValidationError

from scinoephile.audio.subtitles import (
    AudioSeries,
    AudioSubtitle,
    get_series_with_sub_split_at_idx,
    get_sub_merged,
)
from scinoephile.common.validation import val_input_dir_path
from scinoephile.core import ScinoephileError
from scinoephile.core.llms import Queryer
from scinoephile.core.llms.utils import save_test_cases_to_json
from scinoephile.core.ml import get_torch_device
from scinoephile.core.subtitles import Series
from scinoephile.core.synchronization import SyncGroup, get_sync_groups_string
from scinoephile.core.text import remove_punc_and_whitespace
from scinoephile.llms.delineation import (
    DelineationAnswer,
    DelineationManager,
    DelineationPrompt,
    DelineationQuery,
)
from scinoephile.llms.punctuation import PunctuationManager, PunctuationPrompt

from .alignment import TranscriptionAlignment

__all__ = ["TranscriptionAligner"]


logger = getLogger(__name__)


class TranscriptionAligner:
    """Align a transcription with reference subtitles."""

    def __init__(
        self,
        delineation_queryer: Queryer,
        punctuation_queryer: Queryer,
        test_case_dir_path: Path | None = None,
    ):
        """Initialize.

        Arguments:
            delineation_queryer: queryer for delineation
            punctuation_queryer: queryer for punctuation
            test_case_dir_path: directory where encountered test cases are written
        """
        self.delineation_queryer = delineation_queryer
        """Shift transcription text between adjacent reference subtitles."""
        self.punctuation_queryer = punctuation_queryer
        """Punctuate transcription text using corresponding reference subtitles."""
        self.test_case_dir_path = None
        if test_case_dir_path is not None:
            self.test_case_dir_path = val_input_dir_path(test_case_dir_path)

    def align(
        self,
        reference_subs: Series,
        transcription_subs: AudioSeries,
    ) -> TranscriptionAlignment:
        """Align transcribed subtitles with reference subtitles.

        Arguments:
            reference_subs: reference subtitles
            transcription_subs: transcribed subtitles
        Returns:
            aligned transcription and reference subtitles
        """
        alignment = TranscriptionAlignment(reference_subs, transcription_subs)

        delineation_in_progress = True
        while delineation_in_progress:
            delineation_in_progress = self._delineate(alignment)

        self._punctuate(alignment)
        return alignment

    def update_all_test_cases(self):
        """Update all test cases for the specified block."""
        if self.test_case_dir_path is None:
            return

        delineation_output_path = (
            self.test_case_dir_path / "delineation" / f"{get_torch_device()}.json"
        )
        save_test_cases_to_json(
            delineation_output_path,
            list(self.delineation_queryer.encountered_test_cases.values()),
            DelineationManager,
        )
        punctuation_output_path = (
            self.test_case_dir_path / "punctuation" / f"{get_torch_device()}.json"
        )
        save_test_cases_to_json(
            punctuation_output_path,
            list(self.punctuation_queryer.encountered_test_cases.values()),
            PunctuationManager,
        )

    def _delineate(self, alignment: TranscriptionAlignment) -> bool:
        """Delineate transcribed text.

        Arguments:
            alignment: nascent alignment
        Returns:
            whether delineation must restart after splitting a subtitle
        """
        delineation_prompt = cast(DelineationPrompt, self.delineation_queryer.prompt)
        for sync_group_one_idx in range(len(alignment.sync_groups) - 1):
            test_case = alignment.get_delineation_test_case(
                sync_group_one_idx,
                delineation_prompt,
            )
            if test_case is None:
                logger.info(
                    f"Skipping sync groups {sync_group_one_idx} and "
                    f"{sync_group_one_idx + 1} with no transcription"
                )
                continue
            test_case = self.delineation_queryer(test_case)

            query = test_case.query
            answer = test_case.answer
            if answer is None:
                message = "Delineation query returned no answer."
                logger.error(message)
                raise ScinoephileError(message)
            if not answer.output_one and not answer.output_two:
                continue
            if self._delineate_one(
                alignment,
                sync_group_one_idx,
                query,
                answer,
            ):
                return True
        return False

    def _delineate_one(
        self,
        alignment: TranscriptionAlignment,
        sync_group_one_idx: int,
        query: DelineationQuery,
        answer: DelineationAnswer,
    ) -> bool:
        """Delineate text between one sync-group pair.

        Arguments:
            alignment: current alignment being updated
            sync_group_one_idx: index of first sync group in the pair
            query: LLM query payload for the pair
            answer: LLM answer payload for the pair
        Returns:
            whether delineation requires restarting group traversal
        """
        if sync_group_one_idx < 0 or sync_group_one_idx >= len(alignment.sync_groups):
            raise ScinoephileError(
                f"Invalid sync group index {sync_group_one_idx} "
                f"for alignment with {len(alignment.sync_groups)} sync groups."
            )
        sync_group_one = alignment.sync_groups[sync_group_one_idx]

        sync_group_two_idx = sync_group_one_idx + 1
        if sync_group_two_idx >= len(alignment.sync_groups):
            raise ScinoephileError(
                f"Invalid sync group index {sync_group_two_idx} "
                f"for alignment with {len(alignment.sync_groups)} sync groups."
            )
        sync_group_two = alignment.sync_groups[sync_group_two_idx]

        transcription_one_idxs = sync_group_one[1]
        transcription_two_idxs = sync_group_two[1]
        transcription_one = query.target_one
        transcription_two = query.target_two
        shifted_one = answer.output_one
        shifted_two = answer.output_two
        nascent_sync_groups: list[SyncGroup] = deepcopy(alignment.sync_groups)

        if len(transcription_one) < len(shifted_one):
            text_to_shift = shifted_one[len(transcription_one) :]
            remaining_chars = len(text_to_shift)
            for transcription_two_idx in transcription_two_idxs:
                subtitle = alignment.transcription[transcription_two_idx]
                if len(subtitle.text) > remaining_chars:
                    alignment.transcription = get_series_with_sub_split_at_idx(
                        alignment.transcription,
                        transcription_two_idx,
                        remaining_chars,
                    )
                    alignment._sync_groups_override = None
                    return True

                nascent_sync_groups[sync_group_one_idx][1].append(transcription_two_idx)
                nascent_sync_groups[sync_group_two_idx][1].remove(transcription_two_idx)
                remaining_chars -= len(subtitle.text)
                if remaining_chars == 0:
                    alignment._sync_groups_override = nascent_sync_groups
                    return False

        if len(transcription_two) < len(shifted_two):
            text_to_shift = shifted_two[: len(shifted_two) - len(transcription_two)]
            remaining_chars = len(text_to_shift)
            for transcription_one_idx in reversed(transcription_one_idxs):
                subtitle = alignment.transcription[transcription_one_idx]
                if len(subtitle.text) > remaining_chars:
                    alignment.transcription = get_series_with_sub_split_at_idx(
                        alignment.transcription,
                        transcription_one_idx,
                        len(subtitle.text) - remaining_chars,
                    )
                    alignment._sync_groups_override = None
                    return True

                nascent_sync_groups[sync_group_one_idx][1].remove(transcription_one_idx)
                nascent_sync_groups[sync_group_two_idx][1].insert(
                    0, transcription_one_idx
                )
                remaining_chars -= len(subtitle.text)
                if remaining_chars == 0:
                    alignment._sync_groups_override = nascent_sync_groups
                    return False

        raise ScinoephileError(
            f"Unexpected case:\nQuery:\n{query}\n with Answer:\n{answer}\n"
        )

    def _punctuate(self, alignment: TranscriptionAlignment):
        """Punctuate transcribed subtitles.

        Arguments:
            alignment: nascent alignment
        """
        if not alignment.reference_all_assigned_to_sync_groups:
            raise ScinoephileError(
                f"Not all reference subtitles are in a sync group:\n"
                f"SYNC GROUPS:\n{get_sync_groups_string(alignment.sync_groups)}"
            )
        if not alignment.transcription_all_assigned_to_sync_groups:
            raise ScinoephileError(
                f"Not all transcribed subtitles are in a sync group:\n"
                f"SYNC GROUPS:\n{get_sync_groups_string(alignment.sync_groups)}"
            )

        nascent_transcription = AudioSeries(audio=alignment.transcription.audio)
        nascent_sync_groups: list[SyncGroup] = []
        punctuation_prompt = cast(PunctuationPrompt, self.punctuation_queryer.prompt)
        for sync_group_idx, sync_group in enumerate(alignment.sync_groups):
            reference_idx = sync_group[0][0]
            reference = alignment.reference[reference_idx]
            transcription_subtitles: list[AudioSubtitle] = [
                alignment.transcription.events[idx] for idx in sync_group[1]
            ]

            if (
                reference.text == remove_punc_and_whitespace(reference.text)
                and len(transcription_subtitles) == 1
            ):
                subtitle = transcription_subtitles[0]
                subtitle.start = reference.start
                subtitle.end = reference.end
                nascent_transcription.append(subtitle)
                nascent_sync_groups.append(
                    ([reference_idx], [len(nascent_transcription) - 1])
                )
                continue

            test_case = alignment.get_punctuation_test_case(
                sync_group_idx,
                punctuation_prompt,
            )
            if test_case is None:
                logger.info(
                    f"Skipping sync group {sync_group_idx} with no "
                    "transcribed subtitles"
                )
                nascent_sync_groups.append(([reference_idx], []))
                continue
            try:
                test_case = self.punctuation_queryer(test_case)
            except ValidationError as exc:
                logger.error(
                    f"Error punctuating sync group {sync_group_idx}; "
                    f"concatenating.\nTest case:\n{test_case}\nException:\n{exc}"
                )
            punctuated_text = None
            if test_case.answer is not None:
                punctuated_text = test_case.answer.output
            subtitle = get_sub_merged(
                transcription_subtitles,
                text=punctuated_text,
            )
            subtitle.start = reference.start
            subtitle.end = reference.end

            nascent_transcription.append(subtitle)
            transcription_idx = len(nascent_transcription) - 1
            nascent_sync_groups.append(([reference_idx], [transcription_idx]))

        alignment.transcription = nascent_transcription
        alignment._sync_groups_override = nascent_sync_groups
