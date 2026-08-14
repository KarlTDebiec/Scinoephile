#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Generate and evaluate aligned multi-source transcription test data."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping
from logging import getLogger
from pathlib import Path

from pydub import AudioSegment

from scinoephile.analysis.audit.transcription.report import (
    audit_transcription_alignment,
    render_transcription_alignment_terminal,
)
from scinoephile.analysis.character_error_rate import LineCER
from scinoephile.analysis.transcription import AlignmentArtifact
from scinoephile.analysis.transcription.timing import (
    evaluate_timing,
    get_reference_for_alignment,
)
from scinoephile.audio.segment import load_audio_segment
from scinoephile.audio.subtitles import AudioSeries
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms.metrics import (
    format_chat_completion_metrics_report,
    save_chat_completion_metrics_to_json,
)
from scinoephile.core.subtitles import Series
from scinoephile.lang.yue.transcription import YueTokenSimilarity
from scinoephile.llms.providers.registry import get_provider
from scinoephile.media.audio import AudioExtractionMode
from scinoephile.workflows.transcription import transcribe_series
from scinoephile.workflows.transcription_pipeline import TranscriptionPipeline
from scinoephile.workflows.transcription_pipeline.factory import (
    get_transcription_pipeline,
)

__all__ = ["process_transcription_pipeline"]

logger = getLogger(__name__)


def process_transcription_pipeline(  # noqa: PLR0912, PLR0915
    title_root_path: Path,
    *,
    reference_path: Path,
    media_path: Path | None = None,
    stream_index: int | None = None,
    audio_extraction_mode: AudioExtractionMode = AudioExtractionMode.ORIGINAL,
    media_start_seconds: float = 0.0,
    stop_at_idx: int | None = None,
    target_reference_subtitles: int = 100,
    additional_context: str | None = None,
    additional_audit_references: Mapping[str, Series] | None = None,
    reference_name: str = "reference",
    terminal_alignment_authority: str | None = None,
    overwrite: bool = False,
) -> Series:
    """Run one reference-free transcription experiment and save its evaluation.

    The Cantonese reference determines only how many leading blocks are run
    and how the finished output is scored. It is never passed to ASR, alignment,
    CTC timing, diarization, or the consensus LLM.

    Arguments:
        title_root_path: test title root directory
        reference_path: independent Cantonese reference used only for evaluation
        media_path: optional media from which to extract audio when not staged
        stream_index: optional media audio-stream index
        audio_extraction_mode: channel preparation used during media audio extraction
        media_start_seconds: seconds trimmed from extracted media audio
        stop_at_idx: explicit exclusive block index, overriding target count
        target_reference_subtitles: minimum reference subtitles covered by blocks
        additional_context: production consensus prompt context
        additional_audit_references: additional named references used only in audits
        reference_name: audit row name for the primary scoring reference
        terminal_alignment_authority: merged or named reference row for ANSI output
        overwrite: whether to regenerate an existing artifact and SRT
    Returns:
        merged transcription series
    """
    if target_reference_subtitles <= 0:
        raise ValueError("target_reference_subtitles must be positive.")
    output_dir_path = title_root_path / "output" / "yue-Hant_transcribe"
    audio_path = output_dir_path / "audio.wav"
    output_dir_path.mkdir(parents=True, exist_ok=True)
    json_dir_path = output_dir_path / "json"
    json_dir_path.mkdir(parents=True, exist_ok=True)
    artifact_path = json_dir_path / "alignment.json"
    run_manifest_path = json_dir_path / "run.json"
    transcription_path = output_dir_path / "transcribe.srt"
    reference = Series.load(reference_path)
    audit_references = {reference_name: reference}
    for name, audit_reference in (additional_audit_references or {}).items():
        if name in audit_references:
            raise ValueError(f"Duplicate audit reference name: {name}")
        audit_references[name] = audit_reference

    if artifact_path.exists() and not overwrite:
        artifact = AlignmentArtifact.load(artifact_path)
        output = artifact.get_series()
        if not transcription_path.exists():
            output.save(transcription_path)
        _save_evaluation(
            output_dir_path,
            artifact,
            reference,
            audit_references=audit_references,
            terminal_alignment_authority=terminal_alignment_authority,
        )
        return output

    audio = _load_audio_series(
        audio_path,
        media_path=media_path,
        stream_index=stream_index,
        audio_extraction_mode=audio_extraction_mode,
        media_start_seconds=media_start_seconds,
    )
    provider = get_provider()
    initial_completion_count = len(provider.completion_metrics)
    pipeline = get_transcription_pipeline(
        Language.yue_hant,
        provider=provider,
        additional_context=additional_context,
        current_test_cases_path=json_dir_path / "transcription.json",
    )
    if stop_at_idx is None:
        stop_at_idx = _get_stop_at_idx_for_reference_count(
            pipeline, audio, reference, target_reference_subtitles
        )
    output = transcribe_series(
        audio,
        language=Language.yue_hant,
        pipeline=pipeline,
        alignment_outfile_path=artifact_path,
        run_manifest_outfile_path=run_manifest_path,
        stop_at_idx=stop_at_idx,
    )
    output.save(transcription_path)
    artifact = pipeline.last_alignment_artifact
    if artifact is None:
        raise RuntimeError("Transcription pipeline did not produce an artifact.")
    completion_metrics = provider.completion_metrics[initial_completion_count:]
    usage_path = json_dir_path / "llm_usage.json"
    save_chat_completion_metrics_to_json(usage_path, completion_metrics)
    logger.info(format_chat_completion_metrics_report(completion_metrics))
    _save_evaluation(
        output_dir_path,
        artifact,
        reference,
        audit_references=audit_references,
        terminal_alignment_authority=terminal_alignment_authority,
    )
    return output


def _get_stop_at_idx_for_reference_count(
    pipeline: TranscriptionPipeline,
    audio: AudioSeries,
    reference: Series,
    target_count: int,
) -> int:
    """Get the smallest block prefix covering the target reference count."""
    blocks = pipeline.plan_blocks(audio)
    covered = 0
    for stop_at_idx, block in enumerate(blocks, start=1):
        covered += sum(
            block.start_ms <= (subtitle.start + subtitle.end) / 2 < block.end_ms
            for subtitle in reference
        )
        if covered >= target_count:
            logger.info(
                f"Selected {stop_at_idx} blocks covering {covered} reference subtitles."
            )
            return stop_at_idx
    raise ScinoephileError(
        f"The complete block plan covers only {covered} reference subtitles; "
        f"cannot reach target {target_count}."
    )


def _load_audio_series(
    audio_path: Path,
    *,
    media_path: Path | None,
    stream_index: int | None,
    audio_extraction_mode: AudioExtractionMode = AudioExtractionMode.ORIGINAL,
    media_start_seconds: float,
) -> AudioSeries:
    """Load staged complete audio without supplying subtitle events to ASR."""
    if media_start_seconds < 0.0:
        raise ValueError("media_start_seconds must be non-negative.")
    if audio_path.exists():
        return AudioSeries(audio=AudioSegment.from_wav(audio_path), events=[])
    if media_path is None:
        raise ScinoephileError(
            f"Staged audio is missing at {audio_path}; provide media_path."
        )
    audio = AudioSeries(
        audio=load_audio_segment(
            media_path, stream_index=stream_index, mode=audio_extraction_mode
        )
    )
    trim_start_ms = round(media_start_seconds * 1000)
    if trim_start_ms >= len(audio.audio):
        raise ScinoephileError(
            f"Audio trim start {media_start_seconds:.3f}s is outside the media."
        )
    if trim_start_ms:
        audio = AudioSeries(audio=audio.audio[trim_start_ms:], events=[])
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    audio.audio.export(audio_path, format="wav")
    return audio


def _save_evaluation(
    output_dir_path: Path,
    artifact: AlignmentArtifact,
    reference: Series,
    *,
    audit_references: Mapping[str, Series],
    terminal_alignment_authority: str | None = None,
):
    """Save evaluation metrics and readable alignment audits."""
    primary_metrics = _get_reference_metrics(artifact, reference)
    cer = primary_metrics["cer"]
    metrics = {
        "format": "scinoephile-transcription-evaluation",
        "version": 1,
        "processed_blocks": len(artifact.blocks),
        **primary_metrics,
    }
    json_dir_path = output_dir_path / "json"
    json_dir_path.mkdir(parents=True, exist_ok=True)
    (json_dir_path / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    reference_similarity = None
    if artifact.language in {Language.yue_hans, Language.yue_hant}:
        reference_similarity = YueTokenSimilarity(
            timing_weight=2.0, timing_tolerance_seconds=0.75
        )
    (output_dir_path / "audit.md").write_text(
        audit_transcription_alignment(
            artifact,
            audit_references,
            reference_similarity=reference_similarity,
            include_merge_support=True,
        ),
        encoding="utf-8",
    )
    if terminal_alignment_authority is not None:
        terminal_alignment = render_transcription_alignment_terminal(
            artifact,
            audit_references,
            authoritative_row_name=terminal_alignment_authority,
            reference_similarity=reference_similarity,
            include_merge_support=True,
        )
        logger.info(f"\n{terminal_alignment.rstrip()}")
    logger.info(
        "Aligned transcription evaluation: "
        + ", ".join(f"{name} CER {values['cer']:.3%}" for name, values in cer.items())
    )


def _get_reference_metrics(artifact: AlignmentArtifact, reference: Series) -> dict:
    """Calculate lexical and timing metrics against one named reference."""
    selected_reference = get_reference_for_alignment(artifact, reference)
    reference_text = "".join(
        subtitle.text_with_newline for subtitle in selected_reference
    )
    candidate_texts = {source.name: [] for source in artifact.sources}
    for block in artifact.blocks:
        rows = {row.name: row.text for row in block.rows}
        for source in artifact.sources:
            candidate_texts[source.name].append(
                rows.get(source.name, "").replace("　", "").replace("・", "")
            )
    candidate_texts["merged"] = [
        subtitle.text for block in artifact.blocks for subtitle in block.subtitles
    ]
    cer = {
        name: _get_cer_dict(LineCER(reference_text, "".join(text_parts)))
        for name, text_parts in candidate_texts.items()
    }
    timing = evaluate_timing(artifact, reference)
    subtitle_alignment_groups = Counter(
        f"{len(pair.candidate_indexes)}:{len(pair.reference_indexes)}"
        for pair in timing.pairs
    )
    return {
        "reference_subtitles": len(selected_reference),
        "candidate_subtitles": sum(len(block.subtitles) for block in artifact.blocks),
        "cer": cer,
        "timing": {
            "settings": timing.settings.model_dump(mode="json"),
            "text_aligned_groups": len(timing.pairs),
            "micro_intersection_over_union": timing.micro_intersection_over_union,
            "one_to_one_groups": len(timing.one_to_one_pairs),
            "one_to_one_micro_intersection_over_union": (
                timing.one_to_one_micro_intersection_over_union
            ),
            "mean_intersection_over_union": timing.mean_intersection_over_union,
            "mean_reference_coverage": timing.mean_reference_coverage,
            "mean_start_error_ms": timing.mean_start_error_ms,
            "mean_end_error_ms": timing.mean_end_error_ms,
            "mean_absolute_start_error_ms": timing.mean_absolute_start_error_ms,
            "mean_absolute_end_error_ms": timing.mean_absolute_end_error_ms,
            "unmatched_candidate_subtitles": timing.unmatched_candidate_subtitles,
            "unmatched_reference_subtitles": timing.unmatched_reference_subtitles,
            "candidate_to_reference_group_counts": dict(
                sorted(subtitle_alignment_groups.items())
            ),
        },
    }


def _get_cer_dict(result: LineCER) -> dict[str, float | int]:
    """Serialize one character-error result."""
    return {
        "cer": result.cer,
        "correct": result.correct,
        "substitutions": result.substitutions,
        "insertions": result.insertions,
        "deletions": result.deletions,
        "reference_length": result.reference_length,
    }
