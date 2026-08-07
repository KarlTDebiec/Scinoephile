#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Generate and evaluate aligned multi-source transcription test data."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping
from logging import getLogger
from pathlib import Path
from shutil import copy2

from pydub import AudioSegment

from scinoephile.analysis.audit.transcription_alignment import (
    audit_transcription_alignment,
    render_transcription_alignment_terminal,
)
from scinoephile.analysis.character_error_rate import LineCER
from scinoephile.analysis.transcription_alignment import (
    SubtitleTimingSettings,
    TranscriptionAlignmentArtifact,
)
from scinoephile.analysis.transcription_timing import (
    evaluate_transcription_timing,
    get_reference_for_alignment,
)
from scinoephile.audio.diarization import DiarizationMode
from scinoephile.audio.subtitles import AudioSeries
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms.metrics import (
    format_chat_completion_metrics_report,
    save_chat_completion_metrics_to_json,
)
from scinoephile.core.subtitles import Series
from scinoephile.lang.transcription.multisource_alignment import (
    CantoneseTimedTokenSimilarity,
)
from scinoephile.lang.transcription.pipeline import (
    TranscriptionPipeline,
    get_transcription_pipeline,
)
from scinoephile.llms.providers.registry import get_provider
from scinoephile.media.audio import AudioExtractionMode
from scinoephile.workflows.transcription import transcribe_series

__all__ = ["process_transcription_pipeline"]

logger = getLogger(__name__)


def process_transcription_pipeline(
    title_root_path: Path,
    *,
    reference_path: Path,
    language: Language = Language.yue_hant,
    output_dir_path: Path | None = None,
    audio_path: Path | None = None,
    audio_dir_path: Path | None = None,
    audio_source_path: Path | None = None,
    media_path: Path | None = None,
    stream_index: int | None = None,
    audio_extraction_mode: AudioExtractionMode = AudioExtractionMode.ORIGINAL,
    media_start_seconds: float = 0.0,
    stop_at_idx: int | None = None,
    target_reference_subtitles: int = 100,
    additional_context: str | None = None,
    additional_audit_references: Mapping[str, Series] | None = None,
    audit_include_merge_support: bool = False,
    reference_name: str = "reference",
    terminal_alignment_authority: str | None = None,
    timing_settings: SubtitleTimingSettings | None = None,
    diarization_mode: DiarizationMode = DiarizationMode.AUTO,
    skip_singing_blocks: bool = False,
    skip_non_target_language_blocks: bool = False,
    mlx_audio_token_limit_guard: bool = True,
    overwrite: bool = False,
) -> Series:
    """Run one reference-free transcription experiment and save its evaluation.

    The Cantonese reference determines only how many leading VAD blocks are run
    and how the finished output is scored. It is never passed to ASR, alignment,
    CTC timing, diarization, or the consensus LLM.

    Arguments:
        title_root_path: test title root directory
        reference_path: independent Cantonese reference used only for evaluation
        language: transcription and output language
        output_dir_path: standardized output directory
        audio_path: path at which complete staged WAV audio is stored
        audio_dir_path: legacy directory containing `audio.wav`
        audio_source_path: optional WAV copied to the staged audio path
        media_path: optional media from which to extract audio when not staged
        stream_index: optional media audio-stream index
        audio_extraction_mode: channel preparation used during media audio extraction
        media_start_seconds: seconds trimmed from extracted media audio
        stop_at_idx: explicit exclusive VAD block index, overriding target count
        target_reference_subtitles: minimum reference subtitles covered by blocks
        additional_context: production consensus prompt context
        additional_audit_references: additional named references used only in audits
        audit_include_merge_support: whether generated audits show source support
        reference_name: audit row name for the primary scoring reference
        terminal_alignment_authority: merged or named reference row for ANSI output
        timing_settings: reference-free display-timing policy
        diarization_mode: speaker diarization mode
        skip_singing_blocks: whether to omit confidently singing VAD blocks
        skip_non_target_language_blocks: whether to omit confidently non-target
            language VAD blocks
        mlx_audio_token_limit_guard: whether to guard MiMo generation length
        overwrite: whether to regenerate an existing artifact and SRT
    Returns:
        merged transcription series
    """
    if target_reference_subtitles <= 0:
        raise ValueError("target_reference_subtitles must be positive.")
    if output_dir_path is None:
        output_dir_path = title_root_path / "output" / f"{language.code}_transcribe"
    if audio_path is not None and audio_dir_path is not None:
        raise ValueError("Specify audio_path or audio_dir_path, not both.")
    if audio_path is None:
        if audio_dir_path is None:
            audio_path = output_dir_path / "audio.wav"
        else:
            audio_path = audio_dir_path / "audio.wav"
    output_dir_path.mkdir(parents=True, exist_ok=True)
    json_dir_path = output_dir_path / "json"
    json_dir_path.mkdir(parents=True, exist_ok=True)
    artifact_path = json_dir_path / "alignment.json"
    transcription_path = output_dir_path / "transcribe.srt"
    reference = Series.load(reference_path)
    audit_references = {reference_name: reference}
    for name, audit_reference in (additional_audit_references or {}).items():
        if name in audit_references:
            raise ValueError(f"Duplicate audit reference name: {name}")
        audit_references[name] = audit_reference

    if artifact_path.exists() and transcription_path.exists() and not overwrite:
        artifact = TranscriptionAlignmentArtifact.load(artifact_path)
        output = artifact.get_series()
        _save_evaluation(
            output_dir_path,
            artifact,
            reference,
            audit_references=audit_references,
            include_merge_support=audit_include_merge_support,
            terminal_alignment_authority=terminal_alignment_authority,
        )
        return output

    audio = _load_audio_series(
        audio_path,
        audio_source_path=audio_source_path,
        media_path=media_path,
        stream_index=stream_index,
        audio_extraction_mode=audio_extraction_mode,
        media_start_seconds=media_start_seconds,
    )
    provider = get_provider()
    initial_completion_count = len(provider.completion_metrics)
    pipeline = get_transcription_pipeline(
        language,
        diarization_mode=diarization_mode,
        skip_singing_blocks=skip_singing_blocks,
        skip_non_target_language_blocks=skip_non_target_language_blocks,
        provider=provider,
        additional_context=additional_context,
        aligned_merge_json_path=json_dir_path / "aligned_merge.json",
        timing_settings=timing_settings,
        mlx_audio_token_limit_guard=mlx_audio_token_limit_guard,
    )
    if stop_at_idx is None:
        stop_at_idx = _get_stop_at_idx_for_reference_count(
            pipeline, audio, reference, target_reference_subtitles
        )
    output = transcribe_series(
        audio,
        language=language,
        pipeline=pipeline,
        alignment_json_path=artifact_path,
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
        include_merge_support=audit_include_merge_support,
        terminal_alignment_authority=terminal_alignment_authority,
    )
    return output


def _get_stop_at_idx_for_reference_count(
    pipeline: TranscriptionPipeline,
    audio: AudioSeries,
    reference: Series,
    target_count: int,
) -> int:
    """Get the smallest VAD-block prefix covering the target reference count."""
    blocks = pipeline.plan_blocks(audio)
    covered = 0
    for stop_at_idx, block in enumerate(blocks, start=1):
        covered += sum(
            block.start_ms <= (subtitle.start + subtitle.end) / 2 < block.end_ms
            for subtitle in reference
        )
        if covered >= target_count:
            logger.info(
                f"Selected {stop_at_idx} VAD blocks covering {covered} reference "
                "subtitles."
            )
            return stop_at_idx
    raise ScinoephileError(
        f"The complete VAD plan covers only {covered} reference subtitles; "
        f"cannot reach target {target_count}."
    )


def _load_audio_series(
    audio_path: Path,
    *,
    audio_source_path: Path | None,
    media_path: Path | None,
    stream_index: int | None,
    audio_extraction_mode: AudioExtractionMode = AudioExtractionMode.ORIGINAL,
    media_start_seconds: float,
) -> AudioSeries:
    """Load staged complete audio without supplying subtitle events to ASR."""
    if media_start_seconds < 0.0:
        raise ValueError("media_start_seconds must be non-negative.")
    if audio_source_path is not None and not audio_path.exists():
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        copy2(audio_source_path, audio_path)
    if audio_path.exists():
        return AudioSeries(audio=AudioSegment.from_wav(audio_path), events=[])
    if media_path is None:
        raise ScinoephileError(
            f"Staged audio is missing at {audio_path}; provide media_path."
        )
    audio = AudioSeries.load_audio_from_media(
        media_path, stream_index=stream_index, extraction_mode=audio_extraction_mode
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
    artifact: TranscriptionAlignmentArtifact,
    reference: Series,
    *,
    audit_references: Mapping[str, Series] | None = None,
    include_merge_support: bool = False,
    terminal_alignment_authority: str | None = None,
):
    """Save evaluation artifacts and optionally log a colored alignment."""
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
    timing = evaluate_transcription_timing(artifact, reference)
    subtitle_alignment_groups = Counter(
        f"{len(pair.candidate_indexes)}:{len(pair.reference_indexes)}"
        for pair in timing.pairs
    )
    metrics = {
        "format": "scinoephile-transcription-evaluation",
        "version": 1,
        "processed_blocks": len(artifact.blocks),
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
    json_dir_path = output_dir_path / "json"
    json_dir_path.mkdir(parents=True, exist_ok=True)
    (json_dir_path / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    reference_similarity = None
    if artifact.language in {Language.yue_hans, Language.yue_hant}:
        reference_similarity = CantoneseTimedTokenSimilarity(
            timing_weight=4.0, timing_tolerance_seconds=0.75
        )
    references = audit_references or reference
    (output_dir_path / "audit.md").write_text(
        audit_transcription_alignment(
            artifact,
            references,
            reference_similarity=reference_similarity,
            include_merge_support=include_merge_support,
        ),
        encoding="utf-8",
    )
    if terminal_alignment_authority is not None:
        terminal_alignment = render_transcription_alignment_terminal(
            artifact,
            references,
            authoritative_row_name=terminal_alignment_authority,
            reference_similarity=reference_similarity,
            include_merge_support=include_merge_support,
        )
        logger.info(f"\n{terminal_alignment.rstrip()}")
    logger.info(
        "Aligned transcription evaluation: "
        + ", ".join(f"{name} CER {values['cer']:.3%}" for name, values in cer.items())
    )


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
