#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Flask app setup for the subtitle audit editor."""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from scinoephile.common import package_root
from scinoephile.core import ScinoephileError
from scinoephile.core.dependencies.web import import_flask, import_werkzeug_serving
from scinoephile.core.llms import ReasoningEffort
from scinoephile.llms.providers.registry import get_provider_names
from scinoephile.operations.review_audit.project import ReviewAuditProject
from scinoephile.web.security import create_local_app

from .auditing.routes import register_auditing_routes
from .editor_routes import register_editor_routes
from .proofreading.routes import register_proofreading_routes
from .workspace import get_row_differences, get_row_time_label

if TYPE_CHECKING:
    from scinoephile.core.dependencies.web import FlaskApp

__all__ = ["create_app", "serve_audit"]

logger = getLogger(__name__)


def create_app(audit: ReviewAuditProject, *, title: str | None = None) -> FlaskApp:
    """Create the proofreading editor; the original SRT remains read-only.

    Arguments:
        audit: loaded project and independent audit state
        title: display title, defaulting to the input filename stem
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
    title = title or audit.infile_path.stem
    app.add_template_filter(get_row_differences, "audit_differences")
    app.add_template_filter(get_row_time_label, "audit_time_label")

    @app.context_processor
    def editor_context() -> dict[str, object]:
        """Expose the editor title and shared LLM choices.

        Returns:
            editor title, available providers, and reasoning levels
        """
        return {
            "title": title,
            "provider_names": get_provider_names(),
            "reasoning_levels": tuple(ReasoningEffort),
        }

    register_editor_routes(app, audit)
    register_auditing_routes(app, audit)
    register_proofreading_routes(app, audit)
    return app


def serve_audit(
    audit: ReviewAuditProject,
    *,
    title: str | None = None,
    host: str = "127.0.0.1",
    port: int = 5020,
):
    """Serve the local audit app using the existing optional web stack.

    Arguments:
        audit: loaded audit project
        title: display title override
        host: loopback host address
        port: local TCP port
    Raises:
        ScinoephileError: if a server I/O operation fails
    """
    serving = import_werkzeug_serving()
    try:
        server = serving.make_server(
            host, port, create_app(audit, title=title), threaded=True
        )
        try:
            logger.info(f"Subtitle audit: http://{host}:{port}/")
            server.serve_forever()
        finally:
            server.server_close()
    except OSError as exc:
        raise ScinoephileError(
            f"Unable to run review editor on {host}:{port}: {exc}"
        ) from exc
