# Instructions

Review [docs/STYLE.md](/docs/STYLE.md) before planning or coding.

## Code

* Review [docs/ARCHITECTURE.md](/docs/ARCHITECTURE.md) for package boundaries,
  dependency direction, and how the CLI maps onto `core` and domain modules.
* Review [docs/STYLE.md](/docs/STYLE.md) for code style and documentation
  conventions (docstrings, typing, `__all__`, etc.).

## Tools

* This repository uses a virtual environment. To activate the venv in your
  shell, run `source .venv/bin/activate`.
* This repository uses `uv`. Use `UV_CACHE_DIR=/tmp/uv-cache uv run` when
  executing tools.

### Windows / PowerShell

* The examples above use Unix-style environment variable prefixes. In
  PowerShell, set environment variables before running `uv`:
  ```powershell
  $env:UV_CACHE_DIR = "/tmp/uv-cache"
  uv run pytest
  ```
* Before running commands that may print subtitles, CJK text, or other non-ASCII
  output, configure PowerShell and Python for UTF-8:
  ```powershell
  [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
  $OutputEncoding = [System.Text.UTF8Encoding]::new()
  $env:PYTHONUTF8 = "1"
  $env:PYTHONIOENCODING = "utf-8"
  ```
* Combine those settings when running repository tools that may emit subtitle
  text:
  ```powershell
  $env:UV_CACHE_DIR = "/tmp/uv-cache"
  $env:PYTHONUTF8 = "1"
  $env:PYTHONIOENCODING = "utf-8"
  uv run python ...
  ```

### Version Control

* Branches should be named in the format `feature/brief-description`.
* Interact with GitHub using the GitHub MCP; do not use the `gh` CLI.

### Linting

* Before running `ruff` or `ty`, reread [docs/STYLE.md](/docs/STYLE.md) and
  check changed files for compliance.
* Run the following checks on **only the Python files you have changed or been
  asked to**:
  1. `uv run ruff format`
  2. `uv run ruff check --fix`
  3. `uv run ty check`
* If `ruff` or `ty` suggest changes that would require major refactoring,
  confirm with the user before proceeding.

### Testing

* Run the tests as follows:
  * `cd test && UV_CACHE_DIR=/tmp/uv-cache uv run pytest -n auto`
* To reproduce order-sensitive failures, run tests serially:
  * `cd test && UV_CACHE_DIR=/tmp/uv-cache uv run pytest`
* You may run pytest with a timeout of up to 10 minutes without asking the user.
