#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared request and response protection for local authoring applications."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

from scinoephile.core.dependencies.web import import_flask

if TYPE_CHECKING:
    from scinoephile.core.dependencies.web import FlaskApp, FlaskResponse

__all__ = ["create_local_app"]


def create_local_app(
    name: str,
    static_dir_path: Path,
    *,
    host: str = "127.0.0.1",
    require_htmx: bool = True,
) -> FlaskApp:
    """Create a local app with trusted hosts and protected editing requests.

    Loopback names and the explicit bind host are trusted. Wildcard binds retain
    loopback access without trusting arbitrary Host headers. Requiring HTMX's custom
    header prevents foreign forms from editing data while CORS remains disabled.
    Apps that accept native forms must check a session CSRF token on mutations.

    Arguments:
        name: Flask application import name used to locate domain templates
        static_dir_path: existing shared browser asset directory
        host: explicitly configured bind host, or a wildcard bind address
        require_htmx: whether all editing requests must carry the HTMX header
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

    @app.before_request
    def protect_local_requests():
        """Reject foreign browser requests and enforce the editing request policy."""
        request = flask.request
        # Match complete hostnames without treating IPv6 colons as port separators
        try:
            request_host = urlsplit(f"//{request.host}").hostname
        except ValueError:
            flask.abort(400)
        if request_host not in trusted_hosts:
            flask.abort(400)
        origin = request.headers.get("Origin")
        if origin and origin != request.host_url.rstrip("/"):
            flask.abort(403)
        if request.headers.get("Sec-Fetch-Site") in {"cross-site", "same-site"}:
            flask.abort(403)
        if (
            require_htmx
            and request.method not in {"GET", "HEAD", "OPTIONS"}
            and request.headers.get("HX-Request") != "true"
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
