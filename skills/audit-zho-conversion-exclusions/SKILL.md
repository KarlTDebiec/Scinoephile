---
name: audit-zho-conversion-exclusions
description: Use when auditing Scinoephile Chinese conversion exclusions or checking whether Hans/Hant test subtitles change unexpectedly under OpenCC no-op direction conversions.
---

# Audit Chinese Conversion Exclusions

Use this workflow to verify that Chinese subtitle fixtures stay stable under no-op direction OpenCC conversions.

## Run The Audit

Run the bundled script from the repository root:

```powershell
$env:UV_CACHE_DIR = "/tmp/uv-cache"
uv run python skills/audit-zho-conversion-exclusions/scripts/audit_zho_conversion_exclusions.py
```

Pass `--root PATH` when running outside the repository root.

The script discovers regular and OCR/PCR subtitle fixtures, audits Hans files with `t2s`, audits Hant files with `s2t`, filters active exclusions from `scinoephile/lang/zho/script/conversion.py`, and filters known inactive fixture artifacts encoded in the script.

## Handle Findings

Inspect each unexpected table row against the subtitle text and image dump link when one is available.

- Add or refine an active conversion exclusion in `scinoephile/lang/zho/script/conversion.py` only when the source text is legitimate and should remain unchanged in no-op conversion.
- Add a known inactive exception to the audit script only when the fixture artifact is expected but should not affect normal conversion behavior.
- Fix the fixture when the audit surfaces a typo, OCR error, or review error.

Keep exception details in Python source rather than duplicating them in `SKILL.md`: active conversion exclusions belong in `conversion.py`, and known inactive audit artifacts belong in `scripts/audit_zho_conversion_exclusions.py`.

For the final response, paste the script output or briefly report the unexpected rows. For a clean audit, the script summary is enough.
