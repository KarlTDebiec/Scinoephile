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
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.transcription.guided import DEFAULT_SPECS
from scinoephile.workflows.helpers import resolve_language
from scinoephile.workflows.review import review_series_guided
from scinoephile.workflows.transcription import transcribe_series_guided
from scinoephile.workflows.translation import translate_series_gaps

from .helpers import load_or_clean_series

__all__ = [
    "get_reference_for_guide_blocks",
    "process_transcription",
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
    output_dir_path: Path | None = None,
    audio_source_path: Path | None = None,
    media_path: Path | None = None,
    stream_index: int | None = None,
    stop_at_idx: int | None = None,
    transcription_kw: dict[str, Any] | None = None,
    reviewer_kw: dict[str, Any] | None = None,
    translator_kw: dict[str, Any] | None = None,
    overwrite: bool = False,
) -> Series:
    """Generate, clean, review, and gap-translate a guided transcription.

    Arguments:
        title_root_path: title root directory
        guide_path: guide subtitle path used for alignment, review, and translation
        reference_path: expected transcription used only to compute CER
        language: explicit transcription language, or None to detect it from the
          evaluation reference
        guide_language: explicit guide subtitle language, or None to detect it
        output_dir_path: directory where pipeline outputs are written; defaults to
          `title_root_path/output/{language.code}_transcribe`
        audio_source_path: optional existing wav file to copy into the output
        media_path: optional media path used to generate staged audio if missing
        stream_index: media stream index used when generating staged audio, or None
          to use the first audio stream
        stop_at_idx: exclusive block index at which to stop LLM processing
        transcription_kw: additional keyword arguments for
          `transcribe_series_guided`
        reviewer_kw: additional keyword arguments for `review_series_guided`
        translator_kw: additional keyword arguments for `translate_series_gaps`
        overwrite: whether to overwrite existing stage outputs
    Returns:
        cleaned, reviewed, and gap-translated transcription
    Raises:
        ScinoephileError: if staged audio is missing and cannot be generated
    """
    reference = Series.load(reference_path)
    guide = Series.load(guide_path)
    language = resolve_language(reference, language)
    guide_language = resolve_language(guide, guide_language)

    if output_dir_path is None:
        output_dir_path = title_root_path / "output" / f"{language.code}_transcribe"
    output_dir_path.mkdir(parents=True, exist_ok=True)

    evaluation_reference = get_reference_for_guide_blocks(
        reference,
        guide,
        stop_at_idx,
    )

    # Stage guide subtitles and audio under the transcription output
    audio = _stage_audio_series(
        guide,
        output_dir_path,
        audio_source_path=audio_source_path,
        media_path=media_path,
        stream_index=stream_index,
        overwrite=overwrite,
    )

    # Transcribe, delineate, and punctuate
    transcribe_path = output_dir_path / "transcribe.srt"
    transcribe = _load_or_transcribe_series_guided(
        audio,
        guide,
        transcribe_path,
        language,
        guide_language,
        stop_at_idx=stop_at_idx,
        transcription_kw=transcription_kw,
        overwrite=overwrite,
    )
    logger.info(
        f"{language.code} transcription CER after transcription:\n"
        f"{SeriesCER(evaluation_reference, transcribe)}"
    )

    # Clean transcription
    clean_path = output_dir_path / "transcribe_clean.srt"
    informational_detected_language = None
    if language is Language.yue_hans:
        informational_detected_language = Language.zho_hans
    elif language is Language.yue_hant:
        informational_detected_language = Language.zho_hant
    cleaned = load_or_clean_series(
        transcribe,
        clean_path,
        language,
        overwrite,
        informational_detected_language=informational_detected_language,
    )
    logger.info(
        f"{language.code} transcription CER after cleaning:\n"
        f"{SeriesCER(evaluation_reference, cleaned)}"
    )

    # Review cleaned transcription using guide subtitles
    review_path = output_dir_path / "transcribe_clean_review.srt"
    reviewed = _load_or_review_series_guided(
        cleaned,
        guide,
        review_path,
        language,
        guide_language,
        stop_at_idx=stop_at_idx,
        reviewer_kw=reviewer_kw,
        overwrite=overwrite,
    )
    logger.info(
        f"{language.code} transcription CER after review:\n"
        f"{SeriesCER(evaluation_reference, reviewed)}"
    )

    # Fill gaps in reviewed transcription using guide subtitles
    translate_path = output_dir_path / "transcribe_clean_review_translate.srt"
    translated = _load_or_translate_series_gaps(
        guide,
        reviewed,
        translate_path,
        guide_language,
        language,
        stop_at_idx=stop_at_idx,
        translator_kw=translator_kw,
        overwrite=overwrite,
    )
    logger.info(
        f"{language.code} transcription CER after gap translation:\n"
        f"{SeriesCER(evaluation_reference, translated)}"
    )
    logger.info(f"Saved transcription output under {output_dir_path}")
    return translated


def _load_or_review_series_guided(
    target: Series,
    guide: Series,
    output_path: Path,
    language: Language,
    guide_language: Language,
    *,
    stop_at_idx: int | None = None,
    reviewer_kw: dict[str, Any] | None = None,
    overwrite: bool = False,
) -> Series:
    """Load or create a guide-reviewed subtitle series.

    Arguments:
        target: target subtitle series to review
        guide: guide subtitle series
        output_path: reviewed subtitle output path
        language: target subtitle language
        guide_language: guide language
        stop_at_idx: exclusive review block index at which to stop processing
        reviewer_kw: additional keyword arguments for `review_series_guided`
        overwrite: whether to overwrite an existing output
    Returns:
        guide-reviewed subtitle series
    """
    if output_path.exists() and not overwrite:
        return Series.load(output_path)

    reviewer_kw = dict(reviewer_kw or {})
    language_pair_name = f"{language.language}_{guide_language.language}"
    reviewer_kw.setdefault(
        "test_case_path",
        output_path.parent
        / "lang"
        / language_pair_name
        / "guided_review"
        / f"{get_torch_device()}.json",
    )
    reviewed = review_series_guided(
        target,
        guide,
        language=language,
        guide_language=guide_language,
        stop_at_idx=stop_at_idx,
        **reviewer_kw,
    )
    reviewed.save(output_path)
    return reviewed


def _load_or_transcribe_series_guided(
    audio: AudioSeries,
    guide: Series,
    output_path: Path,
    language: Language,
    guide_language: Language,
    *,
    stop_at_idx: int | None = None,
    transcription_kw: dict[str, Any] | None = None,
    overwrite: bool = False,
) -> Series:
    """Load or create a guided transcription.

    Arguments:
        audio: audio series to transcribe
        guide: guide subtitle series
        output_path: transcription output path
        language: transcription language
        guide_language: guide subtitle language
        stop_at_idx: exclusive block index at which to stop processing
        transcription_kw: additional keyword arguments for
          `transcribe_series_guided`
        overwrite: whether to overwrite an existing output
    Returns:
        guided transcription
    """
    if output_path.exists() and not overwrite:
        return Series.load(output_path)

    transcription_kw = dict(transcription_kw or {})
    spec = DEFAULT_SPECS.get((language, guide_language))
    if spec is not None:
        transcription_kw.setdefault(
            "test_case_dir_path",
            output_path.parent / spec.test_case_dir_path,
        )
    audio_transcription = transcribe_series_guided(
        audio,
        guide,
        language=language,
        reference_language=guide_language,
        stop_at_idx=stop_at_idx,
        **transcription_kw,
    )
    transcription = Series(
        events=[Subtitle(**event.as_dict()) for event in audio_transcription]
    )
    transcription.save(output_path)
    return transcription


def _load_or_translate_series_gaps(
    source: Series,
    target: Series,
    output_path: Path,
    source_language: Language,
    target_language: Language,
    *,
    stop_at_idx: int | None = None,
    translator_kw: dict[str, Any] | None = None,
    overwrite: bool = False,
) -> Series:
    """Load or create a gap-translated subtitle series.

    Arguments:
        source: source-language guide subtitle series
        target: target-language gapped subtitle series
        output_path: translated subtitle output path
        source_language: source subtitle language
        target_language: target subtitle language
        stop_at_idx: exclusive block index at which to stop processing
        translator_kw: additional keyword arguments for `translate_series_gaps`
        overwrite: whether to overwrite an existing output
    Returns:
        gap-translated subtitle series
    """
    if output_path.exists() and not overwrite:
        return Series.load(output_path)

    translator_kw = dict(translator_kw or {})
    language_pair_name = f"{target_language.language}_{source_language.language}"
    translator_kw.setdefault(
        "test_case_path",
        output_path.parent
        / "lang"
        / language_pair_name
        / "gap_translation"
        / f"{get_torch_device()}.json",
    )
    translated = translate_series_gaps(
        source,
        target,
        source_language=source_language,
        target_language=target_language,
        stop_at_idx=stop_at_idx,
        **translator_kw,
    )
    translated.save(output_path)
    return translated


def _stage_audio_series(
    guide: Series,
    output_dir_path: Path,
    *,
    audio_source_path: Path | None,
    media_path: Path | None,
    stream_index: int | None,
    overwrite: bool,
) -> AudioSeries:
    """Stage and load guide-aligned audio for transcription.

    Arguments:
        guide: guide subtitles used to segment audio
        output_dir_path: transcription output directory
        audio_source_path: optional existing wav file to stage
        media_path: optional media path from which to extract audio
        stream_index: audio stream index, or None to use the first stream
        overwrite: whether to overwrite staged inputs
    Returns:
        staged guide-aligned audio series
    Raises:
        ScinoephileError: if staged audio is missing and cannot be generated
    """
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
    return AudioSeries.load(audio_dir_path)
