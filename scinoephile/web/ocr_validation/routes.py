#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Flask routes for OCR validation."""

from __future__ import annotations

from io import BytesIO
from threading import Thread

from flask import (
    Flask,
    Response,
    abort,
    current_app,
    render_template,
    request,
)
from PIL import Image

from .concerns import SubtitleRowView
from .session import OcrValidationSession

__all__ = ["register_routes"]


def register_routes(app: Flask):
    """Register OCR validation routes with a Flask app.

    Arguments:
        app: Flask app
    """
    _register_error_handlers(app)
    _register_exit_route(app)
    _register_filter_routes(app)

    @app.get("/")
    def index() -> str:
        """Render the subtitle list."""
        session = _session()
        session.reset_states()
        return _render_index(session)

    @app.get("/subtitles/<int:sub_idx>")
    def subtitle(sub_idx: int) -> str:
        """Render one subtitle row.

        Arguments:
            sub_idx: zero-based subtitle index
        Returns:
            rendered subtitle row
        """
        session = _session()
        row = session.subtitle_row(sub_idx)
        return _render_subtitle_row(session, row)

    @app.get("/subtitles/<int:sub_idx>/concern.png")
    def concern_image(sub_idx: int) -> Response:
        """Render one current concern image.

        Arguments:
            sub_idx: zero-based subtitle index
        Returns:
            PNG response
        """
        session = _session()
        image = session.concern_image(sub_idx)
        return _png_response(image)

    @app.get("/subtitles/<int:sub_idx>/validation.png")
    def validation_image(sub_idx: int) -> Response:
        """Render one subtitle image with validation bboxes.

        Arguments:
            sub_idx: zero-based subtitle index
        Returns:
            PNG response
        """
        session = _session()
        image = session.validation_image(sub_idx)
        return _png_response(image)

    @app.post("/subtitles/<int:sub_idx>/text")
    def update_text(sub_idx: int) -> str:
        """Update one subtitle's OCR text.

        Arguments:
            sub_idx: zero-based subtitle index
        Returns:
            rendered updated subtitle row
        """
        session = _session()
        text = request.form.get(f"text-{sub_idx}")
        if text is None:
            text = request.form.get("text", "")
        row = session.update_text(sub_idx, text)
        return _render_subtitle_row(session, row)

    @app.post("/subtitles/<int:sub_idx>/concern/char")
    def resolve_char(sub_idx: int) -> str:
        """Resolve one character bbox concern.

        Arguments:
            sub_idx: zero-based subtitle index
        Returns:
            rendered updated subtitle row
        """
        session = _session()
        action = request.form.get("action")
        if action is None:
            abort(400, "Missing action.")
        try:
            n_bboxes = int(request.form["n_bboxes"])
        except KeyError:
            abort(400, "Missing n_bboxes.")
        except ValueError:
            abort(400, "Invalid integer for n_bboxes.")
        row = session.resolve_char_concern(
            sub_idx,
            action=action,
            n_bboxes=n_bboxes,
        )
        return _render_subtitle_row(session, row)

    @app.post("/subtitles/<int:sub_idx>/concern/gap")
    def resolve_gap(sub_idx: int) -> str:
        """Resolve one spacing concern.

        Arguments:
            sub_idx: zero-based subtitle index
        Returns:
            rendered updated subtitle row
        """
        session = _session()
        action = request.form.get("action")
        if action is None:
            abort(400, "Missing action.")
        row = session.resolve_gap_concern(sub_idx, action=action)
        return _render_subtitle_row(session, row)


def _handle_index_error(exc: IndexError) -> tuple[str, int]:
    """Handle out-of-range subtitle requests.

    Arguments:
        exc: index error
    Returns:
        error response body and status
    """
    return str(exc), 404


def _handle_value_error(exc: ValueError) -> tuple[str, int]:
    """Handle request-facing validation errors.

    Arguments:
        exc: validation error
    Returns:
        error response body and status
    """
    return str(exc), 400


def _png_response(image: Image.Image) -> Response:
    """Encode an image as a PNG Flask response.

    Arguments:
        image: image to encode
    Returns:
        PNG response
    """
    output = BytesIO()
    image.save(output, format="PNG")
    return Response(output.getvalue(), mimetype="image/png")


def _register_error_handlers(app: Flask):
    """Register request-facing validation error handlers.

    Arguments:
        app: Flask app
    """
    app.register_error_handler(IndexError, _handle_index_error)
    app.register_error_handler(ValueError, _handle_value_error)


def _register_exit_route(app: Flask):
    """Register the route that finishes validation and stops the web server.

    Arguments:
        app: Flask app
    """

    @app.post("/exit")
    def exit_validation() -> str:
        """Finish validation and stop the local web server.

        Returns:
            exit confirmation
        """
        session = _session()
        session.finish()
        server = current_app.config.get("OCR_VALIDATION_SERVER")
        if server is not None:
            if current_app.testing:
                server.shutdown()
            else:
                Thread(target=server.shutdown, daemon=True).start()
        return "Validation exited. You can close this tab."


def _register_filter_routes(app: Flask):
    """Register filter update routes.

    Arguments:
        app: Flask app
    """

    @app.post("/filters/done")
    def update_done_filter() -> str:
        """Update whether completed subtitles are shown.

        Returns:
            rendered subtitle list
        """
        session = _session()
        include_done_subtitles = request.form.get("include_done_subtitles") == "1"
        session.include_done_subtitles = include_done_subtitles
        session.reset_states()
        if request.headers.get("HX-Request") == "true":
            return _render_index_body(session)
        return _render_index(session)


def _render_subtitle_row(session: OcrValidationSession, row: SubtitleRowView) -> str:
    """Render one subtitle row if it is visible.

    Arguments:
        session: OCR validation session
        row: subtitle row view model
    Returns:
        rendered subtitle row, or an empty response for hidden rows
    """
    if not session.subtitle_row_is_visible(row):
        return ""
    return render_template("_subtitle.html", row=row)


def _render_index(session: OcrValidationSession) -> str:
    """Render the full subtitle list.

    Arguments:
        session: OCR validation session
    Returns:
        rendered subtitle list
    """
    rows = session.all_subtitle_rows()
    visible_rows = [row for row in rows if session.subtitle_row_is_visible(row)]
    return render_template(
        "index.html",
        index_body=_render_index_body(session, rows=visible_rows),
        style_rows=rows,
    )


def _render_index_body(
    session: OcrValidationSession,
    rows: list[SubtitleRowView] | None = None,
) -> str:
    """Render the body content of the subtitle list.

    Arguments:
        session: OCR validation session
        rows: optional row view models to render
    Returns:
        rendered subtitle list body
    """
    if rows is None:
        rows = session.subtitle_rows()
    return render_template(
        "_index_body.html",
        rows=rows,
        include_done_subtitles=session.include_done_subtitles,
    )


def _session() -> OcrValidationSession:
    """Get the OCR validation session from Flask app config.

    Returns:
        OCR validation session
    """
    session = current_app.config["OCR_VALIDATION_SESSION"]
    if not isinstance(session, OcrValidationSession):
        raise TypeError("OCR validation session is not configured.")
    return session
