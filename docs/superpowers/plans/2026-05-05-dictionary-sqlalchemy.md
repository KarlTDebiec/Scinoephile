# Dictionary SQLAlchemy Persistence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate dictionary SQLite persistence from direct `sqlite3` calls to SQLAlchemy Core without changing dictionary service APIs.

**Architecture:** Keep `DictionarySqliteStore` as the public store class and replace its direct cursor usage with SQLAlchemy Core tables, expressions, transactions, and SQLite-specific conflict handling. Preserve the existing SQLite schema, `PRAGMA user_version=3`, FTS5 virtual tables, lookup ordering, and dataclass conversion behavior.

**Tech Stack:** Python 3.13, SQLAlchemy Core 2.x, SQLite, pytest, ruff, ty.

---

## File Structure

- Modify `test/core/dictionaries/test_sqlite_store.py`
  - Add regression coverage for SQLAlchemy migration risks before production edits.
  - Keep tests focused on public store behavior and SQLite schema shape.

- Modify `scinoephile/core/dictionaries/sqlite_store.py`
  - Replace `sqlite3` imports and cursor methods with SQLAlchemy Core metadata, tables, engine, and statements.
  - Preserve public method names and return types.

- Create or modify no optimization persistence files.
  - `scinoephile/optimization/persistence/test_cases/sqlite_store.py` remains the style reference only.

---

### Task 1: Add Dictionary Store Regression Tests

**Files:**
- Modify: `test/core/dictionaries/test_sqlite_store.py`

- [ ] **Step 1: Add duplicate and LIKE-escaping fixtures/tests**

Add imports and two tests below `test_sqlite_store_preserves_expected_schema`:

```python
def test_sqlite_store_literal_like_lookups(
    database_path: Path,
    sample_source: DictionarySource,
):
    """Test literal matching of LIKE wildcard characters in romanization."""
    entries = [
        DictionaryEntry(
            traditional="百分號",
            simplified="百分号",
            pinyin="percent% sign",
            jyutping="percent% sign",
            definitions=[DictionaryDefinition(text="percent sign")],
        ),
        DictionaryEntry(
            traditional="底線",
            simplified="底线",
            pinyin="under_score",
            jyutping="under_score",
            definitions=[DictionaryDefinition(text="underscore")],
        ),
        DictionaryEntry(
            traditional="反斜線",
            simplified="反斜线",
            pinyin=r"back\\slash",
            jyutping=r"back\\slash",
            definitions=[DictionaryDefinition(text="backslash")],
        ),
    ]
    store = DictionarySqliteStore(database_path=database_path)
    store.persist((sample_source, entries))

    assert store.lookup_by_pinyin("%", limit=5) == [entries[0]]
    assert store.lookup_by_pinyin("_", limit=5) == [entries[1]]
    assert store.lookup_by_pinyin("\\", limit=5) == [entries[2]]
    assert store.lookup_by_jyutping("%", limit=5) == [entries[0]]
    assert store.lookup_by_jyutping("_", limit=5) == [entries[1]]
    assert store.lookup_by_jyutping("\\", limit=5) == [entries[2]]
```

```python
def test_sqlite_store_collapses_duplicate_entries_and_definitions(
    database_path: Path,
    sample_source: DictionarySource,
):
    """Test duplicate entries and definitions collapse through uniqueness rules."""
    definition = DictionaryDefinition(text="duplicate definition", label="noun")
    duplicate = DictionaryEntry(
        traditional="重複",
        simplified="重复",
        pinyin="chong2 fu4",
        jyutping="cung4 fuk1",
        frequency=1.0,
        definitions=[definition, definition],
    )
    store = DictionarySqliteStore(database_path=database_path)
    store.persist((sample_source, [duplicate, duplicate]))

    assert store.lookup_by_traditional("重複", limit=5) == [
        DictionaryEntry(
            traditional="重複",
            simplified="重复",
            pinyin="chong2 fu4",
            jyutping="cung4 fuk1",
            frequency=1.0,
            definitions=[definition],
        )
    ]
```

- [ ] **Step 2: Run focused tests and verify they pass before migration**

Run:

```bash
cd test && UV_CACHE_DIR=/tmp/uv-cache uv run pytest core/dictionaries/test_sqlite_store.py
```

Expected: PASS. These tests lock current behavior before the SQLAlchemy rewrite.

- [ ] **Step 3: Commit test coverage**

Run:

```bash
git add test/core/dictionaries/test_sqlite_store.py
git commit -m "test: cover dictionary sqlite store edge cases"
```

Expected: commit succeeds with only the focused test file staged.

---

### Task 2: Convert Dictionary Store Schema and Engine to SQLAlchemy Core

**Files:**
- Modify: `scinoephile/core/dictionaries/sqlite_store.py`

- [ ] **Step 1: Replace imports and add SQLAlchemy schema metadata**

Replace direct `sqlite3` and `closing` imports with SQLAlchemy Core imports:

```python
from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Table,
    Text,
    UniqueConstraint,
    case,
    create_engine,
    func,
    select,
    text,
)
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import URL, Connection, RowMapping
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import NullPool
```

Add class attributes:

```python
    schema_version = 3
    """SQLite schema version."""

    _metadata = MetaData()
    """SQLAlchemy Core metadata for dictionary tables."""
```

Define fixed SQLAlchemy tables for `entries`, `sources`, `definitions`, `chinese_sentences`, `nonchinese_sentences`, `sentence_links`, and `definitions_chinese_sentences_links` with the same column names, primary keys, foreign keys, unique constraints, and conflict clauses as the current raw SQL schema.

- [ ] **Step 2: Add engine initialization**

In `__init__`, keep path validation and add an engine matching optimization persistence:

```python
self.engine = create_engine(
    URL.create("sqlite", database=str(self.database_path)),
    future=True,
    poolclass=NullPool,
)
```

- [ ] **Step 3: Run focused tests and verify migration is still red**

Run:

```bash
cd test && UV_CACHE_DIR=/tmp/uv-cache uv run pytest core/dictionaries/test_sqlite_store.py
```

Expected: FAIL until the remaining cursor-based implementation is converted.

---

### Task 3: Convert Persistence Writes to SQLAlchemy Core

**Files:**
- Modify: `scinoephile/core/dictionaries/sqlite_store.py`

- [ ] **Step 1: Replace `persist` transaction body**

Keep the existing parent directory creation and database replacement. Use:

```python
with self.engine.begin() as connection:
    self._write_database_version(connection)
    self._drop_tables(connection)
    self._create_tables(connection)
    source_id = self._insert_source(connection, source)
    for entry in entries:
        entry_id = self._insert_entry(connection, entry)
        for definition in entry.definitions:
            self._insert_definition(connection, definition, entry_id, source_id)
    self._generate_indices(connection)
```

- [ ] **Step 2: Convert table creation/drop helpers**

Implement `_create_tables(connection: Connection)` with SQLAlchemy table `.create(connection)` calls for normal tables and `connection.execute(text(...))` for FTS5 virtual tables:

```python
for table in self._metadata.sorted_tables:
    if table.name not in {"sentence_links", "definitions_chinese_sentences_links"}:
        table.create(connection)
self._sentence_links.create(connection)
self._definitions_chinese_sentences_links.create(connection)
```

Use `text("CREATE VIRTUAL TABLE entries_fts USING fts5(pinyin, jyutping)")` and `text("CREATE VIRTUAL TABLE definitions_fts USING fts5(fk_entry_id UNINDEXED, definition)")`, preserving `_is_missing_fts5`.

Implement `_drop_tables(connection: Connection)` with `text("DROP ...")` statements in dependency-safe order, preserving FTS and index drops.

- [ ] **Step 3: Convert insert helpers**

Use `sqlite_insert(...).on_conflict_do_nothing()` for entries and definitions, then reload existing IDs when `inserted_primary_key` or `rowcount` does not provide a new ID.

Entry insert payload:

```python
{
    "traditional": entry.traditional,
    "simplified": entry.simplified,
    "pinyin": entry.pinyin,
    "jyutping": entry.jyutping,
    "frequency": entry.frequency,
}
```

Definition insert payload:

```python
{
    "definition": definition.text,
    "label": definition.label,
    "fk_entry_id": entry_id,
    "fk_source_id": source_id,
}
```

Source insert uses `self._sources.insert().values(...)` and returns the inserted primary key.

- [ ] **Step 4: Convert FTS/index generation and schema version**

Use SQLAlchemy `insert().from_select()` for FTS population where practical, or `text(...)` for the existing `INSERT INTO ... SELECT ...` statements.

Use:

```python
connection.execute(text(f"PRAGMA user_version={self.schema_version}"))
```

- [ ] **Step 5: Run focused tests**

Run:

```bash
cd test && UV_CACHE_DIR=/tmp/uv-cache uv run pytest core/dictionaries/test_sqlite_store.py
```

Expected: pinyin/traditional persistence may pass, but lookup fetches may still fail until read paths are converted.

---

### Task 4: Convert Lookup Reads to SQLAlchemy Core

**Files:**
- Modify: `scinoephile/core/dictionaries/sqlite_store.py`

- [ ] **Step 1: Convert field lookup methods**

Replace `_select_entry_ids(sql, params)` with `_select_entry_ids(statement)` and build structured SQLAlchemy statements.

Traditional and simplified lookup shape:

```python
statement = (
    select(self._entries.c.entry_id)
    .where(self._entries.c.traditional == query)
    .group_by(self._entries.c.entry_id)
    .order_by(func.length(self._entries.c.traditional), self._entries.c.entry_id)
    .limit(limit)
)
```

Pinyin and Jyutping lookup shape:

```python
like_query = f"%{self._get_escaped_query(query)}%"
statement = (
    select(self._entries.c.entry_id)
    .where(
        (self._entries.c.pinyin == query)
        | self._entries.c.pinyin.like(like_query, escape="\\")
    )
    .group_by(self._entries.c.entry_id)
    .order_by(
        case((self._entries.c.pinyin == query, 0), else_=1),
        func.length(self._entries.c.traditional),
        self._entries.c.entry_id,
    )
    .limit(limit)
)
```

- [ ] **Step 2: Convert `_fetch_entries` and aggregation**

Use `select(...).outerjoin(...)`, `in_(entry_ids)`, and SQLAlchemy `case` ordering:

```python
rank_by_id = {entry_id: rank for rank, entry_id in enumerate(entry_ids)}
statement = (
    select(
        self._entries.c.entry_id,
        self._entries.c.traditional,
        self._entries.c.simplified,
        self._entries.c.pinyin,
        self._entries.c.jyutping,
        self._entries.c.frequency,
        self._definitions.c.label,
        self._definitions.c.definition,
    )
    .outerjoin(
        self._definitions,
        self._definitions.c.fk_entry_id == self._entries.c.entry_id,
    )
    .where(self._entries.c.entry_id.in_(entry_ids))
    .order_by(
        case(rank_by_id, value=self._entries.c.entry_id, else_=len(entry_ids)),
        self._definitions.c.definition_id,
    )
)
```

Change `_aggregate_rows` to accept `list[RowMapping]`.

- [ ] **Step 3: Convert `_is_missing_fts5` type**

Update `_is_missing_fts5` to accept SQLAlchemy `OperationalError` and inspect `str(exc).lower()` as before.

- [ ] **Step 4: Run focused tests**

Run:

```bash
cd test && UV_CACHE_DIR=/tmp/uv-cache uv run pytest core/dictionaries/test_sqlite_store.py
```

Expected: PASS.

- [ ] **Step 5: Commit SQLAlchemy migration**

Run:

```bash
git add scinoephile/core/dictionaries/sqlite_store.py
git commit -m "refactor: migrate dictionary persistence to sqlalchemy"
```

Expected: commit succeeds with only the dictionary store staged.

---

### Task 5: Lint, Type Check, and Run Integration Tests

**Files:**
- Check: `test/core/dictionaries/test_sqlite_store.py`
- Check: `scinoephile/core/dictionaries/sqlite_store.py`

- [ ] **Step 1: Check changed files against style**

Review changed Python files for `docs/STYLE.md` requirements: copyright headers, `from __future__ import annotations`, docstrings, `__all__`, path naming, f-strings, and type annotations.

- [ ] **Step 2: Format changed Python files**

Run:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run ruff format test/core/dictionaries/test_sqlite_store.py scinoephile/core/dictionaries/sqlite_store.py
```

Expected: command succeeds.

- [ ] **Step 3: Lint and fix changed Python files**

Run:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check --fix test/core/dictionaries/test_sqlite_store.py scinoephile/core/dictionaries/sqlite_store.py
```

Expected: command succeeds without requiring major refactoring.

- [ ] **Step 4: Type check changed Python files**

Run:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run ty check test/core/dictionaries/test_sqlite_store.py scinoephile/core/dictionaries/sqlite_store.py
```

Expected: command succeeds.

- [ ] **Step 5: Run focused dictionary tests**

Run:

```bash
cd test && UV_CACHE_DIR=/tmp/uv-cache uv run pytest core/dictionaries/test_sqlite_store.py dictionaries/test_dictionary_tools.py cli/dictionary/test_dictionary_search_cli.py
```

Expected: PASS.

- [ ] **Step 6: Run full repository tests**

Run:

```bash
cd test && UV_CACHE_DIR=/tmp/uv-cache uv run pytest -n auto
```

Expected: PASS.

- [ ] **Step 7: Commit formatting or follow-up fixes**

If formatting, lint, type checking, or tests changed files, run:

```bash
git add test/core/dictionaries/test_sqlite_store.py scinoephile/core/dictionaries/sqlite_store.py
git commit -m "chore: finalize dictionary sqlalchemy migration"
```

Expected: commit only if there are additional changes after Task 4.
