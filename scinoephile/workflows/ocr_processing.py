#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for processing image subtitle OCR end to end."""

from __future__ import annotations

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
        self.additional_context = additional_context
        self.fuser_kw = fuser_kw
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

        # Process
        if self.language is Language.eng:
            fuse_clean = self._process_eng_ocr(image_series)
        else:
            fuse_clean = self._process_zho_ocr(image_series)

        # Validate
        if self.validate:
            self._validate(fuse_clean)

        return OcrProcessingResult(
            infile_path=self.infile_path,
            output_dir_path=self.output_dir_path,
            output_paths=self.output_paths,
        )

    @property
    def clean_function(self):
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

    def _fuse_eng_ocr(self, lens: Series, tesseract: Series) -> Series:
        """Load or create fused English OCR output.

        Arguments:
            lens: Google Lens OCR series
            tesseract: Tesseract OCR series
        Returns:
            fused English OCR series
        """
        kwargs = self._get_fuser_kw()
        path = self.output_dir_path / "fuse.srt"
        try:
            if path.exists() and not self.overwrite:
                logger.info(f"Fuse OCR output exists: {path}")
                series = Series.load(path)
            else:
                series = get_eng_ocr_fused(
                    lens,
                    tesseract,
                    processor=get_eng_ocr_fuser(provider=self.provider, **kwargs),
                )
                series.save(path, format_="srt")
        except (OSError, RuntimeError, ValueError) as exc:
            raise ScinoephileError(
                f"Unable to load or create Fuse OCR output at {path}: {exc}"
            ) from exc
        self.output_paths["fuse"] = path
        return series

    def _fuse_zho_ocr(self, lens: Series, paddle: Series) -> Series:
        """Load or create fused Chinese OCR output.

        Arguments:
            lens: Google Lens OCR series
            paddle: PaddleOCR series
        Returns:
            fused Chinese OCR series
        """
        kwargs = self._get_fuser_kw()
        if self.language is Language.zho_hant:
            kwargs.setdefault("prompt_cls", OcrFusionPromptZhoHant)
        path = self.output_dir_path / "fuse.srt"
        try:
            if path.exists() and not self.overwrite:
                logger.info(f"Fuse OCR output exists: {path}")
                series = Series.load(path)
            else:
                series = get_zho_ocr_fused(
                    lens,
                    paddle,
                    processor=get_zho_ocr_fuser(provider=self.provider, **kwargs),
                )
                series.save(path, format_="srt")
        except (OSError, RuntimeError, ValueError) as exc:
            raise ScinoephileError(
                f"Unable to load or create Fuse OCR output at {path}: {exc}"
            ) from exc
        self.output_paths["fuse"] = path
        return series

    def _get_fuser_kw(self) -> dict[str, Any]:
        """Get keyword arguments for OCR fuser construction.

        Returns:
            keyword arguments for OCR fuser construction
        """
        if self.fuser_kw is None:
            kwargs: dict[str, Any] = {}
        else:
            kwargs = dict(self.fuser_kw)
        kwargs.setdefault("additional_context", self.additional_context)
        return kwargs

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
        # OCR or return pre-existing output
        lens_path = self.output_dir_path / "lens.srt"
        try:
            if lens_path.exists() and not self.overwrite:
                logger.info(f"Lens OCR output exists: {lens_path}")
                lens = Series.load(lens_path)
            else:
                lens = ocr_image_series_with_lens(image_series, language=self.language)
                lens.save(lens_path, format_="srt")
        except (OSError, RuntimeError, ValueError) as exc:
            raise ScinoephileError(
                f"Unable to load or create Lens OCR output at {lens_path}: {exc}"
            ) from exc
        self.output_paths["lens"] = lens_path

        # Clean (if applicable) or return pre-existing output
        if not self.clean:
            return lens
        lens_clean_path = self.output_dir_path / "lens_clean.srt"
        try:
            if lens_clean_path.exists() and not self.overwrite:
                logger.info(f"Lens OCR output exists: {lens_clean_path}")
                lens_clean = Series.load(lens_clean_path)
            else:
                lens_clean = self.clean_function(lens, remove_empty=False)
                lens_clean.save(lens_clean_path, format_="srt")
        except (OSError, RuntimeError, ValueError) as exc:
            raise ScinoephileError(
                "Unable to load or create cleaned Lens OCR output at "
                f"{lens_clean_path}: {exc}"
            ) from exc
        self.output_paths["lens_clean"] = lens_clean_path
        return lens_clean

    def _paddle(self, image_series: ImageSeries) -> Series:
        if self.language.script is None:
            raise ScinoephileError(
                f"language {self.language} does not specify a Chinese script"
            )

        # OCR or return pre-existing output
        paddle_path = self.output_dir_path / "paddle.srt"
        try:
            if paddle_path.exists() and not self.overwrite:
                logger.info(f"Paddle OCR output exists: {paddle_path}")
                paddle = Series.load(paddle_path)
            else:
                paddle = ocr_image_series_with_paddle(
                    image_series, language=self.language
                )
                paddle.save(paddle_path, format_="srt")
        except (OSError, RuntimeError, ValueError) as exc:
            raise ScinoephileError(
                f"Unable to load or create PaddleOCR output at {paddle_path}: {exc}"
            ) from exc
        self.output_paths["paddle"] = paddle_path

        # Clean (if applicable) or return pre-existing output
        if not self.clean:
            return paddle
        paddle_clean_path = self.output_dir_path / "paddle_clean.srt"
        try:
            if paddle_clean_path.exists() and not self.overwrite:
                logger.info(f"Paddle OCR output exists: {paddle_clean_path}")
                paddle_clean = Series.load(paddle_clean_path)
            else:
                paddle_clean = self.clean_function(paddle, remove_empty=False)
                paddle_clean.save(paddle_clean_path, format_="srt")
        except (OSError, RuntimeError, ValueError) as exc:
            raise ScinoephileError(
                "Unable to load or create cleaned PaddleOCR output at "
                f"{paddle_clean_path}: {exc}"
            ) from exc
        self.output_paths["paddle_clean"] = paddle_clean_path
        return paddle_clean

    def _tesseract(self, image_series: ImageSeries) -> Series:
        # OCR or return pre-existing output
        tesseract_path = self.output_dir_path / "tesseract.srt"
        try:
            if tesseract_path.exists() and not self.overwrite:
                logger.info(f"Tesseract OCR output exists: {tesseract_path}")
                tesseract = Series.load(tesseract_path)
            else:
                tesseract = ocr_image_series_with_tesseract(
                    image_series, language=Language.eng
                )
                tesseract.save(tesseract_path, format_="srt")
        except (OSError, RuntimeError, ValueError) as exc:
            raise ScinoephileError(
                "Unable to load or create Tesseract OCR output at "
                f"{tesseract_path}: {exc}"
            ) from exc
        self.output_paths["tesseract"] = tesseract_path

        # Clean (if applicable) or return pre-existing output
        if not self.clean:
            return tesseract
        tesseract_clean_path = self.output_dir_path / "tesseract_clean.srt"
        try:
            if tesseract_clean_path.exists() and not self.overwrite:
                logger.info(f"Tesseract OCR output exists: {tesseract_clean_path}")
                tesseract_clean = Series.load(tesseract_clean_path)
            else:
                tesseract_clean = self.clean_function(tesseract, remove_empty=False)
                tesseract_clean.save(tesseract_clean_path, format_="srt")
        except (OSError, RuntimeError, ValueError) as exc:
            raise ScinoephileError(
                "Unable to load or create cleaned Tesseract OCR output at "
                f"{tesseract_clean_path}: {exc}"
            ) from exc
        self.output_paths["tesseract_clean"] = tesseract_clean_path
        return tesseract_clean

    def _process_eng_ocr(  # noqa: PLR0912, PLR0915
        self, image_series: ImageSeries
    ) -> Series:
        """Process English OCR outputs through fusion and cleaning.

        Arguments:
            image_series: image subtitle series
        Returns:
            cleaned fused OCR output
        """
        # Lens
        lens = self._lens(image_series)

        # Tesseract
        tesseract = self._tesseract(image_series)

        fuse = self._fuse_eng_ocr(lens, tesseract)
        fuse_clean_path = self.output_dir_path / "fuse_clean.srt"
        try:
            if fuse_clean_path.exists() and not self.overwrite:
                logger.info(f"Cleaned fused OCR output exists: {fuse_clean_path}")
                fuse_clean = Series.load(fuse_clean_path)
            else:
                fuse_clean = get_eng_cleaned(fuse, remove_empty=False)
                fuse_clean.save(fuse_clean_path, format_="srt")
        except (OSError, RuntimeError, ValueError) as exc:
            raise ScinoephileError(
                "Unable to load or create Cleaned fused OCR output at "
                f"{fuse_clean_path}: {exc}"
            ) from exc
        self.output_paths["fuse_clean"] = fuse_clean_path
        return fuse_clean

    def _process_zho_ocr(  # noqa: PLR0912, PLR0915
        self, image_series: ImageSeries
    ) -> Series:
        """Process Chinese OCR outputs through fusion and cleaning.

        Arguments:
            image_series: image subtitle series
        Returns:
            cleaned fused OCR output
        """
        # Lens
        lens = self._lens(image_series)

        # Paddle
        paddle = self._paddle(image_series)

        fuse = self._fuse_zho_ocr(lens, paddle)
        fuse_clean_path = self.output_dir_path / "fuse_clean.srt"
        try:
            if fuse_clean_path.exists() and not self.overwrite:
                logger.info(f"Cleaned fused OCR output exists: {fuse_clean_path}")
                fuse_clean = Series.load(fuse_clean_path)
            else:
                fuse_clean = get_zho_cleaned(fuse, remove_empty=False)
                fuse_clean.save(fuse_clean_path, format_="srt")
        except (OSError, RuntimeError, ValueError) as exc:
            raise ScinoephileError(
                "Unable to load or create Cleaned fused OCR output at "
                f"{fuse_clean_path}: {exc}"
            ) from exc
        self.output_paths["fuse_clean"] = fuse_clean_path
        return fuse_clean

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
