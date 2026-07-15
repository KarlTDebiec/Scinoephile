#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Functions for generating reference-guided transcription test data."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path
from shutil import copy2
from typing import Any

from scinoephile.analysis.character_error_rate import SeriesCER
from scinoephile.audio.subtitles import AudioSeries
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.ml import get_torch_device
from scinoephile.core.subtitles import Series
from scinoephile.lang.transcription.guided import DEFAULT_SPECS
from scinoephile.workflows.helpers import resolve_language
from scinoephile.workflows.review import review_series_guided
from scinoephile.workflows.transcription import transcribe_series_guided

__all__ = [
    "get_reference_for_guide_blocks",
    "process_transcription",
    "process_transcription_guided_review",
]

logger = getLogger(__name__)


def get_reference_for_guide_blocks(
    reference: Series,
    guide: Series,
    stop_at_idx: int | None,
) -> Series:
    """Limit an evaluation reference to a prefix of guide blocks.

    Arguments:
        reference: evaluation reference to limit
        guide: guide whose block boundaries define the processed prefix
        stop_at_idx: exclusive guide block index, or None for the full reference
    Returns:
        reference covering only the processed guide block prefix
    Raises:
        ValueError: if stop_at_idx is negative
    """
    if stop_at_idx is None:
        return reference
    if stop_at_idx < 0:
        raise ValueError("stop_at_idx must be greater than or equal to 0")

    guide_blocks = guide.blocks[:stop_at_idx]
    if not guide_blocks:
        return type(reference)()
    end_time = guide_blocks[-1].events[-1].end
    return type(reference)(
        events=[event for event in reference if event.start < end_time]
    )


def process_transcription(
    title_root_path: Path,
    guide_path: Path,
    *,
    reference_path: Path,
    language: Language | None = None,
    guide_language: Language | None = None,
    name: str | None = None,
    output_dir_path: Path | None = None,
    transcribe_path: Path | None = None,
    audio_source_path: Path | None = None,
    media_path: Path | None = None,
    stream_index: int | None = None,
    stop_at_idx: int | None = None,
    overwrite: bool = False,
    transcription_kw: dict[str, Any] | None = None,
) -> Series:
    """Generate an initial transcription and report its CER.

    Arguments:
        title_root_path: title root directory
        guide_path: guide subtitle path used for audio staging and alignment
        reference_path: expected transcription used only to compute CER
        language: explicit transcription language, or None to detect it from the
          evaluation reference
        guide_language: explicit guide subtitle language, or None to detect it
        name: label included in the CER log
        output_dir_path: directory where pipeline outputs are written; defaults to
          `title_root_path/output/{language.code}_transcribe`
        transcribe_path: transcription output path; defaults to
          `output_dir_path/transcribe.srt`
        audio_source_path: optional existing wav file to copy into the output
        media_path: optional media path used to generate staged audio if missing
        stream_index: media stream index used when generating staged audio, or None
          to use the first audio stream
        stop_at_idx: exclusive block index at which to stop processing
        overwrite: whether to overwrite staged and transcribed subtitles
        transcription_kw: additional keyword arguments for
          `transcribe_series_guided`
    Returns:
        initial transcribed series after delineation and punctuation
    Raises:
        ScinoephileError: if staged audio is missing and cannot be generated
    """
    reference = Series.load(reference_path)
    guide = Series.load(guide_path)
    language = resolve_language(reference, language)
    guide_language = resolve_language(guide, guide_language)

    if name is None:
        name = f"{language.code} transcription"
    if output_dir_path is None:
        output_dir_path = title_root_path / "output" / f"{language.code}_transcribe"
    output_dir_path.mkdir(parents=True, exist_ok=True)
    if transcribe_path is None:
        transcribe_path = output_dir_path / "transcribe.srt"

    # Stage guide subtitles and audio under the transcription output
    audio_dir_path = output_dir_path / "audio"
    audio_dir_path.mkdir(parents=True, exist_ok=True)
    staged_audio_path = audio_dir_path / "audio.wav"
    if audio_source_path is not None and audio_source_path != staged_audio_path:
        if overwrite or not staged_audio_path.exists():
            copy2(audio_source_path, staged_audio_path)
    audio_srt_path = audio_dir_path / "audio.srt"
    if overwrite or not audio_srt_path.exists():
        guide.save(audio_srt_path)

    if not staged_audio_path.exists():
        if media_path is None:
            raise ScinoephileError(
                "Staged audio is missing. Provide `audio_source_path` or "
                f"`media_path`, or stage {staged_audio_path} manually."
            )
        audio = AudioSeries.load_from_media(
            media_path=media_path,
            subtitle_path=audio_srt_path,
            stream_index=stream_index,
        )
        audio.save(audio_dir_path)
    audio = AudioSeries.load(audio_dir_path)

    # Transcribe, delineate, and punctuate
    if transcribe_path.exists() and not overwrite:
        transcribe = Series.load(transcribe_path)
    else:
        transcription_kw = dict(transcription_kw or {})
        spec = DEFAULT_SPECS.get((language, guide_language))
        if spec is not None:
            transcription_kw.setdefault(
                "test_case_dir_path",
                output_dir_path / spec.test_case_dir_path,
            )
        transcribe = transcribe_series_guided(
            audio,
            guide,
            language=language,
            reference_language=guide_language,
            stop_at_idx=stop_at_idx,
            **transcription_kw,
        )
        transcribe.save(transcribe_path, exist_ok=True)

    evaluation_reference = get_reference_for_guide_blocks(
        reference,
        guide,
        stop_at_idx,
    )

    logger.info(f"{name} CER:\n{SeriesCER(evaluation_reference, transcribe)}")
    logger.info(f"Saved transcription output under {output_dir_path}")
    return transcribe


def process_transcription_guided_review(
    transcribe_path: Path,
    guide_path: Path,
    *,
    language: Language,
    guide_language: Language,
    reference_path: Path,
    name: str | None = None,
    guided_review_path: Path | None = None,
    stop_at_idx: int | None = None,
    overwrite: bool = False,
    reviewer_kw: dict[str, Any] | None = None,
) -> Series:
    """Review a completed transcription in guide-aligned blocks.

    This is a separate downstream stage from initial transcription, delineation,
    and punctuation.

    Arguments:
        transcribe_path: initial transcription output to review
        guide_path: guide subtitles providing block-level context
        language: transcription language
        guide_language: guide subtitle language
        reference_path: expected transcription used only to compute CER
        name: label included in the CER log
        guided_review_path: guided-review output path; defaults to the transcription
          filename with `_guided_review` appended to its stem
        stop_at_idx: exclusive review block index at which to stop processing
        overwrite: whether to overwrite an existing guided-review output
        reviewer_kw: additional keyword arguments for `review_series_guided`
    Returns:
        guided block-reviewed transcription
    """
    if name is None:
        name = f"{language.code} transcription guided review"
    if guided_review_path is None:
        guided_review_path = transcribe_path.with_name(
            f"{transcribe_path.stem}_guided_review{transcribe_path.suffix}"
        )

    reference = Series.load(reference_path)
    guide = Series.load(guide_path)
    if guided_review_path.exists() and not overwrite:
        guided_review = Series.load(guided_review_path)
    else:
        transcribe = Series.load(transcribe_path)
        reviewer_kw = dict(reviewer_kw or {})
        language_pair_name = f"{language.language}_{guide_language.language}"
        reviewer_kw.setdefault(
            "test_case_path",
            transcribe_path.parent
            / "lang"
            / language_pair_name
            / "guided_review"
            / f"{get_torch_device()}.json",
        )
        guided_review = review_series_guided(
            transcribe,
            guide,
            language=language,
            guide_language=guide_language,
            stop_at_idx=stop_at_idx,
            **reviewer_kw,
        )
        guided_review.save(guided_review_path, exist_ok=True)

    evaluation_reference = get_reference_for_guide_blocks(
        reference,
        guide,
        stop_at_idx,
    )
    logger.info(f"{name} CER:\n{SeriesCER(evaluation_reference, guided_review)}")
    logger.info(f"Saved guided-review output to {guided_review_path}")
    return guided_review
