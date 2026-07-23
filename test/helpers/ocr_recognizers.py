#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared fake OCR recognizers for image-series tests."""

from __future__ import annotations

from typing import ClassVar

from PIL import Image

__all__ = [
    "FailingOcrRecognizer",
    "RecordingOcrRecognizer",
]


class FailingOcrRecognizer:
    """Fake OCR recognizer that raises a configured exception."""

    exception: ClassVar[Exception | None] = None
    """Exception raised during recognition."""

    def __init__(self, **kwargs: object):
        """Initialize.

        Arguments:
            kwargs: ignored recognizer keyword arguments
        """
        self.kwargs = kwargs

    def recognize_image(self, image: Image.Image) -> str:
        """Recognize text from an image.

        Arguments:
            image: input image
        Raises:
            Exception: configured exception
        """
        _ = image
        if self.exception is None:
            raise AssertionError("FailingOcrRecognizer.exception must be configured")
        raise self.exception


class RecordingOcrRecognizer:
    """Fake OCR recognizer that records initialization and image inputs."""

    texts: ClassVar[list[str]] = []
    """Texts to return from subsequent recognitions."""

    instances: ClassVar[list[RecordingOcrRecognizer]] = []
    """Fake recognizer instances created by the OCR helper."""

    def __init__(self, **kwargs: object):
        """Initialize.

        Arguments:
            kwargs: recognizer keyword arguments
        """
        self.kwargs = kwargs
        self.remaining_texts = list(type(self).texts)
        self.images: list[Image.Image] = []
        type(self).instances.append(self)

    @classmethod
    def reset(cls, *texts: str):
        """Reset recognizer state.

        Arguments:
            texts: texts to return from subsequent recognitions
        """
        cls.texts = list(texts)
        cls.instances = []

    def recognize_image(self, image: Image.Image) -> str:
        """Recognize text from an image.

        Arguments:
            image: input image
        Returns:
            configured OCR text
        """
        self.images.append(image)
        return self.remaining_texts.pop(0)
