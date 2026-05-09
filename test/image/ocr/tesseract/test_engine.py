#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Tesseract OCR recognition engines."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from scinoephile.core import ScinoephileError
from scinoephile.image.ocr.tesseract import TesseractOcrRecognizer


class CountingTesseractOcrRecognizer(TesseractOcrRecognizer):
    """Tesseract recognizer that counts uncached recognitions."""

    def __init__(self, cache_dir_path: Path | None = None, *, language: str = "eng"):
        """Initialize.

        Arguments:
            cache_dir_path: directory in which to cache OCR results
            language: Tesseract language code
        """
        super().__init__(
            cache_dir_path=cache_dir_path,
            executable_path=Path("tesseract"),
            language=language,
            skip_executable_validation=True,
        )
        self.recognize_count = 0

    def _run_tesseract(self, image_path: Path, output_base_path: Path) -> str:
        """Run fake Tesseract.

        Arguments:
            image_path: input image path
            output_base_path: output base path
        Returns:
            recognized text
        """
        self.recognize_count += 1
        return f"cached text {self.language}"


def test_tesseract_ocr_recognizer_caches_results_by_image(tmp_path: Path):
    """Test Tesseract recognizer caches OCR results by image content."""
    recognizer = CountingTesseractOcrRecognizer(cache_dir_path=tmp_path)
    image = Image.new("RGBA", (10, 8), (255, 255, 255, 0))

    assert recognizer.recognize_image(image) == "cached text eng"
    assert recognizer.recognize_image(image) == "cached text eng"

    assert recognizer.recognize_count == 1
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_tesseract_ocr_recognizer_caches_by_configuration(tmp_path: Path):
    """Test Tesseract recognizer includes configuration in cache keys."""
    english_recognizer = CountingTesseractOcrRecognizer(
        cache_dir_path=tmp_path,
        language="eng",
    )
    french_recognizer = CountingTesseractOcrRecognizer(
        cache_dir_path=tmp_path,
        language="fra",
    )
    image = Image.new("RGBA", (10, 8), (255, 255, 255, 0))

    assert english_recognizer.recognize_image(image) == "cached text eng"
    assert french_recognizer.recognize_image(image) == "cached text fra"

    assert english_recognizer.recognize_count == 1
    assert french_recognizer.recognize_count == 1
    assert len(list(tmp_path.glob("*.json"))) == 2


def test_tesseract_command_includes_hocr_tessdata_and_language(tmp_path: Path):
    """Test Tesseract command includes hOCR, tessdata, language, psm, and oem."""
    observed_command: list[str] = []
    tessdata_dir_path = tmp_path / "tessdata"
    tessdata_dir_path.mkdir()

    class CommandCapturingRecognizer(TesseractOcrRecognizer):
        """Recognizer that captures command arguments."""

        def _run_command(self, command: list[str]) -> tuple[int, str, str]:
            """Capture command.

            Arguments:
                command: command arguments
            Returns:
                fake process result
            """
            observed_command.extend(command)
            output_base_path = Path(command[2])
            output_base_path.with_suffix(".hocr").write_text(
                "<span class='ocr_line'><span class='ocrx_word'>ok</span></span>",
                encoding="utf-8",
            )
            return 0, "", ""

    recognizer = CommandCapturingRecognizer(
        executable_path=Path("tesseract"),
        language="eng",
        tessdata_dir_path=tessdata_dir_path,
        skip_executable_validation=True,
    )

    assert recognizer.recognize_image(Image.new("RGBA", (2, 2))) == "ok"
    assert observed_command[:3] == [
        "tesseract",
        observed_command[1],
        observed_command[2],
    ]
    assert "-l" in observed_command
    assert "eng" in observed_command
    assert "--psm" in observed_command
    assert "6" in observed_command
    assert "--oem" in observed_command
    assert "3" in observed_command
    assert "hocr" in observed_command
    assert "--tessdata-dir" in observed_command
    assert str(tessdata_dir_path.resolve()) in observed_command


def test_tesseract_detect_italics_runs_legacy_hocr_pass(tmp_path: Path):
    """Test italic detection runs a legacy-engine hOCR pass."""
    observed_commands: list[list[str]] = []
    tessdata_dir_path = tmp_path / "legacy-tessdata"
    tessdata_dir_path.mkdir()

    class CommandCapturingRecognizer(TesseractOcrRecognizer):
        """Recognizer that captures primary and legacy command arguments."""

        def _run_command(self, command: list[str]) -> tuple[int, str, str]:
            """Capture command and write matching hOCR output.

            Arguments:
                command: command arguments
            Returns:
                fake process result
            """
            observed_commands.append(command.copy())
            output_base_path = Path(command[2])
            if "--oem" in command and command[command.index("--oem") + 1] == "0":
                hocr = (
                    "<span class='ocr_line'>"
                    "<span class='ocrx_word'><em>Hey,</em></span>"
                    "<span class='ocrx_word'>let's</span>"
                    "<span class='ocrx_word'>go</span>"
                    "</span>"
                )
            else:
                hocr = (
                    "<span class='ocr_line'>"
                    "<span class='ocrx_word'>Hey,</span>"
                    "<span class='ocrx_word'>let's</span>"
                    "<span class='ocrx_word'>go</span>"
                    "</span>"
                )
            output_base_path.with_suffix(".hocr").write_text(hocr, encoding="utf-8")
            return 0, "", ""

    recognizer = CommandCapturingRecognizer(
        executable_path=Path("tesseract"),
        language="eng",
        legacy_tessdata_dir_path=tessdata_dir_path,
        detect_italics=True,
        skip_executable_validation=True,
    )

    assert recognizer.recognize_image(Image.new("RGBA", (2, 2))) == (
        "<i>Hey,</i> let's go"
    )
    assert len(observed_commands) == 2

    primary_command = observed_commands[0]
    legacy_command = observed_commands[1]
    assert "hocr" in primary_command
    assert "--oem" in legacy_command
    assert legacy_command[legacy_command.index("--oem") + 1] == "0"
    assert "-c" in legacy_command
    assert "tessedit_create_hocr=1" in legacy_command
    assert "hocr_font_info=1" in legacy_command
    assert "--tessdata-dir" in legacy_command
    assert str(tessdata_dir_path.resolve()) in legacy_command
    assert "hocr" not in legacy_command


def test_tesseract_detect_italics_raises_clear_legacy_error(tmp_path: Path):
    """Test italic detection reports missing legacy model support clearly."""

    class LegacyFailingRecognizer(TesseractOcrRecognizer):
        """Recognizer that simulates a missing legacy Tesseract model."""

        def _run_command(self, command: list[str]) -> tuple[int, str, str]:
            """Write primary hOCR and fail the legacy pass.

            Arguments:
                command: command arguments
            Returns:
                fake process result
            """
            output_base_path = Path(command[2])
            if "--oem" in command and command[command.index("--oem") + 1] == "0":
                raise ValueError(
                    "Tesseract (legacy) engine requested, "
                    "but components are not present"
                )
            output_base_path.with_suffix(".hocr").write_text(
                "<span class='ocr_line'><span class='ocrx_word'>ok</span></span>",
                encoding="utf-8",
            )
            return 0, "", ""

    recognizer = LegacyFailingRecognizer(
        cache_dir_path=tmp_path,
        executable_path=Path("tesseract"),
        detect_italics=True,
        skip_executable_validation=True,
    )

    with pytest.raises(ScinoephileError, match="legacy Tesseract data"):
        recognizer.recognize_image(Image.new("RGBA", (2, 2)))

    assert list(tmp_path.glob("*.json")) == []


def test_tesseract_raises_and_does_not_cache_when_output_is_missing(
    tmp_path: Path,
):
    """Test successful Tesseract commands without hOCR output are not cached.

    Arguments:
        tmp_path: temporary directory path
    """

    class MissingOutputRecognizer(TesseractOcrRecognizer):
        """Recognizer that simulates a successful command without hOCR output."""

        def _run_command(self, command: list[str]) -> tuple[int, str, str]:
            """Pretend Tesseract ran successfully without writing output.

            Arguments:
                command: command arguments
            Returns:
                fake process result
            """
            return 0, "", ""

    recognizer = MissingOutputRecognizer(
        cache_dir_path=tmp_path,
        executable_path=Path("tesseract"),
        skip_executable_validation=True,
    )

    with pytest.raises(ValueError, match="did not produce hOCR output"):
        recognizer.recognize_image(Image.new("RGBA", (2, 2)))

    assert list(tmp_path.glob("*.json")) == []
