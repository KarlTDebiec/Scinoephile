# Standard Chinese review policy

- Check script consistency: Hant stages should remain traditional and reviewed
  simplified stages should contain no unintended traditional characters.
- Check `著/着` and `甚/什` within the main audit. Use a separate
  `--filter all --characters 著 着 甚 什` report only when requested or when
  investigating a suspected missed conversion.
- Compare parallel scripts for asymmetric lexical, OCR, punctuation, and
  whitespace corrections. Prefer correcting the corresponding initial review
  rather than relying on simplification cleanup.
- Treat JSON notes only as context. Replace every report note, populated or
  blank, with an independent, concise English interpretation of the row. Do not
  translate or restate the automatic note, and do not use placeholders.
- Flag self-contradictory notes, incorrect proper-name changes, and any edit that
  introduces Hant characters into a simplified stage.
