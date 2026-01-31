#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of ML-based character validation."""

from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

from scinoephile.image.bbox import Bbox
from scinoephile.image.ocr import MLCharacterValidator


@pytest.fixture
def sample_chinese_char_image() -> Image.Image:
    """Create a simple test image with a character-like pattern.

    Returns:
        test image
    """
    # Create a simple 40x40 image with a pattern that looks like a character
    img_array = np.ones((40, 40, 3), dtype=np.uint8) * 255
    # Add some dark pixels to simulate a character
    img_array[10:30, 15:25] = 0
    return Image.fromarray(img_array)


def test_ml_validator_initialization():
    """Test that MLCharacterValidator can be initialized."""
    validator = MLCharacterValidator()
    assert validator is not None
    assert validator.model_name == "saudadez/rec_chinese_char"


def test_ml_validator_custom_model():
    """Test that MLCharacterValidator can be initialized with a custom model."""
    validator = MLCharacterValidator(model_name="custom/model")
    assert validator.model_name == "custom/model"


@pytest.mark.skip(reason="Requires downloading model and may be slow")
def test_ml_validator_validate_character(sample_chinese_char_image: Image.Image):
    """Test character validation with ML model.

    Arguments:
        sample_chinese_char_image: test image fixture
    """
    validator = MLCharacterValidator()
    bbox = Bbox(x1=0, x2=40, y1=0, y2=40)

    # Test validation
    is_valid, predicted_char, confidence = validator.validate_character(
        sample_chinese_char_image, bbox, "测"
    )

    # We can't predict the exact result, but we should get valid types back
    assert isinstance(is_valid, bool)
    assert isinstance(predicted_char, str)
    assert isinstance(confidence, float)
