#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for transcription test-data generation helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.core import Language
from scinoephile.core.subtitles import Series, Subtitle
from test.data.transcription import process_transcription


def test_process_transcription_detects_languages_and_uses_workflow_defaults(
    tmp_path: Path,
):
    """Test the helper infers languages without overriding workflow defaults.

    Arguments:
        tmp_path: temporary path
    """
    reference = Series(events=[Subtitle(start=0, end=1000, text="我哋而家返嚟喇")])
    guide = Series(events=[Subtitle(start=0, end=1000, text="我們現在回來了")])
    audio = Mock(spec=AudioSeries)
    output_dir_path = tmp_path / "output"
    audio_dir_path = output_dir_path / "audio"
    audio_dir_path.mkdir(parents=True)
    (audio_dir_path / "audio.wav").touch()
    transcribe_path = output_dir_path / "transcribe.srt"

    with patch(
        "test.data.transcription.Series.load",
        side_effect=(reference, guide),
    ):
        with patch(
            "test.data.transcription.resolve_language",
            side_effect=(Language.yue_hant, Language.zho_hant),
        ) as resolve_language:
            with patch(
                "test.data.transcription.AudioSeries.load",
                return_value=audio,
            ):
                with patch(
                    "test.data.transcription.transcribe_series_guided",
                    return_value=reference,
                ) as transcribe:
                    process_transcription(
                        tmp_path,
                        tmp_path / "guide.srt",
                        reference_path=tmp_path / "reference.srt",
                        output_dir_path=output_dir_path,
                        transcribe_path=transcribe_path,
                        overwrite=True,
                    )

    assert resolve_language.call_args_list[0].args == (reference, None)
    assert resolve_language.call_args_list[1].args == (guide, None)
    assert transcribe.call_args.kwargs["language"] is Language.yue_hant
    assert transcribe.call_args.kwargs["reference_language"] is Language.zho_hant
    assert "demucs_mode" not in transcribe.call_args.kwargs
    assert "vad_mode" not in transcribe.call_args.kwargs
