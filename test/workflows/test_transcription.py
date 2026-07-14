#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for reference-guided transcription workflow."""

from __future__ import annotations

from unittest.mock import Mock, patch

from pydub import AudioSegment

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.core import Language
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.multilang.transcription.processor import GuidedTranscriptionProcessor
from scinoephile.workflows.transcription import transcribe_series_guided


def test_transcribe_series_guided_constructs_processor_for_language_pair():
    """Test workflow resolves construction and delegates processing."""
    audio_series = Mock(spec=AudioSeries)
    reference_series = Series(events=[Subtitle(start=0, end=1000, text="你好")])
    expected = AudioSeries(audio=AudioSegment.silent(duration=1000))
    transcriber = Mock(spec=GuidedTranscriptionProcessor)
    transcriber.process.return_value = expected

    with patch(
        "scinoephile.workflows.transcription.get_guided_transcriber",
        return_value=transcriber,
    ) as get_transcriber:
        output = transcribe_series_guided(
            audio_series,
            reference_series,
            language=Language.yue_hant,
            reference_language=Language.zho_hans,
            stop_at_idx=2,
        )

    assert output is expected
    assert get_transcriber.call_args.args == (
        Language.yue_hant,
        Language.zho_hans,
    )
    transcriber.process.assert_called_once_with(
        audio_series,
        reference_series,
        stop_at_idx=2,
    )
