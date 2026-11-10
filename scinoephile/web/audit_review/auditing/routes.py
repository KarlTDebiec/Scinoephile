#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Routes for starting an audit and reporting its progress."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from scinoephile.core import ScinoephileError
from scinoephile.core.dependencies.web import import_flask
from scinoephile.web.audit_review.rerun_confirmation import confirm_rerun
from scinoephile.web.audit_review.workspace import get_view_context
from scinoephile.workflows.review_audit.filters import AuditFilters
from scinoephile.workflows.review_audit.project import ReviewAuditProject

from .job import AuditingJob

if TYPE_CHECKING:
    from scinoephile.core.dependencies.web import FlaskApp

__all__ = ["register_auditing_routes"]


def register_auditing_routes(app: FlaskApp, audit: ReviewAuditProject):
    """Register the independent audit card and background worker.

    Arguments:
        app: local audit application
        audit: source-backed review session
    """
    flask = import_flask()
    auditing = AuditingJob(audit)
    app.extensions["review_auditing"] = auditing

    @app.context_processor
    def auditing_context() -> dict[str, object]:
        """Provide current independent audit progress.

        Returns:
            audit card state
        """
        state = auditing.snapshot()
        visibility = flask.request.args.get("reaudit")
        return {
            "auditing": state,
            "auditing_blocked": audit.proofreading_running,
            "show_auditing": visibility == "1"
            or (visibility is None and state.status in {"running", "error"}),
        }

    @app.post("/auditing")
    def start_auditing():
        """Reserve review state and show progress with editing temporarily disabled.

        Returns:
            current page reload or inline configuration error
        """
        rerun = flask.request.form.get("rerun") == "on"
        try:
            if not confirm_rerun("auditing", rerun=rerun):
                state = replace(
                    auditing.snapshot(),
                    **{
                        name: flask.request.form.get(name, "")
                        for name in ("provider", "model", "effort")
                    },
                )
                if flask.request.headers.get("HX-Request") != "true":
                    return flask.render_template(
                        "index.html",
                        **get_view_context(audit, AuditFilters()),
                        auditing=state,
                        show_auditing=True,
                    )
                return flask.render_template(
                    "auditing/_card.html", auditing=state, show_auditing=True
                )
            auditing.start(
                flask.request.form.get("provider", ""),
                flask.request.form.get("model", ""),
                flask.request.form.get("effort", ""),
                rerun=rerun,
            )
        except (ValueError, ScinoephileError) as exc:
            if flask.request.headers.get("HX-Request") == "true":
                return flask.render_template(
                    "auditing/_card.html",
                    auditing=auditing.snapshot(),
                    auditing_message=str(exc),
                    show_auditing=True,
                )
            return flask.render_template("error.html", message=str(exc)), 409
        if flask.request.headers.get("HX-Request") == "true":
            return "", 200, {"HX-Refresh": "true"}
        return flask.redirect(flask.url_for("index"), code=303)

    @app.get("/auditing")
    def auditing_status():
        """Poll only the audit card until completion or failure.

        Returns:
            progress fragment or reload when editable rows may be shown again
        """
        if flask.request.headers.get("HX-Request") != "true":
            return flask.redirect(flask.url_for("index"), code=303)
        state = auditing.snapshot()
        if state.status in {"complete", "error"}:
            return "", 200, {"HX-Refresh": "true"}
        return flask.render_template("auditing/_card.html", auditing=state)
