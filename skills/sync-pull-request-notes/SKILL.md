---
name: sync-pull-request-notes
description: Sync Scinoephile's local/_pull_requests.md map with the repository's open and draft GitHub pull requests while removing merged and closed PRs from both the Mermaid graph and table. Use when asked to refresh, reconcile, or update the local pull-request map.
---

# Sync Pull Request Notes

Update `local/_pull_requests.md` from live GitHub data without discarding the
user's hand-maintained view of how the work was split.

## Active PR scope

The Mermaid graph and table are both views of active work. Include a PR only
when GitHub reports it as open, whether ready for review or draft. Remove merged
and closed PRs from both views; do not retain them as history.

## Sources of truth

GitHub is authoritative for:

- which pull requests are open, including drafts
- PR number, full title, URL, head branch, and draft/open state

The existing note is authoritative for:

- Mermaid ancestry between PRs
- concise Mermaid node labels
- the `Role in the stack` text
- the amount of prose and the overall Markdown structure

Do not recreate explanatory sections that the user removed. Do not modify any
pull request on GitHub; this workflow requires read-only GitHub access.

## Sync

1. Resolve the repository root and GitHub `owner/repository` from the checkout.
   Do not assume a particular local path or remote name.
2. Read `local/_pull_requests.md` before querying GitHub. If it is missing, create
   a minimal note containing `# Pull Requests`, a Mermaid `flowchart LR`, and the
   four-column PR table used below.
3. Use the available GitHub tooling to list every open pull request, including
   drafts. Follow pagination until the complete set is retrieved.
4. Sort PRs by number and reconcile the table to exactly that set:
   - render the state as `Draft` or `Open`
   - update the full linked title and head branch from GitHub
   - preserve an existing role by PR number
   - for a new PR, summarize its role only when the PR body makes it explicit;
     otherwise use `Not yet categorized.`
   - escape or encode Markdown table delimiters in every GitHub-derived cell
     value while preserving the displayed text; a `|` must not create a new cell
   - remove rows for PRs that are no longer open
5. Reconcile the Mermaid figure with the same open PR set:
   - keep surviving hand-authored edges and concise labels unchanged
   - remove nodes for PRs that are no longer open
   - when removing a parent, reconnect its surviving children to the nearest
     surviving ancestor; leave them as root nodes if none remains
   - distinguish conceptual lineage from the Git base branch; a focused PR may
     target `master` while still having been extracted from a larger PR
   - add a new PR beneath another open PR when its body explicitly declares that
     relationship with wording such as `Extracted from #123` or
     `Split from #123`; do not infer ancestry from an incidental PR-number
     mention
   - when the body declares no parent, add the PR beneath another open PR when
     its base branch is that PR's head branch; otherwise add it as a root node
   - include only PR nodes, with no base-branch nodes such as `master`
   - use node IDs in the form `pr<number>` and do not add labels to edges
6. Keep the diff minimal. The table links are sufficient; do not add Mermaid
   `click` directives or restore other deleted commentary.

Use this table shape when creating the file or adding missing structure:

```markdown
| PR | Branch | State | Role in the stack |
| --- | --- | --- | --- |
| [#123: Full title](https://github.com/owner/repository/pull/123) | `feature/example` | Open | Not yet categorized. |
```

## Verify

Before finishing, confirm that:

- the Mermaid figure and table contain the same PR numbers
- every open GitHub PR appears exactly once in each
- every table title, link, branch, and state matches GitHub
- every explicit parent relationship to an open PR is represented by an edge
- the Mermaid graph has no dangling PR nodes or edges
- `local/_pull_requests.md` remains local and untracked

Report which PRs were added, updated, or removed. Do not commit the local note.
