#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Flask app for OCR validation."""

from __future__ import annotations

from flask import Flask

from .routes import register_routes
from .session import OcrValidationSession

__all__ = ["create_app"]


def create_app(session: OcrValidationSession) -> Flask:
    """Create the OCR validation Flask app.

    Arguments:
        session: OCR validation session
    Returns:
        Flask app
    """
    app = Flask(__name__)
    app.config["OCR_VALIDATION_SESSION"] = session
    register_routes(app)
    return app
