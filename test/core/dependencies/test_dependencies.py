#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of centralized optional dependency access."""

from __future__ import annotations

from builtins import __import__ as builtin_import
from importlib import import_module
from pkgutil import iter_modules
from types import SimpleNamespace
from warnings import catch_warnings, simplefilter, warn

from pytest import MonkeyPatch

from scinoephile.core import dependencies
from scinoephile.core.dependencies.transcription import import_pyannote_audio


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


def test_pyannote_import_ignores_irrelevant_torchcodec_warning(
    monkeypatch: MonkeyPatch,
):
    """Ignore pyannote's warning when its unused file decoder is unavailable.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    pyannote_audio = SimpleNamespace()
    pyannote = SimpleNamespace(audio=pyannote_audio)

    def import_module_with_warning(
        name: str,
        globals_: dict[str, object] | None = None,
        locals_: dict[str, object] | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> object:
        """Return mocked pyannote after emitting its decoder warning."""
        if name != "pyannote.audio":
            return builtin_import(name, globals_, locals_, fromlist, level)
        warn(
            "torchcodec is not installed correctly so built-in audio decoding will "
            "fail.",
            UserWarning,
            stacklevel=2,
        )
        return pyannote

    monkeypatch.setattr("builtins.__import__", import_module_with_warning)

    with catch_warnings(record=True) as caught_warnings:
        simplefilter("always")
        module = import_pyannote_audio()

    assert module is pyannote_audio
    assert caught_warnings == []
