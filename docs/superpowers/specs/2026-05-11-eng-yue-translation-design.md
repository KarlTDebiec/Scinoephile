# English From Cantonese Translation Design

## Goal

Generate a new English subtitle script from Cantonese subtitles while using an
existing English subtitle script as reference material. The generated English
must follow the Cantonese timing, line count, meaning, and dramatic intent, but
may reuse wording from the original English when it remains faithful to the
Cantonese.

## Context

The current `scinoephile.multilang.yue_zho.translation` flow fills gaps in a
primary Cantonese series from a secondary Chinese series. That shape does not fit
this feature because the Cantonese and English inputs may have different subtitle
counts, and the output must contain one English subtitle for every Cantonese
subtitle.

Existing reusable LLM shapes cover aligned dual blocks and gapped dual blocks,
but neither represents "two unaligned input blocks, output cardinality follows
source one." This feature should introduce that reusable shape rather than
overloading `DualBlockProcessor`.

## Design

Add a generic LLM shape under `scinoephile.llms.dual_block_cardinality` for
block transforms where:

- `source_one` determines output timing and output count.
- `source_two` provides reference text and may have a different number of
  subtitles in the paired block.
- Blocks are paired with the existing pause-based pairing helper.
- Each query contains all `source_one` subtitles and all `source_two` subtitles
  in the paired block.
- Each answer contains exactly one output field for each `source_one` subtitle.

The generic shape should include:

- A prompt base class with source-one, source-two, and output field naming.
- A manager that builds dynamic query, answer, and test case classes from
  separate source-one and source-two block sizes.
- A processor that queries one paired block at a time and returns a `Series`
  using source-one subtitle start and end times.

Add `scinoephile.multilang.eng_yue.translation` on top of that generic shape.
Its public API should mirror existing feature packages:

- `ENG_YUE_TRANSLATION_OPERATION_SPEC`
- `EngFromYueTranslationProcessKwargs`
- `EngFromYueTranslationProcessorKwargs`
- `EngVsYueTranslationPrompt`
- `get_eng_translated_vs_yue(...)`
- `get_eng_vs_yue_translator(...)`

The feature package should also add `scinoephile.multilang.eng_yue.__init__` and
update the `scinoephile.multilang` package docstring hierarchy.

## Prompt Behavior

The English-from-Cantonese prompt should instruct the model to:

- Translate the Cantonese subtitles into natural English.
- Produce one English subtitle for each Cantonese subtitle.
- Use the original English subtitles as reference, not as authoritative source
  text.
- Preserve names, canonical terminology, register, and recurring phrasing from
  the original English when they are compatible with the Cantonese.
- Prefer the Cantonese meaning when it differs from the original English.
- Return only subtitle text in the structured answer fields, without notes,
  explanations, labels, bracketed commentary, or alternate translations.
- Preserve subtitle markup only when it is appropriate for the generated English.

Field names should make the role of each input clear, for example:

- Query `yue_1`, `yue_2`, ...
- Query `eng_reference_1`, `eng_reference_2`, ...
- Answer `eng_1`, `eng_2`, ...

## Data Flow

`get_eng_translated_vs_yue(yue, eng, translator=None, **kwargs)` obtains a
processor if needed and calls `translator.process(yue, eng, **kwargs)`.

The processor pairs blocks from the Cantonese and English series using
`get_block_pairs_by_pause(...)`. For each paired block it builds a test case
whose shape is based on `(len(yue_block), len(eng_block))`, sends it through the
configured queryer, and creates output subtitles using the Cantonese block's
start and end times with the answer's English text.

The concatenated output series therefore has the Cantonese subtitle count and
timing.

## Validation And Error Handling

The manager should reject invalid dynamic class sizes, such as a source-one size
less than one. Source two may be empty only if the existing block pairing helper
can produce such a block; if that is not supported by current block pairing,
this feature does not need to add synthetic empty reference blocks.

The test case validator should ensure answers provide one string field for every
source-one subtitle. Empty strings should be allowed because some Cantonese
subtitles may be non-dialogue or intentionally silent, but missing fields should
remain invalid through the generated Pydantic schema.

The processor should not require one-to-one series or block alignment. It should
let existing block pairing and subtitle synchronization utilities determine the
paired blocks.

## Testing

Use TDD for the implementation.

Focused unit tests should cover the generic LLM shape:

- Query class generation includes all source-one and source-two fields for
  unequal block sizes.
- Answer class generation includes exactly one output field per source-one
  subtitle.
- Test case class reconstruction from JSON detects both source sizes.
- Processor output uses source-one timing and answer text when block sizes
  differ.

Feature tests should cover `eng_yue.translation`:

- The prompt exposes the expected field names and descriptions.
- `get_eng_vs_yue_translator(...)` wires the processor, prompt, default
  provider, and optional test cases.
- `get_eng_translated_vs_yue(...)` delegates to the provided processor and
  returns one English subtitle per Cantonese subtitle.

Before completion, run formatting and checks only on changed Python files as
required by `AGENTS.md`, then run the relevant focused tests.

## Non-Goals

This change does not add a CLI command, default persisted test case data, or
manual subtitle review workflow. Those can be added later once the core
translation behavior is stable.
