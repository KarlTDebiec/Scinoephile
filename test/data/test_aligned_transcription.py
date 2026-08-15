#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for aligned multi-source transcription test-data generation."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from unittest.mock import Mock, patch

from pydub import AudioSegment
from pytest import LogCaptureFixture, raises

import test.data.aligned_transcription as transcription_data
from scinoephile.analysis.character_error_rate import LineCER
from scinoephile.analysis.transcription import (
    AlignmentArtifact,
    AlignmentBlock,
    AlignmentColumn,
    AlignmentRow,
    AlignmentSource,
    AlignmentSubtitle,
    ProcessorIdentity,
    RunBlock,
    RunManifest,
)
from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.vad import SpeechBlock
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.media.audio import AudioExtractionMode
from scinoephile.workflows.transcription_pipeline import TranscriptionPipeline


def test_evaluation_writes_standardized_metrics_and_audit(
    tmp_path: Path, caplog: LogCaptureFixture
):
    """Evaluation should report every source, merged CER, and display timing."""
    artifact = _get_artifact()
    reference = Series(events=[Subtitle(start=900, end=2_100, text="係呀")])
    caplog.set_level("INFO", logger="test.data.aligned_transcription")

    with patch(
        "scinoephile.analysis.transcription.evaluation.LineCER", wraps=LineCER
    ) as line_cer:
        transcription_data._save_evaluation(  # noqa: SLF001
            tmp_path,
            artifact,
            reference,
            audit_references={"yue-Hant": reference},
            terminal_authority="yue-Hant",
        )

    assert line_cer.call_count == 9
    metrics = json.loads((tmp_path / "json/metrics.json").read_text(encoding="utf-8"))
    assert metrics["format"] == "scinoephile-transcription-evaluation"
    assert set(metrics["cer"]) == {"whisper", "mimo", "merged"}
    assert metrics["candidate_subtitles"] == 1
    assert metrics["reference_subtitles"] == 1
    audit = (tmp_path / "audit.md").read_text(encoding="utf-8")
    assert "# Transcription Alignment Audit" in audit
    assert "yue-Hant" in audit
    assert "support" in audit
    assert f"- whisper CER: {metrics['cer']['whisper']['cer']:.3%}" in audit
    assert "#### Block CER" in audit
    assert "| Block | Reference characters | merged | whisper | mimo |" in audit
    assert "Authority: yue-Hant" in caplog.text
    assert any("\x1b[32m" in record.getMessage() for record in caplog.records)


def test_evaluation_reuses_unchanged_metrics_and_audit(tmp_path: Path):
    """Unchanged evaluation inputs should not realign or rewrite saved output."""
    artifact = _get_artifact()
    reference = Series(events=[Subtitle(start=900, end=2_100, text="係呀")])
    transcription_data._save_evaluation(  # noqa: SLF001
        tmp_path, artifact, reference, audit_references={"yue-Hant": reference}
    )
    metrics_path = tmp_path / "json/metrics.json"
    audit_path = tmp_path / "audit.md"
    metrics_mtime = metrics_path.stat().st_mtime_ns
    audit_mtime = audit_path.stat().st_mtime_ns

    with (
        patch("test.data.aligned_transcription.evaluate_transcription") as evaluate,
        patch("test.data.aligned_transcription.audit_transcription_alignment") as audit,
    ):
        transcription_data._save_evaluation(  # noqa: SLF001
            tmp_path, artifact, reference, audit_references={"yue-Hant": reference}
        )

    evaluate.assert_not_called()
    audit.assert_not_called()
    assert metrics_path.stat().st_mtime_ns == metrics_mtime
    assert audit_path.stat().st_mtime_ns == audit_mtime


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
        patch("test.data.aligned_transcription._load_audio_series") as load_audio,
        patch(
            "test.data.aligned_transcription.get_transcription_pipeline"
        ) as get_pipeline,
    ):
        output = transcription_data.process_transcription(
            title_root_path, reference_path=reference_path, reference_name="yue-Hant"
        )

    assert output == artifact.get_series()
    assert (output_dir_path / "transcribe.srt").exists()
    load_audio.assert_not_called()
    get_pipeline.assert_not_called()


def test_existing_alignment_is_regenerated_for_different_block_count(tmp_path: Path):
    """An explicit block count should invalidate a different existing prefix."""
    title_root_path = tmp_path / "title"
    output_dir_path = title_root_path / "output/yue-Hant_transcribe"
    artifact_path = output_dir_path / "json/alignment.json"
    reference_path = tmp_path / "reference.srt"
    artifact = _get_artifact()
    artifact.save(artifact_path)
    artifact.get_series().save(reference_path)
    audio = AudioSeries(audio=AudioSegment.silent(duration=3_000), events=[])
    provider = Mock(completion_metrics=[])
    pipeline = Mock(spec=TranscriptionPipeline)
    pipeline.last_alignment_artifact = artifact

    with (
        patch(
            "test.data.aligned_transcription._load_audio_series", return_value=audio
        ) as load_audio,
        patch("test.data.aligned_transcription.get_provider", return_value=provider),
        patch(
            "test.data.aligned_transcription.get_transcription_pipeline",
            return_value=pipeline,
        ),
        patch(
            "test.data.aligned_transcription.transcribe_series",
            return_value=artifact.get_series(),
        ) as transcribe,
    ):
        transcription_data.process_transcription(
            title_root_path, reference_path=reference_path, stop_at_idx=2
        )

    load_audio.assert_called_once()
    transcribe.assert_called_once_with(
        audio,
        language=Language.yue_hant,
        pipeline=pipeline,
        alignment_outfile_path=artifact_path,
        run_manifest_outfile_path=output_dir_path / "json/run.json",
        stop_at_idx=2,
    )


def test_fresh_run_routes_and_writes_outputs(tmp_path: Path):
    """A fresh run should route provenance and write harness outputs."""
    title_root_path = tmp_path / "title"
    output_dir_path = title_root_path / "output/yue-Hant_transcribe"
    reference_path = tmp_path / "reference.srt"
    artifact = _get_artifact()
    output = artifact.get_series()
    output.save(reference_path)
    audio = AudioSeries(audio=AudioSegment.silent(duration=3_000), events=[])
    provider = Mock(completion_metrics=[])
    pipeline = Mock(spec=TranscriptionPipeline)
    pipeline.last_alignment_artifact = artifact

    with (
        patch(
            "test.data.aligned_transcription._load_audio_series", return_value=audio
        ) as load_audio,
        patch("test.data.aligned_transcription.get_provider", return_value=provider),
        patch(
            "test.data.aligned_transcription.get_transcription_pipeline",
            return_value=pipeline,
        ) as get_pipeline,
        patch(
            "test.data.aligned_transcription.save_chat_completion_metrics_to_json"
        ) as save_usage,
        patch(
            "test.data.aligned_transcription.transcribe_series", return_value=output
        ) as transcribe,
    ):
        result = transcription_data.process_transcription(
            title_root_path,
            reference_path=reference_path,
            stop_at_idx=1,
            target_reference_count=0,
        )

    json_dir_path = output_dir_path / "json"
    assert result == output
    load_audio.assert_called_once_with(
        title_root_path / "input/yue.wav",
        media_path=None,
        stream_index=None,
        audio_extraction_mode=AudioExtractionMode.ORIGINAL,
        media_start_seconds=0.0,
    )
    get_pipeline.assert_called_once_with(
        Language.yue_hant,
        provider=provider,
        additional_context=None,
        current_test_cases_path=json_dir_path / "transcription.json",
    )
    transcribe.assert_called_once_with(
        audio,
        language=Language.yue_hant,
        pipeline=pipeline,
        alignment_outfile_path=json_dir_path / "alignment.json",
        run_manifest_outfile_path=json_dir_path / "run.json",
        stop_at_idx=1,
    )
    save_usage.assert_called_once_with(json_dir_path / "llm_usage.json", [])
    assert (output_dir_path / "transcribe.srt").exists()
    assert (output_dir_path / "audit.md").exists()
    assert (json_dir_path / "metrics.json").exists()


def test_media_audio_trim_is_applied_before_staging(tmp_path: Path):
    """Media extraction should apply title-specific leading trim before staging."""
    extracted = AudioSeries(
        audio=AudioSegment.silent(duration=5_000, frame_rate=16_000), events=[]
    )
    staged = AudioSegment.silent(duration=4_000, frame_rate=16_000)
    with patch(
        "test.data.aligned_transcription.load_audio_segment",
        side_effect=(extracted.audio, staged),
    ) as load_audio:
        audio_path = tmp_path / "audio.wav"
        audio = transcription_data._load_audio_series(  # noqa: SLF001
            audio_path,
            media_path=tmp_path / "source.mkv",
            stream_index=12,
            media_start_seconds=1.0,
        )
        reloaded = transcription_data._load_audio_series(  # noqa: SLF001
            audio_path,
            media_path=tmp_path / "source.mkv",
            stream_index=12,
            media_start_seconds=1.0,
        )

    assert len(audio.audio) == 4_000
    assert len(reloaded.audio) == 4_000
    assert audio_path.exists()
    assert not audio_path.with_suffix(".srt").exists()
    assert load_audio.call_count == 2
    assert load_audio.call_args_list[0].args == (tmp_path / "source.mkv",)
    assert load_audio.call_args_list[0].kwargs == {
        "stream_index": 12,
        "mode": AudioExtractionMode.ORIGINAL,
    }
    assert load_audio.call_args_list[1].args == (audio_path,)
    assert not load_audio.call_args_list[1].kwargs


def test_reference_count_selects_smallest_block_prefix():
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

    assert (
        transcription_data._get_stop_at_idx_for_reference_count(  # noqa: SLF001
            pipeline, audio, reference, 3
        )
        == 2
    )
    with raises(ScinoephileError, match="covers only 3"):
        transcription_data._get_stop_at_idx_for_reference_count(  # noqa: SLF001
            pipeline, audio, reference, 4
        )


def test_run_prefix_is_reused_only_when_current_configuration_matches():
    """Prefix reuse should require matching audio, plan, processor, and artifact."""
    audio = AudioSeries(audio=AudioSegment.silent(duration=6_000), events=[])
    artifact = _get_artifact().model_copy(update={"audio_duration_ms": 6_000})
    processor = _get_processor_identity()
    manifest = _get_manifest(audio, artifact, processor, planned_block_count=2)
    pipeline = Mock(spec=TranscriptionPipeline)
    pipeline.language = Language.yue_hant
    pipeline.alignment_sources = artifact.sources
    pipeline.timing_settings = artifact.timing
    pipeline.block_vad_identity = {"implementation": "test"}
    pipeline.processor_identity = processor
    pipeline.plan_blocks.return_value = (
        SpeechBlock(
            index=0,
            start_ms=500,
            end_ms=2_500,
            buffered_start_ms=0,
            buffered_end_ms=3_000,
        ),
        SpeechBlock(
            index=1,
            start_ms=3_500,
            end_ms=5_500,
            buffered_start_ms=3_000,
            buffered_end_ms=6_000,
        ),
    )

    assert transcription_data._is_reusable_prefix(  # noqa: SLF001
        pipeline, audio, artifact, manifest, 2
    )

    pipeline.block_vad_identity = {"implementation": "changed"}
    assert not transcription_data._is_reusable_prefix(  # noqa: SLF001
        pipeline, audio, artifact, manifest, 2
    )


def test_run_prefix_combination_renumbers_and_retimes_subtitles():
    """A resumed suffix should combine into one validated artifact and manifest."""
    prefix_artifact = _get_artifact().model_copy(update={"audio_duration_ms": 6_000})
    prefix_block = prefix_artifact.blocks[0]
    suffix_block = AlignmentBlock.model_validate(
        {
            **prefix_block.model_dump(mode="python"),
            "index": 2,
            "core_start_ms": 3_500,
            "core_end_ms": 5_500,
            "buffered_start_ms": 3_000,
            "buffered_end_ms": 6_000,
            "columns": (
                AlignmentColumn(index=1, start_ms=4_000, end_ms=4_500, kind="text"),
                AlignmentColumn(index=2, start_ms=4_500, end_ms=5_000, kind="text"),
            ),
            "subtitles": (
                AlignmentSubtitle(
                    index=1,
                    text="係呀",
                    speech_start_ms=4_000,
                    speech_end_ms=5_000,
                    timing_source="source",
                    start_ms=4_000,
                    end_ms=5_000,
                ),
            ),
        }
    )
    suffix_artifact = prefix_artifact.model_copy(update={"blocks": (suffix_block,)})
    audio = AudioSeries(audio=AudioSegment.silent(duration=6_000), events=[])
    processor = _get_processor_identity()
    prefix_manifest = _get_manifest(
        audio, prefix_artifact, processor, planned_block_count=2
    )
    suffix_manifest = _get_manifest(
        audio, suffix_artifact, processor, planned_block_count=2, block_index=2
    )

    artifact, manifest = transcription_data._combine_run_prefix(  # noqa: SLF001
        prefix_artifact, prefix_manifest, suffix_artifact, suffix_manifest
    )

    assert [block.index for block in artifact.blocks] == [1, 2]
    assert [
        subtitle.index for block in artifact.blocks for subtitle in block.subtitles
    ] == [1, 2]
    assert [block.index for block in manifest.blocks] == [1, 2]
    assert manifest.alignment_sha256 == artifact.sha256


def _get_artifact() -> AlignmentArtifact:
    """Get a compact valid evaluation artifact.

    Returns:
        compact valid evaluation artifact
    """
    return AlignmentArtifact(
        language=Language.yue_hant,
        audio_duration_ms=3_000,
        sources=(
            AlignmentSource(name="whisper", backend="whisper", model="whisper"),
            AlignmentSource(name="mimo", backend="mlx", model="mimo"),
        ),
        blocks=(
            AlignmentBlock(
                index=1,
                core_start_ms=500,
                core_end_ms=2_500,
                buffered_start_ms=0,
                buffered_end_ms=3_000,
                columns=(
                    AlignmentColumn(index=1, start_ms=1_000, end_ms=1_500, kind="text"),
                    AlignmentColumn(index=2, start_ms=1_500, end_ms=2_000, kind="text"),
                ),
                rows=(
                    AlignmentRow(name="whisper", text="係呀"),
                    AlignmentRow(name="mimo", text="是呀"),
                ),
                speaker="ＡＡ",
                language_trace="粵粵",
                language_legend={"粵": "zh-yue"},
                singing_trace="　唱",
                music_trace="樂樂",
                merged="係呀",
                subtitles=(
                    AlignmentSubtitle(
                        index=1,
                        text="係呀",
                        speech_start_ms=1_000,
                        speech_end_ms=2_000,
                        timing_source="source",
                        start_ms=1_000,
                        end_ms=2_000,
                    ),
                ),
            ),
        ),
    )


def _get_processor_identity() -> ProcessorIdentity:
    """Get a compact test processor identity."""
    return ProcessorIdentity(
        operation="transcription",
        prompt_name="test",
        system_prompt_sha256="a" * 64,
        provider_identity={"implementation": "test"},
        no_op=True,
    )


def _get_manifest(
    audio: AudioSeries,
    artifact: AlignmentArtifact,
    processor: ProcessorIdentity,
    *,
    planned_block_count: int,
    block_index: int = 1,
) -> RunManifest:
    """Get a compact test run manifest.

    Arguments:
        audio: complete source audio
        artifact: corresponding alignment artifact
        processor: consensus processor identity
        planned_block_count: number of blocks in the complete plan
        block_index: selected block index
    Returns:
        compact run manifest
    """
    return RunManifest(
        language=artifact.language,
        audio_sha256=sha256(audio.audio.raw_data).hexdigest(),
        audio_duration_ms=len(audio.audio),
        audio_channels=audio.audio.channels,
        audio_frame_rate=audio.audio.frame_rate,
        audio_sample_width=audio.audio.sample_width,
        block_vad_identity={"implementation": "test"},
        planned_block_count=planned_block_count,
        blocks=(RunBlock(index=block_index, status="transcribed"),),
        processor=processor,
        alignment_sha256=artifact.sha256,
    )
