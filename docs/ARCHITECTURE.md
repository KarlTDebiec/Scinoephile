# Architecture

This document describes Scinoephile's stable package boundaries and dependency
policy. It intentionally avoids duplicating source-controlled inventories such
as hierarchy order, CLI commands, and persistence schemas.

## Package hierarchy

The hierarchy block in
[`scinoephile/__init__.py`](../scinoephile/__init__.py) is the source of truth
for dependencies between top-level packages. Each package's `__init__.py` is the
source of truth for dependencies between its direct children.

Every direct child appears exactly once in its package's hierarchy. Each bullet
is a dependency level: entries separated by `/` are independent peers, and a
child may import only from children on earlier bullets. Sibling import cycles are
prohibited.

Declared levels express architectural policy, not a compact description of the
imports that happen to exist today. Removing an import does not require moving a
child earlier, and adding an import does not authorize moving it later. Hierarchy
changes are deliberate architectural changes and should be explained explicitly
during review.

[`test/test_module_hierarchy.py`](../test/test_module_hierarchy.py) verifies that
declarations are complete, rejects duplicate or unknown children, and enforces
dependency direction and import style. Detailed import syntax belongs in the
[`STYLE.md`](STYLE.md) guide rather than being repeated here.

## Package responsibilities

This table is alphabetical and does not encode dependency order; consult the
authoritative hierarchy declaration above for ordering.

| Package | Responsibility |
| --- | --- |
| `analysis` | Subtitle metrics, comparisons, alignment, and review auditing |
| `audio` | Audio representations, transcription, and audio-derived subtitles |
| `cli` | Argument parsing, localization, validation, and user-facing adapters |
| `common` | General-purpose utilities with no dependencies on other Scinoephile packages |
| `core` | Stable subtitle-domain primitives, timing, synchronization, caching, and shared CLI support |
| `dictionaries` | Dictionary lookup, parsing, and cache construction |
| `image` | Image subtitle representations, drawing, OCR, and OCR validation |
| `lang` | Language-specific subtitle operations |
| `llms` | Prompt types, providers, structured correspondence, and model-facing processing |
| `media` | Media probing, subtitle extraction, cache analysis, and visual offset estimation |
| `multilang` | Cross-language and language-pair operations |
| `optimization` | Prompt optimization contracts, operation registry, and persistence |
| `web` | Web interfaces for interactive operations |
| `workflows` | Reusable end-to-end orchestration and application composition |

## Public APIs and internal dependencies

Package `__init__.py` files may expose deliberate public facades through
`__all__`. External consumers may use those facades. Internal imports must keep
the concrete dependency visible according to the rules in `STYLE.md`, allowing
the hierarchy test to evaluate the real dependency graph.

## Command-line interface

The console entry point is declared in [`pyproject.toml`](../pyproject.toml).
`ScinoephileCli` dispatches to `argparse`-based command classes under
`scinoephile/cli/`; those classes define the authoritative command tree and help
text. CLI classes should parse and validate inputs, translate domain failures
for users, and delegate substantive work to lower packages.

## Focused design documents

Subsystem-specific design belongs in focused documents so this overview remains
stable:

- [Prompt optimization and persistence](PROMPT_OPTIMIZATION.md)
