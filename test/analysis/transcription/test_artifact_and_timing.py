#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of portable transcription alignment artifacts and timing evaluation."""

from __future__ import annotations

from pathlib import Path

from pytest import approx, raises

from scinoephile.analysis.transcription.artifact import (
    AlignmentArtifact,
    AlignmentBlock,
    AlignmentColumn,
    AlignmentRow,
    AlignmentSource,
    AlignmentSubtitle,
    TimingSettings,
)
from scinoephile.analysis.transcription.timing import (
    evaluate_timing,
    get_display_intervals,
    retime_alignment,
)
from scinoephile.core.language import Language
from scinoephile.core.subtitles import Series, Subtitle


def test_artifact_can_be_retimed_without_changing_text_or_speech_bounds():
    """Global timing experiments should modify only display bounds and policy."""
    artifact = _get_artifact()
    settings = TimingSettings(
        lead_in_seconds=0.25, lead_out_seconds=0.5, minimum_duration_seconds=1.0
    )

    retimed = retime_alignment(artifact, settings)

    original_subtitle = artifact.blocks[0].subtitles[0]
    retimed_subtitle = retimed.blocks[0].subtitles[0]
    assert retimed.timing == settings
    assert retimed_subtitle.text == original_subtitle.text
    assert retimed_subtitle.speech_start_ms == original_subtitle.speech_start_ms
    assert retimed_subtitle.speech_end_ms == original_subtitle.speech_end_ms
    assert retimed_subtitle.start_ms == 750
    assert retimed_subtitle.end_ms == 2500


def test_artifact_rejects_missing_source_without_error():
    """Every absent expected source row should have a diagnostic."""
    artifact = _get_artifact()
    incomplete_block = artifact.blocks[0].model_copy(
        update={"rows": artifact.blocks[0].rows[:1]}
    )

    with raises(ValueError, match="absent alignment source"):
        AlignmentArtifact(
            language=artifact.language,
            audio_duration_ms=artifact.audio_duration_ms,
            sources=artifact.sources,
            blocks=(incomplete_block,),
        )


def test_artifact_rejects_unsupported_version():
    """Artifacts should reject schemas this code does not implement."""
    artifact_data = _get_artifact().model_dump()
    artifact_data["version"] = 2

    with raises(ValueError, match="version"):
        AlignmentArtifact.model_validate(artifact_data)


def test_artifact_rejects_zero_duration_speech():
    """Artifact subtitles should always contain positive-duration speech."""
    subtitle_data = _get_artifact().blocks[0].subtitles[0].model_dump()
    subtitle_data["speech_end_ms"] = subtitle_data["speech_start_ms"]

    with raises(ValueError, match="speech duration must be positive"):
        AlignmentSubtitle.model_validate(subtitle_data)


def test_artifact_round_trip_preserves_canonical_schema(tmp_path: Path):
    """A saved artifact should validate and reconstruct its merged series.

    Arguments:
        tmp_path: temporary output directory
    """
    artifact = _get_artifact()
    artifact_path = tmp_path / "alignment.json"

    artifact.save(artifact_path)
    loaded = AlignmentArtifact.load(artifact_path)

    assert loaded == artifact
    assert loaded.version == 5
    assert {"gap_character", "pause_character", "speech_character"}.isdisjoint(
        loaded.model_dump()
    )
    assert loaded.get_series()[0].text == "係呀"
    assert loaded.blocks[0].subtitles[0].timing_source == "source"


def test_artifact_source_identity_is_nonblank():
    """Artifact source identity fields should reject whitespace-only values."""
    with raises(ValueError, match="at least 1 character"):
        AlignmentSource(name=" ", backend="whisper", model="whisper")


def test_block_rejects_columns_outside_block():
    """Portable column timing should remain within its ASR input block."""
    block_data = _get_artifact().blocks[0].model_dump()
    block_data["columns"][0]["start_ms"] = 3001
    block_data["columns"][0]["end_ms"] = 3001

    with raises(ValueError, match="within the block"):
        AlignmentBlock.model_validate(block_data)


def test_block_rejects_invalid_speaker_and_inconsistent_pause_rows():
    """Portable blocks should enforce their production annotation contract."""
    block_data = _get_artifact().blocks[0].model_dump()
    with raises(ValueError, match="invalid character"):
        AlignmentBlock.model_validate({**block_data, "speaker": "Ａ-Ａ"})

    rows = block_data["rows"]
    rows[0]["text"] = "係　呀"
    with raises(ValueError, match="shared by every row"):
        AlignmentBlock.model_validate({**block_data, "rows": rows})

    block_data = _get_artifact().blocks[0].model_dump()
    block_data["columns"][1]["kind"] = "text"
    with raises(ValueError, match="pause markers require a pause column"):
        AlignmentBlock.model_validate(block_data)


def test_display_intervals_apply_global_padding_without_overlap():
    """Display padding should remain bounded by neighboring speech midpoints."""
    intervals = get_display_intervals(
        [(1.0, 1.1), (1.4, 1.5)],
        3.0,
        TimingSettings(
            lead_in_seconds=0.2, lead_out_seconds=0.2, minimum_duration_seconds=0.3
        ),
    )

    assert intervals[0][0] == approx(0.8)
    assert intervals[0][1] <= intervals[1][0]
    assert intervals[1][1] == approx(1.7)


def test_display_intervals_reject_nonfinite_timing():
    """Display timing should reject nonfinite audio and speech bounds."""
    with raises(ValueError, match="finite number"):
        TimingSettings(lead_in_seconds=float("inf"))
    with raises(ValueError, match="finite and positive"):
        get_display_intervals([], float("inf"))
    with raises(ValueError, match="speech timing must be finite"):
        get_display_intervals([(float("nan"), 1.0)], 2.0)


def test_timing_evaluation_pairs_text_before_scoring_overlap():
    """Timing evaluation should compare text-aligned candidate/reference groups."""
    artifact = _get_artifact()
    reference = Series(events=[Subtitle(start=800, end=2300, text="係呀")])

    metrics = evaluate_timing(artifact, reference)

    assert metrics.candidate_to_reference_group_counts == {"1:1": 1}
    assert len(metrics.pairs) == 1
    assert metrics.micro_intersection_over_union == approx(1300 / 1500)
    assert metrics.pairs[0].start_error_ms == 100
    assert metrics.pairs[0].end_error_ms == -100


def test_timing_evaluation_scores_multiline_subtitle_once():
    """Line-level alignment should not weight subtitles by their line count."""
    artifact = _get_artifact()
    block = artifact.blocks[0]
    multiline_subtitle = block.subtitles[0].model_copy(update={"text": "係\\N呀"})
    artifact = artifact.model_copy(
        update={
            "blocks": (block.model_copy(update={"subtitles": (multiline_subtitle,)}),)
        }
    )
    reference = Series(events=[Subtitle(start=800, end=2300, text="係\\N呀")])

    metrics = evaluate_timing(artifact, reference)

    assert len(metrics.pairs) == 1
    assert metrics.pairs[0].candidate_indexes == (1,)
    assert metrics.pairs[0].reference_indexes == (1,)


def test_timing_evaluation_preserves_original_reference_indexes():
    """Filtered references should retain their indexes in the caller's series."""
    reference = Series(
        events=[
            Subtitle(start=0, end=400, text="outside"),
            Subtitle(start=800, end=2300, text="係呀"),
        ]
    )

    metrics = evaluate_timing(_get_artifact(), reference)

    assert len(metrics.pairs) == 1
    assert metrics.pairs[0].reference_indexes == (2,)


def _get_artifact() -> AlignmentArtifact:
    """Get a compact valid artifact with one pause-bearing block.

    Returns:
        compact alignment artifact
    """
    return AlignmentArtifact(
        language=Language.yue_hant,
        audio_duration_ms=3000,
        timing=TimingSettings(minimum_duration_seconds=0.75),
        sources=(
            AlignmentSource(name="whisper", backend="whisper", model="whisper"),
            AlignmentSource(name="mimo", backend="mlx", model="mimo"),
        ),
        blocks=(
            AlignmentBlock(
                index=1,
                start_ms=0,
                end_ms=3000,
                columns=(
                    AlignmentColumn(index=1, start_ms=1000, end_ms=1500, kind="text"),
                    AlignmentColumn(index=2, start_ms=1500, end_ms=1750, kind="pause"),
                    AlignmentColumn(index=3, start_ms=1750, end_ms=2000, kind="text"),
                ),
                rows=(
                    AlignmentRow(name="whisper", text="係・呀"),
                    AlignmentRow(name="mimo", text="是・呀"),
                ),
                speaker="Ａ・Ａ",
                merged="係・呀",
                subtitles=(
                    AlignmentSubtitle(
                        index=1,
                        text="係呀",
                        speech_start_ms=1000,
                        speech_end_ms=2000,
                        timing_source="source",
                        start_ms=900,
                        end_ms=2200,
                        speaker="Ａ",
                    ),
                ),
            ),
        ),
    )
