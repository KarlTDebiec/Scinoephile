# Media Search Subtitles CLI Design

## Goal

Add a `scinoephile media search-subs` command that searches OpenSubtitles.com
for subtitle files and can download a selected subtitle file when the user
provides its OpenSubtitles `file_id`.

## User Interface

Search only:

```bash
scinoephile media search-subs --query "The Matrix" --language en
```

Download a specific result:

```bash
scinoephile media search-subs \
  --query "The Matrix" \
  --language en \
  --file-id 1234567 \
  -o matrix.en.srt
```

Arguments:

- `--query`: required text search query.
- `--language`: required OpenSubtitles language code.
- `--api-key`: optional API key. Defaults to `OPENSUBTITLES_API_KEY`.
- `--username`: optional username. Defaults to `OPENSUBTITLES_USERNAME`.
- `--password`: optional password. Defaults to `OPENSUBTITLES_PASSWORD`.
- `--limit`: maximum number of result files to display. Defaults to `10`.
- `--file-id`: optional OpenSubtitles file identifier. Required when
  downloading.
- `-o`, `--outfile`: optional subtitle output file. Required with `--file-id`.
- `--overwrite`: optional output overwrite flag. Valid only with `--outfile`.

The command rejects `--outfile` without `--file-id`, rejects `--file-id`
without `--outfile`, and rejects `--overwrite` without `--outfile`.

## Result Selection

Search output displays one row per downloadable subtitle file, not just one row
per subtitle entry. Each row includes the OpenSubtitles `file_id`, language,
download count, rating or points when available, FPS when available, and release
name or filename when available.

Downloads are explicit: the CLI never downloads an arbitrary top result. The
user must copy a displayed `file_id` into `--file-id`.

## Architecture

Implementation stays within the media subtitle domain:

- `scinoephile/media/subtitles/opensubtitles.py` contains the API client,
  result dataclasses, response parsing, login, search, download-link request,
  and file download logic.
- `scinoephile/cli/media/media_search_subs_cli.py` contains argument parsing,
  environment-variable defaults, parser-level validation, result rendering, and
  CLI error mapping.
- `scinoephile/cli/media/media_cli.py` registers `MediaSearchSubsCli` as the
  `search-subs` subcommand.

No new `scinoephile/workflows` module is needed because this feature does not
coordinate multiple downstream domains. It only wraps the OpenSubtitles API and
writes subtitle files.

## OpenSubtitles API Flow

Search:

1. Build a `GET /subtitles` request with `query` and `languages`.
2. Send `Api-Key` and `User-Agent` headers.
3. Parse each result entry and each entry's `files` array into displayable file
   candidates.

Download:

1. Require API key, username, password, `file_id`, and output path.
2. Log in through `POST /login`.
3. Use the returned token and base URL for subsequent authenticated requests.
4. Request a temporary download URL through `POST /download` with `file_id`.
5. Download the subtitle content from the returned URL.
6. Write the output file, respecting `--overwrite`.

## Error Handling

The media client raises `ScinoephileError` for user-facing failures, including:

- missing API key;
- missing login credentials for download;
- OpenSubtitles HTTP or JSON errors;
- no matching subtitle files;
- requested `file_id` not present in current search results;
- existing output file without `--overwrite`;
- malformed API responses.

The CLI catches `ScinoephileError` and converts it to `argparse` parser errors,
matching the existing media CLI pattern.

## Testing

Tests will be written before implementation. Coverage includes:

- `MediaSearchSubsCli` help and usage, including nested `media` and root CLI
  paths.
- argument passing and environment-variable defaults.
- parser errors for invalid `--file-id`, `--outfile`, and `--overwrite`
  combinations.
- search result rendering with displayed `file_id` values.
- mocked OpenSubtitles search parsing, including multiple files per result.
- download flow with mocked login, download-link, and content responses.
- overwrite protection.
- `MediaCli` registering the new `search-subs` subcommand.

Changed Python files will be checked against `docs/STYLE.md`, then formatted
and checked with `ruff` and `ty` for only the changed Python files.
