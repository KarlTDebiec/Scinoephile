#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of YueTranscriber internals."""

from __future__ import annotations

from unittest.mock import Mock

from scinoephile.multilang.yue_zho.transcription.transcriber import (
    DemucsMode,
    VADMode,
    YueTranscriber,
)


def test_transcribe_block_audio_applies_demucs_before_vad_retry():
    """Test block transcription applies Demucs before VAD retry."""
    transcriber = object.__new__(YueTranscriber)
    transcriber.vad_mode = VADMode.AUTO
    transcriber.demucs_mode = DemucsMode.ON
    transcriber.demucs_separator = Mock()
    transcriber.vad_transcriber = Mock(return_value=[Mock(text="   ")])
    transcriber.no_vad_transcriber = Mock(return_value=[Mock(text="你好")])

    input_audio = Mock()
    input_audio.raw_data = b"raw-audio"
    separated_audio = Mock()
    transcriber.demucs_separator.return_value = separated_audio

    output = transcriber._transcribe_block_audio(input_audio)

    assert output == transcriber.no_vad_transcriber.return_value
    transcriber.demucs_separator.assert_called_once_with(input_audio)
    transcriber.vad_transcriber.assert_called_once_with(separated_audio)
    transcriber.no_vad_transcriber.assert_called_once_with(separated_audio)
