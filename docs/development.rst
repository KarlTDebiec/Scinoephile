:github_url: https://github.com/KarlTDebiec/scinoephile

Development
-----------

Compositor
__________

- [x] Drop short events
- [ ] Improve interactivity
- [ ] Option to use one input subtitle track as primary
- [ ] For each subtitle in primary, List all overlapping subtitles in secondary
- [ ] Show visualization of overlap
- [ ] Clean up documentation and README
- [ ] Extend test coverage
- [ ] Restore support for Hanzi, pinyin, and English together
- [ ] Restore support for IPython prompt
- [ ] Restore support for truecase
- [ ] Restore support for time offset (may use pysubs2)
- [ ] To '--overwrite' flag, add option to back up file

Derasterizer
____________

- [x] Color output intelligently when comparing to standard
- [x] Store character confirmations
- [x] Interactively reassign and confirm characters
- [x] Merge characters and update data structures
- [x] Save char_bounds for each event
- [x] Load char_bounds for each event
- [x] Track reassigned characters
- [x] Merge sets of three characters
- [x] Score incorrectly-segmented lines more precisely
- [x] For unmatchable chars, print out unicode blocks
- [x] Print out list of misassigned chars
- [x] Organize misassigned and unmatchable chars by block
- [ ] Clean up documentation and README
- [ ] Backup files (-o to backup pre-existing file, -oo to overwrite)
- [ ] Figure out if characters can be stored in model
- [ ] Figure out how to host model online

Documentation
_____________

- [ ] Review
- [ ] Move update_badges.py to utils
- [ ] cut update_badges.py down to a single template

Future
______

- Replace matplotlib with another library to improve font support
- Make clearer whether functions are acting on Images or image data
- Visualize weights
- Option to compress or not when saving Datasets (can take a long time)
- Improve requirements.txt; clarify what is required for which functions
- Sphinx checklist extension to convert "- [ ]" to "☐" and "- [X]" to "☑"
