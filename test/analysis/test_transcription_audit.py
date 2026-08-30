#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of portable transcription alignment audits."""

from __future__ import annotations

from pytest import raises

from scinoephile.analysis.alignment.timed_msa import MsaToken
from scinoephile.analysis.audit.transcription.report import (
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


def test_audit_accepts_custom_token_similarity():
    """Reference augmentation should accept custom substitution scoring."""
    artifact = _get_artifact()
    reference = Series(events=[Subtitle(start=800, end=2_300, text="是嗎")])
    compared_characters = []

    def similarity(one: MsaToken, two: MsaToken) -> float:
        """Record compared characters and prefer identical text.

        Arguments:
            one: first timed alignment token
            two: second timed alignment token
        Returns:
            lexical substitution score
        """
        compared_characters.append((one.text, two.text))
        if one.text == two.text:
            return 6.0
        return -2.0

    audit_transcription_alignment(
        artifact, {"reference": reference}, token_similarity=similarity
    )

    assert compared_characters


def test_audit_reports_block_cer_sorted_by_merged_error():
    """Block CER tables should put the most troublesome merged block first."""
    artifact = _get_artifact()
    first_block = artifact.blocks[0].model_copy(
        update={
            "end_ms": 2_500,
            "merged": "是・嗎",
            "subtitles": (
                artifact.blocks[0].subtitles[0].model_copy(update={"text": "是嗎"}),
            ),
        }
    )
    second_block = AlignmentBlock(
        index=2,
        start_ms=2_500,
        end_ms=3_000,
        columns=(AlignmentColumn(index=1, start_ms=2_600, end_ms=2_800, kind="text"),),
        rows=(
            AlignmentRow(name="whisper", text="乙"),
            AlignmentRow(name="mimo", text="丙"),
        ),
        speaker="Ａ",
        merged="乙",
        subtitles=(
            AlignmentSubtitle(
                index=2,
                text="乙",
                speech_start_ms=2_600,
                speech_end_ms=2_800,
                timing_source="source",
                start_ms=2_500,
                end_ms=3_000,
                speaker="Ａ",
            ),
        ),
    )
    artifact = artifact.model_copy(update={"blocks": (first_block, second_block)})
    reference = Series(
        events=[
            Subtitle(start=900, end=2_200, text="係呀"),
            Subtitle(start=2_500, end=3_000, text="乙"),
        ]
    )

    report = audit_transcription_alignment(artifact, {"reference": reference})

    header = "| Block | Reference characters | merged | whisper | mimo |"
    first_row = "|     1 |                    2 |   100% |      0% |  50% |"
    second_row = "|     2 |                    1 |     0% |      0% | 100% |"
    assert "#### Block CER" in report
    assert header in report
    assert first_row in report
    assert second_row in report
    assert report.index(first_row) < report.index(second_row)
    lines = report.splitlines()
    table_start = lines.index(header)
    assert len({len(line) for line in lines[table_start : table_start + 4]}) == 1


def test_audit_marks_blocks_without_reference_characters_unscored():
    """CER should be unscored when a block contains no reference characters."""
    artifact = _get_artifact()

    report = audit_transcription_alignment(artifact, {"reference": Series(events=[])})

    assert "|     1 |                    0 |      — |       — |    — |" in report


def test_audit_assigns_boundary_reference_by_global_text_alignment():
    """Reference text should follow its matching block across a timing boundary."""
    artifact = _get_boundary_artifact()
    reference = Series(events=[Subtitle(start=800, end=1_000, text="乙")])

    report = audit_transcription_alignment(artifact, {"reference": reference})

    reference_lines = [
        line for line in report.splitlines() if line.startswith("reference")
    ]
    assert len(reference_lines) == 2
    assert "乙" not in reference_lines[0]
    assert "乙" in reference_lines[1]
    assert "|     1 |                    0 |      — |" in report
    assert "|     2 |                    1 |     0% |" in report


def test_audit_filtered_summary_uses_globally_assigned_reference():
    """Filtered summaries should score the same globally assigned references."""
    artifact = _get_boundary_artifact()
    reference = Series(events=[Subtitle(start=800, end=1_000, text="乙")])

    report = audit_transcription_alignment(
        artifact,
        {"reference": reference},
        first_block=2,
        last_block=2,
        include_timing_tables=True,
    )

    assert "- reference subtitles: 1" in report
    assert "- text-aligned timing groups: 1" in report
    assert "|     2 |                    1 |     0% |" in report
    assert "| 2 | 1 |" in report


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


def test_audit_preserves_artifact_pause_boundary_despite_column_timing():
    """Reference augmentation should not move a production pause across text."""
    artifact = _get_artifact()
    block = AlignmentBlock(
        index=1,
        start_ms=0,
        end_ms=1_500,
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


def test_audit_rejects_reference_name_conflicting_with_alignment_row():
    """Reference names should not shadow production or annotation rows."""
    artifact = _get_artifact()
    reference = Series(events=[Subtitle(start=800, end=2300, text="係呀")])

    with raises(ValueError, match="conflicts with alignment row"):
        audit_transcription_alignment(artifact, {"merged": reference})


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


def test_audit_omits_trailing_whitespace_from_narrow_characters():
    """Narrow final characters should not leave Markdown trailing whitespace."""
    artifact = _get_artifact()
    block = artifact.blocks[0].model_copy(
        update={
            "rows": (
                AlignmentRow(name="whisper", text="係・a"),
                AlignmentRow(name="mimo", text="係・a"),
            ),
            "merged": "係・a",
        }
    )
    artifact = artifact.model_copy(update={"blocks": (block,)})

    report = audit_transcription_alignment(artifact)

    assert all(line == line.rstrip(" ") for line in report.splitlines())


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
    assert "Language legend: 粵=zh-yue; 日=ja" in report
    assert "Language legend: 粵=zh-yue; 日=ja" in terminal
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
    assert "- whisper CER: 0.000%" in report
    assert "- mimo CER: 50.000%" in report
    assert "- merged CER: 0.000%" in report
    assert "## Timing Comparisons" not in report
    assert "CTC speech" not in report
    assert "+100 ms" not in report


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
    assert "merge support: ０=no similar successful ASR source" in report
    support_line = next(
        line for line in report.splitlines() if line.startswith("support")
    )
    terminal_support_line = next(
        line for line in terminal.splitlines() if line.startswith("support")
    )
    assert support_line.rstrip().endswith("５・９")
    assert "\x1b[35m５\x1b[0m" in terminal_support_line
    assert terminal_support_line.count("\x1b[32m９\x1b[0m") == 1
    assert "⬛︎" not in terminal_support_line
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


def test_audit_quantifies_support_for_merged_omissions():
    """The support row should score source agreement with an omitted character."""
    artifact = _get_artifact()
    block = artifact.blocks[0].model_copy(
        update={
            "rows": (
                AlignmentRow(name="whisper", text="　・呀"),
                AlignmentRow(name="mimo", text="是・呀"),
            ),
            "merged": "　・呀",
            "subtitles": (
                artifact.blocks[0].subtitles[0].model_copy(update={"text": "呀"}),
            ),
        }
    )
    artifact = artifact.model_copy(update={"blocks": (block,)})

    report = audit_transcription_alignment(artifact, include_merge_support=True)

    support_line = next(
        line for line in report.splitlines() if line.startswith("support")
    )
    assert support_line.rstrip().endswith("５・９")


def test_audit_uses_token_similarity_for_merge_support():
    """The support row should count language-aware character matches."""
    artifact = _get_artifact()

    def similarity(one: MsaToken, two: MsaToken) -> float:
        """Treat common copula forms as equivalent.

        Arguments:
            one: first timed alignment token
            two: second timed alignment token
        Returns:
            positive score for matching copula forms
        """
        if one.text in {"係", "是", "系"} and two.text in {"係", "是", "系"}:
            return 5.0
        if one.text == two.text:
            return 6.0
        return -2.0

    report = audit_transcription_alignment(
        artifact, token_similarity=similarity, include_merge_support=True
    )

    support_line = next(
        line for line in report.splitlines() if line.startswith("support")
    )
    assert support_line.rstrip().endswith("９・９")


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


def test_audit_timing_tables_preserve_complete_artifact_indexes():
    """Filtered timing tables should retain complete-artifact subtitle indexes."""
    artifact = _get_artifact()
    first_block = artifact.blocks[0]
    offset_ms = 3_000
    second_block = first_block.model_copy(
        update={
            "index": 2,
            "start_ms": first_block.start_ms + offset_ms,
            "end_ms": first_block.end_ms + offset_ms,
            "columns": tuple(
                column.model_copy(
                    update={
                        "start_ms": column.start_ms + offset_ms,
                        "end_ms": column.end_ms + offset_ms,
                    }
                )
                for column in first_block.columns
            ),
            "subtitles": tuple(
                subtitle.model_copy(
                    update={
                        "index": 2,
                        "speech_start_ms": subtitle.speech_start_ms + offset_ms,
                        "speech_end_ms": subtitle.speech_end_ms + offset_ms,
                        "start_ms": subtitle.start_ms + offset_ms,
                        "end_ms": subtitle.end_ms + offset_ms,
                    }
                )
                for subtitle in first_block.subtitles
            ),
        }
    )
    artifact = AlignmentArtifact.model_validate(
        {
            **artifact.model_dump(),
            "audio_duration_ms": artifact.audio_duration_ms + offset_ms,
            "blocks": (first_block, second_block),
        }
    )
    reference = Series(
        events=[
            Subtitle(start=800, end=2_300, text="係呀"),
            Subtitle(start=3_800, end=5_300, text="係呀"),
        ]
    )

    report = audit_transcription_alignment(
        artifact,
        {"reference": reference},
        first_block=2,
        last_block=2,
        include_timing_tables=True,
    )

    assert "| 2 | 2 | 3.900–5.200 s | 3.800–5.300 s |" in report
    assert "| 1 | 2 | 3.900–5.200 s | 3.800–5.300 s |" not in report


def test_audit_reports_subtitle_range_as_complete_block_context():
    """Subtitle ranges should retain and disclose their complete block context."""
    artifact = _get_artifact()
    block = artifact.blocks[0].model_copy(
        update={
            "subtitles": (
                AlignmentSubtitle(
                    index=1,
                    text="係",
                    speech_start_ms=1_000,
                    speech_end_ms=1_500,
                    timing_source="source",
                    start_ms=900,
                    end_ms=1_600,
                    speaker="Ａ",
                ),
                AlignmentSubtitle(
                    index=2,
                    text="呀",
                    speech_start_ms=1_750,
                    speech_end_ms=2_000,
                    timing_source="source",
                    start_ms=1_700,
                    end_ms=2_200,
                    speaker="Ａ",
                ),
            )
        }
    )
    artifact = artifact.model_copy(update={"blocks": (block,)})

    report = audit_transcription_alignment(
        artifact, first_index=2, last_index=2, include_timing_tables=True
    )
    terminal = render_transcription_alignment_terminal(
        artifact, first_index=2, last_index=2
    )

    assert (
        "requested merged subtitle range: 2 through 2; complete containing blocks shown"
    ) in report
    assert "selected merged subtitles: 2" in report
    assert "| 1 |" in report
    assert "| 2 |" in report
    assert "Block 1" in terminal


def test_audit_retains_merged_text_without_source_support():
    """A fully unsupported merged chunk should remain visible with zero support."""
    artifact = _get_artifact()
    block = AlignmentBlock(
        index=1,
        start_ms=0,
        end_ms=1_000,
        columns=(AlignmentColumn(index=1, start_ms=100, end_ms=200, kind="text"),),
        rows=(
            AlignmentRow(name="whisper", text="　"),
            AlignmentRow(name="mimo", text="　"),
        ),
        speaker="　",
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
    terminal = render_transcription_alignment_terminal(
        artifact, include_merge_support=True
    )

    merged_line = next(
        line for line in report.splitlines() if line.startswith("merged")
    )
    support_line = next(
        line for line in report.splitlines() if line.startswith("support")
    )
    terminal_support_line = next(
        line for line in terminal.splitlines() if line.startswith("support")
    )
    assert merged_line.endswith("甲｜")
    assert support_line.endswith("０　")
    assert "\x1b[31m０\x1b[0m" in terminal_support_line


def test_audit_splits_rows_at_merge_request_boundaries():
    """Audit chunks should use the production long-pause request boundaries."""
    artifact = _get_artifact()
    block = AlignmentBlock(
        index=1,
        start_ms=0,
        end_ms=3000,
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


def _get_artifact() -> AlignmentArtifact:
    """Get a compact valid artifact with one pause-bearing block.

    Returns:
        compact alignment artifact used by audit tests
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


def _get_boundary_artifact() -> AlignmentArtifact:
    """Get two blocks whose reference timing and text imply different owners.

    Returns:
        artifact containing two single-character blocks
    """
    sources = (
        AlignmentSource(name="whisper", backend="whisper", model="whisper"),
        AlignmentSource(name="mimo", backend="mlx", model="mimo"),
    )
    return AlignmentArtifact(
        language=Language.yue_hant,
        audio_duration_ms=2_000,
        sources=sources,
        blocks=(
            _get_character_block(1, 0, "甲", sources),
            _get_character_block(2, 1_000, "乙", sources),
        ),
    )


def _get_character_block(
    index: int, start_ms: int, text: str, sources: tuple[AlignmentSource, ...]
) -> AlignmentBlock:
    """Get one single-character artifact block for audit tests.

    Arguments:
        index: one-based block and subtitle index
        start_ms: block start time in milliseconds
        text: single-character transcription text
        sources: alignment sources represented in the block
    Returns:
        single-character alignment block
    """
    speech_start_ms = start_ms + 100
    speech_end_ms = start_ms + 300
    return AlignmentBlock(
        index=index,
        start_ms=start_ms,
        end_ms=start_ms + 1_000,
        columns=(
            AlignmentColumn(
                index=1, start_ms=speech_start_ms, end_ms=speech_end_ms, kind="text"
            ),
        ),
        rows=tuple(AlignmentRow(name=source.name, text=text) for source in sources),
        speaker="Ａ",
        merged=text,
        subtitles=(
            AlignmentSubtitle(
                index=index,
                text=text,
                speech_start_ms=speech_start_ms,
                speech_end_ms=speech_end_ms,
                timing_source="source",
                start_ms=start_ms,
                end_ms=start_ms + 500,
            ),
        ),
    )
