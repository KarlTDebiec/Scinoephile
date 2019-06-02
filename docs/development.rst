:github_url: https://github.com/KarlTDebiec/scinoephile

Development
-----------

Optical Character Recognition
_____________________________

- [ ] Fix documentation
- [ ] Understand problem with times
- [ ] Reimplement TestOCRDataset to link to a list of ImageSubtitleSeries
- [ ] Replace spec_cols in OCRDataset, TrainOCRDataset and TestOCRDataset
- [ ] Add log output to AutoTrainer
- [ ] Calculate diff between training images and test images to guide spec selection
- [ ] Improve character separation to support split characters such as 儿 and 八
- [ ] Improve character separation to load assignments from another dataset
- [ ] Add support for Western characters and punctuation

Compositor
__________

- [ ] Document
- [ ] Overwrite Support
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
- [ ] DatasetBase: Make load a classmethod
- [ ] OCRDataset: Implement sort function
- [ ] ImageSubtitleSeries: Improve identification of spaces between characters
- [ ] Improve performance of reading and writing training set
- [ ] Replace matplotlib with another library to improve font support
- [ ] Make clearer whether functions are acting on Images or image data
- [ ] Visualize weights
- [ ] Extend generate_training_data to add set number of images rather than use total
- [ ] Convenience function for viewing source of method/property in IPython
- [ ] Track modifications, and if infile==outfile only save if changed
- [ ] Compare to tesseract
- [ ] Implement SUP parsing in numba
- [ ] Option to compress or not when saving Datasets (takes a long time)

Future
______

- Improve requirements.txt;clarify what is required for which functions
- Sphinx checklist extension to convert "- [ ]" to "☐" and "- [X]" to "☑"
