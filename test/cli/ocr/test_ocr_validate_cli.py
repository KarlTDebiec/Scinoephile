#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the OCR validate CLI."""

from __future__ import annotations

from pathlib import Path

from pytest import MonkeyPatch

from scinoephile.cli.ocr.ocr_validate_cli import OcrValidateCli
from scinoephile.common.testing import run_cli_with_args


def test_ocr_validate_cli(monkeypatch: MonkeyPatch, tmp_path: Path):
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
        validation_data_dir_path: Path | str | None = None,
        dev: bool = False,
        overwrite: bool = False,
    ):
        """Capture OCR validation workflow arguments.

        Arguments:
            infile_path_arg: infile path arg value
            outfile_path_arg: outfile path arg value
            validation_data_dir_path: validation data dir path
            dev: dev value
            overwrite: overwrite value
        """
        validate_calls.append(
            {
                "infile_path": infile_path_arg,
                "outfile_path": outfile_path_arg,
                "validation_data_dir_path": validation_data_dir_path,
                "dev": dev,
                "overwrite": overwrite,
            }
        )
        outfile_path_arg.write_text("validated", encoding="utf-8")

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.validate_ocr", fake_validate_ocr
    )

    outfile_path = tmp_path / "validated.srt"
    validation_data_dir_path = tmp_path / "validation-data"
    run_cli_with_args(
        OcrValidateCli,
        f"--infile {infile_path} --outfile {outfile_path} "
        f"--validation-data-dir {validation_data_dir_path}",
    )

    assert validate_calls == [
        {
            "infile_path": infile_path,
            "outfile_path": outfile_path,
            "validation_data_dir_path": validation_data_dir_path.resolve(),
            "dev": False,
            "overwrite": False,
        }
    ]
    assert outfile_path.read_text(encoding="utf-8") == "validated"


def test_ocr_validate_cli_names_persistent_data_separately_from_cache():
    """Test validation data is not presented as a disposable cache."""
    help_text = OcrValidateCli.argparser().format_help()

    assert "--validation-data-dir VALIDATION_DATA_DIR" in help_text
    assert "local OCR validation data directory path" in help_text
    assert "--cache-dir" not in help_text
    assert "--cache-overwrite" not in help_text


def test_ocr_validate_cli_has_no_server_options():
    """Keep the batch command separate from launching the editor."""
    help_text = OcrValidateCli.argparser().format_help()

    for option in ("--interactive", "--host", "--port", "--title"):
        assert option not in help_text
