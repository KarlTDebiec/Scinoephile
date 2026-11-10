#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Flask app for OCR validation."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path
from socket import create_connection
from typing import TYPE_CHECKING

from scinoephile.common import package_root
from scinoephile.core import ScinoephileError
from scinoephile.core.dependencies.web import import_werkzeug_serving
from scinoephile.web.security import create_local_app

from .session import OcrValidationSession

if TYPE_CHECKING:
    from scinoephile.core.dependencies.web import FlaskApp

__all__ = ["create_app", "open_validation_editor", "run_app"]

logger = getLogger(__name__)


def create_app(session: OcrValidationSession, *, host: str = "127.0.0.1") -> FlaskApp:
    """Create the OCR validation Flask app.

    Arguments:
        session: OCR validation session
        host: explicitly configured bind host trusted by request validation
    Returns:
        Flask app
    Raises:
        DependencyError: if optional web dependencies are not installed
    """
    from .routes import register_routes  # noqa: PLC0415

    static_dir_path = package_root / "web/static"
    app = create_local_app(__name__, static_dir_path, host=host)
    app.config["OCR_VALIDATION_SESSION"] = session
    app.config["OCR_VALIDATION_SERVER"] = None
    register_routes(app)
    return app


def open_validation_editor(
    source_dir_path: Path,
    outfile_path: Path,
    *,
    validation_data_dir_path: Path | str | None,
    dev: bool,
    host: str,
    port: int,
):
    """Open the OCR validation editor for an image subtitle directory.

    Arguments:
        source_dir_path: directory containing OCR image subtitles
        outfile_path: validated subtitle output path
        validation_data_dir_path: local OCR validation data directory
        dev: whether to write validation data updates to repo data
        host: host address to bind
        port: port to bind
    """
    session = OcrValidationSession.from_dir_path(
        source_dir_path,
        outfile_path=outfile_path,
        validation_data_dir_path=validation_data_dir_path,
        dev=dev,
    )
    run_app(session, host, port)


def run_app(session: OcrValidationSession, host: str, port: int):
    """Run the OCR validation Flask app.

    Arguments:
        session: OCR validation session
        host: host address to bind
        port: port to bind
    Raises:
        DependencyError: if optional web dependencies are not installed
        ScinoephileError: if server startup fails
    """
    werkzeug_serving = import_werkzeug_serving()

    app = create_app(session, host=host)
    try:
        server_port = port
        if _port_is_in_use(_connection_host(host), port):
            logger.warning(
                f"OCR validation web UI port {port} is already in use; "
                "using an available port instead"
            )
            server_port = 0
        server = werkzeug_serving.make_server(host, server_port, app)
        app.config["OCR_VALIDATION_SERVER"] = server
        url_host = _url_host(host)
        url_port = getattr(server, "server_port", server_port)
        logger.info(f"OCR validation web UI: http://{url_host}:{url_port}/")
        server.serve_forever()
    except (OSError, ValueError) as exc:
        raise ScinoephileError(
            f"Unable to run OCR validation web app on {host}:{port}: {exc}"
        ) from exc


def _connection_host(host: str) -> str:
    """Get host to use when checking a bind host for active connections.

    Arguments:
        host: host address to bind
    Returns:
        host address suitable for connection checks
    """
    if host in {"", "0.0.0.0", "::"}:
        return "127.0.0.1"
    return host


def _port_is_in_use(host: str, port: int) -> bool:
    """Check whether a host port already accepts connections.

    Arguments:
        host: host address to check
        port: port to check
    Returns:
        whether the port accepts connections
    """
    if port == 0:
        return False

    try:
        with create_connection((host, port), timeout=0.2):
            return True
    except OSError:
        return False


def _url_host(host: str) -> str:
    """Get host to display in the validation URL.

    Arguments:
        host: host address to bind
    Returns:
        host address suitable for browser URLs
    """
    if host in {"", "0.0.0.0", "::"}:
        return "127.0.0.1"
    return host
