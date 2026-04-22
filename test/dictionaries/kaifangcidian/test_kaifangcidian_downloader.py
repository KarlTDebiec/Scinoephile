#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.dictionaries.kaifangcidian.KaifangcidianDownloader."""

from __future__ import annotations

import pytest
import requests

from scinoephile.dictionaries.kaifangcidian.downloader import KaifangcidianDownloader


class _MockResponse:
    """Mock HTTP response."""

    def __init__(self, text: str):
        """Initialize.

        Arguments:
            text: response body text
        """
        self.text = text

    def raise_for_status(self):
        """Raise no error for a successful mock response."""


def test_download_payloads_only_fetch_required_sources(
    monkeypatch: pytest.MonkeyPatch,
):
    """Download only the payloads currently used for canonical rows.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    downloader = KaifangcidianDownloader()
    requested_urls: list[str] = []

    def _mock_get(url: str, *, timeout: float) -> _MockResponse:
        """Mock requests.get and record requested URLs.

        Arguments:
            url: requested URL
            timeout: request timeout
        Returns:
            mock response
        """
        requested_urls.append(url)
        return _MockResponse(f'var payload = "{url}";')

    monkeypatch.setattr(requests, "get", _mock_get)

    payloads = downloader._download_payloads()

    assert list(payloads) == ["hzsg", "jpsg"]
    assert len(requested_urls) == 2
