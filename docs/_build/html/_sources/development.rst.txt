:github_url: https://github.com/KarlTDebiec/scinoephile

Development
-----------

Optical Character Recognition
_____________________________

- [x] Fix font support on new macos and matplotlib
- [x] Update GeneratedOCRDataset's generate_minimal_img
- [x] Update GeneratedOCRDataset's gen_add_img
- [x] Review Subtitle and ImageSubtitle Data Structures
- [x] Review OCR Datasets
- [x] Update OCR Datasets' save
- [x] Update OCR Datasets' load
- [x] Confirm that both 8-bit and 1-bit workflows work
- [x] Review and update AutoTrainer
- [x] Save model and reload
- [ ] Extend generate_minimal_img to check for minimal number of images
- [ ] Re-implement test data collector
- [ ] Calculate difference between test images and generated images
- [ ] Add log output to AutoTrainer
- [ ] Re-implement support for configuring AutoTrainer
- [ ] From ImageSubtitleDataset, organize data structures for tensorflow
- [ ] Apply machine learning model to ImageSubtitleDataset
- [ ] Add support for Western characters and punctuation

Migrate Compositor to New Data Structures
_________________________________________

- [ ] Print SubtitleSeries and SubtitleDataset as pandas DataFrames
- [ ] Migrate English, Chinese (may call Hanzi for clarity, and bilingual
  subtitles to SubtitleSeries

Documentation
_____________

- [x] Configure GitHub Pages documentation
- [ ] Document Base and CLToolBase
- [ ] Document Subtitle Data Structures
- [ ] Document Image Subtitle Data Structures
- [ ] Document OCRBase and OCRCLToolBase
- [ ] Document OCR Data Structures

Future Projects
_______________

- Improve requirements.txt and clarify what is required for which functions
- Automated testing using pytest and TravisCI
