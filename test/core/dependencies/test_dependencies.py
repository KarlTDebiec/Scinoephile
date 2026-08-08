#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of centralized optional dependency access."""

from __future__ import annotations

from importlib import import_module
from pkgutil import iter_modules
from types import ModuleType
from unittest.mock import Mock

from pytest import MonkeyPatch

from scinoephile.core import dependencies
from scinoephile.core.dependencies import transcription


def test_dependency_exports_use_lazy_import_naming():
    """Test dependency helpers use the public lazy-import naming convention."""
    module_names = sorted(
        module_info.name
        for module_info in iter_modules(
            dependencies.__path__, f"{dependencies.__name__}."
        )
        if not module_info.name.rsplit(".", 1)[-1].startswith("_")
    )

    assert module_names
    for module_name in module_names:
        module = import_module(module_name)
        exports = getattr(module, "__all__", None)
        assert isinstance(exports, list)
        assert all(name.startswith("import_") for name in exports)


def test_whisper_timestamped_transcribe_imports_submodule(monkeypatch: MonkeyPatch):
    """Import the VAD-bearing submodule rather than its namesake function.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    transcribe_module = ModuleType("whisper_timestamped.transcribe")
    import_module_mock = Mock(return_value=transcribe_module)
    monkeypatch.setattr(transcription, "import_module", import_module_mock)

    imported = transcription.import_whisper_timestamped_transcribe()

    assert imported is transcribe_module
    import_module_mock.assert_called_once_with("whisper_timestamped.transcribe")
