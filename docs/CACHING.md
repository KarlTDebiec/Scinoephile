# Caching

This document defines Scinoephile's cache ownership, layout, identity, and
lifecycle conventions. Cache contents are disposable performance artifacts:
removing the entire cache must not destroy authored output, user decisions, or
other state that cannot be regenerated.

## Boundaries and ownership

Use the runtime cache root for reproducible artifacts such as model output,
downloaded resources, extracted media streams, and derived analysis. Use the
runtime data root for durable application state, including user-reviewed or
user-edited data.

`cache_root_path: Path | None` means the root beneath all cache namespaces.
`None` selects `get_runtime_cache_root_path()`; it does not disable caching.
Represent disabled persistence with an explicit option or a different cache
implementation.

A cache class owns storage mechanics: root and namespace resolution, stable
entry paths, validation, loading, saving, removal, recent-use tracking, and
overwrite behavior. The producer owns computation and external dependencies.
Extraction, network requests, model inference, parsing, and rendering do not
belong in cache classes.

Callers should use cache APIs instead of deriving paths or duplicating lifecycle
logic. An operation that owns a cache's lifetime may construct it from cache
configuration. A function that accepts a caller-supplied cache should not also
accept that cache's constructor arguments.

## Layout

Cache constructors place `cache_root_path` first, followed by cache-specific
configuration, with `overwrite: bool = False` last when supported. Use
`cache_root_path` for the shared root and `cache_dir_path` for a namespaced
directory. CLI `--cache-dir` values are cache roots.

Each cache uses a stable namespace that mirrors the package owning the produced
artifact; third-party model caches remain owned by their dependencies. Owners
declare namespaces in concrete `CacheNamespace` enums, and
`scinoephile.workflows.cache_registry.CACHE_REGISTRY` aggregates them for
application-wide inspection and clearing.

Namespace segments use Python module spelling, including underscores.
Parameterized LLM operation segments may instead use stable operation
identifiers such as `guided-review`. Materially different entry types use
separate leaf namespaces.

Each direct child of a namespace is one independently removable entry. A
directory entry may contain related files that must be kept or removed
together. Keep namespace names and entry boundaries stable so maintenance for
one cache cannot delete another cache's entries.

## Identity and versioning

An entry identity includes every input and configuration value that can change
the reusable result, such as source content or metadata, model identity,
language, preprocessing, and prompt content. Exclude credentials, transient
objects, and unstable representations.

Local inference identities include model identifiers and revisions plus
task-defining dependency versions. Track source dependency revisions when
pinned to a commit. Exclude general execution substrates when their upgrades
may introduce only acceptable numerical drift; retain dependencies that define
model loading, preprocessing, inference semantics, or postprocessing. Remote
services may use a local version for client-side behavior that cannot otherwise
be identified reproducibly.

Each cache implementation or cache-producing module that needs local
invalidation defines at most one private integer `_CACHE_VERSION` and includes
it in the serialized payload, identity hash, or operation identity. Increment
it whenever a storage or result-affecting implementation change makes older
entries unsafe to reuse. Prefer broad invalidation to separate versions for
individual processing stages. Versions remain local; there is no global cache
schema version.

## Lifecycle and safety

Cache APIs make hits, misses, and mutations explicit:

* `get_path(...)` derives an entry location.
* `load(...)` returns a validated value or path, or `None` for a miss.
* `save(...)` persists a complete value and returns its path.
* `remove(...)` returns the removed path, or `None` when no entry exists.

Treat unreadable, malformed, mismatched, or unsupported entries as misses:
remove them, log the reason, and allow regeneration. Successful loads update
the entry's modification timestamp so pruning reflects recent reuse. Use the
log verbs `Loaded`, `Saved`, `Removed`, and `Discarded invalid`; ordinary misses
need no log.

Overwrite mode converts each matching preexisting entry into a miss at most
once per cache instance. Track refreshed paths so values saved during an
operation can be reused. Do not clear an entire namespace for overwrite.

Writes should be atomic whenever practical. Stage them on the destination
filesystem and replace the destination only after the new artifact is complete.
Failed production or serialization must not leave a partial entry that can be
mistaken for a hit. Recursive removal must not follow symbolic links.

## CLI and maintenance

Cache-producing CLIs use the shared cache argument bundle and place
`--cache-dir` and `--cache-overwrite` in the `cache arguments` group. Help shows
the resolved default cache root.

Inspection and filtered clearing operate on registered namespace entry
boundaries. Unfiltered `cache clear --all` removes every child beneath the cache
root, including unregistered or legacy contents, while preserving the root.
Cache roots must therefore contain no unrelated durable data. Destructive
maintenance supports dry-run inspection, explicit scope, and confirmation.

## Tests

Cache tests cover behavior relevant to their format:

* runtime-root defaults, namespace paths, and entry boundaries
* identity changes for result-affecting configuration and `_CACHE_VERSION`
* save/load round trips and recent-use timestamps
* invalid-entry removal, overwrite-once behavior, and atomic-write failures

Producer tests separately verify reuse on a hit and production and persistence
on a miss.
