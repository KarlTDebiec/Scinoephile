:github_url: https://github.com/KarlTDebiec/scinoephile

Development
-----------

Optical Character Recognition
_____________________________

- [x] Fix font support on new macos and matplotlib
- [x] Review Subtitle and ImageSubtitle Data Structures
- [ ] Review OCR Data Structures
- [ ] Migrate Machine Learning code to newer data structures
- [ ] Save machine learning model and reload
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
