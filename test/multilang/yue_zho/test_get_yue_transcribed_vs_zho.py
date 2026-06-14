#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of get_yue_transcribed_vs_zho."""

from __future__ import annotations

from typing import cast
from unittest.mock import Mock, patch

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.core.subtitles import Series
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.multilang.yue_zho.transcription import (
    YueTranscriber,
    get_yue_transcribed_vs_zho,
)


def test_get_yue_transcribed_vs_zho_dispatches_block_processing():
    """Test transcription entrypoint dispatches block processing."""
    yuewen_audio_series = Mock(spec=AudioSeries)
    zhongwen_series = Mock(spec=Series)
    expected_yuewen_series = Mock(spec=AudioSeries)
    transcriber = _RecordingTranscriber(expected_yuewen_series)

    output_series = get_yue_transcribed_vs_zho(
        yuewen=yuewen_audio_series,
        zhongwen=zhongwen_series,
        transcriber=cast(YueTranscriber, transcriber),
    )

    assert output_series == expected_yuewen_series
    assert transcriber.yuewen is yuewen_audio_series
    assert transcriber.zhongwen is zhongwen_series


def test_get_yue_transcribed_vs_zho_constructs_default_transcriber():
    """Test transcription entrypoint builds a default transcriber when omitted."""
    yuewen_audio_series = Mock(spec=AudioSeries)
    zhongwen_series = Mock(spec=Series)
    expected_yuewen_series = Mock(spec=AudioSeries)
    transcriber = _RecordingTranscriber(expected_yuewen_series)
    factory_convert: list[OpenCCConfig | None] = []

    def get_transcriber(convert: OpenCCConfig | None = None) -> _RecordingTranscriber:
        """Record the requested conversion and return the test transcriber.

        Arguments:
            convert: requested conversion
        Returns:
            recording transcriber
        """
        factory_convert.append(convert)
        return transcriber

    with patch(
        "scinoephile.multilang.yue_zho.transcription.get_yue_vs_zho_transcriber",
        side_effect=get_transcriber,
    ):
        output_series = get_yue_transcribed_vs_zho(
            yuewen=yuewen_audio_series,
            zhongwen=zhongwen_series,
            convert=OpenCCConfig.hk2s,
            stop_at_idx=2,
        )

    assert output_series == expected_yuewen_series
    assert factory_convert == [OpenCCConfig.hk2s]
    assert transcriber.yuewen is yuewen_audio_series
    assert transcriber.zhongwen is zhongwen_series
    assert transcriber.stop_at_idx == 2


class _RecordingTranscriber:
    """Test transcriber that records process_all_blocks inputs."""

    def __init__(self, output_series: AudioSeries):
        """Initialize.

        Arguments:
            output_series: series to return
        """
        self.output_series = output_series
        self.yuewen: AudioSeries | None = None
        self.zhongwen: Series | None = None
        self.stop_at_idx: int | None = None

    def process_all_blocks(
        self,
        yuewen: AudioSeries,
        zhongwen: Series,
        stop_at_idx: int | None = None,
    ) -> AudioSeries:
        """Record inputs and return configured output.

        Arguments:
            yuewen: written Cantonese audio series
            zhongwen: standard Chinese subtitle series
            stop_at_idx: block index at which to stop
        Returns:
            configured output series
        """
        self.yuewen = yuewen
        self.zhongwen = zhongwen
        self.stop_at_idx = stop_at_idx
        return self.output_series
