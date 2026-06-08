#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the OCR validation web app."""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Mapping, Sequence
from typing import cast

import pytest

from scinoephile.core import ScinoephileError
from scinoephile.web.ocr_validation.app import create_app, run_app
from scinoephile.web.ocr_validation.session import OcrValidationSession


def test_create_app_import_error_is_actionable(monkeypatch: pytest.MonkeyPatch):
    """Test missing Flask dependency produces an actionable error."""
    real_import = __import__

    def fake_import(
        name: str,
        globals_: Mapping[str, object] | None = None,
        locals_: Mapping[str, object] | None = None,
        fromlist: Sequence[str] | None = (),
        level: int = 0,
    ) -> object:
        """Fake import that treats Flask as missing.

        Arguments:
            name: module name
            globals_: global namespace
            locals_: local namespace
            fromlist: names to import
            level: import level
        Returns:
            imported module
        Raises:
            ImportError: if importing flask
        """
        if name == "flask":
            raise ImportError("missing flask")
        return real_import(name, globals_, locals_, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import)

    with pytest.raises(ScinoephileError, match="'web' extra") as excinfo:
        create_app(cast(OcrValidationSession, object()))

    assert isinstance(excinfo.value.__cause__, ImportError)


def test_run_app_wraps_server_errors(monkeypatch: pytest.MonkeyPatch):
    """Test web app server errors are user-facing."""

    class FakeApp:
        """Fake Flask app."""

        def run(self, host: str, port: int):
            """Raise a server startup error.

            Arguments:
                host: Flask app host
                port: Flask app port
            """
            raise OSError(f"cannot bind {host}:{port}")

    monkeypatch.setattr(
        "scinoephile.web.ocr_validation.app.create_app",
        lambda session: FakeApp(),
    )

    with pytest.raises(
        ScinoephileError,
        match=(
            "Unable to run OCR validation web app on 127.0.0.1:5000: "
            "cannot bind 127.0.0.1:5000"
        ),
    ) as excinfo:
        run_app(cast(OcrValidationSession, object()), "127.0.0.1", 5000)

    assert isinstance(excinfo.value.__cause__, OSError)


def test_web_package_imports_flask_only_when_needed():
    """Test importing OCR validation web support does not import Flask."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys;"
                "import scinoephile.web.ocr_validation;"
                "raise SystemExit('flask' in sys.modules)"
            ),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
