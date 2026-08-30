#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Tesseract legacy data caching."""

from __future__ import annotations

from pathlib import Path
from time import time

from pytest import MonkeyPatch, raises

from scinoephile.image.ocr.tesseract.legacy_data_cache import TesseractLegacyDataCache
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
    assert cache.cache_dir_path == (
        runtime_cache_root_path / "image/ocr/tesseract/legacy_data"
    )


def test_tesseract_legacy_data_cache_round_trip(tmp_path: Path):
    """Test legacy traineddata round-trips through its cache.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    cache = TesseractLegacyDataCache(tmp_path)
    traineddata_path = cache.save("eng", b"traineddata")
    old_timestamp = time() - 60 * 60 * 24 * 40
    set_mtime(traineddata_path, old_timestamp)

    assert traineddata_path.parent == (
        tmp_path
        / "image/ocr/tesseract/legacy_data"
        / "eng-ced78752cc61322fb554c280d13360b35b8684e4-v2"
    )
    assert cache.load("eng") == traineddata_path
    assert traineddata_path.read_bytes() == b"traineddata"
    assert traineddata_path.stat().st_mtime > old_timestamp


def test_tesseract_legacy_data_cache_path_includes_version(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Test legacy data from another cache version is not reused.

    Arguments:
        tmp_path: temporary directory path
        monkeypatch: pytest monkeypatch fixture
    """
    cache = TesseractLegacyDataCache(tmp_path)
    traineddata_path = cache.save("eng", b"traineddata")

    monkeypatch.setattr(
        "scinoephile.image.ocr.tesseract.legacy_data_cache._CACHE_VERSION", 3
    )

    assert cache.load("eng") is None
    assert traineddata_path.exists()


def test_tesseract_legacy_data_cache_path_includes_source_revision(tmp_path: Path):
    """Test traineddata paths differ between pinned source revisions.

    Arguments:
        tmp_path: temporary directory path
    """
    first_cache = TesseractLegacyDataCache(tmp_path, source_revision="revision-one")
    second_cache = TesseractLegacyDataCache(tmp_path, source_revision="revision-two")

    assert first_cache.get_path("eng") != second_cache.get_path("eng")


def test_tesseract_legacy_data_cache_overwrites_matching_entry_once(tmp_path: Path):
    """Test overwrite refreshes matching traineddata once per instance.

    Arguments:
        tmp_path: temporary directory path
    """
    TesseractLegacyDataCache(tmp_path).save("eng", b"stale")
    overwrite_cache = TesseractLegacyDataCache(tmp_path, overwrite=True)

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


def test_tesseract_legacy_data_cache_discards_empty_entry(tmp_path: Path):
    """Test an empty traineddata artifact is discarded as a cache miss.

    Arguments:
        tmp_path: temporary directory path
    """
    cache = TesseractLegacyDataCache(tmp_path)
    traineddata_path = cache.get_path("eng")
    traineddata_path.parent.mkdir(parents=True)
    traineddata_path.touch()

    assert cache.load("eng") is None
    assert not traineddata_path.exists()


def test_tesseract_legacy_data_cache_rejects_empty_save(tmp_path: Path):
    """Test empty traineddata cannot be saved as a valid cache entry.

    Arguments:
        tmp_path: temporary directory path
    """
    cache = TesseractLegacyDataCache(tmp_path)

    with raises(ValueError, match="cannot be empty"):
        cache.save("eng", b"")
