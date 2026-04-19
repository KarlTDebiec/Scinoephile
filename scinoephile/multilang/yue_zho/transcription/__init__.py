#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Cantonese transcription tooling for 粤文/中文 workflows."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack
from warnings import catch_warnings, filterwarnings

import ffmpeg

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.common.file import get_temp_directory_path
from scinoephile.common.validation import val_input_path
from scinoephile.core import ScinoephileError
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

with catch_warnings():
    filterwarnings("ignore", category=SyntaxWarning)
    filterwarnings("ignore", category=RuntimeWarning)
    from pydub import AudioSegment

from .transcriber import YueTranscriber

__all__ = [
    "YueTranscriber",
    "YueZhoTranscriberKwargs",
    "YueZhoTranscriptionKwargs",
    "get_yue_audio_series_for_transcription",
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


def get_yue_audio_series_for_transcription(
    zhongwen: Series,
    media_path: Path | str,
    stream_index: int = 0,
    buffer: int = 1000,
) -> AudioSeries:
    """Get an AudioSeries for transcription from subtitles and media input.

    Arguments:
        zhongwen: 中文字幕 subtitles with timing data
        media_path: path to video container or audio media file
        stream_index: audio stream index (zero-based)
        buffer: additional buffer to include before and after subtitles (ms)
    Returns:
        AudioSeries aligned to 中文字幕 timings
    """
    validated_media_path = val_input_path(media_path)

    try:
        probe = ffmpeg.probe(str(validated_media_path))
    except ffmpeg.Error as exc:
        raise ScinoephileError(
            f"Could not probe media file {validated_media_path}"
        ) from exc
    streams = probe.get("streams", [])
    audio_streams = [
        stream for stream in streams if stream.get("codec_type") == "audio"
    ]
    if not audio_streams:
        raise ScinoephileError(
            f"No audio streams found in media file {validated_media_path}"
        )
    if stream_index < 0 or stream_index >= len(audio_streams):
        raise ScinoephileError(
            f"Invalid audio stream index {stream_index} for {validated_media_path}; "
            f"found {len(audio_streams)} audio stream(s)."
        )

    stream = audio_streams[stream_index]
    channels = stream.get("channels")
    try:
        channel_count = int(channels)
    except (TypeError, ValueError) as exc:
        raise ScinoephileError(
            f"Audio stream {stream_index} in {validated_media_path} "
            "cannot be used for transcription."
        ) from exc

    with get_temp_directory_path() as temp_dir_path:
        audio_output_path = temp_dir_path / "full_audio.wav"
        try:
            AudioSeries.extract_audio_track(
                validated_media_path, audio_output_path, stream_index, channel_count
            )
            full_audio = AudioSegment.from_wav(audio_output_path)
        except ffmpeg.Error as exc:
            raise ScinoephileError(
                "Could not extract audio stream "
                f"{stream_index} from {validated_media_path}"
            ) from exc

    return AudioSeries.build_series(zhongwen, full_audio, buffer)


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
    yuewen = get_yue_audio_series_for_transcription(
        zhongwen=zhongwen,
        media_path=media_path,
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
