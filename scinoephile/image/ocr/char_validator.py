#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""OCR character validator."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path
from typing import Any

import numpy as np
import paddle
from huggingface_hub import snapshot_download
from paddleocr import PaddleOCR
from PIL import Image

from scinoephile.image.bbox import Bbox
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle

__all__ = ["CharValidator"]

logger = getLogger(__name__)


class CharValidator:
    """OCR character validator."""

    def __init__(
        self,
        model_name: str = "saudadez/rec_chinese_char",
        paddle_model_dir: Path | str | None = None,
        paddle_ocr_kwargs: dict[str, Any] | None = None,
    ):
        """Initialize.

        Arguments:
            model_name: Hugging Face model name or local directory
            paddle_model_dir: local directory containing PaddleOCR model artifacts
            paddle_ocr_kwargs: extra keyword arguments passed to PaddleOCR
        """
        self.model_name = model_name
        self._paddle_model_dir = Path(paddle_model_dir) if paddle_model_dir else None
        self._paddle_ocr_kwargs = paddle_ocr_kwargs or {}
        logger.info(f"Loading PaddleOCR model {self.model_name}")
        self.paddle_ocr = self._load_paddle_ocr()

    def _resolve_paddle_model_dir(self) -> Path:
        """Resolve the directory containing PaddleOCR recognition model artifacts."""
        if self._paddle_model_dir is not None:
            return self._paddle_model_dir

        logger.info(f"Downloading Hugging Face model {self.model_name}")
        download_dir = Path(snapshot_download(repo_id=self.model_name))
        return download_dir

    def _load_paddle_ocr(self) -> PaddleOCR:
        """Instantiate PaddleOCR for single-character recognition."""
        gpu_available = paddle.device.is_compiled_with_cuda()
        model_dir = self._resolve_paddle_model_dir()

        kwargs: dict[str, Any] = {
            "use_angle_cls": False,
            "lang": "ch",
            "det": False,
            "use_gpu": gpu_available,
            "rec_model_dir": str(model_dir),
            "rec_char_dict_path": str(model_dir / "rec_custom_keys.txt"),
            "rec_image_shape": "3,48,48",
        }
        kwargs.update(self._paddle_ocr_kwargs)
        return PaddleOCR(**kwargs)

    def validate(
        self,
        series: ImageSeries,
        stop_at_idx: int | None = None,
    ) -> ImageSeries:
        """Validate all characters in an image series using ML.

        Arguments:
            series: image series to validate
            stop_at_idx: stop validating at this index
        Returns:
            image series (unchanged, validation is for logging only)
        """
        if stop_at_idx is None:
            stop_at_idx = len(series) - 1

        messages = []
        for sub_idx, sub in enumerate(series.events):
            if sub_idx > stop_at_idx:
                break
            messages.extend(self._validate_sub(sub, sub_idx))

        for message in messages:
            logger.warning(message)

        return series

    def _validate_sub(self, sub: ImageSubtitle, sub_idx: int) -> list[str]:
        """Validate all characters in a subtitle.

        Arguments:
            sub: subtitle to validate
            sub_idx: subtitle index for logging
        Returns:
            list of validation messages
        """
        if sub.bboxes is None:
            return [f"Sub {sub_idx:4d} | No bboxes; run BboxValidator first"]

        messages = []

        # Validate each bbox/character pair
        for bbox_idx, bbox in enumerate(sub.bboxes):
            # Get the corresponding character from text
            # Note: This assumes bboxes and characters are 1:1 aligned
            if bbox_idx < len(sub.text):
                expected_char = sub.text[bbox_idx]
                is_valid, predicted_char, _ = self._validate_character(
                    sub.img, bbox, expected_char
                )

                if not is_valid:
                    messages.append(
                        f"Sub {sub_idx:4d} | Bbox {bbox_idx:3d} | "
                        f"expected='{expected_char}', predicted='{predicted_char}'"
                    )

        return messages

    def _validate_character(
        self, img: Image.Image, bbox: Bbox, expected_char: str
    ) -> tuple[bool, str, float]:
        """Validate a character using ML model.

        Arguments:
            img: full subtitle image
            bbox: bounding box for the character to validate
            expected_char: the expected character from OCR
        Returns:
            tuple of (is_valid, predicted_char, confidence).
            Note: confidence is currently a binary value (1.0 for match, 0.0 for
            mismatch). A more sophisticated confidence score would require accessing
            the model's logits, which is not currently implemented.
        """
        return self._validate_character_paddleocr(img, bbox, expected_char)

    @staticmethod
    def _extract_paddleocr_text_and_score(result: Any) -> tuple[str, float]:
        """Extract text and score from PaddleOCR's varying return formats.

        Arguments:
            result: object returned by PaddleOCR.ocr
        Returns:
            tuple of (text, score)
        """

        def _walk(obj: Any) -> tuple[str, float]:
            if isinstance(obj, (tuple, list)):
                if len(obj) == 0:
                    return "", 0.0
                if (
                    len(obj) == 2
                    and isinstance(obj[0], str)
                    and isinstance(obj[1], (float, int))
                ):
                    return obj[0], float(obj[1])
                if len(obj) == 2 and isinstance(obj[1], (tuple, list)):
                    return _walk(obj[1])
                return _walk(obj[0])
            return "", 0.0

        return _walk(result)

    def _validate_character_paddleocr(
        self, img: Image.Image, bbox: Bbox, expected_char: str
    ) -> tuple[bool, str, float]:
        """Validate a character using PaddleOCR recognition.

        Arguments:
            img: full subtitle image
            bbox: bounding box for the character to validate
            expected_char: the expected character from OCR
        Returns:
            tuple of (is_valid, predicted_char, confidence).
        """
        char_img = img.crop((bbox.x1, bbox.y1, bbox.x2, bbox.y2))
        if char_img.mode != "RGB":
            char_img = char_img.convert("RGB")

        result = self.paddle_ocr.ocr(np.asarray(char_img))
        text, score = self._extract_paddleocr_text_and_score(result)

        predicted_char = text[:1] if text else ""
        is_valid = predicted_char == expected_char

        logger.debug(
            f"PaddleOCR validation: expected='{expected_char}', "
            f"predicted='{predicted_char}', is_valid={is_valid}"
        )
        return is_valid, predicted_char, score
