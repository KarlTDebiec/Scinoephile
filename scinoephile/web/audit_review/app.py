#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Server-rendered, progressively enhanced subtitle audit browser."""

from __future__ import annotations

from dataclasses import asdict, replace
from logging import getLogger
from secrets import compare_digest, token_urlsafe
from time import time
from typing import TYPE_CHECKING
from urllib.parse import urlencode, urlsplit

from scinoephile.common import package_root
from scinoephile.core import ScinoephileError
from scinoephile.core.dependencies.web import import_flask, import_werkzeug_serving
from scinoephile.core.llms import ReasoningEffort
from scinoephile.llms.providers.registry import get_provider_names

from .auditing import AuditingJob
from .proofreading import ProofreadingJob
from .session import AuditFilters, AuditSession

if TYPE_CHECKING:
    from collections.abc import Mapping

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
    app = flask.Flask(
        __name__,
        static_folder=str(package_root / "web/static"),
        template_folder=str(package_root / "web/audit_review/templates"),
    )
    app.register_blueprint(
        flask.Blueprint(
            "audit_review_assets",
            __name__,
            static_folder=str(package_root / "web/audit_review/static"),
            static_url_path="/audit-review-assets",
        )
    )
    app.config.update(
        SECRET_KEY=token_urlsafe(32),
        SESSION_COOKIE_SAMESITE="Strict",
        MAX_CONTENT_LENGTH=100_000,
    )
    app.json.ensure_ascii = False

    _register_operation_routes(app, audit)

    @app.get("/")
    def index():
        """Render full pages or HTMX fragments from the same GET route.

        Returns:
            rendered audit page
        """
        try:
            view = _get_view_context(audit, _parse_filters(flask.request.args))
        except ValueError as exc:
            return flask.render_template("error.html", message=str(exc)), 400
        template = "index.html"
        if (
            flask.request.headers.get("HX-Request") == "true"
            and flask.request.headers.get("HX-History-Restore-Request") != "true"
        ):
            template = "_workspace.html"
            if flask.request.headers.get("HX-Target") == "load-more":
                template = "_batch.html"
        return flask.render_template(template, **view)

    @app.post("/rows/<key>")
    def save_row(key: str):
        """Save one row without replacing other rows' unsaved forms.

        Arguments:
            key: content identity of the row
        Returns:
            updated row and out-of-band counts, or an ordinary redirect
        """
        try:
            filters = _parse_filters(flask.request.args)
            through_value = flask.request.form.get("through") or flask.request.args.get(
                "through"
            )
            through = None
            if through_value is not None:
                through = max(0, int(through_value))
            before = audit.page(filters, through=through)
            affected = audit.save(
                key,
                reviewed=flask.request.form.get("reviewed", ""),
                review_note=flask.request.form.get("review_note", ""),
                notes=flask.request.form.get("notes", ""),
                finding=flask.request.form.get("finding", "unaudited"),
                verified=flask.request.form.get("verified") == "on",
                version=int(flask.request.form["version"]),
            )
            view = _get_view_context(audit, filters, through=through)
        except KeyError:
            flask.abort(404)
        except (ValueError, ScinoephileError) as exc:
            if flask.request.headers.get("HX-Request") == "true":
                return (
                    flask.render_template("_message.html", message=str(exc)),
                    409,
                    {"HX-Retarget": "#messages", "HX-Reswap": "innerHTML"},
                )
            return flask.render_template("error.html", message=str(exc)), 409
        page = audit.page(filters, through=through)
        destination_values = dict(asdict(page.filters), through=page.last_block)
        destination = f"/?{urlencode(destination_values)}#row-{key}"
        if flask.request.headers.get("HX-Request") != "true":
            return flask.redirect(destination, code=303)
        current = next(row for row in audit.rows() if row.key == key)
        visible_row = None
        if filters.matches(current):
            visible_row = current
        old_keys = {row.key for row in before.rows}
        old_blocks = {block.number for block in before.blocks}
        additions = {
            block.number: [row for row in block.rows if row.key not in old_keys]
            for block in page.blocks
            if block.number in old_blocks
        }
        visible = {row.key: row for row in page.rows}
        others = {
            changed_key: visible.get(changed_key)
            for changed_key in affected
            if changed_key != key and changed_key in old_keys
        }
        return flask.render_template(
            "_saved.html",
            row=visible_row,
            current=current,
            autosave=flask.request.headers.get("HX-Target") == f"sync-{key}",
            additions=additions,
            others=others,
            old_blocks=old_blocks,
            removed_blocks=old_blocks - {block.number for block in page.blocks},
            **view,
        )

    @app.get("/export")
    def export():
        """Download the independent audit decisions as portable JSON.

        Returns:
            UTF-8 audit progress download
        """
        response = flask.jsonify(
            {"title": audit.title, "rows": [asdict(row) for row in audit.rows()]}
        )
        response.headers["Content-Disposition"] = (
            'attachment; filename="audit-progress.json"'
        )
        return response

    return app


def serve_audit(audit: AuditSession, *, host: str = "127.0.0.1", port: int = 5020):
    """Serve the local audit app using the existing optional web stack.

    Arguments:
        audit: loaded audit project
        host: loopback host address
        port: local TCP port
    """
    serving = import_werkzeug_serving()
    server = serving.make_server(host, port, create_app(audit), threaded=True)
    logger.info(f"Subtitle audit: http://{host}:{port}/")
    try:
        server.serve_forever()
    finally:
        server.server_close()


def _confirm_rerun(operation: str, *, rerun: bool) -> bool:
    """Require two preparation clicks and a delayed third click for a rerun.

    Arguments:
        operation: worker whose settings and confirmation must match
        rerun: whether existing persisted output will be replaced
    Returns:
        whether this submission authorizes starting the worker
    Raises:
        ValueError: if the submitted provider or reasoning is unsupported
    """
    flask = import_flask()
    if not rerun:
        return True
    settings = {
        name: flask.request.form.get(name, "")
        for name in ("provider", "model", "effort")
    }
    if settings["effort"]:
        ReasoningEffort(settings["effort"])
    if settings["provider"] not in get_provider_names():
        raise ValueError("Choose a supported provider")
    pending = dict(flask.session.get("rerun_confirmations", {}))
    current = pending.get(operation, {})
    supplied = flask.request.form.get("confirmation", "")
    matches = (
        supplied.isascii()
        and compare_digest(supplied, current.get("token", ""))
        and current.get("settings") == settings
        and time() < current.get("expires_at", 0)
    )
    if matches and current.get("stage") == 2:
        if time() < current["ready_at"]:
            return False
        pending.pop(operation, None)
        flask.session["rerun_confirmations"] = pending
        return True
    stage = 1
    if matches and current.get("stage") == 1:
        stage = 2
    pending[operation] = {
        "stage": stage,
        "token": token_urlsafe(24),
        "settings": settings,
        "ready_at": time() + 3,
        "expires_at": time() + 600,
    }
    flask.session["rerun_confirmations"] = pending
    return False


def _get_view_context(
    audit: AuditSession, filters: AuditFilters, *, through: int | None = None
) -> dict[str, object]:
    """Build a bounded view, stable next cursor, and native save context.

    Arguments:
        audit: active editable review session
        filters: requested filter state
        through: inclusive browser-loaded cursor during a save
    Returns:
        template context
    """
    flask = import_flask()
    if through is None and flask.request.args.get("through"):
        through = max(0, int(flask.request.args["through"]))
    after = max(0, int(flask.request.args.get("after", "0")))
    page = audit.page(filters, after=after, through=through)
    values = asdict(page.filters)
    return {
        "verification_token": audit.verification_token(filters),
        "audit": audit,
        "page": page,
        "filters": page.filters,
        "query": urlencode(dict(values, through=page.last_block)),
        "next_url": f"/?{urlencode(dict(values, after=page.last_block))}",
        "csrf": flask.session.setdefault("csrf", token_urlsafe(32)),
    }


def _parse_filters(values: Mapping[str, str]) -> AuditFilters:
    """Parse URL query filters shared by ordinary and HTMX requests.

    Arguments:
        values: query parameters
    Returns:
        requested filters
    """
    return AuditFilters(
        verification=values.get("verification", "all"),
        changes=values.get("changes", "all"),
        finding=values.get("finding", "all"),
        q=values.get("q", ""),
    )


def _protect_local_forms():
    """Reject untrusted Host, cross-origin writes, and stale CSRF tokens."""
    flask = import_flask()
    host = urlsplit(flask.request.host_url).hostname
    if host not in {"127.0.0.1", "localhost", "::1"}:
        flask.abort(403)
    if flask.request.method == "POST":
        origin = flask.request.headers.get("Origin")
        if origin and origin.rstrip("/") != flask.request.host_url.rstrip("/"):
            flask.abort(403)
        expected = flask.session.get("csrf", "")
        received = flask.request.form.get("csrf", "")
        if not expected or not compare_digest(expected, received):
            flask.abort(403)


def _register_auditing_routes(app: FlaskApp, audit: AuditSession):
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
            "reauditing": state.has_output,
            "show_auditing": visibility == "1"
            or (visibility is None and state.status in {"running", "error"}),
        }

    @app.post("/auditing")
    def start_auditing():
        """Reserve review state and show progress with editing temporarily disabled.

        Returns:
            current page reload or inline configuration error
        """
        rerun = auditing.snapshot().has_output
        try:
            if not _confirm_rerun("auditing", rerun=rerun):
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
                        **_get_view_context(audit, AuditFilters()),
                        auditing=state,
                        reauditing=True,
                        show_auditing=True,
                    )
                return flask.render_template(
                    "_auditing.html",
                    auditing=state,
                    reauditing=True,
                    show_auditing=True,
                    csrf=flask.session["csrf"],
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
                    "_auditing.html",
                    auditing=auditing.snapshot(),
                    auditing_message=str(exc),
                    reauditing=rerun,
                    show_auditing=True,
                    csrf=flask.session["csrf"],
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
        return flask.render_template("_auditing.html", auditing=state)


def _register_operation_routes(app: FlaskApp, audit: AuditSession):
    """Register proofreading and audit setup cards with their background workers.

    Arguments:
        app: local audit application
        audit: source-backed session owning output creation
    """
    _register_auditing_routes(app, audit)
    _register_verification_routes(app, audit)
    _register_preview_routes(app, audit)
    flask = import_flask()
    app.before_request(_protect_local_forms)
    proofreading = ProofreadingJob(audit)
    app.extensions["audit_proofreading"] = proofreading

    @app.context_processor
    def proofreading_context() -> dict[str, object]:
        """Provide shared provider choices and the current background job state.

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
            "provider_names": get_provider_names(),
            "reasoning_levels": tuple(ReasoningEffort),
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
            if not _confirm_rerun("proofreading", rerun=rerun):
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
                        **_get_view_context(audit, AuditFilters()),
                        proofreading=state,
                        reproofreading=True,
                        show_proofreading=True,
                    )
                return flask.render_template(
                    "_proofreading.html",
                    proofreading=state,
                    reproofreading=True,
                    show_proofreading=True,
                    csrf=flask.session["csrf"],
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
                "_proofreading.html",
                csrf=flask.session["csrf"],
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
        return flask.render_template(
            "_proofreading.html",
            csrf=flask.session.setdefault("csrf", token_urlsafe(32)),
            proofreading=state,
        )


def _register_preview_routes(app: FlaskApp, audit: AuditSession):
    """Render unsaved text differences independently of note validation.

    Arguments:
        app: local audit application
        audit: source-backed review session
    """
    flask = import_flask()

    @app.post("/rows/<key>/preview")
    def preview_row(key: str):
        """Preview one draft without changing subtitles, decisions or progress.

        Arguments:
            key: content identity of the row
        Returns:
            escaped original and draft differences, or an input error
        """
        row = next((row for row in audit.rows() if row.key == key), None)
        if row is None:
            return flask.abort(404)
        reviewed = flask.request.form.get("reviewed", "").replace("\r\n", "\n")
        if len(reviewed) > 1000:
            flask.abort(400)
        return flask.render_template(
            "_preview.html", row=replace(row, reviewed=reviewed)
        )


def _register_verification_routes(app: FlaskApp, audit: AuditSession):
    """Register filtered bulk verification with the ordinary form fallback.

    Arguments:
        app: local audit application
        audit: source-backed review session
    """
    flask = import_flask()

    @app.post("/verify-visible")
    def verify_visible():
        """Prepare bulk verification, then apply it on the confirmation click.

        Returns:
            confirmation control, updated workspace, ordinary redirect, or error
        Raises:
            ValueError: if selection is stale; rendered as a conflict response
        """
        try:
            filters = _parse_filters(flask.request.args)
            selection = flask.request.form.get("selection", "")
            if selection != audit.verification_token(filters):
                raise ValueError(
                    "The matching subtitles changed. Reload before verifying."
                )
            if flask.request.form.get("confirm") != "on":
                template = "index.html"
                if flask.request.headers.get("HX-Request") == "true":
                    template = "_verification.html"
                return flask.render_template(
                    template,
                    **_get_view_context(audit, filters),
                    verification_pending=True,
                )
            audit.verify_visible(filters, selection)
        except (ValueError, ScinoephileError) as exc:
            if flask.request.headers.get("HX-Request") == "true":
                return (
                    flask.render_template("_message.html", message=str(exc)),
                    409,
                    {"HX-Retarget": "#messages", "HX-Reswap": "innerHTML"},
                )
            return flask.render_template("error.html", message=str(exc)), 409
        if flask.request.headers.get("HX-Request") == "true":
            return (
                flask.render_template(
                    "_workspace.html", **_get_view_context(audit, filters)
                ),
                200,
                {"HX-Retarget": "#workspace", "HX-Reswap": "outerHTML"},
            )
        return flask.redirect(f"/?{urlencode(asdict(filters))}", code=303)
