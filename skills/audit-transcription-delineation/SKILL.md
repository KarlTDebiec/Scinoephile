---
name: audit-transcription-delineation
description: Audit Scinoephile pairwise or sparse windowed block transcription delineation JSON by matching its guides to SRT indexes and judging whether fixed target text is assigned to the right subtitles. Use when inspecting delineation-*.json, block_delineation-*.json, legacy mps.json or cuda.json, correcting boundary decisions, or verifying cases. Do not assess transcription accuracy.
---

# Audit Transcription Delineation

Run commands from the repository root. A delineation audit assesses whether
target text was divided appropriately across adjacent guide subtitles. The same
CLI automatically recognizes legacy pairwise JSON, complete sparse block JSON,
and overlapping sparse block windows. Treat
the provided target text as fixed input, even when it appears incorrect. Do not
assess or comment on transcription accuracy, punctuation, wording, or character
choice; those are reviewed later in a separate workflow.

## Required report file

Always save the complete six-column Markdown report under `local/`. After
auditing every row, add each concise audit judgment directly to that file's
`Notes` cell. Do not leave notes only in commentary, tool output, or the final
response.

- Keep the table at exactly these columns: `Indexes`, `Reference`, `Input`,
  `Output`, `Notes`, and `Verified`.
- Delineation JSON has no note field, so generated `Notes` cells begin blank.
  If a future schema populates one, read it as context and replace the entire
  cell with your own independent judgment; never append to or merely endorse
  generated note content.
- Preserve the generated `Verified` cell: `✓` means the JSON test case is
  verified, and an empty cell means it is not verified. Each block-window row
  is one complete JSON case, so its marker maps directly to that case.
- Do not add a separate findings section; keep each observation beside the row
  it describes.
- Validate the saved report after adding notes, then provide a clickable link
  to it in the final response. Do not paste the table inline unless the user
  explicitly requests it.

## Protect source data

- Never edit files under `test/data/<dataset>/input/`.
- For an audit-only request, do not edit delineation JSON, guide subtitles,
  transcription output, or validation sources.
- When corrections are requested, apply model-answer corrections to the
  relevant delineation JSON and regenerate downstream outputs.
- Treat guide or transcription-source corrections as separate changes and make
  them only when the user explicitly requests them.

## Locate artifacts

Find the exact guide SRT used during transcription and the logged delineation
JSON. Do not substitute a similarly named subtitle track. Current workflows may
use flat names such as `delineation-<provider>.json` or
`block_delineation-<provider>.json`; older workflows may use provider names such
as `delineation/mps.json` or `delineation/cuda.json`.

The guide SRT is required because delineation JSON stores guide text but not
global subtitle numbers. The CLI matches each pair or complete window sequence
to consecutive guide subtitles and rejects absent or ambiguous matches rather
than displaying misleading indexes. It auto-detects the JSON shape; do not pass
an implementation-mode option or use a separate command for block JSON.

An official target-language subtitle track may be consulted only to determine
which utterance owns text near a boundary. It is not an input to the CLI and
does not belong in the report as a separate column. Never use it to evaluate or
comment on the accuracy of the target transcription.

## Generate the report

Always set `UV_CACHE_DIR=/tmp/uv-cache`:

```shell
UV_CACHE_DIR=/tmp/uv-cache uv run scinoephile audit delineation \
  --reference <guide.srt> \
  --json <delineation.json> \
  --first-index <first> \
  --last-index <last> \
  --filter all \
  --outfile local/<dataset>_delineation_audit_<first>-<last>.md \
  --overwrite
```

On PowerShell, configure UTF-8 as directed by the repository `AGENTS.md` before
printing subtitles.

The index bounds are inclusive. Pairwise cases are retained only when both
subtitles are contained in the requested range. Legacy complete-block cases are
retained only when their complete guide sequence is contained in the range.
Windowed cases are retained when their complete owned range is contained; their
displayed context may extend outside the requested range. Omit either bound for
an open-ended range. The default `--filter all` includes changed,
unchanged, and unanswered cases; use `--filter changes` to show only answers
that moved text, or `--filter unverified` when continuing verification of a
partly audited file. A complete audit must use `all`, because `changes` cannot
reveal missed shifts. The report summary labels these bounds as the reference
subtitle range.

Use `--first-block` and `--last-block` for an inclusive, one-based range of
reference blocks. A boundary is included only when both reference subtitles
belong to selected blocks. Block and subtitle bounds are mutually exclusive.
Omit either block bound for an open-ended range.

Pairwise rows stack the first and second subtitle with `<br>`. Block rows show
the JSON case number and global reference range in `Indexes`, then show every
guide and preliminary target with its one-based local JSON index. Window rows
also show `Owns boundaries after refs ...`; local lines are marked
`[owns next boundary]` or `[context]`. The ownership fields persisted in JSON
are inclusive local `first_owned_index` and `last_owned_index` values. A block
Output cell lists only the sparse replacement indexes; mentally overlay those
replacements on Input to assess the reconstructed window. A blank line is
displayed as `—`. Rows are sorted by matched reference indexes. Preserve the
original log order among repeated pairwise cases because they may record
successive decisions. In pairwise JSON, an empty answer (`{}`) means no boundary
shift. In block JSON, an empty `changes` list means the complete preliminary
assignment was retained. In either case, unchanged rows have a blank Output
cell.

## Audit every row

Read the saved report from beginning to end and judge every row independently.
For pairwise rows, target characters may move across the displayed boundary.
For complete-block rows, target characters may move among any indexed subtitles
in the case. For window rows, judge every boundary following an owned index;
context exists only to make those edge decisions intelligible. Sparse changes
may include a context index when moving the final owned boundary requires
changing both sides. Their complete window concatenation must remain unchanged.
Do not flag a context boundary that the window does not own; another overlapping
case owns it. Assess whether the output divides the target speech more faithfully
among the meanings and
utterances represented by the guide subtitles.

Judge only alignment. Ignore misspellings, mistranscriptions, Mandarinisms,
punctuation, omissions, repetitions, and other defects in the target text except
as fixed evidence for deciding which side of the boundary owns each phrase. Do
not mention these defects in Notes. Write exactly `OK` when the shift or no-shift
answer is appropriate.

Use semantic and discourse alignment rather than literal word matching:

- Keep a phrase together when splitting it would damage its meaning or grammar.
- Do not move a Cantonese sentence-final particle solely because the guide lacks
  an equivalent token; attach it to the utterance it pragmatically completes.
- Treat vocatives, discourse markers, repetitions, and other speech absent from
  the guide according to their role in the target-language dialogue.
- Accept a no-shift answer when the input division is already the best available
  alignment; a change is not required merely because the two languages segment
  an idea differently.
- Flag a shift that makes alignment worse, and flag a no-shift answer when a
  clear phrase belongs in another guide subtitle.

Classify alignment notes precisely:

- **Delineation error:** the model chose the wrong boundary or failed to shift a
  clearly misplaced phrase.
- **Uncertain:** the appropriateness of the boundary cannot be determined from
  the provided target text, guide pair, and available context.

After reviewing every row, replace every saved report `Notes` cell with `OK` or
an alignment finding. Begin each finding with `Delineation error;` or
`Uncertain;`, followed by a concise explanation focused only on boundary
ownership. Never mark an unanswered row `OK`. Validate that the edited file
retains every generated row and the exact six-column shape. Do not claim the
audit is complete until every row has been reviewed, all notes have been written
to the saved report, and its link is ready for the final response.

## Correct and verify cases

When the user requests corrections, update the delineation JSON answer rather
than a generated SRT:

- Correct the boundary output before marking the case verified.
- For pairwise JSON, edit `output_one` and `output_two` as needed.
- For block JSON, keep `answer.changes` sparse: include only indexes whose text
  differs from the query target, use the full replacement text for each listed
  index, and remove entries that no longer change anything. A window correction
  may include context only when needed to express an owned edge boundary. The
  concatenation of all reconstructed window outputs must preserve every original
  target character in exactly the same order.
- Mark a case `verified: true` only after auditing the entire pairwise case,
  complete block, or every owned boundary in a window and correcting its answer
  where necessary.
- Leave unanswered, unaudited, or partially audited cases unverified. Do not
  treat an empty no-shift answer as unanswered; only a missing answer is
  unanswered.

After corrections, regenerate the transcription output and downstream
artifacts through the dataset workflow. Rerun the audit over the corrected
range, confirm the JSON remains canonical, and confirm corrected cases no
longer appear with `--filter unverified` before linking the complete interpreted
report.
