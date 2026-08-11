# Caching

This document defines Scinoephile's cache ownership, layout, and lifecycle
conventions. Cache contents are disposable performance artifacts. Every entry
must be regenerable from durable inputs and configuration.

## Cache and data boundaries

Use the runtime cache root for reproducible artifacts such as model output,
downloaded resources, extracted media streams, and derived analysis. Use the
runtime data root for durable application state, including user-reviewed or
user-edited data. Authored output and user decisions are durable application
state.

`cache_root_path: Path | None` consistently means the root beneath all cache
namespaces. `None` selects `get_runtime_cache_root_path()`.

## Responsibilities

A cache class owns storage mechanics:

* resolving and validating the cache root
* resolving its registered namespace and exposing concrete `cache_root_path` and
  `cache_dir_path` attributes
* deriving stable entry paths
* validating, loading, saving, removing, and marking entries as recently used
* implementing overwrite-once behavior

The operation that produces an artifact owns computation and external
dependencies, including extraction, network requests, model inference, parsing,
and rendering. Producers load from the cache, produce on a miss, and save the
result.

Callers use the cache's path and lifecycle methods. A cache containing multiple
related artifact types exposes explicit path, load, save, and remove methods for
each type as needed.

An operation that owns a cache's lifetime may accept cache configuration and
construct the cache. A function supporting cache injection accepts the cache
itself and may create a default instance when omitted. Related caches may reuse
the owning cache's resolved root and overwrite policy.

## Construction and nomenclature

Cache constructors should place `cache_root_path` first, followed by required
and optional cache-specific configuration, with `overwrite: bool = False` last
when replacement is supported.

Use `cache_root_path` for the shared root and `cache_dir_path` for a cache's
namespaced directory. CLI `--cache-dir` values are cache roots, even though the
command-line name uses the shorter conventional spelling.

## Namespaces and entries

The namespace mirrors the package that owns the produced artifact. The
Scinoephile operation producing the cache entry determines ownership.

`scinoephile.core.cache.cache_namespace.CacheNamespace` supplies generic
namespace validation, resolution, and discovery behavior. Each owning package
defines its concrete namespace enum in `cache_namespace.py`, and its cache
constructors resolve directories through members of that enum.

`scinoephile.workflows.cache_registry.CACHE_REGISTRY` explicitly aggregates the
owner-defined enums for application-wide cache inspection, statistics, pruning,
and clearing. The generic maintenance operations in `scinoephile.core.cache`
receive this registry from their caller.

The registered layout is:

```text
audio/
  classification/<operation>/
  diarization/
  separation/
    demucs/
  transcription/
    mlx_audio/
    whisper/
  vad/
dictionaries/
  cuhk/
    discovery/
    pages/
image/
  ocr/
    lens/
    paddle/
    tesseract/
      results/
      legacy_data/
lang/
  zho/
    subtitles/
      analysis/
llms/
  <operation>/
media/
  subtitles/
```

Namespace segments use Python module spelling, including underscores such as
`mlx_audio`. A parameterized `<operation>` segment is one validated path
component. Materially different entry types receive separate leaf namespaces,
as with Tesseract results and legacy trained data.

The registry covers Scinoephile-owned caches. Dependency-managed caches,
including Hugging Face, Torch Hub, Whisper model, and Paddle model caches, retain
their dependencies' layouts and lifecycle.

Cache inspection treats each direct child of a namespace as one independently
removable entry. A directory entry may contain related files that must be kept
or removed together. Add a new namespace to its owner's enum; the cache
constructor and application registry then consume the same declaration.

Keep namespace names and entry boundaries stable across compatible releases.
Layout changes preserve isolation between namespaces.

## Identity and versioning

An entry identity must include every input and configuration value that can
change the reusable result. Depending on the domain, that may include source
content or file metadata, model and backend identifiers, language, preprocessing
settings, or prompt content. Identity values are stable and non-secret;
credentials, transient client objects, and unstable representations remain
outside the identity.

Persistent cache implementations should define a private `_CACHE_VERSION`
constant and include it in the serialized payload, identity hash, or path.
Increment it whenever older entries are no longer safe to reuse. A version is
local to the cache format, and each cache owns its version independently.

## Lifecycle behavior

Cache APIs should make hits, misses, and mutations explicit:

* `get_path(...)` derives the entry location.
* `load(...)` returns the validated cached value or path, and returns `None` for
  a miss.
* `save(...)` persists a complete value and returns its path.
* `remove(...)`, when targeted invalidation is needed, returns the removed path
  or `None` when no matching entry exists.

Treat unreadable, malformed, mismatched, or unsupported entries as misses:
remove them, log the reason, and allow the producer to regenerate them. A
successful load should update the entry's modification timestamp inside the
cache so pruning reflects recent reuse. If a caller performs additional domain
validation, it removes a rejected entry through the cache.

Use clear log verbs consistently: `Loaded`, `Saved`, `Removed`, and `Discarded
invalid`.

## Overwrite behavior

Overwrite mode converts each matching preexisting entry into a miss at most once
per cache instance. Track refreshed paths so an entry saved earlier in the same
operation can be reused rather than immediately removed. A successful save
counts as a refresh.

Replacement is scoped to requested entry identities.

## Filesystem safety

Writes should be atomic whenever practical. Stage files or directories on the
same filesystem as their destination and replace the destination only after the
new artifact is complete. Cache classes create their required destination
directories; producers may use cache-owned locations for same-filesystem
staging but should hand completed artifacts back to the cache for persistence.

Failed production or serialization leaves the previous valid entry intact or no
entry. Recursive removal treats symbolic links as leaf entries.

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
and save behavior.
