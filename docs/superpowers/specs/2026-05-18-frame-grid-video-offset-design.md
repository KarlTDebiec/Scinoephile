# Frame-Grid Video Offset Design

## Goal

Make `scinoephile media offset` choose visually detected video offsets on the
reference video's frame grid and make default sampling less fragile by using
multiple windows across the shared runtime.

## Behavior

`get_video_offset` probes the reference video frame rate before visual scoring.
If no usable reference frame rate is available, it raises `ScinoephileError`.
Fine search candidates are integer multiples of the reference frame duration,
limited to the coarse winner's neighborhood and the configured maximum offset.
The result reports the final offset in seconds and, when available, reference
frames.

When no explicit start time is supplied, the tool samples multiple windows. The
default is four windows, each using `duration` as the per-window duration. Window
starts are evenly distributed between 10% and 90% of the shared usable runtime
of the two videos, clamped so each window fits. If an explicit `--start-time` is
provided, the command runs one window unless `--sample-windows` is also provided.

Each window is scored independently. The aggregate result uses valid window
results and aggregates frame offsets when a frame rate is available, then
converts the median frame offset back to seconds. The CLI prints per-window
offset, frame count, confidence, best score, next-best score, and an aggregate
summary.

## Scope

The change is limited to visual video-to-video offset detection. It does not add
seconds-grid fine-search fallback, legacy modes, or subtitle synchronization
changes.

## Testing

Unit tests cover frame-grid fine candidates, ffprobe parsing failures, automatic
window start generation, aggregation in frame units, and CLI output. Manual
verification uses the provided Toy Story files on `/Volumes/Backup/Video`.
