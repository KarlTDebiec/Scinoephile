#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Tesseract legacy traineddata caching."""

from __future__ import annotations

from pathlib import Path
from time import time

from pytest import raises

from scinoephile.image.ocr.tesseract.traineddata_cache import (
    TesseractLegacyTessdataCache,
)
from test.helpers.files import set_mtime


def test_tesseract_legacy_tessdata_cache_round_trip(tmp_path: Path):
    """Test legacy traineddata round-trips through its cache.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    cache = TesseractLegacyTessdataCache(tmp_path)
    traineddata_path = cache.save("eng", b"traineddata")
    old_timestamp = time() - 60 * 60 * 24 * 40
    set_mtime(traineddata_path, old_timestamp)

    assert traineddata_path.parent == tmp_path / "tesseract-legacy-tessdata"
    assert cache.load("eng") == traineddata_path
    assert traineddata_path.read_bytes() == b"traineddata"
    assert traineddata_path.stat().st_mtime > old_timestamp


def test_tesseract_legacy_tessdata_cache_rejects_unsafe_language(tmp_path: Path):
    """Test traineddata cache paths reject unsafe language codes.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    cache = TesseractLegacyTessdataCache(tmp_path)

    with raises(ValueError, match="simple filename stem"):
        cache.load("../eng")
