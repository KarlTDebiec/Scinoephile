#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, create_model

from scinoephile.open_ai.subtitle_group_response import SubtitleGroupResponse


def get_sync_notes_response_model(language: str, count: int) -> BaseModel:
    model_name = f"SyncNotes{language.capitalize()}{count}ResponseModel"
    keys = [f"{language}_{i}" for i in range(1, count + 1)]
    fields = {key: (str, ...) for key in keys}
    model = create_model(model_name, **fields)

    return model


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

    # Prepare SubtitleGroupResponse objects only for valid groups (where primary language has entries)
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
