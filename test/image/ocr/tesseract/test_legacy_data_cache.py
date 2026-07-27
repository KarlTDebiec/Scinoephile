#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Tesseract legacy data caching."""

from __future__ import annotations

from pathlib import Path
from time import time

from pytest import MonkeyPatch, raises

from scinoephile.image.ocr.tesseract.legacy_data_cache import (
    TesseractLegacyDataCache,
)
from test.helpers.files import set_mtime


def test_tesseract_legacy_data_cache_uses_runtime_default(
    runtime_cache_root_path: Path,
):
    """Test a missing configured root selects the runtime cache root.

    Arguments:
        runtime_cache_root_path: isolated default runtime cache root
    """
    cache = TesseractLegacyDataCache()

    assert cache.cache_root_path == runtime_cache_root_path
    assert cache.cache_dir_path == (runtime_cache_root_path / "tesseract-legacy-data")


def test_tesseract_legacy_data_cache_round_trip(tmp_path: Path):
    """Test legacy traineddata round-trips through its cache.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    cache = TesseractLegacyDataCache(tmp_path)
    traineddata_path = cache.save("eng", b"traineddata")
    old_timestamp = time() - 60 * 60 * 24 * 40
    set_mtime(traineddata_path, old_timestamp)

    assert traineddata_path.parent == tmp_path / "tesseract-legacy-data" / "eng-v1"
    assert cache.load("eng") == traineddata_path
    assert traineddata_path.read_bytes() == b"traineddata"
    assert traineddata_path.stat().st_mtime > old_timestamp


def test_tesseract_legacy_data_cache_path_includes_version(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test legacy data from another cache version is not reused."""
    cache = TesseractLegacyDataCache(tmp_path)
    traineddata_path = cache.save("eng", b"traineddata")

    monkeypatch.setattr(
        "scinoephile.image.ocr.tesseract.legacy_data_cache._CACHE_VERSION",
        2,
    )

    assert cache.load("eng") is None
    assert traineddata_path.exists()


def test_tesseract_legacy_data_cache_overwrites_matching_entry_once(
    tmp_path: Path,
):
    """Test overwrite refreshes matching traineddata once per instance."""
    TesseractLegacyDataCache(tmp_path).save("eng", b"stale")
    overwrite_cache = TesseractLegacyDataCache(tmp_path, True)

    assert overwrite_cache.load("eng") is None
    traineddata_path = overwrite_cache.save("eng", b"fresh")

    assert overwrite_cache.load("eng") == traineddata_path
    assert traineddata_path.read_bytes() == b"fresh"


def test_tesseract_legacy_data_cache_rejects_unsafe_language(tmp_path: Path):
    """Test traineddata cache paths reject unsafe language codes.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    cache = TesseractLegacyDataCache(tmp_path)

    with raises(ValueError, match="simple filename stem"):
        cache.load("../eng")
