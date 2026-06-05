#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the OCR validate CLI for English subtitles."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.cli.ocr.ocr_validate_cli import OcrValidateCli
from scinoephile.common.testing import run_cli_with_args
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

    load_paths: list[Path] = []
    validate_calls: list[tuple[ImageSeries, bool]] = []

    def fake_load(path: Path) -> ImageSeries:
        """Fake image subtitle loading.

        Arguments:
            path: image subtitle input path
        Returns:
            configured image subtitle series
        """
        load_paths.append(path)
        return tiny_image_series

    def fake_validate_eng_ocr(
        series: ImageSeries,
        dev: bool = False,
    ) -> ImageSeries:
        """Fake English OCR validation.

        Arguments:
            series: ImageSeries to validate
            dev: whether to write validation data updates to the repo
        Returns:
            configured validated image series
        """
        validate_calls.append((series, dev))
        return tiny_image_series

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.ImageSeries.load",
        fake_load,
    )
    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.validate_eng_ocr",
        fake_validate_eng_ocr,
    )

    outfile_path = tmp_path / "validated.srt"
    run_cli_with_args(
        OcrValidateCli,
        f"--language eng --infile {infile_path} --outfile {outfile_path}",
    )

    assert load_paths == [infile_path]
    assert validate_calls == [(tiny_image_series, False)]
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
    captured_dev = None

    def fake_load(path: Path) -> ImageSeries:
        """Fake image subtitle loading.

        Arguments:
            path: image subtitle input path
        Returns:
            configured image subtitle series
        """
        _ = path
        return tiny_image_series

    def mock_validate_eng_ocr(
        series: ImageSeries,
        dev: bool = False,
    ) -> ImageSeries:
        """Mock English OCR validation.

        Arguments:
            series: ImageSeries to validate
            dev: whether to write validation data updates to the repo
        Returns:
            input image series
        """
        nonlocal captured_dev
        captured_dev = dev
        return series

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.validate_eng_ocr",
        mock_validate_eng_ocr,
    )
    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.ImageSeries.load",
        fake_load,
    )
    full_input_path = tmp_path / "image"
    full_input_path.mkdir()
    outfile_path = Path(tmp_path) / "validated.srt"

    run_cli_with_args(
        OcrValidateCli,
        f"--language eng --infile {full_input_path} --outfile {outfile_path} --dev",
    )

    assert captured_dev is True


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
    run_calls = []
    session = object()

    def fake_session_from_dir_path(
        dir_path: Path,
        *,
        outfile_path: Path | None = None,
        dev: bool = False,
    ) -> object:
        """Capture web session construction arguments."""
        run_calls.append(("from_dir_path", dir_path, outfile_path, dev))
        return session

    class FakeFlaskApp:
        """Fake OCR validation Flask app."""

        def run(
            self,
            *,
            host: str = "127.0.0.1",
            port: int = 5000,
        ):
            """Capture web app run arguments."""
            run_calls.append(("run", host, port))

    def fake_create_app(value: object) -> FakeFlaskApp:
        """Capture Flask app construction arguments."""
        run_calls.append(("create_app", value))
        return FakeFlaskApp()

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.OcrValidationSession.from_dir_path",
        fake_session_from_dir_path,
    )
    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.create_app",
        fake_create_app,
    )

    outfile_path = tmp_path / "validated.srt"
    run_cli_with_args(
        OcrValidateCli,
        f"--language eng --infile {infile_path} --interactive --outfile {outfile_path}",
    )

    assert run_calls == [
        ("from_dir_path", infile_path, outfile_path, False),
        ("create_app", session),
        ("run", "127.0.0.1", 5000),
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
