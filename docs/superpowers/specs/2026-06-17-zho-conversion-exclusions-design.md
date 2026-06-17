# Chinese Conversion Exclusions Design

## Context

`scinoephile/lang/zho/script/conversion.py` currently keeps one conversion exclusion
mapping and reverses it by value depending on the OpenCC conversion direction. This
cannot represent cases where a character should be preserved only in one direction.

The exclusion list should be regenerated from repository subtitle fixtures. Raw OpenCC
conversion is expected to leave already-traditional fixtures unchanged under `s2t`, and
already-simplified fixtures unchanged under `t2s`. Any changed source characters from
those no-op expectations are candidates for directional preservation.

## Data Scope

Review subtitle text from both fixture families:

- OCR output fixtures matching
  `test/data/*/output/{yue-Hans,yue-Hant,zho-Hans,zho-Hant}_ocr/fuse_clean_validate.srt`.
- Original input SRT fixtures matching
  `test/data/*/input/{yue-Hans,yue-Hant,zho-Hans,zho-Hant}.srt`.

For Hant fixtures, run raw `s2t` and collect source characters that OpenCC changes.
For Hans fixtures, run raw `t2s` and collect source characters that OpenCC changes.
Same-length changes are handled character by character. If length-changing changes are
found, classify them manually before deciding whether the character-level exclusion
mechanism is still sufficient.

## Implementation

Replace the single mapping with two private directional sets:

- `_S2T_EXCLUDED_CHARS`: characters preserved when converting simplified to
  traditional, used for configurations in `TRADITIONAL_CONFIGS`.
- `_T2S_EXCLUDED_CHARS`: characters preserved when converting traditional to
  simplified, used for configurations in `SIMPLIFIED_CONFIGS`.

`get_zho_text_converted` keeps the same public signature and behavior outside exclusion
selection. When exclusions apply, it selects the relevant set based on the conversion
configuration and preserves matching source characters by original character position,
as it does today. Exclusions still apply only when the converted text length equals the
input text length.

## Annotation

Each active exclusion gets an inline comment explaining why the source character is
preserved, using Chinese script knowledge and fixture context. Likely OCR or review
artifacts are included near the relevant set as commented-out entries with a note and
the first file and line where they were found, but they are not active exclusions.

## Tests

Update focused conversion tests to cover directional behavior:

- A character may be preserved in `s2t` without requiring a corresponding preservation
  rule in `t2s`.
- A character may be preserved in `t2s` without requiring a corresponding preservation
  rule in `s2t`.
- Existing public conversion behavior still works for representative series fixtures.

Before running `ruff` or `ty`, check changed Python files against `docs/STYLE.md`. Then
run `ruff format`, `ruff check --fix`, and `ty check` only on changed Python files.
Run the relevant conversion tests, and run the broader test command if the focused tests
indicate shared behavior risk.

## Self-Review

The design is scoped to one conversion module and its tests. It names the data sources,
the directional data structure, the runtime behavior, annotation expectations, and
verification path. It intentionally avoids changing OpenCC configuration support or
script analysis behavior.
