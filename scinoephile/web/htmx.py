#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""HTMX request handling shared by local editors."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from werkzeug.datastructures import Headers

__all__ = ["get_editor_page_template", "is_htmx_request"]


def get_editor_page_template(headers: Headers) -> tuple[str, bool]:
    """Select the document, workspace, or next batch for an editor GET.

    Arguments:
        headers: incoming request headers
    Returns:
        template name and whether the response appends a new batch
    """
    if not is_htmx_request(headers):
        return "index.html", False
    if headers.get("HX-Target") == "load-more":
        return "_batch.html", True
    return "_workspace.html", False


def is_htmx_request(headers: Headers) -> bool:
    """Check whether HTMX is requesting a fragment instead of restoring history.

    Arguments:
        headers: incoming request headers
    Returns:
        whether the request expects a fragment
    """
    return (
        headers.get("HX-Request") == "true"
        and headers.get("HX-History-Restore-Request") != "true"
    )
