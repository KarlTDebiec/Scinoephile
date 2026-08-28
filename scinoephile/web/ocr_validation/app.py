#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Flask app for OCR validation."""

from __future__ import annotations

from logging import getLogger
from socket import create_connection
from typing import TYPE_CHECKING

from scinoephile.common import package_root
from scinoephile.core import DependencyError, ScinoephileError
from scinoephile.core.dependencies.web import import_flask, import_werkzeug_serving

from .session import OcrValidationSession

if TYPE_CHECKING:
    from scinoephile.core.dependencies.web import FlaskApp

__all__ = ["create_app", "run_app"]

logger = getLogger(__name__)


def create_app(session: OcrValidationSession) -> FlaskApp:
    """Create the OCR validation Flask app.

    Arguments:
        session: OCR validation session
    Returns:
        Flask app
    Raises:
        DependencyError: if optional web dependencies are not installed
    """
    try:
        flask = import_flask()
        from .routes import register_routes  # noqa: PLC0415
    except ImportError as exc:
        raise DependencyError(str(exc)) from exc

    static_dir_path = package_root / "web/static"
    app = flask.Flask(__name__, static_folder=str(static_dir_path))
    app.config["OCR_VALIDATION_SESSION"] = session
    app.config["OCR_VALIDATION_SERVER"] = None
    register_routes(app)
    return app


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

    app = create_app(session)
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
