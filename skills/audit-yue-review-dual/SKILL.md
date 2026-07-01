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

Start with the script summary, including subtitle counts, the successful timing
alignment check, changed counts, and image-index links. Then output the table
with the `Notes` column filled in.

The table columns are:

| Subtitle | yue-Hans | yue-Hant | yue-Hans vs Hant->Hans | Notes |
|---:|---|---|---|---|

In the `yue-Hans` and `yue-Hant` columns:

- If a script has a review edit for that subtitle, show exactly two lines:
  - first line = pre-review text
  - second line = post-review text
- If a script did not change that subtitle, show exactly one line: the unchanged text.
- If both scripts changed, both columns must show two lines each.
- Do not include any extra unchanged duplicate lines in any column.

In the `yue-Hans vs Hant->Hans` column, show the final texts from both scripts on
separate lines when they differ; otherwise show one instance of the shared final
text. Do not use arrows in these cells.

In the `Subtitle` column, output only the shared subtitle number, such as `123`.
The yue-Hans and yue-Hant series must be 1:1, so do not include separate Hans
and Hant anchor IDs or repeated subtitle numbers.
