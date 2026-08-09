# Caching

This document defines Scinoephile's cache ownership, layout, and lifecycle
conventions. Cache contents are disposable performance artifacts: removing the
entire cache must not destroy authored output, user decisions, or other state
that cannot be regenerated.

## Cache and data boundaries

Use the runtime cache root for reproducible artifacts such as model output,
downloaded resources, extracted media streams, and derived analysis. Use the
runtime data root for durable application state, including user-reviewed or
user-edited data. A convenient filesystem location does not make durable data a
cache.

`cache_root_path: Path | None` consistently means the root beneath all cache
namespaces. `None` selects `get_runtime_cache_root_path()`; it does not disable
caching. If an operation ever needs to disable persistence, represent that with
an explicit option or a different cache implementation.

## Responsibilities

A cache class owns storage mechanics:

* resolving and validating the cache root
* appending its namespace and exposing concrete `cache_root_path` and
  `cache_dir_path` attributes
* deriving stable entry paths
* validating, loading, saving, removing, and marking entries as recently used
* implementing overwrite-once behavior

The operation that produces an artifact owns computation and external
dependencies. Extraction, network requests, model inference, parsing, and
rendering do not belong in cache classes. Producers should follow the simple
flow of loading from the cache, producing on a miss, and saving the result.

Callers should not derive persistent entry paths, directly delete entries, or
otherwise duplicate cache lifecycle logic. When a cache contains multiple
related artifact types, give each type explicit path, load, save, and remove
methods as needed.

An operation that owns a cache's lifetime may accept cache configuration and
construct the cache. A function that accepts a caller-supplied cache should
accept only that cache, optionally creating a default instance when omitted;
it should not also accept the cache's constructor arguments. Related caches may
reuse the owning cache's resolved root and overwrite policy.

## Construction and nomenclature

Cache constructors should place `cache_root_path` first, followed by required
and optional cache-specific configuration, with `overwrite: bool = False` last
when replacement is supported.

Use `cache_root_path` for the shared root and `cache_dir_path` for a cache's
namespaced directory. CLI `--cache-dir` values are cache roots, even though the
command-line name uses the shorter conventional spelling.

## Namespaces and entries

Each cache appends its own stable namespace beneath the cache root. Group
related namespaces under domain directories such as `llm/` and `media/` rather
than flattening every cache into the root. Do not introduce marker files merely
to declare namespaces.

Cache inspection treats each direct child of a namespace as one independently
removable entry. A directory entry may contain related files that must be kept
or removed together. New grouped or nested namespace layouts must also be made
discoverable by `scinoephile.core.cache.operations` so list, stats, prune, and
clear commands agree with the owning cache.

Keep namespace names and entry boundaries stable when possible. Layout changes
should not cause one cache's maintenance operation to delete another cache's
entries.

## Identity and versioning

An entry identity must include every input and configuration value that can
change the reusable result. Depending on the domain, that may include source
content or file metadata, model and backend identifiers, language, preprocessing
settings, or prompt content. Exclude credentials, transient client objects, and
unstable representations.

Persistent cache implementations should define a private `_CACHE_VERSION`
constant and include it in the serialized payload, identity hash, or path.
Increment it whenever older entries are no longer safe to reuse. A version is
local to the cache format; there is no global cache schema version.

## Lifecycle behavior

Cache APIs should make hits, misses, and mutations explicit:

* `get_path(...)` derives the entry location without implementing production.
* `load(...)` returns the validated cached value or path, and returns `None` for
  a miss.
* `save(...)` persists a complete value and returns its path.
* `remove(...)`, when targeted invalidation is needed, returns the removed path
  or `None` when no matching entry exists.

Treat unreadable, malformed, mismatched, or unsupported entries as misses:
remove them, log the reason, and allow the producer to regenerate them. A
successful load should update the entry's modification timestamp inside the
cache so pruning reflects recent reuse. If a caller performs additional domain
validation, it should remove a rejected entry rather than managing timestamps
itself.

Use clear log verbs consistently: `Loaded`, `Saved`, `Removed`, and `Discarded
invalid`. Cache misses do not normally need logging.

## Overwrite behavior

Overwrite mode converts each matching preexisting entry into a miss at most once
per cache instance. Track refreshed paths so an entry saved earlier in the same
operation can be reused rather than immediately removed. A successful save
counts as a refresh.

Do not clear an entire namespace when overwrite is requested. Only entries whose
identities are actually requested should be replaced.

## Filesystem safety

Writes should be atomic whenever practical. Stage files or directories on the
same filesystem as their destination and replace the destination only after the
new artifact is complete. Cache classes create their required destination
directories; producers may use cache-owned locations for same-filesystem
staging but should hand completed artifacts back to the cache for persistence.

Failed production or serialization must not leave a partial entry that can be
mistaken for a hit. Removal code must not follow symbolic links when recursively
deleting directory entries.

## CLI and maintenance integration

Cache-producing CLIs should use the shared cache argument bundle, placing
`--cache-dir` and `--cache-overwrite` in the `cache arguments` group. Cache
directory help should display the resolved default cache root path.

The cache list, stats, prune, and clear commands operate on namespace entry
boundaries. Because pruning uses modification times, caches must touch valid
hits as described above. Destructive maintenance commands should continue to
support dry-run inspection and explicit confirmation.

## Tests

Cache tests should cover the behavior relevant to their format:

* runtime-root defaults and namespace paths
* identity changes for result-affecting configuration and `_CACHE_VERSION`
* valid save/load round trips and recent-use timestamp updates
* invalid-entry removal and regeneration as a miss
* overwrite-once behavior within one cache instance
* atomic-write failure behavior for persistent artifacts
* namespace discovery and entry boundaries for new layouts

Producer tests should separately verify cache-hit reuse, production on a miss,
and save behavior without making the cache responsible for the production
dependency.
