---
name: write-movie-context
description: Research and draft concise, operation-specific, prompt-ready additional context for LLM calls involving a movie, including canonical character names, aliases, places, objects, organizations, culture-specific terms, and other recurring terminology. Use when preparing or revising a Scinoephile movie dataset's additional_context for transcription, review, OCR, or translation; when an LLM needs title-specific naming or tone guidance; or when reference subtitles and web sources such as official film pages, Wikipedia, or Douban should be reconciled into a terminology list.
---

# Write Movie Context

Run commands from the repository root. Produce context that can be sent to an
LLM verbatim; do not write a general film report or an exhaustive cast list.

## Determine the scope

Identify these from the request, the dataset's `create_output.py`, and the
available subtitle tracks:

- The movie and dataset.
- The LLM operation receiving the context.
- The input, guide, reference, and output languages and scripts.
- The file or variable to update, if the user named one.

Ask only when an unresolved ambiguity would materially change the terminology
or target-language forms. Otherwise state the inferred scope and proceed.

Treat context as belonging to a specific LLM operation, not to the movie in the
abstract. Inspect the actual call site before researching or drafting. Do not
pass one generic movie context to every LLM workflow merely because they share a
dataset.

Emphasize different evidence and instructions by operation:

| Operation | Emphasize |
|---|---|
| Transcription | Canonical spelling in the transcription language and script, spoken aliases, acoustically confusable names, and differences between guide wording and the words actually spoken. |
| Guided translation | Source-language variants mapped to established target-language names and terms, plus target-language tone and localization guidance. |
| Monolingual review | Canonical spellings, relationships, register, and terminology in the reviewed language; omit translation instructions. |
| OCR fusion or review | Exact forms likely to resolve image-text ambiguity; omit speech-specific or translation-specific instructions. |

Allow tightly coupled stages to share context only when they serve the same
target language and purpose. For example, KOB's `yue-Hant` transcription,
guided review, and gap translation can share Cantonese naming guidance. If a
dataset also performs English translation, give that translation its own
English-targeted context.

Use these repository examples as contrasts:

- For KOB transcription, prefer `yue-Hant` spellings and document where the
  `zho-Hant` guide differs from spoken Cantonese, such as `打狗棒` versus
  `打狗棍`.
- For MNT guided translation, map Chinese names and recurring terms to
  established English Totoro terminology and describe the desired English
  tone.

## Inspect subtitle evidence

Locate the best available human-authored or human-reviewed reference subtitle
tracks. Trace the workflow in `create_output.py` rather than choosing a file by
its name alone. Do not treat generated LLM output as naming authority.

Search the reference subtitles and inspect occurrences in context. Collect only
terms likely to help the requested LLM operation:

- Character names, surnames, nicknames, aliases, and titles.
- Relationship terms when they consistently identify a particular character.
- Places, organizations, ranks, creatures, objects, foods, techniques, and
  other story-specific concepts.
- Recurring culturally loaded phrases or terms whose literal rendering would
  be misleading.
- Script, spelling, or localization variants that could cause inconsistent
  output.

Preserve the exact observed source forms. Check nearby dialogue before treating
a common noun or kinship term as a proper-name alias. For example, map `姐姐` to
a character only if its relevant uses consistently identify that character; if
needed, qualify the mapping with its context.

Never edit files under `test/data/<dataset>/input/` while researching context.

## Research canonical usage

Use the web by default when it is available unless the user requests a
subtitle-only draft. Prefer sources in this order:

1. Official studio, distributor, credits, or release material in the desired
   output language.
2. Established reference sources such as Wikipedia for canonical titles,
   character names, relationships, setting, and premise.
3. Douban or comparable sources for Chinese titles, names, and terminology.
4. Reputable film databases, interviews, or specialist sources when the first
   three do not resolve a question.

Use fan wikis, machine-translated pages, search snippets, and subtitle-download
sites only as leads. Corroborate them before adopting terminology. When sources
conflict, prefer the official localization for the requested output language,
then use the subtitles to determine which source variants need to be mapped.

Keep citations and research commentary out of the prompt-ready context. Cite
the supporting web pages in the final response instead.

## Draft the context

Follow this plain-text shape, modeled on `test/data/mnt/create_output.py`:

```text
Movie context:
<Canonical title, premise, relationships, setting, tone, and only the
movie-specific interpretation or style guidance useful to the LLM.>

Movie-specific names and terminology:
- <observed source form / alias>: <preferred output form or concise meaning>
```

For a directional translation, put exact observed input variants on the left
and the preferred target-language form on the right. For monolingual review or
transcription, map variants to the preferred canonical spelling or briefly
explain the term. Preserve the requested output script exactly; do not assume
automatic Chinese conversion will handle proper names correctly.

Write the headings, movie summary, and terminology explanations in the language
of the LLM prompt. If one context is shared across operations with different
prompt languages, use the primary target language unless the user specifies
otherwise. Keep observed source forms unchanged even when they are in another
language or script.

Keep the prose concise and operational:

- Aim for roughly 150–400 words unless the movie genuinely needs more terms.
- Describe only plot facts and relationships needed to interpret dialogue.
- Include tone or register guidance only when it is movie-specific.
- Prefer one canonical output form for each entity or concept.
- Combine true variants in one bullet, separated by ` / `.
- Do not add obvious vocabulary, irrelevant cast members, speculative aliases,
  spoilers that do not aid interpretation, or generic instructions already
  supplied by the underlying prompt.
- State a real ambiguity rather than forcing a false one-to-one mapping.

## Write or integrate the result

When the user names a code or configuration destination, update that destination
and preserve its established representation. For a Scinoephile
`create_output.py`, follow the existing `additional_context` multiline-string
pattern and do not change which LLM calls receive it unless requested.

Otherwise write prompt-ready UTF-8 text to:

```text
local/<dataset>_additional_context.txt
```

The file must contain only the text intended for the LLM: no Markdown title,
citations, confidence notes, research log, or code fence. Provide a clickable
link to the file in the final response.

## Validate

Before finishing:

- Re-read every listed source form in its subtitle context.
- Confirm canonical output forms against the strongest available source.
- Remove duplicate, contradictory, unused, and over-broad mappings.
- Confirm names and terminology use the requested language and script.
- Read the complete result as literal LLM input and remove research-facing
  prose.
- If a Python destination changed, format and check only that changed Python
  file according to the repository instructions.

Summarize the subtitle tracks consulted, link the output, and cite any web
sources used.
