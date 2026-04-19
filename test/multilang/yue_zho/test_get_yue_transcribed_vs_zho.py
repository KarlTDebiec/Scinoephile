#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of get_yue_transcribed_vs_zho."""

from __future__ import annotations

from unittest.mock import Mock, patch

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.core.subtitles import Series
from scinoephile.multilang.yue_zho.transcription import get_yue_transcribed_vs_zho


def test_get_yue_transcribed_vs_zho_dispatches_media_and_stream_index():
    """Test transcription entrypoint dispatches media loading and block processing."""
    zhongwen_series = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n你好\n",
        format_="srt",
    )
    media_infile_path = "/tmp/test_media.mp4"
    yuewen_audio_series = Mock(spec=AudioSeries)
    expected_yuewen_series = Mock(spec=AudioSeries)
    transcriber = Mock()
    transcriber.process_all_blocks.return_value = expected_yuewen_series

    with patch(
        "scinoephile.multilang.yue_zho.transcription.AudioSeries.load_from_media",
        return_value=yuewen_audio_series,
    ) as patched_media_loader:
        output_series = get_yue_transcribed_vs_zho(
            zhongwen=zhongwen_series,
            media_path=media_infile_path,
            stream_index=3,
            transcriber=transcriber,
        )

    assert output_series == expected_yuewen_series
    assert patched_media_loader.call_count == 1
    assert patched_media_loader.call_args.kwargs["media_path"] == media_infile_path
    assert patched_media_loader.call_args.kwargs["stream_index"] == 3
    transcriber.process_all_blocks.assert_called_once_with(
        yuewen_audio_series, zhongwen_series
    )
