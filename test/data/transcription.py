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
from scinoephile.core.subtitles import Series
from scinoephile.lang.transcription.guided import DEFAULT_SPECS
from scinoephile.workflows.transcription import transcribe_series_guided

__all__ = ["process_transcription"]

logger = getLogger(__name__)


def process_transcription(
    title_root_path: Path,
    guide_path: Path,
    *,
    language: Language,
    guide_language: Language,
    reference_path: Path,
    name: str | None = None,
    output_dir_path: Path | None = None,
    audio_source_path: Path | None = None,
    media_path: Path | None = None,
    stream_index: int | None = None,
    overwrite_srt: bool = False,
    transcription_kw: dict[str, Any] | None = None,
) -> Series:
    """Generate an initial transcription and report its CER.

    Arguments:
        title_root_path: title root directory
        guide_path: guide subtitle path used for audio staging and alignment
        language: transcription language
        guide_language: guide subtitle language
        reference_path: expected transcription used only to compute CER
        name: label included in the CER log
        output_dir_path: directory where pipeline outputs are written; defaults to
          `title_root_path/output/{language.tag}_transcribe`
        audio_source_path: optional existing wav file to copy into the output
        media_path: optional media path used to generate staged audio if missing
        stream_index: media stream index used when generating staged audio, or None
          to use the first audio stream
        overwrite_srt: whether to overwrite staged and transcribed subtitles
        transcription_kw: additional keyword arguments for
          `transcribe_series_guided`
    Returns:
        initial transcribed series after delineation and punctuation
    Raises:
        ScinoephileError: if staged audio is missing and cannot be generated
    """
    if name is None:
        name = f"{language.tag} transcription"
    if output_dir_path is None:
        output_dir_path = title_root_path / "output" / f"{language.tag}_transcribe"
    output_dir_path.mkdir(parents=True, exist_ok=True)

    reference = Series.load(reference_path)
    guide = Series.load(guide_path)

    # Stage guide subtitles and audio under the transcription output
    audio_dir_path = output_dir_path / "audio"
    audio_dir_path.mkdir(parents=True, exist_ok=True)
    staged_audio_path = audio_dir_path / "audio.wav"
    if audio_source_path is not None and audio_source_path != staged_audio_path:
        if overwrite_srt or not staged_audio_path.exists():
            copy2(audio_source_path, staged_audio_path)
    audio_srt_path = audio_dir_path / "audio.srt"
    if overwrite_srt or not audio_srt_path.exists():
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
    transcribe_path = output_dir_path / "transcribe.srt"
    if transcribe_path.exists() and not overwrite_srt:
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
            **transcription_kw,
        )
        transcribe.save(transcribe_path, exist_ok=True)

    logger.info(f"{name} CER:\n{SeriesCER(reference, transcribe)}")
    logger.info(f"Saved transcription output under {output_dir_path}")
    return transcribe
