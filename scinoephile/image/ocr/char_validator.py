#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ML-based OCR character validation using Hugging Face models."""

from __future__ import annotations

from logging import getLogger

from PIL import Image
from transformers import AutoTokenizer, TrOCRProcessor, VisionEncoderDecoderModel

from scinoephile.image.bbox import Bbox
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle

__all__ = ["CharValidator"]

logger = getLogger(__name__)


class CharValidator:
    """ML-based character validator using Hugging Face rec_chinese_char model."""

    def __init__(self, model_name: str = "saudadez/rec_chinese_char"):
        """Initialize the ML character validator.

        Arguments:
            model_name: name of the Hugging Face model to use
        """
        self.model_name = model_name
        self._model = None
        self._processor = None
        self._tokenizer = None

    @property
    def model(self) -> VisionEncoderDecoderModel:
        """Lazy-load the model."""
        if self._model is None:
            logger.info(f"Loading model {self.model_name}")
            self._model = VisionEncoderDecoderModel.from_pretrained(self.model_name)
            self._model.eval()
        return self._model

    @property
    def processor(self) -> TrOCRProcessor:
        """Lazy-load the processor."""
        if self._processor is None:
            logger.info(f"Loading processor for {self.model_name}")
            self._processor = TrOCRProcessor.from_pretrained(self.model_name)
        return self._processor

    @property
    def tokenizer(self) -> AutoTokenizer:
        """Lazy-load the tokenizer."""
        if self._tokenizer is None:
            logger.info(f"Loading tokenizer for {self.model_name}")
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        return self._tokenizer

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
        # Crop the character from the image
        char_img = img.crop((bbox.x1, bbox.y1, bbox.x2, bbox.y2))

        # Convert to RGB if needed
        if char_img.mode != "RGB":
            char_img = char_img.convert("RGB")

        # Process the image
        pixel_values = self.processor(char_img, return_tensors="pt").pixel_values

        # Generate prediction
        generated_ids = self.model.generate(pixel_values)
        predicted_text = self.tokenizer.batch_decode(
            generated_ids, skip_special_tokens=True
        )[0]

        # Check if prediction matches expected character
        is_valid = predicted_text == expected_char

        # Binary confidence score based on match
        # TODO: Calculate actual confidence from model logits if needed
        confidence = 1.0 if is_valid else 0.0

        logger.debug(
            f"ML validation: expected='{expected_char}', "
            f"predicted='{predicted_text}', is_valid={is_valid}"
        )

        return is_valid, predicted_text, confidence
