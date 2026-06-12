#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the style audit helper script."""

from __future__ import annotations

import importlib.util
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Protocol, cast

import pytest

REPO_DIR_PATH = Path(__file__).resolve().parents[1]
AUDIT_STYLE_PATH = REPO_DIR_PATH / "skills/audit-style/scripts/audit_style.py"
COPYRIGHT_LINE_ONE = (
    "#  Copyright 2017-2026 Karl T Debiec. All rights reserved. "
    "This software may be modified"
)
COPYRIGHT_LINE_TWO = (
    "#  and distributed under the terms of the BSD license. "
    "See the LICENSE file for details."
)


class StyleNoteLike(Protocol):
    """Protocol for style audit notes loaded from the audit script."""

    category: str
    """Style category."""

    line_number: int
    """Source line number."""

    message: str
    """Note text."""


AuditFile = Callable[[Path, dict[str, list[StyleNoteLike]]], None]
GetPythonFiles = Callable[[Path], list[Path]]


def test_get_python_files_excludes_local_directory(tmp_path: Path):
    """Test local scratch files are excluded from recursive style audits."""
    source_path = tmp_path / "scinoephile/source.py"
    local_path = tmp_path / "local/scratch.py"
    source_path.parent.mkdir()
    local_path.parent.mkdir()
    source_path.write_text("", encoding="utf-8")
    local_path.write_text("", encoding="utf-8")

    file_paths = get_python_files()(tmp_path)

    assert file_paths == [source_path]


def test_audit_file_reads_source_as_utf8(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Test source files are read with explicit UTF-8 encoding."""
    source_path = write_source(tmp_path / "sample.py", '"""Café."""')
    original_read_text = Path.read_text

    def read_text(
        path: Path, encoding: str | None = None, errors: str | None = None
    ) -> str:
        """Require audit source reads to pass explicit UTF-8 encoding."""
        if path == source_path and encoding != "utf-8":
            raise AssertionError("expected explicit UTF-8 source read")
        return original_read_text(path, encoding=encoding, errors=errors)

    monkeypatch.setattr(Path, "read_text", read_text)
    notes: dict[str, list[StyleNoteLike]] = defaultdict(list)

    audit_file()(source_path, notes)


def test_audit_file_flags_percent_interpolation_arguments(tmp_path: Path):
    """Test audit flags logging-style percent interpolation arguments."""
    source_path = write_source(
        tmp_path / "sample.py",
        "\n".join(
            [
                '"""Sample module."""',
                "",
                "from __future__ import annotations",
                "",
                "",
                "def render(name: str) -> str:",
                '    """Render a name."""',
                '    logger.warning("hello %s", name)',
                '    return f"hello {name}"',
            ]
        ),
    )
    notes: dict[str, list[StyleNoteLike]] = defaultdict(list)

    audit_file()(source_path, notes)

    assert get_string_note_messages(notes) == [
        "uses `%` interpolation arguments; prefer f-strings"
    ]


def audit_file() -> AuditFile:
    """Get the audit-file function from the audit script.

    Returns:
        audit-file function
    """
    return cast(AuditFile, getattr(get_audit_style_module(), "audit_file"))


def get_audit_style_module() -> ModuleType:
    """Load the audit-style helper module.

    Returns:
        loaded audit-style module
    """
    spec = importlib.util.spec_from_file_location("audit_style", AUDIT_STYLE_PATH)
    if spec is None or spec.loader is None:
        pytest.fail(f"Could not load audit script at {AUDIT_STYLE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_python_files() -> GetPythonFiles:
    """Get the get-python-files function from the audit script.

    Returns:
        get-python-files function
    """
    return cast(GetPythonFiles, getattr(get_audit_style_module(), "get_python_files"))


def get_string_note_messages(
    notes: dict[str, list[StyleNoteLike]],
) -> list[str]:
    """Get string style note messages from audit notes.

    Arguments:
        notes: style notes by file
    Returns:
        string style note messages
    """
    return [
        note.message
        for file_notes in notes.values()
        for note in file_notes
        if note.category == "Strings"
    ]


def write_source(source_path: Path, body: str) -> Path:
    """Write a Python source file with the repository copyright header.

    Arguments:
        source_path: path to write
        body: source body after the copyright header
    Returns:
        written source path
    """
    source_path.write_text(
        "\n".join([COPYRIGHT_LINE_ONE, COPYRIGHT_LINE_TWO, body]) + "\n",
        encoding="utf-8",
    )
    return source_path
