#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
# ruff: noqa: PLC0415
"""Lazy access to optional web dependencies."""

from __future__ import annotations

from types import ModuleType
from typing import TYPE_CHECKING

__all__ = [
    "import_flask",
    "import_werkzeug_serving",
]

if TYPE_CHECKING:
    from flask import Flask, Response

    type FlaskApp = Flask
    type FlaskResponse = Response

_WEB_EXTRA_MESSAGE = (
    "Web support requires optional web dependencies. "
    "Install scinoephile with the 'web' extra."
)


def import_flask() -> ModuleType:
    """Import Flask on demand.

    Returns:
        Flask module
    """
    try:
        import flask
    except ImportError as exc:
        raise ImportError(_WEB_EXTRA_MESSAGE) from exc
    return flask


def import_werkzeug_serving() -> ModuleType:
    """Import Werkzeug serving utilities on demand.

    Returns:
        Werkzeug serving module
    """
    try:
        import werkzeug.serving as werkzeug_serving
    except ImportError as exc:
        raise ImportError(_WEB_EXTRA_MESSAGE) from exc
    return werkzeug_serving
