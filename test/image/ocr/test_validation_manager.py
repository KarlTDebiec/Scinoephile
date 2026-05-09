#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of OCR validation manager data storage."""

from __future__ import annotations

from scinoephile.image.ocr.validation import ValidationManager, validation_manager


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

    manager = ValidationManager(
        cache_dir_path=cache_dir_path,
    )

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

    manager = ValidationManager(
        cache_dir_path=cache_dir_path,
        dev=True,
    )

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

    manager = ValidationManager(
        cache_dir_path=cache_dir_path,
    )

    manager._update_char_dims("A", (10, 20))

    assert (cache_dir_path / "char_dims_1.csv").read_text(encoding="utf-8") == (
        "A,10,20\n"
    )
    assert not (repo_data_dir_path / "char_dims_1.csv").exists()


def test_validation_manager_writes_updates_to_repo_in_dev_mode(tmp_path, monkeypatch):
    """Test dev mode writes OCR validation data updates to repo data."""
    repo_root_path = tmp_path / "repo"
    repo_data_dir_path = repo_root_path / "data" / "ocr"
    repo_data_dir_path.mkdir(parents=True)
    monkeypatch.setattr(validation_manager, "package_root", repo_root_path)
    cache_dir_path = tmp_path / "cache" / "ocr_validation"

    manager = ValidationManager(
        cache_dir_path=cache_dir_path,
        dev=True,
    )

    manager._update_char_dims("A", (10, 20))

    assert (repo_data_dir_path / "char_dims_1.csv").read_text(encoding="utf-8") == (
        "A,10,20\n"
    )
    assert not (cache_dir_path / "char_dims_1.csv").exists()
