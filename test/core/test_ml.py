#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of shared machine-learning helpers."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from scinoephile.core import ml
from scinoephile.core.ml import get_huggingface_snapshot_dir_path


def test_huggingface_snapshot_uses_complete_local_cache(
    monkeypatch: pytest.MonkeyPatch,
):
    """A complete cached snapshot should not allow network access.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    snapshot_download = Mock(return_value="/cached/model")
    monkeypatch.setattr(
        ml,
        "import_huggingface_hub",
        Mock(return_value=SimpleNamespace(snapshot_download=snapshot_download)),
    )

    model_dir_path = get_huggingface_snapshot_dir_path(
        "organization/model", "revision", ("config.json", "model.safetensors")
    )

    assert model_dir_path == Path("/cached/model")
    snapshot_download.assert_called_once_with(
        repo_id="organization/model",
        revision="revision",
        allow_patterns=("config.json", "model.safetensors"),
        local_files_only=True,
    )


def test_huggingface_snapshot_downloads_after_local_miss(
    monkeypatch: pytest.MonkeyPatch,
):
    """A missing cached snapshot should fall back to network access.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    snapshot_download = Mock(side_effect=[OSError("not cached"), "/cached/model"])
    monkeypatch.setattr(
        ml,
        "import_huggingface_hub",
        Mock(return_value=SimpleNamespace(snapshot_download=snapshot_download)),
    )

    model_dir_path = get_huggingface_snapshot_dir_path("organization/model", "revision")

    assert model_dir_path == Path("/cached/model")
    local_kwargs = dict(snapshot_download.call_args_list[0].kwargs)
    remote_kwargs = dict(snapshot_download.call_args_list[1].kwargs)
    assert local_kwargs["repo_id"] == "organization/model"
    assert local_kwargs["revision"] == "revision"
    assert local_kwargs["local_files_only"] is True
    assert "*.safetensors" in local_kwargs["allow_patterns"]
    del local_kwargs["local_files_only"]
    assert remote_kwargs == local_kwargs
