:github_url: https://github.com/KarlTDebiec/scinoephile

Development
-----------

Compositor
__________

- [ ] Add support for input and output files of the same type
- [ ] Document overwrite parameter
- [ ] Extend test coverage
- [ ] Complete documentation
- [ ] Restore support for Hanzi, pinyin, and English together
- [ ] Restore support for IPython prompt
- [ ] Restore support fo truecase
- [ ] Restore support for time offset

Derasterizer
____________

- [x] Add command-line arguments
- [x] Read infiles
- [x] Write outfile
- [x] Segment characters
- [ ] Predict characters
- [ ] Reconstruct text
- [ ] Compare to standard
- [ ] Print statistics

Documentation
_____________

- [ ] Review

Miscellaneous
_____________

- [ ] ImageSubtitleEvent: rename data to full_data, char_data to data
- [ ] ImageSubtitleSeries: Improve identification of spaces between characters
- [ ] Replace matplotlib with another library to improve font support
- [ ] Make clearer whether functions are acting on Images or image data
- [ ] Visualize weights
- [ ] Convenience function for viewing source of method/property in IPython
- [ ] Track modifications, and if infile==outfile only save if changed
- [ ] Compare to tesseract
- [ ] Option to compress or not when saving Datasets (takes a long time)

Future
______

- Improve requirements.txt; clarify what is required for which functions
- Sphinx checklist extension to convert "- [ ]" to "☐" and "- [X]" to "☑"
