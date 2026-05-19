#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of OCR command-line interfaces."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from os import getenv
from pathlib import Path

import pytest

from scinoephile.cli.ocr import (
    OcrLensCli,
    OcrPaddleCli,
    OcrTesseractCli,
)
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.image.subtitles import ImageSeries
from test.helpers import (
    assert_series_equal,
    skip_if_ci,
    test_data_root,
)


def _patch_image_series_load(
    monkeypatch: pytest.MonkeyPatch,
    target: str,
    image_series: ImageSeries,
) -> list[Path]:
    """Patch image subtitle loading and return captured input paths.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        target: monkeypatch target for ImageSeries.load
        image_series: image subtitle series to return
    Returns:
        paths passed to ImageSeries.load
    """
    input_paths: list[Path] = []

    def fake_load(path: Path) -> ImageSeries:
        """Fake image subtitle loading.

        Arguments:
            path: image subtitle input path
        Returns:
            configured image subtitle series
        """
        input_paths.append(path)
        return image_series

    monkeypatch.setattr(target, fake_load)
    return input_paths


def _write_placeholder_sup_path(tmp_path: Path) -> Path:
    """Write a placeholder SUP file for CLI path validation.

    Arguments:
        tmp_path: pytest temporary path fixture
    Returns:
        placeholder SUP file path
    """
    infile_path = tmp_path / "source.sup"
    infile_path.write_bytes(b"unused")
    return infile_path


def test_ocr_lens_cli_help_lists_language_and_retry_options_only():
    """Test Google Lens CLI help lists supported operation options."""
    stdout = StringIO()
    stderr = StringIO()
    with pytest.raises(SystemExit) as excinfo:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(OcrLensCli, "-h")

    assert excinfo.value.code == 0
    assert stderr.getvalue() == ""
    help_text = " ".join(stdout.getvalue().split())
    assert "--language" in help_text
    assert "--retries" in help_text
    assert "--api-key" not in help_text
    assert "--client-region" not in help_text
    assert "--client-time-zone" not in help_text
    assert "--max-concurrent" not in help_text
    assert "--proxy" not in help_text
    assert "--timeout" not in help_text


def test_ocr_lens_cli_converts_image_subtitles_to_srt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test Google Lens CLI writes OCR output to SRT.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
        tiny_image_series: small image subtitle series
    """
    input_paths = _patch_image_series_load(
        monkeypatch,
        "scinoephile.cli.ocr.ocr_lens_cli.ImageSeries.load",
        tiny_image_series,
    )
    input_path = _write_placeholder_sup_path(tmp_path)
    observed_kwargs = []

    def fake_ocr_image_series_with_lens(*args: object, **kwargs: object) -> Series:
        """Fake Google Lens image series processing.

        Arguments:
            *args: positional arguments
            **kwargs: keyword arguments
        Returns:
            text subtitle series
        """
        observed_kwargs.append(kwargs)
        return Series(events=[Subtitle(start=1000, end=2000, text="recognized")])

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_lens_cli.ocr_image_series_with_lens",
        fake_ocr_image_series_with_lens,
    )

    output_path = tmp_path / "ocr.srt"
    run_cli_with_args(
        OcrLensCli,
        f"--infile {input_path} --outfile {output_path} --language zh-CN --retries 5",
    )

    assert input_paths == [input_path.resolve()]
    assert observed_kwargs == [{"language": "zh-CN", "retries": 5}]
    output = Series.load(output_path)
    assert [(event.start, event.end, event.text) for event in output] == [
        (1000, 2000, "recognized")
    ]


def test_ocr_paddle_cli_help_lists_language_codes():
    """Test PaddleOCR CLI help lists common subtitle language codes."""
    stdout = StringIO()
    stderr = StringIO()
    with pytest.raises(SystemExit) as excinfo:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(OcrPaddleCli, "-h")

    assert excinfo.value.code == 0
    assert stderr.getvalue() == ""
    help_text = " ".join(stdout.getvalue().split())
    assert "en (English)" in help_text
    assert "ch (simplified Chinese and English)" in help_text
    assert "chinese_cht (traditional Chinese)" in help_text


def test_ocr_tesseract_cli_help_lists_default_language():
    """Test Tesseract OCR CLI help lists default language code."""
    stdout = StringIO()
    stderr = StringIO()
    with pytest.raises(SystemExit) as excinfo:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(OcrTesseractCli, "-h")

    assert excinfo.value.code == 0
    assert stderr.getvalue() == ""
    help_text = " ".join(stdout.getvalue().split())
    assert "Tesseract language code installed in Tesseract" in help_text
    assert "such as eng or chi_sim (default: eng)" in help_text
    assert "run a second legacy-engine pass to detect italic text" in help_text


def test_ocr_paddle_cli_converts_image_subtitles_to_srt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test PaddleOCR CLI writes OCR output to SRT.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
        tiny_image_series: small image subtitle series
    """
    input_paths = _patch_image_series_load(
        monkeypatch,
        "scinoephile.cli.ocr.ocr_paddle_cli.ImageSeries.load",
        tiny_image_series,
    )
    input_path = _write_placeholder_sup_path(tmp_path)

    def fake_ocr_image_series_with_paddle(*args: object, **kwargs: object) -> Series:
        """Fake PaddleOCR image series processing.

        Arguments:
            *args: positional arguments
            **kwargs: keyword arguments
        Returns:
            text subtitle series
        """
        return Series(events=[Subtitle(start=1000, end=2000, text="recognized")])

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_paddle_cli.ocr_image_series_with_paddle",
        fake_ocr_image_series_with_paddle,
    )

    output_path = tmp_path / "ocr.srt"
    run_cli_with_args(
        OcrPaddleCli,
        f"--infile {input_path} --outfile {output_path}",
    )

    assert input_paths == [input_path.resolve()]
    output = Series.load(output_path)
    assert [(event.start, event.end, event.text) for event in output] == [
        (1000, 2000, "recognized")
    ]


def test_ocr_tesseract_cli_converts_image_subtitles_to_srt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test Tesseract OCR CLI writes OCR output to SRT.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
        tiny_image_series: small image subtitle series
    """
    input_paths = _patch_image_series_load(
        monkeypatch,
        "scinoephile.cli.ocr.ocr_tesseract_cli.ImageSeries.load",
        tiny_image_series,
    )
    input_path = _write_placeholder_sup_path(tmp_path)

    def fake_ocr_image_series_with_tesseract(*args: object, **kwargs: object) -> Series:
        """Fake Tesseract OCR image series processing.

        Arguments:
            *args: positional arguments
            **kwargs: keyword arguments
        Returns:
            text subtitle series
        """
        assert kwargs == {
            "detect_italics": False,
            "language": "eng",
        }
        return Series(events=[Subtitle(start=1000, end=2000, text="recognized")])

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_tesseract_cli.ocr_image_series_with_tesseract",
        fake_ocr_image_series_with_tesseract,
    )

    output_path = tmp_path / "ocr.srt"
    run_cli_with_args(
        OcrTesseractCli,
        f"--infile {input_path} --outfile {output_path}",
    )

    assert input_paths == [input_path.resolve()]
    output = Series.load(output_path)
    assert [(event.start, event.end, event.text) for event in output] == [
        (1000, 2000, "recognized")
    ]


def test_ocr_tesseract_cli_passes_italic_detection_options(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test Tesseract OCR CLI passes italic detection options.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
        tiny_image_series: small image subtitle series
    """
    input_paths = _patch_image_series_load(
        monkeypatch,
        "scinoephile.cli.ocr.ocr_tesseract_cli.ImageSeries.load",
        tiny_image_series,
    )
    input_path = _write_placeholder_sup_path(tmp_path)

    def fake_ocr_image_series_with_tesseract(*args: object, **kwargs: object) -> Series:
        """Fake Tesseract OCR image series processing.

        Arguments:
            *args: positional arguments
            **kwargs: keyword arguments
        Returns:
            text subtitle series
        """
        assert kwargs == {
            "detect_italics": True,
            "language": "eng",
        }
        return Series(events=[Subtitle(start=1000, end=2000, text="recognized")])

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_tesseract_cli.ocr_image_series_with_tesseract",
        fake_ocr_image_series_with_tesseract,
    )

    output_path = tmp_path / "ocr.srt"
    run_cli_with_args(
        OcrTesseractCli,
        f"--infile {input_path} --detect-italics --outfile {output_path}",
    )

    assert input_paths == [input_path.resolve()]
    output = Series.load(output_path)
    assert [(event.start, event.end, event.text) for event in output] == [
        (1000, 2000, "recognized")
    ]


def test_ocr_tesseract_cli_rejects_italic_detection_for_non_english(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test Tesseract OCR CLI rejects italic detection for non-English OCR."""
    input_path = test_data_root / "mlamd/input/zho-Hans_ocr/source.sup"
    output_path = tmp_path / "unused.srt"
    stderr = StringIO()

    def fail_ocr_image_series_with_tesseract(
        *args: object,
        **kwargs: object,
    ) -> Series:
        """Fail if OCR is invoked before argument validation."""
        _ = args, kwargs
        raise AssertionError("unexpected OCR")

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_tesseract_cli.ocr_image_series_with_tesseract",
        fail_ocr_image_series_with_tesseract,
    )

    with pytest.raises(SystemExit) as excinfo:
        with redirect_stderr(stderr):
            run_cli_with_args(
                OcrTesseractCli,
                f"--infile {input_path} "
                "--language chi_sim "
                "--detect-italics "
                f"--outfile {output_path}",
            )

    assert excinfo.value.code == 2
    assert "--detect-italics may only be used with --language eng" in stderr.getvalue()


@skip_if_ci()
@pytest.mark.skipif(
    not getenv("SCINOEPHILE_RUN_MLAMD_LENS_OCR"),
    reason=(
        "Set SCINOEPHILE_RUN_MLAMD_LENS_OCR=1 to run full MLAMD Google Lens OCR tests"
    ),
)
def test_ocr_lens_cli_matches_mlamd_sup_ocr_fixture(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test Google Lens CLI against a full MLAMD SUP subtitle fixture.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary path fixture
    """
    full_sup_path = test_data_root / "mlamd/input/eng_ocr/source.sup"
    full_expected_path = test_data_root / "mlamd/input/eng_ocr/lens.srt"
    monkeypatch.setenv("SCINOEPHILE_CACHE_DIR", str(tmp_path / "cache"))

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            OcrLensCli,
            f"--infile {full_sup_path} "
            "--language en "
            f"--outfile {output_path} "
            "--overwrite",
        )
        output = Series.load(output_path)
        expected = Series.load(full_expected_path)

    assert_series_equal(output, expected)


@skip_if_ci()
@pytest.mark.skipif(
    not getenv("SCINOEPHILE_RUN_MLAMD_PADDLE_OCR"),
    reason="Set SCINOEPHILE_RUN_MLAMD_PADDLE_OCR=1 to run full MLAMD PaddleOCR tests",
)
@pytest.mark.parametrize(
    (
        "sup_path",
        "language",
        "expected_path",
    ),
    [
        (
            "mlamd/input/eng_ocr/source.sup",
            "en",
            "mlamd/input/eng_ocr/paddle_new.srt",
        ),
        (
            "mlamd/input/zho-Hans_ocr/source.sup",
            "ch",
            "mlamd/input/zho-Hans_ocr/paddle_new.srt",
        ),
        (
            "mlamd/input/zho-Hant_ocr/source.sup",
            "chinese_cht",
            "mlamd/input/zho-Hant_ocr/paddle_new.srt",
        ),
    ],
)
def test_ocr_paddle_cli_matches_mlamd_sup_ocr_fixtures(
    monkeypatch: pytest.MonkeyPatch,
    sup_path: str,
    language: str,
    expected_path: str,
    tmp_path: Path,
):
    """Test PaddleOCR CLI against full MLAMD SUP subtitle fixtures.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        sup_path: source SUP subtitle path
        language: PaddleOCR language code
        expected_path: expected OCR subtitle fixture path
        tmp_path: temporary path fixture
    """
    full_sup_path = test_data_root / sup_path
    full_expected_path = test_data_root / expected_path
    monkeypatch.setenv("SCINOEPHILE_CACHE_DIR", str(tmp_path / "cache"))

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            OcrPaddleCli,
            f"--infile {full_sup_path} "
            f"--language {language} "
            f"--outfile {output_path} "
            "--overwrite",
        )
        output = Series.load(output_path)
        expected = Series.load(full_expected_path)

    assert_series_equal(output, expected)
