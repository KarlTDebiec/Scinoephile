# Contributing

## Branches

Name branches `feature/brief-description`. Continue the existing branch when
requested. The remote is `github`; target pull requests at `master`. Keep unrelated
working-tree changes out of commits and pull requests.

Interact with GitHub through the GitHub MCP; do not use `gh`.

## CI usage

Batch related changes, validate locally, and push when ready for review. Do not
push each small edit or use Actions as the primary edit/test loop; cancelled runs
still consume runner time. Use remote CI to confirm platform behavior and
investigate failures that cannot be reproduced locally.

Use `uv run` for repository tools and follow the
[validation guidance](../AGENTS.md) before pushing. Keep tests requiring
serial execution serial.

The [workflow files](../.github/workflows/) own exact triggers, commands,
dependencies, and tool versions. Pull requests targeting `master` and pushes to
`master` run Linux checks. Newer updates cancel older runs for the same Git ref.
GitHub checks provide routine validation results. Mention validation gaps or
platform limitations in PR Notes only when they materially affect review.

## Pull requests

Keep descriptions concise. Use these sections:

```markdown
## Background

The current problem or constraint, stated in the present tense.

## Changes

- What the change does, stated in the present tense.

## Notes

Optional: a non-obvious choice, implementation limitation, or separate issue.
```

Write for reviewers without prior context. Use present tense in both Background
and Changes:

- Background describes the current problem or constraint: "Checkpoint writes leave
  partial files when a runner fails."
- Changes describes the resulting behavior: "Writes checkpoints to temporary files
  before replacing the destination."

Each Changes bullet identifies the affected area and its concrete result.
Describe the final implementation and omit chat history or a work log. Notes
covers non-obvious choices, material limitations, or architectural decisions;
omit Notes when there is nothing to add.

Keep routine validation out of the description. Do not list executed commands,
passing checks, test counts, or statements that tests, Ruff, ty, or CI pass.
Required checks still run; their results belong in GitHub checks. Do not add a
Testing or Validation section or append a validation checklist to Notes. Describe
new regression coverage by the behavior it protects when that helps explain the
change, rather than reporting that the tests run. Mention a validation gap only
when it leaves relevant behavior unverified and materially affects review.

Attach related issues separately from the description. Closing keywords are not
required.
