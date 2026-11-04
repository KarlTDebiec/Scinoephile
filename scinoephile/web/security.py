#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared request and response protection for local authoring applications."""

from __future__ import annotations

from pathlib import Path
from secrets import compare_digest, token_hex
from typing import TYPE_CHECKING

from scinoephile.core.dependencies.web import import_flask

if TYPE_CHECKING:
    from scinoephile.core.dependencies.web import FlaskApp, FlaskResponse

__all__ = ["create_local_app"]


def create_local_app(
    name: str, static_dir_path: Path, *, host: str = "127.0.0.1"
) -> FlaskApp:
    """Create an authoring app with trusted hosts and session-bound mutation tokens.

    Loopback names and the explicit bind host are trusted. Wildcard binds retain
    loopback access without trusting arbitrary Host headers. Templates retain Flask's
    default location beneath the caller's application package.
    Each server uses a separate cookie name because browser cookies ignore ports.

    Arguments:
        name: Flask application import name used to locate domain templates
        static_dir_path: existing shared browser asset directory
        host: explicitly configured bind host, or a wildcard bind address
    Returns:
        Flask app with local request checks and defensive response headers
    Raises:
        DependencyError: if optional web dependencies are unavailable
    """
    flask = import_flask()
    trusted_hosts = ["127.0.0.1", "localhost", "[::1]"]
    if host not in {"", "0.0.0.0", "::"}:
        trusted_host = host
        if ":" in host and not host.startswith("["):
            trusted_host = f"[{host}]"
        trusted_hosts.append(trusted_host)
    app = flask.Flask(name, static_folder=str(static_dir_path))
    app.config.update(
        SECRET_KEY=token_hex(32),
        MAX_CONTENT_LENGTH=65536,
        TRUSTED_HOSTS=trusted_hosts,
        SESSION_COOKIE_NAME=f"scinoephile_{token_hex(8)}",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
    )

    @app.before_request
    def protect_local_requests():
        """Reject foreign mutation origins and require the session's CSRF token."""
        request = flask.request
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            origin = request.headers.get("Origin")
            if origin and origin != request.host_url.rstrip("/"):
                flask.abort(403)
            if request.headers.get("Sec-Fetch-Site") == "cross-site":
                flask.abort(403)
            expected = flask.session.get("csrf_token", "")
            supplied = request.headers.get("X-CSRF-Token") or request.form.get(
                "csrf_token", ""
            )
            if not expected or not compare_digest(
                expected.encode("utf-8"), supplied.encode("utf-8")
            ):
                flask.abort(403)
        flask.session.setdefault("csrf_token", token_hex(32))

    @app.after_request
    def protect_response(response: FlaskResponse) -> FlaskResponse:
        """Disable caching, framing, MIME sniffing, and unbundled executable content.

        Arguments:
            response: pending Flask response
        Returns:
            response with shared protection headers
        """
        response.headers.update(
            {
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
                "Referrer-Policy": "same-origin",
                "Content-Security-Policy": "default-src 'self'; script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; media-src 'self'; "
                "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
                "base-uri 'self'; frame-ancestors 'none'; form-action 'self'",
            }
        )
        return response

    return app
