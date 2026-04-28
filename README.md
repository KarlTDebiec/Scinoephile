[![Python: =3.13](https://img.shields.io/badge/python-3.13-green.svg)](https://docs.python.org/3/whatsnew/3.13.html)
[![Build](https://github.com/KarlTDebiec/Scinoephile/actions/workflows/build.yml/badge.svg)](https://github.com/KarlTDebiec/Scinoephile/actions/workflows/build.yml)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: BSD 3-Clause](https://img.shields.io/badge/license-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

[English](/README.md) | [繁體中文](/docs/README.zh-hant.md) | [简体中文](/docs/README.zh-hans.md)

Scinoephile is a package for working with Chinese, English, and bilingual subtitles.
It includes workflows for turning messy real-world sources (OCR, audio, and imperfect
subtitle tracks) into clean, aligned, reviewable series.

## Features

- **Cantonese transcription (Yue vs. Zho)**: transcribe written Cantonese subtitles from
  audio using Standard Chinese reference subtitles to guide segmentation and revision.
  This supports a multi-stage pipeline (transcription → review → translation → review)
  and is designed to be testable and comparable across Whisper models and prompt sets.
- **OCR workflows**:
  - **Validate OCR against images**: interactively validate OCR text using subtitle
    image outputs (directory containing `index.html` + images, or `.sup` inputs).
  - **Fuse multiple OCR sources**: combine OCR outputs (e.g. Lens + Tesseract for English,
    Lens + PaddleOCR for Chinese) into a higher-quality subtitle series.
- **Synchronization**:
  - **Bilingual sync**: combine two series (e.g. Chinese + English) into the top and
    bottom lines of a single time-aligned series.
  - **Timewarping**: shift and stretch one subtitle series to match another using
    anchor points.
- **Other features**:
  - **Language-specific processing**: clean/flatten/proofread/romanize pipelines for
    English, Standard Chinese, and written Cantonese subtitle series.
  - **Analysis tooling**: compute diffs and Character Error Rate (CER) between series.
  - **Dictionary tooling**: build and query Chinese dictionary assets used by downstream
    processing.

## Installation

Scinoephile is a Python package targeting Python 3.13 and is developed with `uv`.

```bash
git clone https://github.com/KarlTDebiec/Scinoephile
cd Scinoephile
uv sync
```

## Usage

Run the CLI via `uv run`:

```bash
uv run scinoephile --help
```

Available subcommands:

- `analysis`: analyze subtitles
- `dictionary`: build or search Chinese dictionaries
- `eng`: modify English subtitles
- `sync`: combine two series into the top and bottom of a synchronized series
- `timewarp`: shift and stretch timings to match another series
- `yue`: modify written Cantonese subtitles
- `zho`: modify Standard Chinese subtitles

To see help for a specific tool:

```bash
uv run scinoephile sync --help
```

## Development

Run tests:

```bash
cd test
uv run pytest
```

## Notices

Third-party license and data-source acknowledgements are listed in
`docs/THIRD_PARTY_NOTICES.md`.
