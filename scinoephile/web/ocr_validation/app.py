#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Flask app for OCR validation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scinoephile.core import ScinoephileError

from .session import OcrValidationSession

if TYPE_CHECKING:
    from flask import Flask

__all__ = [
    "create_app",
    "run_app",
]

_WEB_EXTRA_MESSAGE = (
    "OCR validation web UI support requires optional web dependencies. "
    "Install scinoephile with the 'web' extra."
)


def create_app(session: OcrValidationSession) -> Flask:
    """Create the OCR validation Flask app.

    Arguments:
        session: OCR validation session
    Returns:
        Flask app
    Raises:
        ScinoephileError: if optional web dependencies are not installed
    """
    try:
        from flask import Flask  # noqa: PLC0415

        from .routes import register_routes  # noqa: PLC0415
    except ImportError as exc:
        raise ScinoephileError(_WEB_EXTRA_MESSAGE) from exc

    app = Flask(__name__)
    app.config["OCR_VALIDATION_SESSION"] = session
    register_routes(app)
    return app


def run_app(session: OcrValidationSession, host: str, port: int):
    """Run the OCR validation Flask app.

    Arguments:
        session: OCR validation session
        host: host address to bind
        port: port to bind
    Raises:
        ScinoephileError: if optional dependencies are missing or server startup fails
    """
    try:
        create_app(session).run(host, port)
    except (OSError, ValueError) as exc:
        raise ScinoephileError(
            f"Unable to run OCR validation web app on {host}:{port}: {exc}"
        ) from exc
