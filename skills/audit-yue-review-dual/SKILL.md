---
name: audit-yue-review-dual
description: Use when auditing Cantonese datasets across yue-Hans review, yue-Hant review, and final yue-Hans versus simplified yue-Hant outputs in one combined table, including OCR and SRT pipelines.
---

# Audit Yue Review Dual

Use this workflow when a Yue dataset needs one table that shows:

- what yue-Hans block review changed
- what yue-Hant block review changed
- what still differs between final yue-Hans and final simplified yue-Hant

This is useful when review decisions should be checked across both scripts at
the same subtitle number.

Important:

- Never edit files under `test/data/<dataset>/input/`.
- Do not edit source `.srt` or reviewed `.srt` fixture files directly.
- Only edit review JSON files and regenerate reviewed outputs from them.

## Inputs

For OCR datasets, use:

- `test/data/<dataset>/output/yue-Hans_ocr/fuse_clean_validate.srt`
- `test/data/<dataset>/output/yue-Hans_ocr/fuse_clean_validate_review.srt`
- `test/data/<dataset>/output/yue-Hans_ocr/fuse_clean_validate_review_flatten.srt`
- `test/data/<dataset>/output/yue-Hant_ocr/fuse_clean_validate.srt`
- `test/data/<dataset>/output/yue-Hant_ocr/fuse_clean_validate_review.srt`
- `test/data/<dataset>/output/yue-Hant_ocr/fuse_clean_validate_review_flatten_simplify_review.srt`

For SRT datasets, the review step happens before
timewarping:

- yue-Hans source: `test/data/<dataset>/input/yue-Hans.srt`
- yue-Hans review: `test/data/<dataset>/output/yue-Hans/clean_review.srt`
- final yue-Hans: `test/data/<dataset>/output/yue-Hans/clean_review_flatten_timewarp.srt`
- yue-Hant source: `test/data/<dataset>/input/yue-Hant.srt`
- yue-Hant review: `test/data/<dataset>/output/yue-Hant/clean_review.srt`
- final simplified yue-Hant: `test/data/<dataset>/output/yue-Hant/clean_review_flatten_timewarp_simplify_review.srt`

Edit these review JSON files (and only these) when applying corrections:

- OCR datasets:
  - `test/data/<dataset>/output/yue-Hans_ocr/lang/yue/block_review.json`
  - `test/data/<dataset>/output/yue-Hant_ocr/lang/yue/block_review.json`
  - `test/data/<dataset>/output/yue-Hant_ocr/lang/yue/simplify_block_review.json`
- SRT datasets:
  - `test/data/<dataset>/output/yue-Hans/lang/yue/block_review.json`
  - `test/data/<dataset>/output/yue-Hant/lang/yue/block_review.json`
  - `test/data/<dataset>/output/yue-Hant/lang/yue/simplify_block_review.json`

For SRT datasets, source/review timings should match within each script, and
final yue-Hans/final simplified yue-Hant timings should match after timewarp.
Do not require pre-timewarp source timings to match post-timewarp final timings.

## Run

On Windows, set UTF-8 first:

```powershell
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [System.Text.UTF8Encoding]::new()
$env:UV_CACHE_DIR = "/tmp/uv-cache"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
```

Run the bundled script from the repository root:

```powershell
uv run python skills/audit-yue-review-dual/scripts/audit_yue_review_dual.py --dataset acoptc
```

The default audit type is `changes`, which reports rows where either initial
review changed text or the final yue-Hans and simplified yue-Hant outputs still
differ. To audit subtitles containing `些`, pass `--audit 些`:

```powershell
uv run python skills/audit-yue-review-dual/scripts/audit_yue_review_dual.py --dataset kob --layout non-ocr --audit 些
```

To audit subtitles containing `番`, pass `--audit 番`:

```powershell
uv run python skills/audit-yue-review-dual/scripts/audit_yue_review_dual.py --dataset kob --layout non-ocr --audit 番
```

To audit subtitles containing `是`, pass `--audit 是`:

```powershell
uv run python skills/audit-yue-review-dual/scripts/audit_yue_review_dual.py --dataset kob --layout non-ocr --audit 是
```

To audit subtitles containing `着`, pass `--audit 着`:

```powershell
uv run python skills/audit-yue-review-dual/scripts/audit_yue_review_dual.py --dataset kob --layout non-ocr --audit 着
```

To audit review changes or final differences containing `喇`, `啦`, `啰`, or
`囉`, pass `--audit 喇啦啰`:

```powershell
uv run python skills/audit-yue-review-dual/scripts/audit_yue_review_dual.py --dataset kob --layout non-ocr --audit 喇啦啰
```

To audit subtitles containing `这`, `這`, or `那`, pass `--audit 这那`:

```powershell
uv run python skills/audit-yue-review-dual/scripts/audit_yue_review_dual.py --dataset kob --layout non-ocr --audit 这那
```

To limit the audit to a subtitle-number range, pass `--first-index` and/or
`--last-index`. These bounds are 1-indexed subtitle numbers and are inclusive:

```powershell
uv run python skills/audit-yue-review-dual/scripts/audit_yue_review_dual.py --dataset tmm --first-index 1 --last-index 200
```

For SRT datasets, run:

```powershell
uv run python skills/audit-yue-review-dual/scripts/audit_yue_review_dual.py --dataset <dataset> --layout non-ocr
```

The script prints Markdown directly to stdout for review in the console/conversation.
Do not redirect to an intermediate `.md` file as part of normal runs; keep output
in the immediate conversation or terminal output so it can be reviewed inline.
When the table is extremely large, still run this in-console and capture only the
range/summary as needed.

The script fails before printing the table if any of the yue-Hans input,
yue-Hans reviewed, final yue-Hans, yue-Hant input, yue-Hant reviewed, or final
simplified yue-Hant SRT files disagree on subtitle numbers. It also fails if
timings differ within comparable timing groups: all files for OCR datasets,
source/review pairs plus final/final pairs for SRT datasets.

## Interpret

Review the union table row by row. A row appears when at least one of these is
true:

- yue-Hans review changed the subtitle
- yue-Hant review changed the subtitle
- final yue-Hans text differs from final simplified yue-Hant text

Use the yue-Hans and yue-Hant columns to check whether both scripts made the
same approved correction at the same subtitle number. Use the final-comparison
columns to find remaining simplification, Mandarinization, punctuation, or
whitespace issues.

For `--audit 些`, a row appears when any audited source, review, or final text
contains `些`. Fill the `Notes` column with a judgment about whether each
instance should be corrected to `啲` during initial review, and whether that
correction is already applied symmetrically. Keep notes short, for example:

- `Both should change 些 to 啲.`
- `Already corrected to 啲 in both reviews.`
- `Hans should also change 些 to 啲.`
- `Keep 些 here.`

For `--audit 番`, a row appears when any audited source, review, or final text
contains `番`. Fill the `Notes` column with a judgment about whether each
instance should be corrected during initial review. Common outcomes include
`返` for colloquial back/again/return usage, `翻` where the meaning is
turning/overturning, or keeping `番` where it is correct. Keep notes short, for
example:

- `Already corrected to 返 in both reviews.`
- `Both should change 番 to 返.`
- `Change 番 to 翻 here.`
- `Keep 番 here.`

For `--audit 是`, a row appears when any audited source, review, or final text
contains `是`. Fill the `Notes` column with a judgment about whether each
instance should be corrected during initial review. Common outcomes include
`係` for the Cantonese copula/focus marker, or keeping `是` where it is part of
a standard word, title, or fixed expression. Keep notes short, for example:

- `Already corrected to 係 in both reviews.`
- `Both should change 是 to 係.`
- `Keep 是 here.`

For `--audit 喇啦啰`, a row appears when a review edit or final text difference
contains `喇`, `啦`, `啰`, or `囉`. This audit is intentionally scoped to changed
rows because these particles are too common for a broad occurrence audit. Fill
the `Notes` column with a judgment about whether the particle choice is
appropriate and symmetrical. Common outcomes include `啦` for general
imperative/exclamatory particle uses, `喇` where the source particle should be
kept, `啰`/`囉` where the lo particle is intended, or removing inappropriate
particle/punctuation changes. Keep notes short, for example:

- `Both changed 喇 to 啦.`
- `Keep 喇 here.`
- `Hans should also change 喇 to 啦.`
- `Remove final particle change.`

For `--audit 这那`, a row appears when any audited source, review, or final text
contains `这`, `這`, or `那`. Fill the `Notes` column with a judgment about
whether each instance should be corrected during initial review. Common outcomes
include `呢`/`呢啲` for proximal demonstratives, `嗰`/`嗰個` for distal
demonstratives, or keeping the source text for fixed/formal language. Keep notes
short, for example:

- `Already corrected to 嗰個 in both reviews.`
- `Both should change 這啲 to 呢啲.`
- `Both should change 那 to 嗰.`
- `Keep 那 here.`

Flag asymmetric review corrections as discrepancies. If one script makes an
approved lexical or OCR correction and the corresponding other-script line has
the same underlying issue, the other script should usually make the same
correction in its review output instead of leaving it to simplification review
or final comparison.

The script output is a draft table. Read that Python script output first.

Manual review rule:

- The script intentionally leaves `Notes` blank; you **must** fill every row
  manually using the three content columns in the same row. As the reviewing
  agent, you are responsible for writing these notes; do not defer note-taking
  to any other source.
- Do not change subtitle numbers, text columns, or summary lines.
- For each row, infer what happened by reading:
  - `yue-Hans` and `yue-Hant` review cells (initial review edits and asymmetry),
  - `yue-Hans vs Hant->Hans` (post-review final alignment or mismatch).
- Then write a concise, specific note describing that behavior:
  - write your judgment on the change; do not restate the change
  - one sentence only
  - do not repeat the subtitle text
  - for clean, aligned rows, prefer ultra-short judgment notes
  - If no change was made to `yue-Hant` other than simplification, do state so unless there is some concern.
  - If final output is aligned, do not state so.
  - be as concise as possible; the fewer words the better, here are some examples:
    - `Both changed 喇 to 啦.`
    - `Hans changed 㖞 to 喎`
    - `Hant removed 係/是, creating a final inconsistency`
    - `Hant innapropriately Mandarinized to 過來.`
Important review-quality rule:

- Never add or keep Mandarinization changes in any yue review path. In particular, do not replace Cantonese particles and short forms with Mandarin-style equivalents (e.g. `咗 -> 了`) in `simplify_block_review.json` or other review files. If such a change exists, remove that `xiugai_*` entry and keep the Cantonese wording so the Cantonese review and finalization stay dialect-consistent.

Output safety rule:

- Do not wrap the output in code fences under any circumstances.
- Do not wrap the report in Markdown fences or inline code ticks (no triple backticks).
- Do not prepend or append explanatory prose outside the report.
- Do not include a leading or trailing ``` block, markdown language tag (for example ```markdown), or any wrapper.
- The final user-facing response must begin with the summary header and contain only raw markdown content.
- The first non-empty line must be the report title, e.g. `# kob Yue Review Dual`.

- The script is a data extractor; `Notes` is a manual annotation layer.

Do not leave the `Notes` column blank in user-facing output. If any note is blank in the raw script output, you must populate it before sending the response.
If any row is missing a note, you must treat that as a hard stop condition: do not output or send the table until that note is filled.

## Output

When you run this skill, the script output must be returned directly in your response.
Do not summarize or replace it.
Include the full Markdown report text (summary + table) exactly as printed, then
immediately fill in the `Notes` cells in-place for every displayed row.
`Notes` must never be blank, and you must not use placeholders such as `N/A`, `-`, or whitespace.

Before presenting, ensure every row in the table has a non-empty `Notes` cell.
If any note is missing in the raw script output, set it manually before continuing.

Absolutely do not output any table (or any partial report) with a blank `Notes` cell.  
If the table contains even one empty note, pause and populate it first; do not proceed to user-facing output.

Start with the script summary, including changed counts, table rows, and the
subtitle range when present. Then output the table with the `Notes` column
filled in.

The table columns are:

| Subtitle | yue-Hans | yue-Hant | yue-Hans vs Hant->Hans | Notes |
|---:|---|---|---|---|

In the `yue-Hans` and `yue-Hant` columns:

- If a script has a review edit for that subtitle, show exactly two lines:
  - first line = pre-review text
  - second line = post-review text
- If a script did not change that subtitle, show exactly one line: the unchanged text.
  This includes rows that appear only because final yue-Hans and simplified
  yue-Hant differ.
- If both scripts changed, both columns must show two lines each.
- Do not include any extra unchanged duplicate lines in any column.

In the `yue-Hans vs Hant->Hans` column, show the final texts from both scripts on
separate lines when they differ; otherwise show one instance of the shared final
text. Do not use arrows in these cells.

In the `Subtitle` column, output only the shared subtitle number, such as `123`.
The yue-Hans and yue-Hant series must be 1:1, so do not include separate Hans
and Hant anchor IDs or repeated subtitle numbers.
