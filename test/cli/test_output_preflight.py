#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Reject existing subtitle outputs before processing or persistent LLM work."""

from __future__ import annotations

from importlib import import_module
from io import StringIO
from pathlib import Path
from unittest.mock import Mock

from pytest import CaptureFixture, MonkeyPatch, raises

from scinoephile.cli.multi.multi_stack_cli import MultiStackCli
from scinoephile.cli.multi.multi_sync_cli import MultiSyncCli
from scinoephile.cli.multi.multi_timewarp_cli import MultiTimewarpCli
from scinoephile.cli.ocr.ocr_fuse_cli import OcrFuseCli
from scinoephile.cli.process_cli import ProcessCli
from scinoephile.cli.review_cli import ReviewCli
from scinoephile.cli.translate_cli import TranslateCli
from scinoephile.core.cli.scinoephile_cli_base import ScinoephileCliBase
from scinoephile.core.subtitles import Series, Subtitle
from test.helpers import parametrize

_LLM_CASES = [
    (ReviewCli, ["{infile}", "--language", "eng"], "review_series"),
    (
        ReviewCli,
        ["{infile}", "--guide-infile", "{infile}", "--guide-language", "eng"],
        "review_series_guided",
    ),
    (TranslateCli, ["{infile}", "--target-language", "eng"], "translate_series"),
    (
        TranslateCli,
        ["{infile}", "--gapped-infile", "{infile}"],
        "translate_series_gaps",
    ),
    (
        TranslateCli,
        ["{infile}", "--guide-infile", "{infile}"],
        "translate_series_guided",
    ),
    (
        OcrFuseCli,
        [
            "--lens-infile",
            "{infile}",
            "--tesseract-infile",
            "{infile}",
            "--language",
            "eng",
        ],
        "fuse_ocr_series",
    ),
]


@parametrize(
    ("cli", "arguments", "workflow_name"),
    _LLM_CASES
    + [
        (
            ProcessCli,
            ["--infile", "{infile}", "--clean", "--language", "eng"],
            "clean_series",
        ),
        (
            MultiStackCli,
            ["--top-infile", "{infile}", "--bottom-infile", "{infile}"],
            "get_stacked_series",
        ),
        (
            MultiSyncCli,
            ["--anchor-infile", "{infile}", "--mobile-infile", "{infile}"],
            "get_sync_offset_stats",
        ),
        (
            MultiTimewarpCli,
            ["--anchor-infile", "{infile}", "--mobile-infile", "{infile}"],
            "get_series_timewarped",
        ),
    ],
)
def test_existing_output_stops_before_processing_or_persistence(
    cli: type[ScinoephileCliBase],
    arguments: list[str],
    workflow_name: str,
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
):
    """Leave existing subtitles and unused JSON/cache paths untouched on rejection.

    Arguments:
        cli: command whose output must be checked before work starts
        arguments: valid mode arguments with a placeholder input path
        workflow_name: expensive operation that must not run
        tmp_path: temporary directory containing authored output
        monkeypatch: fixture replacing readers, providers, and workflows
        capsys: fixture capturing the CLI's user-facing error
    """
    infile_path = tmp_path / "input.srt"
    Series(events=[Subtitle(start=0, end=1000, text="source")]).save(infile_path)
    outfile_path = tmp_path / "output.srt"
    outfile_path.write_text("authored subtitles", encoding="utf-8")
    json_path = tmp_path / "test-cases" / "cases.json"
    cache_dir_path = tmp_path / "cache"
    cli_arguments = [argument.format(infile=infile_path) for argument in arguments]
    module = import_module(cli.__module__)
    reader = Mock()
    workflow = Mock()
    provider = Mock()
    monkeypatch.setattr(module, "read_series", reader)
    monkeypatch.setattr(module, workflow_name, workflow)
    if cli in {ReviewCli, TranslateCli, OcrFuseCli}:
        monkeypatch.setattr(module, "get_provider", provider)
        cli_arguments.extend(
            ["--json", str(json_path), "--cache-dir", str(cache_dir_path)]
        )
    cli_arguments.extend(["--outfile", str(outfile_path)])

    with raises(SystemExit) as excinfo:
        cli.main(cli_arguments)

    assert excinfo.value.code == 2
    assert "already exists" in capsys.readouterr().err
    reader.assert_not_called()
    provider.assert_not_called()
    workflow.assert_not_called()
    assert outfile_path.read_text(encoding="utf-8") == "authored subtitles"
    assert not json_path.parent.exists()
    assert not cache_dir_path.exists()


@parametrize(("cli", "arguments", "workflow_name"), _LLM_CASES)
@parametrize("destination", ["overwrite", "stdout"])
def test_llm_operations_keep_overwrite_and_stdout_support(
    cli: type[ScinoephileCliBase],
    arguments: list[str],
    workflow_name: str,
    destination: str,
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Continue through the selected workflow when output is stdout or replaceable.

    Arguments:
        cli: LLM command to exercise without provider calls
        arguments: valid mode arguments with a placeholder input path
        workflow_name: workflow selected by those mode arguments
        destination: explicit overwrite or implicit stdout behavior
        tmp_path: temporary directory containing input and replaceable output
        monkeypatch: fixture replacing providers and expensive workflows
    """
    infile_path = tmp_path / "input.srt"
    Series(events=[Subtitle(start=0, end=1000, text="source")]).save(infile_path)
    outfile_path = tmp_path / "output.srt"
    outfile_path.write_text("authored subtitles", encoding="utf-8")
    output = Series(events=[Subtitle(start=0, end=1000, text="processed")])
    module = import_module(cli.__module__)
    workflow = Mock(return_value=output)
    monkeypatch.setattr(module, workflow_name, workflow)
    monkeypatch.setattr(module, "get_provider", Mock())
    stdout = StringIO()
    monkeypatch.setattr("scinoephile.cli.helpers.io.stdout", stdout)
    cli_arguments = [argument.format(infile=infile_path) for argument in arguments]
    if destination == "overwrite":
        cli_arguments.extend(["--outfile", str(outfile_path), "--overwrite"])

    cli.main(cli_arguments)

    workflow.assert_called_once()
    if destination == "overwrite":
        assert Series.load(outfile_path).events[0].text == "processed"
    else:
        assert "processed" in stdout.getvalue()
        assert outfile_path.read_text(encoding="utf-8") == "authored subtitles"
