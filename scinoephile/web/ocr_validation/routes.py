#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Flask routes for the OCR validation editor."""

from __future__ import annotations

from bisect import bisect_left
from io import BytesIO
from threading import Thread
from typing import TYPE_CHECKING

from scinoephile.core.dependencies.web import import_flask

from .concerns import CharDimsConcern, ErrorConcern, GapConcern, SubtitleRowView
from .session import OcrValidationSession

__all__ = ["register_routes"]

if TYPE_CHECKING:
    from scinoephile.core.dependencies.web import FlaskApp, FlaskResponse

flask = import_flask()
request = flask.request
_PAGE_SIZE = 8
_FILTERS = {
    "needs-review": "Needs review",
    "all": "All subtitles",
    "character": "Character boxes",
    "spacing": "Spacing",
    "blocked": "Blocked",
    "done": "Validated",
}


def register_routes(app: FlaskApp, session: OcrValidationSession):
    """Register the OCR editor and its subtitle actions.

    Arguments:
        app: Flask application
        session: validation state for this subtitle track
    """
    app.register_error_handler(IndexError, _handle_index_error)
    app.register_error_handler(ValueError, _handle_value_error)

    @app.get("/")
    def index() -> str:
        """Render a filtered page of subtitles.

        Returns:
            complete document or workspace fragment
        """
        session.refresh_concerns()
        status, query, after = _filters()
        matches, validated = _matching_subtitles(session, status, query)
        start = bisect_left(matches, after)
        visible = matches[start : start + _PAGE_SIZE]
        previous_after = None
        if start > 0:
            previous_after = 0
            if start > _PAGE_SIZE:
                previous_after = matches[start - _PAGE_SIZE - 1] + 1
        next_after = None
        if start + _PAGE_SIZE < len(matches):
            next_after = visible[-1] + 1

        template = "index.html"
        if _is_htmx():
            template = "_workspace.html"
        return flask.render_template(
            template,
            after=after,
            filters=_FILTERS,
            matched=len(matches),
            next_after=next_after,
            previous_after=previous_after,
            query=query,
            rows=[session.subtitle_row(sub_idx) for sub_idx in visible],
            status=status,
            total=len(session.entries),
            validated=validated,
        )

    @app.get("/subtitles/<int:sub_idx>/image.png")
    def source_image(sub_idx: int) -> FlaskResponse:
        """Serve the source subtitle pixels used by the box overlay.

        Arguments:
            sub_idx: zero-based subtitle index
        Returns:
            original subtitle image as PNG
        """
        image = session.source_image(sub_idx)
        output = BytesIO()
        image.save(output, format="PNG")
        return flask.Response(output.getvalue(), mimetype="image/png")

    @app.post("/subtitles/<int:sub_idx>/text", defaults={"operation": "text"})
    @app.post("/subtitles/<int:sub_idx>/concern/char", defaults={"operation": "char"})
    @app.post("/subtitles/<int:sub_idx>/concern/gap", defaults={"operation": "gap"})
    def update_subtitle(
        sub_idx: int, operation: str
    ) -> str | FlaskResponse | tuple[str, int] | tuple[str, int, dict[str, str]]:
        """Save text or apply an action to the concern shown in the submitted row.

        Arguments:
            sub_idx: zero-based subtitle index
            operation: text, character, or spacing action selected by the route
        Raises:
            ValueError: if a character action has no active character concern
        Returns:
            updated fragments or a redirect to the current view
        """
        current = session.subtitle_row(sub_idx)
        if request.form.get("version") != current.version:
            message = "This subtitle changed. Reload it before submitting again."
            if _is_htmx():
                return (
                    message,
                    409,
                    {"HX-Retarget": "#messages", "HX-Reswap": "innerHTML"},
                )
            return message, 409

        if operation == "text":
            text = request.form["text"].replace("\r\n", "\n").replace("\r", "\n")
            row = session.update_text(sub_idx, text.replace("\n", "\\N"))
        elif operation == "char":
            if not isinstance(current.concern, CharDimsConcern):
                raise ValueError("This subtitle has no character box concern.")
            row = session.resolve_char_concern(
                sub_idx,
                action=request.form["action"],
                n_bboxes=current.concern.n_bboxes,
            )
        else:
            row = session.resolve_gap_concern(sub_idx, action=request.form["action"])

        return _render_update(session, row)

    @app.post("/exit")
    def exit_validation() -> str:
        """Save the subtitle output and stop the web server.

        Returns:
            exit confirmation
        """
        session.finish()
        server = app.config.get("OCR_VALIDATION_SERVER")
        if server is not None:
            if app.testing:
                server.shutdown()
            else:
                Thread(target=server.shutdown, daemon=True).start()
        return "Validation exited. You can close this tab."


def _filters() -> tuple[str, str, int]:
    """Read the status filter, text search, and pagination cursor.

    Returns:
        selected status, trimmed search text, and first candidate subtitle index
    """
    default = "needs-review"
    status = request.args.get("status", default)
    if status not in _FILTERS:
        status = default
    return (
        status,
        request.args.get("q", "").strip(),
        max(0, request.args.get("after", 0, type=int)),
    )


def _handle_index_error(exc: IndexError) -> tuple[str, int]:
    """Return a 404 for an out-of-range subtitle.

    Arguments:
        exc: index error
    Returns:
        error message and HTTP status
    """
    return str(exc), 404


def _handle_value_error(exc: ValueError) -> tuple[str, int]:
    """Return a 400 for an invalid subtitle action.

    Arguments:
        exc: validation error
    Returns:
        error message and HTTP status
    """
    return str(exc), 400


def _is_htmx() -> bool:
    """Check whether the request expects a fragment.

    Returns:
        whether HTMX requested a partial update
    """
    return (
        request.headers.get("HX-Request") == "true"
        and request.headers.get("HX-History-Restore-Request") != "true"
    )


def _matching_subtitles(
    session: OcrValidationSession, status: str, query: str
) -> tuple[list[int], int]:
    """Find matching subtitles and count validated rows without building row views.

    Arguments:
        session: current validation state
        status: requested concern filter
        query: search text or subtitle number
    Returns:
        matching subtitle indices and total validated count
    """
    matches = []
    validated = 0
    query = query.casefold()
    for sub_idx, concern in enumerate(session.subtitle_concerns()):
        kind = "done"
        if isinstance(concern, CharDimsConcern):
            kind = "character"
        elif isinstance(concern, GapConcern):
            kind = "spacing"
        elif isinstance(concern, ErrorConcern):
            kind = "blocked"
        else:
            validated += 1
        if status not in {"all", kind}:
            if status != "needs-review" or kind == "done":
                continue
        entry = session.entries[sub_idx]
        if query in entry.text.casefold() or query == str(entry.index):
            matches.append(sub_idx)
    return matches, validated


def _render_update(
    session: OcrValidationSession, row: SubtitleRowView
) -> str | FlaskResponse:
    """Update only the affected row and counts, or redirect a native submission.

    Arguments:
        session: current validation state
        row: updated subtitle
    Returns:
        fragments or a redirect back to the current page
    """
    status, query, after = _filters()
    matches, validated = _matching_subtitles(session, status, query)
    visible = row.sub_idx in matches
    if not _is_htmx():
        anchor = None
        if visible:
            anchor = f"sub-{row.number}"
        return flask.redirect(
            flask.url_for("index", status=status, q=query, after=after, _anchor=anchor),
            code=303,
        )
    return flask.render_template(
        "_updated.html",
        row=row,
        after=after,
        query=query,
        status=status,
        visible=visible,
        matched=len(matches),
        total=len(session.entries),
        validated=validated,
    )
