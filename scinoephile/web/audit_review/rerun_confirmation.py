#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Confirm when an editor job can replace previously saved results."""

from __future__ import annotations

from secrets import compare_digest, token_urlsafe
from time import time

from scinoephile.core.dependencies.web import import_flask
from scinoephile.core.llms import ReasoningEffort
from scinoephile.llms.providers.registry import get_provider_names

__all__ = ["confirm_rerun"]


def confirm_rerun(operation: str, *, rerun: bool) -> bool:
    """Require two preparation clicks and a delayed third click for a rerun.

    A normal start clears any pending rerun confirmation for the operation.

    Arguments:
        operation: worker whose settings and confirmation must match
        rerun: whether existing persisted output will be replaced
    Returns:
        whether this submission authorizes starting the worker
    Raises:
        ValueError: if the submitted provider or reasoning is unsupported
    """
    flask = import_flask()
    pending = dict(flask.session.get("rerun_confirmations", {}))
    if not rerun:
        if pending.pop(operation, None) is not None:
            flask.session["rerun_confirmations"] = pending
        return True
    settings = {
        name: flask.request.form.get(name, "")
        for name in ("provider", "model", "effort")
    }
    if settings["effort"]:
        ReasoningEffort(settings["effort"])
    if settings["provider"] not in get_provider_names():
        raise ValueError("Choose a supported provider")
    current = pending.get(operation, {})
    supplied = flask.request.form.get("confirmation", "")
    matches = (
        supplied.isascii()
        and compare_digest(supplied, current.get("token", ""))
        and current.get("settings") == settings
        and time() < current.get("expires_at", 0)
    )
    if matches and current.get("stage") == 2:
        if time() < current["ready_at"]:
            return False
        pending.pop(operation, None)
        flask.session["rerun_confirmations"] = pending
        return True
    stage = 1
    if matches and current.get("stage") == 1:
        stage = 2
    pending[operation] = {
        "stage": stage,
        "token": token_urlsafe(24),
        "settings": settings,
        "ready_at": time() + 3,
        "expires_at": time() + 600,
    }
    flask.session["rerun_confirmations"] = pending
    return False
