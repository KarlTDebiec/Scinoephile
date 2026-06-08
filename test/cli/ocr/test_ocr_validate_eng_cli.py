#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the OCR validate CLI for English subtitles."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.cli.ocr.ocr_validate_cli import OcrValidateCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core import ScinoephileError


@pytest.mark.parametrize(
    ("input_path",),
    [
        ("mlamd/output/eng_ocr/image",),
        ("mlamd/input/eng_ocr/source.sup",),
    ],
)
def test_ocr_validate_eng_cli(
    input_path: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test OCR validate CLI processing for English subtitles with directory output.

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

    def fake_validate_ocr(
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
        "scinoephile.cli.ocr.ocr_validate_cli.validate_ocr",
        fake_validate_ocr,
    )

    outfile_path = tmp_path / "validated.srt"
    cache_dir_path = tmp_path / "cache"
    run_cli_with_args(
        OcrValidateCli,
        f"--language eng --infile {infile_path} --outfile {outfile_path} "
        f"--cache-dir {cache_dir_path}",
    )

    assert validate_calls == [
        {
            "infile_path": infile_path,
            "language": "eng",
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


def test_ocr_validate_eng_cli_dev(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test OCR validate CLI forwards dev mode for English subtitles.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    validate_calls: list[dict[str, object]] = []

    def fake_validate_ocr(
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
        "scinoephile.cli.ocr.ocr_validate_cli.validate_ocr",
        fake_validate_ocr,
    )
    full_input_path = tmp_path / "image"
    full_input_path.mkdir()
    outfile_path = Path(tmp_path) / "validated.srt"
    cache_dir_path = tmp_path / "cache"

    run_cli_with_args(
        OcrValidateCli,
        f"--language eng --infile {full_input_path} --outfile {outfile_path} "
        f"--cache-dir {cache_dir_path} --dev",
    )

    assert validate_calls == [
        {
            "infile_path": full_input_path,
            "language": "eng",
            "outfile_path": outfile_path,
            "cache_dir_path": cache_dir_path.resolve(),
            "interactive": False,
            "dev": True,
            "overwrite": False,
            "host": "127.0.0.1",
            "port": 5000,
        }
    ]


def test_ocr_validate_eng_cli_web(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test OCR validate CLI launches web validation for English subtitles.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    infile_path = tmp_path / "image"
    infile_path.mkdir()
    (infile_path / "index.html").write_text("<html></html>", encoding="utf-8")
    validate_calls: list[dict[str, object]] = []

    def fake_validate_ocr(
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
        "scinoephile.cli.ocr.ocr_validate_cli.validate_ocr",
        fake_validate_ocr,
    )

    outfile_path = tmp_path / "validated.srt"
    cache_dir_path = tmp_path / "cache"
    run_cli_with_args(
        OcrValidateCli,
        f"--language eng --infile {infile_path} --interactive "
        f"--cache-dir {cache_dir_path} --outfile {outfile_path}",
    )

    assert validate_calls == [
        {
            "infile_path": infile_path,
            "language": "eng",
            "outfile_path": outfile_path,
            "cache_dir_path": cache_dir_path.resolve(),
            "interactive": True,
            "dev": False,
            "overwrite": False,
            "host": "127.0.0.1",
            "port": 5000,
        }
    ]


def test_ocr_validate_eng_cli_web_rejects_sup_input(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
):
    """Test OCR validate web mode requires a prepared OCR image directory.

    Arguments:
        capsys: pytest stdout and stderr capture fixture
        tmp_path: pytest temporary path fixture
    """
    infile_path = tmp_path / "source.sup"
    infile_path.write_bytes(b"unused")
    outfile_path = tmp_path / "validated.srt"

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            OcrValidateCli,
            f"--language eng --infile {infile_path} --interactive "
            f"--outfile {outfile_path}",
        )

    captured = capsys.readouterr()
    assert "must be a directory when --interactive is set" in captured.err


def test_ocr_validate_eng_cli_web_delegates_image_dir_validation(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test web mode lets the session validate OCR image directory contents.

    Arguments:
        capsys: pytest stdout and stderr capture fixture
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    infile_path = tmp_path / "image"
    infile_path.mkdir()

    def fake_validate_ocr(*args: object, **kwargs: object):
        """Raise the workflow-level validation error."""
        raise ScinoephileError("session checked OCR image directory")

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.validate_ocr",
        fake_validate_ocr,
    )

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            OcrValidateCli,
            f"--language eng --infile {infile_path} --interactive "
            f"--outfile {tmp_path / 'validated.srt'}",
        )

    captured = capsys.readouterr()
    assert "session checked OCR image directory" in captured.err


def test_ocr_validate_eng_cli_web_reports_run_error(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test OCR validate web mode maps app run errors to a parser error.

    Arguments:
        capsys: pytest stdout and stderr capture fixture
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    infile_path = tmp_path / "image"
    infile_path.mkdir()
    (infile_path / "index.html").write_text("<html></html>", encoding="utf-8")

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.validate_ocr",
        lambda *args, **kwargs: (_ for _ in ()).throw(ScinoephileError("port in use")),
    )

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            OcrValidateCli,
            f"--language eng --infile {infile_path} --interactive "
            f"--outfile {tmp_path / 'validated.srt'}",
        )

    captured = capsys.readouterr()
    assert "port in use" in captured.err
