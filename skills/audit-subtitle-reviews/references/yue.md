# Cantonese review policy

- Never Mandarinize Cantonese wording. Do not replace Cantonese particles or
  short forms with Mandarin equivalents such as `咗 -> 了`.
- Check these high-value characters and particles:
  - `些`: consider whether colloquial usage should be `啲`.
  - `番`: distinguish `返`, `翻`, and legitimate `番`.
  - `是`: consider whether the Cantonese copula should be `係`.
  - `着`: check Cantonese aspect and lexical usage.
  - `喇啦啰`: check final-particle choice.
  - `这那`: consider `呢` or `嗰` in colloquial dialogue.
- Use `--filter all --characters 些 番 是 着 这那` for an occurrence audit, or
  `--characters 喇啦啰` with the default changed-row filter for particles.
- Compare parallel scripts for asymmetric lexical, OCR, punctuation, whitespace,
  and Mandarinization corrections.
- Treat JSON notes only as context. Replace each report note with an independent,
  concise assessment; do not merely restate the JSON or use placeholders.
