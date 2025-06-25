#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image code related to base64 encoding."""

from __future__ import annotations

from base64 import b64encode
from io import BytesIO

from PIL import Image


def get_base64_image(image: Image) -> str:
    """Get base64 encoding of image.

    Arguments:
        image: Image to encode
    Returns:
        Base64 encoding of image
    """
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return b64encode(buffered.getvalue()).decode("utf-8")
