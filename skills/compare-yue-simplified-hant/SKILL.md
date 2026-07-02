---
name: compare-yue-simplified-hant
description: Use when comparing final simplified yue-Hant subtitle outputs against yue-Hans outputs, especially for SeriesDiff fixtures, simplification review audits, or deciding whether yue-Hant simplification outputs and expected diff test fixtures need updates.
---

# Compare Yue Simplified Hant

Use this workflow to audit the remaining differences between a yue-Hans series
and the corresponding yue-Hant series after traditional-to-simplified conversion
and simplification review.

## Inputs

For OCR datasets, compare:

- yue-Hans: `test/data/<dataset>/output/yue-Hans_ocr/fuse_clean_validate_review_flatten.srt`
- simplified yue-Hant: `test/data/<dataset>/output/yue-Hant_ocr/fuse_clean_validate_review_flatten_simplify_review.srt`

For non-OCR datasets, use the analogous final yue-Hans flattened output and final
yue-Hant flattened-simplified-review output.

If the comparison is tied to `test_series_diff_matches_expected_fixture`, also
find the expected diff fixture in `test/data/<dataset>/__init__.py` and the test
case in `test/analysis/diff/test_series_diff.py`.

## Compare

On Windows, set UTF-8 before printing subtitle text:

```powershell
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [System.Text.UTF8Encoding]::new()
$env:UV_CACHE_DIR = "/tmp/uv-cache"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
```

Use `SeriesDiff` with clear labels so the output matches any expected fixture:

```python
from scinoephile.analysis.diff import SeriesDiff

messages = [
    str(message)
    for message in SeriesDiff(yue_hans_series, yue_hant_simplified_series, one_lbl="SIMP", two_lbl="TRAD")
]
```

Report subtitle count and timing differences before assessing text differences.
If the expected fixture exists, compare the generated messages to that fixture and
say whether it needs to be updated.

## Assess Differences

Classify every text difference conservatively:

- `Expected OpenCC variant`: automatic conversion reasonably maps traditional
  text to a different simplified synonym or variant than the yue-Hans source
  uses.
- `Expected Cantonese-script preservation`: conversion or review intentionally
  preserves a Cantonese character, phrase, or particle rather than forcing a
  Mandarin-standard simplified equivalent.
- `Expected simplification review`: the yue-Hant simplification review fixed a
  leftover conversion issue or accepted typo correction, such as `甚么 -> 什么`,
  `著 -> 着`, or an already-approved dataset-specific OCR fix.
- `Needs pre-simplification review`: the difference is a lexical typo that should
  be corrected before simplification and, when applicable, in both yue-Hans and
  yue-Hant direct block reviews.
- `Needs source review`: the difference may be a real OCR/subtitle source
  divergence, but cannot be judged from text alone.
- `Likely incorrect`: the simplified yue-Hant review appears to introduce an
  unsupported content, punctuation, or whitespace change.

Do not silently discard differences. The table should include every remaining
subtitle whose text differs, including expected differences.

## Output

Start with a short summary:

- compared files or fixtures
- subtitle counts and whether timings changed
- number of text differences
- whether the expected diff test fixture should be updated
- links to the two image indexes:
  - yue-Hans: `test/data/<dataset>/output/yue-Hans_ocr/image/index.html`
  - yue-Hant: `test/data/<dataset>/output/yue-Hant_ocr/image/index.html`

Use normal local-file links to the two `image/index.html` files without
fragments when the current surface supports them; otherwise show their absolute
paths as text. For each subtitle row, include the exact anchor IDs as plain
text, such as `Hans #subtitle-number-123 / Hant #subtitle-number-123`. Local
HTML fragment links such as `C:/.../index.html#subtitle-number-123`,
`/C:/.../index.html#subtitle-number-123`, and `file://...#subtitle-number-123`
do not work reliably in Codex because the fragment may be resolved as part of
the filename. Do not start a static server just to make these anchors clickable.
If the current output surface explicitly supports local HTML fragments, then the
anchor IDs may be made clickable there.

Then output a Markdown table with these exact columns:

| Subtitle | yue-Hans Text | simplified yue-Hant Text | Difference | Assessment / Next Action |
|---:|---|---|---|---|

In the `Subtitle` column, include both side-specific anchor IDs, for example:
`123 (Hans #subtitle-number-123 / Hant #subtitle-number-123)`.

Keep each assessment actionable. If all differences are accepted, regenerate the
expected `SeriesDiff` fixture so `test_series_diff_matches_expected_fixture`
matches the current final outputs.
