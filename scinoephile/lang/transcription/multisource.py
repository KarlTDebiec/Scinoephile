#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Reference-free fusion of multiple timestamped transcription sources."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path

from pydub import AudioSegment

from scinoephile.audio.transcription import (
    CtcAligner,
    TranscribedSegment,
    Transcriber,
    TranscriptionEmptyError,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.yue.review import (
    TimedTranscriptionMultiReviewPromptYueHans,
    TimedTranscriptionMultiReviewPromptYueHant,
)
from scinoephile.llms.multi_review import MultiReviewProcessor, MultiReviewPrompt
from scinoephile.llms.providers.registry import get_provider

__all__ = ["UnguidedMultiSourceTranscriber"]


logger = getLogger(__name__)

_FUSION_SPAN_MS = 10_000
"""Duration of neutral source-fusion timing spans."""

_MAX_EVIDENCE_WORD_DURATION_SECONDS = 5.0
"""Longest plausible ASR word duration included in temporal evidence."""

_PROMPTS: Mapping[Language, MultiReviewPrompt] = {
    Language.yue_hans: TimedTranscriptionMultiReviewPromptYueHans,
    Language.yue_hant: TimedTranscriptionMultiReviewPromptYueHant,
}
"""Timed transcription merge prompts keyed by output language."""


@dataclass(frozen=True, slots=True)
class _TimedEvidence:
    """One source text unit with a robust local timing anchor."""

    anchor_ms: int
    """Local millisecond position used to assign the unit to a fusion span."""
    end_seconds: float
    """Original local end time in seconds."""
    sequence_idx: int
    """Stable original order within one transcription source."""
    start_seconds: float
    """Original local start time in seconds."""
    text: str
    """Transcribed source text."""


class UnguidedMultiSourceTranscriber:
    """Merge timed ASR evidence and realign its consensus text to source audio."""

    def __init__(
        self,
        *,
        language: Language,
        transcribers: Mapping[str, Transcriber],
        reviewer: MultiReviewProcessor,
        aligner: CtcAligner | None = None,
    ):
        """Initialize.

        Arguments:
            language: transcription and output language
            transcribers: named equal-status ASR sources
            reviewer: equal-status timed-source reviewer
            aligner: CTC aligner used to produce fresh consensus word timings
        Raises:
            ValueError: if there are too few named transcription sources
        """
        if len(transcribers) < 2:
            raise ValueError(
                "Unguided multi-source transcription requires at least two sources."
            )
        if any(not name.strip() for name in transcribers):
            raise ValueError("Transcription source names must be nonblank.")
        self.language = language
        """Transcription and output language."""
        self.transcribers = dict(transcribers)
        """Named equal-status ASR sources in stable query order."""
        self.reviewer = reviewer
        """Equal-status timed-source reviewer."""
        if aligner is None:
            aligner = CtcAligner(language)
        self.aligner = aligner
        """Aligner used to timestamp the merged complete transcript."""

    def __call__(self, audio: AudioSegment) -> list[TranscribedSegment]:
        """Transcribe audio using all available sources and merge their evidence.

        Arguments:
            audio: complete padded unguided block audio
        Returns:
            merged transcription with newly inferred word timings
        Raises:
            TranscriptionEmptyError: if no source provides usable text
        """
        successful_sources: dict[str, list[TranscribedSegment]] = {}
        for source_name, transcriber in self.transcribers.items():
            try:
                segments = transcriber(audio)
            except TranscriptionEmptyError as exc:
                logger.info(
                    f"Unguided transcription source {source_name!r} contains no "
                    f"transcribed speech: {exc}"
                )
                continue
            if any(segment.text.strip() for segment in segments):
                successful_sources[source_name] = segments

        if not successful_sources:
            raise TranscriptionEmptyError(
                "All unguided transcription sources produced empty output."
            )
        if len(successful_sources) == 1:
            source_name, segments = next(iter(successful_sources.items()))
            logger.warning(
                f"Only unguided transcription source {source_name!r} produced "
                "output; skipping multi-source review."
            )
            return segments
        return self.merge(successful_sources, audio)

    def merge(
        self, sources: Mapping[str, Sequence[TranscribedSegment]], audio: AudioSegment
    ) -> list[TranscribedSegment]:
        """Merge timed transcription sources and align the result to audio.

        Arguments:
            sources: named equal-status timestamped transcription sources
            audio: original block audio corresponding to local source timings
        Returns:
            merged transcription with newly inferred word timings
        Raises:
            ScinoephileError: if fewer than two named sources are provided
            TranscriptionEmptyError: if no usable source or merged text is available
        """
        if len(sources) < 2:
            raise ScinoephileError(
                "Unguided multi-source transcription requires at least two sources."
            )
        if len(audio) <= 0:
            raise TranscriptionEmptyError(
                "Cannot merge transcription evidence for empty audio."
            )

        evidence_by_source = {
            name: self._get_timed_evidence(segments)
            for name, segments in sources.items()
        }
        if not any(evidence_by_source.values()):
            raise TranscriptionEmptyError(
                "Timed transcription sources contain no usable text."
            )
        guide = self._get_timing_guide(len(audio))
        source_series = {
            name: self._get_source_series(evidence, guide)
            for name, evidence in evidence_by_source.items()
        }
        if not any(source_series.values()):
            raise TranscriptionEmptyError(
                "Timed transcription sources contain no usable text."
            )

        reviewed = self.reviewer.process(source_series, guide)
        if not any(subtitle.text_with_newline.strip() for subtitle in reviewed):
            raise TranscriptionEmptyError(
                "Multi-source transcription review produced no usable text."
            )

        output_segments = []
        for subtitle in reviewed:
            text = subtitle.text_with_newline.strip()
            if not text:
                continue
            span_audio = audio[subtitle.start : subtitle.end]
            aligned_segments = self.aligner(span_audio, text)
            offset_seconds = subtitle.start / 1000
            for segment in aligned_segments:
                words = None
                if segment.words is not None:
                    words = [
                        word.model_copy(
                            update={
                                "start": word.start + offset_seconds,
                                "end": word.end + offset_seconds,
                            }
                        )
                        for word in segment.words
                    ]
                output_segments.append(
                    segment.model_copy(
                        update={
                            "start": segment.start + offset_seconds,
                            "end": segment.end + offset_seconds,
                            "words": words,
                        }
                    )
                )
        return [
            segment.model_copy(update={"id": segment_idx})
            for segment_idx, segment in enumerate(output_segments)
        ]

    def _get_source_series(
        self, evidence: Sequence[_TimedEvidence], guide: Series
    ) -> Series:
        """Assign one source's evidence to neutral timing spans."""
        timed_text_by_span: list[list[_TimedEvidence]] = [[] for _ in guide]
        for item in evidence:
            for span_idx, span in enumerate(guide):
                if item.anchor_ms < span.start:
                    break
                if item.anchor_ms < span.end or (
                    span_idx == len(guide) - 1 and item.anchor_ms == span.end
                ):
                    timed_text_by_span[span_idx].append(item)
                    break
        events = []
        for guide_subtitle, timed_text in zip(guide, timed_text_by_span):
            if not timed_text:
                continue
            timed_text.sort(key=lambda item: (item.start_seconds, item.sequence_idx))
            events.append(
                Subtitle(
                    start=guide_subtitle.start,
                    end=guide_subtitle.end,
                    text="".join(item.text for item in timed_text),
                )
            )
        return Series(events=events)

    def _get_timed_evidence(
        self, segments: Sequence[TranscribedSegment]
    ) -> list[_TimedEvidence]:
        """Normalize source segments into deduplicated robustly anchored evidence."""
        evidence = []
        seen_items: set[tuple[str, float, float]] = set()
        sequence_idx = 0
        for segment in segments:
            if segment.words:
                source_items = [
                    (word.text, word.start, word.end) for word in segment.words
                ]
            else:
                source_items = [(segment.text, segment.start, segment.end)]
            for text, start_seconds, end_seconds in source_items:
                item_key = (text, start_seconds, end_seconds)
                if not text.strip() or item_key in seen_items:
                    sequence_idx += 1
                    continue
                seen_items.add(item_key)
                duration_seconds = end_seconds - start_seconds
                if duration_seconds > _MAX_EVIDENCE_WORD_DURATION_SECONDS:
                    logger.warning(
                        f"Anchoring implausible {duration_seconds:.3f}-second "
                        f"transcription unit {text!r} at its end time."
                    )
                    anchor_seconds = max(start_seconds, end_seconds - 0.001)
                else:
                    anchor_seconds = (start_seconds + end_seconds) / 2
                evidence.append(
                    _TimedEvidence(
                        anchor_ms=round(anchor_seconds * 1000),
                        end_seconds=end_seconds,
                        sequence_idx=sequence_idx,
                        start_seconds=start_seconds,
                        text=text,
                    )
                )
                sequence_idx += 1
        return evidence

    def _get_timing_guide(self, duration_ms: int) -> Series:
        """Build complete neutral timing-only spans for source fusion."""
        events = []
        for start_ms in range(0, duration_ms, _FUSION_SPAN_MS):
            end_ms = min(start_ms + _FUSION_SPAN_MS, duration_ms)
            events.append(
                Subtitle(
                    start=start_ms,
                    end=end_ms,
                    text=(
                        f"{self._format_timestamp(start_ms)}–"
                        f"{self._format_timestamp(end_ms)}"
                    ),
                )
            )
        return Series(events=events)

    @staticmethod
    def _format_timestamp(timestamp_ms: int) -> str:
        """Format a nonnegative millisecond timestamp for a timing-only label."""
        minutes, remainder_ms = divmod(timestamp_ms, 60_000)
        seconds, milliseconds = divmod(remainder_ms, 1000)
        return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


def get_unguided_multi_source_transcriber(
    language: Language,
    transcribers: Mapping[str, Transcriber],
    *,
    provider: LLMProvider | None = None,
    cache_root_path: Path | None = None,
    overwrite_cache: bool = False,
    additional_context: str | None = None,
    no_op: bool = False,
) -> UnguidedMultiSourceTranscriber:
    """Get a reference-free timed multi-source transcriber.

    Arguments:
        language: transcription and output language
        transcribers: named equal-status ASR sources
        provider: provider to use for the consensus query
        cache_root_path: cache root directory path
        overwrite_cache: whether to replace matching generated cache files
        additional_context: additional context to include in the merge prompt
        no_op: select the first available source instead of querying an LLM
    Returns:
        configured timed multi-source transcriber
    Raises:
        ScinoephileError: if timed multi-source merging does not support the language
    """
    try:
        prompt = _PROMPTS[language]
    except KeyError as exc:
        raise ScinoephileError(
            f"Unguided multi-source transcription does not support "
            f"language {language.code}."
        ) from exc
    if provider is None:
        provider = get_provider()
    reviewer = MultiReviewProcessor(
        prompt,
        provider=provider,
        cache_root_path=cache_root_path,
        overwrite_cache=overwrite_cache,
        additional_context=additional_context,
        no_op=no_op,
    )
    return UnguidedMultiSourceTranscriber(
        language=language, transcribers=transcribers, reviewer=reviewer
    )
