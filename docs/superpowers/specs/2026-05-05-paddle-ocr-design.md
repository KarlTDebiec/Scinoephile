# PaddleOCR Design

## Summary

Add a native Python PaddleOCR path for converting image-based subtitles to SRT.
The initial command will be `scinoephile ocr paddle --infile INFILE --outfile
OUTFILE`, where `INFILE` is either a `.sup` file or an existing Scinoephile
image subtitle directory, and `OUTFILE` is an SRT file.

The implementation will use the Python `paddleocr` package and PaddlePaddle
runtime directly rather than invoking the `paddleocr` executable. It will adapt
SubtitleEdit's PaddleOCR preprocessing and result line-grouping ideas where they
improve subtitle OCR behavior, while keeping Scinoephile's existing subtitle
loading, validation, CLI, and serialization patterns.

## Goals

- Add `scinoephile ocr paddle` as a nested CLI following existing dispatcher
  patterns such as `cache` and `dictionary build`.
- Accept both `.sup` files and image subtitle directories using the existing
  `ImageSeries.load(...)` contract.
- Write recognized subtitles to SRT using the existing text `Series` save path.
- Keep OCR implementation code under `scinoephile/image/ocr`.
- Move the current OCR validation code to `scinoephile/image/ocr/validation`.
- Add basic PaddleOCR dependency support without pulling in document parsing
  extras.
- Annotate adapted logic and update `docs/THIRD_PARTY_NOTICES.md` for
  SubtitleEdit.

## Non-Goals

- Do not add Tesseract, Ollama, Google Lens, cloud OCR, or PaddleOCR-VL in this
  first implementation.
- Do not implement SubtitleEdit's standalone PaddleOCR download manager or C#
  subprocess approach.
- Do not require live model downloads during the normal test suite.
- Do not change the existing OCR validation behavior beyond moving its package.

## CLI Design

Add:

```bash
scinoephile ocr paddle --infile INFILE --outfile OUTFILE --language en
```

Arguments:

- `--infile`: path to a `.sup` file or image subtitle directory containing
  `index.html` and PNG files.
- `--outfile`: path to the output `.srt` file.
- `--language`: PaddleOCR language code, defaulting to `en`. The help text
  should explicitly list the subtitle-relevant options: `en` (English), `ch`
  (simplified Chinese and English), and `chinese_cht` (traditional Chinese).

Likely follow-up arguments, if straightforward after inspecting PaddleOCR's
current Python API:

- `--device`: optional execution device, if PaddleOCR exposes a stable setting.
- `--score-threshold`: minimum recognition confidence used to keep text.
- `--no-preprocess`: debugging escape hatch to disable SubtitleEdit-inspired
  image preprocessing.

The CLI will use `get_arg_groups_by_name(...)` with `input arguments`,
`operation arguments`, and `output arguments`, and will define `_main(...)` with
keyword-only parameters matching `argparse` destinations.

## Package Layout

New and moved modules:

```text
scinoephile/cli/ocr/
  __init__.py
  ocr_cli.py
  ocr_paddle_cli.py

scinoephile/image/ocr/
  __init__.py
  paddle/
    __init__.py
    engine.py
    preprocessing.py
    result.py
    series.py
  validation/
    __init__.py
    char_cursor.py
    char_dims.py
    char_grp_dims.py
    char_pair_gaps.py
    gap_cursor.py
    validation_manager.py
```

`scinoephile/cli/scinoephile_cli.py` will add `OcrCli` as a top-level
subcommand.

`scinoephile/image/ocr/__init__.py` will export PaddleOCR public API entries and
continue to expose validation API compatibility only where that is useful and
style-compliant. Validation imports should preferably move to
`scinoephile.image.ocr.validation`.

## Data Flow

1. `OcrPaddleCli._main(...)` validates `INFILE` and `OUTFILE`.
2. Load `INFILE` with `ImageSeries.load(...)`.
3. Initialize the PaddleOCR engine once for the requested language.
4. For each `ImageSubtitle`:
   - preprocess its image for OCR;
   - run PaddleOCR prediction;
   - normalize structured PaddleOCR output into internal result objects;
   - group detections into subtitle text lines;
   - preserve the original subtitle start and end times.
5. Build a `scinoephile.core.subtitles.Series` with recognized text.
6. Save the output with `format_="srt"`.

## PaddleOCR Integration

Use `from paddleocr import PaddleOCR` lazily inside the Paddle engine so import
errors can be converted into clear user-facing CLI errors.

The initial engine should configure document preprocessing features for subtitle
images conservatively:

- disable document orientation classification;
- disable document unwarping;
- allow textline orientation only if it improves SubtitleEdit parity and does
  not create unnecessary overhead for subtitle images.

The normal dependency should be `paddleocr`, not `paddleocr[all]`. PaddlePaddle
will be added explicitly if dependency resolution or runtime import checks show
that relying on PaddleOCR's metadata is not sufficiently reliable for Python
3.13.

## SubtitleEdit Adaptation

SubtitleEdit behavior to adapt:

- add a transparent/black border around subtitle bitmaps before OCR when useful;
- use PaddleOCR language codes such as `en`, `ch`, and `chinese_cht`;
- reconstruct output lines from OCR result geometry by grouping detections by
  vertical position and sorting each line by horizontal position;
- preserve per-image batching opportunities internally without making the first
  implementation depend on PaddleOCR CLI stdout.

Adapted modules or functions will include concise comments naming SubtitleEdit
as the source inspiration or adapted logic. `docs/THIRD_PARTY_NOTICES.md` will
add a SubtitleEdit MIT section following the existing `jyut-dict` pattern,
including project URL, license, copyright notice if available from the source,
and MIT license text or a link to the complete license text.

## Error Handling

- If PaddleOCR or PaddlePaddle cannot be imported, raise a Scinoephile-specific
  user-facing error with installation guidance.
- If `INFILE` is neither a valid `.sup` nor an image subtitle directory, surface
  the existing `ImageSeries.load(...)` error through `parser.error(...)`.
- If PaddleOCR returns no detections for an event, write an empty subtitle text
  event only if preserving the timing is useful for downstream review; otherwise
  omit empty OCR events. The initial implementation will preserve timing with
  empty text because that keeps a one-to-one mapping with image subtitles.
- If output already exists, follow the repository's standard output validation
  behavior for CLI tools.

## Testing

Unit tests that do not require PaddleOCR:

- CLI parser and top-level dispatch include `ocr` and `paddle`.
- `.sup` and image-directory inputs are accepted by the command path using a
  fake recognizer.
- Result line grouping orders words top-to-bottom and left-to-right.
- Preprocessing returns a valid image with expected dimensions and mode.
- Existing validation imports are updated after package movement.

Integration tests:

- A live PaddleOCR test may be added behind an explicit marker or skip condition
  that requires the runtime and local models. It must not run in the default
  suite or download models implicitly.

Verification for implementation:

- Run `uv run ruff format`, `uv run ruff check --fix`, and `uv run ty check`
  only on changed Python files.
- Run targeted tests for new OCR CLI and image OCR modules.
- Run the repository test command if the change set is broad enough:
  `cd test && UV_CACHE_DIR=/tmp/uv-cache uv run pytest -n auto`.

## Open Decisions

- Exact PaddleOCR version constraints will be selected during implementation
  after resolving the lock file with Python 3.13.
- Whether `paddlepaddle` must be an explicit dependency will be decided by
  dependency resolution and import verification.
- Whether to expose `--device` in the first CLI depends on current PaddleOCR API
  stability.
