---
name: review-yue-review
description: Use when auditing Cantonese OCR block-review fixtures, especially when comparing fuse_clean_validate.srt to fuse_clean_validate_review.srt and judging whether review JSON changes are valid.
---

# Review Yue Review

Use this workflow to audit a written Cantonese OCR review fixture before accepting or
fixing its generated output.

## Inputs

Work from an OCR output directory such as:

```text
test/data/<dataset>/output/yue-Hans_ocr
test/data/<dataset>/output/yue-Hant_ocr
```

Use these files:

- `fuse_clean_validate.srt`: original validated OCR subtitle input
- `fuse_clean_validate_review.srt`: block-review output
- `lang/yue/block_review.json`: persisted review test cases and rationales

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

Map `block_review.json` to global subtitle numbers by walking the JSON test cases
in order and counting each `query.zimu_N` key by numeric `N`. For each changed
subtitle, look up the matching local answer keys:

- revised text: `answer.xiugai_N`
- rationale: `answer.beizhu_N`

If a changed subtitle has no matching rationale, say so in the rationale column and
investigate whether the generated SRT is stale or the change came from another
processing step.

## Assess Changes

Use conservative judgment. The review step should produce relatively few content
changes.

Accept changes when they are clear OCR/subtitle fixes, such as:

- obvious character typos: `哂 -> 晒`, `观音大使 -> 观音大士`
- appropriate simplification in a simplified fixture: `決 -> 决`
- punctuation preservation or correction only when the source image/text clearly
  supports it or a prior cleaning step explicitly requires it
- Cantonese-preserving typo fixes: `既刻 -> 即刻`, not `既刻 -> 立刻`

Reject or flag changes when they:

- Mandarinize written Cantonese, such as `嘅 -> 的`, `佢 -> 他`, `咗 -> 了`,
  `唔 -> 不`, `睇 -> 看`, `搵 -> 找`, `嚟 -> 来`, or `番 -> 回`
- replace valid Cantonese words or particles, such as `踎低`, `出便`, `锡`,
  `吖吗`, or sentence-final particles
- add missing-looking sentence-final punctuation, such as changing `着火啦` to
  `着火啦！`, unless the source image/text proves the punctuation was omitted by
  OCR
- rewrite quote styles or other punctuation solely for normalization, such as
  `〝虾〞 -> 「虾」`, unless that exact normalization is the audited behavior
- make whitespace-only changes between subtitle fragments unless the user
  specifically requested that exact cleanup
- change content without source evidence, such as fruit/object/action names
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
