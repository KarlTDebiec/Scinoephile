#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of portable transcription alignment artifacts and timing evaluation."""

from __future__ import annotations

from pathlib import Path

from pytest import approx, raises

from scinoephile.analysis.audit.transcription_alignment import (
    audit_transcription_alignment,
)
from scinoephile.analysis.multisequence_alignment import TimedAlignmentToken
from scinoephile.analysis.transcription_alignment import (
    SubtitleTimingSettings,
    TranscriptionAlignmentArtifact,
    TranscriptionAlignmentBlock,
    TranscriptionAlignmentColumn,
    TranscriptionAlignmentRow,
    TranscriptionAlignmentSource,
    TranscriptionAlignmentSubtitle,
)
from scinoephile.analysis.transcription_timing import (
    evaluate_transcription_timing,
    get_display_intervals,
    get_transcription_alignment_with_timing,
)
from scinoephile.core import Language
from scinoephile.core.subtitles import Series, Subtitle


def test_artifact_round_trip_preserves_canonical_schema(tmp_path: Path):
    """A saved artifact should validate and reconstruct its merged series."""
    artifact = _get_artifact()
    artifact_path = tmp_path / "alignment.json"

    artifact.save(artifact_path)
    loaded = TranscriptionAlignmentArtifact.load(artifact_path)

    assert loaded == artifact
    assert loaded.get_series()[0].text == "係呀"
    assert loaded.get_series()[0].start == 900
    assert loaded.get_series()[0].end == 2200


def test_artifact_rejects_missing_source_without_error():
    """Every absent expected source row should have a diagnostic."""
    artifact = _get_artifact()
    incomplete_block = artifact.blocks[0].model_copy(
        update={"rows": artifact.blocks[0].rows[:1]}
    )

    with raises(ValueError, match="absent alignment source"):
        TranscriptionAlignmentArtifact(
            language=artifact.language,
            audio_duration_ms=artifact.audio_duration_ms,
            sources=artifact.sources,
            blocks=(incomplete_block,),
        )


def test_block_rejects_invalid_speaker_and_inconsistent_pause_rows():
    """Portable blocks should enforce their production annotation contract."""
    block_data = _get_artifact().blocks[0].model_dump()
    with raises(ValueError, match="invalid character"):
        TranscriptionAlignmentBlock.model_validate({**block_data, "speaker": "Ａ-Ａ"})

    rows = block_data["rows"]
    rows[0]["text"] = "係　呀"
    with raises(ValueError, match="shared by ASR rows"):
        TranscriptionAlignmentBlock.model_validate({**block_data, "rows": rows})


def test_display_intervals_apply_global_padding_without_overlap():
    """Display padding should remain bounded by neighboring speech midpoints."""
    intervals = get_display_intervals(
        [(1.0, 1.1), (1.4, 1.5)],
        3.0,
        SubtitleTimingSettings(
            lead_in_seconds=0.2, lead_out_seconds=0.2, minimum_duration_seconds=0.3
        ),
    )

    assert intervals[0][0] == approx(0.8)
    assert intervals[0][1] <= intervals[1][0]
    assert intervals[1][1] == approx(1.7)


def test_timing_evaluation_pairs_text_before_scoring_overlap():
    """Timing evaluation should compare text-aligned candidate/reference groups."""
    artifact = _get_artifact()
    reference = Series(events=[Subtitle(start=800, end=2300, text="係呀")])

    metrics = evaluate_transcription_timing(artifact, reference)

    assert len(metrics.pairs) == 1
    assert metrics.micro_intersection_over_union == approx(1300 / 1500)
    assert metrics.one_to_one_micro_intersection_over_union == approx(1300 / 1500)
    assert metrics.pairs[0].start_error_ms == 100
    assert metrics.pairs[0].end_error_ms == -100
    assert metrics.mean_start_error_ms == 100
    assert metrics.mean_end_error_ms == -100


def test_artifact_can_be_retimed_without_changing_text_or_speech_bounds():
    """Global timing experiments should modify only display bounds and policy."""
    artifact = _get_artifact()
    settings = SubtitleTimingSettings(
        lead_in_seconds=0.25, lead_out_seconds=0.5, minimum_duration_seconds=1.0
    )

    retimed = get_transcription_alignment_with_timing(artifact, settings)

    original_subtitle = artifact.blocks[0].subtitles[0]
    retimed_subtitle = retimed.blocks[0].subtitles[0]
    assert retimed.timing == settings
    assert retimed_subtitle.text == original_subtitle.text
    assert retimed_subtitle.speech_start_ms == original_subtitle.speech_start_ms
    assert retimed_subtitle.speech_end_ms == original_subtitle.speech_end_ms
    assert retimed_subtitle.start_ms == 750
    assert retimed_subtitle.end_ms == 2500


def test_audit_renders_merged_speaker_reference_and_boundary():
    """The audit should stack production evidence above reference boundaries."""
    artifact = _get_artifact()
    reference = Series(events=[Subtitle(start=800, end=2300, text="係呀")])

    report = audit_transcription_alignment(artifact, reference)

    assert "whisper" in report
    assert "mimo" in report
    assert "merged" in report
    assert "speaker" in report
    assert "reference" in report
    assert "｜" in report
    assert "temporal micro IoU" in report
    assert "1:1 × 1" in report
    assert "## Timing Comparisons" in report
    assert "CTC speech" in report
    assert "+100 ms" in report


def test_audit_accepts_reference_specific_similarity():
    """Reference augmentation should accept dialect-aware substitution scoring."""
    artifact = _get_artifact()
    reference = Series(events=[Subtitle(start=800, end=2_300, text="是嗎")])
    compared_characters = []

    def similarity(one: TimedAlignmentToken, two: TimedAlignmentToken) -> float:
        """Record compared characters and prefer identical text."""
        compared_characters.append((one.text, two.text))
        if one.text == two.text:
            return 6.0
        return -2.0

    audit_transcription_alignment(artifact, reference, reference_similarity=similarity)

    assert compared_characters


def _get_artifact() -> TranscriptionAlignmentArtifact:
    """Get a compact valid artifact with one pause-bearing block."""
    return TranscriptionAlignmentArtifact(
        language=Language.yue_hant,
        audio_duration_ms=3000,
        timing=SubtitleTimingSettings(minimum_duration_seconds=0.75),
        sources=(
            TranscriptionAlignmentSource(
                name="whisper", backend="whisper", model="whisper"
            ),
            TranscriptionAlignmentSource(name="mimo", backend="mlx", model="mimo"),
        ),
        blocks=(
            TranscriptionAlignmentBlock(
                index=1,
                core_start_ms=500,
                core_end_ms=2500,
                buffered_start_ms=0,
                buffered_end_ms=3000,
                columns=(
                    TranscriptionAlignmentColumn(
                        index=1, start_ms=1000, end_ms=1500, kind="text"
                    ),
                    TranscriptionAlignmentColumn(
                        index=2, start_ms=1500, end_ms=1750, kind="pause"
                    ),
                    TranscriptionAlignmentColumn(
                        index=3, start_ms=1750, end_ms=2000, kind="text"
                    ),
                ),
                rows=(
                    TranscriptionAlignmentRow(name="whisper", text="係・呀"),
                    TranscriptionAlignmentRow(name="mimo", text="是・呀"),
                ),
                speaker="Ａ・Ａ",
                merged="係・呀",
                subtitles=(
                    TranscriptionAlignmentSubtitle(
                        index=1,
                        text="係呀",
                        speech_start_ms=1000,
                        speech_end_ms=2000,
                        start_ms=900,
                        end_ms=2200,
                        speaker="SPEAKER_00",
                    ),
                ),
            ),
        ),
    )
