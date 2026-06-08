#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of OCR validation manager data storage."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest
from PIL import Image

from scinoephile.core import ScinoephileError
from scinoephile.image.bbox import Bbox
from scinoephile.image.ocr.validation import ValidationManager, validation_manager
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle


def test_validation_manager_layers_cache_data_over_repo_data(tmp_path, monkeypatch):
    """Test loading OCR validation data from repo and cache directories."""
    repo_root_path = tmp_path / "repo"
    repo_data_dir_path = repo_root_path / "data" / "ocr"
    repo_data_dir_path.mkdir(parents=True)
    monkeypatch.setattr(validation_manager, "package_root", repo_root_path)
    cache_dir_path = tmp_path / "cache" / "ocr_validation"
    cache_dir_path.mkdir(parents=True)

    (repo_data_dir_path / "char_dims_1.csv").write_text(
        "A,10,20\nB,30,40\n", encoding="utf-8"
    )
    (cache_dir_path / "char_dims_1.csv").write_text("A,11,21\n", encoding="utf-8")
    (repo_data_dir_path / "char_grp_dims.csv").write_text(
        "AB,50,20\n", encoding="utf-8"
    )
    (cache_dir_path / "char_grp_dims.csv").write_text("CD,60,20\n", encoding="utf-8")
    (repo_data_dir_path / "char_pair_gaps.csv").write_text(
        "A,B,1,2,3,4\nB,C,5,6,7,8\n", encoding="utf-8"
    )
    (cache_dir_path / "char_pair_gaps.csv").write_text(
        "A,B,9,10,11,12\n", encoding="utf-8"
    )

    manager = ValidationManager(cache_dir_path=cache_dir_path)

    assert manager.char_dims_by_n[1] == {
        "A": {(10, 20), (11, 21)},
        "B": {(30, 40)},
    }
    assert manager.char_grp_dims_by_n == {
        2: {
            "AB": {(50, 20)},
            "CD": {(60, 20)},
        }
    }
    assert manager.char_pair_gaps == {
        ("A", "B"): (9, 10, 11, 12),
        ("B", "C"): (5, 6, 7, 8),
    }


def test_validation_manager_uses_only_repo_data_in_dev_mode(tmp_path, monkeypatch):
    """Test dev mode loads active OCR validation data from the repo."""
    repo_root_path = tmp_path / "repo"
    repo_data_dir_path = repo_root_path / "data" / "ocr"
    repo_data_dir_path.mkdir(parents=True)
    monkeypatch.setattr(validation_manager, "package_root", repo_root_path)
    cache_dir_path = tmp_path / "cache" / "ocr_validation"
    cache_dir_path.mkdir(parents=True)

    (repo_data_dir_path / "char_dims_1.csv").write_text(
        "A,10,20\nB,30,40\n", encoding="utf-8"
    )
    (cache_dir_path / "char_dims_1.csv").write_text("A,11,21\n", encoding="utf-8")
    (repo_data_dir_path / "char_grp_dims.csv").write_text(
        "AB,50,20\n", encoding="utf-8"
    )
    (cache_dir_path / "char_grp_dims.csv").write_text("CD,60,20\n", encoding="utf-8")
    (repo_data_dir_path / "char_pair_gaps.csv").write_text(
        "A,B,1,2,3,4\nB,C,5,6,7,8\n", encoding="utf-8"
    )
    (cache_dir_path / "char_pair_gaps.csv").write_text(
        "A,B,9,10,11,12\n", encoding="utf-8"
    )

    manager = ValidationManager(cache_dir_path=cache_dir_path, dev=True)

    assert manager.char_dims_by_n[1] == {
        "A": {(10, 20)},
        "B": {(30, 40)},
    }
    assert manager.char_grp_dims_by_n == {
        2: {
            "AB": {(50, 20)},
        }
    }
    assert manager.char_pair_gaps == {
        ("A", "B"): (1, 2, 3, 4),
        ("B", "C"): (5, 6, 7, 8),
    }


def test_validation_manager_writes_updates_to_cache_by_default(tmp_path, monkeypatch):
    """Test OCR validation data updates write to the cache by default."""
    repo_root_path = tmp_path / "repo"
    repo_data_dir_path = repo_root_path / "data" / "ocr"
    repo_data_dir_path.mkdir(parents=True)
    monkeypatch.setattr(validation_manager, "package_root", repo_root_path)
    cache_dir_path = tmp_path / "cache" / "ocr_validation"
    cache_dir_path.mkdir(parents=True)

    manager = ValidationManager(cache_dir_path=cache_dir_path)

    manager._update_char_dims("A", (10, 20))

    assert (cache_dir_path / "char_dims_1.csv").read_text(encoding="utf-8") == (
        "A,10,20\n"
    )
    assert not (repo_data_dir_path / "char_dims_1.csv").exists()


def test_validation_manager_writes_only_cache_updates_to_cache(tmp_path, monkeypatch):
    """Test cache writes do not snapshot repo validation data."""
    repo_root_path = tmp_path / "repo"
    repo_data_dir_path = repo_root_path / "data" / "ocr"
    repo_data_dir_path.mkdir(parents=True)
    monkeypatch.setattr(validation_manager, "package_root", repo_root_path)
    cache_dir_path = tmp_path / "cache" / "ocr_validation"
    cache_dir_path.mkdir(parents=True)
    (repo_data_dir_path / "char_dims_1.csv").write_text("A,10,20\n", encoding="utf-8")
    (repo_data_dir_path / "char_grp_dims.csv").write_text(
        "AB,50,20\n", encoding="utf-8"
    )
    (repo_data_dir_path / "char_pair_gaps.csv").write_text(
        "A,B,1,2,3,4\n", encoding="utf-8"
    )

    manager = ValidationManager(cache_dir_path=cache_dir_path)

    manager._update_char_dims("B", (30, 40))
    manager._update_char_grp_dims("CD", (60, 20))
    manager._update_pair_gaps(("B", "C"), (5, 6, 7, 8))

    assert (cache_dir_path / "char_dims_1.csv").read_text(encoding="utf-8") == (
        "B,30,40\n"
    )
    assert (cache_dir_path / "char_grp_dims.csv").read_text(encoding="utf-8") == (
        "CD,60,20\n"
    )
    assert (cache_dir_path / "char_pair_gaps.csv").read_text(encoding="utf-8") == (
        "B,C,5,6,7,8\n"
    )


def test_validation_manager_allows_new_custom_cache_dir(tmp_path, monkeypatch):
    """Test missing custom cache directories are created on first write."""
    repo_root_path = tmp_path / "repo"
    repo_data_dir_path = repo_root_path / "data" / "ocr"
    repo_data_dir_path.mkdir(parents=True)
    monkeypatch.setattr(validation_manager, "package_root", repo_root_path)
    cache_dir_path = tmp_path / "cache" / "ocr_validation"

    manager = ValidationManager(cache_dir_path=cache_dir_path)

    manager._update_char_dims("A", (10, 20))

    assert (cache_dir_path / "char_dims_1.csv").read_text(encoding="utf-8") == (
        "A,10,20\n"
    )


def test_validation_manager_wraps_cache_path_errors(tmp_path: Path):
    """Test cache path validation errors are user-facing.

    Arguments:
        tmp_path: pytest temporary directory path
    """
    cache_dir_path = tmp_path / "cache-file"
    cache_dir_path.write_text("not a directory", encoding="utf-8")

    with pytest.raises(
        ScinoephileError,
        match="Unable to initialize OCR validation data",
    ) as excinfo:
        ValidationManager(cache_dir_path=cache_dir_path)

    assert isinstance(excinfo.value.__cause__, OSError)


def test_validation_manager_writes_updates_to_repo_in_dev_mode(tmp_path, monkeypatch):
    """Test dev mode writes OCR validation data updates to repo data."""
    repo_root_path = tmp_path / "repo"
    repo_data_dir_path = repo_root_path / "data" / "ocr"
    repo_data_dir_path.mkdir(parents=True)
    monkeypatch.setattr(validation_manager, "package_root", repo_root_path)
    cache_dir_path = tmp_path / "cache" / "ocr_validation"

    manager = ValidationManager(cache_dir_path=cache_dir_path, dev=True)

    manager._update_char_dims("A", (10, 20))

    assert (repo_data_dir_path / "char_dims_1.csv").read_text(encoding="utf-8") == (
        "A,10,20\n"
    )
    assert not (cache_dir_path / "char_dims_1.csv").exists()


def test_validation_manager_logs_automatic_gap_corrections(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
):
    """Test automatic gap text corrections are logged at info level."""
    repo_root_path = tmp_path / "repo"
    repo_data_dir_path = repo_root_path / "data" / "ocr"
    repo_data_dir_path.mkdir(parents=True)
    monkeypatch.setattr(validation_manager, "package_root", repo_root_path)
    monkeypatch.setattr(
        validation_manager,
        "get_bboxes",
        lambda img: [Bbox(0, 10, 0, 20), Bbox(21, 31, 0, 20)],
    )
    manager = ValidationManager(cache_dir_path=tmp_path / "cache")
    manager.char_dims_by_n[1]["A"] = {(10, 20)}
    manager.char_dims_by_n[1]["B"] = {(10, 20)}
    manager.char_pair_gaps[("A", "B")] = (22, 41, 90, 200)
    series = ImageSeries(
        events=[
            ImageSubtitle(
                img=Image.new("LA", (40, 20), (255, 255)),
                start=0,
                end=1000,
                text="A B",
            )
        ]
    )
    caplog.set_level(logging.INFO, logger=validation_manager.__name__)

    output = manager.validate(series)

    assert output.events[0].text == "AB"
    assert (
        "Sub    1 | Char  1 | A B | 'A,B' -> 11 | corrected gap text from ' ' to ''"
    ) in [record.getMessage() for record in caplog.records]
