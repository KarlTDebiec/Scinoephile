# Audit editor quickstart

`scinoephile audit review serve` opens a local proofreading and audit editor
for one subtitle language. Use `scinoephile audit review report` for a Markdown
report.

```sh
UV_CACHE_DIR=/tmp/uv-cache uv run --extra web scinoephile audit review serve \
  --infile validated.srt --outfile proofread.srt --json review.json
```

On Windows, set `$env:UV_CACHE_DIR = '/tmp/uv-cache'` before running `uv`.
Open `http://127.0.0.1:5020/`. Use `--port` for a second track or `--language`
to override detection.

- `--infile` is the read-only OCR SRT. `--outfile` is the edited SRT and is
  resumed if it already exists.
- `--json` is an optional native proofreading log. A proofreading edit can
  update or create it. Identical source blocks share a decision; omit `--json`
  if an existing SRT corrects identical blocks differently.
- Keep `<output-stem>.review.sqlite3` beside the output to resume audit notes
  and verification. Audit-only edits update this database. An optional
  `--audit-notes` Markdown report can seed the findings.

Use the editor to proofread, record findings, or verify subtitles. Changed text
requires a proofreading note. A **Review** finding requires an audit note;
**OK** requires an empty audit note. **Verify All Visible** covers every subtitle
matching the filters, including those farther down the page.

Model requests start only when you run proofreading or auditing. Choose a
provider, model and reasoning effort in either panel. LLM-backed CLI workflows
expose the same setting as `--llm-reasoning-effort`. Leaving it unset keeps the
provider default; different effective settings use separate response caches.

Reruns reuse compatible decisions and cached responses. **Re-proofread** reloads
the OCR file, which must retain its cue count and timings, and backs up the
previous SRT, JSON and progress before replacement. **Re-audit** updates findings
while keeping the proofread text and human verification.
