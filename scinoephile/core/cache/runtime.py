#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runtime identities for persistent cache entries."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, distribution
from json import JSONDecodeError, loads

__all__ = ["get_distribution_identity"]


def get_distribution_identity(distribution_name: str) -> dict[str, str]:
    """Get an installed distribution's runtime identity.

    Arguments:
        distribution_name: installed distribution name
    Returns:
        distribution name, installed version, and VCS revision when available
    """
    try:
        installed_distribution = distribution(distribution_name)
    except PackageNotFoundError:
        return {"distribution": distribution_name, "version": "unavailable"}

    identity = {
        "distribution": distribution_name,
        "version": installed_distribution.version,
    }
    direct_url_json = installed_distribution.read_text("direct_url.json")
    if direct_url_json is None:
        return identity
    try:
        direct_url = loads(direct_url_json)
    except JSONDecodeError:
        return identity
    if not isinstance(direct_url, dict):
        return identity
    vcs_info = direct_url.get("vcs_info")
    if not isinstance(vcs_info, dict):
        return identity
    source_revision = vcs_info.get("commit_id")
    if isinstance(source_revision, str) and source_revision:
        identity["source_revision"] = source_revision
    return identity
