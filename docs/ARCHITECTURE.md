# Architecture

This document describes Scinoephile’s package boundaries, dependency direction, and
how the command-line interface maps onto the core implementation.

## Package layering (dependency direction)

Scinoephile documents the intended package hierarchy in `scinoephile/__init__.py`.
Modules may import from packages listed above them in that hierarchy:

- `scinoephile.common`: general-purpose utilities; may not import from other Scinoephile packages
- `scinoephile.core`: core subtitle-domain logic; may import from `common`
- `analysis`, `image`, and `llms`: domain packages that may import from `common`
  and `core`
- `scinoephile.lang`: language-specific subtitle operations that may import from
  the packages above
- `audio` and `dictionaries`: audio and dictionary packages that may import from
  the packages above
- `scinoephile.multilang`: cross-language workflows that may import from the
  packages above
- `scinoephile.optimization`: prompt optimization tooling that may import from the
  packages above
- `scinoephile.cli`: user-facing command-line wrappers that may import from any
  lower package layer

This layering is enforced socially (by convention and code review) and is intended
to keep dependencies flowing toward earlier layers:

- **`common`**: utilities shared everywhere; should remain dependency-free within the
  `scinoephile` package.
- **`core`**: stable, domain-oriented primitives (series loading/saving, timing,
  synchronization, shared CLI helpers); may import `common` but should avoid importing
  mid-layer domain packages.
- **`analysis`, `image`, and `llms`**: specialized functionality that builds on
  `core`:
  - **`analysis`**: metrics and comparisons (for example CER and diffing).
  - **`image`**: image/OCR representations and helpers.
  - **`llms`**: prompt definitions, providers, and model-facing processing utilities.
- **`lang`**: language-specific subtitle operations (English, standard Chinese,
  written Cantonese, etc.).
- **`audio` and `dictionaries`**: audio extraction/representation, transcription
  tooling, and dictionary lookup/build logic.
- **`multilang`**: cross-language pipelines (for example Yue vs. Zho workflows)
  that coordinate multiple domain packages.
- **`optimization`**: prompt optimization operations and persisted test-case
  synchronization.
- **`cli`**: thin wrappers around lower layers; argument parsing, validation, and
  user-facing orchestration.

### `__init__.py` files document local hierarchy

In addition to the top-level hierarchy in `scinoephile/__init__.py`, each package’s
`__init__.py` documents its **internal hierarchy** using the same rule of thumb:
modules may import from modules listed “above” them in that package’s hierarchy
comment. This serves two purposes:

- **Documentation**: a fast, local reference for where new code should live.
- **Dependency hygiene**: a place to notice and resolve sibling dependency cycles
  (cycles should be called out explicitly and grouped together).

## Command Line Interface

The entrypoint configured in `pyproject.toml` is:

- `scinoephile = scinoephile.cli.scinoephile_cli:ScinoephileCli.main`

`ScinoephileCli` is an `argparse`-based top-level dispatcher that selects a
subcommand and forwards arguments to the corresponding CLI class.

### Full CLI surface

The CLI is organized as a tree of `argparse` subparsers. The complete command
surface (commands and subcommands) is:

- `scinoephile`
  - `analysis`
    - `cer`: character error rate (CER) analysis
    - `diff`: diff analysis between two subtitle series
  - `cache`
    - `clear`: remove cached files
    - `list`: list cached files
    - `prune`: remove stale cached files
    - `stats`: inspect cache size and entry counts
  - `dictionary`
    - `build`
      - `cuhk`: build CUHK dictionary cache
      - `gzzj`: build GZZJ dictionary cache
      - `kaifangcidian`: build Kaifangcidian dictionary cache
      - `unihan`: build Unihan dictionary cache
      - `wiktionary`: build Wiktionary dictionary cache
    - `search`: search one or more configured dictionaries
  - `eng`
    - `fuse`: fuse OCR output (Lens + Tesseract)
    - `process`: process English subtitles (clean/flatten/proofread)
    - `validate-ocr`: validate OCR text against subtitle images
  - `extract`: extract matching subtitle streams from media
  - `optimization`
    - `sync-test-cases`: synchronize persisted prompt-optimization test cases
  - `sync`: combine two series into a synchronized top/bottom series
  - `timewarp`: shift/stretch timings of one series to match another
  - `yue`
    - `process`: process written Cantonese subtitles (clean/convert/flatten/proofread/romanize)
    - `review-vs-zho`: review written Cantonese against standard Chinese
    - `transcribe-vs-zho`: transcribe from media audio using standard Chinese as reference
    - `translate-vs-zho`: translate missing Cantonese lines using standard Chinese as reference
  - `zho`
    - `fuse`: fuse OCR output (Lens + PaddleOCR)
    - `process`: process standard Chinese subtitles (clean/convert/flatten/proofread/romanize)
    - `validate-ocr`: validate OCR text against subtitle images

Each subcommand lives under `scinoephile/cli/` and is responsible for:

- Defining its argument parser
- Validating inputs and outputs
- Calling into the appropriate `core` and domain-layer modules to do the real work
