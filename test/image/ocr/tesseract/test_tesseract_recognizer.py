#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Tesseract OCR recognition engines."""

from __future__ import annotations

from pathlib import Path

import requests
from PIL import Image
from pytest import MonkeyPatch, raises

from scinoephile.core import Language, ScinoephileError
from scinoephile.image.ocr.tesseract import TesseractRecognizer
from test.helpers import parametrize


class CountingTesseractRecognizer(TesseractRecognizer):
    """Tesseract recognizer that counts uncached recognitions."""

    def __init__(
        self,
        cache_dir_path: Path | None = None,
        *,
        language: Language = Language.eng,
    ):
        """Initialize.

        Arguments:
            cache_dir_path: directory in which to cache OCR results
            language: Scinoephile language
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
        return f"cached text {self.tesseract_language_code}"


def test_tesseract_recognizer_caches_results_by_image(tmp_path: Path):
    """Test Tesseract recognizer caches OCR results by image content."""
    recognizer = CountingTesseractRecognizer(cache_dir_path=tmp_path)
    image = Image.new("RGBA", (10, 8), (255, 255, 255, 0))

    assert recognizer.recognize_image(image) == "cached text eng"
    assert recognizer.recognize_image(image) == "cached text eng"

    assert recognizer.recognize_count == 1
    assert len(list(tmp_path.glob("*.json"))) == 1


@parametrize(
    ("language", "expected_code"),
    [
        (Language.eng, "eng"),
        (Language.yue_hans, "chi_sim"),
        (Language.yue_hant, "chi_tra"),
        (Language.zho_hans, "chi_sim"),
        (Language.zho_hant, "chi_tra"),
    ],
)
def test_tesseract_recognizer_maps_supported_languages_to_engine_codes(
    language: Language,
    expected_code: str,
):
    """Test Tesseract recognizer maps supported languages to engine codes.

    Arguments:
        language: language to use
        expected_code: expected Tesseract language code
    """
    recognizer = TesseractRecognizer(
        executable_path=Path("tesseract"),
        language=language,
        skip_executable_validation=True,
    )

    assert recognizer.language is language
    assert recognizer.tesseract_language_code == expected_code


def test_tesseract_recognizer_caches_by_configuration(tmp_path: Path):
    """Test Tesseract recognizer includes configuration in cache keys."""
    english_recognizer = CountingTesseractRecognizer(
        cache_dir_path=tmp_path,
        language=Language.eng,
    )
    chinese_recognizer = CountingTesseractRecognizer(
        cache_dir_path=tmp_path,
        language=Language.zho_hans,
    )
    image = Image.new("RGBA", (10, 8), (255, 255, 255, 0))

    assert english_recognizer.recognize_image(image) == "cached text eng"
    assert chinese_recognizer.recognize_image(image) == "cached text chi_sim"

    assert english_recognizer.recognize_count == 1
    assert chinese_recognizer.recognize_count == 1
    assert len(list(tmp_path.glob("*.json"))) == 2


def test_tesseract_recognizer_cache_key_ignores_engine_version(tmp_path: Path):
    """Test Tesseract recognizer cache keys do not include an engine version."""

    class VersionedCountingRecognizer(CountingTesseractRecognizer):
        """Counting recognizer with a legacy cache version attribute."""

        engine_version = "unused-version"

    image = Image.new("RGBA", (10, 8), (255, 255, 255, 0))
    unversioned_recognizer = CountingTesseractRecognizer(cache_dir_path=tmp_path)
    versioned_recognizer = VersionedCountingRecognizer(cache_dir_path=tmp_path)

    assert unversioned_recognizer.recognize_image(image) == "cached text eng"
    assert versioned_recognizer.recognize_image(image) == "cached text eng"

    assert unversioned_recognizer.recognize_count == 1
    assert versioned_recognizer.recognize_count == 0
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_tesseract_command_includes_hocr_tessdata_and_language(tmp_path: Path):
    """Test Tesseract command includes hOCR, tessdata, language, psm, and oem."""
    observed_command: list[str] = []
    tessdata_dir_path = tmp_path / "tessdata"
    tessdata_dir_path.mkdir()

    class CommandCapturingRecognizer(TesseractRecognizer):
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
        language=Language.eng,
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
    assert observed_command.index("--tessdata-dir") < observed_command.index("hocr")


def test_tesseract_chinese_hocr_words_are_joined_without_spaces():
    """Test Chinese hOCR word spans are joined without spaces."""

    class ChineseRecognizer(TesseractRecognizer):
        """Recognizer that writes Chinese hOCR output."""

        def _run_command(self, command: list[str]) -> tuple[int, str, str]:
            """Write fake hOCR output.

            Arguments:
                command: command arguments
            Returns:
                fake process result
            """
            output_base_path = Path(command[2])
            output_base_path.with_suffix(".hocr").write_text(
                (
                    "<span class='ocr_line'>"
                    "<span class='ocrx_word'>在</span>"
                    "<span class='ocrx_word'>麦</span>"
                    "<span class='ocrx_word'>太</span>"
                    "</span>"
                ),
                encoding="utf-8",
            )
            return 0, "", ""

    recognizer = ChineseRecognizer(
        executable_path=Path("tesseract"),
        language=Language.zho_hans,
        skip_executable_validation=True,
    )

    assert recognizer.recognize_image(Image.new("RGBA", (2, 2))) == "在麦太"


def test_tesseract_detect_italics_runs_legacy_hocr_pass(tmp_path: Path):
    """Test italic detection runs a legacy-engine hOCR pass."""
    observed_commands: list[list[str]] = []
    legacy_tessdata_dir_path = tmp_path / "legacy-tessdata"
    legacy_tessdata_dir_path.mkdir()
    (legacy_tessdata_dir_path / "eng.traineddata").touch()

    class CommandCapturingRecognizer(TesseractRecognizer):
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
        cache_dir_path=tmp_path,
        executable_path=Path("tesseract"),
        language=Language.eng,
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
    assert str(legacy_tessdata_dir_path.resolve()) in legacy_command
    assert "hocr" not in legacy_command


def test_tesseract_detect_italics_rejects_non_english_language():
    """Test italic detection is only supported for English Tesseract OCR."""
    with raises(ValueError, match="only supported with language eng"):
        TesseractRecognizer(
            executable_path=Path("tesseract"),
            detect_italics=True,
            language=Language.zho_hans,
            skip_executable_validation=True,
        )


def test_tesseract_detect_italics_downloads_missing_legacy_tessdata(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
):
    """Test italic detection downloads missing legacy traineddata lazily.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary path fixture
    """
    observed_urls: list[str] = []

    class FakeResponse:
        """Fake download response."""

        content = b"legacy traineddata"

        def raise_for_status(self):
            """Raise for unsuccessful response."""

    def fake_get(url: str, *, timeout: float) -> FakeResponse:
        """Record download URL and return fake response.

        Arguments:
            url: requested URL
            timeout: request timeout in seconds
        Returns:
            fake response
        """
        assert timeout == 60.0
        observed_urls.append(url)
        return FakeResponse()

    monkeypatch.setattr(requests, "get", fake_get)

    class CommandCapturingRecognizer(TesseractRecognizer):
        """Recognizer that writes primary and legacy hOCR output."""

        def _run_command(self, command: list[str]) -> tuple[int, str, str]:
            """Write hOCR output.

            Arguments:
                command: command arguments
            Returns:
                fake process result
            """
            output_base_path = Path(command[2])
            output_base_path.with_suffix(".hocr").write_text(
                "<span class='ocr_line'><span class='ocrx_word'>ok</span></span>",
                encoding="utf-8",
            )
            return 0, "", ""

    recognizer = CommandCapturingRecognizer(
        cache_dir_path=tmp_path,
        executable_path=Path("tesseract"),
        language=Language.eng,
        detect_italics=True,
        skip_executable_validation=True,
    )

    assert recognizer.recognize_image(Image.new("RGBA", (2, 2))) == "ok"
    assert observed_urls == [
        "https://raw.githubusercontent.com/tesseract-ocr/tessdata/master/"
        "eng.traineddata"
    ]
    assert (tmp_path / "legacy-tessdata" / "eng.traineddata").read_bytes() == (
        b"legacy traineddata"
    )


def test_tesseract_detect_italics_reuses_existing_legacy_tessdata(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
):
    """Test italic detection reuses cached legacy traineddata.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary path fixture
    """
    legacy_tessdata_dir_path = tmp_path / "legacy-tessdata"
    legacy_tessdata_dir_path.mkdir()
    (legacy_tessdata_dir_path / "eng.traineddata").write_bytes(b"existing")

    def fail_get(*args: object, **kwargs: object) -> object:
        """Fail if a download is attempted.

        Arguments:
            *args: positional arguments
            **kwargs: keyword arguments
        Returns:
            never returns
        Raises:
            AssertionError: always
        """
        _ = args, kwargs
        raise AssertionError("unexpected download")

    monkeypatch.setattr(requests, "get", fail_get)

    class CommandCapturingRecognizer(TesseractRecognizer):
        """Recognizer that writes primary and legacy hOCR output."""

        def _run_command(self, command: list[str]) -> tuple[int, str, str]:
            """Write hOCR output.

            Arguments:
                command: command arguments
            Returns:
                fake process result
            """
            output_base_path = Path(command[2])
            output_base_path.with_suffix(".hocr").write_text(
                "<span class='ocr_line'><span class='ocrx_word'>ok</span></span>",
                encoding="utf-8",
            )
            return 0, "", ""

    recognizer = CommandCapturingRecognizer(
        cache_dir_path=tmp_path,
        executable_path=Path("tesseract"),
        language=Language.eng,
        detect_italics=True,
        skip_executable_validation=True,
    )

    assert recognizer.recognize_image(Image.new("RGBA", (2, 2))) == "ok"


def test_tesseract_blank_english_result_uses_legacy_fallback(tmp_path: Path):
    """Test blank English OCR result falls back to legacy single-line OCR."""
    observed_commands: list[list[str]] = []
    legacy_tessdata_dir_path = tmp_path / "legacy-tessdata"
    legacy_tessdata_dir_path.mkdir()
    (legacy_tessdata_dir_path / "eng.traineddata").touch()

    class LegacyFallbackRecognizer(TesseractRecognizer):
        """Recognizer that simulates blank primary OCR and useful legacy OCR."""

        def _run_command(self, command: list[str]) -> tuple[int, str, str]:
            """Capture command and write fallback hOCR output.

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
                    "<span class='ocrx_word'>I...</span>"
                    "<span class='ocrx_word'>I...</span>"
                    "</span>"
                )
            else:
                hocr = "<span class='ocr_line'></span>"
            output_base_path.with_suffix(".hocr").write_text(hocr, encoding="utf-8")
            return 0, "", ""

    recognizer = LegacyFallbackRecognizer(
        cache_dir_path=tmp_path,
        executable_path=Path("tesseract"),
        language=Language.eng,
        skip_executable_validation=True,
    )

    assert recognizer.recognize_image(Image.new("RGBA", (2, 2))) == "I... I..."
    assert len(observed_commands) == 2

    fallback_command = observed_commands[1]
    assert "--oem" in fallback_command
    assert fallback_command[fallback_command.index("--oem") + 1] == "0"
    assert "--psm" in fallback_command
    assert fallback_command[fallback_command.index("--psm") + 1] == "7"
    assert "--tessdata-dir" in fallback_command
    assert str(legacy_tessdata_dir_path.resolve()) in fallback_command


def test_tesseract_blank_chinese_result_uses_legacy_fallback(tmp_path: Path):
    """Test blank Chinese OCR result falls back to legacy single-line OCR."""
    observed_commands: list[list[str]] = []
    legacy_tessdata_dir_path = tmp_path / "legacy-tessdata"
    legacy_tessdata_dir_path.mkdir()
    (legacy_tessdata_dir_path / "chi_tra.traineddata").touch()

    class LegacyFallbackRecognizer(TesseractRecognizer):
        """Recognizer that simulates blank primary OCR and useful legacy OCR."""

        def _run_command(self, command: list[str]) -> tuple[int, str, str]:
            """Capture command and write fallback hOCR output.

            Arguments:
                command: command arguments
            Returns:
                fake process result
            """
            observed_commands.append(command.copy())
            output_base_path = Path(command[2])
            if "--oem" in command and command[command.index("--oem") + 1] == "0":
                hocr = (
                    "<span class='ocr_line'><span class='ocrx_word'>你好</span></span>"
                )
            else:
                hocr = "<span class='ocr_line'></span>"
            output_base_path.with_suffix(".hocr").write_text(hocr, encoding="utf-8")
            return 0, "", ""

    recognizer = LegacyFallbackRecognizer(
        cache_dir_path=tmp_path,
        executable_path=Path("tesseract"),
        language=Language.zho_hant,
        skip_executable_validation=True,
    )

    assert recognizer.recognize_image(Image.new("RGBA", (2, 2))) == "你好"
    assert len(observed_commands) == 2


def test_tesseract_detect_italics_raises_clear_legacy_error(tmp_path: Path):
    """Test italic detection reports missing legacy model support clearly."""
    legacy_tessdata_dir_path = tmp_path / "legacy-tessdata"
    legacy_tessdata_dir_path.mkdir()
    (legacy_tessdata_dir_path / "eng.traineddata").touch()

    class LegacyFailingRecognizer(TesseractRecognizer):
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

    with raises(ScinoephileError, match="legacy Tesseract data"):
        recognizer.recognize_image(Image.new("RGBA", (2, 2)))

    assert list(tmp_path.glob("*.json")) == []


def test_tesseract_raises_and_does_not_cache_when_output_is_missing(tmp_path: Path):
    """Test successful Tesseract commands without hOCR output are not cached.

    Arguments:
        tmp_path: temporary directory path
    """

    class MissingOutputRecognizer(TesseractRecognizer):
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

    with raises(ValueError, match="did not produce hOCR output"):
        recognizer.recognize_image(Image.new("RGBA", (2, 2)))

    assert list(tmp_path.glob("*.json")) == []
