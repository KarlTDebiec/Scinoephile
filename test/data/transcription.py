#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Generate and evaluate aligned multi-source transcription test data."""

from __future__ import annotations

import json
from collections import Counter
from logging import getLogger
from pathlib import Path
from shutil import copy2

from scinoephile.analysis.audit.transcription_alignment import (
    audit_transcription_alignment,
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
from scinoephile.lang.transcription.pipeline import (
    TranscriptionPipeline,
    get_transcription_pipeline,
)
from scinoephile.llms.providers.registry import get_provider
from scinoephile.workflows.transcription import transcribe_series

__all__ = ["process_transcription_pipeline"]

logger = getLogger(__name__)


def process_transcription_pipeline(
    title_root_path: Path,
    *,
    reference_path: Path,
    language: Language = Language.yue_hant,
    output_dir_path: Path | None = None,
    audio_dir_path: Path | None = None,
    audio_source_path: Path | None = None,
    media_path: Path | None = None,
    stream_index: int | None = None,
    stop_at_idx: int | None = None,
    target_reference_subtitles: int = 100,
    additional_context: str | None = None,
    timing_settings: SubtitleTimingSettings | None = None,
    diarization_mode: DiarizationMode = DiarizationMode.AUTO,
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
        audio_dir_path: directory containing ``audio.wav`` and ``audio.srt``
        audio_source_path: optional WAV copied into the audio directory
        media_path: optional media from which to extract audio when not staged
        stream_index: optional media audio-stream index
        stop_at_idx: explicit exclusive VAD block index, overriding target count
        target_reference_subtitles: minimum reference subtitles covered by blocks
        additional_context: production consensus prompt context
        timing_settings: reference-free display-timing policy
        diarization_mode: speaker diarization mode
        mlx_audio_token_limit_guard: whether to guard MiMo generation length
        overwrite: whether to regenerate an existing artifact and SRT
    Returns:
        merged transcription series
    """
    if target_reference_subtitles <= 0:
        raise ValueError("target_reference_subtitles must be positive.")
    if output_dir_path is None:
        output_dir_path = title_root_path / "output" / f"{language.code}_transcribe"
    if audio_dir_path is None:
        audio_dir_path = output_dir_path / "audio"
    output_dir_path.mkdir(parents=True, exist_ok=True)
    artifact_path = output_dir_path / "alignment.json"
    transcription_path = output_dir_path / "transcribe.srt"
    reference = Series.load(reference_path)

    if artifact_path.exists() and transcription_path.exists() and not overwrite:
        artifact = TranscriptionAlignmentArtifact.load(artifact_path)
        output = artifact.get_series()
        _save_evaluation(output_dir_path, artifact, reference)
        return output

    audio = _load_audio_series(
        audio_dir_path,
        audio_source_path=audio_source_path,
        media_path=media_path,
        stream_index=stream_index,
    )
    provider = get_provider()
    initial_completion_count = len(provider.completion_metrics)
    pipeline = get_transcription_pipeline(
        language,
        diarization_mode=diarization_mode,
        provider=provider,
        additional_context=additional_context,
        aligned_merge_json_path=output_dir_path / "json" / "aligned_merge.json",
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
    usage_path = output_dir_path / "json" / "llm_usage.json"
    save_chat_completion_metrics_to_json(usage_path, completion_metrics)
    logger.info(format_chat_completion_metrics_report(completion_metrics))
    _save_evaluation(output_dir_path, artifact, reference)
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
    audio_dir_path: Path,
    *,
    audio_source_path: Path | None,
    media_path: Path | None,
    stream_index: int | None,
) -> AudioSeries:
    """Load staged complete audio without supplying subtitle events to ASR."""
    staged_audio_path = audio_dir_path / "audio.wav"
    if audio_source_path is not None and not staged_audio_path.exists():
        audio_dir_path.mkdir(parents=True, exist_ok=True)
        copy2(audio_source_path, staged_audio_path)
        (audio_dir_path / "audio.srt").write_text("", encoding="utf-8")
    if staged_audio_path.exists():
        staged = AudioSeries.load(audio_dir_path)
        return AudioSeries(audio=staged.audio, events=[])
    if media_path is None:
        raise ScinoephileError(
            f"Staged audio is missing at {staged_audio_path}; provide media_path."
        )
    audio = AudioSeries.load_audio_from_media(media_path, stream_index=stream_index)
    audio.save(audio_dir_path)
    return audio


def _save_evaluation(
    output_dir_path: Path, artifact: TranscriptionAlignmentArtifact, reference: Series
):
    """Save standardized reference-only evaluation metrics and audit Markdown."""
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
    (output_dir_path / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir_path / "audit.md").write_text(
        audit_transcription_alignment(artifact, reference), encoding="utf-8"
    )
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
