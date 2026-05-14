#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for optional runtime dependency boundaries."""

from __future__ import annotations

import builtins
import importlib
import sys
import tomllib
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

REPO_DIR_PATH = Path(__file__).resolve().parents[1]
PYPROJECT_PATH = REPO_DIR_PATH / "pyproject.toml"


@contextmanager
def _blocked_imports(
    monkeypatch: pytest.MonkeyPatch,
    *,
    blocked_roots: set[str],
    purge_prefixes: set[str],
) -> Iterator[None]:
    """Temporarily block selected import roots and purge selected modules.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        blocked_roots: root module names to report as uninstalled
        purge_prefixes: module prefixes to remove before importing
    """
    original_import = builtins.__import__
    original_import_module = importlib.import_module
    saved_modules = _pop_modules(blocked_roots | purge_prefixes)

    def guarded_import(
        name: str,
        globals_: dict[str, Any] | None = None,
        locals_: dict[str, Any] | None = None,
        fromlist: Sequence[str] | None = (),
        level: int = 0,
    ) -> ModuleType:
        """Import while pretending selected root modules are unavailable."""
        if level == 0 and name.split(".", 1)[0] in blocked_roots:
            missing_name = name.split(".", 1)[0]
            raise ModuleNotFoundError(
                f"No module named '{missing_name}'",
                name=missing_name,
            )
        return original_import(name, globals_, locals_, fromlist, level)

    def guarded_import_module(name: str, package: str | None = None) -> ModuleType:
        """Import a module while pretending selected root modules are unavailable."""
        if name.split(".", 1)[0] in blocked_roots:
            missing_name = name.split(".", 1)[0]
            raise ModuleNotFoundError(
                f"No module named '{missing_name}'",
                name=missing_name,
            )
        return original_import_module(name, package)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    monkeypatch.setattr(importlib, "import_module", guarded_import_module)
    try:
        yield
    finally:
        _pop_modules(blocked_roots | purge_prefixes)
        sys.modules.update(saved_modules)


def test_audio_transcription_package_imports_without_ml_dependencies(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test transcription package imports without ML runtime extras."""
    with _blocked_imports(
        monkeypatch,
        blocked_roots={
            "demucs_infer",
            "huggingface_hub",
            "torch",
            "torchaudio",
            "whisper_timestamped",
        },
        purge_prefixes={"scinoephile.audio"},
    ):
        from scinoephile.audio import transcription  # noqa: PLC0415
        from scinoephile.audio.transcription import (  # noqa: PLC0415
            DemucsSeparator,
            WhisperTranscriber,
        )

        assert DemucsSeparator.__name__ == "DemucsSeparator"
        assert transcription.TranscribedSegment.__name__ == "TranscribedSegment"
        assert transcription.TranscribedWord.__name__ == "TranscribedWord"
        assert WhisperTranscriber.__name__ == "WhisperTranscriber"
        assert callable(transcription.get_segment_split_on_whitespace)


def test_core_llms_package_imports_without_openai(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test LLM abstractions import without the OpenAI SDK extra."""
    with _blocked_imports(
        monkeypatch,
        blocked_roots={"openai"},
        purge_prefixes={
            "scinoephile.core",
            "scinoephile.llms.providers",
        },
    ):
        from scinoephile.core import llms  # noqa: PLC0415
        from scinoephile.core.llms import OpenAIProviderBase  # noqa: PLC0415
        from scinoephile.llms.providers import (  # noqa: PLC0415
            DeepSeekProvider,
            OpenAIProvider,
            registry,  # noqa: PLC0415
        )

        assert llms.Answer.__name__ == "Answer"
        assert llms.LLMProvider.__name__ == "LLMProvider"
        assert DeepSeekProvider.__name__ == "DeepSeekProvider"
        assert OpenAIProvider.__name__ == "OpenAIProvider"
        assert OpenAIProviderBase.__name__ == "OpenAIProviderBase"

        with pytest.raises(ImportError, match="llm"):
            registry.get_default_provider()


def test_image_subtitles_package_imports_without_ocr_dependencies(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test image subtitle package import does not require OCR extras."""
    with _blocked_imports(
        monkeypatch,
        blocked_roots={"numba"},
        purge_prefixes={"scinoephile.image"},
    ):
        from scinoephile.image.subtitles import (  # noqa: PLC0415
            ImageSeries,
            ImageSubtitle,
        )

        assert ImageSeries.__name__ == "ImageSeries"
        assert ImageSubtitle.__name__ == "ImageSubtitle"


def test_runtime_heavy_dependencies_are_optional():
    """Test heavyweight runtime dependencies are assigned to extras."""
    project = _load_pyproject()["project"]
    base_dependency_names = _get_dependency_names(project["dependencies"])
    extras = project["optional-dependencies"]

    assert base_dependency_names.isdisjoint(
        {
            "demucs-infer",
            "huggingface-hub",
            "numba",
            "onnxruntime",
            "openai",
            "torch",
            "torchaudio",
            "transformers",
            "whisper-timestamped",
        }
    )
    assert "numba" in _get_dependency_names(extras["ocr"])
    assert _get_dependency_names(extras["llm"]) == {"openai"}
    assert {
        "huggingface-hub",
        "onnxruntime",
        "torch",
        "transformers",
        "whisper-timestamped",
    }.issubset(_get_dependency_names(extras["transcription"]))
    assert {
        "demucs-infer",
        "torch",
        "torchaudio",
    }.issubset(_get_dependency_names(extras["demucs"]))


def _get_dependency_names(requirements: list[str]) -> set[str]:
    """Get normalized dependency names from requirement strings.

    Arguments:
        requirements: Python requirement strings
    Returns:
        dependency names
    """
    names = set()
    for requirement in requirements:
        name = requirement.split(";", 1)[0]
        name = name.split("[", 1)[0]
        for separator in ("<", ">", "=", "!", "~"):
            name = name.split(separator, 1)[0]
        names.add(name.strip())
    return names


def _load_pyproject() -> dict[str, Any]:
    """Load the project configuration.

    Returns:
        parsed pyproject data
    """
    return tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))


def _pop_modules(module_names: set[str]) -> dict[str, ModuleType]:
    """Remove modules matching root names or prefixes from sys.modules.

    Arguments:
        module_names: module roots or prefixes to remove
    Returns:
        removed modules, keyed by full module name
    """
    removed_modules: dict[str, ModuleType] = {}
    for module_name in list(sys.modules):
        if any(
            module_name == prefix or module_name.startswith(f"{prefix}.")
            for prefix in module_names
        ):
            removed_modules[module_name] = sys.modules.pop(module_name)
    return removed_modules
