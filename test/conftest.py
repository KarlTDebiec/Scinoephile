#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Configuration of tests of scinoephile."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from PIL import Image
from pytest import MonkeyPatch, fixture

from scinoephile.common.file import get_temp_directory_path, get_temp_file_path
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle

# ruff: noqa: F401 F403
from test.data.acopopb import *
from test.data.acoptc import *
from test.data.kob import *
from test.data.mlamd import *
from test.data.mnt import *
from test.data.t import *
from test.data.tmm import *


@fixture(autouse=True)
def runtime_cache_root_path(tmp_path: Path, monkeypatch: MonkeyPatch) -> Path:
    """Provide an isolated default runtime cache root.

    Arguments:
        tmp_path: temporary directory provided by pytest
        monkeypatch: pytest monkeypatch fixture
    """
    cache_root_path = tmp_path / "runtime-cache"
    monkeypatch.setenv("SCINOEPHILE_CACHE_DIR", str(cache_root_path))
    return cache_root_path


@fixture
def database_path() -> Generator[Path]:
    """Provide a temporary SQLite database path.

    Yields:
        temporary database path
    """
    with get_temp_file_path(".db") as temp_path:
        yield temp_path


@fixture
def local_data_dir_path() -> Generator[Path]:
    """Provide a temporary canonical local data directory.

    Yields:
        temporary local data directory
    """
    with get_temp_directory_path() as dir_path:
        yield dir_path


@fixture
def runtime_data_dir_path() -> Generator[Path]:
    """Provide a temporary runtime canonical data directory.

    Yields:
        temporary runtime data directory
    """
    with get_temp_directory_path() as dir_path:
        yield dir_path


@fixture
def tiny_image_series() -> ImageSeries:
    """Small image subtitle series for tests that do not need full fixtures."""
    return ImageSeries(
        events=[
            ImageSubtitle(
                start=1000,
                end=2000,
                img=Image.new("LA", (4, 3), (255, 255)),
                text="recognized",
            ),
            ImageSubtitle(
                start=3000,
                end=4000,
                img=Image.new("LA", (2, 5), (255, 255)),
                text="validated",
            ),
        ]
    )
