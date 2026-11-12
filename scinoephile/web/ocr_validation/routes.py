#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Flask routes for the OCR validation editor."""

from __future__ import annotations

from hashlib import sha256
from io import BytesIO
from typing import TYPE_CHECKING

from scinoephile.core.dependencies.web import import_flask
from scinoephile.web.blocks import get_block_page

from .concerns import FILTER_OPTIONS, CharDimsConcern, SubtitleRowView
from .session import OcrValidationSession
from .workspace import get_filtered_blocks

__all__ = ["register_routes"]

if TYPE_CHECKING:
    from scinoephile.core.dependencies.web import FlaskApp, FlaskResponse

flask = import_flask()
request = flask.request
_FILTER_CHOICES = tuple((key, *option) for key, option in FILTER_OPTIONS.items())


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
        append = _is_htmx() and request.headers.get("HX-Target") == "load-more"
        if not append:
            session.refresh_concerns()
        status, query, after, through = _filters()
        matching, counts, validated = get_filtered_blocks(session, status, query)
        blocks, last_block, has_more = get_block_page(
            matching, after=after, through=through, append=append
        )
        template = "index.html"
        if append:
            template = "_batch.html"
        elif _is_htmx():
            template = "_workspace.html"
        return flask.render_template(
            template,
            blocks=blocks,
            counts=counts,
            filter_options=_FILTER_CHOICES,
            font_size_px=session.text_font_size_px,
            font_size_key=sha256(str(session.dir_path).encode()).hexdigest(),
            has_more=has_more,
            matched=counts[status],
            query=query,
            status=status,
            subtitle_row=session.subtitle_row,
            through=last_block,
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
        loaded_rows: dict[int, int] = {}
        if _is_htmx():
            status, query, _, through = _filters()
            matching, _, _ = get_filtered_blocks(session, status, query)
            loaded, _, _ = get_block_page(matching, through=through)
            loaded_rows = {
                index: block.number for block in loaded for index in block.rows
            }
        affected: set[int] = set()
        if operation != "text":
            affected = session.refresh_concerns()
        current = session.subtitle_row(sub_idx)
        if request.form.get("version") != current.version:
            if operation != "text":
                return _render_update(
                    session, current, loaded_rows, affected, stale=True
                )
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

        affected.update(session.refresh_concerns())
        if sub_idx in affected:
            row = session.subtitle_row(sub_idx)
        return _render_update(session, row, loaded_rows, affected)


def _filters() -> tuple[str, str, int, int | None]:
    """Read the status filter, search text, and loaded block cursors.

    Returns:
        selected status, trimmed query, and cursors for new and loaded blocks
    """
    default = "needs-review"
    status = request.args.get("status", default)
    if status != "all" and status not in FILTER_OPTIONS:
        status = default
    through = request.form.get("through", type=int)
    if through is None:
        through = request.args.get("through", type=int)
    if through is not None:
        through = max(0, through)
    return (
        status,
        request.args.get("q", "").strip(),
        max(0, request.args.get("after", 0, type=int)),
        through,
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


def _render_update(
    session: OcrValidationSession,
    row: SubtitleRowView,
    loaded_rows: dict[int, int],
    affected: set[int],
    *,
    stale: bool = False,
) -> str | FlaskResponse:
    """Update affected cards and counts, or redirect a native submission.

    Arguments:
        session: current validation state
        row: updated subtitle
        loaded_rows: subtitle indexes and block numbers in the submitted view
        affected: subtitle indexes rechecked after learning new rules
        stale: whether the submitted concern was superseded
    Returns:
        fragments or a redirect back to the current page
    """
    status, query, _, through = _filters()
    blocks, counts, validated = get_filtered_blocks(session, status, query)
    block = next(
        (
            candidate
            for candidate in blocks
            if candidate.first_index <= row.sub_idx + 1 <= candidate.last_index
        ),
        None,
    )
    visible = block is not None and row.sub_idx in block.rows
    if not _is_htmx():
        anchor = None
        if visible:
            anchor = f"sub-{row.number}"
        return flask.redirect(
            flask.url_for(
                "index", status=status, q=query, through=through, _anchor=anchor
            ),
            code=303,
        )
    matching_rows = {index for item in blocks for index in item.rows}
    related_indexes = sorted((affected & loaded_rows.keys()) - {row.sub_idx})
    affected_blocks = {loaded_rows[index] for index in related_indexes}
    if block is not None:
        affected_blocks.add(block.number)
    message = ""
    if stale and visible and row.concern is not None:
        message = "The concern changed. Review the updated subtitle."
    fragments = flask.render_template(
        "_updated.html",
        row=row,
        blocks=[item for item in blocks if item.number in affected_blocks],
        related_rows=[
            (session.subtitle_row(index), index in matching_rows)
            for index in related_indexes
        ],
        through=through,
        query=query,
        status=status,
        visible=visible,
        counts=counts,
        filter_options=_FILTER_CHOICES,
        matched=counts[status],
        total=len(session.entries),
        validated=validated,
        message=message,
    )
    if stale:
        return flask.make_response(fragments, 409)
    return fragments
