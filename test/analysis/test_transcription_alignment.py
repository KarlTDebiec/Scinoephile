#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of portable transcription alignment artifacts and timing evaluation."""

from __future__ import annotations

from pathlib import Path

from pytest import approx, raises

from scinoephile.analysis.audit.transcription_alignment import (
    audit_transcription_alignment,
    render_transcription_alignment_terminal,
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


def test_audit_renders_merged_reference_and_boundary_by_default():
    """Default rows should show ASR, merged, and collapsed reference boundaries."""
    artifact = _get_artifact()
    reference = Series(events=[Subtitle(start=800, end=2300, text="係呀")])

    report = audit_transcription_alignment(artifact, reference)

    assert "whisper" in report
    assert "mimo" in report
    assert "merged" in report
    assert "reference" in report
    assert "｜" in report
    assert "Core " not in report
    assert "Language trace:" not in report
    assert not any(
        line.startswith(("speaker", "language", "singing", "music"))
        for line in report.splitlines()
    )
    merged_line = next(
        line for line in report.splitlines() if line.startswith("merged")
    )
    reference_line = next(
        line for line in report.splitlines() if line.startswith("reference")
    )
    whisper_line = next(
        line for line in report.splitlines() if line.startswith("whisper")
    )
    report_lines = report.splitlines()
    merged_idx = report_lines.index(merged_line)
    separator_line = report_lines[merged_idx - 1]
    assert report_lines[merged_idx - 2].startswith("mimo")
    assert set(separator_line.lstrip(" ")) == {"－"}
    assert merged_line.endswith("｜")
    assert reference_line.endswith("｜")
    assert whisper_line.endswith("　")
    assert "＋" not in report
    assert "temporal micro IoU" in report
    assert "1:1 × 1" in report
    assert "## Timing Comparisons" not in report
    assert "CTC speech" not in report
    assert "+100 ms" not in report


def test_terminal_alignment_colors_rows_against_merged_authority():
    """Terminal rows should reuse the standard four-color diff palette."""
    artifact = _get_artifact()
    block = artifact.blocks[0].model_copy(
        update={
            "columns": (
                TranscriptionAlignmentColumn(
                    index=1, start_ms=1_000, end_ms=1_200, kind="text"
                ),
                TranscriptionAlignmentColumn(
                    index=2, start_ms=1_200, end_ms=1_400, kind="text"
                ),
                TranscriptionAlignmentColumn(
                    index=3, start_ms=1_400, end_ms=1_600, kind="text"
                ),
                TranscriptionAlignmentColumn(
                    index=4, start_ms=1_600, end_ms=1_800, kind="text"
                ),
            ),
            "rows": (
                TranscriptionAlignmentRow(name="whisper", text="甲丙　戊"),
                TranscriptionAlignmentRow(name="mimo", text="甲　　　"),
            ),
            "speaker": "ＡＡＡＡ",
            "merged": "甲乙丁　",
            "subtitles": (
                TranscriptionAlignmentSubtitle(
                    index=1,
                    text="甲乙丁",
                    speech_start_ms=1_000,
                    speech_end_ms=1_600,
                    start_ms=900,
                    end_ms=1_900,
                ),
            ),
        }
    )
    artifact = artifact.model_copy(update={"blocks": (block,)})

    rendered = render_transcription_alignment_terminal(artifact)

    whisper_line = next(
        line for line in rendered.splitlines() if line.startswith("whisper")
    )
    merged_line = next(
        line for line in rendered.splitlines() if line.startswith("merged")
    )
    assert "Authority: merged" in rendered
    assert "\x1b[32m甲\x1b[0m" in whisper_line
    assert "\x1b[35m丙\x1b[0m" in whisper_line
    assert "\x1b[34m戊\x1b[0m" in whisper_line
    assert "\x1b[32m甲\x1b[0m" in merged_line
    assert "\x1b[35m乙\x1b[0m" in merged_line
    assert "\x1b[31m丁\x1b[0m" in merged_line


def test_terminal_alignment_accepts_named_reference_authority():
    """A named audit reference should be selectable as terminal authority."""
    artifact = _get_artifact()
    references = {
        "yue-Hant": Series(events=[Subtitle(start=800, end=2_300, text="係呀")])
    }

    rendered = render_transcription_alignment_terminal(
        artifact, references, authoritative_row_name="yue-Hant"
    )

    assert "Authority: yue-Hant" in rendered
    reference_line = next(
        line for line in rendered.splitlines() if line.startswith("yue-Hant")
    )
    assert "\x1b[32m係\x1b[0m" in reference_line
    with raises(ValueError, match="Authoritative alignment row"):
        render_transcription_alignment_terminal(
            artifact, references, authoritative_row_name="zho-Hant"
        )


def test_terminal_reference_deletion_ignores_asr_matches():
    """Reference deletions should be determined solely by the merged row."""
    artifact = _get_artifact()
    block = artifact.blocks[0].model_copy(
        update={
            "columns": (
                TranscriptionAlignmentColumn(
                    index=1, start_ms=1_000, end_ms=1_200, kind="text"
                ),
                TranscriptionAlignmentColumn(
                    index=2, start_ms=1_200, end_ms=1_400, kind="text"
                ),
                TranscriptionAlignmentColumn(
                    index=3, start_ms=1_400, end_ms=1_600, kind="text"
                ),
            ),
            "rows": (
                TranscriptionAlignmentRow(name="whisper", text="甲唉乙"),
                TranscriptionAlignmentRow(name="mimo", text="甲　乙"),
            ),
            "speaker": "ＡＡＡ",
            "merged": "甲　乙",
            "subtitles": (
                TranscriptionAlignmentSubtitle(
                    index=1,
                    text="甲乙",
                    speech_start_ms=1_000,
                    speech_end_ms=1_600,
                    start_ms=900,
                    end_ms=1_700,
                ),
            ),
        }
    )
    artifact = artifact.model_copy(update={"blocks": (block,)})
    references = {
        "yue-Hant": Series(events=[Subtitle(start=900, end=1_700, text="甲唉乙")])
    }

    rendered = render_transcription_alignment_terminal(
        artifact, references, authoritative_row_name="yue-Hant"
    )

    reference_line = next(
        line for line in rendered.splitlines() if line.startswith("yue-Hant")
    )
    whisper_line = next(
        line for line in rendered.splitlines() if line.startswith("whisper")
    )
    assert "\x1b[31m唉\x1b[0m" in reference_line
    assert "\x1b[32m唉\x1b[0m" in whisper_line


def test_audit_renders_timing_tables_when_requested():
    """Detailed timing tables should remain available as opt-in evidence."""
    artifact = _get_artifact()
    reference = Series(events=[Subtitle(start=800, end=2300, text="係呀")])

    report = audit_transcription_alignment(
        artifact, reference, include_timing_tables=True
    )

    assert "## Timing Comparisons" in report
    assert "CTC speech" in report
    assert "+100 ms" in report


def test_audit_preserves_artifact_pause_boundary_despite_column_timing():
    """Reference augmentation should not move a production pause across text."""
    artifact = _get_artifact()
    block = TranscriptionAlignmentBlock(
        index=1,
        core_start_ms=0,
        core_end_ms=1_500,
        buffered_start_ms=0,
        buffered_end_ms=1_500,
        columns=(
            TranscriptionAlignmentColumn(
                index=1, start_ms=0, end_ms=1_000, kind="text"
            ),
            TranscriptionAlignmentColumn(
                index=2, start_ms=1_000, end_ms=1_100, kind="text"
            ),
            TranscriptionAlignmentColumn(
                index=3, start_ms=500, end_ms=750, kind="pause"
            ),
            TranscriptionAlignmentColumn(
                index=4, start_ms=1_200, end_ms=1_400, kind="text"
            ),
        ),
        rows=(
            TranscriptionAlignmentRow(name="whisper", text="三夜・見"),
            TranscriptionAlignmentRow(name="mimo", text="三夜・見"),
        ),
        speaker="ＡＡ・Ａ",
        merged="三夜・見",
        subtitles=(
            TranscriptionAlignmentSubtitle(
                index=1,
                text="三夜",
                speech_start_ms=0,
                speech_end_ms=1_100,
                start_ms=0,
                end_ms=1_100,
                speaker="SPEAKER_00",
            ),
            TranscriptionAlignmentSubtitle(
                index=2,
                text="見",
                speech_start_ms=1_200,
                speech_end_ms=1_400,
                start_ms=1_200,
                end_ms=1_500,
                speaker="SPEAKER_00",
            ),
        ),
    )
    artifact = artifact.model_copy(
        update={"audio_duration_ms": 1_500, "blocks": (block,)}
    )
    reference = Series(
        events=[
            Subtitle(start=0, end=1_100, text="三夜"),
            Subtitle(start=1_200, end=1_500, text="見"),
        ]
    )

    report = audit_transcription_alignment(artifact, reference)

    for row_name in ("whisper", "mimo", "merged", "reference"):
        row = next(line for line in report.splitlines() if line.startswith(row_name))
        assert "三夜" in row
        assert "三・夜" not in row


def test_audit_distinguishes_unaligned_merged_and_reference_boundaries():
    """Unaligned boundaries should mark only their owning alignment row."""
    artifact = _get_artifact()
    reference = Series(
        events=[
            Subtitle(start=800, end=1500, text="係"),
            Subtitle(start=1500, end=2300, text="呀"),
        ]
    )

    report = audit_transcription_alignment(artifact, reference)

    merged_line = next(
        line for line in report.splitlines() if line.startswith("merged")
    )
    reference_line = next(
        line for line in report.splitlines() if line.startswith("reference")
    )
    whisper_line = next(
        line for line in report.splitlines() if line.startswith("whisper")
    )
    assert "係　呀｜" in merged_line.replace("・", "")
    assert "係｜呀｜" in reference_line.replace("・", "")
    assert "係　呀　" in whisper_line.replace("・", "")


def test_audit_renders_multiple_named_reference_rows():
    """Multiple named references should retain independent owned boundaries."""
    artifact = _get_artifact()
    references = {
        "zho-Hant": Series(events=[Subtitle(start=800, end=2300, text="係呀")]),
        "yue-Hant": Series(
            events=[
                Subtitle(start=800, end=1500, text="係"),
                Subtitle(start=1500, end=2300, text="呀"),
            ]
        ),
    }

    report = audit_transcription_alignment(artifact, references)

    merged_line = next(
        line for line in report.splitlines() if line.startswith("merged")
    )
    zho_hant_line = next(
        line for line in report.splitlines() if line.startswith("zho-Hant")
    )
    yue_hant_line = next(
        line for line in report.splitlines() if line.startswith("yue-Hant")
    )
    assert "references: zho-Hant, yue-Hant" in report
    assert "### Reference zho-Hant" in report
    assert "### Reference yue-Hant" in report
    assert "係　呀｜" in merged_line.replace("・", "")
    assert "係　呀｜" in zho_hant_line.replace("・", "")
    assert "係｜呀｜" in yue_hant_line.replace("・", "")


def test_audit_rejects_reference_name_conflicting_with_alignment_row():
    """Reference names should not shadow production or annotation rows."""
    artifact = _get_artifact()
    reference = Series(events=[Subtitle(start=800, end=2300, text="係呀")])

    with raises(ValueError, match="conflicts with alignment row"):
        audit_transcription_alignment(artifact, {"merged": reference})


def test_audit_renders_language_singing_and_music_rows():
    """Portable FireRed traces should remain available as opt-in rows."""
    artifact = _get_artifact()
    block = artifact.blocks[0].model_copy(
        update={
            "language_trace": "粵・日",
            "language_legend": {"粵": "zh-yue", "日": "ja"},
            "singing_trace": "唱・　",
            "music_trace": "　・樂",
        }
    )
    artifact = artifact.model_copy(update={"blocks": (block,)})

    report = audit_transcription_alignment(
        artifact, include_audio_events=True, include_language=True, include_speaker=True
    )

    assert "Language trace:" not in report
    assert "speaker" in report
    assert "language" in report
    assert "singing" in report
    assert "music" in report
    assert "粵・日" in report
    assert "唱・　" in report
    assert "　・樂" in report


def test_audit_splits_rows_at_merge_request_boundaries():
    """Audit chunks should use the production long-pause request boundaries."""
    artifact = _get_artifact()
    block = TranscriptionAlignmentBlock(
        index=1,
        core_start_ms=500,
        core_end_ms=2500,
        buffered_start_ms=0,
        buffered_end_ms=3000,
        columns=(
            TranscriptionAlignmentColumn(
                index=1, start_ms=1000, end_ms=1200, kind="text"
            ),
            *(
                TranscriptionAlignmentColumn(
                    index=index,
                    start_ms=1200 + (index - 2) * 250,
                    end_ms=1450 + (index - 2) * 250,
                    kind="pause",
                )
                for index in range(2, 6)
            ),
            TranscriptionAlignmentColumn(
                index=6, start_ms=2200, end_ms=2400, kind="text"
            ),
        ),
        rows=(
            TranscriptionAlignmentRow(name="whisper", text="係・・・・呀"),
            TranscriptionAlignmentRow(name="mimo", text="是・・・・呀"),
        ),
        speaker="Ａ・・・・Ａ",
        merged="係・・・・呀",
        subtitles=(
            TranscriptionAlignmentSubtitle(
                index=1,
                text="係",
                speech_start_ms=1000,
                speech_end_ms=1200,
                start_ms=900,
                end_ms=1300,
                speaker="SPEAKER_00",
            ),
            TranscriptionAlignmentSubtitle(
                index=2,
                text="呀",
                speech_start_ms=2200,
                speech_end_ms=2400,
                start_ms=2100,
                end_ms=2500,
                speaker="SPEAKER_00",
            ),
        ),
    )
    artifact = artifact.model_copy(update={"blocks": (block,)})

    report = audit_transcription_alignment(artifact)

    assert report.count("whisper") == 2
    assert "\n\nwhisper" in report
    assert "[request " not in report
    assert "[0001-" not in report
    assert "・・・・" not in report


def test_audit_renders_halfwidth_characters_as_fullwidth_cells():
    """The audit should widen Latin, digits, and halfwidth katakana."""
    artifact = _get_artifact()
    block = artifact.blocks[0].model_copy(
        update={
            "rows": (
                TranscriptionAlignmentRow(name="whisper", text="A・1"),
                TranscriptionAlignmentRow(name="mimo", text="ｶ・B"),
            ),
            "merged": "A・1",
        }
    )
    artifact = artifact.model_copy(update={"blocks": (block,)})

    report = audit_transcription_alignment(artifact)

    assert "whisper  Ａ・１" in report
    assert "mimo     カ・Ｂ" in report


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
