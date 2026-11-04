# Audio subtitle directories

`AudioSeries.save(directory)` exports the series audio to `<directory-name>.wav`,
absolute subtitle timestamps to `<directory-name>.srt`, and buffered block WAVs.
Exports also own the reserved metadata file `.scinoephile-audio.json`:

```json
{"version": 1, "audio_start_ms": 10000}
```

`audio_start_ms` is the nonnegative integer timestamp, in milliseconds, corresponding
to the beginning of the full WAV. For example, a slice containing a cue at
10–12 seconds exports a two-second WAV, retains the 10–12-second cue, and records an
origin of 10000 milliseconds. Loading restores the absolute timestamps while
constructing audio clips relative to this origin.

Directories without metadata retain the legacy origin of zero. Metadata must be a
JSON object containing integer `version: 1` and a nonnegative integer
`audio_start_ms`; booleans and unsupported versions are rejected. Every export
rewrites the metadata, including an origin of zero, so replacing cropped audio
cannot retain a stale offset.

All managed files, including metadata, are produced in a staging directory before
any existing files are replaced. Unrelated files in the output directory remain
untouched. Production failures leave the previous export intact; replacement of
the individual completed files is not a filesystem-wide transaction.
