#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.ocr.OcrProcessCli."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from scinoephile.cli.ocr.ocr_cli import OcrCli
from scinoephile.cli.ocr.ocr_process_cli import OcrProcessCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core import ScinoephileError
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

    with (
        patch(
            "scinoephile.cli.ocr.ocr_process_cli.get_provider",
            return_value=provider,
        ) as get_provider,
        patch(
            "scinoephile.cli.ocr.ocr_process_cli.process_eng_ocr",
            return_value=result,
        ) as process,
    ):
        run_cli_with_args(
            OcrProcessCli,
            f"--infile {infile_path} --stream-index 3 --language eng "
            f"-o {output_dir_path} --cache-dir {cache_dir_path} "
            "--clean --dev --overwrite",
        )

    get_provider.assert_called_once_with("openai", model=None)
    process.assert_called_once_with(
        infile_path=infile_path.resolve(),
        output_dir_path=output_dir_path.resolve(),
        stream_index=3,
        cache_dir_path=cache_dir_path.resolve(),
        clean=True,
        dev=True,
        overwrite=True,
        provider=provider,
        additional_context=None,
    )


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

    with (
        patch(
            "scinoephile.cli.ocr.ocr_process_cli.get_provider",
            return_value=provider,
        ),
        patch(
            "scinoephile.cli.ocr.ocr_process_cli.process_zho_ocr",
            return_value=result,
        ) as process,
    ):
        run_cli_with_args(
            OcrProcessCli,
            f"--infile {infile_path} --stream-index 3 --language zho "
            f"--clean -o {output_dir_path}",
        )

    process.assert_called_once_with(
        infile_path=infile_path.resolve(),
        output_dir_path=output_dir_path.resolve(),
        stream_index=3,
        cache_dir_path=get_runtime_cache_dir_path("media", "subtitles", create=False),
        script="simplified",
        clean=True,
        dev=False,
        overwrite=False,
        provider=provider,
        additional_context=None,
    )


def test_ocr_process_cli_passes_traditional_script_to_zho_workflow(tmp_path: Path):
    """Test OCR process CLI passes traditional script to Chinese workflow.

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

    with (
        patch(
            "scinoephile.cli.ocr.ocr_process_cli.get_provider",
            return_value=provider,
        ),
        patch(
            "scinoephile.cli.ocr.ocr_process_cli.process_zho_ocr",
            return_value=result,
        ) as process,
    ):
        run_cli_with_args(
            OcrProcessCli,
            f"--infile {infile_path} --stream-index 3 --language zho "
            f"--script traditional -o {output_dir_path}",
        )

    process.assert_called_once_with(
        infile_path=infile_path.resolve(),
        output_dir_path=output_dir_path.resolve(),
        stream_index=3,
        cache_dir_path=get_runtime_cache_dir_path("media", "subtitles", create=False),
        script="traditional",
        clean=False,
        dev=False,
        overwrite=False,
        provider=provider,
        additional_context=None,
    )


def test_ocr_process_cli_reports_workflow_errors(tmp_path: Path):
    """Test OCR process CLI maps workflow errors to parser errors.

    Arguments:
        tmp_path: pytest temporary path fixture
    """
    infile_path = tmp_path / "source.sup"
    infile_path.touch()

    with (
        patch(
            "scinoephile.cli.ocr.ocr_process_cli.process_eng_ocr",
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
