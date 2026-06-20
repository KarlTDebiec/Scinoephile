---
name: review-zho-review
description: Use when auditing standard Chinese OCR block-review fixtures, especially when comparing zho-Hans or zho-Hant fuse_clean_validate.srt to fuse_clean_validate_review.srt and judging whether review JSON changes are valid.
---

# Review Zho Review

Use this workflow to audit a standard Chinese OCR review fixture before accepting
or fixing its generated output.

## Inputs

Work from a standard Chinese OCR output directory such as:

```text
test/data/<dataset>/output/zho-Hans_ocr
test/data/<dataset>/output/zho-Hant_ocr
```

For direct review, use these files:

- `fuse_clean_validate.srt`: original validated OCR subtitle input
- `fuse_clean_validate_review.srt`: block-review output
- `lang/zho/block_review.json`: persisted review test cases and rationales

For a traditional-to-simplified review stage, compare
`fuse_clean_validate_review_flatten_simplify.srt` to
`fuse_clean_validate_review_flatten_simplify_review.srt` and use
`lang/zho/simplify_block_review.json`.

## Compare

Parse SRT files as raw UTF-8 text, not through `Series.load`, so whitespace and
punctuation are preserved exactly. On Windows, set UTF-8 first:

```powershell
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [System.Text.UTF8Encoding]::new()
$env:UV_CACHE_DIR = "/tmp/uv-cache"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
```

Compare subtitle count, timing lines, and text by subtitle number. The main audit
table should include every subtitle whose text differs between the two SRT files.
If subtitle count or timing differs, report that before the table.

## Map Review Rationales

Map the review JSON to global subtitle numbers by walking the JSON test cases in
order and counting each `query.zimu_N` key by numeric `N`. For each changed
subtitle, look up the matching local answer keys:

- revised text: `answer.xiugai_N`
- rationale: `answer.beizhu_N`

If a changed subtitle has no matching rationale, say so in the rationale column
and investigate whether the generated SRT is stale or the change came from
another processing step.

## Assess Changes

Use conservative judgment. The review step should produce relatively few content
changes.

Accept changes when they are clear OCR/subtitle fixes, such as:

- obvious character typos or OCR confusions
- wrong but visually similar characters
- missing or extra characters when context makes the source error clear
- script-appropriate character fixes: zho-Hans direct review should stay
  simplified, while zho-Hant direct review should stay traditional
- punctuation preservation or correction only when the source image/text clearly
  supports it or a prior cleaning step explicitly requires it

Reject or flag changes when they:

- simplify zho-Hant text during direct `fuse_clean_validate_review.srt` review
- traditionalize zho-Hans text during direct `fuse_clean_validate_review.srt`
  review
- rewrite style, diction, or wording without source evidence
- add missing-looking sentence-final punctuation unless the source image/text
  proves the punctuation was omitted by OCR
- rewrite quote styles or other punctuation solely for normalization, such as
  `〝虾〞 -> 「虾」`, unless that exact normalization is the audited behavior
- make whitespace-only changes between subtitle fragments unless the user
  specifically requested that exact cleanup
- convert uncertain homophones or ambiguous OCR artifacts without checking the
  source video/subtitle image

Use `Needs source check` when a change may be correct but cannot be verified from
the subtitle text alone.

## Output

Start with a short summary:

- subtitle counts and whether timings changed
- number of text changes
- changed subtitle numbers

Then output a Markdown table with these exact columns:

| Subtitle | Original Text | Revised Text | Review JSON Rationale | Assessment |
|---:|---|---|---|---|

Include every changed subtitle, not only the bad ones. Keep assessments specific:
`Correct`, `Incorrect`, `Questionable`, or `Needs source check`, followed by a
brief reason.
