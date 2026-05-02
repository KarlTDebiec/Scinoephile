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
from scinoephile.core import ScinoephileError
from scinoephile.core.ml import get_torch_device
from scinoephile.core.subtitles import Series
from scinoephile.multilang.yue_zho import (
    get_yue_block_reviewed_vs_zho,
    get_yue_line_reviewed_vs_zho,
    get_yue_transcribed_vs_zho,
    get_yue_translated_vs_zho,
)
from scinoephile.multilang.yue_zho.block_review import get_yue_vs_zho_block_reviewer
from scinoephile.multilang.yue_zho.line_review import get_yue_vs_zho_line_reviewer
from scinoephile.multilang.yue_zho.transcription import (
    get_yue_vs_zho_transcriber,
)
from scinoephile.multilang.yue_zho.translation import get_yue_vs_zho_translator

__all__ = [
    "process_yue_hans_transcription",
]

logger = getLogger(__name__)


def process_yue_hans_transcription(  # noqa: PLR0912, PLR0915
    title_root: Path,
    zho_path: Path,
    *,
    name: str = "Yue Hans transcription",
    reference_path: Path,
    output_dir_path: Path | None = None,
    audio_path: Path | None = None,
    media_path: Path | None = None,
    stream_index: int = 0,
    overwrite_srt: bool = False,
    transcriber_kw: dict[str, Any] | None = None,
    line_reviewer_kw: dict[str, Any] | None = None,
    translator_kw: dict[str, Any] | None = None,
    block_reviewer_kw: dict[str, Any] | None = None,
) -> Series:
    """Process 简体粤文 transcription through review/translation stages.

    Stages:
    - Audio staging from a Zho Hans reference series
    - Transcription (Yue from Zho)
    - Line review
    - Translation
    - Block review

    Arguments:
        title_root: title root directory
        zho_path: Zho reference series path used for audio staging and as the
          reference language during transcription/review/translation
        name: label printed above CER summaries
        reference_path: reference series path used to compute CER after each stage
        output_dir_path: directory where pipeline outputs are written; defaults to
          `title_root/output/yue-Hans_transcribe`
        audio_path: path to the staged audio wav file; defaults to
          `title_root/output/yue-Hans_transcribe/audio/audio.wav`
        media_path: optional media path used to generate `audio_path` if missing
        stream_index: audio stream index in media used when generating audio
        overwrite_srt: whether to overwrite subtitle outputs
        transcriber_kw: additional keyword arguments for get_yue_vs_zho_transcriber
        line_reviewer_kw: additional keyword arguments for get_yue_vs_zho_line_reviewer
        translator_kw: additional keyword arguments for get_yue_vs_zho_translator
        block_reviewer_kw: additional keyword arguments for
          get_yue_vs_zho_block_reviewer
    Returns:
        final block-reviewed series
    """
    output_dir = title_root / "output"
    yue_hans_transcribe_dir_path = (
        output_dir / "yue-Hans_transcribe"
        if output_dir_path is None
        else output_dir_path
    )
    yue_hans_transcribe_dir_path.mkdir(parents=True, exist_ok=True)
    reference = Series.load(reference_path)

    device = get_torch_device()
    test_case_dir_path = yue_hans_transcribe_dir_path / "multilang" / "yue_zho"

    # Ensure test-case directories exist (some constructors validate as "input dirs")
    transcription_test_case_dir_path = test_case_dir_path / "transcription"
    (transcription_test_case_dir_path / "deliniation").mkdir(
        parents=True, exist_ok=True
    )
    (transcription_test_case_dir_path / "punctuation").mkdir(
        parents=True, exist_ok=True
    )
    (test_case_dir_path / "line_review").mkdir(parents=True, exist_ok=True)
    (test_case_dir_path / "translation").mkdir(parents=True, exist_ok=True)
    (test_case_dir_path / "block_review").mkdir(parents=True, exist_ok=True)

    # Stage audio
    if audio_path is None:
        audio_path = output_dir / "yue-Hans_transcribe" / "audio" / "audio.wav"
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
            "test_case_directory_path",
            transcription_test_case_dir_path,
        )
        transcriber = get_yue_vs_zho_transcriber(
            **transcriber_kw,
        )
        transcribe = get_yue_transcribed_vs_zho(
            yue_hans_audio, zho, transcriber=transcriber
        )
        transcribe.save(transcribe_path, exist_ok=True)

    if reference is not None:
        print(f"{name} — transcription CER:")
        print(SeriesCER(reference, transcribe))

    # Review (line-by-line)
    line_review_path = yue_hans_transcribe_dir_path / "transcribe_review.srt"
    if line_review_path.exists() and not overwrite_srt:
        line_review = Series.load(line_review_path)
    else:
        # Detach from any non-serializable extras created by the transcriber stage
        transcribe = Series(
            events=[
                Series.event_class(**event.as_dict()) for event in transcribe.events
            ]
        )
        if line_reviewer_kw is None:
            line_reviewer_kw = {}
        line_reviewer_kw.setdefault(
            "test_case_path",
            test_case_dir_path / "line_review" / f"{device}.json",
        )
        line_reviewer_kw.setdefault("auto_verify", True)
        line_reviewer = get_yue_vs_zho_line_reviewer(**line_reviewer_kw)
        line_review = get_yue_line_reviewed_vs_zho(
            transcribe, zho, line_reviewer=line_reviewer
        )
        line_review.save(line_review_path, exist_ok=True)

    if reference is not None:
        print(f"{name} — transcription → line review CER:")
        print(SeriesCER(reference, line_review))

    # Translate
    translate_path = yue_hans_transcribe_dir_path / "transcribe_review_translate.srt"
    if translate_path.exists() and not overwrite_srt:
        translate = Series.load(translate_path)
    else:
        if translator_kw is None:
            translator_kw = {}
        translator_kw.setdefault(
            "test_case_path",
            test_case_dir_path / "translation" / f"{device}.json",
        )
        translator_kw.setdefault("auto_verify", True)
        translator = get_yue_vs_zho_translator(**translator_kw)
        translate = get_yue_translated_vs_zho(line_review, zho, translator=translator)
        translate.save(translate_path, exist_ok=True)

    if reference is not None:
        print(f"{name} — transcription → line review → translate CER:")
        print(SeriesCER(reference, translate))

    # Review (block-by-block)
    block_review_path = (
        yue_hans_transcribe_dir_path / "transcribe_review_translate_block_review.srt"
    )
    if block_review_path.exists() and not overwrite_srt:
        block_review = Series.load(block_review_path)
    else:
        if block_reviewer_kw is None:
            block_reviewer_kw = {}
        block_reviewer_kw.setdefault(
            "test_case_path",
            test_case_dir_path / "block_review" / f"{device}.json",
        )
        block_reviewer_kw.setdefault("auto_verify", True)
        reviewer = get_yue_vs_zho_block_reviewer(**block_reviewer_kw)
        block_review = get_yue_block_reviewed_vs_zho(translate, zho, reviewer=reviewer)
        block_review.save(block_review_path, exist_ok=True)

    if reference is not None:
        print(f"{name} — transcription → line review → translate → block review CER:")
        print(SeriesCER(reference, block_review))

    logger.info(f"Saved Yue transcription outputs under {yue_hans_transcribe_dir_path}")
    return block_review
