#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Flask app setup for the subtitle audit editor."""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from scinoephile.common import package_root
from scinoephile.core import ScinoephileError
from scinoephile.core.dependencies.web import import_flask, import_werkzeug_serving
from scinoephile.web.security import create_local_app

from .routes import register_routes
from .session import AuditSession

if TYPE_CHECKING:
    from scinoephile.core.dependencies.web import FlaskApp

__all__ = ["create_app", "serve_audit"]

logger = getLogger(__name__)


def create_app(audit: AuditSession) -> FlaskApp:
    """Create the proofreading editor; the original SRT remains read-only.

    Arguments:
        audit: loaded project and independent audit state
    Returns:
        local Flask application
    """
    flask = import_flask()
    app = create_local_app(__name__, package_root / "web/static", require_htmx=False)
    app.register_blueprint(
        flask.Blueprint(
            "audit_review_assets",
            __name__,
            static_folder=str(package_root / "web/audit_review/static"),
            static_url_path="/audit-review-assets",
        )
    )
    app.config["MAX_CONTENT_LENGTH"] = 100_000

    register_routes(app, audit)
    return app


def serve_audit(audit: AuditSession, *, host: str = "127.0.0.1", port: int = 5020):
    """Serve the local audit app using the existing optional web stack.

    Arguments:
        audit: loaded audit project
        host: loopback host address
        port: local TCP port
    Raises:
        ScinoephileError: if a server I/O operation fails
    """
    serving = import_werkzeug_serving()
    try:
        server = serving.make_server(host, port, create_app(audit), threaded=True)
        try:
            logger.info(f"Subtitle audit: http://{host}:{port}/")
            server.serve_forever()
        finally:
            server.server_close()
    except OSError as exc:
        raise ScinoephileError(
            f"Unable to run review editor on {host}:{port}: {exc}"
        ) from exc
