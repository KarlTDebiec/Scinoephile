#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Generate and evaluate aligned multi-source transcription test data."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict
from hashlib import sha256
from logging import getLogger
from pathlib import Path
from typing import cast

from scinoephile.analysis.audit.transcription.report import (
    audit_transcription_alignment,
    render_transcription_alignment_terminal,
)
from scinoephile.analysis.transcription import AlignmentArtifact, RunManifest
from scinoephile.analysis.transcription.evaluation import (
    TranscriptionEvaluation,
    evaluate_transcription,
)
from scinoephile.analysis.transcription.timing import retime_alignment
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

__all__ = ["process_transcription"]

logger = getLogger(__name__)

_EVALUATION_VERSION = 4
"""Version of evaluation metrics and audit rendering behavior."""


def process_transcription(
    title_root_path: Path,
    *,
    reference_path: Path,
    media_path: Path | None = None,
    stream_index: int | None = None,
    audio_extraction_mode: AudioExtractionMode = AudioExtractionMode.ORIGINAL,
    media_start_seconds: float = 0.0,
    stop_at_idx: int | None = None,
    target_reference_count: int = 100,
    additional_context: str | None = None,
    additional_audit_references: Mapping[str, Series] | None = None,
    reference_name: str = "reference",
    terminal_authority: str | None = None,
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
        target_reference_count: minimum reference subtitles covered by blocks
        additional_context: production consensus prompt context
        additional_audit_references: additional named references used only in audits
        reference_name: audit row name for the primary scoring reference
        terminal_authority: merged or named reference row for ANSI output
        overwrite: whether to regenerate an existing artifact and SRT
    Returns:
        merged transcription series
    """
    if stop_at_idx is None and target_reference_count <= 0:
        raise ValueError("target_reference_count must be positive.")
    output_dir_path = title_root_path / "output" / "yue-Hant_transcribe"
    audio_path = title_root_path / "input" / "yue-Hant_transcribe" / "audio.wav"
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

    existing_artifact, existing_manifest = _load_existing_run(
        artifact_path, run_manifest_path, overwrite
    )
    if existing_artifact is not None:
        existing_output = _get_matching_existing_output(
            existing_artifact, existing_manifest, stop_at_idx
        )
        if existing_output is not None:
            if not transcription_path.exists():
                existing_output.save(transcription_path)
            _save_evaluation(
                output_dir_path,
                existing_artifact,
                reference,
                audit_references=audit_references,
                terminal_authority=terminal_authority,
            )
            return existing_output
        logger.info(
            f"Existing alignment does not match the requested {stop_at_idx}-block "
            "prefix; checking whether it can be extended."
        )

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
            pipeline, audio, reference, target_reference_count
        )
    output, artifact = _transcribe_requested_blocks(
        audio,
        pipeline,
        stop_at_idx,
        artifact_path,
        run_manifest_path,
        existing_artifact,
        existing_manifest,
    )
    output.save(transcription_path)
    completion_metrics = provider.completion_metrics[initial_completion_count:]
    usage_path = json_dir_path / "llm_usage.json"
    save_chat_completion_metrics_to_json(usage_path, completion_metrics)
    logger.info(format_chat_completion_metrics_report(completion_metrics))
    _save_evaluation(
        output_dir_path,
        artifact,
        reference,
        audit_references=audit_references,
        terminal_authority=terminal_authority,
    )
    return output


def _get_matching_existing_output(
    artifact: AlignmentArtifact, manifest: RunManifest | None, stop_at_idx: int | None
) -> Series | None:
    """Get output when an existing artifact covers the requested prefix exactly.

    Arguments:
        artifact: existing portable alignment artifact
        manifest: corresponding validated run manifest, if available
        stop_at_idx: requested exclusive block index, or None for existing output
    Returns:
        existing merged subtitles when the request matches, otherwise None
    """
    if stop_at_idx is None:
        return artifact.get_series()
    processed_block_indexes = tuple(block.index for block in artifact.blocks)
    if manifest is not None and manifest.alignment_sha256 == artifact.sha256:
        processed_block_indexes = tuple(block.index for block in manifest.blocks)
    requested_block_indexes = tuple(range(1, stop_at_idx + 1))
    if processed_block_indexes != requested_block_indexes:
        return None
    return artifact.get_series()


def _load_existing_run(
    artifact_path: Path, run_manifest_path: Path, overwrite: bool
) -> tuple[AlignmentArtifact | None, RunManifest | None]:
    """Load an existing alignment artifact and its valid linked manifest.

    Arguments:
        artifact_path: portable alignment artifact path
        run_manifest_path: compact run manifest path
        overwrite: whether existing output must be ignored
    Returns:
        existing artifact and linked manifest, when available
    """
    if overwrite or not artifact_path.exists():
        return None, None
    artifact = AlignmentArtifact.load(artifact_path)
    if not run_manifest_path.exists():
        return artifact, None
    try:
        manifest = RunManifest.load(run_manifest_path)
    except (OSError, ValueError) as exc:
        logger.warning(f"Ignoring invalid transcription run manifest: {exc}")
        return artifact, None
    if manifest.alignment_sha256 != artifact.sha256:
        return artifact, None
    return artifact, manifest


def _transcribe_requested_blocks(
    audio: AudioSeries,
    pipeline: TranscriptionPipeline,
    stop_at_idx: int,
    artifact_path: Path,
    run_manifest_path: Path,
    existing_artifact: AlignmentArtifact | None,
    existing_manifest: RunManifest | None,
) -> tuple[Series, AlignmentArtifact]:
    """Transcribe a requested prefix, reusing a compatible completed prefix.

    Arguments:
        audio: complete source audio
        pipeline: configured transcription pipeline
        stop_at_idx: requested exclusive block index
        artifact_path: portable alignment artifact output path
        run_manifest_path: compact run manifest output path
        existing_artifact: candidate reusable alignment prefix
        existing_manifest: provenance for the candidate prefix
    Returns:
        merged subtitles and complete alignment artifact
    """
    start_at_idx = 0
    if (
        existing_artifact is not None
        and existing_manifest is not None
        and _is_reusable_prefix(
            pipeline, audio, existing_artifact, existing_manifest, stop_at_idx
        )
    ):
        start_at_idx = len(existing_manifest.blocks)
        logger.info(
            f"Reusing {start_at_idx} completed transcription blocks and processing "
            f"blocks {start_at_idx + 1}-{stop_at_idx}."
        )
    elif existing_artifact is not None:
        logger.info("Existing alignment is not a compatible prefix; regenerating.")

    if not start_at_idx:
        output = transcribe_series(
            audio,
            language=Language.yue_hant,
            pipeline=pipeline,
            alignment_outfile_path=artifact_path,
            run_manifest_outfile_path=run_manifest_path,
            stop_at_idx=stop_at_idx,
        )
        artifact = pipeline.last_alignment_artifact
        if artifact is None:
            raise RuntimeError("Transcription pipeline did not produce an artifact.")
        return output, artifact

    transcribe_series(
        audio,
        language=Language.yue_hant,
        pipeline=pipeline,
        alignment_outfile_path=artifact_path,
        run_manifest_outfile_path=run_manifest_path,
        start_at_idx=start_at_idx,
        stop_at_idx=stop_at_idx,
    )
    suffix_artifact = pipeline.last_alignment_artifact
    suffix_manifest = pipeline.last_run_manifest
    if suffix_artifact is None or suffix_manifest is None:
        raise RuntimeError("Transcription pipeline did not retain resumable outputs.")
    assert existing_artifact is not None
    assert existing_manifest is not None
    artifact, manifest = _combine_run_prefix(
        existing_artifact, existing_manifest, suffix_artifact, suffix_manifest
    )
    pipeline.last_alignment_artifact = artifact
    pipeline.last_run_manifest = manifest
    artifact.save(artifact_path)
    manifest.save(run_manifest_path)
    return artifact.get_series(), artifact


def _combine_run_prefix(
    prefix_artifact: AlignmentArtifact,
    prefix_manifest: RunManifest,
    suffix_artifact: AlignmentArtifact,
    suffix_manifest: RunManifest,
) -> tuple[AlignmentArtifact, RunManifest]:
    """Combine a validated prior prefix with newly processed suffix blocks.

    Arguments:
        prefix_artifact: reusable leading alignment blocks
        prefix_manifest: provenance for the reusable leading blocks
        suffix_artifact: newly generated trailing alignment blocks
        suffix_manifest: provenance for the newly generated trailing blocks
    Returns:
        combined alignment artifact and run manifest
    Raises:
        RuntimeError: if the suffix does not immediately follow the prefix
    """
    prefix_count = len(prefix_manifest.blocks)
    suffix_indexes = tuple(block.index for block in suffix_manifest.blocks)
    expected_suffix_indexes = tuple(
        range(prefix_count + 1, prefix_count + len(suffix_indexes) + 1)
    )
    if suffix_indexes != expected_suffix_indexes:
        raise RuntimeError("Transcription suffix does not immediately follow prefix.")

    subtitle_index = 1
    blocks = []
    for block in (*prefix_artifact.blocks, *suffix_artifact.blocks):
        subtitles = []
        for subtitle in block.subtitles:
            subtitles.append(subtitle.model_copy(update={"index": subtitle_index}))
            subtitle_index += 1
        blocks.append(block.model_copy(update={"subtitles": tuple(subtitles)}))
    artifact = retime_alignment(
        AlignmentArtifact.model_validate(
            {**suffix_artifact.model_dump(mode="python"), "blocks": tuple(blocks)}
        ),
        suffix_artifact.timing,
    )
    manifest = RunManifest.model_validate(
        {
            **suffix_manifest.model_dump(mode="python"),
            "blocks": (*prefix_manifest.blocks, *suffix_manifest.blocks),
            "alignment_sha256": artifact.sha256,
        }
    )
    return artifact, manifest


def _is_reusable_prefix(
    pipeline: TranscriptionPipeline,
    audio: AudioSeries,
    artifact: AlignmentArtifact,
    manifest: RunManifest,
    stop_at_idx: int,
) -> bool:
    """Check whether a completed run is a compatible proper prefix.

    Arguments:
        pipeline: currently configured transcription pipeline
        audio: complete decoded source audio
        artifact: candidate reusable alignment artifact
        manifest: provenance corresponding to the candidate artifact
        stop_at_idx: requested exclusive block index
    Returns:
        whether only the requested suffix needs processing
    """
    prefix_count = len(manifest.blocks)
    if (
        prefix_count == 0
        or prefix_count >= stop_at_idx
        or tuple(block.index for block in manifest.blocks)
        != tuple(range(1, prefix_count + 1))
        or manifest.alignment_sha256 != artifact.sha256
    ):
        return False
    transcribed_indexes = tuple(
        block.index for block in manifest.blocks if block.status == "transcribed"
    )
    if tuple(block.index for block in artifact.blocks) != transcribed_indexes:
        return False

    blocks = pipeline.plan_blocks(audio)
    if (
        stop_at_idx > len(blocks)
        or manifest.language is not pipeline.language
        or artifact.language is not pipeline.language
        or artifact.audio_duration_ms != len(audio.audio)
        or artifact.sources != pipeline.alignment_sources
        or artifact.timing != pipeline.timing_settings
        or manifest.audio_sha256 != sha256(audio.audio.raw_data).hexdigest()
        or manifest.audio_duration_ms != len(audio.audio)
        or manifest.audio_channels != audio.audio.channels
        or manifest.audio_frame_rate != audio.audio.frame_rate
        or manifest.audio_sample_width != audio.audio.sample_width
        or manifest.block_vad_identity != pipeline.block_vad_identity
        or manifest.planned_block_count != len(blocks)
        or manifest.processor != pipeline.processor_identity
    ):
        return False
    for alignment_block in artifact.blocks:
        planned_block = blocks[alignment_block.index - 1]
        if (
            alignment_block.core_start_ms,
            alignment_block.core_end_ms,
            alignment_block.buffered_start_ms,
            alignment_block.buffered_end_ms,
        ) != (
            planned_block.start_ms,
            planned_block.end_ms,
            planned_block.buffered_start_ms,
            planned_block.buffered_end_ms,
        ):
            return False
    return True


def _get_stop_at_idx_for_reference_count(
    pipeline: TranscriptionPipeline,
    audio: AudioSeries,
    reference: Series,
    target_count: int,
) -> int:
    """Get the smallest block prefix covering the target reference count.

    Arguments:
        pipeline: transcription pipeline used to plan blocks
        audio: complete audio used for block planning
        reference: independent reference whose subtitles are counted
        target_count: minimum reference subtitle count to cover
    Returns:
        exclusive block index covering the requested number of subtitles
    Raises:
        ScinoephileError: if the complete block plan does not cover the target
    """
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
    """Load staged complete audio without supplying subtitle events to ASR.

    Arguments:
        audio_path: staged complete-audio WAV path
        media_path: optional media from which to extract missing staged audio
        stream_index: optional media audio-stream index
        audio_extraction_mode: channel preparation used during media extraction
        media_start_seconds: seconds trimmed from extracted media audio
    Returns:
        complete audio without subtitle events
    Raises:
        ScinoephileError: if staged audio cannot be loaded or generated
        ValueError: if the media start time is negative
    """
    if media_start_seconds < 0.0:
        raise ValueError("media_start_seconds must be non-negative.")
    if audio_path.exists():
        return AudioSeries(audio=load_audio_segment(audio_path), events=[])
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
    terminal_authority: str | None = None,
):
    """Save evaluation metrics and readable alignment audits.

    Arguments:
        output_dir_path: transcription output directory
        artifact: aligned multi-source transcription artifact
        reference: independent reference used for metrics
        audit_references: named independent references rendered in the audit
        terminal_authority: optional authoritative row rendered in the terminal
    """
    json_dir_path = output_dir_path / "json"
    json_dir_path.mkdir(parents=True, exist_ok=True)
    metrics_path = json_dir_path / "metrics.json"
    audit_path = output_dir_path / "audit.md"
    evaluation_identity = _get_evaluation_identity(
        artifact, reference, audit_references
    )
    metrics = _load_cached_evaluation(metrics_path, audit_path, evaluation_identity)
    token_similarity = None
    if artifact.language in {Language.yue_hans, Language.yue_hant}:
        token_similarity = YueTokenSimilarity(
            timing_weight=2.0, timing_tolerance_seconds=0.75
        )
    if metrics is None:
        evaluation = evaluate_transcription(artifact, reference)
        cer = {
            name: asdict(character_errors)
            for name, character_errors in evaluation.character_errors.items()
        }
        metrics = {
            "format": "scinoephile-transcription-evaluation",
            "version": _EVALUATION_VERSION,
            "input": evaluation_identity,
            "processed_blocks": len(artifact.blocks),
            "reference_subtitles": evaluation.reference_subtitles,
            "candidate_subtitles": evaluation.candidate_subtitles,
            "cer": cer,
            "timing": _serialize_timing(evaluation),
        }
        metrics_path.write_text(
            json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        audit_path.write_text(
            audit_transcription_alignment(
                artifact,
                audit_references,
                token_similarity=token_similarity,
                include_merge_support=True,
            ),
            encoding="utf-8",
        )
    else:
        logger.info("Reusing unchanged transcription metrics and Markdown audit.")
    cer = cast(dict[str, dict[str, float]], metrics["cer"])
    if terminal_authority is not None:
        terminal_alignment = render_transcription_alignment_terminal(
            artifact,
            audit_references,
            authoritative_row_name=terminal_authority,
            token_similarity=token_similarity,
            include_merge_support=True,
        )
        logger.info(f"\n{terminal_alignment.rstrip()}")
    logger.info(
        "Aligned transcription evaluation: "
        + ", ".join(f"{name} CER {values['cer']:.3%}" for name, values in cer.items())
    )


def _get_evaluation_identity(
    artifact: AlignmentArtifact,
    reference: Series,
    audit_references: Mapping[str, Series],
) -> dict[str, object]:
    """Get the inputs determining saved evaluation and audit output.

    Arguments:
        artifact: aligned multi-source transcription artifact
        reference: independent reference used for metrics
        audit_references: named independent references rendered in the audit
    Returns:
        stable content identity for reusable evaluation output
    """
    return {
        "alignment_sha256": artifact.sha256,
        "reference_sha256": _get_series_sha256(reference),
        "audit_reference_sha256s": {
            name: _get_series_sha256(series)
            for name, series in sorted(audit_references.items())
        },
    }


def _get_series_sha256(series: Series) -> str:
    """Get a stable digest of subtitle content used by evaluation.

    Arguments:
        series: subtitle series to digest
    Returns:
        lowercase hexadecimal SHA-256 digest
    """
    payload = [
        {
            "end": subtitle.end,
            "name": subtitle.name,
            "start": subtitle.start,
            "text": subtitle.text,
        }
        for subtitle in series
    ]
    return sha256(
        json.dumps(
            payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True
        ).encode("utf-8")
    ).hexdigest()


def _load_cached_evaluation(
    metrics_path: Path, audit_path: Path, evaluation_identity: Mapping[str, object]
) -> dict[str, object] | None:
    """Load reusable evaluation metrics when both saved outputs are current.

    Arguments:
        metrics_path: evaluation metrics JSON path
        audit_path: Markdown alignment audit path
        evaluation_identity: expected artifact and reference identity
    Returns:
        parsed metrics when reusable, otherwise None
    """
    if not metrics_path.is_file() or not audit_path.is_file():
        return None
    try:
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    except (OSError, TypeError, ValueError):
        return None
    if (
        not isinstance(metrics, dict)
        or metrics.get("format") != "scinoephile-transcription-evaluation"
        or metrics.get("version") != _EVALUATION_VERSION
        or metrics.get("input") != evaluation_identity
        or not isinstance(metrics.get("cer"), dict)
    ):
        return None
    return metrics


def _serialize_timing(evaluation: TranscriptionEvaluation) -> dict[str, object]:
    """Serialize timing metrics from one transcription evaluation.

    Arguments:
        evaluation: structured transcription evaluation
    Returns:
        JSON-compatible timing metrics
    """
    timing = evaluation.timing
    return {
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
        "candidate_to_reference_group_counts": (
            timing.candidate_to_reference_group_counts
        ),
    }
