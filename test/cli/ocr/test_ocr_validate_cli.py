#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the OCR validate CLI."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.cli.ocr.ocr_validate_cli import OcrValidateCli
from scinoephile.common.testing import run_cli_with_args


def test_ocr_validate_cli(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test OCR validate CLI forwards noninteractive workflow arguments.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    infile_path = tmp_path / "source.sup"
    infile_path.parent.mkdir(parents=True, exist_ok=True)
    infile_path.write_bytes(b"unused")

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

    outfile_path = tmp_path / "validated.srt"
    cache_dir_path = tmp_path / "cache"
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
