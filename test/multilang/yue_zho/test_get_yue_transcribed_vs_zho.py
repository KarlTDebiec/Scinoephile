#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of get_yue_transcribed_vs_zho."""

from __future__ import annotations

from unittest.mock import Mock

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.core.subtitles import Series
from scinoephile.multilang.yue_zho.transcription import get_yue_transcribed_vs_zho


def test_get_yue_transcribed_vs_zho_dispatches_block_processing():
    """Test transcription entrypoint dispatches block processing."""
    yuewen_audio_series = Mock(spec=AudioSeries)
    zhongwen_series = Mock(spec=Series)
    expected_yuewen_series = Mock(spec=AudioSeries)
    transcriber = Mock()
    transcriber.process_all_blocks.return_value = expected_yuewen_series

    output_series = get_yue_transcribed_vs_zho(
        yuewen=yuewen_audio_series,
        zhongwen=zhongwen_series,
        transcriber=transcriber,
    )

    assert output_series == expected_yuewen_series
    transcriber.process_all_blocks.assert_called_once_with(
        yuewen_audio_series, zhongwen_series
    )
