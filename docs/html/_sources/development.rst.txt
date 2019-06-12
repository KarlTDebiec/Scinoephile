:github_url: https://github.com/KarlTDebiec/scinoephile

Development
-----------

Optical Character Recognition
_____________________________

- [ ] Fix documentation
- [ ] Understand problem with times
- [ ] Reimplement TestOCRDataset to link to a list of ImageSubtitleSeries
- [ ] Replace spec_cols in OCRDataset, TrainOCRDataset and TestOCRDataset
- [ ] Improve character separation to support split characters such as 儿 and 八
- [ ] Improve character separation to load assignments from another dataset
- [ ] Add support for Western characters and punctuation

Compositor
__________

- [x] Add support for overwriting files
- [x] Tests
- [ ] Add support for input and output files of the same type
- [ ] Complete documentation
- [ ] Restore support for Hanzi, pinyin, and English together
- [ ] Restore support for IPython console
- [ ] Restore truecase argument support
- [ ] Restore time offset support

Documentation
_____________

- [ ] Document Base and CLToolBase
- [ ] Document Subtitle Data Structures
- [ ] Document Image Subtitle Data Structures
- [ ] Document OCRBase and OCRCLToolBase
- [ ] Document OCR Data Structures
- [ ] Document Training tool
- [ ] Improve examples

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
