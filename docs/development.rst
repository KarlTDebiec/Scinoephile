:github_url: https://github.com/KarlTDebiec/scinoephile

Development
-----------

Compositor
__________

- [x] Improve file arguments
- [ ] Extend test coverage
- [ ] Clean up documentation and README
- [ ] Restore support for Hanzi, pinyin, and English together
- [ ] Restore support for IPython prompt
- [ ] Restore support for truecase
- [ ] Restore support for time offset
- [ ] To '--overwrite' flag, add option to back up file

Derasterizer
____________

- [x] Add command-line arguments
- [x] Read infiles
- [x] Write outfile
- [x] Segment characters
- [x] Predict characters
- [x] Reconstruct text
- [x] Compare to standard
- [x] Print statistics
- [x] Compare to tesseract
- [ ] Clean up and organize into functions
- [ ] Color output intelligently when comparing to standard
- [ ] Clean up documentation and README
- [ ] To '--overwrite' flag, add option to back up file
- [ ] Figure out if characters can be stored into model

Documentation
_____________

- [ ] Review
- [ ] Move badge generator to utils, and cut down to a single template

Miscellaneous
_____________

- [ ] ImageSubtitleEvent: rename data to full_data, char_data to data
- [ ] ImageSubtitleSeries: Improve identification of spaces between characters
- [ ] Replace matplotlib with another library to improve font support
- [ ] Make clearer whether functions are acting on Images or image data
- [ ] Visualize weights
- [ ] Convenience function for viewing source of method/property in IPython
- [ ] Track modifications, and if infile==outfile only save if changed
- [ ] Option to compress or not when saving Datasets (takes a long time)

Future
______

- Improve requirements.txt; clarify what is required for which functions
- Sphinx checklist extension to convert "- [ ]" to "☐" and "- [X]" to "☑"
