#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Routes for starting proofreading and reporting its progress."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from scinoephile.core import ScinoephileError
from scinoephile.core.dependencies.web import import_flask
from scinoephile.operations.review_audit.filters import AuditFilters
from scinoephile.operations.review_audit.project import ReviewAuditProject
from scinoephile.web.audit_review.rerun_confirmation import confirm_rerun
from scinoephile.web.audit_review.workspace import get_view_context

from .job import ProofreadingJob

if TYPE_CHECKING:
    from scinoephile.core.dependencies.web import FlaskApp

__all__ = ["register_proofreading_routes"]


def register_proofreading_routes(app: FlaskApp, audit: ReviewAuditProject):
    """Register the proofreading card and background worker.

    Arguments:
        app: local audit application
        audit: source-backed session owning output creation
    """
    flask = import_flask()
    proofreading = ProofreadingJob(audit)
    app.extensions["audit_proofreading"] = proofreading

    @app.context_processor
    def proofreading_context() -> dict[str, object]:
        """Provide the current proofreading state and card visibility.

        Returns:
            proofreading card context
        """
        state = proofreading.snapshot()
        visibility = flask.request.args.get("reproofread")
        return {
            "proofreading": state,
            "proofreading_blocked": audit.auditing_running,
            "reproofreading": not state.available,
            "show_proofreading": visibility == "1"
            or (visibility is None and state.status in {"running", "error"}),
        }

    @app.post("/proofreading")
    def start_proofreading():
        """Start a CSRF-protected run and immediately return progress.

        Returns:
            current card, validation error, or ordinary redirect
        """
        message = ""
        status = 200
        rerun = audit.outfile_path.exists()
        try:
            if not confirm_rerun("proofreading", rerun=rerun):
                state = replace(
                    proofreading.snapshot(),
                    **{
                        name: flask.request.form.get(name, "")
                        for name in ("provider", "model", "effort")
                    },
                )
                if flask.request.headers.get("HX-Request") != "true":
                    return flask.render_template(
                        "index.html",
                        **get_view_context(audit, AuditFilters()),
                        proofreading=state,
                        reproofreading=True,
                        show_proofreading=True,
                    )
                return flask.render_template(
                    "proofreading/_card.html",
                    proofreading=state,
                    reproofreading=True,
                    show_proofreading=True,
                )
            proofreading.start(
                flask.request.form.get("provider", ""),
                flask.request.form.get("model", ""),
                flask.request.form.get("effort", ""),
                rerun=rerun,
            )
        except (ValueError, ScinoephileError) as exc:
            message = str(exc)
            status = 409
        if flask.request.headers.get("HX-Request") == "true":
            state = proofreading.snapshot()
            if not message and state.status in {"running", "complete"}:
                return "", 200, {"HX-Refresh": "true"}
            return flask.render_template(
                "proofreading/_card.html",
                proofreading=state,
                proofreading_message=message,
                reproofreading=rerun,
                show_proofreading=True,
            ), status
        if message:
            return flask.render_template("error.html", message=message), status
        return flask.redirect(flask.url_for("index"), code=303)

    @app.get("/proofreading")
    def proofreading_status():
        """Refresh progress without replacing subtitle drafts or filter controls.

        Returns:
            progress card or a completed-run navigation
        """
        if flask.request.headers.get("HX-Request") != "true":
            return flask.redirect(flask.url_for("index"), code=303)
        state = proofreading.snapshot()
        if state.status in {"complete", "error"}:
            return "", 200, {"HX-Refresh": "true"}
        return flask.render_template("proofreading/_card.html", proofreading=state)
