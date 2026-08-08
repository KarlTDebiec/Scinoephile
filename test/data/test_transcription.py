#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for aligned multi-source transcription test-data generation."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock, patch

from pydub import AudioSegment
from pytest import LogCaptureFixture, raises

from scinoephile.analysis.transcription_alignment import (
    TranscriptionAlignmentArtifact,
    TranscriptionAlignmentBlock,
    TranscriptionAlignmentColumn,
    TranscriptionAlignmentRow,
    TranscriptionAlignmentSource,
    TranscriptionAlignmentSubtitle,
)
from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.transcription import SpeechBlock
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.transcription.pipeline import TranscriptionPipeline
from test.data.transcription import (
    _get_stop_at_idx_for_reference_count,
    _load_audio_series,
    _save_evaluation,
    process_transcription_pipeline,
)


def test_reference_count_selects_smallest_vad_block_prefix():
    """The evaluation harness should stop after the target reference count."""
    pipeline = Mock(spec=TranscriptionPipeline)
    pipeline.plan_blocks.return_value = (
        SpeechBlock(
            index=0,
            start_ms=1_000,
            end_ms=3_000,
            buffered_start_ms=0,
            buffered_end_ms=4_000,
        ),
        SpeechBlock(
            index=1,
            start_ms=5_000,
            end_ms=8_000,
            buffered_start_ms=4_000,
            buffered_end_ms=9_000,
        ),
    )
    audio = AudioSeries(audio=AudioSegment.silent(duration=10_000), events=[])
    reference = Series(
        events=[
            Subtitle(start=1_100, end=1_500, text="甲"),
            Subtitle(start=2_000, end=2_400, text="乙"),
            Subtitle(start=5_200, end=5_600, text="丙"),
        ]
    )

    assert _get_stop_at_idx_for_reference_count(pipeline, audio, reference, 3) == 2
    with raises(ScinoephileError, match="covers only 3"):
        _get_stop_at_idx_for_reference_count(pipeline, audio, reference, 4)


def test_media_audio_trim_is_applied_before_staging(tmp_path: Path):
    """Media extraction should apply title-specific leading trim before staging."""
    extracted = AudioSeries(
        audio=AudioSegment.silent(duration=5_000, frame_rate=16_000), events=[]
    )
    with patch.object(
        AudioSeries, "load_audio_from_media", return_value=extracted
    ) as load_audio:
        audio_path = tmp_path / "audio.wav"
        audio = _load_audio_series(
            audio_path,
            media_path=tmp_path / "source.mkv",
            stream_index=12,
            media_start_seconds=1.0,
        )
        reloaded = _load_audio_series(
            audio_path,
            media_path=tmp_path / "source.mkv",
            stream_index=12,
            media_start_seconds=1.0,
        )

    assert len(audio.audio) == 4_000
    assert len(reloaded.audio) == 4_000
    assert audio_path.exists()
    assert not audio_path.with_suffix(".srt").exists()
    load_audio.assert_called_once()


def test_existing_alignment_recreates_srt_without_transcription(tmp_path: Path):
    """A portable alignment alone should be sufficient to reuse test output."""
    title_root_path = tmp_path / "title"
    output_dir_path = title_root_path / "output/yue-Hant_transcribe"
    artifact_path = output_dir_path / "json/alignment.json"
    reference_path = tmp_path / "reference.srt"
    artifact = _get_artifact()
    artifact.save(artifact_path)
    artifact.get_series().save(reference_path)

    with (
        patch("test.data.transcription._load_audio_series") as load_audio,
        patch("test.data.transcription.get_transcription_pipeline") as get_pipeline,
    ):
        output = process_transcription_pipeline(
            title_root_path, reference_path=reference_path, reference_name="yue-Hant"
        )

    assert output == artifact.get_series()
    assert (output_dir_path / "transcribe.srt").exists()
    load_audio.assert_not_called()
    get_pipeline.assert_not_called()


def test_evaluation_writes_standardized_metrics_and_audit(
    tmp_path: Path, caplog: LogCaptureFixture
):
    """Evaluation should report every source, merged CER, and display timing."""
    artifact = _get_artifact()
    reference = Series(events=[Subtitle(start=900, end=2_100, text="係呀")])
    caplog.set_level("INFO", logger="test.data.transcription")

    _save_evaluation(
        tmp_path,
        artifact,
        reference,
        audit_references={"yue-Hant": reference},
        terminal_alignment_authority="yue-Hant",
    )

    metrics = json.loads((tmp_path / "json/metrics.json").read_text(encoding="utf-8"))
    assert metrics["format"] == "scinoephile-transcription-evaluation"
    assert set(metrics["cer"]) == {"whisper", "mimo", "merged"}
    assert metrics["candidate_subtitles"] == 1
    assert metrics["reference_subtitles"] == 1
    audit = (tmp_path / "audit.md").read_text(encoding="utf-8")
    assert "# Transcription Alignment Audit" in audit
    assert "yue-Hant" in audit
    assert "support" in audit
    assert "Authority: yue-Hant" in caplog.text
    assert any("\x1b[32m" in record.getMessage() for record in caplog.records)


def _get_artifact() -> TranscriptionAlignmentArtifact:
    """Get a compact valid evaluation artifact."""
    return TranscriptionAlignmentArtifact(
        language=Language.yue_hant,
        audio_duration_ms=3_000,
        sources=(
            TranscriptionAlignmentSource(
                name="whisper", backend="whisper", model="whisper"
            ),
            TranscriptionAlignmentSource(name="mimo", backend="mlx", model="mimo"),
        ),
        blocks=(
            TranscriptionAlignmentBlock(
                index=1,
                core_start_ms=500,
                core_end_ms=2_500,
                buffered_start_ms=0,
                buffered_end_ms=3_000,
                columns=(
                    TranscriptionAlignmentColumn(
                        index=1, start_ms=1_000, end_ms=1_500, kind="text"
                    ),
                    TranscriptionAlignmentColumn(
                        index=2, start_ms=1_500, end_ms=2_000, kind="text"
                    ),
                ),
                rows=(
                    TranscriptionAlignmentRow(name="whisper", text="係呀"),
                    TranscriptionAlignmentRow(name="mimo", text="是呀"),
                ),
                speaker="ＡＡ",
                language_trace="粵粵",
                language_legend={"粵": "zh-yue"},
                singing_trace="　唱",
                music_trace="樂樂",
                merged="係呀",
                subtitles=(
                    TranscriptionAlignmentSubtitle(
                        index=1,
                        text="係呀",
                        speech_start_ms=1_000,
                        speech_end_ms=2_000,
                        start_ms=1_000,
                        end_ms=2_000,
                    ),
                ),
            ),
        ),
    )
