#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runnable for getting sync groups between source and transcribed series."""

from __future__ import annotations

from pprint import pformat
from typing import Any

from langchain_core.runnables import Runnable, RunnableConfig

from scinoephile.audio.models import TranscriptionPayload
from scinoephile.core.pairs import get_pair_strings
from scinoephile.core.synchronization import (
    get_overlap_string,
    get_sync_groups,
    get_sync_overlap_matrix,
)


class SyncGrouper(Runnable):
    """Runnable for getting sync groups between source and transcribed series."""

    def invoke(
        self,
        input: TranscriptionPayload,
        config: RunnableConfig | None = None,
        **kwargs: Any,
    ) -> TranscriptionPayload:
        source = input["source"]
        series = input["series"]

        source_str, transcribed_str = get_pair_strings(source, series)
        print(f"\nMANDARIN:\n{source_str}")
        print(f"\nCANTONESE:\n{transcribed_str}")

        overlap = get_sync_overlap_matrix(source, series)
        print("\nOVERLAP:")
        print(get_overlap_string(overlap))

        sync_groups = get_sync_groups(source, series)
        print(f"\nSYNC GROUPS:\n{pformat(sync_groups, width=120)}")

        return TranscriptionPayload(
            source=source,
            segments=input["segments"],
            series=series,
            sync_groups=sync_groups,
        )
