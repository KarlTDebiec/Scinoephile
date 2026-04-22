#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Download and normalize Kaifangcidian website data into canonical CSV."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path

import opencc
import requests
from pypinyin import Style, lazy_pinyin

from .constants import (
    KAIFANGCIDIAN_HZSG_URL,
    KAIFANGCIDIAN_JPSG_URL,
    KAIFANGCIDIAN_LG_URL,
)

__all__ = [
    "KaifangcidianDownloader",
]

logger = getLogger(__name__)

_JS_VAR_REGEX = re.compile(
    r'var\s+(?P<name>[A-Za-z_]\w*)\s*=\s*"(?P<value>.*?)";',
    re.DOTALL,
)


@dataclass(frozen=True)
class _CanonicalRow:
    """One canonical Kaifangcidian CSV row."""

    kind: str
    """Source subsection key."""

    traditional: str
    """Traditional headword text."""

    simplified: str
    """Simplified headword text."""

    pinyin: str
    """Mandarin pinyin string."""

    jyutping: str
    """Cantonese Jyutping string."""

    definition: str
    """Primary normalized definition text."""

    note: str
    """Optional note text."""

    variants: str
    """Optional variant headword payload."""


class KaifangcidianDownloader:
    """Downloader for Kaifangcidian website JavaScript datasets."""

    def __init__(self, request_timeout_seconds: float = 60.0):
        """Initialize.

        Arguments:
            request_timeout_seconds: timeout for each HTTP request
        """
        self.request_timeout_seconds = request_timeout_seconds
        self.opencc_converter = opencc.OpenCC("hk2s")

    def download_to_csv(self, output_csv_path: Path) -> Path:
        """Download current Kaifangcidian data and write canonical CSV.

        Arguments:
            output_csv_path: canonical CSV output path
        Returns:
            canonical CSV path
        """
        output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        payloads = self._download_payloads()
        rows = self._get_canonical_rows(payloads)

        with output_csv_path.open("w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(
                outfile,
                fieldnames=[
                    "kind",
                    "traditional",
                    "simplified",
                    "pinyin",
                    "jyutping",
                    "definition",
                    "note",
                    "variants",
                ],
            )
            writer.writeheader()
            for row in rows:
                writer.writerow(
                    {
                        "kind": row.kind,
                        "traditional": row.traditional,
                        "simplified": row.simplified,
                        "pinyin": row.pinyin,
                        "jyutping": row.jyutping,
                        "definition": row.definition,
                        "note": row.note,
                        "variants": row.variants,
                    }
                )
        return output_csv_path

    def _download_payloads(self) -> dict[str, str]:
        """Download required Kaifangcidian JavaScript payloads.

        Returns:
            javascript payload text by source key
        """
        urls = {
            "hzsg": KAIFANGCIDIAN_HZSG_URL,
            "jpsg": KAIFANGCIDIAN_JPSG_URL,
            "lg": KAIFANGCIDIAN_LG_URL,
        }
        payloads: dict[str, str] = {}
        for payload_name, url in urls.items():
            logger.info(f"Downloading Kaifangcidian payload: {url}")
            response = requests.get(url, timeout=self.request_timeout_seconds)
            response.raise_for_status()
            payloads[payload_name] = response.text
        return payloads

    def _get_canonical_rows(self, payloads: dict[str, str]) -> list[_CanonicalRow]:
        """Convert raw website payloads into canonical rows.

        Arguments:
            payloads: JavaScript payload text by source key
        Returns:
            canonical rows
        """
        hzsg_vars = self._parse_js_vars(payloads["hzsg"])
        jpsg_vars = self._parse_js_vars(payloads["jpsg"])

        rows: list[_CanonicalRow] = []
        rows.extend(
            self._pair_rows("zi", hzsg_vars.get("zi", ""), jpsg_vars.get("jpzi", ""))
        )
        rows.extend(
            self._pair_rows("ci", hzsg_vars.get("ci", ""), jpsg_vars.get("jpci", ""))
        )
        rows.extend(
            self._pair_rows("smj", hzsg_vars.get("smj", ""), jpsg_vars.get("jpsmj", ""))
        )

        rows.sort(
            key=lambda row: (
                row.kind,
                row.traditional,
                row.jyutping,
                row.definition,
                row.note,
                row.variants,
            )
        )
        return rows

    def _pair_rows(
        self, kind: str, han_data: str, jyutping_data: str
    ) -> list[_CanonicalRow]:
        """Pair headword rows with Jyutping rows by position.

        Arguments:
            kind: source subsection key
            han_data: `@`-separated headword payload string
            jyutping_data: `@`-separated Jyutping payload string
        Returns:
            canonical rows
        """
        han_rows = han_data.split("@") if han_data else []
        jyutping_rows = jyutping_data.split("@") if jyutping_data else []
        if len(han_rows) != len(jyutping_rows):
            logger.warning(
                f"Kaifangcidian {kind} rows mismatch: "
                f"{len(han_rows)} han rows vs {len(jyutping_rows)} jyutping rows"
            )

        row_count = min(len(han_rows), len(jyutping_rows))
        rows: list[_CanonicalRow] = []
        for row_index in range(row_count):
            rows.extend(
                self._parse_paired_row(
                    kind=kind,
                    han_row=han_rows[row_index],
                    jyutping_row=jyutping_rows[row_index],
                )
            )
        return rows

    def _parse_paired_row(
        self,
        *,
        kind: str,
        han_row: str,
        jyutping_row: str,
    ) -> list[_CanonicalRow]:
        """Parse one paired Han/Jyutping row.

        Arguments:
            kind: source subsection key
            han_row: Han row text
            jyutping_row: Jyutping row text
        Returns:
            canonical rows
        """
        fields = han_row.split("|")
        traditional = fields[0].strip() if fields else ""
        if not traditional:
            return []

        if kind == "ci":
            definition = fields[1].strip() if len(fields) > 1 else ""
            note = fields[2].strip() if len(fields) > 2 else ""
        elif kind == "zi":
            definition = fields[2].strip() if len(fields) > 2 else ""
            note = fields[1].strip() if len(fields) > 1 else ""
        else:
            definition = fields[1].strip() if len(fields) > 1 else ""
            note = fields[2].strip() if len(fields) > 2 else ""

        variants = "|".join(field.strip() for field in fields[3:] if field.strip())
        simplified = self.opencc_converter.convert(traditional)
        pinyin = self._get_pinyin(simplified)

        jyutping_variants = [
            re.sub(r"\s+", " ", variant).strip().lower()
            for variant in jyutping_row.split("#")
            if variant.strip()
        ]
        if not jyutping_variants:
            jyutping_variants = [""]

        return [
            _CanonicalRow(
                kind=kind,
                traditional=traditional,
                simplified=simplified,
                pinyin=pinyin,
                jyutping=jyutping,
                definition=definition,
                note=note,
                variants=variants,
            )
            for jyutping in jyutping_variants
        ]

    @staticmethod
    def _get_pinyin(text: str) -> str:
        """Get numbered pinyin for one text string.

        Arguments:
            text: input text
        Returns:
            numbered pinyin
        """
        return (
            " ".join(
                lazy_pinyin(
                    text,
                    style=Style.TONE3,
                    neutral_tone_with_five=True,
                    v_to_u=True,
                )
            )
            .lower()
            .replace("ü", "u:")
        )

    @staticmethod
    def _parse_js_vars(js_text: str) -> dict[str, str]:
        """Parse JavaScript `var name = "value";` assignments.

        Arguments:
            js_text: JavaScript source text
        Returns:
            mapping of variable names to raw string payloads
        """
        parsed: dict[str, str] = {}
        for match in _JS_VAR_REGEX.finditer(js_text):
            parsed[match.group("name")] = match.group("value")
        return parsed
