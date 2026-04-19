#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Cantonese transcription tooling for 粤文/中文 workflows."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.common.file import get_temp_file_path
from scinoephile.core.llms import TestCase
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series
from scinoephile.llms.default_test_cases import (
    YUE_ZHO_TRANSCRIPTION_MERGING_JSON_PATHS,
    YUE_ZHO_TRANSCRIPTION_SHIFTING_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.dual_pair import DualPairManager
from scinoephile.multilang.yue_zho.transcription.merging import (
    YueZhoHansMergingPrompt,
    YueZhoMergingManager,
)
from scinoephile.multilang.yue_zho.transcription.shifting import (
    YueZhoHansShiftingPrompt,
)

from .transcriber import YueTranscriber

__all__ = [
    "YueTranscriber",
    "YueZhoTranscriberKwargs",
    "YueZhoTranscriptionKwargs",
    "get_yue_transcribed_vs_zho",
    "get_yue_transcriber_vs_zho",
]


class YueZhoTranscriptionKwargs(TypedDict, total=False):
    """Keyword arguments for get_yue_transcribed_vs_zho forwarding."""

    stop_at_idx: int | None
    """block index at which to stop processing, inclusive."""


class YueZhoTranscriberKwargs(TypedDict, total=False):
    """Keyword arguments for default YueTranscriber construction."""

    test_case_directory_path: Path | None
    """directory where encountered transcription test cases are persisted."""
    shifting_test_cases: list[TestCase] | None
    """preloaded shifting test cases used to seed the transcriber."""
    merging_test_cases: list[TestCase] | None
    """preloaded merging test cases used to seed the transcriber."""


def get_yue_transcriber_vs_zho(
    shifting_test_cases: list[TestCase] | None = None,
    merging_test_cases: list[TestCase] | None = None,
    test_case_directory_path: Path | None = None,
) -> YueTranscriber:
    """Get YueTranscriber with default resources when available.

    Arguments:
        shifting_test_cases: optional shifting test cases
        merging_test_cases: optional merging test cases
        test_case_directory_path: optional directory where test cases are updated
    Returns:
        configured YueTranscriber
    """
    if shifting_test_cases is None:
        shifting_test_cases = list(
            load_default_test_cases(
                DualPairManager,
                YueZhoHansShiftingPrompt,
                YUE_ZHO_TRANSCRIPTION_SHIFTING_JSON_PATHS,
            )
        )
    if merging_test_cases is None:
        merging_test_cases = list(
            load_default_test_cases(
                YueZhoMergingManager,
                YueZhoHansMergingPrompt,
                YUE_ZHO_TRANSCRIPTION_MERGING_JSON_PATHS,
            )
        )
    if test_case_directory_path is None:
        test_case_directory_path = _get_default_test_case_dir_path()
    return YueTranscriber(
        test_case_directory_path=test_case_directory_path,
        shifting_test_cases=shifting_test_cases,
        merging_test_cases=merging_test_cases,
    )


def get_yue_transcribed_vs_zho(
    zhongwen: Series,
    media_path: Path | str,
    stream_index: int = 0,
    transcriber: YueTranscriber | None = None,
    **kwargs: Unpack[YueZhoTranscriptionKwargs],
) -> AudioSeries:
    """Get initial 粤文 transcription aligned to 中文字幕.

    Arguments:
        zhongwen: 中文字幕 subtitle series
        media_path: path to video container or audio media file
        stream_index: audio stream index (zero-based)
        transcriber: transcriber to use
        **kwargs: additional keyword arguments for YueTranscriber.process_all_blocks
    Returns:
        transcribed 粤文 subtitle series
    """
    with get_temp_file_path(".srt") as subtitle_path:
        zhongwen.save(subtitle_path, format_="srt")
        yuewen = AudioSeries.load_from_media(
            media_path=media_path,
            subtitle_path=subtitle_path,
            stream_index=stream_index,
        )
    if transcriber is None:
        transcriber = get_yue_transcriber_vs_zho()
    return transcriber.process_all_blocks(yuewen, zhongwen, **kwargs)


def _get_default_test_case_dir_path() -> Path:
    """Get the default writable test-case directory for transcription updates.

    Returns:
        writable runtime test-case root with transcription subdirectories present
    """
    test_case_dir_path = get_runtime_cache_dir_path("test_cases")
    (test_case_dir_path / "multilang" / "yue_zho" / "transcription" / "shifting").mkdir(
        parents=True, exist_ok=True
    )
    (test_case_dir_path / "multilang" / "yue_zho" / "transcription" / "merging").mkdir(
        parents=True, exist_ok=True
    )
    return test_case_dir_path
