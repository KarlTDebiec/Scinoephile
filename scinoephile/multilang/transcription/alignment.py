#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Nascent alignment between a transcription and reference subtitles."""

from __future__ import annotations

from pprint import pformat
from typing import cast

import numpy as np

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.core import ScinoephileError
from scinoephile.core.pairs import get_pair_strings
from scinoephile.core.subtitles import Series
from scinoephile.core.synchronization import (
    SyncGroup,
    get_overlap_string,
    get_sync_groups_string,
    get_sync_overlap_matrix,
)
from scinoephile.llms.delineation import (
    DelineationManager,
    DelineationPrompt,
    DelineationTestCase,
)
from scinoephile.llms.punctuation import (
    PunctuationManager,
    PunctuationPrompt,
    PunctuationTestCase,
)

__all__ = ["TranscriptionAlignment"]


class TranscriptionAlignment:
    """Nascent alignment between a transcription and reference subtitles."""

    def __init__(self, reference: Series, transcription: AudioSeries):
        """Initialize.

        Arguments:
            reference: reference subtitles
            transcription: transcribed subtitles
        """
        self._reference = reference
        self._transcription = transcription
        self._sync_groups_override: list[SyncGroup] | None = None

    def __str__(self) -> str:
        """Get string representation.

        Returns:
            string representation
        """
        reference_string, transcription_string = get_pair_strings(
            self.reference, self.transcription
        )
        string = f"REFERENCE:\n{reference_string}"
        string += f"\nTRANSCRIPTION:\n{transcription_string}"
        string += f"\nOVERLAP:\n{get_overlap_string(self.overlap)}"
        if self._sync_groups_override is not None:
            string += "\nSYNC GROUPS (OVERRIDDEN):"
        else:
            string += "\nSYNC GROUPS:"
        string += f"\n{get_sync_groups_string(self.sync_groups)}"
        string += (
            f"\nTO DISTRIBUTE:\n"
            f"{pformat([idx + 1 for idx in self.transcription_to_distribute])}"
        )
        return string

    @property
    def overlap(self) -> np.ndarray:
        """Overlap matrix between reference and transcribed subtitles."""
        return get_sync_overlap_matrix(self.reference, self.transcription)

    @property
    def reference(self) -> Series:
        """Reference subtitle series."""
        return self._reference

    @reference.setter
    def reference(self, value: Series):
        """Set reference subtitle series.

        Arguments:
            value: reference subtitle series
        """
        self._reference = value

    @property
    def reference_all_assigned_to_sync_groups(self) -> bool:
        """Whether all reference subtitles are assigned to sync groups."""
        reference_idxs = {
            reference_idx
            for sync_group in self.sync_groups
            for reference_idx in sync_group[0]
        }
        return reference_idxs == set(range(len(self.reference)))

    @property
    def sync_groups(self) -> list[SyncGroup]:
        """Sync groups between reference and transcribed subtitles."""
        if self._sync_groups_override is not None:
            return self._sync_groups_override

        nascent_sync_groups: list[SyncGroup] = [
            ([idx], []) for idx in range(len(self.reference))
        ]
        overlap = self.overlap
        for transcription_idx in range(len(self.transcription)):
            sync_group_idx = int(np.argmax(overlap[:, transcription_idx]))
            nascent_sync_groups[sync_group_idx][1].append(transcription_idx)
        return nascent_sync_groups

    @property
    def transcription(self) -> AudioSeries:
        """Transcribed subtitle series."""
        return self._transcription

    @transcription.setter
    def transcription(self, value: AudioSeries):
        """Set transcribed subtitle series.

        Arguments:
            value: transcribed subtitle series
        """
        self._transcription = value

    @property
    def transcription_all_assigned_to_sync_groups(self) -> bool:
        """Whether all transcribed subtitles are assigned to sync groups."""
        transcription_idxs = {
            transcription_idx
            for sync_group in self.sync_groups
            for transcription_idx in sync_group[1]
        }
        return transcription_idxs == set(range(len(self.transcription)))

    @property
    def transcription_to_distribute(self) -> list[int]:
        """Transcription indices in need of distribution."""
        transcription_idxs = {
            transcription_idx
            for sync_group in self.sync_groups
            for transcription_idx in sync_group[1]
        }
        return sorted(set(range(len(self.transcription))) - transcription_idxs)

    def get_delineation_test_case(
        self,
        sync_group_one_idx: int,
        prompt: DelineationPrompt,
    ) -> DelineationTestCase | None:
        """Get a delineation test case for adjacent sync groups.

        Arguments:
            sync_group_one_idx: index of first sync group
            prompt: text and field aliases for LLM correspondence
        Returns:
            test case, or None if there are no transcribed subtitles to shift
        """
        if sync_group_one_idx < 0 or sync_group_one_idx >= len(self.sync_groups):
            raise ScinoephileError(
                f"Invalid sync group index {sync_group_one_idx} "
                f"for alignment with {len(self.sync_groups)} sync groups."
            )
        sync_group_one = self.sync_groups[sync_group_one_idx]

        sync_group_two_idx = sync_group_one_idx + 1
        if sync_group_two_idx >= len(self.sync_groups):
            raise ScinoephileError(
                f"Invalid sync group index {sync_group_two_idx} "
                f"for alignment with {len(self.sync_groups)} sync groups."
            )
        sync_group_two = self.sync_groups[sync_group_two_idx]

        reference_one_idxs = sync_group_one[0]
        if len(reference_one_idxs) != 1:
            raise ScinoephileError(
                f"Sync group {sync_group_one_idx} has {len(reference_one_idxs)} "
                "reference subtitles, expected 1."
            )
        reference_one_idx = reference_one_idxs[0]
        reference_one = self.reference[reference_one_idx].text

        reference_two_idxs = sync_group_two[0]
        if len(reference_two_idxs) != 1:
            raise ScinoephileError(
                f"Sync group {sync_group_two_idx} has {len(reference_two_idxs)} "
                "reference subtitles, expected 1."
            )
        reference_two_idx = reference_two_idxs[0]
        if reference_one_idx + 1 != reference_two_idx:
            raise ScinoephileError(
                f"Reference indexes {reference_one_idx} and {reference_two_idx} "
                "are not consecutive."
            )
        reference_two = self.reference[reference_two_idx].text

        transcription_one = "".join(
            self.transcription[idx].text for idx in sync_group_one[1]
        )
        transcription_two = "".join(
            self.transcription[idx].text for idx in sync_group_two[1]
        )
        if not transcription_one and not transcription_two:
            return None

        test_case_cls = DelineationManager.get_test_case_cls(prompt=prompt)
        query = test_case_cls.query_cls.model_validate(
            {
                "reference_one": reference_one,
                "reference_two": reference_two,
                "target_one": transcription_one,
                "target_two": transcription_two,
            }
        )
        return cast(DelineationTestCase, test_case_cls(query=query))

    def get_punctuation_test_case(
        self,
        sync_group_idx: int,
        prompt: PunctuationPrompt,
    ) -> PunctuationTestCase | None:
        """Get a punctuation test case for a sync group.

        Arguments:
            sync_group_idx: index of sync group
            prompt: text and field aliases for LLM correspondence
        Returns:
            test case, or None if there are no transcribed subtitles to punctuate
        """
        if sync_group_idx < 0 or sync_group_idx >= len(self.sync_groups):
            raise ScinoephileError(
                f"Invalid sync group index {sync_group_idx} "
                f"for alignment with {len(self.sync_groups)} sync groups."
            )
        sync_group = self.sync_groups[sync_group_idx]

        reference_idxs = sync_group[0]
        if len(reference_idxs) != 1:
            raise ScinoephileError(
                f"Sync group {sync_group_idx} has {len(reference_idxs)} "
                "reference subtitles, expected 1."
            )
        reference = self.reference[reference_idxs[0]].text

        transcription_idxs = sync_group[1]
        if not transcription_idxs:
            return None
        transcriptions = [self.transcription[idx].text for idx in transcription_idxs]

        test_case_cls = PunctuationManager.get_test_case_cls(prompt=prompt)
        query = test_case_cls.query_cls.model_validate(
            {
                "subtitles": transcriptions,
                "guide": reference,
            }
        )
        return cast(PunctuationTestCase, test_case_cls(query=query))
