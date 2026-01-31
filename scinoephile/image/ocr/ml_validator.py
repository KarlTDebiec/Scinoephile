#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ML-based OCR character validation using Hugging Face models."""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from PIL import Image
from transformers import AutoTokenizer, TrOCRProcessor, VisionEncoderDecoderModel

if TYPE_CHECKING:
    from scinoephile.image.bbox import Bbox

__all__ = ["MLCharacterValidator"]

logger = getLogger(__name__)


class MLCharacterValidator:
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

    def validate_character(
        self, img: Image.Image, bbox: Bbox, expected_char: str
    ) -> tuple[bool, str, float]:
        """Validate a character using ML model.

        Arguments:
            img: full subtitle image
            bbox: bounding box for the character to validate
            expected_char: the expected character from OCR
        Returns:
            tuple of (is_valid, predicted_char, confidence)
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

        # For confidence, we can use the model's output probability
        # This is a simplified version - confidence score would require
        # accessing the model's logits
        confidence = 1.0 if is_valid else 0.0

        logger.debug(
            f"ML validation: expected='{expected_char}', "
            f"predicted='{predicted_text}', is_valid={is_valid}"
        )

        return is_valid, predicted_text, confidence
