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

## Run The CLI

Use the project CLI, not a hidden module entry point. Choose `zho process` for standard Chinese files and `yue process` for written Cantonese files.

PowerShell:

```powershell
$env:UV_CACHE_DIR = "/tmp/uv-cache"
uv run scinoephile zho process -i test/data/tmm/output/zho-Hans_ocr/fuse_clean_validate.srt --convert t2s -o local/zho-Hans.t2s.srt --overwrite
uv run scinoephile zho process -i test/data/tmm/output/zho-Hant_ocr/fuse_clean_validate.srt --convert s2t -o local/zho-Hant.s2t.srt --overwrite
uv run scinoephile yue process -i test/data/tmm/output/yue-Hans_ocr/fuse_clean_validate.srt --convert t2s -o local/yue-Hans.t2s.srt --overwrite
uv run scinoephile yue process -i test/data/tmm/output/yue-Hant_ocr/fuse_clean_validate.srt --convert s2t -o local/yue-Hant.s2t.srt --overwrite
```

Bash:

```bash
export UV_CACHE_DIR=/tmp/uv-cache
uv run scinoephile zho process -i test/data/tmm/output/zho-Hans_ocr/fuse_clean_validate.srt --convert t2s -o local/zho-Hans.t2s.srt --overwrite
uv run scinoephile zho process -i test/data/tmm/output/zho-Hant_ocr/fuse_clean_validate.srt --convert s2t -o local/zho-Hant.s2t.srt --overwrite
uv run scinoephile yue process -i test/data/tmm/output/yue-Hans_ocr/fuse_clean_validate.srt --convert t2s -o local/yue-Hans.t2s.srt --overwrite
uv run scinoephile yue process -i test/data/tmm/output/yue-Hant_ocr/fuse_clean_validate.srt --convert s2t -o local/yue-Hant.s2t.srt --overwrite
```

For batch work, discover targets first, then run the matching command for each path.

PowerShell:

```powershell
$targets = Get-ChildItem test/data -Recurse -Filter *.srt | Where-Object {
    $_.FullName -match "\\input\\(yue|zho)-Han[st]\.srt$" -or
    $_.FullName -match "\\output\\(yue|zho)-Han[st]_ocr\\fuse_clean_validate\.srt$"
}

foreach ($target in $targets) {
    $language = [regex]::Match($target.FullName, "(yue|zho)-Han[st]").Groups[1].Value
    $config = if ($target.FullName -match "-Hant") { "s2t" } else { "t2s" }
    $command = if ($language -eq "yue") { "yue" } else { "zho" }
    $out = "local/conversion-audit/$($target.FullName -replace '[:\\\\/]', '_').$config.srt"
    New-Item -ItemType Directory -Force (Split-Path $out) | Out-Null
    uv run scinoephile $command process -i $target.FullName --convert $config -o $out --overwrite
}
```

Bash:

```bash
export UV_CACHE_DIR=/tmp/uv-cache
find test/data -type f -name "*.srt" \
    | grep -E "/input/(yue|zho)-Han[st]\.srt$|/output/(yue|zho)-Han[st]_ocr/fuse_clean_validate\.srt$" \
    | sort \
    | while IFS= read -r target; do
        if [[ "$target" == *"-Hant"* ]]; then
            config=s2t
        else
            config=t2s
        fi

        if [[ "$target" == *"/yue-Han"* ]]; then
            command=yue
        else
            command=zho
        fi

        out="local/conversion-audit/${target//[\/:]/_}.${config}.srt"
        mkdir -p "$(dirname "$out")"
        uv run scinoephile "$command" process -i "$target" --convert "$config" -o "$out" --overwrite
    done
```

Compare parsed subtitle text, not raw file bytes, because CLI output may normalize SRT serialization.

## Report Format

Group findings by source file. Report only unexpected changes. Use this comment style, without the word `inactive:`:

```python
# test/data/acopopb/output/yue-Hans_ocr/fuse_clean_validate.srt:
# "決",  # traditional 決 in Hans OCR output; expected 决
#        # found: subtitle 16 (LEGIT; not OCR error)
```

For Hant audited through `s2t`, write comments as simplified-to-traditional expectations. For Hans audited through `t2s`, write comments as traditional-to-simplified expectations.

## Known t2s No-Op Exceptions

Do not report these as unexpected if the same character appears at the same subtitle:

```python
# test/data/acopopb/input/zho-Hans.srt:
# "潚",  # subtitle typo for 瀟/潇; expected 潇
#        # found: subtitle 517 (TYPO; not OCR error)
#
# test/data/acopopb/output/yue-Hans_ocr/fuse_clean_validate.srt:
# "決",  # traditional 決 in Hans OCR output; expected 决
#        # found: subtitle 16 (LEGIT; not OCR error)
# "幫",  # traditional 幫 in Hans OCR output; expected 帮
#        # found: subtitle 261 (LEGIT; not OCR error)
#
# test/data/acopopb/output/zho-Hans_ocr/fuse_clean_validate.srt:
# "瀟",  # traditional 瀟 in Hans OCR output; expected 潇
#        # found: subtitle 521 (TYPO; not OCR error)
```

## Practical Comparison Helper

When the user asks for an audit report rather than converted fixture files, use a temporary Python snippet to compare parsed SRT events and print the report. It should:

1. Discover the regular and OCR/PCR target files above.
2. Select `t2s` for `*-Hans*` and `s2t` for `*-Hant*`.
3. Use `get_zho_text_converted(text, OpenCCConfig(...), apply_exclusions=False)` so the audit finds raw OpenCC changes rather than current exclusion behavior.
4. For each event whose text changes, emit the source path, original character, expected converted character, and subtitle number.
5. Remove any exact known exceptions before printing.

Keep the final response concise: list unexpected changes only, then mention if there were no unexpected changes.
