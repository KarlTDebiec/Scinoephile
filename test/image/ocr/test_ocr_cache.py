#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of OCR result caches."""

from __future__ import annotations

import json
from pathlib import Path
from time import time

from PIL import Image

from scinoephile.image.ocr.tesseract import TesseractCache
from test.helpers.files import set_mtime


def test_ocr_cache_uses_backend_directory_and_configuration(tmp_path: Path):
    """Test OCR cache paths use backend directories and configuration metadata."""
    cache = TesseractCache(tmp_path)
    image = Image.new("RGB", (2, 2), "white")

    english_path = cache.get_path(image, {"language": "eng"})
    chinese_path = cache.get_path(image, {"language": "chi_sim"})

    assert cache.cache_root_path == tmp_path.resolve()
    assert english_path.parent == tmp_path.resolve() / "tesseract"
    assert english_path != chinese_path


def test_ocr_cache_loads_results_and_updates_modification_time(tmp_path: Path):
    """Test OCR cache loads results and refreshes file modification times."""
    cache = TesseractCache(tmp_path)
    image = Image.new("RGB", (2, 2), "white")
    metadata = {"language": "eng"}
    cache_path = cache.save(image, metadata, "cached text")
    old_timestamp = time() - 60
    set_mtime(cache_path, old_timestamp)

    result = cache.load(image, metadata)

    assert result == "cached text"
    assert json.loads(cache_path.read_text(encoding="utf-8")) == {
        "cache_version": 1,
        "result": {"text": "cached text"},
    }
    assert cache_path.stat().st_mtime > old_timestamp


def test_ocr_cache_discards_mismatched_version(tmp_path: Path):
    """Test an OCR cache version mismatch is discarded as a cache miss."""
    cache = TesseractCache(tmp_path)
    image = Image.new("RGB", (2, 2), "white")
    metadata = {"language": "eng"}
    cache_path = cache.save(image, metadata, "cached text")
    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    payload["cache_version"] = 0
    cache_path.write_text(json.dumps(payload), encoding="utf-8")

    assert cache.load(image, metadata) is None
    assert not cache_path.exists()


def test_ocr_cache_overwrite_removes_matching_result(tmp_path: Path):
    """Test OCR cache overwrite converts a matching result into a cache miss."""
    image = Image.new("RGB", (2, 2), "white")
    metadata = {"language": "eng"}
    cache_path = TesseractCache(tmp_path).save(image, metadata, "stale text")

    result = TesseractCache(tmp_path, overwrite=True).load(image, metadata)

    assert result is None
    assert not cache_path.exists()


def test_ocr_cache_overwrites_matching_result_once(tmp_path: Path):
    """Test overwrite refreshes a matching OCR result once per instance."""
    image = Image.new("RGB", (2, 2), "white")
    metadata = {"language": "eng"}
    TesseractCache(tmp_path).save(image, metadata, "stale text")
    overwrite_cache = TesseractCache(tmp_path, overwrite=True)

    assert overwrite_cache.load(image, metadata) is None
    overwrite_cache.save(image, metadata, "fresh text")

    assert overwrite_cache.load(image, metadata) == "fresh text"


def test_ocr_cache_uses_runtime_default(runtime_cache_root_path: Path):
    """Test a missing configured root selects the runtime cache root.

    Arguments:
        runtime_cache_root_path: isolated default runtime cache root
    """
    cache = TesseractCache(None)
    image = Image.new("RGB", (2, 2), "white")
    metadata = {"language": "eng"}

    cache_path = cache.save(image, metadata, "cached text")

    assert cache.cache_root_path == runtime_cache_root_path
    assert cache_path.parent == runtime_cache_root_path / "tesseract"
    assert cache.load(image, metadata) == "cached text"
