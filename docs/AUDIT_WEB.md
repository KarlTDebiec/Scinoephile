# Interactive proofreading review

`audit review serve` edits one subtitle language directly. It is separate from
`audit review report`: no report, project manifest, or existing JSON is required.
The app uses Flask/Jinja and bundled HTMX, with ordinary form submissions as a
fallback. Its compact filters and light/dark styling follow aXYom32's music tool.

## Launch

Install Scinoephile's `web` extra, then run:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit review serve \
  --infile validated.srt --outfile proofread.srt \
  --json review.json --title "Made in Hong Kong (1997) English"
```

On Windows, set `$env:UV_CACHE_DIR='/tmp/uv-cache'` before running `uv`.
The default URL is `http://127.0.0.1:5020/`; `--port` changes the port. The server
accepts loopback hosts only. `--title` supplies the exact heading and tab title;
its default is the input filename stem. `--language` overrides automatic language
and script detection. Each invocation handles one language, without a language
selector. Cross-script and dual-review workflows are outside this first version.

## Files

- `--infile` / `-i`: original subtitle input, always read-only.
- `--outfile` / `-o`: required SRT output. If present, it is resumed; otherwise,
  the app starts with original text or corrections from the optional JSON. Saving
  a row writes the complete SRT with the original counts and timings.
- `--json`: optional **read/write native proofreading decision JSON**. Existing
  sparse answers supply proposed wording and revision notes. A missing file is
  created on the first save. Without this option, manual editing and output SRT
  saving still work. This is not a manifest or a new editor-specific JSON format.
- `--audit-notes`: optional existing Markdown report whose Notes seed independent
  audit findings. This file remains read-only and is never required.

The input path should point at the actual validated OCR output, not a separate
manual snapshot. The editor retains its last published OCR baseline in the SQLite
sidecar so restarting after an OCR correction preserves existing decisions and
verification. A changed input is shown in the header; Re-proofread reloads its
current contents. The app never modifies that source file.

Input, output, JSON, progress and report paths must be distinct. Existing output
and native JSON must agree. Merely opening the app does not write the output SRT
or create/change the native decision JSON. Model calls start only when a user
submits a proofreading or auditing operation.

## Editing

Original and proofread text appear in stacked labeled rows. The diff uses the
CLI pairwise alignment and change colors: matches in the normal text color, substitutions purple, deletions
red, and insertions blue. **Proofread** is directly editable in its comparison
line, with an outline on hover or focus. **Note** appears below it when the draft
differs from Original; autosave writes the text and native revision note. Both start and end timestamps include milliseconds. Restoring the original text removes its
sparse JSON revision. Saving a changed native answer clears that case's verified
and few-shot flags; unrelated and historical cases, and every existing query,
are preserved. New manual decisions use immutable original pause-block queries.

A native query can occur more than once. The app lists the linked subtitle indexes
before editing; changing its wording or revision note updates those occurrences
consistently. The affected forms and versions update together. Unrelated editable
forms remain in place during HTMX saves.

Audit notes, findings, and the **Verified** checkbox remain separate from native
case verification. Verified means the audit finding was checked; it can accompany
an incorrect proposal. It does not silently approve an entire multi-subtitle JSON
case. Editing linked text resets other changed occurrences to Unaudited, clears
their obsolete audit notes, and clears independent verification.

Audit status uses an explicit enum: Unaudited, Review, and OK. Previous Incorrect
and Needs checking statuses migrate to Review; Unassessed migrates to Unaudited.
Existing notes and human verification are retained. Old filter bookmarks continue
to work. Legacy Markdown notes are imported at the boundary, including Review;,
Incorrect;, and Check; prefixes as Review.

Filter by verification, changed/unchanged text, audit status, or Unicode search.
Dropdowns update immediately; changed search text waits for a 750 ms typing pause.
Enter submits immediately, and the funnel icon clears all filters. URLs preserve filters; later block batches append as you scroll. Each
status option includes a count adjusted for the other filters and search. Search
also accepts `block 27` to select one original block. The `--json` file remains
the native decision log; independent findings remain in the SQLite sidecar.

## Blocks and navigation

Outer cards group subtitles into numbered proofreading blocks, collapsed by default.
The native summary header uses Block N at left, count/time centered in the border,
and a boxed plus/minus disclosure icon at right. Clicking the header, including
the subtitle count and time, toggles the block. The Block N link navigates to a view
filtered to that block. CSS places the header on the card border; no JavaScript swaps, initializes,
or replaces the individual accordion control. Existing JSON query
boundaries determine groups; overlapping queries are kept together. Rows without
logged queries use the original three-second pause boundaries. The first five matching blocks render initially, collapsed. Additional complete
blocks append through an HTMX intersection marker as you scroll. Filtering retains original block numbers and
visible/total counts. Row saves update only affected rows and block summaries,
preserving other drafts and disclosure states. Filtered block removals also preserve
newer drafts within that block until they can be saved. Stable source-block cursors keep later saves within the already-loaded prefix.
An icon-only Load more button and ordinary saves remain available without scripts.


The three equal-width dropdowns span the same width as the search field beneath
them. The search button is hidden once live search is initialized; it remains available
for ordinary form submissions without JavaScript.

## Persistence and conflicts

Independent progress and edit versions live beside the output as
`<output-stem>.review.sqlite3`. Keep that file with the output to resume notes and
verification. Source identities include the original file contents and subtitle
position; external changes to saved text invalidate obsolete independent approvals.

Stale form submissions are rejected. External output or JSON changes require a restart before saving. A changed OCR
input instead requires Re-proofread; source edits during a run prevent publication.
Reloaded input must retain subtitle counts and timings. File writes use atomic replacement;
if a write fails, already replaced outputs are restored and progress is not
committed. Ordinary I/O failures are reported in the page.

The domain-owned `static/audit-review.css` groups nested rules by component.
Individual pinned SVGs live under `static/icons/` and are referenced with `use`;
licenses ship beside them. Shared HTMX remains under `web/static/`.
Status filters and subtitle footers share icon-and-text options. As in aXYom32,
native customizable selects use `appearance: base-select` and `selectedcontent`;
browsers without that enhancement retain ordinary text selects. No JavaScript
is needed to render, select, or update dropdown icons.


The small `static/audit-review.js` script enhances draft presentation, live
Changed/Unchanged text, and conditional revision notes. Native disclosures,
verification, and audit-note validation remain available without JavaScript. The baseline
renders normal editable text with revision notes available, even if enhancement
fails to load; enhanced idle rows show the CLI-compatible colored diff overlay.
HTMX fragments and history restores reinitialize enhancements safely. Ordinary
GET/POST forms remain available without scripts.

The optional Collapse all / Expand all icon sits at the right of the operations toolbar. It
changes loaded native details elements, retaining drafts, and reflects
individual disclosure changes and subsequent HTMX updates. It is hidden without
JavaScript; individual summary controls remain usable. Its small delegated
handler is presentation-only and does not save or fetch data. HTMX preserves
the button across workspace swaps; CSS derives its visibility and icon from the
loaded native disclosure states instead of hiding it during every refresh.

Loaded subtitles remain in the DOM. CSS content-visibility defers off-screen
rendering, and unchanged text skips pairwise alignment. Bulk collapse pauses the
loader until a block is expanded, avoiding immediate loading caused by collapse.
The boxed plus/minus icons share a fixed grid slot and use visibility instead of
changing display modes, so their positions remain identical.

## Autosave and validation

With enhancement enabled, textarea blur and audit/verification control changes
save through HTMX. The footer shows a noninteractive icon-and-text status aligned
with the neighboring controls, with a fixed width for Saved/Saving/Unsaved/Invalid/
Error labels: green check for saved, rotating sync for saving, disk for an unsaved
valid draft, and red warning for invalid input or a failed save. The tooltip and
accessible name explain the state. An ordinary Save button remains available
when scripts or HTMX are unavailable.

Text differing from the original requires a nonblank proofreading Note. Browser
constraints highlight incomplete text/note pairs and block submission; server
validation independently rejects them before any writes. Unchanged text does not
require a Note. Review requires a nonblank Audit note, and OK requires an empty
Audit note. Invalid pairs cannot save or be bulk verified. Existing audit notes
remain visible until cleared. Verification remains independent audit progress in the SQLite
sidecar, while proofreading text and Note update the output SRT/native JSON.

Autosave acknowledges with the new version, diff display, and counts instead of
replacing editable fields. Per-form weak state records the submitted snapshot;
newer typing stays intact, and another blur during an active save coalesces into
a subsequent valid save. Failed requests retain drafts and show an error state;
focusing and leaving a text field retries the save.
Shared-decision updates do not replace newer drafts in related rows. Stale or
external changes remain conflicts; an error never becomes a green saved check.

## Proofreading and auditing operations

Both settings panels are nested in the operations toolbar and hidden initially.
The operation buttons independently show or hide them, using ordinary GET forms
with HTMX enhancement. Missing proofreading output produces a **Proofread** button;
existing output produces **Re-proofread**. Missing audit findings similarly produce
**Audit**; any persisted findings produce **Re-audit**. Auditing requires the
proofread subtitle output to exist. Panels can still be opened and configured while
the other operation runs; only their Run buttons are disabled until it finishes.

Each panel offers a registered provider, a free-text model identifier, and shared
reasoning-effort levels. Blank fields retain provider defaults; the app does not
discover model catalogs. First runs start immediately. Replacing existing results
requires three clicks: the first prepares the action, the second starts a
three-second cooling-off period, and the final click starts the job. The server
independently enforces the delay and binds confirmation to the selected settings.
Changing settings resets confirmation. Icons progress from play to red single-
and double-alert variants; tooltips retain the step descriptions.

Jobs use Scinoephile's Python APIs directly in background workers. Clock overlays
identify running jobs. HTMX checks progress every five seconds, including when a
running panel is hidden, and refreshes the workspace on completion or failure.
Ordinary page reloads provide the same progress without JavaScript. Conflicting
workers and subtitle edits are blocked while an operation runs. Unsaved subtitle
drafts must be saved before starting an operation or replacing the workspace.

Proofreading reads the configured OCR file afresh when each run starts. Completed
output and its source baseline are published atomically; failed runs retain the
previous output and review progress. Matching provider, model, reasoning, prompt,
examples, and schemas allow unchanged authored block decisions to be reused.
Other blocks use the normal configuration-aware response cache; reruns do not
force cache replacement. One changed subtitle generally needs only its context
block, provided the rest of the request configuration still matches.

Re-proofreading backs up the previous SRT, native decision JSON, and SQLite state
before publication. Source-row identities migrate with the baseline so untouched
rows retain findings and verification. Rows whose original text, proofread text,
or revision note changes become unaudited and unverified. Successful run settings
and project-specific proofreading context persist in the sidecar for the next run.

Auditing compares original and current proofread text in full context blocks. It
stores explicit Review/OK findings and notes independently of the proofreading
JSON. Completed blocks persist as they finish. Re-audit processes the whole saved
file through the shared response cache, preserving subtitle text, proofreading
notes, and human verification. Matching block inputs, provider settings, and
prompts reuse cached results; only cache misses make new requests. Failed blocks
retain their previous findings.

**Verify All Visible** uses two clicks: the first turns the button yellow without
changing progress; the second verifies every row matching the current filters,
including matching rows not yet loaded by infinite scrolling. There is no delay.
Changing filters or saving a subtitle resets the confirmation. Both clicks work
with HTMX or ordinary forms. A signed selection token and
row versions reject stale bulk operations; invalid audit-note pairs cannot be
silently marked verified.
