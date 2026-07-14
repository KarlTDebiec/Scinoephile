#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Functions for transcribing Yue subtitles from Zho references.

This module centralizes the multi-step transcription pipeline used by test data
generation scripts, so path conventions and stage outputs remain consistent.
"""

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
from scinoephile.lang.review.guided import get_guided_reviewer
from scinoephile.lang.review.pairwise import get_pairwise_reviewer
from scinoephile.lang.transcription.guided import get_guided_transcriber
from scinoephile.lang.translation.gap import get_gap_translator
from scinoephile.workflows.review import review_series_guided, review_series_pairwise
from scinoephile.workflows.transcription import transcribe_series_guided
from scinoephile.workflows.translation import translate_series_gaps

__all__ = ["process_yue_hans_transcription"]

logger = getLogger(__name__)


def process_yue_hans_transcription(  # noqa: PLR0912, PLR0915
    title_root_path: Path,
    zho_path: Path,
    *,
    name: str = "Yue Hans transcription",
    reference_path: Path,
    output_dir_path: Path | None = None,
    audio_path: Path | None = None,
    media_path: Path | None = None,
    stream_index: int | None = None,
    overwrite_srt: bool = False,
    transcriber_kw: dict[str, Any] | None = None,
    pairwise_reviewer_kw: dict[str, Any] | None = None,
    translator_kw: dict[str, Any] | None = None,
    guided_reviewer_kw: dict[str, Any] | None = None,
) -> Series:
    """Process yue-Hans transcription through review/translation stages.

    Stages:
    - Audio staging from a Zho Hans reference series
    - Transcription (Yue from Zho)
    - Pairwise review
    - Translation
    - Guided review

    Arguments:
        title_root_path: title root directory
        zho_path: Zho reference series path used for audio staging and as the
          reference language during transcription/review/translation
        name: label printed above CER summaries
        reference_path: reference series path used to compute CER after each stage
        output_dir_path: directory where pipeline outputs are written; defaults to
          `title_root_path/output/yue-Hans_transcribe`
        audio_path: path to the staged audio wav file; defaults to
          `title_root_path/output/yue-Hans_transcribe/audio/audio.wav`
        media_path: optional media path used to generate `audio_path` if missing
        stream_index: media stream index of audio stream used when generating audio,
          or None to use the first audio stream
        overwrite_srt: whether to overwrite subtitle outputs
        transcriber_kw: additional keyword arguments for get_guided_transcriber
        pairwise_reviewer_kw: additional keyword arguments for get_pairwise_reviewer
        translator_kw: additional keyword arguments for get_gap_translator
        guided_reviewer_kw: additional keyword arguments for
          get_guided_reviewer
    Returns:
        final guided-reviewed series
    """
    output_dir = title_root_path / "output"
    yue_hans_transcribe_dir_path = (
        output_dir / "yue-Hans_transcribe"
        if output_dir_path is None
        else output_dir_path
    )
    yue_hans_transcribe_dir_path.mkdir(parents=True, exist_ok=True)
    reference = Series.load(reference_path)

    device = get_torch_device()
    test_case_dir_path = yue_hans_transcribe_dir_path / "lang/yue_zho"

    # Ensure test-case directories exist (some constructors validate as "input dirs")
    transcription_test_case_dir_path = test_case_dir_path / "transcription"
    (transcription_test_case_dir_path / "delineation").mkdir(
        parents=True, exist_ok=True
    )
    (transcription_test_case_dir_path / "punctuation").mkdir(
        parents=True, exist_ok=True
    )
    (test_case_dir_path / "pairwise_review").mkdir(parents=True, exist_ok=True)
    (test_case_dir_path / "gap_translation").mkdir(parents=True, exist_ok=True)
    (test_case_dir_path / "guided_review").mkdir(parents=True, exist_ok=True)

    # Stage audio
    if audio_path is None:
        audio_path = output_dir / "yue-Hans_transcribe/audio/audio.wav"
    audio_dir_path = audio_path.parent
    audio_dir_path.mkdir(parents=True, exist_ok=True)
    expected_audio_path = audio_dir_path / "audio.wav"
    if audio_path.exists() and audio_path != expected_audio_path:
        if not expected_audio_path.exists() or overwrite_srt:
            copy2(audio_path, expected_audio_path)

    zho = Series.load(zho_path)
    audio_srt_path = audio_dir_path / "audio.srt"
    if overwrite_srt or not audio_srt_path.exists():
        zho.save(audio_srt_path)

    if not expected_audio_path.exists():
        if media_path is None:
            raise ScinoephileError(
                "Staged audio is missing. Provide `media_path` to generate it, or "
                f"stage {expected_audio_path} manually."
            )
        yue_hans_audio = AudioSeries.load_from_media(
            media_path=media_path,
            subtitle_path=audio_srt_path,
            stream_index=stream_index,
        )
        yue_hans_audio.save(audio_dir_path)
    yue_hans_audio = AudioSeries.load(audio_dir_path)

    # Transcribe
    transcribe_path = yue_hans_transcribe_dir_path / "transcribe.srt"
    if transcribe_path.exists() and not overwrite_srt:
        transcribe = Series.load(transcribe_path)
    else:
        if transcriber_kw is None:
            transcriber_kw = {}
        transcriber_kw.setdefault(
            "test_case_dir_path",
            transcription_test_case_dir_path,
        )
        transcriber = get_guided_transcriber(
            Language.yue_hans,
            Language.zho_hans,
            **transcriber_kw,
        )
        transcribe = transcribe_series_guided(
            yue_hans_audio,
            zho,
            language=Language.yue_hans,
            reference_language=Language.zho_hans,
            transcriber=transcriber,
        )
        transcribe.save(transcribe_path, exist_ok=True)

    if reference is not None:
        print(f"{name} — transcription CER:")
        print(SeriesCER(reference, transcribe))

    # Pairwise review
    pairwise_review_path = yue_hans_transcribe_dir_path / "transcribe_review.srt"
    if pairwise_review_path.exists() and not overwrite_srt:
        pairwise_review = Series.load(pairwise_review_path)
    else:
        # Detach from any non-serializable extras created by the transcriber stage
        transcribe = Series(
            events=[
                Series.event_class(**event.as_dict()) for event in transcribe.events
            ]
        )
        if pairwise_reviewer_kw is None:
            pairwise_reviewer_kw = {}
        pairwise_reviewer_kw.setdefault(
            "test_case_path",
            test_case_dir_path / "pairwise_review" / f"{device}.json",
        )
        pairwise_reviewer_kw.setdefault("auto_verify", True)
        pairwise_reviewer = get_pairwise_reviewer(
            Language.yue_hans,
            Language.zho_hans,
            **pairwise_reviewer_kw,
        )
        pairwise_review = review_series_pairwise(
            transcribe,
            zho,
            reviewer=pairwise_reviewer,
        )
        pairwise_review.save(pairwise_review_path, exist_ok=True)

    if reference is not None:
        print(f"{name} — transcription → pairwise review CER:")
        print(SeriesCER(reference, pairwise_review))

    # Translate
    translate_path = yue_hans_transcribe_dir_path / "transcribe_review_translate.srt"
    if translate_path.exists() and not overwrite_srt:
        translate = Series.load(translate_path)
    else:
        if translator_kw is None:
            translator_kw = {}
        translator_kw.setdefault(
            "test_case_path",
            test_case_dir_path / "gap_translation" / f"{device}.json",
        )
        translator_kw.setdefault("auto_verify", True)
        translator = get_gap_translator(
            Language.zho_hans, Language.yue_hans, **translator_kw
        )
        translate = translate_series_gaps(
            zho,
            pairwise_review,
            source_language=Language.zho_hans,
            target_language=Language.yue_hans,
            translator=translator,
        )
        translate.save(translate_path, exist_ok=True)

    if reference is not None:
        print(f"{name} — transcription → pairwise review → translate CER:")
        print(SeriesCER(reference, translate))

    # Guided review
    guided_review_path = (
        yue_hans_transcribe_dir_path / "transcribe_review_translate_guided_review.srt"
    )
    if guided_review_path.exists() and not overwrite_srt:
        guided_review = Series.load(guided_review_path)
    else:
        if guided_reviewer_kw is None:
            guided_reviewer_kw = {}
        guided_reviewer_kw.setdefault(
            "test_case_path",
            test_case_dir_path / "guided_review" / f"{device}.json",
        )
        guided_reviewer_kw.setdefault("auto_verify", True)
        reviewer = get_guided_reviewer(
            Language.yue_hans,
            Language.zho_hans,
            **guided_reviewer_kw,
        )
        guided_review = review_series_guided(
            translate,
            zho,
            reviewer=reviewer,
        )
        guided_review.save(guided_review_path, exist_ok=True)

    if reference is not None:
        print(f"{name} — transcription → pairwise review → translate → review CER:")
        print(SeriesCER(reference, guided_review))

    logger.info(f"Saved Yue transcription outputs under {yue_hans_transcribe_dir_path}")
    return guided_review
