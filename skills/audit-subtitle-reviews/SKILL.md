---
name: audit-subtitle-reviews
description: Audit Scinoephile English, standard Chinese, or Cantonese subtitle reviews using the review, review-trad, or review-dual CLI workflow. Use when inspecting pre/post-review SRT changes, traditional-to-simplified review stages, parallel Hans/Hant paths, review JSON notes, character-focused rows, or final script discrepancies in OCR or SRT test datasets.
---

# Audit Subtitle Reviews

Run commands from the repository root. Discover the available artifacts before
choosing a workflow; do not infer the workflow from language alone.

## Protect source data

- Never edit files under `test/data/<dataset>/input/`.
- Do not edit generated reviewed, flattened, simplified, timewarped, or romanized
  SRT files.
- For an audit-only request, do not modify review JSON or validation sources.
- When corrections are requested, apply review corrections to the relevant JSON
  and regenerate outputs.
- Edit `fuse_clean_validate.srt` and `image/index.html` only when the user
  explicitly requests an OCR validation-source correction.

## Select the workflow

Inspect `test/data/<dataset>/output/` and use the narrowest shape containing all
requested stages:

| Available stages | Command |
|---|---|
| One original/reviewed pair | `scinoephile audit review` |
| Traditional review plus review of its simplified form | `scinoephile audit review-trad` |
| Parallel simplified and traditional-to-simplified paths | `scinoephile audit review-dual` |

Use `review` for English or a single Chinese-script track. It detects English,
Zho/Yue, and Hans/Hant automatically. Use `review-trad` when only the Hant path
and its reviewed simplification exist. Use `review-dual` only when both the
independent Hans path and the Hant-to-Hans path exist.

## Locate artifacts

For OCR outputs, review pairs normally use:

- original: `<language>_ocr/fuse_clean_validate.srt`
- reviewed: `<language>_ocr/fuse_clean_validate_review.srt`
- review JSON: `<language>_ocr/lang/<language-code>/review.json`
- simplified Hant: `<language-Hant>_ocr/fuse_clean_validate_review_flatten_simplify.srt`
- reviewed simplified Hant: the same stem ending in `_simplify_review.srt`
- simplification JSON: `<language-Hant>_ocr/lang/<language-code>/simplify_review.json`

For text-source outputs, review pairs normally use `clean.srt` and
`clean_review.srt`. Discover later stages rather than assuming their stems;
Yue SRT workflows may include `flatten_timewarp_simplify`.

Confirm every selected SRT exists. The CLI rejects unequal subtitle counts.

## Run the audit

Always set `UV_CACHE_DIR=/tmp/uv-cache`. Pass the matching JSON when present so
the report includes review context.

For one review:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit review \
  --original <original.srt> \
  --reviewed <reviewed.srt> \
  --json <review.json>
```

For a traditional-to-simplified path:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit review-trad \
  --traditional <traditional.srt> \
  --traditional-reviewed <traditional-reviewed.srt> \
  --traditional-simplified <simplified-traditional.srt> \
  --traditional-simplified-reviewed <simplified-traditional-reviewed.srt> \
  --traditional-json <review.json> \
  --traditional-simplified-json <simplify-review.json>
```

For parallel script paths:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit review-dual \
  --simplified <simplified.srt> \
  --simplified-reviewed <simplified-reviewed.srt> \
  --traditional <traditional.srt> \
  --traditional-reviewed <traditional-reviewed.srt> \
  --traditional-simplified <simplified-traditional.srt> \
  --traditional-simplified-reviewed <simplified-traditional-reviewed.srt> \
  --simplified-json <simplified-review.json> \
  --traditional-json <traditional-review.json> \
  --traditional-simplified-json <simplify-review.json>
```

Omit a JSON option when its file is absent. On PowerShell, configure UTF-8 as
directed by the repository `AGENTS.md` before printing subtitles.

## Focus and inspect

The default `--filter changes` includes all review edits. For `review-dual`, it
also includes final discrepancies; use `--filter discrepancies` for those only.
Use `--filter all` for every subtitle. Add `--characters` for occurrence checks;
simplified and traditional variants are added automatically. Use inclusive
1-indexed bounds with `--first-index` and `--last-index`.
Do not generate or present a separate character-focused report by default. Use
one only when the user requests it or a specific suspected conversion gap needs
investigation.

Read the relevant language policy before assessing rows:

- Standard Chinese: [references/zho.md](references/zho.md)
- Cantonese: [references/yue.md](references/yue.md)
- English: apply ordinary English proofreading judgment; do not apply Chinese
  script or conversion rules.

Inspect every displayed row for incorrect edits, missed parallel corrections,
script leakage, lexical errors, OCR errors, punctuation, and whitespace. Treat
automatic JSON-backed notes only as context, not as proof that an edit is
correct. Before presenting the report, replace every `Notes` cell—including
populated and blank cells—with your own concise interpretation of the row in
English. Do not translate, preserve, quote, or merely restate an automatic note.
Keep each note to one terse verdict and only the essential reason. Begin accepted
edits with `OK;`, rejected edits with `Incorrect;`, and uncertain edits with
`Check;`. Prefer arrow notation for simple substitutions and omit boilerplate
about normalization, output stages, or preserved formatting. For example:
`OK; 甚么 -> 什么.`, `OK; 著 -> 着.`, and
`OK; 搞 is the idiomatic verb in 怎么搞的; 搅 is a likely error.`

Review stages must preserve the source punctuation and whitespace exactly.
Treat punctuation-only or whitespace-only revisions as invalid. When correcting
review data, remove those revisions; when a revision also corrects text, retain
the text correction while restoring the source punctuation and whitespace.
Assign every correction to the earliest review stage where it applies. Put OCR,
lexical, grammatical, semantic, and proper-name corrections in the initial
review, using that stage's script. Reserve later simplification reviews for
conversion-specific cleanup; move any generally applicable correction back to
the initial review and regenerate every downstream artifact.

Always show the complete raw Markdown report inline in the final response. Do
not replace it with a summary, findings, or a file link, and do not wrap it in a
code fence. Counts, actionable findings, and a link may accompany the report.
For a large report, also write it under `local/` with `--outfile` to inspect the
whole file before pasting its complete contents into the response.
