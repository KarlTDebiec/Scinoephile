#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the OCR validate CLI for English subtitles."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.cli.ocr.ocr_validate_cli import OcrValidateCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core import ScinoephileError
from scinoephile.image.subtitles import ImageSeries


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
    tiny_image_series: ImageSeries,
):
    """Test OCR validate CLI processing for English subtitles with directory output.

    Arguments:
        input_path: path to input image subtitle fixture
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
        tiny_image_series: small image subtitle series
    """
    infile_path = tmp_path / input_path
    infile_path.parent.mkdir(parents=True, exist_ok=True)
    if infile_path.suffix:
        infile_path.write_bytes(b"unused")
    else:
        infile_path.mkdir()

    validate_calls: list[tuple[Path, str, Path, bool]] = []

    def fake_validate_ocr(
        path: Path,
        language: str,
        *,
        cache_dir_path: Path,
        dev: bool = False,
    ) -> ImageSeries:
        """Fake OCR validation workflow."""
        validate_calls.append((path, language, cache_dir_path, dev))
        return tiny_image_series

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

    assert validate_calls == [(infile_path, "eng", cache_dir_path.resolve(), False)]
    output = outfile_path.read_text(encoding="utf-8")
    assert "recognized" in output
    assert "validated" in output


def test_ocr_validate_eng_cli_dev(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test OCR validate CLI forwards dev mode for English subtitles.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
        tiny_image_series: small image subtitle series
    """
    validate_calls: list[tuple[Path, str, Path, bool]] = []

    def fake_validate_ocr(
        path: Path,
        language: str,
        *,
        cache_dir_path: Path,
        dev: bool = False,
    ) -> ImageSeries:
        """Fake OCR validation workflow."""
        validate_calls.append((path, language, cache_dir_path, dev))
        return tiny_image_series

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

    assert validate_calls == [(full_input_path, "eng", cache_dir_path.resolve(), True)]


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
    run_calls: list[tuple[Path, Path, Path, str, int, bool]] = []

    def fake_run_ocr_validation_web(
        path: Path,
        outfile_path: Path,
        cache_dir_path: Path,
        *,
        host: str,
        port: int,
        dev: bool,
    ):
        """Capture web validation workflow arguments."""
        run_calls.append((path, outfile_path, cache_dir_path, host, port, dev))

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.run_ocr_validation_web",
        fake_run_ocr_validation_web,
    )

    outfile_path = tmp_path / "validated.srt"
    cache_dir_path = tmp_path / "cache"
    run_cli_with_args(
        OcrValidateCli,
        f"--language eng --infile {infile_path} --interactive "
        f"--cache-dir {cache_dir_path} --outfile {outfile_path}",
    )

    assert run_calls == [
        (infile_path, outfile_path, cache_dir_path.resolve(), "127.0.0.1", 5000, False)
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

    def fake_run_ocr_validation_web(*args: object, **kwargs: object):
        """Raise the workflow-level validation error."""
        raise ScinoephileError("session checked OCR image directory")

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.run_ocr_validation_web",
        fake_run_ocr_validation_web,
    )

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            OcrValidateCli,
            f"--language eng --infile {infile_path} --interactive "
            f"--outfile {tmp_path / 'validated.srt'}",
        )

    captured = capsys.readouterr()
    assert "session checked OCR image directory" in captured.err


def test_ocr_validate_eng_cli_web_reports_missing_dependency(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test OCR validate web mode maps missing Flask to a parser error.

    Arguments:
        capsys: pytest stdout and stderr capture fixture
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    infile_path = tmp_path / "image"
    infile_path.mkdir()
    (infile_path / "index.html").write_text("<html></html>", encoding="utf-8")

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.run_ocr_validation_web",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            ScinoephileError("Install with 'web' extra")
        ),
    )

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            OcrValidateCli,
            f"--language eng --infile {infile_path} --interactive "
            f"--outfile {tmp_path / 'validated.srt'}",
        )

    captured = capsys.readouterr()
    assert "Install with 'web' extra" in captured.err
