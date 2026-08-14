#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for the transcription audit command-line interface."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

from pytest import CaptureFixture, raises

from scinoephile.cli.audit.audit_transcription_cli import AuditTranscriptionCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core import Language
from scinoephile.lang.yue.transcription import YueTokenSimilarity


def test_audit_transcription_cli_help_and_validation(
    tmp_path: Path, capsys: CaptureFixture
):
    """Test help, argument parsing, and alignment artifact validation.

    Arguments:
        tmp_path: temporary path
        capsys: pytest stdout/stderr capture fixture
    """
    actions = {
        action.dest: action
        for action in AuditTranscriptionCli.argparser()._actions  # noqa: SLF001
    }
    assert actions["first_index"].help == (
        "first 1-indexed subtitle number to include, inclusive"
    )
    assert actions["first_block"].help == (
        "first 1-indexed subtitle block to process, inclusive"
    )
    assert actions["last_block"].help == (
        "last 1-indexed subtitle block to process, inclusive"
    )
    assert actions["alignment_path"].required
    assert actions["reference_specs"].metavar == "NAME=PATH"
    assert actions["reference_specs"].help == (
        "named independent reference SRT file as NAME=PATH; repeat for multiple "
        "references"
    )
    assert actions["include_timing_tables"].default is False
    assert actions["include_speaker"].default is False
    assert actions["include_language"].default is False
    assert actions["include_merge_support"].default is False
    assert actions["include_audio_events"].default is False

    invalid_path = tmp_path / "alignment.json"
    invalid_path.write_text("{}", encoding="utf-8")
    reference_path = tmp_path / "reference.srt"
    _write_srt(reference_path, ("係呀",))
    parsed = AuditTranscriptionCli.argparser().parse_args(
        [
            "--alignment",
            str(invalid_path),
            "--reference",
            f" zho-Hant = {reference_path} ",
            "--reference",
            f"yue-Hant={reference_path}",
            "--include-speaker",
            "--include-language",
            "--include-merge-support",
            "--include-audio-events",
            "--include-timing",
        ]
    )
    assert parsed.reference_specs == [
        ("zho-Hant", reference_path),
        ("yue-Hant", reference_path),
    ]
    assert parsed.include_speaker is True
    assert parsed.include_language is True
    assert parsed.include_merge_support is True
    assert parsed.include_audio_events is True
    assert parsed.include_timing_tables is True
    with raises(SystemExit):
        run_cli_with_args(AuditTranscriptionCli, f"--alignment {invalid_path}")
    assert "Unable to load transcription alignment artifact" in capsys.readouterr().err


def test_audit_transcription_cli_runs_with_yue_similarity(
    tmp_path: Path, capsys: CaptureFixture
):
    """Test input loading, Yue similarity, report generation, and output.

    Arguments:
        tmp_path: temporary path
        capsys: pytest stdout/stderr capture fixture
    """
    alignment_path = tmp_path / "alignment.json"
    alignment_path.write_text("{}", encoding="utf-8")
    reference_path = tmp_path / "reference.srt"
    _write_srt(reference_path, ("係呀",))
    artifact = Mock(language=Language.yue_hant)
    reference = Mock()

    with (
        patch(
            "scinoephile.cli.audit.audit_transcription_cli.AlignmentArtifact.load",
            return_value=artifact,
        ) as load_artifact,
        patch(
            "scinoephile.cli.audit.audit_transcription_cli.read_series",
            return_value=reference,
        ) as load_reference,
        patch(
            "scinoephile.cli.audit.audit_transcription_cli."
            "audit_transcription_alignment",
            return_value="# Audit\n",
        ) as audit,
    ):
        run_cli_with_args(
            AuditTranscriptionCli,
            (
                f"--alignment {alignment_path} "
                f"--reference reference={reference_path} "
                "--first-block 2 --last-block 3 "
                "--include-audio-events --include-language "
                "--include-merge-support --include-speaker --include-timing"
            ),
        )

    load_artifact.assert_called_once_with(alignment_path)
    load_reference.assert_called_once()
    assert load_reference.call_args.args[1] == reference_path
    reference_similarity = audit.call_args.kwargs["reference_similarity"]
    assert reference_similarity == YueTokenSimilarity()
    audit.assert_called_once_with(
        artifact,
        {"reference": reference},
        reference_similarity=reference_similarity,
        first_index=None,
        last_index=None,
        first_block=2,
        last_block=3,
        include_audio_events=True,
        include_language=True,
        include_merge_support=True,
        include_speaker=True,
        include_timing_tables=True,
    )
    assert capsys.readouterr().out == "# Audit\n"


def _write_srt(file_path: Path, texts: tuple[str, ...]):
    """Write subtitle text to a simple SRT fixture.

    Arguments:
        file_path: output SRT path
        texts: subtitle text by event
    """
    blocks = [
        f"{index}\n00:00:{index:02d},000 --> 00:00:{index:02d},500\n{text}"
        for index, text in enumerate(texts, 1)
    ]
    file_path.write_text(f"{'\n\n'.join(blocks)}\n", encoding="utf-8")
