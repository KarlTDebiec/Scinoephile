#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the OCR editor's command-line entry point."""

from __future__ import annotations

from pathlib import Path

from pytest import CaptureFixture, MonkeyPatch, raises

from scinoephile.cli.ocr.ocr_cli import OcrCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.web.ocr_validation.session import OcrValidationSession
from test.helpers.ocr_validation import make_ocr_html_dir
from test.helpers.series_files import get_ocr_text_series


def test_ocr_serve_cli_resumes_from_the_image_index(
    monkeypatch: MonkeyPatch, tmp_path: Path
):
    """Open the editor on a prepared directory with an existing output.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: isolated OCR images, output, and validation data
    """
    images_path = make_ocr_html_dir(tmp_path, text="Saved review")
    outfile_path = tmp_path / "validated.srt"
    get_ocr_text_series("Older SRT output").save(outfile_path)
    validation_data_dir_path = tmp_path / "validation-data"
    calls = []

    def prepare_app(
        session: OcrValidationSession, host: str, port: int, *, title: str | None
    ):
        """Prepare the actual OCR session without blocking on the web server.

        Arguments:
            session: OCR session from the CLI
            host: host passed to the server
            port: port passed to the server
            title: display title passed to the server
        """
        calls.append((host, port, title))
        assert session.dir_path == images_path
        assert session.manager.validation_data_dir_path == validation_data_dir_path
        session.prepare()

    monkeypatch.setattr("scinoephile.workflows.ocr_validation.run_app", prepare_app)
    run_cli_with_args(
        OcrCli,
        f'serve -i "{images_path}" -o "{outfile_path}" '
        f'--validation-data-dir "{validation_data_dir_path}" '
        '--host localhost --port 5050 --title "Film - English"',
    )

    assert calls == [("localhost", 5050, "Film - English")]
    assert "Saved review" in outfile_path.read_text(encoding="utf-8")


def test_ocr_serve_cli_requires_an_image_index(
    capsys: CaptureFixture[str], tmp_path: Path
):
    """Report an invalid editor input as a CLI argument error.

    Arguments:
        capsys: pytest output capture fixture
        tmp_path: isolated directory lacking the required index
    """
    with raises(SystemExit, match="2"):
        run_cli_with_args(
            OcrCli, f'serve -i "{tmp_path}" -o "{tmp_path / "validated.srt"}"'
        )

    assert "index.html" in capsys.readouterr().err
