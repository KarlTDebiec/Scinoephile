#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""OpenSubtitles.com API helpers."""

from __future__ import annotations

from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import Protocol

import requests

from scinoephile.core import ScinoephileError

__all__ = [
    "OpenSubtitlesClient",
    "OpenSubtitlesFile",
]

logger = getLogger(__name__)


class _HttpResponse(Protocol):
    """Minimal HTTP response protocol used by the OpenSubtitles client."""

    content: bytes
    """Response content bytes."""

    def json(self) -> object:
        """Return decoded JSON response data."""

    def raise_for_status(self):
        """Raise for unsuccessful HTTP statuses."""


class _HttpSession(Protocol):
    """Minimal HTTP session protocol used by the OpenSubtitles client."""

    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> _HttpResponse:
        """Send a GET request."""

    def post(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, object] | None = None,
        timeout: float | None = None,
    ) -> _HttpResponse:
        """Send a POST request."""


@dataclass(frozen=True)
class OpenSubtitlesFile:
    """Search result for one downloadable OpenSubtitles file."""

    file_id: int
    """OpenSubtitles file identifier."""
    language: str | None = None
    """Subtitle language code."""
    download_count: int | None = None
    """OpenSubtitles download count."""
    rating: float | None = None
    """OpenSubtitles rating or points value."""
    fps: float | None = None
    """Subtitle frame rate."""
    release_name: str | None = None
    """Release name from the subtitle entry."""
    file_name: str | None = None
    """Subtitle file name."""


class OpenSubtitlesClient:
    """Client for the OpenSubtitles.com REST API."""

    def __init__(
        self,
        *,
        api_key: str | None,
        base_url: str = "https://api.opensubtitles.com/api/v1",
        user_agent: str = "Scinoephile v0.1.0",
        session: _HttpSession | None = None,
        timeout_seconds: float = 60.0,
    ):
        """Initialize.

        Arguments:
            api_key: OpenSubtitles API key
            base_url: OpenSubtitles API base URL
            user_agent: HTTP user agent
            session: optional requests session
            timeout_seconds: request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.user_agent = user_agent
        self.session = session or requests.Session()
        self.timeout_seconds = timeout_seconds

    def search(
        self, *, query: str, language: str, limit: int
    ) -> list[OpenSubtitlesFile]:
        """Search OpenSubtitles files.

        Arguments:
            query: text search query
            language: OpenSubtitles language code
            limit: maximum number of result files
        Returns:
            matching subtitle files
        """
        response = self.session.get(
            f"{self.base_url}/subtitles",
            headers=self._api_headers(),
            params={"query": query, "languages": language},
            timeout=self.timeout_seconds,
        )
        try:
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ScinoephileError("OpenSubtitles search request failed") from exc
        data = _require_mapping(response.json(), "OpenSubtitles search response")
        return _parse_search_files(data)[:limit]

    def download(
        self,
        *,
        file_id: int,
        outfile_path: Path,
        username: str | None,
        password: str | None,
        overwrite: bool = False,
    ) -> Path:
        """Download one OpenSubtitles file.

        Arguments:
            file_id: OpenSubtitles file identifier
            outfile_path: output subtitle path
            username: OpenSubtitles username
            password: OpenSubtitles password
            overwrite: whether to overwrite an existing output file
        Returns:
            output subtitle path
        """
        if username is None or not username.strip():
            raise ScinoephileError(
                "OpenSubtitles username is required for downloads; set "
                "OPENSUBTITLES_USERNAME or pass --username"
            )
        if password is None or not password.strip():
            raise ScinoephileError(
                "OpenSubtitles password is required for downloads; set "
                "OPENSUBTITLES_PASSWORD or pass --password"
            )
        if outfile_path.exists() and not overwrite:
            raise ScinoephileError(f"Output file already exists: {outfile_path}")

        token, download_base_url = self._login(username=username, password=password)
        link = self._request_download_link(
            file_id=file_id,
            token=token,
            download_base_url=download_base_url,
        )
        response = self.session.get(link, timeout=self.timeout_seconds)
        try:
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ScinoephileError("OpenSubtitles subtitle download failed") from exc

        if not outfile_path.parent.exists():
            outfile_path.parent.mkdir(parents=True)
            logger.info(f"Created subtitle output directory: {outfile_path.parent}")
        outfile_path.write_bytes(response.content)
        logger.info(f"Downloaded OpenSubtitles file {file_id} to {outfile_path}")
        return outfile_path

    def _api_headers(self) -> dict[str, str]:
        """Build OpenSubtitles API headers.

        Returns:
            OpenSubtitles API headers
        Raises:
            ScinoephileError: if API key is not configured
        """
        if self.api_key is None or not self.api_key.strip():
            raise ScinoephileError(
                "OpenSubtitles API key is required; set OPENSUBTITLES_API_KEY "
                "or pass --api-key"
            )
        return {
            "Api-Key": self.api_key,
            "User-Agent": self.user_agent,
        }

    def _login(self, *, username: str, password: str) -> tuple[str, str]:
        """Log in to OpenSubtitles.

        Arguments:
            username: OpenSubtitles username
            password: OpenSubtitles password
        Returns:
            bearer token and download API base URL
        """
        response = self.session.post(
            f"{self.base_url}/login",
            headers=self._api_headers(),
            json={"username": username, "password": password},
            timeout=self.timeout_seconds,
        )
        try:
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ScinoephileError("OpenSubtitles login request failed") from exc
        data = _require_mapping(response.json(), "OpenSubtitles login response")
        token = _require_str(data.get("token"), "OpenSubtitles login token")
        base_url = _get_str(data, "base_url")
        if base_url is None:
            base_url = self.base_url
        return token, base_url.rstrip("/")

    def _request_download_link(
        self,
        *,
        file_id: int,
        token: str,
        download_base_url: str,
    ) -> str:
        """Request a temporary subtitle download link.

        Arguments:
            file_id: OpenSubtitles file identifier
            token: OpenSubtitles bearer token
            download_base_url: authenticated API base URL
        Returns:
            temporary subtitle download link
        """
        headers = self._api_headers()
        headers["Authorization"] = f"Bearer {token}"
        response = self.session.post(
            f"{download_base_url}/download",
            headers=headers,
            json={"file_id": file_id},
            timeout=self.timeout_seconds,
        )
        try:
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ScinoephileError(
                "OpenSubtitles download-link request failed"
            ) from exc
        data = _require_mapping(response.json(), "OpenSubtitles download response")
        return _require_str(data.get("link"), "OpenSubtitles download link")


def _get_float(mapping: dict[str, object], key: str) -> float | None:
    """Get an optional float from a mapping.

    Arguments:
        mapping: mapping to inspect
        key: key to get
    Returns:
        float value, if present and numeric
    """
    value = mapping.get(key)
    if isinstance(value, int | float):
        return float(value)
    return None


def _get_int(mapping: dict[str, object], key: str) -> int | None:
    """Get an optional integer from a mapping.

    Arguments:
        mapping: mapping to inspect
        key: key to get
    Returns:
        integer value, if present and integral
    """
    value = mapping.get(key)
    if isinstance(value, int):
        return value
    return None


def _get_str(mapping: dict[str, object], key: str) -> str | None:
    """Get an optional string from a mapping.

    Arguments:
        mapping: mapping to inspect
        key: key to get
    Returns:
        string value, if present
    """
    value = mapping.get(key)
    if isinstance(value, str):
        return value
    return None


def _parse_search_files(data: dict[str, object]) -> list[OpenSubtitlesFile]:
    """Parse OpenSubtitles search results into downloadable files.

    Arguments:
        data: decoded OpenSubtitles search response
    Returns:
        downloadable subtitle file candidates
    """
    raw_entries = data.get("data")
    if not isinstance(raw_entries, list):
        raise ScinoephileError("OpenSubtitles search response missing data list")

    files = []
    for raw_entry in raw_entries:
        entry = _require_mapping(raw_entry, "OpenSubtitles subtitle entry")
        attributes = _require_mapping(
            entry.get("attributes"), "OpenSubtitles subtitle attributes"
        )
        raw_files = attributes.get("files")
        if not isinstance(raw_files, list):
            continue
        for raw_file in raw_files:
            file_data = _require_mapping(raw_file, "OpenSubtitles file")
            file_id = _get_int(file_data, "file_id")
            if file_id is None:
                continue
            files.append(
                OpenSubtitlesFile(
                    file_id=file_id,
                    language=_get_str(attributes, "language"),
                    download_count=_get_int(attributes, "download_count"),
                    rating=_get_float(attributes, "ratings"),
                    fps=_get_float(attributes, "fps"),
                    release_name=_get_str(attributes, "release"),
                    file_name=_get_str(file_data, "file_name"),
                )
            )
    return files


def _require_mapping(value: object, label: str) -> dict[str, object]:
    """Require a JSON value to be an object mapping.

    Arguments:
        value: value to inspect
        label: user-facing value label
    Returns:
        value narrowed to a string-keyed mapping
    Raises:
        ScinoephileError: if value is not an object mapping
    """
    if not isinstance(value, dict):
        raise ScinoephileError(f"{label} is malformed")
    mapping: dict[str, object] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise ScinoephileError(f"{label} is malformed")
        mapping[key] = item
    return mapping


def _require_str(value: object, label: str) -> str:
    """Require a JSON value to be a string.

    Arguments:
        value: value to inspect
        label: user-facing value label
    Returns:
        value narrowed to a string
    Raises:
        ScinoephileError: if value is not a string
    """
    if not isinstance(value, str) or not value:
        raise ScinoephileError(f"{label} is malformed")
    return value
