#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the OCR validate CLI."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.cli.ocr.ocr_validate_cli import OcrValidateCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core import ScinoephileError


def test_ocr_validate_cli(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test OCR validate CLI forwards workflow arguments.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    infile_path = tmp_path / "source.sup"
    infile_path.write_bytes(b"unused")
    outfile_path = tmp_path / "validated.srt"
    cache_dir_path = tmp_path / "cache"
    validate_calls: list[dict[str, object]] = []

    def fake_validate_ocr(
        infile_path_arg: Path,
        outfile_path_arg: Path,
        *,
        cache_dir_path: Path | str | None = None,
        dev: bool = False,
        overwrite: bool = False,
    ):
        """Capture OCR validation workflow arguments."""
        validate_calls.append(
            {
                "infile_path": infile_path_arg,
                "outfile_path": outfile_path_arg,
                "cache_dir_path": cache_dir_path,
                "dev": dev,
                "overwrite": overwrite,
            }
        )
        outfile_path_arg.write_text("validated", encoding="utf-8")

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.validate_ocr",
        fake_validate_ocr,
    )

    run_cli_with_args(
        OcrValidateCli,
        f"--infile {infile_path} --outfile {outfile_path} --cache-dir {cache_dir_path}",
    )

    assert validate_calls == [
        {
            "infile_path": infile_path,
            "outfile_path": outfile_path,
            "cache_dir_path": cache_dir_path.resolve(),
            "dev": False,
            "overwrite": False,
        }
    ]
    assert outfile_path.read_text(encoding="utf-8") == "validated"


def test_ocr_validate_cli_forwards_dev_and_overwrite(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test OCR validate CLI forwards dev and overwrite flags.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    infile_path = tmp_path / "image"
    infile_path.mkdir()
    outfile_path = tmp_path / "validated.srt"
    outfile_path.write_text("existing", encoding="utf-8")
    validate_calls: list[tuple[bool, bool]] = []

    def fake_validate_ocr(
        infile_path_arg: Path,
        outfile_path_arg: Path,
        *,
        cache_dir_path: Path | str | None = None,
        dev: bool = False,
        overwrite: bool = False,
    ):
        """Capture OCR validation workflow arguments."""
        _ = infile_path_arg, outfile_path_arg, cache_dir_path
        validate_calls.append((dev, overwrite))

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.validate_ocr",
        fake_validate_ocr,
    )

    run_cli_with_args(
        OcrValidateCli,
        f"--infile {infile_path} --outfile {outfile_path} --dev --overwrite",
    )

    assert validate_calls == [(True, True)]


def test_ocr_validate_cli_rejects_existing_outfile(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
):
    """Test OCR validate CLI rejects an existing outfile without overwrite.

    Arguments:
        capsys: pytest stdout and stderr capture fixture
        tmp_path: pytest temporary path fixture
    """
    infile_path = tmp_path / "source.sup"
    infile_path.write_bytes(b"unused")
    outfile_path = tmp_path / "validated.srt"
    outfile_path.write_text("existing", encoding="utf-8")

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            OcrValidateCli,
            f"--infile {infile_path} --outfile {outfile_path}",
        )

    captured = capsys.readouterr()
    assert f"{outfile_path} already exists" in captured.err


def test_ocr_validate_cli_reports_workflow_errors(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test OCR validate CLI reports workflow errors through argparse.

    Arguments:
        capsys: pytest stdout and stderr capture fixture
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    infile_path = tmp_path / "source.sup"
    infile_path.write_bytes(b"unused")

    def fake_validate_ocr(*args: object, **kwargs: object):
        """Raise a workflow-level validation error."""
        raise ScinoephileError("validation failed")

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.validate_ocr",
        fake_validate_ocr,
    )

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            OcrValidateCli,
            f"--infile {infile_path} --outfile {tmp_path / 'validated.srt'}",
        )

    captured = capsys.readouterr()
    assert "validation failed" in captured.err
