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
    original_load = ImageSeries.load
    infile_path = tmp_path / input_path
    infile_path.parent.mkdir(parents=True, exist_ok=True)
    if infile_path.suffix:
        infile_path.write_bytes(b"unused")
    else:
        infile_path.mkdir()

    load_paths: list[Path] = []
    validate_calls: list[tuple[ImageSeries, int | None, bool, bool]] = []

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
        stop_at_idx: int | None = None,
        interactive: bool = False,
        dev: bool = False,
    ) -> ImageSeries:
        """Fake English OCR validation.

        Arguments:
            series: ImageSeries to validate
            stop_at_idx: stop processing at this index
            interactive: whether to prompt user for confirmations
            dev: whether to write validation data updates to the repo
        Returns:
            configured validated image series
        """
        validate_calls.append((series, stop_at_idx, interactive, dev))
        return tiny_image_series

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.ImageSeries.load",
        fake_load,
    )
    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.validate_eng_ocr",
        fake_validate_eng_ocr,
    )

    outfile_path = tmp_path / "validated"
    run_cli_with_args(
        OcrValidateCli,
        f"--language eng --infile {infile_path} --stop-at-idx 1 "
        f"--outfile {outfile_path}",
    )

    assert load_paths == [infile_path]
    assert validate_calls == [(tiny_image_series, 1, False, False)]
    output = original_load(outfile_path)
    assert len(output) == len(tiny_image_series)
    assert (outfile_path / "index.html").exists()
    assert len(list(outfile_path.glob("*.png"))) == len(tiny_image_series)


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
        stop_at_idx: int | None = None,
        interactive: bool = False,
        dev: bool = False,
    ) -> ImageSeries:
        """Mock English OCR validation.

        Arguments:
            series: ImageSeries to validate
            stop_at_idx: stop processing at this index
            interactive: whether to prompt user for confirmations
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
    outfile_path = Path(tmp_path) / "validated"

    run_cli_with_args(
        OcrValidateCli,
        f"--language eng --infile {full_input_path} --outfile {outfile_path} --dev",
    )

    assert captured_dev is True
