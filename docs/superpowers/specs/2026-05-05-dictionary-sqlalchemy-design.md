# Dictionary SQLAlchemy Persistence Design

## Goal

Migrate dictionary SQLite persistence from direct `sqlite3` calls to SQLAlchemy Core while preserving runtime behavior, persisted SQLite database shape, and existing dictionary service APIs.

## Scope

This change covers the dictionary persistence layer centered on `scinoephile/core/dictionaries/sqlite_store.py` and its tests. Dictionary services should continue to construct and call the store the same way they do today.

This change does not modify optimization test case persistence. That store on `github/master` already uses SQLAlchemy Core and provides the style reference for engine setup, table metadata, transactions, reflection, and SQLite-specific inserts.

## Naming

Keep the current module and class names:

- `scinoephile.core.dictionaries.sqlite_store`
- `DictionarySqliteStore`

The name remains accurate because the persisted database format is SQLite. No compatibility aliases or neutral `DictionaryStore` class will be introduced in this PR.

## Architecture

Use SQLAlchemy Core, not SQLAlchemy ORM. The dictionary store should define fixed table metadata for the persistent dictionary schema and create a SQLite engine with `future=True` and `NullPool`, matching the optimization persistence style.

The store should keep these responsibilities:

- validate and store the database path
- create the dictionary SQLite schema
- replace an existing database during `persist`
- insert source, entry, and definition records
- populate FTS tables when SQLite supports FTS5
- run lookup queries and convert result rows back to immutable dictionary dataclasses

The dictionary dataclasses remain separate from SQLAlchemy table definitions. SQLAlchemy is an implementation detail of the store, not a new domain model.

## Schema Behavior

The SQLAlchemy migration must preserve the existing SQLite schema shape:

- `entries`
- `entries_fts`
- `sources`
- `definitions`
- `definitions_fts`
- `chinese_sentences`
- `nonchinese_sentences`
- `sentence_links`
- `definitions_chinese_sentences_links`
- `fk_entry_id_index`

The database should continue to set `PRAGMA user_version=3`. This version marker is useful for identifying the schema written by dictionary builds even if no migration system exists yet.

The compatibility sentence tables should remain. They are not used by current dictionary services, but preserving them avoids changing the database shape produced by dictionary builds.

FTS5 virtual tables should remain because they are part of the current generated database shape and can support future full-text lookup work. Current lookup methods do not need to switch to FTS queries in this migration. If SQLite lacks FTS5, the store should keep the current graceful warning behavior and continue without FTS tables.

## Lookup Behavior

The migration must preserve these lookup behaviors:

- traditional and simplified lookups match exact headwords only
- pinyin and Jyutping lookups prefer exact matches, then literal substring matches
- pinyin and Jyutping substring matching must continue escaping `%`, `_`, and backslash as literal characters
- lookup result ordering remains stable by exact-match rank, traditional length where applicable, and entry ID
- fetched definitions remain ordered by `definition_id`
- duplicate entries and definitions still rely on SQLite uniqueness rules with conflict-ignore behavior

Dynamic SQL should be avoided where SQLAlchemy supports structured expression building. The one expected exception is ordered fetching by a variable entry ID list, which may use SQLAlchemy `case` expressions rather than interpolated SQL.

## Error Handling

The migration should preserve the current user-visible error behavior:

- missing FTS5 support logs warnings and does not fail dictionary builds
- failed inserts that cannot be reloaded raise `RuntimeError`
- lookup methods return empty lists when no matching entries exist

No new exception hierarchy is needed.

## Testing

Tests should be updated before production changes following the Superpowers TDD workflow.

Core tests should cover:

- field-specific lookups still round-trip the existing fixture entries
- expected schema tables and `PRAGMA user_version=3` are preserved
- literal LIKE escaping works for `%`, `_`, and backslash queries
- duplicate entries and definitions still collapse through uniqueness constraints

Existing service, CLI, and dictionary-tool tests should continue to pass without service API changes.

Changed Python files should be checked against `docs/STYLE.md` before running:

- `UV_CACHE_DIR=/tmp/uv-cache uv run ruff format <changed-python-files>`
- `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check --fix <changed-python-files>`
- `UV_CACHE_DIR=/tmp/uv-cache uv run ty check <changed-python-files>`

The relevant focused tests should run first, followed by the repository test command if the focused suite passes:

- `cd test && UV_CACHE_DIR=/tmp/uv-cache uv run pytest core/dictionaries/test_sqlite_store.py`
- `cd test && UV_CACHE_DIR=/tmp/uv-cache uv run pytest -n auto`

## Later Notes

After this PR, a separate cleanup could consider whether `DictionarySqliteStore` and `TestCaseSqliteStore` should share a small SQLite SQLAlchemy base helper for engine construction and path validation. That should wait until both stores are stable enough to show real duplication.
