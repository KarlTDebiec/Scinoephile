#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for processing image subtitle OCR end to end."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import Any

from scinoephile.common.argument_parsing import enum_options_list_str
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series
from scinoephile.image.ocr.lens import (
    ocr_image_series_with_lens,
)
from scinoephile.image.ocr.paddle import ocr_image_series_with_paddle
from scinoephile.image.ocr.tesseract import (
    ocr_image_series_with_tesseract,
)
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.eng.cleaning import get_eng_cleaned
from scinoephile.lang.eng.ocr_fusion import get_eng_ocr_fused, get_eng_ocr_fuser
from scinoephile.lang.zho.cleaning import get_zho_cleaned
from scinoephile.lang.zho.ocr_fusion import (
    OcrFusionPromptZhoHant,
    get_zho_ocr_fused,
    get_zho_ocr_fuser,
)
from scinoephile.media.subtitles.cache import (
    cache_subtitles,
    get_subtitle_cache_path,
)
from scinoephile.media.subtitles.selection import get_media_subtitle_stream

from .ocr_validation import validate_ocr

__all__ = [
    "OcrProcessingResult",
    "OcrProcessingWorkflow",
]

logger = getLogger(__name__)


@dataclass(frozen=True)
class OcrProcessingResult:
    """Result of an OCR processing workflow run."""

    infile_path: Path
    """Input path processed by the workflow."""
    output_dir_path: Path
    """Directory containing workflow outputs."""
    output_paths: dict[str, Path]
    """Output paths keyed by output name."""


class OcrProcessingWorkflow:
    """Workflow for processing image subtitle OCR end to end."""

    def __init__(
        self,
        infile_path: Path,
        output_dir_path: Path,
        *,
        language: Language | str,
        stream_index: int | None = None,
        cache_dir_path: Path | None = None,
        clean: bool = False,
        validate: bool = True,
        interactive: bool = False,
        dev: bool = False,
        overwrite: bool = False,
        provider: LLMProvider | None = None,
        additional_context: str | None = None,
        fuser_kw: dict[str, Any] | None = None,
        host: str = "127.0.0.1",
        port: int = 5000,
    ):
        """Initialize.

        Arguments:
            infile_path: SUP, image subtitle directory, or media input path
            output_dir_path: directory where OCR outputs are written
            language: OCR text language to process
            stream_index: media subtitle stream index when infile is media
            cache_dir_path: media subtitle cache directory path
            clean: whether to clean OCR subtitle outputs before fusing
            validate: whether to validate fused OCR subtitles against images
            interactive: whether to launch the OCR validation web UI
            dev: whether validation should write data updates to repo data
            overwrite: whether to overwrite existing workflow outputs
            provider: provider to use for OCR fusion queries
            additional_context: additional context to include in OCR fusion prompts
            fuser_kw: keyword arguments for OCR fuser construction
            host: OCR validation web UI host
            port: OCR validation web UI port
        """
        try:
            language = Language(language)
        except ValueError as exc:
            raise ScinoephileError(
                f"language must be {enum_options_list_str(Language)}, not {language}"
            ) from exc

        self.infile_path = infile_path
        self.output_dir_path = output_dir_path
        self.language = language
        self.stream_index = stream_index
        self.cache_dir_path = cache_dir_path
        self.clean = clean
        self.validate = validate
        self.interactive = interactive
        self.dev = dev
        self.overwrite = overwrite
        self.provider = provider
        if fuser_kw is None:
            self.fuser_kw: dict[str, Any] = {}
        else:
            self.fuser_kw = dict(fuser_kw)
        self.fuser_kw.setdefault("additional_context", additional_context)
        if language is Language.zho_hant:
            self.fuser_kw.setdefault("prompt_cls", OcrFusionPromptZhoHant)
        self.host = host
        self.port = port
        self.output_paths: dict[str, Path] = {}

    def __call__(self) -> OcrProcessingResult:
        """Run OCR processing workflow.

        Returns:
            OCR processing result
        """
        # Load input series
        image_series = self._load_image_series()

        # Export image series
        self._export_image_series(image_series)

        # OCR
        lens = self._lens(image_series)
        if self.language is Language.eng:
            secondary = self._tesseract(image_series)
        else:
            secondary = self._paddle(image_series)

        # Fuse
        fuse_clean = self._fuse(lens, secondary)

        # Validate
        if self.validate:
            self._validate(fuse_clean)

        return OcrProcessingResult(
            infile_path=self.infile_path,
            output_dir_path=self.output_dir_path,
            output_paths=self.output_paths,
        )

    @property
    def clean_function(self) -> Callable[..., Series]:
        """OCR output cleaning function for the workflow language."""
        if self.language is Language.eng:
            return get_eng_cleaned
        else:
            return get_zho_cleaned

    def _export_image_series(self, series: ImageSeries):
        """Export source image subtitles.

        Arguments:
            series: image subtitle series
        """
        image_dir_path = self.output_dir_path / "image"
        if image_dir_path.exists() and not self.overwrite:
            logger.info(f"Image OCR output exists: {image_dir_path}")
        else:
            series.save(image_dir_path)
        self.output_paths["image"] = image_dir_path

    def _fuse(self, lens: Series, secondary: Series) -> Series:
        """Load or create fused and cleaned OCR output.

        Arguments:
            lens: Google Lens OCR series
            secondary: Tesseract or PaddleOCR series
        Returns:
            cleaned fused OCR series
        """
        # Fuse or return pre-existing output
        fuse_path = self.output_dir_path / "fuse.srt"
        if fuse_path.exists() and not self.overwrite:
            logger.info(f"Fuse OCR output exists: {fuse_path}")
            fuse = Series.load(fuse_path)
        else:
            if self.language is Language.eng:
                fuser = get_eng_ocr_fuser(provider=self.provider, **self.fuser_kw)
                fuse = get_eng_ocr_fused(lens, secondary, fuser)
            else:
                fuser = get_zho_ocr_fuser(provider=self.provider, **self.fuser_kw)
                fuse = get_zho_ocr_fused(lens, secondary, fuser)
            fuse.save(fuse_path, format_="srt")
        self.output_paths["fuse"] = fuse_path

        # Clean or return pre-existing output
        fuse_clean_path = self.output_dir_path / "fuse_clean.srt"
        if fuse_clean_path.exists() and not self.overwrite:
            logger.info(f"Cleaned fused OCR output exists: {fuse_clean_path}")
            fuse_clean = Series.load(fuse_clean_path)
        else:
            fuse_clean = self.clean_function(fuse, remove_empty=False)
            fuse_clean.save(fuse_clean_path, format_="srt")
        self.output_paths["fuse_clean"] = fuse_clean_path
        return fuse_clean

    def _load_image_series(self) -> ImageSeries:
        """Load image subtitles from SUP, image directory, or selected media stream.

        Returns:
            image subtitle series
        """
        try:
            if self.infile_path.is_dir() or self.infile_path.suffix.lower() == ".sup":
                return ImageSeries.load(self.infile_path)

            stream = get_media_subtitle_stream(self.infile_path, self.stream_index)
            cache_subtitles(
                self.infile_path, [stream], cache_dir_path=self.cache_dir_path
            )
            stream_path = get_subtitle_cache_path(
                self.infile_path, stream, cache_dir_path=self.cache_dir_path
            )
            return ImageSeries.load(stream_path)
        except (OSError, RuntimeError, ValueError) as exc:
            raise ScinoephileError(
                f"Unable to load OCR image subtitles from {self.infile_path}: {exc}"
            ) from exc

    def _lens(self, image_series: ImageSeries) -> Series:
        """Load or create Google Lens OCR output.

        Arguments:
            image_series: image subtitle series
        Returns:
            Google Lens OCR series
        """
        # OCR or return pre-existing output
        lens_path = self.output_dir_path / "lens.srt"
        if lens_path.exists() and not self.overwrite:
            logger.info(f"Lens OCR output exists: {lens_path}")
            lens = Series.load(lens_path)
        else:
            lens = ocr_image_series_with_lens(image_series, language=self.language)
            lens.save(lens_path, format_="srt")
        self.output_paths["lens"] = lens_path
        if not self.clean:
            return lens

        # Clean or return pre-existing output
        lens_clean_path = self.output_dir_path / "lens_clean.srt"
        if lens_clean_path.exists() and not self.overwrite:
            logger.info(f"Lens OCR output exists: {lens_clean_path}")
            lens_clean = Series.load(lens_clean_path)
        else:
            lens_clean = self.clean_function(lens, remove_empty=False)
            lens_clean.save(lens_clean_path, format_="srt")
        self.output_paths["lens_clean"] = lens_clean_path
        return lens_clean

    def _paddle(self, image_series: ImageSeries) -> Series:
        """Load or create PaddleOCR output.

        Arguments:
            image_series: image subtitle series
        Returns:
            PaddleOCR series
        """
        # OCR or return pre-existing output
        paddle_path = self.output_dir_path / "paddle.srt"
        if paddle_path.exists() and not self.overwrite:
            logger.info(f"Paddle OCR output exists: {paddle_path}")
            paddle = Series.load(paddle_path)
        else:
            paddle = ocr_image_series_with_paddle(image_series, language=self.language)
            paddle.save(paddle_path, format_="srt")
        self.output_paths["paddle"] = paddle_path
        if not self.clean:
            return paddle

        # Clean or return pre-existing output
        paddle_clean_path = self.output_dir_path / "paddle_clean.srt"
        if paddle_clean_path.exists() and not self.overwrite:
            logger.info(f"Paddle OCR output exists: {paddle_clean_path}")
            paddle_clean = Series.load(paddle_clean_path)
        else:
            paddle_clean = self.clean_function(paddle, remove_empty=False)
            paddle_clean.save(paddle_clean_path, format_="srt")
        self.output_paths["paddle_clean"] = paddle_clean_path
        return paddle_clean

    def _tesseract(self, image_series: ImageSeries) -> Series:
        """Load or create Tesseract OCR output.

        Arguments:
            image_series: image subtitle series
        Returns:
            Tesseract OCR series
        """
        # OCR or return pre-existing output
        tesseract_path = self.output_dir_path / "tesseract.srt"
        if tesseract_path.exists() and not self.overwrite:
            logger.info(f"Tesseract OCR output exists: {tesseract_path}")
            tesseract = Series.load(tesseract_path)
        else:
            tesseract = ocr_image_series_with_tesseract(
                image_series, language=Language.eng
            )
            tesseract.save(tesseract_path, format_="srt")
        self.output_paths["tesseract"] = tesseract_path
        if not self.clean:
            return tesseract

        # Clean or return pre-existing output
        tesseract_clean_path = self.output_dir_path / "tesseract_clean.srt"
        if tesseract_clean_path.exists() and not self.overwrite:
            logger.info(f"Tesseract OCR output exists: {tesseract_clean_path}")
            tesseract_clean = Series.load(tesseract_clean_path)
        else:
            tesseract_clean = self.clean_function(tesseract, remove_empty=False)
            tesseract_clean.save(tesseract_clean_path, format_="srt")
        self.output_paths["tesseract_clean"] = tesseract_clean_path
        return tesseract_clean

    def _validate(self, series: Series):
        """Validate OCR output.

        Arguments:
            series: cleaned fused OCR output
        """
        validate_path = self.output_dir_path / "fuse_clean_validate.srt"

        # Load and return pre-existing output
        if validate_path.exists() and not self.overwrite:
            logger.info(f"Validated OCR output exists: {validate_path}")
            Series.load(validate_path)
            self.output_paths["fuse_clean_validate"] = validate_path
            return

        # Copy text from input series to pre-existing image series
        image_dir_path = self.output_dir_path / "image"
        image_series = ImageSeries.load(image_dir_path)
        image_series.copy_text_from(series)
        image_series.save(image_dir_path)

        # Validate and save output
        validate_ocr(
            image_dir_path,
            validate_path,
            interactive=self.interactive,
            dev=self.dev,
            overwrite=self.overwrite,
            host=self.host,
            port=self.port,
        )
        self.output_paths["fuse_clean_validate"] = validate_path
