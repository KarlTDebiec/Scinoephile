# Architecture

This document describes Scinoephile’s package boundaries, dependency direction, and
how the command-line interface maps onto the core implementation.

## Package layering (dependency direction)

Scinoephile enforces a simple “only import downward” rule. The intended hierarchy is
documented in `scinoephile/__init__.py` and can be summarized as:

- `scinoephile.common`: general-purpose utilities; may not import from other Scinoephile packages
- `scinoephile.core`: core subtitle-domain logic; may import from `common`
- Mid-layer domain packages: `analysis`, `image`, `llms`, `lang`, `audio`, `dictionaries`, `multilang`; these build on `core` and `common`
- `scinoephile.cli`: user-facing command-line wrappers; may import from any lower layer

This layering is enforced socially (by convention and code review) and is intended
to keep dependencies flowing in one direction:

- **`common`**: utilities shared everywhere; should remain dependency-free within the
  `scinoephile` package.
- **`core`**: stable, domain-oriented primitives (series loading/saving, timing,
  synchronization, shared CLI helpers); may import `common` but should avoid importing
  mid-layer domain packages.
- **Domain packages**: specialized functionality that builds on `core`:
  - **`analysis`**: metrics and comparisons (for example CER and diffing).
  - **`image`**: image/OCR representations and helpers.
  - **`llms`**: prompt definitions, providers, and model-facing processing utilities.
  - **`lang`**: language-specific subtitle operations (English, standard Chinese,
    written Cantonese, etc.).
  - **`audio`**: audio extraction/representation and transcription tooling.
  - **`dictionaries`**: dictionary services and lookup/build logic.
  - **`multilang`**: cross-language pipelines (for example Yue vs. Zho workflows) that
    coordinate multiple domain packages.
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
