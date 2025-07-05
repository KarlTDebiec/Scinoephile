#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runnables related to audio."""

from __future__ import annotations

from langchain_core.runnables import Runnable, RunnableLambda

from scinoephile.audio.runnables.cantonese_distributor import CantoneseDistributor
from scinoephile.audio.runnables.cantonese_merger import CantoneseMerger
from scinoephile.audio.runnables.hanzi_converter import HanziConverter
from scinoephile.audio.runnables.segment_splitter import SegmentSplitter
from scinoephile.audio.runnables.series_compiler import (
    SeriesCompiler,
)
from scinoephile.audio.runnables.sync_grouper import SyncGrouper
from scinoephile.audio.runnables.whisper_transcriber import WhisperTranscriber


def map_field(
    input_field: str,
    runnable: Runnable,
    output_field: str | None = None,
) -> Runnable:
    """Apply a Runnable to value stored under a specified field.

    Arguments:
        input_field: Field from which to load input
        runnable: Runnable to which to apply
        output_field: Field in which to store output (default: input_field)
    """
    if output_field is None:
        output_field = input_field

    def map_and_store(x):
        output = runnable.invoke(x[input_field])
        return {**x, output_field: output}

    return RunnableLambda(map_and_store)


def map_iterable_field(
    input_field: str,
    runnable: Runnable,
    output_field: str | None = None,
    flatten: bool = False,
) -> Runnable:
    """Apply a Runnable to each element in an iterable stored under a specified field.

    Arguments:
        input_field: Field from which to load input
        runnable: Runnable over which to map
        output_field: Field in which to store output (default: input_field)
        flatten: Whether to flatten output
    """
    if output_field is None:
        output_field = input_field

    def map_and_store(x):
        output = runnable.map().invoke(x[input_field])
        if flatten:
            output = [item for sublist in output for item in sublist]
        return {**x, output_field: output}

    return RunnableLambda(map_and_store)


__all__ = [
    "CantoneseMerger",
    "CantoneseDistributor",
    "HanziConverter",
    "SegmentSplitter",
    "SeriesCompiler",
    "SyncGrouper",
    "WhisperTranscriber",
    "map_field",
    "map_iterable_field",
]
