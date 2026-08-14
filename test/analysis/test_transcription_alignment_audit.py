#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of portable transcription alignment audits."""

from __future__ import annotations

from pytest import raises

from scinoephile.analysis.alignment.timed_msa.models import Token
from scinoephile.analysis.audit.transcription_alignment import (
    audit_transcription_alignment,
    render_transcription_alignment_terminal,
)
from scinoephile.analysis.transcription.artifact import (
    AlignmentArtifact,
    AlignmentBlock,
    AlignmentColumn,
    AlignmentRow,
    AlignmentSource,
    AlignmentSubtitle,
    TimingSettings,
)
from scinoephile.core import Language
from scinoephile.core.subtitles import Series, Subtitle


def test_audit_renders_merged_reference_and_boundary_by_default():
    """Default rows should show ASR, merged, and collapsed reference boundaries."""
    artifact = _get_artifact()
    reference = Series(events=[Subtitle(start=800, end=2300, text="係呀")])

    report = audit_transcription_alignment(artifact, {"reference": reference})

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
                AlignmentColumn(index=1, start_ms=1_000, end_ms=1_200, kind="text"),
                AlignmentColumn(index=2, start_ms=1_200, end_ms=1_400, kind="text"),
                AlignmentColumn(index=3, start_ms=1_400, end_ms=1_600, kind="text"),
                AlignmentColumn(index=4, start_ms=1_600, end_ms=1_800, kind="text"),
            ),
            "rows": (
                AlignmentRow(name="whisper", text="甲丙　戊"),
                AlignmentRow(name="mimo", text="甲　　　"),
            ),
            "speaker": "ＡＡＡＡ",
            "merged": "甲乙丁　",
            "subtitles": (
                AlignmentSubtitle(
                    index=1,
                    text="甲乙丁",
                    speech_start_ms=1_000,
                    speech_end_ms=1_600,
                    timing_source="source",
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


def test_terminal_alignment_colors_compatibility_width_matches_green():
    """Visibly identical halfwidth and fullwidth cells should compare as exact."""
    artifact = _get_artifact()
    block = artifact.blocks[0].model_copy(
        update={
            "columns": (
                AlignmentColumn(index=1, start_ms=1_000, end_ms=1_200, kind="text"),
            ),
            "rows": (
                AlignmentRow(name="whisper", text="J"),
                AlignmentRow(name="mimo", text="Ｊ"),
            ),
            "speaker": "Ａ",
            "merged": "Ｊ",
            "subtitles": (
                AlignmentSubtitle(
                    index=1,
                    text="Ｊ",
                    speech_start_ms=1_000,
                    speech_end_ms=1_200,
                    timing_source="source",
                    start_ms=900,
                    end_ms=1_300,
                ),
            ),
        }
    )
    artifact = artifact.model_copy(update={"blocks": (block,)})
    references = {"zho-Hant": Series(events=[Subtitle(start=900, end=1_300, text="J")])}

    rendered = render_transcription_alignment_terminal(artifact, references)

    for row_name in ("whisper", "mimo", "merged", "zho-Hant"):
        row = next(line for line in rendered.splitlines() if line.startswith(row_name))
        assert "\x1b[32mＪ\x1b[0m" in row
        assert "\x1b[35mＪ\x1b[0m" not in row


def test_terminal_reference_deletion_ignores_asr_matches():
    """Reference deletions should be determined solely by the merged row."""
    artifact = _get_artifact()
    block = artifact.blocks[0].model_copy(
        update={
            "columns": (
                AlignmentColumn(index=1, start_ms=1_000, end_ms=1_200, kind="text"),
                AlignmentColumn(index=2, start_ms=1_200, end_ms=1_400, kind="text"),
                AlignmentColumn(index=3, start_ms=1_400, end_ms=1_600, kind="text"),
            ),
            "rows": (
                AlignmentRow(name="whisper", text="甲唉乙"),
                AlignmentRow(name="mimo", text="甲　乙"),
            ),
            "speaker": "ＡＡＡ",
            "merged": "甲　乙",
            "subtitles": (
                AlignmentSubtitle(
                    index=1,
                    text="甲乙",
                    speech_start_ms=1_000,
                    speech_end_ms=1_600,
                    timing_source="source",
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
        artifact, {"reference": reference}, include_timing_tables=True
    )

    assert "## Timing Comparisons" in report
    assert "CTC speech" in report
    assert "+100 ms" in report


def test_audit_preserves_artifact_pause_boundary_despite_column_timing():
    """Reference augmentation should not move a production pause across text."""
    artifact = _get_artifact()
    block = AlignmentBlock(
        index=1,
        core_start_ms=0,
        core_end_ms=1_500,
        buffered_start_ms=0,
        buffered_end_ms=1_500,
        columns=(
            AlignmentColumn(index=1, start_ms=0, end_ms=1_000, kind="text"),
            AlignmentColumn(index=2, start_ms=1_000, end_ms=1_100, kind="text"),
            AlignmentColumn(index=3, start_ms=500, end_ms=750, kind="pause"),
            AlignmentColumn(index=4, start_ms=1_200, end_ms=1_400, kind="text"),
        ),
        rows=(
            AlignmentRow(name="whisper", text="三夜・見"),
            AlignmentRow(name="mimo", text="三夜・見"),
        ),
        speaker="ＡＡ・Ａ",
        merged="三夜・見",
        subtitles=(
            AlignmentSubtitle(
                index=1,
                text="三夜",
                speech_start_ms=0,
                speech_end_ms=1_100,
                timing_source="source",
                start_ms=0,
                end_ms=1_100,
                speaker="Ａ",
            ),
            AlignmentSubtitle(
                index=2,
                text="見",
                speech_start_ms=1_200,
                speech_end_ms=1_400,
                timing_source="source",
                start_ms=1_200,
                end_ms=1_500,
                speaker="Ａ",
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

    report = audit_transcription_alignment(artifact, {"reference": reference})

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

    report = audit_transcription_alignment(artifact, {"reference": reference})

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
    """Opt-in FireRed traces should render below merged and reference rows."""
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
    reference = Series(events=[Subtitle(start=800, end=2300, text="係呀")])

    report = audit_transcription_alignment(
        artifact,
        {"reference": reference},
        include_audio_events=True,
        include_language=True,
        include_merge_support=True,
        include_speaker=True,
    )
    terminal = render_transcription_alignment_terminal(
        artifact,
        {"reference": reference},
        include_audio_events=True,
        include_language=True,
        include_merge_support=True,
        include_speaker=True,
    )

    assert "Language trace:" not in report
    assert "speaker" in report
    assert "language" in report
    assert "singing" in report
    assert "music" in report
    assert "粵・日" in report
    assert "唱・　" in report
    assert "　・樂" in report
    expected_rows = [
        "merged",
        "speaker",
        "reference",
        "support",
        "language",
        "music",
        "singing",
    ]
    for rendered in (report, terminal):
        rendered_rows = [
            line.split(maxsplit=1)[0]
            for line in rendered.splitlines()
            if line.startswith(tuple(expected_rows))
        ]
        assert rendered_rows == expected_rows


def test_audit_renders_normalized_merge_support_as_optional_row():
    """The support row should show source agreement without claiming confidence."""
    artifact = _get_artifact()
    reference = Series(events=[Subtitle(start=800, end=2300, text="係呀")])

    default_report = audit_transcription_alignment(artifact)
    report = audit_transcription_alignment(
        artifact, {"reference": reference}, include_merge_support=True
    )
    terminal = render_transcription_alignment_terminal(
        artifact, {"reference": reference}, include_merge_support=True
    )

    assert not any(line.startswith("support") for line in default_report.splitlines())
    assert "exact merge support: ０=no matching successful ASR source" in report
    support_line = next(
        line for line in report.splitlines() if line.startswith("support")
    )
    terminal_support_line = next(
        line for line in terminal.splitlines() if line.startswith("support")
    )
    assert support_line.rstrip().endswith("５・９")
    assert "\x1b[48;2;212;225;87m　\x1b[0m" in terminal_support_line
    assert terminal_support_line.count("\x1b[48;2;0;168;63m　\x1b[0m") == 1
    assert "⬛︎" not in terminal_support_line
    assert "９" not in terminal_support_line
    report_rows = [
        line.split(maxsplit=1)[0]
        for line in report.splitlines()
        if line.startswith(("merged", "reference", "support"))
    ]
    terminal_rows = [
        line.split(maxsplit=1)[0]
        for line in terminal.splitlines()
        if line.startswith(("merged", "reference", "support"))
    ]
    assert report_rows == ["merged", "reference", "support"]
    assert terminal_rows == ["merged", "reference", "support"]


def test_audit_retains_merged_text_without_source_support():
    """A fully unsupported merged chunk should remain visible with zero support."""
    artifact = _get_artifact()
    block = AlignmentBlock(
        index=1,
        core_start_ms=0,
        core_end_ms=1_000,
        buffered_start_ms=0,
        buffered_end_ms=1_000,
        columns=(AlignmentColumn(index=1, start_ms=100, end_ms=200, kind="text"),),
        rows=(
            AlignmentRow(name="whisper", text="　"),
            AlignmentRow(name="mimo", text="　"),
        ),
        speaker="＊",
        merged="甲",
        subtitles=(
            AlignmentSubtitle(
                index=1,
                text="甲",
                speech_start_ms=100,
                speech_end_ms=200,
                timing_source="source",
                start_ms=0,
                end_ms=300,
            ),
        ),
    )
    artifact = artifact.model_copy(update={"blocks": (block,)})

    report = audit_transcription_alignment(artifact, include_merge_support=True)

    merged_line = next(
        line for line in report.splitlines() if line.startswith("merged")
    )
    support_line = next(
        line for line in report.splitlines() if line.startswith("support")
    )
    assert merged_line.endswith("甲｜")
    assert support_line.endswith("０　")


def test_audit_splits_rows_at_merge_request_boundaries():
    """Audit chunks should use the production long-pause request boundaries."""
    artifact = _get_artifact()
    block = AlignmentBlock(
        index=1,
        core_start_ms=500,
        core_end_ms=2500,
        buffered_start_ms=0,
        buffered_end_ms=3000,
        columns=(
            AlignmentColumn(index=1, start_ms=1000, end_ms=1200, kind="text"),
            *(
                AlignmentColumn(
                    index=index,
                    start_ms=1200 + (index - 2) * 250,
                    end_ms=1450 + (index - 2) * 250,
                    kind="pause",
                )
                for index in range(2, 6)
            ),
            AlignmentColumn(index=6, start_ms=2200, end_ms=2400, kind="text"),
        ),
        rows=(
            AlignmentRow(name="whisper", text="係・・・・呀"),
            AlignmentRow(name="mimo", text="是・・・・呀"),
        ),
        speaker="Ａ・・・・Ａ",
        merged="係・・・・呀",
        subtitles=(
            AlignmentSubtitle(
                index=1,
                text="係",
                speech_start_ms=1000,
                speech_end_ms=1200,
                timing_source="source",
                start_ms=900,
                end_ms=1300,
                speaker="Ａ",
            ),
            AlignmentSubtitle(
                index=2,
                text="呀",
                speech_start_ms=2200,
                speech_end_ms=2400,
                timing_source="source",
                start_ms=2100,
                end_ms=2500,
                speaker="Ａ",
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
                AlignmentRow(name="whisper", text="A・1"),
                AlignmentRow(name="mimo", text="ｶ・B"),
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

    def similarity(one: Token, two: Token) -> float:
        """Record compared characters and prefer identical text."""
        compared_characters.append((one.text, two.text))
        if one.text == two.text:
            return 6.0
        return -2.0

    audit_transcription_alignment(
        artifact, {"reference": reference}, reference_similarity=similarity
    )

    assert compared_characters


def _get_artifact() -> AlignmentArtifact:
    """Get a compact valid artifact with one pause-bearing block."""
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
                core_start_ms=500,
                core_end_ms=2500,
                buffered_start_ms=0,
                buffered_end_ms=3000,
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
