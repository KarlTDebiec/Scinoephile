#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared request and response protection for local authoring applications."""

from __future__ import annotations

from pathlib import Path
from secrets import compare_digest, token_urlsafe
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

from scinoephile.core.dependencies.web import import_flask

if TYPE_CHECKING:
    from scinoephile.core.dependencies.web import FlaskApp, FlaskResponse

__all__ = ["create_local_app"]


def create_local_app(
    name: str, static_dir_path: Path, *, host: str = "127.0.0.1"
) -> FlaskApp:
    """Create a local app with trusted hosts and protected editing requests.

    Loopback names and the explicit bind host are trusted. Wildcard binds retain
    loopback access without trusting arbitrary Host headers. Native forms and
    their HTMX enhancements use the same session CSRF token.

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
    trusted_hosts = {"127.0.0.1", "localhost", "::1"}
    if host not in {"", "0.0.0.0", "::"}:
        trusted_host = host.removeprefix("[").removesuffix("]")
        trusted_hosts.add(trusted_host.encode("idna").decode("ascii").lower())
    app = flask.Flask(name, static_folder=str(static_dir_path))
    app.register_blueprint(
        flask.Blueprint("web_templates", __name__, template_folder="templates")
    )
    app.config.update(SECRET_KEY=token_urlsafe(32), SESSION_COOKIE_SAMESITE="Strict")

    @app.context_processor
    def csrf_context() -> dict[str, str]:
        """Supply the session token to templates that render editing forms.

        Returns:
            template context containing the CSRF token
        """
        if "csrf" not in flask.session:
            flask.session["csrf"] = token_urlsafe(32)
        return {"csrf": flask.session["csrf"]}

    @app.before_request
    def protect_local_requests():
        """Check the request host, origin, and credentials for edits."""
        request = flask.request
        # Match complete hostnames without treating IPv6 colons as port separators
        try:
            request_host = urlsplit(f"//{request.host}")
            if (
                request_host.hostname not in trusted_hosts
                or request_host.port == 0
                or request_host.username is not None
            ):
                flask.abort(400)
        except ValueError:
            flask.abort(400)
        origin = request.headers.get("Origin")
        if origin and origin != request.host_url.rstrip("/"):
            flask.abort(403)
        if request.headers.get("Sec-Fetch-Site") in {"cross-site", "same-site"}:
            flask.abort(403)
        if request.method in {"GET", "HEAD", "OPTIONS"}:
            return
        expected = flask.session.get("csrf", "")
        received = request.form.get("csrf", "")
        if (
            not expected
            or not received.isascii()
            or not compare_digest(expected, received)
        ):
            flask.abort(403)

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
