#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Installed voice activity detection runtime identity helpers."""

from __future__ import annotations

from collections.abc import Mapping
from hashlib import sha256
from importlib.metadata import Distribution, PackageNotFoundError, distribution
from json import JSONDecodeError, loads
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

__all__ = ["get_distribution_identity"]


def _get_distribution_artifact_sha256(
    installed_distribution: Distribution, package_name: str
) -> str | None:
    """Hash installed runtime files belonging to one distribution package.

    Arguments:
        installed_distribution: installed package distribution metadata
        package_name: import package whose runtime files should be hashed
    Returns:
        SHA-256 digest of installed runtime files, if all can be identified
    """
    distribution_files = installed_distribution.files
    if distribution_files is None:
        return None
    package_parts = tuple(package_name.split("."))
    runtime_files = [
        package_path
        for package_path in distribution_files
        if package_path.parts[: len(package_parts)] == package_parts
        and "__pycache__" not in package_path.parts
        and package_path.suffix != ".pyc"
    ]
    if not runtime_files:
        return None

    digest = sha256()
    for package_path in sorted(runtime_files, key=lambda value: value.as_posix()):
        installed_path = Path(str(installed_distribution.locate_file(package_path)))
        if not installed_path.is_file():
            return None
        digest.update(package_path.as_posix().encode())
        digest.update(b"\0")
        try:
            with installed_path.open("rb") as file_handle:
                while chunk := file_handle.read(1024 * 1024):
                    digest.update(chunk)
        except OSError:
            return None
    return digest.hexdigest()


def get_distribution_identity(
    distribution_name: str, package_name: str
) -> dict[str, str]:
    """Get an installed distribution's version, source, and artifact identity.

    Arguments:
        distribution_name: installed distribution name
        package_name: import package containing its runtime artifacts
    Returns:
        installed distribution identity, or an unavailable marker
    """
    try:
        installed_distribution = distribution(distribution_name)
    except PackageNotFoundError:
        return {"distribution": distribution_name, "version": "unavailable"}

    identity = {
        "distribution": distribution_name,
        "version": installed_distribution.version,
    }
    if artifact_sha256 := _get_distribution_artifact_sha256(
        installed_distribution, package_name
    ):
        identity["artifact_sha256"] = artifact_sha256

    direct_url_text = installed_distribution.read_text("direct_url.json")
    if direct_url_text is None:
        return identity
    try:
        direct_url = loads(direct_url_text)
    except (JSONDecodeError, TypeError):
        return identity
    if not isinstance(direct_url, Mapping):
        return identity
    if isinstance(source_url := direct_url.get("url"), str):
        identity["source_url"] = _sanitize_source_url(source_url)
    vcs_info = direct_url.get("vcs_info")
    if not isinstance(vcs_info, Mapping):
        return identity
    if isinstance(vcs := vcs_info.get("vcs"), str):
        identity["source_vcs"] = vcs
    if isinstance(commit_id := vcs_info.get("commit_id"), str):
        identity["source_commit"] = commit_id
    if isinstance(requested_revision := vcs_info.get("requested_revision"), str):
        identity["source_requested_revision"] = requested_revision
    return identity


def _sanitize_source_url(source_url: str) -> str:
    """Remove credentials, query, and fragment data from a package source URL.

    Arguments:
        source_url: source URL from PEP 610 distribution metadata
    Returns:
        sanitized source URL safe for cache metadata
    """
    parsed_url = urlsplit(source_url)
    hostname = parsed_url.hostname
    netloc = ""
    if hostname is not None:
        netloc = hostname
        if ":" in hostname:
            netloc = f"[{hostname}]"
        try:
            if parsed_url.port is not None:
                netloc = f"{netloc}:{parsed_url.port}"
        except ValueError:
            netloc = hostname
    return urlunsplit((parsed_url.scheme, netloc, parsed_url.path, "", ""))
