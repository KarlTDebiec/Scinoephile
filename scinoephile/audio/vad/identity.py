#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Installed voice activity detection runtime identity helpers."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

__all__ = ["get_distribution_identity"]


def get_distribution_identity(distribution_name: str) -> dict[str, str]:
    """Get an installed distribution's stable identity.

    Arguments:
        distribution_name: installed distribution name
    Returns:
        distribution name and installed version
    """
    try:
        distribution_version = version(distribution_name)
    except PackageNotFoundError:
        distribution_version = "unavailable"
    return {"distribution": distribution_name, "version": distribution_version}
