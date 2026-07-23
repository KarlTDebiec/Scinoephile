#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the OCR validation web app."""

from __future__ import annotations

import logging
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import cast

from pytest import LogCaptureFixture, MonkeyPatch, raises

from scinoephile.common import package_root
from scinoephile.common.subprocess import run_command
from scinoephile.core import ScinoephileError
from scinoephile.web.ocr_validation.app import create_app, run_app
from scinoephile.web.ocr_validation.session import OcrValidationSession


def test_create_app_uses_shared_web_static_dir():
    """Test OCR validation serves shared web static assets."""
    app = create_app(cast(OcrValidationSession, object()))

    assert app.static_folder is not None
    assert Path(app.static_folder) == package_root / "web/static"


def test_create_app_import_error_is_actionable(monkeypatch: MonkeyPatch):
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

    with raises(ScinoephileError, match="'web' extra") as excinfo:
        create_app(cast(OcrValidationSession, object()))

    assert isinstance(excinfo.value.__cause__, ImportError)


def test_run_app_wraps_server_errors(monkeypatch: MonkeyPatch):
    """Test web app server errors are user-facing."""
    monkeypatch.setattr(
        "scinoephile.web.ocr_validation.app._port_is_in_use",
        lambda host, port: False,
    )
    monkeypatch.setattr(
        "scinoephile.web.ocr_validation.app.create_app",
        lambda session: object(),
    )
    monkeypatch.setattr(
        "werkzeug.serving.make_server",
        lambda host, port, app: (_ for _ in ()).throw(
            OSError(f"cannot bind {host}:{port}")
        ),
    )

    with raises(
        ScinoephileError,
        match=(
            "Unable to run OCR validation web app on 127.0.0.1:5000: "
            "cannot bind 127.0.0.1:5000"
        ),
    ) as excinfo:
        run_app(cast(OcrValidationSession, object()), "127.0.0.1", 5000)

    assert isinstance(excinfo.value.__cause__, OSError)


def test_run_app_import_error_is_actionable(monkeypatch: MonkeyPatch):
    """Test missing Werkzeug dependency produces an actionable error."""
    real_import = __import__

    def fake_import(
        name: str,
        globals_: Mapping[str, object] | None = None,
        locals_: Mapping[str, object] | None = None,
        fromlist: Sequence[str] | None = (),
        level: int = 0,
    ) -> object:
        """Fake import that treats Werkzeug as missing.

        Arguments:
            name: module name
            globals_: global namespace
            locals_: local namespace
            fromlist: names to import
            level: import level
        Returns:
            imported module
        Raises:
            ImportError: if importing werkzeug
        """
        if name == "werkzeug.serving":
            raise ImportError("missing werkzeug")
        return real_import(name, globals_, locals_, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import)

    with raises(ScinoephileError, match="'web' extra") as excinfo:
        run_app(cast(OcrValidationSession, object()), "127.0.0.1", 5000)

    assert isinstance(excinfo.value.__cause__, ImportError)


def test_run_app_uses_available_port_when_requested_port_is_in_use(
    caplog: LogCaptureFixture,
    monkeypatch: MonkeyPatch,
):
    """Test web app falls back when the requested port is already occupied."""

    class FakeServer:
        """Fake Werkzeug server."""

        server_port = 54321

        def serve_forever(self):
            """Serve until stopped."""

    class FakeApp:
        """Fake Flask app."""

        def __init__(self):
            """Initialize."""
            self.config: dict[str, object] = {}

    captured: dict[str, int] = {}

    def fake_make_server(host: str, port: int, app: object) -> FakeServer:
        """Fake Werkzeug server factory.

        Arguments:
            host: host address to bind
            port: port to bind
            app: WSGI app
        Returns:
            fake server
        """
        captured["port"] = port
        return FakeServer()

    caplog.set_level(logging.INFO, logger="scinoephile.web.ocr_validation.app")
    monkeypatch.setattr(
        "scinoephile.web.ocr_validation.app._port_is_in_use",
        lambda host, port: True,
    )
    monkeypatch.setattr(
        "scinoephile.web.ocr_validation.app.create_app",
        lambda session: FakeApp(),
    )
    monkeypatch.setattr("werkzeug.serving.make_server", fake_make_server)

    run_app(cast(OcrValidationSession, object()), "127.0.0.1", 5000)

    assert captured["port"] == 0
    assert "OCR validation web UI port 5000 is already in use" in caplog.text
    assert "OCR validation web UI: http://127.0.0.1:54321/" in caplog.text


def test_web_package_imports_flask_only_when_needed():
    """Test importing OCR validation web support does not import Flask."""
    exitcode, _, _ = run_command(
        [
            sys.executable,
            "-c",
            (
                "import sys;"
                "import scinoephile.web.ocr_validation;"
                "raise SystemExit('flask' in sys.modules)"
            ),
        ],
    )

    assert exitcode == 0
