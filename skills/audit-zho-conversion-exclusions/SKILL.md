---
name: audit-zho-conversion-exclusions
description: Use when auditing Scinoephile Chinese conversion exclusions or checking whether Hans/Hant test subtitles change unexpectedly under OpenCC no-op direction conversions.
---

# Audit Chinese Conversion Exclusions

Use this workflow to find characters that should be added to, removed from, or left out of `scinoephile/lang/zho/script/conversion.py` conversion exclusions.

## What To Audit

Audit both regular subtitles and OCR/PCR-generated fixtures:

- Regular source subtitles: `test/data/*/input/{yue,zho}-Hans.srt` and `test/data/*/input/{yue,zho}-Hant.srt`
- OCR/PCR fixtures: `test/data/*/output/{yue,zho}-Hans_ocr/fuse_clean_validate.srt` and `test/data/*/output/{yue,zho}-Hant_ocr/fuse_clean_validate.srt`

Run each Hans file through `t2s` and each Hant file through `s2t`. These are no-op direction checks, so text should mostly remain unchanged. Changes usually mean one of:

- A legitimate fixture character should become an active conversion exclusion.
- The fixture contains a typo or OCR/review artifact and should stay inactive.
- The conversion audit has surfaced a real subtitle problem for review.

## Run The Audit

Run the bundled Python script from the repository root. It discovers all regular and OCR/PCR subtitle fixtures, runs the appropriate no-op direction conversion, filters active exclusions and known inactive exceptions, and prints Markdown tables with unexpected changes and image dump links.

PowerShell:

```powershell
$env:UV_CACHE_DIR = "/tmp/uv-cache"
uv run python skills/audit-zho-conversion-exclusions/scripts/audit_zho_conversion_exclusions.py
```

Bash:

```bash
export UV_CACHE_DIR=/tmp/uv-cache
uv run python skills/audit-zho-conversion-exclusions/scripts/audit_zho_conversion_exclusions.py
```

Pass `--root PATH` when running outside the repository root:

```bash
uv run python skills/audit-zho-conversion-exclusions/scripts/audit_zho_conversion_exclusions.py --root /path/to/Scinoephile
```

The script compares parsed subtitle text, not raw file bytes, and uses `get_zho_text_converted(..., apply_exclusions=False)` for raw OpenCC counts plus `apply_exclusions=True` for reportable changes after active exclusions.

## Report Format

Report only unexpected changes as a merged Markdown table:

| Source | Image dump | Character | Expected | Subtitle | Note |
| --- | --- | --- | --- | --- | --- |
| [ACOPB yue-Hans](C:/Users/karls/Code/Scinoephile/test/data/acopopb/output/yue-Hans_ocr/fuse_clean_validate.srt) | [image](C:/Users/karls/Code/Scinoephile/test/data/acopopb/output/yue-Hans_ocr/image/index.html) | `決` | `决` | 16 | Traditional `決` in Hans OCR output; LEGIT, not OCR error |

For Hant audited through `s2t`, write comments as simplified-to-traditional expectations. For Hans audited through `t2s`, write comments as traditional-to-simplified expectations.

Use compact source labels such as `TMM zho-Hans`, linked to the source SRT file. The script derives image dump paths from OCR/PCR fixture paths by replacing `fuse_clean_validate.srt` with `image/index.html`. For example, `test/data/tmm/output/zho-Hant_ocr/fuse_clean_validate.srt` maps to `test/data/tmm/output/zho-Hant_ocr/image/index.html`. It uses absolute local Markdown links. For regular `input/*.srt` findings, it includes an image link only when a corresponding OCR/PCR `image/index.html` exists.

## Known t2s No-Op Exceptions

Do not report these as unexpected if the same character appears at the same subtitle:

| Source | Character | Expected | Subtitle | Note |
| --- | --- | --- | --- | --- |
| `test/data/acopopb/input/zho-Hans.srt` | `潚` | `潇` | 517 | Subtitle typo for `瀟`/`潇`; TYPO, not OCR error |
| `test/data/acopopb/output/yue-Hans_ocr/fuse_clean_validate.srt` | `決` | `决` | 16 | Traditional `決` in Hans OCR output; LEGIT, not OCR error |
| `test/data/acopopb/output/yue-Hans_ocr/fuse_clean_validate.srt` | `幫` | `帮` | 261 | Traditional `幫` in Hans OCR output; LEGIT, not OCR error |
| `test/data/acopopb/output/zho-Hans_ocr/fuse_clean_validate.srt` | `潚` | `㴋` | 521 | Traditional `潚` in Hans OCR output; known exception |
| `test/data/acoptc/output/yue-Hans_ocr/fuse_clean_validate.srt` | `決` | `决` | 326 | Traditional `決` in Hans OCR output; known exception |

Keep the final response concise: paste the script output, or summarize it only if the user asks for a summary.
