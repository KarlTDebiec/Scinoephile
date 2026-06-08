#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the OCR validate CLI for standard Chinese subtitles."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.cli.ocr.ocr_validate_cli import OcrValidateCli
from scinoephile.common.testing import run_cli_with_args


@pytest.mark.parametrize(
    ("input_path",),
    [
        ("mlamd/output/zho-Hans_ocr/image",),
        ("mlamd/input/zho-Hans_ocr/source.sup",),
    ],
)
def test_ocr_validate_zho_cli(
    input_path: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test OCR validate CLI processing for standard Chinese subtitles.

    Arguments:
        input_path: path to input image subtitle fixture
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    infile_path = tmp_path / input_path
    infile_path.parent.mkdir(parents=True, exist_ok=True)
    if infile_path.suffix:
        infile_path.write_bytes(b"unused")
    else:
        infile_path.mkdir()

    validate_calls: list[dict[str, object]] = []

    def fake_validate_ocr_from_path(
        infile_path_arg: Path,
        language: str,
        outfile_path_arg: Path,
        *,
        cache_dir_path: Path | str | None = None,
        interactive: bool = False,
        dev: bool = False,
        overwrite: bool = False,
        host: str = "127.0.0.1",
        port: int = 5000,
    ):
        """Capture OCR validation workflow arguments."""
        validate_calls.append(
            {
                "infile_path": infile_path_arg,
                "language": language,
                "outfile_path": outfile_path_arg,
                "cache_dir_path": cache_dir_path,
                "interactive": interactive,
                "dev": dev,
                "overwrite": overwrite,
                "host": host,
                "port": port,
            }
        )
        outfile_path_arg.write_text("validated", encoding="utf-8")

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.validate_ocr_from_path",
        fake_validate_ocr_from_path,
    )

    outfile_path = tmp_path / "validated.srt"
    cache_dir_path = tmp_path / "cache"
    run_cli_with_args(
        OcrValidateCli,
        f"--language zho --infile {infile_path} --outfile {outfile_path} "
        f"--cache-dir {cache_dir_path}",
    )

    assert validate_calls == [
        {
            "infile_path": infile_path,
            "language": "zho",
            "outfile_path": outfile_path,
            "cache_dir_path": cache_dir_path.resolve(),
            "interactive": False,
            "dev": False,
            "overwrite": False,
            "host": "127.0.0.1",
            "port": 5000,
        }
    ]
    assert outfile_path.read_text(encoding="utf-8") == "validated"


def test_ocr_validate_zho_cli_dev(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test OCR validate CLI forwards dev mode for Chinese subtitles.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    validate_calls: list[dict[str, object]] = []

    def fake_validate_ocr_from_path(
        infile_path: Path,
        language: str,
        outfile_path: Path,
        *,
        cache_dir_path: Path | str | None = None,
        interactive: bool = False,
        dev: bool = False,
        overwrite: bool = False,
        host: str = "127.0.0.1",
        port: int = 5000,
    ):
        """Capture OCR validation workflow arguments."""
        validate_calls.append(
            {
                "infile_path": infile_path,
                "language": language,
                "outfile_path": outfile_path,
                "cache_dir_path": cache_dir_path,
                "interactive": interactive,
                "dev": dev,
                "overwrite": overwrite,
                "host": host,
                "port": port,
            }
        )

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.validate_ocr_from_path",
        fake_validate_ocr_from_path,
    )
    full_input_path = tmp_path / "image"
    full_input_path.mkdir()
    outfile_path = Path(tmp_path) / "validated.srt"
    cache_dir_path = tmp_path / "cache"

    run_cli_with_args(
        OcrValidateCli,
        f"--language zho --infile {full_input_path} --outfile {outfile_path} "
        f"--cache-dir {cache_dir_path} --dev",
    )

    assert validate_calls == [
        {
            "infile_path": full_input_path,
            "language": "zho",
            "outfile_path": outfile_path,
            "cache_dir_path": cache_dir_path.resolve(),
            "interactive": False,
            "dev": True,
            "overwrite": False,
            "host": "127.0.0.1",
            "port": 5000,
        }
    ]


def test_ocr_validate_zho_cli_web(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test OCR validate CLI launches web validation for Chinese subtitles.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    infile_path = tmp_path / "image"
    infile_path.mkdir()
    (infile_path / "index.html").write_text("<html></html>", encoding="utf-8")
    validate_calls: list[dict[str, object]] = []

    def fake_validate_ocr_from_path(
        infile_path_arg: Path,
        language: str,
        outfile_path_arg: Path,
        *,
        cache_dir_path: Path | str | None = None,
        interactive: bool = False,
        dev: bool = False,
        overwrite: bool = False,
        host: str = "127.0.0.1",
        port: int = 5000,
    ):
        """Capture OCR validation workflow arguments."""
        validate_calls.append(
            {
                "infile_path": infile_path_arg,
                "language": language,
                "outfile_path": outfile_path_arg,
                "cache_dir_path": cache_dir_path,
                "interactive": interactive,
                "dev": dev,
                "overwrite": overwrite,
                "host": host,
                "port": port,
            }
        )

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.validate_ocr_from_path",
        fake_validate_ocr_from_path,
    )

    outfile_path = tmp_path / "validated.srt"
    cache_dir_path = tmp_path / "cache"
    run_cli_with_args(
        OcrValidateCli,
        f"--language zho --infile {infile_path} --dev "
        f"--interactive --host 0.0.0.0 --port 5050 "
        f"--cache-dir {cache_dir_path} --outfile {outfile_path}",
    )

    assert validate_calls == [
        {
            "infile_path": infile_path,
            "language": "zho",
            "outfile_path": outfile_path,
            "cache_dir_path": cache_dir_path.resolve(),
            "interactive": True,
            "dev": True,
            "overwrite": False,
            "host": "0.0.0.0",
            "port": 5050,
        }
    ]
