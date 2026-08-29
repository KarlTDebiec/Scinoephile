#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.ocr.OcrProcessCli."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

from pytest import raises

from scinoephile.cli.ocr.ocr_cli import OcrCli
from scinoephile.cli.ocr.ocr_process_cli import OcrProcessCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core import Language, ScinoephileError
from scinoephile.workflows.ocr_processing import OcrProcessingResult


def test_ocr_process_cli_passes_eng_arguments_to_workflow(tmp_path: Path):
    """Test OCR process CLI passes English arguments to the workflow.

    Arguments:
        tmp_path: pytest temporary path fixture
    """
    infile_path = tmp_path / "movie.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "ocr"
    cache_root_path = tmp_path / "cache"
    expected_provider = object()
    result = OcrProcessingResult(
        infile_path=infile_path.resolve(),
        output_dir_path=output_dir_path.resolve(),
        output_paths={},
    )
    workflow_calls = 0

    class _Workflow:
        """Recording OCR processing workflow."""

        def __call__(self) -> OcrProcessingResult:
            """Record workflow execution.

            Returns:
                recorded workflow result
            """
            nonlocal workflow_calls
            workflow_calls += 1
            return result

    def get_provider(provider_name: str, *, model: str | None) -> object:
        """Validate provider options.

        Arguments:
            provider_name: provider name
            model: model
        Returns:
            provider
        """
        assert provider_name == "openai"
        assert model is None
        return expected_provider

    def get_workflow(
        workflow_infile_path: Path,
        workflow_output_dir_path: Path,
        *,
        language: Language,
        stream_index: int | None,
        cache_root_path: Path,
        clean: bool,
        interactive: bool,
        host: str,
        port: int,
        dev: bool,
        overwrite: bool,
        overwrite_cache: bool,
        provider: object,
        additional_context: str | None,
        fuser_kw: dict[str, Any],
    ) -> _Workflow:
        """Validate workflow arguments.

        Arguments:
            workflow_infile_path: workflow infile path
            workflow_output_dir_path: workflow output dir path
            language: language
            stream_index: stream index
            cache_root_path: cache root path
            clean: clean value
            interactive: interactive value
            host: host value
            port: port value
            dev: dev value
            overwrite: overwrite value
            overwrite_cache: overwrite cache
            provider: provider
            additional_context: additional context value
            fuser_kw: fuser kw value
        Returns:
            workflow
        """
        assert workflow_infile_path == infile_path.resolve()
        assert workflow_output_dir_path == output_dir_path.resolve()
        assert language is Language.eng
        assert stream_index == 3
        assert cache_root_path == (tmp_path / "cache").resolve()
        assert clean is True
        assert interactive is True
        assert host == "0.0.0.0"
        assert port == 5051
        assert dev is True
        assert overwrite is True
        assert overwrite_cache is True
        assert provider is expected_provider
        assert additional_context is None
        assert fuser_kw == {"no_op": True}
        return _Workflow()

    with (
        patch(
            "scinoephile.cli.ocr.ocr_process_cli.get_provider", side_effect=get_provider
        ),
        patch(
            "scinoephile.cli.ocr.ocr_process_cli.OcrProcessingWorkflow",
            side_effect=get_workflow,
        ),
    ):
        run_cli_with_args(
            OcrProcessCli,
            f"--infile {infile_path} --stream-index 3 --language eng "
            f"-o {output_dir_path} --cache-dir {cache_root_path} "
            "--clean --interactive --host 0.0.0.0 --port 5051 --dev "
            "--overwrite --cache-overwrite --llm-no-op",
        )

    assert workflow_calls == 1


def test_ocr_process_cli_reports_workflow_errors(tmp_path: Path):
    """Test OCR process CLI maps workflow errors to parser errors.

    Arguments:
        tmp_path: pytest temporary path fixture
    """
    infile_path = tmp_path / "source.sup"
    infile_path.touch()

    with (
        patch(
            "scinoephile.cli.ocr.ocr_process_cli.OcrProcessingWorkflow",
            side_effect=ScinoephileError("No subtitle stream 3 found"),
        ),
        raises(SystemExit) as excinfo,
    ):
        run_cli_with_args(
            OcrProcessCli,
            f"--infile {infile_path} --language eng -o {tmp_path / 'ocr'}",
        )

    assert excinfo.value.code == 2


def test_ocr_cli_includes_process_subcommand():
    """Test top-level OCR CLI exposes OCR processing."""
    assert OcrCli.subcommands()["process"] is OcrProcessCli
