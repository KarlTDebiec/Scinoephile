#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Page, editing, and verification routes for the subtitle audit editor."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, replace
from typing import TYPE_CHECKING
from urllib.parse import urlencode

from scinoephile.core import ScinoephileError
from scinoephile.core.dependencies.web import import_flask
from scinoephile.workflows.review_audit.filters import AuditFilters
from scinoephile.workflows.review_audit.project import ReviewAuditProject

from .workspace import get_audit_page, get_view_context

if TYPE_CHECKING:
    from scinoephile.core.dependencies.web import FlaskApp

__all__ = ["register_editor_routes"]


def register_editor_routes(app: FlaskApp, audit: ReviewAuditProject, *, title: str):
    """Register routes for browsing, editing, verifying, and exporting audit rows.

    Arguments:
        app: local audit application
        audit: source-backed audit project
        title: editor title to include in exported progress
    """
    flask = import_flask()
    _register_verification_routes(app, audit)
    _register_preview_routes(app, audit)

    @app.get("/")
    def index():
        """Render full pages or HTMX fragments from the same GET route.

        Returns:
            rendered audit page
        """
        try:
            view = get_view_context(audit, _parse_filters(flask.request.args))
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
        Raises:
            ValueError: if the saved row changed again, rendered as a conflict response
        """
        is_htmx = flask.request.headers.get("HX-Request") == "true"
        try:
            filters = _parse_filters(flask.request.args)
            through_value = flask.request.form.get("through") or flask.request.args.get(
                "through"
            )
            through = None
            if through_value is not None:
                through = max(0, int(through_value))
            before = get_audit_page(audit.rows(), filters, through=through)
            version = int(flask.request.form["version"])
            affected = audit.save(
                key,
                reviewed=flask.request.form.get("reviewed", ""),
                review_note=flask.request.form.get("review_note", ""),
                notes=flask.request.form.get("notes", ""),
                finding=flask.request.form.get("finding", "unaudited"),
                verified=flask.request.form.get("verified") == "on",
                version=version,
            )
            page = get_audit_page(audit.rows(), filters, through=through)
            current = next((row for row in page.all_rows if row.key == key), None)
            if current is None or current.version != version + 1:
                raise ValueError("This subtitle changed. Reload before editing.")
        except KeyError:
            flask.abort(404)
        except (ValueError, ScinoephileError) as exc:
            if is_htmx:
                return (
                    flask.render_template("_message.html", message=str(exc)),
                    409,
                    {"HX-Retarget": "#messages", "HX-Reswap": "innerHTML"},
                )
            return flask.render_template("error.html", message=str(exc)), 409
        if not is_htmx:
            destination_values = dict(asdict(page.filters), through=page.last_block)
            destination = f"/?{urlencode(destination_values)}#row-{key}"
            return flask.redirect(destination, code=303)
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
            row=visible.get(key),
            current=current,
            autosave=flask.request.headers.get("HX-Target") == f"sync-{key}",
            additions=additions,
            others=others,
            old_blocks=old_blocks,
            removed_blocks=old_blocks - {block.number for block in page.blocks},
            **get_view_context(audit, filters, page=page),
        )

    @app.get("/export")
    def export():
        """Download the independent audit decisions as portable JSON.

        Returns:
            UTF-8 audit progress download
        """
        body = app.json.dumps(
            {"title": title, "rows": [asdict(row) for row in audit.rows()]},
            ensure_ascii=False,
        )
        response = flask.Response(body, mimetype="application/json")
        response.headers["Content-Disposition"] = (
            'attachment; filename="audit-progress.json"'
        )
        return response


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


def _register_preview_routes(app: FlaskApp, audit: ReviewAuditProject):
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


def _register_verification_routes(app: FlaskApp, audit: ReviewAuditProject):
    """Register filtered bulk verification with the ordinary form fallback.

    Arguments:
        app: local audit application
        audit: source-backed review session
    """
    flask = import_flask()

    @app.post("/verify-matching-rows")
    def verify_matching_rows():
        """Prepare bulk verification, then apply it on the confirmation click.

        Returns:
            confirmation control, updated workspace, ordinary redirect, or error
        Raises:
            ValueError: if selection is stale; rendered as a conflict response
        """
        try:
            filters = _parse_filters(flask.request.args)
            selection = flask.request.form.get("selection", "")
            if flask.request.form.get("confirm") != "on":
                view = get_view_context(audit, filters)
                if selection != view["verification_token"]:
                    raise ValueError(
                        "The matching subtitles changed. Reload before verifying."
                    )
                template = "index.html"
                if flask.request.headers.get("HX-Request") == "true":
                    template = "_verification.html"
                return flask.render_template(
                    template, **view, verification_pending=True
                )
            audit.verify_matching_rows(filters, selection)
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
                    "_workspace.html", **get_view_context(audit, filters)
                ),
                200,
                {"HX-Retarget": "#workspace", "HX-Reswap": "outerHTML"},
            )
        return flask.redirect(f"/?{urlencode(asdict(filters))}", code=303)
