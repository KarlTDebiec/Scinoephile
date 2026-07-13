# Architecture

This document describes Scinoephile’s package boundaries, dependency direction,
and how the command-line interface maps onto the core implementation.

## Package layering (dependency direction)

Scinoephile documents the intended package hierarchy in
`scinoephile/__init__.py`. Modules may import from packages listed above them in
that hierarchy. The hierarchy block in that file is authoritative; the list
below describes package responsibilities in the same order:

- `scinoephile.common`: general-purpose utilities; may not import from other
  Scinoephile packages
- `scinoephile.core`: core subtitle-domain logic; may import from `common`
- `analysis`, `image`, and `llms`: domain packages that may import from `common`
  and `core`
- `scinoephile.media`: media tooling built on the lower layers
- `scinoephile.lang`: language-specific subtitle operations that may import from
  the packages above
- `audio`, `dictionaries`, and `web`: audio, dictionary, and web UI packages
  that may import from the packages above
- `multilang`: cross-language operations that may import from the packages above
- `optimization`: prompt optimization infrastructure that may import from the
  packages above
- `workflows`: reusable workflow orchestration that may import from the packages
  above, including `optimization`
- `scinoephile.cli`: user-facing command-line wrappers that may import from any
  package listed above it

This layering is enforced automatically by `test/test_module_hierarchy.py` and
through code review. It is intended to keep dependencies flowing toward earlier
layers:

- **`common`**: utilities shared everywhere; should remain dependency-free
  within the `scinoephile` package.
- **`core`**: stable, domain-oriented primitives (series loading/saving, timing,
  synchronization, shared CLI helpers); may import `common` but should avoid
  importing mid-layer domain packages.
- **`analysis`, `image`, and `llms`**: specialized functionality that builds on
  `core`:
  - **`analysis`**: metrics and comparisons (for example CER and diffing).
  - **`image`**: image/OCR representations and helpers.
  - **`llms`**: prompt definitions, providers, and model-facing processing
    utilities.
- **`media`**: media-file probing, subtitle extraction helpers, subtitle cache
  analysis, and visual offset estimation.
- **`lang`**: language-specific subtitle operations (English, standard Chinese,
  written Cantonese, etc.).
- **`audio`, `dictionaries`, and `web`**: audio representation and transcription
  tooling, dictionary lookup/build logic, and web interfaces.
- **`multilang`**: pair-specific cross-language operations.
- **`optimization`**: prompt optimization operations and prompt and test-case
  persistence built on the preceding domain packages.
- **`workflows`**: reusable end-to-end orchestration that coordinates multiple
  domain packages, including `multilang` and `optimization`.
- **`cli`**: thin wrappers around lower layers; argument parsing, validation,
  and user-facing orchestration.

### `__init__.py` files document local hierarchy

In addition to the top-level hierarchy in `scinoephile/__init__.py`, each
package’s `__init__.py` is the source of truth for its **internal hierarchy**.
Every package containing child modules or packages must list each child exactly
once. Each bullet is a dependency level: entries separated by `/` are independent
peers, and a child may import only from children on earlier bullets. Sibling import
cycles are prohibited.

Declared levels express architectural policy rather than a compact description of
the imports that happen to exist today. A child may remain on a later level even
when it does not currently import from an earlier level. Removing an import does
not require rearranging the hierarchy, and adding an import does not authorize
rearranging it. Hierarchy changes are deliberate architectural changes and should
be explained explicitly during review.

`test/test_module_hierarchy.py` verifies that declarations are complete, rejects
duplicate or unknown children, and rejects imports that violate the declared
direction. It also enforces import forms that keep those dependencies visible:
same-directory modules use relative imports, imports across directories use
absolute concrete paths, package-facade imports name public exports, and modules
do not reach internal siblings through their own ancestor package facades. The
declarations serve two purposes:

- **Documentation**: a fast, local reference for where new code should live.
- **Dependency hygiene**: an enforced boundary that prevents sibling dependency
  cycles and upward imports.

### Immutable prompt values

Operation-specific prompt types in `scinoephile.llms` are frozen, keyword-only
dataclasses defining behavior and named correspondence fields for review,
translation, OCR fusion, and the other LLM shapes. Authored and localized
prompts construct those types directly with a `Language` and string fields. LLM
managers, processors, queryers, and workflows pass these values directly.
Authored prompts may reuse typed language-specific field dictionaries while
keeping their language and operation-specific fields explicit.

Operation-specific Pydantic query, answer, and test-case models define stable
structural fields. When JSON field names are part of LLM correspondence, managers
generate and cache prompt-specific subclasses whose aliases and descriptions come
from the immutable prompt value. List-shaped operations represent variable
cardinality in model data, such as indexed subtitle lists, rather than in generated
class fields. The prompt's stable content-addressed name is used in generated model
names.

LLM providers require a structured answer model for every completion. The provider's
structured response format is the authoritative answer schema; system prompts do not
duplicate that schema as text.

Optimization persistence stores each prompt alias with its content-addressed
identifier, language, and complete set of string fields. Prompt and test-case
SQLite stores own and create their tables independently. Model persistence uses
immutable, content-addressed rows containing the provider, resolved model name,
effective base URL, and non-secret inference settings. Credentials and provider
client state are excluded. All table groups may coexist in one SQLite file
without a global schema version or migration contract.

## Command Line Interface

The entrypoint configured in `pyproject.toml` is:

- `scinoephile = scinoephile.cli.scinoephile_cli:ScinoephileCli.main`

`ScinoephileCli` is an `argparse`-based top-level dispatcher that selects a
subcommand and forwards arguments to the corresponding CLI class.

### Full CLI surface

The CLI is organized as a tree of `argparse` subparsers. The complete command
surface (commands and subcommands) is:

- `scinoephile`
  - `audit`: audit subtitle review workflows
    - `review`: audit one review with automatic language and script detection
    - `review-trad`: audit traditional review followed by review of its
      simplified form
    - `review-dual`: audit parallel simplified and traditional-to-simplified
      review paths and their final discrepancy
  - `dictionary`
    - `build`
      - `cuhk`: build CUHK dictionary cache
      - `gzzj`: build GZZJ dictionary cache
      - `kaifangcidian`: build Kaifangcidian dictionary cache
      - `unihan`: build Unihan dictionary cache
      - `wiktionary`: build Wiktionary dictionary cache
    - `search`: search one or more configured dictionaries
  - `media`
    - `extract-subs`: extract matching subtitle streams from a video file
    - `offset`: estimate visual offset between two media files
    - `probe`: list media streams in a media file
  - `multi`
    - `cer`: calculate character error rate (CER) for one series relative to
      another
    - `diff`: calculate the diff between two series
    - `stack`: stack two series into top and bottom subtitle lines
    - `sync`: estimate subtitle offset and shift a mobile series to an anchor
      series
    - `timewarp`: shift/stretch timings of one series to match another
  - `ocr`
    - `fuse`: fuse OCR output for a selected language
    - `lens`: recognize image subtitles with Google Lens
    - `paddle`: recognize image subtitles with PaddleOCR
    - `process`: process image subtitle OCR and fuse output for a selected
      language
    - `tesseract`: recognize image subtitles with Tesseract OCR
    - `validate`: validate OCR text against subtitle images
  - `process`: process subtitles (clean/convert/flatten/romanize/offset)
  - `proofread`: review one subtitle series, review it pairwise against a
    reference series, or review it in blocks using a guide series
  - `utility`
    - `cache`
      - `clear`: remove cached files
      - `list`: list cached files
      - `prune`: remove stale cached files
      - `stats`: inspect cache size and entry counts
    - `optimization`
      - `sync-prompts`: synchronize registered prompts
      - `sync-test-cases`: synchronize persisted prompt-optimization test cases
  - `translate`: translate subtitles between supported languages
  - `yue`
    - `transcribe-vs-zho`: transcribe from media audio using standard Chinese
      as reference

Each subcommand lives under `scinoephile/cli/` and is responsible for:

- Defining its argument parser
- Validating inputs and outputs
- Calling into the appropriate `core` and domain-layer modules to do the real
  work
