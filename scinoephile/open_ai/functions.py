#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, create_model

from scinoephile.core import Series
from scinoephile.core.pairs import get_pair_with_zero_start
from scinoephile.open_ai.subtitle_group_response import SubtitleGroupResponse


def get_sync_notes_model(language: str, count: int) -> BaseModel:
    model_name = f"SyncNotes{language.capitalize()}{count}ResponseModel"
    keys = [f"{language}_{i}" for i in range(1, count + 1)]
    fields = {key: (str, ...) for key in keys}
    model = create_model(model_name, **fields)

    return model


def get_sync_overlap_notes(
    hanzi: Series,
    english: Series,
    primary: str,
) -> dict[str, str]:
    """Get notes describing the overlap in timing between two series.

    Arguments:
        hanzi: Hanzi series
        english: English series
        primary: Language to treat as primary
    Returns:
        Dictionary whose keys are the subtitle index in the primary language, and
        whose values are text describing which subtitles each overlaps with in the
        secondary language
    """
    if not (hanzi.events[0].start == 0 or english.events[0].start == 0):
        hanzi, english = get_pair_with_zero_start(hanzi, english)

    primary_series = hanzi if primary == "chinese" else english
    secondary_series = english if primary == "chinese" else hanzi
    primary_label = primary.capitalize()
    secondary_label = "English" if primary == "chinese" else "Chinese"

    notes = {}

    for primary_index, primary_event in enumerate(primary_series.events, 1):
        primary_start, primary_end = primary_event.start, primary_event.end
        primary_duration = primary_end - primary_start

        # Find overlapping secondary subtitles
        overlaps = []
        for secondary_index, secondary_event in enumerate(secondary_series.events, 1):
            secondary_start, secondary_end = secondary_event.start, secondary_event.end

            # Calculate overlap
            overlap_start = max(primary_start, secondary_start)
            overlap_end = min(primary_end, secondary_end)
            overlap_duration = max(0, overlap_end - overlap_start)

            # Calculate percentage of overlap relative to primary subtitle
            if overlap_duration > 0:
                overlap_percentage = (overlap_duration / primary_duration) * 100
                overlaps.append(
                    f"overlaps with {overlap_percentage:.0f}% of "
                    f"{secondary_label} {secondary_index}"
                )

        # Combine overlap descriptions for the primary subtitle
        if overlaps:
            notes[f"{primary}_{primary_index}"] = (
                f"{primary_label} {primary_index} {', '.join(overlaps)}."
            )
        else:
            notes[f"{primary}_{primary_index}"] = (
                f"{primary_label} {primary_index} has no overlapping "
                f"{secondary_label} subtitles."
            )

    return notes


def get_sync_indexes_from_notes(notes: dict[str, str]) -> dict[str, list[int]]:
    if any(key.startswith("english") for key in notes):
        target_language = "Chinese"
    elif any(key.startswith("chinese") for key in notes):
        target_language = "English"
    else:
        raise ValueError("Unknown language prefix in notes keys.")

    pattern = re.compile(rf"{target_language} (\d+)")
    mapping = {}

    for source_key, note in notes.items():
        target_indices = [int(match) for match in pattern.findall(note)]
        mapping[source_key] = sorted(list(set(target_indices)))

    return mapping


def get_sync_groups_from_indexes(mapping: dict[str, list[int]]) -> list[dict[str, Any]]:
    if next(iter(mapping)).startswith("english"):
        source_language = "english"
        target_language = "chinese"
    else:
        source_language = "chinese"
        target_language = "english"

    # Group subtitles by unique sets of indices
    grouped_subtitles = {}
    for source_key, target_indices in mapping.items():
        target_indices_tuple = (
            tuple(sorted(target_indices)) if target_indices else (source_key,)
        )

        source_index = int(source_key.split("_")[1])

        if target_indices_tuple not in grouped_subtitles:
            grouped_subtitles[target_indices_tuple] = {
                source_language: [],
                target_language: list(target_indices) if target_indices else [],
            }

        grouped_subtitles[target_indices_tuple][source_language].append(source_index)

    return [
        {
            source_language: sorted(group[source_language]),
            target_language: sorted(group[target_language]),
        }
        for group in grouped_subtitles.values()
    ]


def get_sync_from_sync_groups(
    groups: list[dict[str, list[int]]],
    primary: str,
    count: int,
) -> list[SubtitleGroupResponse]:
    # Determine the secondary language
    secondary = "chinese" if primary == "english" else "english"

    # Collect all primary language indices that are already grouped
    existing_primary_indexes = {idx for group in groups for idx in group[primary]}

    # Prepare SubtitleGroupResponse objects only for valid groups
    # (where primary language has entries)
    filled_groups = [
        SubtitleGroupResponse(
            **{
                primary: sorted(group[primary]),
                secondary: sorted(group[secondary]),
            }
        )
        for group in groups
        if group[primary]  # Only include if primary language has entries
    ]

    # Insert missing subtitles as single-item groups in primary language
    for idx in range(1, count + 1):
        if idx not in existing_primary_indexes:
            filled_groups.append(
                SubtitleGroupResponse(**{primary: [idx], secondary: []})
            )

    # Sort groups by the first index of the primary language subtitles
    filled_groups.sort(
        key=lambda g: (g.dict()[primary][0] if g.dict()[primary] else float("inf"))
    )

    return filled_groups
