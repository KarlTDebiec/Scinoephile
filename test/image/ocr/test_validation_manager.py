#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of ValidationManager with ML validation."""

from __future__ import annotations

from scinoephile.image.ocr import ValidationManager


def test_validation_manager_with_ml_disabled():
    """Test that ValidationManager works without ML validation."""
    manager = ValidationManager(use_ml_validation=False)
    assert manager.use_ml_validation is False
    assert manager._ml_validator is None
    # ml_validator property should return None when disabled
    assert manager.ml_validator is None


def test_validation_manager_with_ml_enabled():
    """Test that ValidationManager can be configured to use ML validation."""
    manager = ValidationManager(use_ml_validation=True)
    assert manager.use_ml_validation is True
    assert manager._ml_validator is None
    # ml_validator property should lazy-load the validator
    validator = manager.ml_validator
    assert validator is not None


def test_validation_manager_default():
    """Test that ValidationManager defaults to no ML validation."""
    manager = ValidationManager()
    assert manager.use_ml_validation is False
