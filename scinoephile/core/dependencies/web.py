#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
# ruff: noqa: PLC0415
"""Lazy access to optional web dependencies."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, NoReturn

__all__ = [
    "import_flask_abort",
    "import_flask_current_app",
    "import_flask_flask",
    "import_flask_render_template",
    "import_flask_request",
    "import_flask_response",
    "import_werkzeug_serving_make_server",
]

if TYPE_CHECKING:
    from flask import Flask, Request, Response
    from werkzeug.serving import BaseWSGIServer

    type FlaskApp = Flask
    type FlaskResponse = Response

_WEB_EXTRA_MESSAGE = (
    "Web support requires optional web dependencies. "
    "Install scinoephile with the 'web' extra."
)


def import_flask_abort() -> Callable[..., NoReturn]:
    """Import the Flask request-abort function on demand.

    Returns:
        Flask request-abort function
    """
    try:
        from flask import abort
    except ImportError as exc:
        raise ImportError(_WEB_EXTRA_MESSAGE) from exc
    return abort


def import_flask_current_app() -> Flask:
    """Import the Flask current-app proxy on demand.

    Returns:
        Flask current-app proxy
    """
    try:
        from flask import current_app
    except ImportError as exc:
        raise ImportError(_WEB_EXTRA_MESSAGE) from exc
    return current_app


def import_flask_flask() -> type[Flask]:
    """Import the Flask app class on demand.

    Returns:
        Flask app class
    """
    try:
        from flask import Flask
    except ImportError as exc:
        raise ImportError(_WEB_EXTRA_MESSAGE) from exc
    return Flask


def import_flask_render_template() -> Callable[..., str]:
    """Import the Flask template-rendering function on demand.

    Returns:
        Flask template-rendering function
    """
    try:
        from flask import render_template
    except ImportError as exc:
        raise ImportError(_WEB_EXTRA_MESSAGE) from exc
    return render_template


def import_flask_request() -> Request:
    """Import the Flask request proxy on demand.

    Returns:
        Flask request proxy
    """
    try:
        from flask import request
    except ImportError as exc:
        raise ImportError(_WEB_EXTRA_MESSAGE) from exc
    return request


def import_flask_response() -> type[Response]:
    """Import the Flask response class on demand.

    Returns:
        Flask response class
    """
    try:
        from flask import Response
    except ImportError as exc:
        raise ImportError(_WEB_EXTRA_MESSAGE) from exc
    return Response


def import_werkzeug_serving_make_server() -> Callable[..., BaseWSGIServer]:
    """Import the Werkzeug server factory on demand.

    Returns:
        Werkzeug server factory
    """
    try:
        from werkzeug.serving import make_server
    except ImportError as exc:
        raise ImportError(_WEB_EXTRA_MESSAGE) from exc
    return make_server
