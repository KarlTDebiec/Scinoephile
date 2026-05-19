#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of OpenSubtitles API helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from scinoephile.media.subtitles.opensubtitles import OpenSubtitlesClient


@dataclass(frozen=True)
class _FakeRequest:
    """Recorded fake HTTP request."""

    method: str
    """HTTP method."""
    url: str
    """Request URL."""
    headers: dict[str, str] | None
    """Request headers."""
    params: dict[str, str] | None
    """Request query parameters."""
    json: dict[str, object] | None
    """Request JSON body."""


class _FakeResponse:
    """Fake requests response."""

    def __init__(self, *, json_data: object | None = None, content: bytes = b""):
        """Initialize.

        Arguments:
            json_data: JSON data returned by response
            content: response content bytes
        """
        self._json_data = json_data
        self.content = content

    def json(self) -> object:
        """Return fake JSON data."""
        return self._json_data

    def raise_for_status(self):
        """Simulate a successful HTTP status."""


class _FakeSession:
    """Fake requests session."""

    def __init__(self):
        """Initialize."""
        self._responses: list[_FakeResponse] = []
        self.requests: list[_FakeRequest] = []

    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> _FakeResponse:
        """Record a GET request and return the next response."""
        del timeout
        self.requests.append(
            _FakeRequest(
                method="GET",
                url=url,
                headers=headers,
                params=params,
                json=None,
            )
        )
        return self._responses.pop(0)

    def post(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, object] | None = None,
        timeout: float | None = None,
    ) -> _FakeResponse:
        """Record a POST request and return the next response."""
        del timeout
        self.requests.append(
            _FakeRequest(
                method="POST",
                url=url,
                headers=headers,
                params=None,
                json=json,
            )
        )
        return self._responses.pop(0)

    def queue_content(self, content: bytes):
        """Queue a fake content response.

        Arguments:
            content: response content bytes
        """
        self._responses.append(_FakeResponse(content=content))

    def queue_json(self, json_data: object):
        """Queue a fake JSON response.

        Arguments:
            json_data: response JSON data
        """
        self._responses.append(_FakeResponse(json_data=json_data))


def test_opensubtitles_search_returns_one_candidate_per_file():
    """Test OpenSubtitles search flattens files from result entries."""
    session = _FakeSession()
    session.queue_json(
        {
            "data": [
                {
                    "attributes": {
                        "language": "en",
                        "download_count": 42,
                        "ratings": 9.1,
                        "fps": 23.976,
                        "release": "The.Matrix.1999.1080p.BluRay.x264",
                        "files": [
                            {
                                "file_id": 123,
                                "file_name": "The.Matrix.1999.1080p.srt",
                            },
                            {
                                "file_id": 456,
                                "file_name": "The.Matrix.1999.commentary.srt",
                            },
                        ],
                    }
                }
            ]
        }
    )
    client = OpenSubtitlesClient(api_key="key", session=session)

    results = client.search(query="The Matrix", language="en", limit=10)

    assert [result.file_id for result in results] == [123, 456]
    assert results[0].language == "en"
    assert results[0].download_count == 42
    assert results[0].rating == 9.1
    assert results[0].fps == 23.976
    assert results[0].release_name == "The.Matrix.1999.1080p.BluRay.x264"
    assert results[0].file_name == "The.Matrix.1999.1080p.srt"
    assert session.requests[0].method == "GET"
    assert session.requests[0].url.endswith("/subtitles")
    assert session.requests[0].params == {
        "query": "The Matrix",
        "languages": "en",
    }


def test_opensubtitles_download_logs_in_requests_link_and_writes_file(
    tmp_path: Path,
):
    """Test OpenSubtitles download authenticates and writes subtitle content.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    outfile_path = tmp_path / "matrix.en.srt"
    session = _FakeSession()
    session.queue_json({"token": "token", "base_url": "https://dl.opensubtitles.com"})
    session.queue_json({"link": "https://dl.opensubtitles.com/download/123"})
    session.queue_content(b"1\n00:00:01,000 --> 00:00:02,000\nWake up.\n")
    client = OpenSubtitlesClient(api_key="key", session=session)

    client.download(
        file_id=123,
        outfile_path=outfile_path,
        username="user",
        password="password",
    )

    assert outfile_path.read_text(encoding="utf-8") == (
        "1\n00:00:01,000 --> 00:00:02,000\nWake up.\n"
    )
    assert [request.method for request in session.requests] == [
        "POST",
        "POST",
        "GET",
    ]
    assert session.requests[1].json == {"file_id": 123}
    assert session.requests[1].headers is not None
    assert session.requests[1].headers["Authorization"] == "Bearer token"
