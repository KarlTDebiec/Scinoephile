# Architecture

This document describes Scinoephile’s package boundaries, dependency direction, and
how the command-line interface maps onto the core implementation.

## High-level goals
- Separate project-agnostic helpers (`scinoephile/common/`)
- Centralize core code and abstract details (`scinoephile/core/`)
- Separate functionality into appropriate domains (`lang`, `audio`, `image`, `dictionaries`, `multilang`, `llms`)
- Centralize user-facing command-line interface (`scinoephile/cli/`)

## Package layering (dependency direction)

Scinoephile enforces a simple “only import downward” rule. The intended hierarchy is
documented in `scinoephile/__init__.py` and can be summarized as:

- `scinoephile.common`: general-purpose utilities; may not import from other Scinoephile packages
- `scinoephile.core`: core subtitle-domain logic; may import from `common`
- Mid-layer domain packages: `analysis`, `image`, `llms`, `lang`, `audio`,
  `dictionaries`, `multilang`; these build on `core` (and `common`)
- `scinoephile.cli`: user-facing command-line wrappers; may import from any lower
  layer

This structure keeps reusable components testable and prevents the CLI from becoming
an accidental “god layer”.

## CLI architecture

The entrypoint configured in `pyproject.toml` is:

- `scinoephile = scinoephile.cli.scinoephile_cli:ScinoephileCli.main`

`ScinoephileCli` is an `argparse`-based top-level dispatcher that selects a
subcommand and forwards arguments to the corresponding CLI class.

Top-level subcommands currently include:

- `analysis`
- `dictionary`
- `eng`
- `sync`
- `timewarp`
- `yue`
- `zho`

Each subcommand lives under `scinoephile/cli/` and is responsible for:

- Defining its argument parser
- Validating inputs and outputs
- Calling into the appropriate `core` and domain-layer modules to do the real work

## Localization

CLI help text localization is implemented in `scinoephile/core/cli/ScinoephileCliBase`.
At runtime, the active locale is resolved from environment/system settings, and
parser text is translated for supported locales (currently `zh-hans` and `zh-hant`).

This localization layer is intentionally scoped to CLI text; it does not attempt to
translate internal object names or identifiers.

