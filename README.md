[![Python: =3.13](https://img.shields.io/badge/python-3.13-green.svg)](https://docs.python.org/3/whatsnew/3.13.html)
[![Build](https://github.com/KarlTDebiec/Scinoephile/actions/workflows/build.yml/badge.svg)](https://github.com/KarlTDebiec/Scinoephile/actions/workflows/build.yml)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: BSD 3-Clause](https://img.shields.io/badge/license-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

[English](/README.md) | [繁體中文](/docs/README.zh-hant.md) | [简体中文](/docs/README.zh-hans.md)

Scinoephile is a package for working with Chinese, English, and bilingual subtitles,
with a focus on combining separate Chinese and English subtitle tracks into a single
synchronized bilingual subtitle file.

## Features

- **Synchronize bilingual subtitles**: combine two subtitle series (e.g. Chinese + English)
  into the top and bottom lines of a single time-aligned series
- **Timing adjustments**: shift and stretch one subtitle series to match another
- **Language-specific tools**:
  - **English**: post-processing and editing workflows for English subtitle tracks
  - **Standard Chinese**: post-processing and editing workflows for Standard Chinese tracks
  - **Written Cantonese**: workflows for written Cantonese tracks, including integration
    with Standard Chinese where helpful
- **Dictionary tooling**: build and query Chinese dictionary assets used by downstream
  processing

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
