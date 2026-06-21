---
name: compare-zho-simplified-hant
description: Use when comparing final simplified zho-Hant subtitle outputs against zho-Hans outputs, especially for SeriesDiff fixtures, simplification review audits, or deciding whether zho-Hant simplification outputs and expected diff test fixtures need updates.
---

# Compare Zho Simplified Hant

Use this workflow to audit the remaining differences between a zho-Hans series
and the corresponding zho-Hant series after traditional-to-simplified conversion
and simplification review.

## Inputs

For OCR datasets, compare:

- zho-Hans: `test/data/<dataset>/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt`
- simplified zho-Hant: `test/data/<dataset>/output/zho-Hant_ocr/fuse_clean_validate_review_flatten_simplify_review.srt`

For non-OCR datasets, use the analogous final zho-Hans flattened output and final
zho-Hant flattened-simplified-review output.

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

Use `SeriesDiff` with clear labels so the output matches the expected fixture:

```python
from scinoephile.analysis.diff import SeriesDiff

messages = [
    str(message)
    for message in SeriesDiff(zho_hans_series, zho_hant_simplified_series, one_lbl="SIMP", two_lbl="TRAD")
]
```

Report subtitle count and timing differences before assessing text differences.
If the expected fixture exists, compare the generated messages to that fixture and
say whether it needs to be updated.

## Assess Differences

Classify every text difference conservatively:

- `Expected OpenCC variant`: automatic conversion reasonably maps traditional
  text to a different simplified synonym or variant than the zho-Hans source
  uses, such as `藉 -> 借` or `捱 -> 挨`.
- `Expected simplification review`: the zho-Hant simplification review fixed a
  leftover conversion issue or accepted typo correction, such as `甚么 -> 什么`,
  `著 -> 着`, `菩甚么 -> 菩提什么`, or an already-approved dataset-specific OCR fix.
- `Needs pre-simplification review`: the difference is a lexical typo that should
  be corrected before simplification and, when applicable, in both zho-Hans and
  zho-Hant direct block reviews.
- `Needs source review`: the difference may be a real OCR/subtitle source
  divergence, but cannot be judged from text alone.
- `Likely incorrect`: the simplified zho-Hant review appears to introduce an
  unsupported content, punctuation, or whitespace change.

Do not silently discard differences. The table should include every remaining
subtitle whose text differs, including expected differences.

## Output

Start with a short summary:

- compared files or fixtures
- subtitle counts and whether timings changed
- number of text differences
- whether the expected diff test fixture should be updated

Then output a Markdown table with these exact columns:

| Subtitle | zho-Hans Text | simplified zho-Hant Text | Difference | Assessment / Next Action |
|---:|---|---|---|---|

Keep each assessment actionable. If all differences are accepted, regenerate the
expected `SeriesDiff` fixture so `test_series_diff_matches_expected_fixture`
matches the current final outputs.
