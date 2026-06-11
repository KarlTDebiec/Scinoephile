#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.ocr.OcrProcessCli."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from scinoephile.cli.ocr.ocr_cli import OcrCli
from scinoephile.cli.ocr.ocr_process_cli import OcrProcessCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.workflows.ocr_processing import OcrProcessingResult


def test_ocr_process_cli_passes_eng_arguments_to_workflow(tmp_path: Path):
    """Test OCR process CLI passes English arguments to the workflow.

    Arguments:
        tmp_path: pytest temporary path fixture
    """
    infile_path = tmp_path / "movie.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "ocr"
    cache_dir_path = tmp_path / "cache"
    provider = object()
    result = OcrProcessingResult(
        infile_path=infile_path.resolve(),
        output_dir_path=output_dir_path.resolve(),
        output_paths={},
    )
    workflow = Mock(return_value=result)

    with (
        patch(
            "scinoephile.cli.ocr.ocr_process_cli.get_provider",
            return_value=provider,
        ) as get_provider,
        patch(
            "scinoephile.cli.ocr.ocr_process_cli.OcrProcessingWorkflow",
            return_value=workflow,
        ) as workflow_cls,
    ):
        run_cli_with_args(
            OcrProcessCli,
            f"--infile {infile_path} --stream-index 3 --language eng "
            f"-o {output_dir_path} --cache-dir {cache_dir_path} "
            "--clean --interactive --host 0.0.0.0 --port 5051 --dev "
            "--overwrite",
        )

    get_provider.assert_called_once_with("openai", model=None)
    workflow_cls.assert_called_once_with(
        infile_path.resolve(),
        output_dir_path.resolve(),
        language=Language.eng,
        stream_index=3,
        cache_dir_path=cache_dir_path.resolve(),
        clean=True,
        interactive=True,
        host="0.0.0.0",
        port=5051,
        dev=True,
        overwrite=True,
        provider=provider,
        additional_context=None,
    )
    workflow.assert_called_once_with()


def test_ocr_process_cli_passes_zho_arguments_to_workflow(tmp_path: Path):
    """Test OCR process CLI passes Chinese arguments to the workflow.

    Arguments:
        tmp_path: pytest temporary path fixture
    """
    infile_path = tmp_path / "movie.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "ocr"
    provider = object()
    result = OcrProcessingResult(
        infile_path=infile_path.resolve(),
        output_dir_path=output_dir_path.resolve(),
        output_paths={},
    )
    workflow = Mock(return_value=result)

    with (
        patch(
            "scinoephile.cli.ocr.ocr_process_cli.get_provider",
            return_value=provider,
        ),
        patch(
            "scinoephile.cli.ocr.ocr_process_cli.OcrProcessingWorkflow",
            return_value=workflow,
        ) as workflow_cls,
    ):
        run_cli_with_args(
            OcrProcessCli,
            f"--infile {infile_path} --stream-index 3 --language zho-Hans "
            f"--clean -o {output_dir_path}",
        )

    workflow_cls.assert_called_once_with(
        infile_path.resolve(),
        output_dir_path.resolve(),
        language=Language.zho_hans,
        stream_index=3,
        cache_dir_path=get_runtime_cache_dir_path("media", "subtitles", create=False),
        clean=True,
        interactive=False,
        host="127.0.0.1",
        port=5000,
        dev=False,
        overwrite=False,
        provider=provider,
        additional_context=None,
    )
    workflow.assert_called_once_with()


def test_ocr_process_cli_passes_zho_hant_language_to_workflow(tmp_path: Path):
    """Test OCR process CLI passes zho-Hant language to workflow.

    Arguments:
        tmp_path: pytest temporary path fixture
    """
    infile_path = tmp_path / "movie.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "ocr"
    provider = object()
    result = OcrProcessingResult(
        infile_path=infile_path.resolve(),
        output_dir_path=output_dir_path.resolve(),
        output_paths={},
    )
    workflow = Mock(return_value=result)

    with (
        patch(
            "scinoephile.cli.ocr.ocr_process_cli.get_provider",
            return_value=provider,
        ),
        patch(
            "scinoephile.cli.ocr.ocr_process_cli.OcrProcessingWorkflow",
            return_value=workflow,
        ) as workflow_cls,
    ):
        run_cli_with_args(
            OcrProcessCli,
            f"--infile {infile_path} --stream-index 3 --language zho-Hant "
            f"-o {output_dir_path}",
        )

    workflow_cls.assert_called_once_with(
        infile_path.resolve(),
        output_dir_path.resolve(),
        language=Language.zho_hant,
        stream_index=3,
        cache_dir_path=get_runtime_cache_dir_path("media", "subtitles", create=False),
        clean=False,
        interactive=False,
        host="127.0.0.1",
        port=5000,
        dev=False,
        overwrite=False,
        provider=provider,
        additional_context=None,
    )
    workflow.assert_called_once_with()


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
        pytest.raises(SystemExit) as excinfo,
    ):
        run_cli_with_args(
            OcrProcessCli,
            f"--infile {infile_path} --language eng -o {tmp_path / 'ocr'}",
        )

    assert excinfo.value.code == 2


def test_ocr_cli_includes_process_subcommand():
    """Test top-level OCR CLI exposes OCR processing."""
    assert OcrCli.subcommands()["process"] is OcrProcessCli
