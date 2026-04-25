# Instructions

Review [docs/STYLE.md](/Users/karldebiec/Code/Scinoephile/docs/STYLE.md) before planning or coding.

## Tools

* This repository uses a virtual environment. To activate the venv in your shell: `source .venv/bin/activate`.
* This repository uses `uv`. Use `UV_CACHE_DIR=/tmp/uv-cache uv run` when executing tools.

### Version Control

* Branches should be named in the format `feature/brief-description`.
* Interact with GitHub using the GitHub MCP; do not use the `gh` CLI.

### Linting

* Before running `ruff` or `ty`, check changed files for compliance with [docs/STYLE.md](/Users/karldebiec/Code/Scinoephile/docs/STYLE.md).
* Run the following checks on **only the Python files you have changed or been asked to**:
  1. `uv run ruff format`
  2. `uv run ruff check --fix`
  3. `uv run ty check`
* If `ruff` or `ty` suggest changes that would require major refactoring, confirm with the user before proceeding.

### Testing

* Run the tests as follows:
  * `cd test && uv run pytest`
* You may run pytest with a timeout of up to 10 minutes without asking the user.
