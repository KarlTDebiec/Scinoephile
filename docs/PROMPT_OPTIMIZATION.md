# Prompt optimization and persistence

This document records the data-model and persistence decisions used by prompt
optimization without expanding the high-level architecture overview.

## Prompt values

Operation-specific prompt types in `scinoephile.llms` are frozen, keyword-only
dataclasses. They define behavior and named correspondence fields for review,
translation, OCR fusion, and other LLM operations. Authored and localized prompts
construct these types directly with a language and explicit string fields. LLM
managers, processors, queryers, and workflows pass the immutable values directly.

Authored prompts may reuse typed language-specific field dictionaries while
keeping language and operation-specific fields explicit. Each prompt has a stable
content-addressed name.

## Catalog composition

Prompt-owning modules in `lang` and `multilang` expose their defaults through
read-only `DEFAULT_PROMPTS` mappings. The application catalog in
`workflows.prompt_catalog` assigns stable aliases and pairs each prompt with the
manager defining its operation. It rejects duplicate aliases during composition.

The `optimization` package owns the prompt specification, supported-operation
registry, and persistence operations. Callers pass an application catalog into
those operations; the package does not discover or import concrete domain prompts.

## Structured models

Operation-specific Pydantic query, answer, and test-case models define stable
structural fields. When JSON field names are part of LLM correspondence, managers
generate and cache prompt-specific subclasses whose aliases and descriptions come
from the prompt value. List-shaped operations represent variable cardinality in
model data rather than generated class fields. Generated model names include the
prompt's content-addressed name.

LLM providers require a structured answer model for every completion. The
provider's structured response format is the authoritative answer schema; system
prompts do not duplicate that schema as text.

## Persistence

Optimization persistence stores each prompt alias with its content-addressed
identifier, language, and complete set of string fields. Prompt and test-case
SQLite stores own and create their tables independently.

Model persistence uses immutable, content-addressed rows containing the provider,
resolved model name, effective base URL, and non-secret inference settings.
Credentials and provider client state are excluded. All table groups may coexist
in one SQLite file without a global schema version or migration contract.
